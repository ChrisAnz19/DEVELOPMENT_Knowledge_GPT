#!/usr/bin/env python3
"""
Test agency owner search with the improved AI prompting system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_prompt_enhancement import enhance_prompt, analyze_prompt
from prompt_formatting import parse_prompt_to_internal_database_filters

def test_agency_owner_search():
    """Test agency owner search with various prompt variations."""
    print("=== Testing Agency Owner Search Prompts ===")
    
    agency_prompts = [
        "Help me find an outbound agency owner that is looking to buy a new cold email tool",
        "Find marketing agency owners",
        "Looking for agency owners interested in lead generation tools",
        "Need owners of digital marketing agencies",
        "Find founders of outbound marketing agencies",
        "Agency owners evaluating email marketing platforms",
        "Marketing agency CEOs looking for new tools"
    ]
    
    for prompt in agency_prompts:
        print(f"\n{'='*80}")
        print(f"Original Prompt: {prompt}")
        print(f"{'='*80}")
        
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
            
            # Validate filter quality
            org_filters = filters.get('organization_filters', {})
            person_filters = filters.get('person_filters', {})
            
            print(f"\nFilter Quality Check:")
            
            # Check for industry targeting
            has_industry_context = bool(org_filters.get('q_organization_keyword_tags'))
            print(f"  ✅ Industry targeting: {has_industry_context} - {org_filters.get('q_organization_keyword_tags', 'None')}")
            
            # Check for appropriate titles
            titles = person_filters.get('person_titles', [])
            appropriate_titles = any(title.lower() in ['owner', 'founder', 'ceo', 'president'] for title in titles)
            print(f"  ✅ Appropriate titles: {appropriate_titles} - {titles}")
            
            # Check for seniority
            has_seniority = bool(person_filters.get('person_seniorities'))
            print(f"  ✅ Seniority targeting: {has_seniority} - {person_filters.get('person_seniorities', 'None')}")
            
        except Exception as e:
            print(f"Error processing prompt: {e}")
            import traceback
            traceback.print_exc()

def test_agency_behavioral_patterns():
    """Test behavioral pattern generation for agency owners."""
    print(f"\n{'='*80}")
    print("=== Testing Agency Owner Behavioral Patterns ===")
    print(f"{'='*80}")
    
    # Mock agency owner candidates
    agency_candidates = [
        {
            "name": "Sarah Martinez",
            "title": "Founder & CEO", 
            "company": "Digital Growth Agency",
            "email": "sarah@digitalgrowth.com"
        },
        {
            "name": "Mike Thompson",
            "title": "Owner",
            "company": "Outbound Marketing Solutions",
            "email": "mike@outboundmarketing.com"
        },
        {
            "name": "Lisa Chen",
            "title": "President",
            "company": "Lead Generation Experts LLC",
            "email": "lisa@leadgenexperts.com"
        }
    ]
    
    try:
        from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
        
        test_prompt = "Help me find an outbound agency owner that is looking to buy a new cold email tool"
        enhanced_candidates = enhance_behavioral_data_for_multiple_candidates(agency_candidates, test_prompt)
        
        print(f"Generated behavioral data for {len(enhanced_candidates)} agency owner candidates:")
        
        for i, candidate in enumerate(enhanced_candidates):
            behavioral_data = candidate.get("behavioral_data", {})
            insight = behavioral_data.get("behavioral_insight", "No insight generated")
            
            print(f"\nAgency Owner {i+1}: {candidate['name']} ({candidate['title']})")
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
    print("Testing Agency Owner Search with Improved AI Prompting")
    print("=" * 100)
    
    try:
        test_agency_owner_search()
        test_agency_behavioral_patterns()
        
        print(f"\n{'='*100}")
        print("Agency owner search testing completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()