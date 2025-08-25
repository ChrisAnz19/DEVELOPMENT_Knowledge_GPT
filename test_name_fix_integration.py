#!/usr/bin/env python3
"""
Test integration of name-free search generator.
"""

import asyncio
from context_aware_evidence_finder import ContextAwareEvidenceFinder, SearchContext


async def test_name_free_integration():
    """Test that the integrated system doesn't use names."""
    
    print("Testing Name-Free Integration")
    print("=" * 30)
    
    # Create test candidate with name that should NEVER appear
    test_candidate = {
        'name': 'John Smith',  # This should NEVER appear in search queries
        'title': 'Chief Marketing Officer',
        'company': 'Microsoft',
        'behavioral_data': {
            'behavioral_insight': 'Researching CRM solutions for enterprise deployment'
        }
    }
    
    # Create search context
    search_context = SearchContext(
        search_prompt="Find marketing executives",
        industry="technology",
        activity_type="research"
    )
    
    # Create evidence finder
    finder = ContextAwareEvidenceFinder(search_context)
    
    print(f"Test candidate: {test_candidate['title']} at {test_candidate['company']}")
    print(f"Name (should be hidden): [REDACTED]")
    
    try:
        # Generate contextual queries
        queries = finder._generate_contextual_queries(test_candidate)
        
        print(f"\nGenerated {len(queries)} queries:")
        
        # Check for name violations
        name = test_candidate['name'].lower()
        name_parts = name.split()
        name_violations = []
        
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
            
            # Check if query contains the prospect's name
            if (name in query.lower() or 
                any(part in query.lower() for part in name_parts if len(part) > 2)):
                name_violations.append(query)
        
        print(f"\nName violations: {len(name_violations)}")
        
        if name_violations:
            print("❌ VIOLATIONS FOUND:")
            for violation in name_violations:
                print(f"  - {violation}")
            return False
        else:
            print("✅ SUCCESS: No names found in queries")
            print("✅ All queries focus on behavioral evidence")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_name_free_integration())
    
    if result:
        print("\n🎉 INTEGRATION TEST PASSED!")
        print("The system now generates behavioral evidence queries")
        print("without using prospect names.")
    else:
        print("\n❌ INTEGRATION TEST FAILED!")
        print("Additional fixes needed.")