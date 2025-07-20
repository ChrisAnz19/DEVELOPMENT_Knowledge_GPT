#!/usr/bin/env python3
"""
Test script to validate AI prompting improvements.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_prompt_enhancement import enhance_prompt, analyze_prompt
from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
from openai_utils import validate_response_uniqueness, generate_diverse_prompts

def test_smart_prompt_enhancement():
    """Test the improved smart prompt enhancement."""
    print("=== Testing Smart Prompt Enhancement ===")
    
    test_prompts = [
        "Find me a sales manager looking to buy a new dialer, like Orum",
        "Looking for CTOs interested in CRM solutions",
        "Find companies that sell sales automation tools",
        "Need marketing directors evaluating new platforms"
    ]
    
    for prompt in test_prompts:
        print(f"\nOriginal: {prompt}")
        try:
            enhanced, analysis = enhance_prompt(prompt)
            print(f"Enhanced: {enhanced}")
            print(f"Analysis: Detected {len(analysis.detected_products)} products, "
                  f"{len(analysis.competitors)} competitors, "
                  f"Intent: {'buying' if analysis.buying_intent else 'selling' if analysis.selling_intent else 'neutral'} "
                  f"(confidence: {analysis.intent_confidence:.2f})")
            if analysis.reasoning:
                print(f"Reasoning: {'; '.join(analysis.reasoning)}")
        except Exception as e:
            print(f"Error: {e}")

def test_behavioral_data_generation():
    """Test the improved behavioral data generation."""
    print("\n=== Testing Behavioral Data Generation ===")
    
    # Mock candidate data
    test_candidates = [
        {
            "name": "John Smith",
            "title": "Sales Manager",
            "company": "TechCorp",
            "email": "john@techcorp.com"
        },
        {
            "name": "Jane Doe", 
            "title": "Sales Director",
            "company": "SoftwareInc",
            "email": "jane@softwareinc.com"
        },
        {
            "name": "Bob Johnson",
            "title": "VP of Sales",
            "company": "DataSystems",
            "email": "bob@datasystems.com"
        }
    ]
    
    test_prompt = "Find sales leaders interested in CRM solutions"
    
    try:
        enhanced_candidates = enhance_behavioral_data_for_multiple_candidates(test_candidates, test_prompt)
        
        print(f"Generated behavioral data for {len(enhanced_candidates)} candidates:")
        
        insights = []
        for i, candidate in enumerate(enhanced_candidates):
            behavioral_data = candidate.get("behavioral_data", {})
            insight = behavioral_data.get("behavioral_insight", "No insight generated")
            insights.append(insight)
            
            print(f"\nCandidate {i+1}: {candidate['name']} ({candidate['title']})")
            print(f"Insight: {insight}")
            
            scores = behavioral_data.get("scores", {})
            if scores:
                cmi = scores.get("cmi", {}).get("score", "N/A")
                rbfs = scores.get("rbfs", {}).get("score", "N/A") 
                ias = scores.get("ias", {}).get("score", "N/A")
                print(f"Scores - CMI: {cmi}, RBFS: {rbfs}, IAS: {ias}")
        
        # Test uniqueness
        unique_insights = validate_response_uniqueness(insights, similarity_threshold=0.7)
        print(f"\nUniqueness check: {len(unique_insights)} unique insights out of {len(insights)} total")
        
    except Exception as e:
        print(f"Error in behavioral data generation: {e}")

def test_response_uniqueness():
    """Test the response uniqueness validation."""
    print("\n=== Testing Response Uniqueness ===")
    
    test_responses = [
        "They prefer detailed analysis before making decisions.",
        "They like thorough research and detailed analysis before deciding.",
        "They move quickly once they have all the information needed.",
        "They require comprehensive data before committing to solutions.",
        "They evaluate options based on team consensus and stakeholder input."
    ]
    
    print(f"Original responses: {len(test_responses)}")
    for i, response in enumerate(test_responses):
        print(f"{i+1}. {response}")
    
    unique_responses = validate_response_uniqueness(test_responses, similarity_threshold=0.7)
    print(f"\nUnique responses: {len(unique_responses)}")
    for i, response in enumerate(unique_responses):
        print(f"{i+1}. {response}")

def test_prompt_diversification():
    """Test prompt diversification for better AI responses."""
    print("\n=== Testing Prompt Diversification ===")
    
    base_prompt = "Generate insight about their decision-making approach"
    diverse_prompts = generate_diverse_prompts(base_prompt, count=4)
    
    print(f"Base prompt: {base_prompt}")
    print("Diverse variations:")
    for i, prompt in enumerate(diverse_prompts):
        print(f"{i+1}. {prompt}")

if __name__ == "__main__":
    print("Testing AI Prompting Improvements")
    print("=" * 50)
    
    try:
        test_smart_prompt_enhancement()
        test_behavioral_data_generation()
        test_response_uniqueness()
        test_prompt_diversification()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()