#!/usr/bin/env python3
"""
Test script to demonstrate the complete search output including all behavioral metrics.
"""

import json
from typing import Dict, Any, List
from behavioral_metrics import enhance_behavioral_data

def simulate_search_response() -> Dict[str, Any]:
    """
    Simulates a complete search response with all behavioral metrics.
    
    Returns:
        A dictionary representing a complete search response
    """
    # Sample behavioral data with all original metrics
    behavioral_data = {
        "commitment_momentum_index": {
            "score": 75,
            "description": "High commitment momentum - This prospect has shown consistent engagement with bottom-funnel content",
            "factors": {
                "bottom_funnel_engagement": 0.8,
                "recency_frequency": 0.7,
                "off_hours_activity": 0.6
            }
        },
        "risk_barrier_focus_score": {
            "score": 60,
            "description": "Moderate risk focus - This prospect is somewhat concerned with potential implementation challenges",
            "factors": {
                "risk_content_engagement": 0.6,
                "negative_review_focus": 0.5,
                "compliance_focus": 0.7
            }
        },
        "identity_alignment_signal": {
            "score": 85,
            "description": "Strong identity alignment - This prospect's values align well with your solution's positioning",
            "factors": {
                "purpose_driven_engagement": 0.9,
                "thought_leadership_focus": 0.8,
                "community_engagement": 0.7
            }
        },
        "psychometric_modeling_insight": "This prospect shows a preference for data-driven decision making and values technical expertise over relationship building."
    }
    
    # Sample candidate data
    candidates = [
        {
            "name": "John Doe",
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "email": "john.doe@techcorp.com",
            "accuracy": 92,
            "reasons": [
                "5+ years experience with Python",
                "Cloud architecture expertise",
                "Machine learning background"
            ],
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "profile_photo_url": "https://example.com/photo.jpg",
            "location": "San Francisco, CA"
        }
    ]
    
    # Enhance behavioral data with focused insight
    enhanced_data = enhance_behavioral_data(
        behavioral_data=behavioral_data,
        candidates=candidates,
        user_prompt="Find a senior software engineer with Python and cloud experience"
    )
    
    # Complete search response
    search_response = {
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "completed",
        "prompt": "Find a senior software engineer with Python and cloud experience",
        "filters": {
            "person_titles": ["Software Engineer", "Senior Software Engineer"],
            "person_seniorities": ["senior"],
            "organization_locations": ["San Francisco", "New York"]
        },
        "candidates": candidates,
        "behavioral_data": enhanced_data,
        "created_at": "2025-07-16T01:23:45Z",
        "completed_at": "2025-07-16T01:23:50Z"
    }
    
    return search_response

if __name__ == "__main__":
    # Generate sample search response
    response = simulate_search_response()
    
    # Print the complete response in a formatted way
    print("\n=== COMPLETE SEARCH RESPONSE ===\n")
    print(json.dumps(response, indent=2))
    
    # Print just the behavioral data for clarity
    print("\n=== BEHAVIORAL DATA SECTION ===\n")
    print(json.dumps(response["behavioral_data"], indent=2))