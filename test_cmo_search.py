#!/usr/bin/env python3
"""
Test CMO search with the improved AI prompting system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_prompt_enhancement import enhance_prompt, analyze_prompt
from prompt_formatting import parse_prompt_to_internal_database_filters

def test_cmo_search():
    """Test CMO search with various prompt variations."""
    print("=== Testing CMO Search Prompts ===")
    
    cmo_prompts = [
        "I was asking for CMOs",
        "Find CMOs",
        "Looking for Chief Marketing Officers",
        "Need CMOs at tech companies",
        "Find CMOs interested in marketing automation",
        "CMOs evaluating new marketing platforms",
        "Chief Marketing Officers at SaaS companies"
    ]
    
    for prompt in cmo_prompts:
        print(f"\n{'='*60}")
        print(f"Original Prompt: {prompt}")
        print(f"{'='*60}")
        
        try:
            # Test smart prompt enhancement
            enhanced, analysis = enhance_prompt(prompt)
            print(f"Enhanced Prompt: {enhanced}")
            print(f"\nAnalysis:")
            print(f"  - Detected products: {analysis.detected_products}")
            print(f"  - Competitors to exclude: {analysis.competitors}")
            print(f"  - Intent: {'Buying' if analysis.buying_intent else 'Selling' if analysis.selling_intent else 'Neutral'}")
            print(f"  - Confidence: {analysis.intent_confidence:.2f}")
            if analysis.reasoning:
                print(f"  - Reasoning: {'; '.join(analysis.reasoning)}")
            
            # Test filter generation
            filters = parse_prompt_to_internal_database_filters(enhanced)
            print(f"\nGenerated Filters:")
            print(f"  Organization filters: {filters.get('organization_filters', {})}")
            print(f"  Person filters: {filters.get('person_filters', {})}")
            print(f"  Reasoning: {filters.get('reasoning', 'N/A')}")
            
        except Exception as e:
            print(f"Error processing prompt: {e}")
            import traceback
            traceback.print_exc()

def test_cmo_behavioral_patterns():
    """Test behavioral pattern generation for CMOs."""
    print(f"\n{'='*60}")
    print("=== Testing CMO Behavioral Patterns ===")
    print(f"{'='*60}")
    
    # Mock CMO candidates
    cmo_candidates = [
        {
            "name": "Sarah Johnson",
            "title": "Chief Marketing Officer", 
            "company": "TechStartup Inc",
            "email": "sarah@techstartup.com"
        },
        {
            "name": "Michael Chen",
            "title": "CMO",
            "company": "SaaS Solutions Corp",
            "email": "michael@saassolutions.com"
        },
        {
            "name": "Lisa Rodriguez",
            "title": "Chief Marketing Officer",
            "company": "Enterprise Software Ltd",
            "email": "lisa@enterprisesoftware.com"
        }
    ]
    
    try:
        from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
        
        test_prompt = "Find CMOs interested in marketing automation"
        enhanced_candidates = enhance_behavioral_data_for_multiple_candidates(cmo_candidates, test_prompt)
        
        print(f"Generated behavioral data for {len(enhanced_candidates)} CMO candidates:")
        
        for i, candidate in enumerate(enhanced_candidates):
            behavioral_data = candidate.get("behavioral_data", {})
            insight = behavioral_data.get("behavioral_insight", "No insight generated")
            
            print(f"\nCMO {i+1}: {candidate['name']} ({candidate['title']})")
            print(f"Company: {candidate['company']}")
            print(f"Behavioral Insight: {insight}")
            
            scores = behavioral_data.get("scores", {})
            if scores:
                cmi = scores.get("cmi", {}).get("score", "N/A")
                rbfs = scores.get("rbfs", {}).get("score", "N/A")
                ias = scores.get("ias", {}).get("score", "N/A")
                print(f"Behavioral Scores:")
                print(f"  - CMI (Commitment Momentum): {cmi}")
                print(f"  - RBFS (Risk-Barrier Focus): {rbfs}")
                print(f"  - IAS (Identity Alignment): {ias}")
                
                # Show explanations
                cmi_exp = scores.get("cmi", {}).get("explanation", "")
                rbfs_exp = scores.get("rbfs", {}).get("explanation", "")
                ias_exp = scores.get("ias", {}).get("explanation", "")
                if cmi_exp or rbfs_exp or ias_exp:
                    print(f"Score Explanations:")
                    if cmi_exp: print(f"  - CMI: {cmi_exp}")
                    if rbfs_exp: print(f"  - RBFS: {rbfs_exp}")
                    if ias_exp: print(f"  - IAS: {ias_exp}")
        
    except Exception as e:
        print(f"Error in behavioral data generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing CMO Search with Improved AI Prompting")
    print("=" * 80)
    
    try:
        test_cmo_search()
        test_cmo_behavioral_patterns()
        
        print(f"\n{'='*80}")
        print("CMO search testing completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()