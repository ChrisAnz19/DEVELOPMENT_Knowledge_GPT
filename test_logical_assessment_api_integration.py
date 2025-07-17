#!/usr/bin/env python3
"""
Integration tests for the logical assessment feature via the API.

This test script makes actual API calls to test the logical assessment feature
in a running instance of the API.
"""

import requests
import json
import time
import sys
import os
import argparse
from datetime import datetime

def test_api_with_coherent_query():
    """
    Test the API with a query that should return coherent results.
    
    This test verifies that the API correctly processes a query that should
    return logically coherent results.
    """
    # Define the API endpoint
    base_url = "http://localhost:8000"
    
    # Define the test query
    test_query = "Find me senior software engineers at Google with experience in AI"
    
    print(f"\n=== Testing API with coherent query: '{test_query}' ===")
    
    # Make the request
    print(f"Making request to {base_url}/api/search...")
    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"prompt": test_query, "max_candidates": 2, "include_linkedin": False}
        )
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {base_url}. Is the API running?")
        return False
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    # Get the request ID from the response
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
            
            # Check if candidates were returned
            candidates = result.get("candidates", [])
            if not candidates:
                print("Error: No candidates returned")
                return False
            
            print(f"\nFound {len(candidates)} candidates:")
            for i, candidate in enumerate(candidates):
                print(f"\nCandidate {i + 1}:")
                print(f"Name: {candidate.get('name')}")
                print(f"Title: {candidate.get('title')}")
                print(f"Company: {candidate.get('company')}")
                print(f"Accuracy: {candidate.get('accuracy')}%")
                print(f"Reasons: {', '.join(candidate.get('reasons', []))}")
            
            # Test passed
            print("\nTest passed: API returned candidates for a coherent query")
            return True
        
        elif status == "failed":
            print(f"Error: Search failed - {result.get('error')}")
            return False
    
    print(f"Error: Search did not complete after {max_attempts} attempts")
    return False

def test_api_with_incoherent_query():
    """
    Test the API with a query that should not return coherent results.
    
    This test verifies that the API correctly processes a query that should
    not return logically coherent results, falling back to behavioral simulation.
    """
    # Define the API endpoint
    base_url = "http://localhost:8000"
    
    # Define the test query (intentionally nonsensical)
    test_query = "Find me underwater basket weavers who can code in COBOL and have experience with quantum computing"
    
    print(f"\n=== Testing API with incoherent query: '{test_query}' ===")
    
    # Make the request
    print(f"Making request to {base_url}/api/search...")
    try:
        response = requests.post(
            f"{base_url}/api/search",
            json={"prompt": test_query, "max_candidates": 2, "include_linkedin": False}
        )
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {base_url}. Is the API running?")
        return False
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Request failed with status code {response.status_code}")
        print(response.text)
        return False
    
    # Get the request ID from the response
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
            
            # Check if behavioral data was returned
            behavioral_data = result.get("behavioral_data", {})
            if not behavioral_data:
                print("Error: No behavioral data returned")
                return False
            
            print("\nBehavioral data returned:")
            print(json.dumps(behavioral_data, indent=2))
            
            # Test passed
            print("\nTest passed: API fell back to behavioral simulation for an incoherent query")
            return True
        
        elif status == "failed":
            print(f"Error: Search failed - {result.get('error')}")
            return False
    
    print(f"Error: Search did not complete after {max_attempts} attempts")
    return False

def run_tests():
    """Run all the API integration tests."""
    print(f"Starting API integration tests at {datetime.now().isoformat()}")
    
    # Run the tests
    test_results = [
        test_api_with_coherent_query(),
        test_api_with_incoherent_query()
    ]
    
    # Print the summary
    print("\n=== Test Summary ===")
    print(f"Tests passed: {test_results.count(True)}/{len(test_results)}")
    print(f"Tests failed: {test_results.count(False)}/{len(test_results)}")
    
    # Return True if all tests passed
    return all(test_results)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run API integration tests for the logical assessment feature")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Base URL of the API (default: http://localhost:8000)")
    args = parser.parse_args()
    
    # Run the tests
    success = run_tests()
    
    # Exit with non-zero code if tests failed
    sys.exit(0 if success else 1)