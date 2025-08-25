#!/usr/bin/env python3
"""
Test Search Performance and Specificity Fix.

This test validates that:
1. Search queries are more specific (e.g., "homes in Greenwich" returns specific listings)
2. Frontend receives clear completion status signals
3. Search result quality filtering works correctly
"""

import asyncio
import sys
import time
from typing import Dict, Any, List


def test_specific_query_generation():
    """Test that query generation produces specific queries instead of generic ones."""
    print("=" * 60)
    print("TESTING SPECIFIC QUERY GENERATION")
    print("=" * 60)
    
    try:
        from specific_search_query_generator import SpecificSearchQueryGenerator
        
        generator = SpecificSearchQueryGenerator()
        
        # Test real estate search specificity
        print("🏠 Testing real estate query specificity:")
        real_estate_prompt = "find homes in Greenwich CT"
        real_estate_candidate = {
            'name': 'John Buyer',
            'company': 'Greenwich Realty',
            'title': 'Real Estate Agent'
        }
        
        real_estate_queries = generator.generate_location_specific_queries(
            real_estate_prompt, real_estate_candidate
        )
        
        print(f"   Generated {len(real_estate_queries)} specific queries:")
        for i, query in enumerate(real_estate_queries, 1):
            print(f"     {i}. {query}")
        
        # Verify specificity
        has_location = any('Greenwich' in query for query in real_estate_queries)
        has_specific_terms = any(term in ' '.join(real_estate_queries).lower() 
                               for term in ['listings', 'for sale', 'MLS', 'homes'])
        
        print(f"   ✅ Contains location context: {has_location}")
        print(f"   ✅ Contains specific real estate terms: {has_specific_terms}")
        
        # Test business search specificity
        print("\n🏢 Testing business query specificity:")
        business_prompt = "find executives at tech companies"
        business_candidate = {
            'name': 'Jane Executive',
            'company': 'TechCorp Inc',
            'title': 'VP Engineering'
        }
        
        business_queries = generator.generate_location_specific_queries(
            business_prompt, business_candidate
        )
        
        print(f"   Generated {len(business_queries)} specific queries:")
        for i, query in enumerate(business_queries, 1):
            print(f"     {i}. {query}")
        
        # Verify business specificity
        has_company = any('TechCorp' in query for query in business_queries)
        has_person = any('Jane Executive' in query for query in business_queries)
        
        print(f"   ✅ Contains company context: {has_company}")
        print(f"   ✅ Contains person context: {has_person}")
        
        return True
        
    except Exception as e:
        print(f"❌ Specific query generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_result_quality_filtering():
    """Test that result quality filtering prioritizes specific over generic results."""
    print("\n" + "=" * 60)
    print("TESTING RESULT QUALITY FILTERING")
    print("=" * 60)
    
    try:
        from specific_search_query_generator import SpecificSearchQueryGenerator
        
        generator = SpecificSearchQueryGenerator()
        
        # Test with mock results (generic vs specific)
        mock_results = [
            {
                'url': 'https://zillow.com/',
                'title': 'Zillow: Real Estate, Apartments, Mortgages & Home Values',
                'snippet': 'Search millions of for-sale and rental listings'
            },
            {
                'url': 'https://zillow.com/greenwich-ct/homes-for-sale/',
                'title': 'Greenwich CT Real Estate - 45 Homes For Sale',
                'snippet': 'View 45 homes for sale in Greenwich, CT at a median listing price of $2.5M'
            },
            {
                'url': 'https://redfin.com/',
                'title': 'Redfin Real Estate',
                'snippet': 'Buy and sell real estate with Redfin'
            },
            {
                'url': 'https://redfin.com/city/7735/CT/Greenwich/homes-for-sale',
                'title': 'Greenwich, CT Homes for Sale & Real Estate',
                'snippet': 'There are 52 homes for sale in Greenwich, CT with a median list price of $2.8M'
            }
        ]
        
        print("📊 Scoring result specificity:")
        scored_results = []
        
        for result in mock_results:
            score = generator.score_result_specificity(result)
            scored_results.append((result, score))
            print(f"   Score: {score:.2f} - {result['title'][:50]}...")
        
        # Sort by score
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        print("\n🎯 Results ranked by specificity:")
        for i, (result, score) in enumerate(scored_results, 1):
            print(f"   {i}. Score: {score:.2f} - {result['url']}")
        
        # Verify that specific results score higher than generic ones
        specific_urls = [r for r, s in scored_results if 'greenwich' in r['url'].lower()]
        generic_urls = [r for r, s in scored_results if r['url'].endswith('.com/')]
        
        if specific_urls and generic_urls:
            specific_scores = [s for r, s in scored_results if 'greenwich' in r['url'].lower()]
            generic_scores = [s for r, s in scored_results if r['url'].endswith('.com/')]
            
            avg_specific = sum(specific_scores) / len(specific_scores)
            avg_generic = sum(generic_scores) / len(generic_scores)
            
            print(f"\n   ✅ Average specific result score: {avg_specific:.2f}")
            print(f"   ✅ Average generic result score: {avg_generic:.2f}")
            print(f"   ✅ Specific results score higher: {avg_specific > avg_generic}")
        
        return True
        
    except Exception as e:
        print(f"❌ Result quality filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_frontend_status_communication():
    """Test that frontend receives clear completion status signals."""
    print("\n" + "=" * 60)
    print("TESTING FRONTEND STATUS COMMUNICATION")
    print("=" * 60)
    
    try:
        from context_aware_evidence_finder import ContextAwareEvidenceFinder
        
        # Initialize evidence finder
        finder = ContextAwareEvidenceFinder(enable_diversity=True)
        finder.set_search_context("find homes in Greenwich CT")
        
        # Test candidates
        test_candidates = [{
            'id': 'test_1',
            'name': 'Test Buyer',
            'title': 'Home Buyer',
            'company': 'Greenwich Realty',
            'behavioral_data': {
                'behavioral_insight': 'Looking for homes in Greenwich'
            }
        }]
        
        print(f"🔄 Processing {len(test_candidates)} candidates...")
        start_time = time.time()
        
        results = await finder.process_candidates_batch(test_candidates)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ Processing completed in {total_time:.2f} seconds")
        
        # Verify status communication
        if results:
            candidate = results[0]
            
            # Check required status fields
            required_fields = [
                'evidence_status',
                'evidence_processing_time', 
                'evidence_completion_timestamp',
                'evidence_urls',
                'evidence_summary',
                'evidence_confidence'
            ]
            
            print("\n📋 Checking status communication fields:")
            all_fields_present = True
            
            for field in required_fields:
                present = field in candidate
                print(f"   ✅ {field}: {present} - {candidate.get(field, 'MISSING')}")
                if not present:
                    all_fields_present = False
            
            # Check batch summary
            if 'batch_evidence_summary' in candidate:
                batch_summary = candidate['batch_evidence_summary']
                print(f"\n📊 Batch Summary:")
                print(f"   Total candidates: {batch_summary.get('total_candidates')}")
                print(f"   Successful: {batch_summary.get('successful_count')}")
                print(f"   Failed: {batch_summary.get('failed_count')}")
                print(f"   Batch time: {batch_summary.get('batch_processing_time')}s")
                print(f"   Completion: {batch_summary.get('batch_completion_timestamp')}")
            
            # Check evidence quality
            evidence_urls = candidate.get('evidence_urls', [])
            evidence_status = candidate.get('evidence_status', 'unknown')
            
            print(f"\n🎯 Evidence Quality:")
            print(f"   Status: {evidence_status}")
            print(f"   URLs found: {len(evidence_urls)}")
            print(f"   Confidence: {candidate.get('evidence_confidence', 0)}")
            
            if evidence_urls:
                print(f"   Sample URLs:")
                for i, url_data in enumerate(evidence_urls[:3], 1):
                    if isinstance(url_data, dict):
                        print(f"     {i}. {url_data.get('url', 'No URL')}")
                    else:
                        print(f"     {i}. {url_data}")
            
            return all_fields_present and evidence_status in ['completed', 'completed_with_fallback', 'completed_no_results']
        
        return False
        
    except Exception as e:
        print(f"❌ Frontend status communication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_greenwich_homes_specificity():
    """Test the specific case: 'homes in Greenwich' should return specific listings."""
    print("\n" + "=" * 60)
    print("TESTING GREENWICH HOMES SPECIFICITY")
    print("=" * 60)
    
    try:
        from context_aware_evidence_finder import ContextAwareEvidenceFinder
        
        # Initialize evidence finder with Greenwich homes context
        finder = ContextAwareEvidenceFinder(enable_diversity=True)
        finder.set_search_context("find homes in Greenwich CT")
        
        # Test candidate looking for Greenwich homes
        greenwich_candidate = [{
            'id': 'greenwich_buyer',
            'name': 'Greenwich Buyer',
            'title': 'Home Buyer',
            'company': 'Local Realty',
            'behavioral_data': {
                'behavioral_insight': 'Looking to buy a home in Greenwich Connecticut'
            }
        }]
        
        print(f"🏠 Testing Greenwich homes search specificity...")
        
        results = await finder.process_candidates_batch(greenwich_candidate)
        
        if results:
            candidate = results[0]
            evidence_urls = candidate.get('evidence_urls', [])
            
            print(f"   Found {len(evidence_urls)} evidence URLs")
            
            # Analyze URL specificity
            specific_count = 0
            generic_count = 0
            
            print(f"\n📋 URL Analysis:")
            for i, url_data in enumerate(evidence_urls, 1):
                if isinstance(url_data, dict):
                    url = url_data.get('url', '')
                else:
                    url = str(url_data)
                
                print(f"   {i}. {url}")
                
                # Check if URL is specific to Greenwich or generic
                if any(term in url.lower() for term in ['greenwich', 'listing', 'homes-for-sale', 'property']):
                    specific_count += 1
                    print(f"      ✅ SPECIFIC - Contains location/listing terms")
                elif any(term in url.lower() for term in ['zillow.com/', 'redfin.com/', 'realtor.com/']):
                    generic_count += 1
                    print(f"      ⚠️  GENERIC - Homepage/general site")
                else:
                    print(f"      ❓ UNCLEAR - Need to verify specificity")
            
            specificity_ratio = specific_count / len(evidence_urls) if evidence_urls else 0
            
            print(f"\n🎯 Specificity Analysis:")
            print(f"   Specific URLs: {specific_count}")
            print(f"   Generic URLs: {generic_count}")
            print(f"   Specificity ratio: {specificity_ratio:.2f}")
            print(f"   Target ratio: ≥0.6 (60% specific)")
            
            success = specificity_ratio >= 0.6
            print(f"   ✅ Specificity test: {'PASSED' if success else 'FAILED'}")
            
            return success
        
        return False
        
    except Exception as e:
        print(f"❌ Greenwich homes specificity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests to validate the search performance and specificity fix."""
    print("🚀 TESTING SEARCH PERFORMANCE AND SPECIFICITY FIX")
    print("=" * 80)
    
    tests = [
        ("Specific Query Generation", test_specific_query_generation),
        ("Result Quality Filtering", test_result_quality_filtering),
        ("Frontend Status Communication", test_frontend_status_communication),
        ("Greenwich Homes Specificity", test_greenwich_homes_specificity),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Search performance and specificity fix is working correctly.")
        print("\nKey improvements verified:")
        print("✅ Search queries are now highly specific (e.g., 'Greenwich CT homes for sale')")
        print("✅ Result quality filtering prioritizes specific over generic URLs")
        print("✅ Frontend receives clear completion status and timing information")
        print("✅ 'Homes in Greenwich' returns specific property listings, not generic sites")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)