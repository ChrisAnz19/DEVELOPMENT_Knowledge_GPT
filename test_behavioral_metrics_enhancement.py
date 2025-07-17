"""
Test the behavioral metrics enhancement locally using the API response.
"""

import requests
import json
import time
import sys
from pprint import pprint

from behavioral_metrics import enhance_behavioral_data

def test_behavioral_metrics_enhancement(prompt):
    """
    Test the behavioral metrics enhancement locally using the API response.
    
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
    
    # Display the candidates
    candidates = data.get("candidates", [])
    print(f"Found {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates):
        print(f"\nCandidate {i+1}: {candidate.get('name', 'Unknown')}")
        print(f"Title: {candidate.get('title', 'Unknown')}")
        print(f"Company: {candidate.get('company', 'Unknown')}")
    
    # Get the behavioral data from the API
    api_behavioral_data = data.get("behavioral_data", {})
    
    print("\n=== API BEHAVIORAL DATA ===\n")
    pprint(api_behavioral_data)
    
    # Convert the API behavioral data to the format expected by enhance_behavioral_data
    behavioral_data = {
        "insights": [],
        "page_views": [],
        "sessions": [],
        "content_interactions": []
    }
    
    # Add insights from the API behavioral data
    if "behavioral_insights" in api_behavioral_data:
        for key, value in api_behavioral_data["behavioral_insights"].items():
            behavioral_data["insights"].append(value)
    
    # Simulate some engagement data based on the API response
    current_time = time.time()
    
    # Add page views
    behavioral_data["page_views"] = [
        {"url": "/pricing", "title": "Pricing Plans", "timestamp": current_time - 86400},
        {"url": "/features", "title": "Product Features", "timestamp": current_time - 43200},
        {"url": "/case-studies", "title": "Customer Success Stories", "timestamp": current_time - 21600},
        {"url": "/about-us", "title": "Our Mission", "timestamp": current_time - 7200}
    ]
    
    # Add sessions
    behavioral_data["sessions"] = [
        {"timestamp": current_time - 86400, "duration": 600, "pages": 5},
        {"timestamp": current_time - 43200, "duration": 900, "pages": 8},
        {"timestamp": current_time - 21600, "duration": 300, "pages": 3},
        {"timestamp": current_time - 10800, "duration": 1200, "pages": 10}
    ]
    
    # Add content interactions
    behavioral_data["content_interactions"] = [
        {"content_type": "pricing_document", "title": "Enterprise Pricing", "timestamp": current_time - 86400},
        {"content_type": "whitepaper", "title": "Cloud Security Best Practices", "timestamp": current_time - 43200},
        {"content_type": "case_study", "title": "Financial Services Success Story", "timestamp": current_time - 21600},
        {"content_type": "webinar", "title": "Product Demo", "timestamp": current_time - 10800}
    ]
    
    # Enhance the behavioral data with our metrics
    print("\n=== ENHANCING BEHAVIORAL DATA ===\n")
    enhanced_data = enhance_behavioral_data(
        behavioral_data,
        candidates,
        prompt
    )
    
    # Display the enhanced behavioral metrics
    print("\n=== ENHANCED BEHAVIORAL METRICS ===\n")
    
    # Display Commitment Momentum Index
    cmi = enhanced_data.get("commitment_momentum_index", {})
    print("Commitment Momentum Index:")
    print(f"Score: {cmi.get('score', 'N/A')}/100")
    print(f"Description: {cmi.get('description', 'N/A')}")
    print("Factors:")
    factors = cmi.get("factors", {})
    for factor, value in factors.items():
        print(f"  - {factor}: {value:.2f}")
    print()
    
    # Display Risk-Barrier Focus Score
    rbfs = enhanced_data.get("risk_barrier_focus_score", {})
    print("Risk-Barrier Focus Score:")
    print(f"Score: {rbfs.get('score', 'N/A')}/100")
    print(f"Description: {rbfs.get('description', 'N/A')}")
    print("Factors:")
    factors = rbfs.get("factors", {})
    for factor, value in factors.items():
        print(f"  - {factor}: {value:.2f}")
    print()
    
    # Display Identity Alignment Signal
    ias = enhanced_data.get("identity_alignment_signal", {})
    print("Identity Alignment Signal:")
    print(f"Score: {ias.get('score', 'N/A')}/100")
    print(f"Description: {ias.get('description', 'N/A')}")
    print("Factors:")
    factors = ias.get("factors", {})
    for factor, value in factors.items():
        print(f"  - {factor}: {value:.2f}")
    print()
    
    # Display Psychometric Modeling Insight
    pmi = enhanced_data.get("psychometric_modeling_insight")
    print("Psychometric Modeling Insight:")
    print(pmi)

if __name__ == "__main__":
    # Get the prompt from command line arguments or use a default prompt
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Find a senior software engineer with experience in machine learning and cloud computing"
    
    # Run the test
    test_behavioral_metrics_enhancement(prompt)