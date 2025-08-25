#!/usr/bin/env python3
"""
Simple test to verify that prospect names are NOT used in search queries.
"""

from search_query_generator import SearchQueryGenerator
from explanation_analyzer import ExplanationAnalyzer, SearchableClaim, ClaimType


def test_name_removal():
    """Test that search queries do not contain prospect names."""
    
    print("Testing Name Removal from Search Queries")
    print("=" * 45)
    
    # Create test claim that might trigger name usage
    claim = SearchableClaim(
        text="CMO looking to leave Fortune 500 role for startup opportunity",
        claim_type=ClaimType.GENERAL_ACTIVITY,
        entities={
            'roles': ['CMO', 'Chief Marketing Officer'],
            'companies': ['Fortune 500'],
            'industries': ['startup']
        },
        search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity'],
        priority=8,
        confidence=0.9
    )
    
    # Test with problematic names that should NEVER appear
    test_names = ['John Smith', 'Jane Doe', 'Michael Johnson', 'Sarah Wilson']
    
    generator = SearchQueryGenerator()
    
    for test_name in test_names:
        print(f"\nTesting with name: {test_name}")
        
        # Generate queries
        queries = generator.generate_queries(claim, candidate_id=f"test_{test_name.replace(' ', '_')}")
        
        name_violations = []
        name_parts = test_name.lower().split()
        
        for query in queries:
            query_text = query.query.lower()
            
            # Check if any part of the name appears in the query
            if (test_name.lower() in query_text or 
                any(part in query_text for part in name_parts if len(part) > 2)):
                name_violations.append(query.query)
        
        print(f"  Generated {len(queries)} queries")
        print(f"  Name violations: {len(name_violations)}")
        
        if name_violations:
            print(f"  ❌ VIOLATION: Found name in queries:")
            for violation in name_violations:
                print(f"    - {violation}")
            return False
        else:
            print(f"  ✅ SUCCESS: No names found in queries")
            
            # Show sample queries to verify they're behavioral
            print(f"  Sample queries:")
            for i, query in enumerate(queries[:3]):
                print(f"    {i+1}. {query.query}")
    
    return True


def test_behavioral_focus():
    """Test that queries focus on behavioral evidence."""
    
    print("\nTesting Behavioral Focus")
    print("=" * 25)
    
    # Create behavioral claim
    claim = SearchableClaim(
        text="Executive researching CRM solutions for enterprise deployment",
        claim_type=ClaimType.PRODUCT_EVALUATION,
        entities={
            'products': ['CRM'],
            'companies': ['Salesforce', 'HubSpot'],
            'activities': ['researching']
        },
        search_terms=['CRM', 'enterprise', 'deployment', 'solutions'],
        priority=9,
        confidence=0.9
    )
    
    generator = SearchQueryGenerator()
    queries = generator.generate_queries(claim)
    
    behavioral_indicators = [
        'pricing', 'comparison', 'features', 'evaluation', 'review',
        'enterprise', 'solution', 'platform', 'deployment', 'implementation'
    ]
    
    behavioral_count = 0
    for query in queries:
        query_text = query.query.lower()
        if any(indicator in query_text for indicator in behavioral_indicators):
            behavioral_count += 1
    
    print(f"Generated {len(queries)} queries")
    print(f"Behavioral queries: {behavioral_count}/{len(queries)}")
    
    if behavioral_count > 0:
        print("✅ SUCCESS: Queries focus on behavioral evidence")
        
        # Show sample behavioral queries
        print("Sample behavioral queries:")
        for i, query in enumerate(queries[:3]):
            print(f"  {i+1}. {query.query}")
        
        return True
    else:
        print("❌ FAILURE: No behavioral focus detected")
        return False


if __name__ == "__main__":
    print("Name Removal and Behavioral Focus Test")
    print("=" * 40)
    
    # Run tests
    name_test_passed = test_name_removal()
    behavioral_test_passed = test_behavioral_focus()
    
    print("\n" + "=" * 40)
    print("FINAL RESULTS:")
    
    if name_test_passed and behavioral_test_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Names are NOT used in search queries")
        print("✅ Queries focus on behavioral evidence")
        print("\nThe system will find relevant behavioral evidence")
        print("without returning irrelevant name-based websites.")
    else:
        print("❌ SOME TESTS FAILED")
        if not name_test_passed:
            print("❌ Names are still being used in queries")
        if not behavioral_test_passed:
            print("❌ Queries lack behavioral focus")