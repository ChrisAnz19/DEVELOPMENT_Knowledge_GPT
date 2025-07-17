#!/usr/bin/env python3
"""
Test script for the enhanced assessment API
"""

import json
from assess_and_return import select_top_candidates

# Sample candidate data
sample_candidates = [
    {
        "name": "Jane Smith",
        "title": "Senior Software Engineer",
        "organization_name": "Tech Solutions Inc.",
        "email": "jane.smith@example.com",
        "linkedin_url": "https://linkedin.com/in/janesmith"
    },
    {
        "name": "John Doe",
        "title": "Marketing Director",
        "organization_name": "Brand Builders LLC",
        "email": "john.doe@example.com",
        "linkedin_url": "https://linkedin.com/in/johndoe"
    },
    {
        "name": "Alex Johnson",
        "title": "Financial Analyst",
        "organization_name": "Investment Partners",
        "email": "alex.johnson@example.com",
        "linkedin_url": "https://linkedin.com/in/alexjohnson"
    },
    {
        "name": "Sarah Williams",
        "title": "Frontend Developer",
        "organization_name": "Web Wizards",
        "email": "sarah.williams@example.com",
        "linkedin_url": "https://linkedin.com/in/sarahwilliams"
    }
]

# Test with a specific prompt
test_prompt = "Looking for someone with experience in manufacturing operations"

print(f"Testing enhanced assessment with prompt: '{test_prompt}'")
print("Candidates:")
for candidate in sample_candidates:
    print(f"- {candidate['name']}: {candidate['title']} at {candidate['organization_name']}")

print("\nCalling API...")
results = select_top_candidates(test_prompt, sample_candidates)

print("\nResults:")
print(json.dumps(results, indent=2))

# Print in a more readable format
print("\nTop candidates:")
for i, candidate in enumerate(results):
    print(f"\n{i+1}. {candidate['name']} - {candidate['title']} at {candidate['company']}")
    print(f"   Match accuracy: {candidate['accuracy']}%")
    print("   Behavioral reasons:")
    for reason in candidate['reasons']:
        print(f"   - {reason}")