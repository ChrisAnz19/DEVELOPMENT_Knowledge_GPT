#!/usr/bin/env python3
"""
Test investment/climate search with the improved AI prompting system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from smart_prompt_enhancement import enhance_prompt, analyze_prompt
from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates, analyze_search_context

def test_investment_context_detection():
    """Test that investment contexts are properly detected."""
    print("=== Testing Investment Context Detection ===")
    
    investment_prompts = [
        "Find investors interested in climate funds",
        "Looking for people investing in ESG opportunities", 
        "Find portfolio managers evaluating sustainable investments",
        "Need venture capitalists interested in green technology",
        "Find wealth managers exploring climate investment opportunities"
    ]
    
    for prompt in investment_prompts:
        print(f"\nPrompt: {prompt}")
        context = analyze_search_context(prompt)
        print(f"Context Type: {context['context_type']}")
        print(f"Decision Factors: {context['decision_factors']}")

def test_investment_behavioral_patterns():
    """Test behavioral pattern generation for investment contexts."""
    print(f"\n{'='*80}")
    print("=== Testing Investment Behavioral Patterns ===")
    print(f"{'='*80}")
    
    # Mock investment-related candidates
    investment_candidates = [
        {
            "name": "Robert Chen",
            "title": "Portfolio Manager", 
            "company": "Green Capital Partners",
            "email": "robert@greencapital.com"
        },
        {
            "name": "Sarah Williams",
            "title": "Investment Director",
            "company": "Sustainable Wealth Management",
            "email": "sarah@sustainablewealth.com"
        },
        {
            "name": "Michael Rodriguez",
            "title": "Managing Partner",
            "company": "Climate Investment Fund",
            "email": "michael@climatefund.com"
        }
    ]
    
    try:
        test_prompt = "Find investors interested in climate funds"
        enhanced_candidates = enhance_behavioral_data_for_multiple_candidates(investment_candidates, test_prompt)
        
        print(f"Generated behavioral data for {len(enhanced_candidates)} investment candidates:")
        
        for i, candidate in enumerate(enhanced_candidates):
            behavioral_data = candidate.get("behavioral_data", {})
            insight = behavioral_data.get("behavioral_insight", "No insight generated")
            
            print(f"\nInvestor {i+1}: {candidate['name']} ({candidate['title']})")
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
                print(f"Score Explanations:")
                if cmi_exp: print(f"  - CMI: {cmi_exp}")
                if rbfs_exp: print(f"  - RBFS: {rbfs_exp}")
                if ias_exp: print(f"  - IAS: {ias_exp}")
                
                # Validate appropriateness for investment context
                print(f"Context Appropriateness Check:")
                inappropriate_terms = ["implementation", "leadership goals", "team", "workflow", "productivity"]
                has_inappropriate = any(term in (cmi_exp + rbfs_exp + ias_exp).lower() for term in inappropriate_terms)
                print(f"  ✅ Investment-appropriate language: {'No' if has_inappropriate else 'Yes'}")
                
                investment_terms = ["investment", "portfolio", "capital", "financial", "due diligence", "risk", "returns"]
                has_investment_terms = any(term in (cmi_exp + rbfs_exp + ias_exp).lower() for term in investment_terms)
                print(f"  ✅ Contains investment terminology: {'Yes' if has_investment_terms else 'No'}")
        
    except Exception as e:
        print(f"Error in behavioral data generation: {e}")
        import traceback
        traceback.print_exc()

def test_business_vs_investment_context():
    """Test that business and investment contexts generate different explanations."""
    print(f"\n{'='*80}")
    print("=== Testing Business vs Investment Context Differences ===")
    print(f"{'='*80}")
    
    # Same candidate, different contexts
    test_candidate = {
        "name": "Alex Johnson",
        "title": "CEO",
        "company": "Strategic Ventures",
        "email": "alex@strategicventures.com"
    }
    
    business_prompt = "Find CEOs interested in new CRM software"
    investment_prompt = "Find CEOs interested in climate investment opportunities"
    
    print("Business Context (CRM software):")
    business_candidates = enhance_behavioral_data_for_multiple_candidates([test_candidate], business_prompt)
    business_data = business_candidates[0]["behavioral_data"]
    print(f"CMI: {business_data['scores']['cmi']['explanation']}")
    print(f"RBFS: {business_data['scores']['rbfs']['explanation']}")
    print(f"IAS: {business_data['scores']['ias']['explanation']}")
    
    print(f"\nInvestment Context (Climate investments):")
    investment_candidates = enhance_behavioral_data_for_multiple_candidates([test_candidate], investment_prompt)
    investment_data = investment_candidates[0]["behavioral_data"]
    print(f"CMI: {investment_data['scores']['cmi']['explanation']}")
    print(f"RBFS: {investment_data['scores']['rbfs']['explanation']}")
    print(f"IAS: {investment_data['scores']['ias']['explanation']}")

if __name__ == "__main__":
    print("Testing Investment/Climate Search Context Handling")
    print("=" * 100)
    
    try:
        test_investment_context_detection()
        test_investment_behavioral_patterns()
        test_business_vs_investment_context()
        
        print(f"\n{'='*100}")
        print("Investment search testing completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()