#!/usr/bin/env python3
"""
Comprehensive test suite for the real web search system.

Tests SerpAPI, DuckDuckGo, and fallback functionality.
"""

import asyncio
import time
from typing import List

from web_search_engine import WebSearchEngine, WebSearchConfig, load_search_config
from search_query_generator import SearchQuery
from context_aware_evidence_finder import ContextAwareEvidenceFinder


async def test_serpapi_search():
    """Test SerpAPI integration with real API calls."""
    print("\n" + "="*60)
    print("TESTING SERPAPI SEARCH")
    print("="*60)
    
    config = load_search_config()
    if not config.serpapi_key:
        print("❌ No SerpAPI key found - skipping SerpAPI test")
        return False
    
    engine = WebSearchEngine(config)
    
    # Test query
    query = SearchQuery(
        query="real estate market trends 2024",
        expected_domains=[],
        page_types=["article", "news", "research"],
        priority=5,
        claim_support="test search",
        search_strategy="serpapi_test"
    )
    
    start_time = time.time()
    try:
        result = await engine._search_with_serpapi(query)
        end_time = time.time()
        
        print(f"✅ SerpAPI search completed in {end_time - start_time:.2f} seconds")
        print(f"   Success: {result.success}")
        print(f"   URLs found: {len(result.urls)}")
        print(f"   Error: {result.error_message}")
        
        if result.urls:
            print("   Sample URLs:")
            for i, url in enumerate(result.urls[:3]):
                print(f"     {i+1}. {url.title}")
                print(f"        {url.url}")
                print(f"        Domain: {url.domain}")
        
        return result.success and len(result.urls) > 0
        
    except Exception as e:
        print(f"❌ SerpAPI test failed: {e}")
        return False





async def test_fallback_system():
    """Test fallback URL generation."""
    print("\n" + "="*60)
    print("TESTING FALLBACK SYSTEM")
    print("="*60)
    
    # Create config with no API keys to force fallback
    config = WebSearchConfig(
        serpapi_key=None,
        enable_fallback_urls=True
    )
    engine = WebSearchEngine(config)
    
    # Test query
    query = SearchQuery(
        query="finance industry analysis",
        expected_domains=[],
        page_types=["article", "news", "research"],
        priority=5,
        claim_support="test search",
        search_strategy="fallback_test"
    )
    
    start_time = time.time()
    try:
        result = await engine._execute_search(query)
        end_time = time.time()
        
        print(f"✅ Fallback search completed in {end_time - start_time:.2f} seconds")
        print(f"   Success: {result.success}")
        print(f"   URLs found: {len(result.urls)}")
        print(f"   Source: {result.search_metadata.get('source', 'unknown')}")
        
        if result.urls:
            print("   Fallback URLs:")
            for i, url in enumerate(result.urls[:3]):
                print(f"     {i+1}. {url.title}")
                print(f"        {url.url}")
                print(f"        Domain: {url.domain}")
        
        return result.success and len(result.urls) > 0
        
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False


async def test_search_strategy():
    """Test the complete search strategy (SerpAPI -> DuckDuckGo -> Fallback)."""
    print("\n" + "="*60)
    print("TESTING COMPLETE SEARCH STRATEGY")
    print("="*60)
    
    config = load_search_config()
    engine = WebSearchEngine(config)
    
    # Test queries
    queries = [
        SearchQuery(
            query="artificial intelligence trends 2024",
            expected_domains=[],
            page_types=["article", "news", "research"],
            priority=5,
            claim_support="test search",
            search_strategy="strategy_test"
        ),
        SearchQuery(
            query="sustainable energy investments",
            expected_domains=[],
            page_types=["article", "news", "research"],
            priority=5,
            claim_support="test search",
            search_strategy="strategy_test"
        )
    ]
    
    start_time = time.time()
    try:
        results = await engine.search_for_evidence(queries)
        end_time = time.time()
        
        print(f"✅ Strategy test completed in {end_time - start_time:.2f} seconds")
        print(f"   Queries processed: {len(results)}")
        
        success_count = 0
        total_urls = 0
        
        for i, result in enumerate(results):
            print(f"\n   Query {i+1}: {result.query.query[:50]}...")
            print(f"     Success: {result.success}")
            print(f"     URLs: {len(result.urls)}")
            print(f"     Source: {result.search_metadata.get('source', 'unknown')}")
            
            if result.success:
                success_count += 1
            total_urls += len(result.urls)
            
            if result.urls:
                print(f"     Sample URL: {result.urls[0].url}")
        
        print(f"\n   Overall Success Rate: {success_count}/{len(results)} queries")
        print(f"   Total URLs Found: {total_urls}")
        
        return success_count > 0 and total_urls > 0
        
    except Exception as e:
        print(f"❌ Strategy test failed: {e}")
        return False


async def test_context_aware_integration():
    """Test context-aware evidence finder with real search."""
    print("\n" + "="*60)
    print("TESTING CONTEXT-AWARE INTEGRATION")
    print("="*60)
    
    finder = ContextAwareEvidenceFinder(enable_diversity=True)
    finder.set_search_context("Find executives at technology companies considering AI investments")
    
    # Test candidate
    test_candidate = {
        'id': 'test_1',
        'name': 'Sarah Johnson',
        'title': 'CTO',
        'company': 'TechCorp Inc',
        'behavioral_data': {
            'behavioral_insight': 'Sarah is evaluating AI investment opportunities and researching market trends'
        }
    }
    
    start_time = time.time()
    try:
        result = await finder._process_candidate_with_context(test_candidate)
        end_time = time.time()
        
        print(f"✅ Context-aware test completed in {end_time - start_time:.2f} seconds")
        
        evidence_urls = result.get('evidence_urls', [])
        print(f"   Evidence URLs found: {len(evidence_urls)}")
        print(f"   Evidence confidence: {result.get('evidence_confidence', 0)}")
        print(f"   Evidence summary: {result.get('evidence_summary', 'None')}")
        
        if evidence_urls:
            print("   Sample evidence URLs:")
            for i, url_data in enumerate(evidence_urls[:3]):
                if isinstance(url_data, dict):
                    print(f"     {i+1}. {url_data.get('title', 'No title')}")
                    print(f"        {url_data.get('url', 'No URL')}")
                else:
                    print(f"     {i+1}. {url_data}")
        
        return len(evidence_urls) > 0
        
    except Exception as e:
        print(f"❌ Context-aware test failed: {e}")
        return False


async def run_all_tests():
    """Run all web search tests."""
    print("🚀 STARTING COMPREHENSIVE WEB SEARCH TESTS")
    print("="*80)
    
    tests = [
        ("SerpAPI Search", test_serpapi_search),
        ("Fallback System", test_fallback_system),
        ("Search Strategy", test_search_strategy),
        ("Context-Aware Integration", test_context_aware_integration)
    ]
    
    results = {}
    total_start = time.time()
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    total_end = time.time()
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    print(f"Total execution time: {total_end - total_start:.2f} seconds")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Web search system is working correctly.")
    elif passed > 0:
        print("⚠️  PARTIAL SUCCESS: Some search methods are working.")
    else:
        print("💥 ALL TESTS FAILED: Web search system needs attention.")
    
    return passed, total


if __name__ == '__main__':
    asyncio.run(run_all_tests())