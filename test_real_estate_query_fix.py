#!/usr/bin/env python3
"""
Test Real Estate Query Fix.

This test verifies that the real estate query fix is working correctly.
"""

import asyncio
from context_aware_evidence_finder import ContextAwareEvidenceFinder


async def test_real_estate_query_fix():
    """Test that real estate queries are generated correctly."""
    print("Testing Real Estate Query Fix")
    print("=" * 50)
    
    # Initialize the context-aware evidence finder
    evidence_finder = ContextAwareEvidenceFinder(enable_diversity=True)
    
    # Set the search context with the problematic query
    search_prompt = "Find me an executive looking to buy a new home in Greenwich, Connecticut"
    evidence_finder.set_search_context(search_prompt)
    
    # Create a test candidate
    test_candidate = {
        'name': 'John Smith',
        'title': 'Chief Executive Officer',
        'company': 'TechCorp',
        'behavioral_data': {
            'behavioral_insight': 'Researched luxury real estate markets and high-end property investment opportunities'
        }
    }
    
    print(f"Search Prompt: {search_prompt}")
    print(f"Test Candidate: {test_candidate['name']} - {test_candidate['title']} at {test_candidate['company']}")
    print()
    
    # Generate contextual queries
    queries = evidence_finder._generate_contextual_queries(test_candidate)
    
    print(f"Generated {len(queries)} queries:")
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")
    
    print()
    
    # Analyze the queries
    real_estate_queries = []
    procurement_queries = []
    other_queries = []
    
    real_estate_keywords = ['home', 'house', 'real estate', 'property', 'greenwich', 'listing', 'buy house']
    procurement_keywords = ['procurement', 'purchasing', 'purchase executive', 'buy-in', 'procurement executive']
    
    for query in queries:
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in real_estate_keywords):
            real_estate_queries.append(query)
        elif any(keyword in query_lower for keyword in procurement_keywords):
            procurement_queries.append(query)
        else:
            other_queries.append(query)
    
    print("Query Analysis:")
    print(f"✅ Real Estate Queries: {len(real_estate_queries)}")
    for query in real_estate_queries:
        print(f"    - {query}")
    
    print(f"❌ Procurement Queries: {len(procurement_queries)}")
    for query in procurement_queries:
        print(f"    - {query}")
    
    print(f"⚪ Other Queries: {len(other_queries)}")
    for query in other_queries:
        print(f"    - {query}")
    
    print()
    
    # Determine success
    success = len(real_estate_queries) > 0 and len(procurement_queries) == 0
    
    if success:
        print("🎉 SUCCESS: Real estate query fix is working!")
        print("✅ Generated real estate-specific queries")
        print("✅ No procurement/purchasing queries generated")
        print("✅ System correctly understands 'executive buying home' context")
    else:
        print("❌ FAILURE: Real estate query fix needs more work")
        if len(real_estate_queries) == 0:
            print("❌ No real estate queries generated")
        if len(procurement_queries) > 0:
            print("❌ Still generating procurement queries")
    
    return success


async def main():
    """Run the real estate query fix test."""
    success = await test_real_estate_query_fix()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)