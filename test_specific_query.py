#!/usr/bin/env python3
"""
Test script to test the API with a more specific prompt.
"""

import requests
import json
import time
import sys

def test_api_with_prompt(prompt):
    """Test the API with a specific prompt."""
    # Define the API endpoint
    base_url = "http://localhost:8000"
    
    # Make the request
    print(f"Making request to {base_url}/api/search with prompt: {prompt}")
    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"prompt": prompt, "max_candidates": 3, "include_linkedin": False}
        )
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {base_url}. Is the API running?")
        return False
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    # Get the request ID
    request_id = response.json().get("request_id")
    if not request_id:
        print("Error: No request ID in response")
        return False
    
    print(f"Request ID: {request_id}")
    print("Waiting for processing to complete...")
    
    # Poll for results
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(2)  # Wait 2 seconds between polls
        
        # Get the search result
        try:
            result_response = requests.get(f"{base_url}/api/search/{request_id}")
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to {base_url}. Is the API running?")
            return False
        
        # Check if the request was successful
        if result_response.status_code != 200:
            print(f"Error: Result request failed with status code {result_response.status_code}")
            print(result_response.text)
            continue
        
        # Check if processing is complete
        result = result_response.json()
        status = result.get("status")
        
        print(f"Status: {status} (attempt {attempt + 1}/{max_attempts})")
        
        if status == "completed":
            # Print the results
            print("\nSearch completed!")
            
            print("\nFilters:")
            filters = result.get("filters", {})
            print(json.dumps(filters, indent=2))
            
            print("\nCandidates:")
            candidates = result.get("candidates", [])
            for i, candidate in enumerate(candidates):
                print(f"\nCandidate {i + 1}:")
                print(f"Name: {candidate.get('name')}")
                print(f"Title: {candidate.get('title')}")
                print(f"Company: {candidate.get('company')}")
                print(f"Accuracy: {candidate.get('accuracy')}%")
                print(f"Reasons: {', '.join(candidate.get('reasons', []))}")
                print(f"LinkedIn: {candidate.get('linkedin_url')}")
                print(f"Location: {candidate.get('location')}")
            
            print("\nBehavioral Data:")
            behavioral_data = result.get("behavioral_data", {})
            print(json.dumps(behavioral_data, indent=2))
            
            return True
        
        elif status == "failed":
            print(f"Error: Search failed - {result.get('error')}")
            return False
    
    print(f"Error: Search did not complete after {max_attempts} attempts")
    return False

if __name__ == "__main__":
    prompt = "find me senior sales directors at tech companies who are evaluating CRM solutions"
    test_api_with_prompt(prompt)