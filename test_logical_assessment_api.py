#!/usr/bin/env python3
"""
Test script for the logical assessment feature via the API.
"""

import requests
import json
import time
import sys

def test_logical_assessment():
    """Test the logical assessment feature by making a request to the API."""
    # Define the API endpoint
    base_url = "http://localhost:8000"
    
    # Define the test query
    test_query = "Find me senior software engineers at Google with experience in AI"
    
    # Make the request
    print(f"Making request to {base_url}/api/search with query: {test_query}")
    response = requests.post(
        f"{base_url}/api/search",
        json={"prompt": test_query, "max_candidates": 2, "include_linkedin": False}
    )
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Request failed with status code {response.status_code}")
        print(response.text)
        return
    
    # Get the request ID
    request_id = response.json().get("request_id")
    if not request_id:
        print("Error: No request ID in response")
        return
    
    print(f"Request ID: {request_id}")
    print("Waiting for processing to complete...")
    
    # Poll for results
    max_attempts = 30
    for attempt in range(max_attempts):
        time.sleep(2)  # Wait 2 seconds between polls
        
        # Get the search result
        result_response = requests.get(f"{base_url}/api/search/{request_id}")
        
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
            print(json.dumps(result.get("filters", {}), indent=2))
            
            print("\nCandidates:")
            candidates = result.get("candidates", [])
            for i, candidate in enumerate(candidates):
                print(f"\nCandidate {i + 1}:")
                print(f"Name: {candidate.get('name')}")
                print(f"Title: {candidate.get('title')}")
                print(f"Company: {candidate.get('company')}")
                print(f"Accuracy: {candidate.get('accuracy')}%")
                print(f"Reasons: {', '.join(candidate.get('reasons', []))}")
            
            print("\nBehavioral Data:")
            print(json.dumps(result.get("behavioral_data", {}), indent=2))
            
            return
        
        elif status == "failed":
            print(f"Error: Search failed - {result.get('error')}")
            return
    
    print(f"Error: Search did not complete after {max_attempts} attempts")

if __name__ == "__main__":
    test_logical_assessment()