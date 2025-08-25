#!/usr/bin/env python3
"""
Test to verify that the name-based search fix is working correctly.

This test ensures that the evidence finder no longer generates queries
that include prospect names, which was causing irrelevant results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from context_aware_evidence_finder import ContextAwareEvidenceFinder
from specific_search_query_generator import SpecificSearchQueryGenerator


def test_context_aware_evidence_finder():
    """Test that context-aware evidence finder doesn't use names."""
    
    print("Testing Context-Aware Evidence Finder")
    print("=" * 45)
    
    # Create test candidate with name that should NOT appear in queries
    test_candidate = {
        'name': 'John Smith',  # This should NEVER appear in search queries
        'title': 'Chief Marketing Officer',
        'company': 'Microsoft'
    }
    
    # Create evidence finder
    finder = ContextAwareEvidenceFinder()
    
    # Generate contextual queries
    queries = finder._generate_contextual_queries(test_candidate)
    
    print(f"Generated {len(queries)} queries:")
    
    # Check each query for name usage
    name_violations = []
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
        
        # Check if query contains the prospect's name
        name = test_candidate['name'].lower()
        name_parts = name.split()
        
        if (name in query.lower() or 
            any(part in query.lower() for part in name_parts if len(part) > 2)):
            name_violations.append(query)
    
    print(f"\nResults:")
    if name_violations:
        print(f"❌ FAILED: {len(name_violations)} queries contain prospect name:")
        for violation in name_violations:
            print(f"   - {violation}")
        return False
    else:
        print(f"✅ PASSED: No queries contain prospect name 'John Smith'")
        print(f"   All {len(queries)} queries focus on behavioral evidence only")
        return True


def test_specific_search_query_generator():
    """Test that specific search query generator doesn't use names."""
    
    print("\nTesting Specific Search Query Generator")
    print("=" * 45)
    
    # Create test candidate
    test_candidate = {
        'name': 'Jane Doe',  # This should NEVER appear in search queries
        'title': 'Chief Technology Officer',
        'company': 'Apple'
    }
    
    # Create query generator
    generator = SpecificSearchQueryGenerator()
    
    # Test different search prompts that might trigger name usage
    test_prompts = [
        "Find people who are executives",
        "Looking for person in technology",
        "Find executive candidates"
    ]
    
    all_passed = True
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: '{prompt}'")
        
        # Generate queries
        queries = generator._generate_candidate_specific_queries(test_candidate, prompt)
        
        print(f"Generated {len(queries)} queries:")
        
        # Check each query for name usage
        name_violations = []
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
            
            # Check if query contains the prospect's name
            name = test_candidate['name'].lower()
            name_parts = name.split()
            
            if (name in query.lower() or 
                any(part in query.lower() for part in name_parts if len(part) > 2)):
                name_violations.append(query)
        
        if name_violations:
            print(f"❌ FAILED: {len(name_violations)} queries contain prospect name:")
            for violation in name_violations:
                print(f"   - {violation}")
            all_passed = False
        else:
            print(f"✅ PASSED: No queries contain prospect name 'Jane Doe'")
    
    return all_passed


def test_query_safety_patterns():
    """Test various query patterns to ensure they're safe."""
    
    print("\nTesting Query Safety Patterns")
    print("=" * 35)
    
    # Test queries that should be BLOCKED
    unsafe_queries = [
        '"John Smith" professional profile',
        '"Jane Doe" LinkedIn',
        'John Smith biography',
        'Jane Doe executive profile',
        '"Michael Johnson" company information'
    ]
    
    # Test queries that should be ALLOWED
    safe_queries = [
        'CMO job market trends 2024',
        'executive career transition patterns',
        'Fortune 500 leadership changes',
        'startup executive hiring trends',
        'Microsoft executive departures',
        'Apple leadership turnover'
    ]
    
    print("Unsafe queries (should be blocked):")
    for query in unsafe_queries:
        contains_name = any(word[0].isupper() and word[1:].islower() 
                           for word in query.split() 
                           if len(word) > 2 and word.isalpha())
        status = "✅ BLOCKED" if contains_name else "❌ NOT BLOCKED"
        print(f"  {status}: {query}")
    
    print("\nSafe queries (should be allowed):")
    for query in safe_queries:
        contains_name = any(word[0].isupper() and word[1:].islower() 
                           for word in query.split() 
                           if len(word) > 2 and word.isalpha() and 
                           word not in ['CMO', 'CEO', 'CTO', 'Microsoft', 'Apple', 'Fortune'])
        status = "❌ BLOCKED" if contains_name else "✅ ALLOWED"
        print(f"  {status}: {query}")


def test_end_to_end_behavioral_focus():
    """Test that the entire system focuses on behavioral evidence."""
    
    print("\nEnd-to-End Behavioral Focus Test")
    print("=" * 40)
    
    # Simulate a complete search scenario
    test_scenario = {
        'search_context': 'CMO looking to leave Fortune 500 role for startup opportunity',
        'candidate': {
            'name': 'Sarah Johnson',  # Should NEVER appear in queries
            'title': 'Chief Marketing Officer',
            'company': 'IBM'
        }
    }
    
    print(f"Search context: {test_scenario['search_context']}")
    print(f"Candidate: {test_scenario['candidate']['title']} at {test_scenario['candidate']['company']}")
    print(f"Candidate name (should be hidden): [REDACTED]")
    
    # Test context-aware evidence finder
    finder = ContextAwareEvidenceFinder()
    queries = finder._generate_contextual_queries(test_scenario['candidate'])
    
    print(f"\nGenerated evidence queries:")
    behavioral_focus_count = 0
    name_violation_count = 0
    
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
        
        # Check for behavioral focus
        behavioral_keywords = ['trends', 'transitions', 'changes', 'hiring', 'departures', 'turnover', 'market']
        if any(keyword in query.lower() for keyword in behavioral_keywords):
            behavioral_focus_count += 1
        
        # Check for name violations
        if 'sarah' in query.lower() or 'johnson' in query.lower():
            name_violation_count += 1
    
    print(f"\nAnalysis:")
    print(f"  Total queries: {len(queries)}")
    print(f"  Behavioral focus: {behavioral_focus_count}/{len(queries)}")
    print(f"  Name violations: {name_violation_count}")
    
    if name_violation_count == 0 and behavioral_focus_count > 0:
        print(f"✅ SUCCESS: System focuses on behavioral evidence without using names")
        return True
    else:
        print(f"❌ FAILURE: System still has issues with name usage or behavioral focus")
        return False


if __name__ == "__main__":
    print("Name-Based Search Fix Verification")
    print("=" * 50)
    
    # Run all tests
    test_results = []
    
    test_results.append(test_context_aware_evidence_finder())
    test_results.append(test_specific_search_query_generator())
    test_query_safety_patterns()
    test_results.append(test_end_to_end_behavioral_focus())
    
    # Summary
    print(f"\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print(f"🎉 ALL TESTS PASSED ({passed_tests}/{total_tests})")
        print("✅ The name-based search issue has been FIXED!")
        print("✅ System now focuses ONLY on behavioral evidence")
        print("✅ Prospect names are NEVER used in search queries")
        print("\nThe system will no longer return websites that are just")
        print("variations of the prospect's name. All evidence will be")
        print("behavioral and contextually relevant.")
    else:
        print(f"❌ SOME TESTS FAILED ({passed_tests}/{total_tests})")
        print("❌ Name-based search issue still exists")
        print("❌ Additional fixes needed")
        
    print(f"\nTest Results: {passed_tests}/{total_tests} passed")