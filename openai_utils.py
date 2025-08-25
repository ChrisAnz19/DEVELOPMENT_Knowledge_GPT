#!/usr/bin/env python3
"""
OpenAI Utilities for Knowledge_GPT
General functions for making OpenAI API calls throughout the application
"""

import os
import json
import openai
from typing import Dict, List, Any, Optional, Union
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            OPENAI_API_KEY = secrets.get("openai_api_key")
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable or create secrets.json")

# Configure OpenAI client
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    logger.error("OpenAI API key not configured. OpenAI functions will not work.")

def call_openai(
    prompt: str,
    model: str = "gpt-4",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system_message: Optional[str] = None,
    messages: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Optional[str]:
    """
    General OpenAI API call function
    
    Args:
        prompt: The user prompt/message
        model: OpenAI model to use (default: gpt-4)
        max_tokens: Maximum tokens for response (default: 1000)
        temperature: Response creativity (0.0-1.0, default: 0.7)
        system_message: Optional system message to set context
        messages: Optional list of previous messages for conversation
        **kwargs: Additional parameters to pass to OpenAI API
    
    Returns:
        OpenAI response text or None if error
    """
    if not OPENAI_API_KEY:
        logger.error("OpenAI API key not configured")
        return None
    
    try:
        # Prepare messages
        if messages is None:
            messages = []
            
        # Add system message if provided
        if system_message:
            messages.insert(0, {"role": "system", "content": system_message})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Make API call using the correct OpenAI client format
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        # Extract and return response
        result = response.choices[0].message.content.strip()
        logger.info(f"OpenAI API call successful (model: {model}, tokens: {response.usage.total_tokens})")
        return result
        
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return None

def call_openai_with_retry(
    prompt: str,
    max_retries: int = 3,
    **kwargs
) -> Optional[str]:
    """
    OpenAI API call with automatic retry on failure
    
    Args:
        prompt: The user prompt/message
        max_retries: Maximum number of retry attempts
        **kwargs: Parameters to pass to call_openai
    
    Returns:
        OpenAI response text or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            result = call_openai(prompt, **kwargs)
            if result:
                return result
        except Exception as e:
            logger.warning(f"OpenAI API call attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
    
    logger.error(f"OpenAI API call failed after {max_retries} attempts")
    return None

def extract_json_from_response(response_text: str) -> Optional[dict]:
    """
    Extract the first valid JSON object from a string, even if extra data is present.
    """
    try:
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Find the first {...} block with proper nesting
        brace_count = 0
        start_idx = -1
        
        for i, char in enumerate(response_text):
            if char == '{':
                if start_idx == -1:
                    start_idx = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_idx != -1:
                    json_str = response_text[start_idx:i+1]
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
        
        # Fallback: try to parse the whole response
        return json.loads(response_text.strip())
        
    except Exception as e:
        logger.error(f"Failed to extract JSON: {e}")
        logger.debug(f"Response was: {response_text}")
    return None

def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON response from OpenAI, robust to extra data or multiple JSON objects.
    """
    try:
        # Debug: print raw response
        logger.error(f"RAW OPENAI RESPONSE: {response}")
        # Try to extract JSON from the response
        start_idx = response.find('{')
        end_idx = response.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            json_str = response[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Fallback to regex extraction
                return extract_json_from_response(response)
        else:
            # If no JSON brackets found, try parsing the whole response
            return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}")
        logger.debug(f"Response was: {response}")
        # Fallback to regex extraction
        return extract_json_from_response(response)

def call_openai_for_json(
    prompt: str,
    expected_keys: Optional[List[str]] = None,
    validate_response: bool = True,
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    OpenAI API call that expects and parses JSON response with validation
    
    Args:
        prompt: The user prompt/message
        expected_keys: Optional list of expected keys in the JSON response
        validate_response: Whether to validate the response structure
        **kwargs: Parameters to pass to call_openai
    
    Returns:
        Parsed JSON dict or None if failed
    """
    # Add JSON formatting instruction to prompt
    json_prompt = f"{prompt}\n\nRespond with valid JSON only. No additional text or explanation."
    if expected_keys:
        json_prompt += f"\nRequired JSON keys: {', '.join(expected_keys)}"
        example_format = ', '.join([f'"{key}": "value"' for key in expected_keys])
        json_prompt += f"\nExample format: {{{example_format}}}"
    
    response = call_openai_with_retry(json_prompt, **kwargs)
    if response:
        parsed_response = parse_json_response(response)
        
        # Validate response if requested
        if validate_response and parsed_response and expected_keys:
            missing_keys = [key for key in expected_keys if key not in parsed_response]
            if missing_keys:
                logger.warning(f"Response missing expected keys: {missing_keys}")
                return None
        
        return parsed_response
    return None

# Convenience functions for common use cases
def analyze_text(text: str, analysis_type: str = "general") -> Optional[str]:
    """Analyze text using OpenAI"""
    prompts = {
        "general": f"Please analyze the following text and provide insights:\n\n{text}",
        "sentiment": f"Analyze the sentiment of this text:\n\n{text}",
        "summary": f"Provide a concise summary of this text:\n\n{text}",
        "extract": f"Extract key information from this text:\n\n{text}"
    }
    
    prompt = prompts.get(analysis_type, prompts["general"])
    return call_openai(prompt, temperature=0.3)

def generate_content(content_type: str, topic: str, **kwargs) -> Optional[str]:
    """Generate content using OpenAI"""
    prompts = {
        "email": f"Write a professional email about: {topic}",
        "summary": f"Write a summary about: {topic}",
        "description": f"Write a description for: {topic}",
        "analysis": f"Provide analysis on: {topic}"
    }
    
    prompt = prompts.get(content_type, f"Generate {content_type} about: {topic}")
    return call_openai(prompt, **kwargs)

def validate_response_uniqueness(responses: List[str], similarity_threshold: float = 0.8) -> List[str]:
    """
    Validate that responses are sufficiently unique to avoid duplication.
    
    Args:
        responses: List of response strings to validate
        similarity_threshold: Threshold for considering responses too similar (0.0-1.0)
        
    Returns:
        List of unique responses
    """
    if len(responses) <= 1:
        return responses
    
    unique_responses = []
    
    for response in responses:
        is_unique = True
        response_words = set(response.lower().split())
        
        for existing in unique_responses:
            existing_words = set(existing.lower().split())
            
            # Calculate Jaccard similarity (intersection over union)
            if len(response_words) > 0 and len(existing_words) > 0:
                intersection = len(response_words.intersection(existing_words))
                union = len(response_words.union(existing_words))
                similarity = intersection / union
                
                if similarity > similarity_threshold:
                    is_unique = False
                    break
        
        if is_unique:
            unique_responses.append(response)
    
    return unique_responses


def generate_diverse_prompts(base_prompt: str, count: int = 3) -> List[str]:
    """
    Generate diverse variations of a base prompt to encourage unique responses.
    
    Args:
        base_prompt: The base prompt to vary
        count: Number of variations to generate
        
    Returns:
        List of prompt variations
    """
    variations = [base_prompt]  # Include original
    
    # Add perspective variations
    perspective_prefixes = [
        "From a strategic perspective, ",
        "Considering their daily workflow, ",
        "Based on their decision-making style, ",
        "Looking at their professional priorities, "
    ]
    
    # Add context variations
    context_suffixes = [
        " Focus on their evaluation process.",
        " Emphasize their decision criteria.",
        " Consider their implementation approach.",
        " Think about their stakeholder involvement."
    ]
    
    for i in range(1, min(count, len(perspective_prefixes) + 1)):
        if i <= len(perspective_prefixes):
            variation = perspective_prefixes[i-1] + base_prompt.lower()
        else:
            variation = base_prompt + context_suffixes[(i-1) % len(context_suffixes)]
        variations.append(variation)
    
    return variations[:count]


if __name__ == "__main__":
    # Test the OpenAI functions
    test_prompt = "What is the capital of France?"
    result = call_openai(test_prompt, temperature=0.1)
    print(f"Test result: {result}")
    
    # Test uniqueness validation
    test_responses = [
        "They prefer detailed analysis before making decisions.",
        "They like thorough research and detailed analysis before deciding.",
        "They move quickly once they have all the information needed."
    ]
    unique_responses = validate_response_uniqueness(test_responses)
    print(f"Unique responses: {len(unique_responses)} out of {len(test_responses)}") 