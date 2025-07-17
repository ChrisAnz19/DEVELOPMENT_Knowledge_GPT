#!/usr/bin/env python3
"""
Test script to test the full flow from prompt to Apollo query to output.
"""

import requests
import json
import time
import sys
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_full_flow(prompt):
    """Test the full flow from prompt to Apollo query to output."""
    # Define the API endpoint
    base_url = "http://localhost:8000"
    
    # Step 1: Make the search request
    logger.info(f"Step 1: Making request to {base_url}/api/search with prompt: {prompt}")
    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"prompt": prompt, "max_candidates": 3, "include_linkedin": False}
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to {base_url}. Is the API running?")
        return False
    
    # Check if the request was successful
    if response.status_code != 200:
        logger.error(f"Request failed with status code {response.status_code}")
        logger.error(response.text)
        return False
    
    # Get the request ID
    request_id = response.json().get("request_id")
    if not request_id:
        logger.error("No request ID in response")
        return False
    
    logger.info(f"Request ID: {request_id}")
    logger.info("Step 2: Waiting for processing to complete...")
    
    # Step 2: Poll for results
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(2)  # Wait 2 seconds between polls
        
        # Get the search result
        try:
            result_response = requests.get(f"{base_url}/api/search/{request_id}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to {base_url}. Is the API running?")
            return False
        
        # Check if the request was successful
        if result_response.status_code != 200:
            logger.error(f"Result request failed with status code {result_response.status_code}")
            logger.error(result_response.text)
            continue
        
        # Check if processing is complete
        result = result_response.json()
        status = result.get("status")
        
        logger.info(f"Status: {status} (attempt {attempt + 1}/{max_attempts})")
        
        if status == "completed":
            # Step 3: Get the detailed results
            logger.info("Step 3: Search completed! Getting detailed results...")
            
            # Get the JSON file for more details
            json_response = requests.get(f"{base_url}/api/search/{request_id}/json")
            if json_response.status_code != 200:
                logger.error(f"JSON request failed with status code {json_response.status_code}")
                logger.error(json_response.text)
                # Try to get the JSON file directly
                json_file_path = f"search_results/{request_id}.json"
                if os.path.exists(json_file_path):
                    logger.info(f"Found JSON file: {json_file_path}")
                    with open(json_file_path, 'r') as f:
                        json_data = json.load(f)
                else:
                    logger.error(f"JSON file not found: {json_file_path}")
                    return False
            else:
                json_data = json_response.json()
            
            # Step 4: Print the results
            logger.info("Step 4: Displaying results")
            
            # Print the filters
            logger.info("Filters:")
            filters = json_data.get("filters", {})
            logger.info(json.dumps(filters, indent=2))
            
            # Print the candidates
            logger.info("Candidates:")
            candidates = json_data.get("candidates", [])
            for i, candidate in enumerate(candidates):
                logger.info(f"Candidate {i + 1}:")
                logger.info(f"Name: {candidate.get('name')}")
                logger.info(f"Title: {candidate.get('title')}")
                logger.info(f"Company: {candidate.get('company')}")
                logger.info(f"Accuracy: {candidate.get('accuracy')}%")
                logger.info("Behavioral Reasons:")
                for reason in candidate.get('reasons', []):
                    logger.info(f"- {reason}")
                logger.info("")
            
            return True
        
        elif status == "failed":
            logger.error(f"Search failed - {result.get('error')}")
            return False
    
    logger.error(f"Search did not complete after {max_attempts} attempts")
    return False

if __name__ == "__main__":
    # Test with a specific prompt
    prompt = input("Enter your search prompt: ")
    if not prompt:
        prompt = "find me senior software engineers with experience in cloud computing"
    test_full_flow(prompt)