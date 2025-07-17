"""
Test the API live from prompt to output and show the behavioral metrics scores and insights.
"""

import requests
import json
import time
import sys
from pprint import pprint

def test_api_with_prompt(prompt):
    """
    Test the API with a prompt and display the behavioral metrics scores and insights.
    
    Args:
        prompt: The search prompt to use
    """
    # API base URL
    base_url = "https://knowledge-gpt-siuq.onrender.com"
    
    # Create a search request
    print(f"Creating search with prompt: '{prompt}'")
    response = requests.post(
        f"{base_url}/api/search",
        json={
            "prompt": prompt,
            "max_candidates": 3,
            "include_linkedin": True
        }
    )
    
    if response.status_code != 200:
        print(f"Error creating search: {response.status_code}")
        print(response.text)
        return
    
    # Get the request ID
    data = response.json()
    request_id = data["request_id"]
    print(f"Search created with request ID: {request_id}")
    
    # Poll for results
    print("Polling for results...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        # Get the search result
        response = requests.get(f"{base_url}/api/search/{request_id}")
        
        if response.status_code != 200:
            print(f"Error getting search result: {response.status_code}")
            print(response.text)
            return
        
        # Parse the response
        data = response.json()
        
        # Check if the search is completed
        if data["status"] == "completed":
            print("Search completed!")
            break
        elif data["status"] == "failed":
            print("Search failed!")
            print(data.get("error", "No error message provided"))
            return
        
        # Wait before polling again
        print(f"Search still processing (attempt {attempt}/{max_attempts})... waiting 2 seconds")
        time.sleep(2)
    
    if attempt >= max_attempts:
        print("Timed out waiting for search to complete")
        return
    
    # Display the results
    print("\n=== SEARCH RESULTS ===\n")
    
    # Display the filters
    print("Filters:")
    pprint(data.get("filters", {}))
    print()
    
    # Display the candidates
    candidates = data.get("candidates", [])
    print(f"Found {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates):
        print(f"\nCandidate {i+1}: {candidate.get('name', 'Unknown')}")
        print(f"Title: {candidate.get('title', 'Unknown')}")
        print(f"Company: {candidate.get('company', 'Unknown')}")
        print(f"Email: {candidate.get('email', 'Unknown')}")
        print(f"Accuracy: {candidate.get('accuracy', 0)}%")
        print("Reasons:")
        for reason in candidate.get("reasons", []):
            print(f"  - {reason}")
    
    # Display the behavioral metrics
    print("\n=== BEHAVIORAL METRICS ===\n")
    
    # Get the behavioral data
    behavioral_data = data.get("behavioral_data", {})
    
    # Print the structure of the behavioral data
    print("Behavioral Data Structure:")
    print(f"Keys: {list(behavioral_data.keys())}")
    print()
    
    # Check if we have the enhanced behavioral metrics
    if "commitment_momentum_index" in behavioral_data:
        # Display Commitment Momentum Index
        cmi = behavioral_data.get("commitment_momentum_index", {})
        print("Commitment Momentum Index:")
        print(f"Score: {cmi.get('score', 'N/A')}/100")
        print(f"Description: {cmi.get('description', 'N/A')}")
        print("Factors:")
        factors = cmi.get("factors", {})
        for factor, value in factors.items():
            print(f"  - {factor}: {value:.2f}")
        print()
        
        # Display Risk-Barrier Focus Score
        rbfs = behavioral_data.get("risk_barrier_focus_score", {})
        print("Risk-Barrier Focus Score:")
        print(f"Score: {rbfs.get('score', 'N/A')}/100")
        print(f"Description: {rbfs.get('description', 'N/A')}")
        print("Factors:")
        factors = rbfs.get("factors", {})
        for factor, value in factors.items():
            print(f"  - {factor}: {value:.2f}")
        print()
        
        # Display Identity Alignment Signal
        ias = behavioral_data.get("identity_alignment_signal", {})
        print("Identity Alignment Signal:")
        print(f"Score: {ias.get('score', 'N/A')}/100")
        print(f"Description: {ias.get('description', 'N/A')}")
        print("Factors:")
        factors = ias.get("factors", {})
        for factor, value in factors.items():
            print(f"  - {factor}: {value:.2f}")
        print()
        
        # Display Psychometric Modeling Insight
        pmi = behavioral_data.get("psychometric_modeling_insight")
        print("Psychometric Modeling Insight:")
        print(pmi)
    else:
        # Display the standard behavioral data
        print("Behavioral Insights:")
        insights = behavioral_data.get("behavioral_insights", [])
        for insight in insights:
            print(f"- {insight}")
        print()
        
        print("Supporting Data Points:")
        data_points = behavioral_data.get("supporting_data_points", [])
        for point in data_points:
            print(f"- {point}")
        print()
        
        # Print the full behavioral data for inspection
        print("Full Behavioral Data:")
        pprint(behavioral_data)

if __name__ == "__main__":
    # Get the prompt from command line arguments or use a default prompt
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Find a senior software engineer with experience in machine learning and cloud computing"
    
    # Run the test
    test_api_with_prompt(prompt)