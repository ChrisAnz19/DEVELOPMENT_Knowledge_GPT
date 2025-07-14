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
        # Find the first {...} block
        match = re.search(r'(\{.*?\})', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        logger.error(f"Still failed to parse JSON: {e}")
    return None

def parse_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Parse JSON response from OpenAI, robust to extra data or multiple JSON objects.
    """
    try:
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
    **kwargs
) -> Optional[Dict[str, Any]]:
    """
    OpenAI API call that expects and parses JSON response
    
    Args:
        prompt: The user prompt/message
        expected_keys: Optional list of expected keys in the JSON response
        **kwargs: Parameters to pass to call_openai
    
    Returns:
        Parsed JSON dict or None if failed
    """
    # Add JSON formatting instruction to prompt
    json_prompt = f"{prompt}\n\nPlease respond with valid JSON only."
    if expected_keys:
        json_prompt += f"\nExpected keys: {', '.join(expected_keys)}"
    
    response = call_openai_with_retry(json_prompt, **kwargs)
    if response:
        return parse_json_response(response)
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

if __name__ == "__main__":
    # Test the OpenAI functions
    test_prompt = "What is the capital of France?"
    result = call_openai(test_prompt, temperature=0.1)
    print(f"Test result: {result}") 