#!/usr/bin/env python3
"""
Test to verify if our current behavioral reason generation system is working
"""

from assess_and_return import select_top_candidates
from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
import json

def test_current_behavioral_system():
    """Test the current system to see what it actually generates"""
    
    print("TESTING CURRENT BEHAVIORAL SYSTEM")
    print("="*80)
    
    # Create test candidate data similar to what the API would use
    test_candidates = [
        {
            "name": "Test CMO",
            "title": "Chief Marketing Officer",
            "company": "Test Company",
            "email": "test@example.com",
            "organization_name": "Test Company"
        }
    ]
    
    test_prompt = "Find me CMOs interested in CRM solutions"
    
    print(f"Test Prompt: {test_prompt}")
    print(f"Test Candidate: {test_candidates[0]['name']} - {test_candidates[0]['title']}")
    print("-" * 80)
    
    # Test 1: Direct behavioral enhancement (what the API uses)
    print("\n1. Testing enhance_behavioral_data_for_multiple_candidates():")
    try:
        enhanced_candidates = enhance_behavioral_data_for_multiple_candidates(test_candidates, test_prompt)
        
        if enhanced_candidates and len(enhanced_candidates) > 0:
            candidate = enhanced_candidates[0]
            if "behavioral_data" in candidate:
                insight = candidate["behavioral_data"].get("behavioral_insight", "No insight generated")
                print(f"   Behavioral Insight: {insight}")
                
                # Check for problematic patterns
                problematic_patterns = ["downloaded", "whitepaper", "webinar", "attended", "joined", "visited"]
                found_patterns = [p for p in problematic_patterns if p.lower() in insight.lower()]
                
                if found_patterns:
                    print(f"   ❌ PROBLEMATIC PATTERNS FOUND: {found_patterns}")
                else:
                    print(f"   ✅ No problematic patterns detected")
            else:
                print(f"   ❌ No behavioral_data in candidate")
        else:
            print(f"   ❌ No enhanced candidates returned")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 2: Direct assessment (fallback path)
    print("\n2. Testing select_top_candidates():")
    try:
        top_candidates = select_top_candidates(test_prompt, test_candidates)
        
        if top_candidates and len(top_candidates) > 0:
            candidate = top_candidates[0]
            reasons = candidate.get("reasons", [])
            print(f"   Generated {len(reasons)} reasons:")
            
            for i, reason in enumerate(reasons, 1):
                print(f"     {i}. {reason}")
                
                # Check for problematic patterns
                problematic_patterns = ["downloaded", "whitepaper", "webinar", "attended", "joined", "visited"]
                found_patterns = [p for p in problematic_patterns if p.lower() in reason.lower()]
                
                if found_patterns:
                    print(f"        ❌ PROBLEMATIC PATTERNS: {found_patterns}")
        else:
            print(f"   ❌ No top candidates returned")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    # Test 3: Check if we're using the right functions
    print("\n3. Function verification:")
    try:
        from assess_and_return import _generate_realistic_behavioral_reasons
        reasons = _generate_realistic_behavioral_reasons("Chief Marketing Officer", test_prompt, 0)
        print(f"   _generate_realistic_behavioral_reasons() returned {len(reasons)} reasons:")
        
        for i, reason in enumerate(reasons, 1):
            print(f"     {i}. {reason}")
            
            # Check for problematic patterns
            problematic_patterns = ["downloaded", "whitepaper", "webinar", "attended", "joined", "visited"]
            found_patterns = [p for p in problematic_patterns if p.lower() in reason.lower()]
            
            if found_patterns:
                print(f"        ❌ PROBLEMATIC PATTERNS: {found_patterns}")
            else:
                print(f"        ✅ Clean reason")
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
    
    print("\n" + "="*80)
    print("If you see problematic patterns above, the issue is in our code.")
    print("If you see clean patterns above, the production system is using different code.")
    print("="*80)

if __name__ == "__main__":
    test_current_behavioral_system()