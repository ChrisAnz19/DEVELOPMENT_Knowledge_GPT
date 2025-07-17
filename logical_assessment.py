#!/usr/bin/env python3
"""
Logical Assessment Module

This module provides functionality to assess the logical coherence between
a user's query and the results returned by Apollo API.
"""

import os
import json
import logging
from typing import List, Dict, Tuple, Any, Optional
from openai_utils import call_openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def assess_logical_coherence(user_query: str, apollo_results: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Assesses the logical coherence between the user's query and the Apollo API results.
    
    Args:
        user_query: The original user query
        apollo_results: The results returned by the Apollo API
        
    Returns:
        tuple containing:
        - bool: Whether the results are logically coherent
        - list: Filtered list of logically coherent results (or empty if none)
        - str: Explanation of the assessment
    """
    # Handle edge cases
    if not apollo_results:
        logger.info("No Apollo results to assess")
        return True, [], "No results to assess for logical coherence"
    
    # Limit the number of results to assess to reduce token usage
    results_to_assess = apollo_results[:5]  # Only assess top 5 results
    
    # Prepare the data for assessment
    assessment_data = {
        "user_query": user_query,
        "apollo_results": [
            {
                "name": result.get("name", "Unknown"),
                "title": result.get("title", "Unknown"),
                "company": result.get("organization_name", result.get("company", "Unknown")),
                "linkedin_url": result.get("linkedin_url", ""),
                "location": result.get("location", "Unknown"),
                "seniority": result.get("seniority", "Unknown")
            }
            for result in results_to_assess
        ]
    }
    
    # Create the prompt for the AI model
    system_message = """
    You are a logical assessment system that evaluates whether search results logically match a user's query intent.
    Your task is to determine if each candidate in the results makes sense given the user's search criteria.
    
    For each candidate, assess:
    1. Does the candidate's profile logically match what the user is looking for?
    2. Are there any obvious mismatches or inconsistencies?
    3. Would a human reasonably consider this candidate relevant to the query?
    
    Important guidelines for assessment:
    - Recognize semantic equivalence in job titles (e.g., "Director of Sales" and "Sales Director" are equivalent)
    - Consider variations in title formatting (e.g., "VP Sales" and "Vice President, Sales" are equivalent)
    - Look for relevant keywords in titles even if they don't match exactly (e.g., "Chief Revenue Officer" is relevant for a sales leadership query)
    - Consider seniority levels appropriately (e.g., "Senior" or "Sr." prefixes, or "Director" vs "Manager" levels)
    - Be flexible with industry-specific title variations while maintaining the core role requirements
    - Understand that some titles may use different terminology for the same role (e.g., "Business Development" can be equivalent to "Sales" in many contexts)
    
    Provide your assessment as a JSON object with the following structure:
    {
        "overall_coherent": true/false,
        "coherent_results": [indices of coherent results],
        "explanation": "Brief explanation of your assessment"
    }
    """
    
    prompt = f"""
    Please assess the logical coherence between this user query and the Apollo API results:
    
    USER QUERY:
    {user_query}
    
    APOLLO RESULTS:
    {json.dumps(assessment_data["apollo_results"], indent=2)}
    
    Determine if each result logically matches the user's query intent.
    Return your assessment as a JSON object.
    """
    
    try:
        # Call the AI model to assess logical coherence
        response = call_openai(
            prompt=prompt,
            system_message=system_message,
            model="gpt-3.5-turbo",  # Using a smaller, faster model as specified in the design
            temperature=0.2,  # Low temperature for more consistent results
            max_tokens=800
        )
        
        if not response:
            logger.error("Failed to get response from AI model")
            return True, apollo_results, "Assessment failed, proceeding with all results"
        
        # Parse the response
        try:
            # Extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                assessment = json.loads(json_match.group(0))
            else:
                assessment = json.loads(response)
                
            overall_coherent = assessment.get("overall_coherent", True)
            coherent_indices = assessment.get("coherent_results", list(range(len(results_to_assess))))
            explanation = assessment.get("explanation", "No explanation provided")
            
            # Filter the results based on the assessment
            coherent_results = []
            if coherent_indices:
                # Map the indices back to the original results
                for idx in coherent_indices:
                    if 0 <= idx < len(results_to_assess):
                        coherent_results.append(results_to_assess[idx])
                
                # If we assessed only a subset, include the rest as they weren't assessed
                if len(apollo_results) > len(results_to_assess):
                    coherent_results.extend(apollo_results[len(results_to_assess):])
            
            # If no coherent results were found but we have results, return all results
            if not coherent_results and apollo_results:
                logger.warning("No coherent results found, falling back to all results")
                return False, apollo_results, "No logically coherent results found, using all results as fallback"
            
            return overall_coherent, coherent_results, explanation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse assessment response: {e}")
            logger.debug(f"Response was: {response}")
            return True, apollo_results, "Failed to parse assessment, proceeding with all results"
            
    except Exception as e:
        logger.error(f"Error during logical assessment: {e}")
        return True, apollo_results, f"Assessment error: {str(e)}, proceeding with all results"