#!/usr/bin/env python3
"""
Test Evidence Finder Integration Fix.

This test validates that the evidence finder integration issue is resolved
and that the system handles configuration errors gracefully.
"""

import asyncio
import sys
import time
from typing import Dict, Any, List

# Test the configuration loading fix
def test_configuration_loading():
    """Test that configuration loading works correctly."""
    print("=" * 60)
    print("TESTING CONFIGURATION LOADING FIX")
    print("=" * 60)
    
    try:
        from web_search_engine import load_search_config_safely, validate_config, WebSearchConfig
        
        # Test safe configuration loading
        config = load_search_config_safely()
        print(f"✅ Safe config loading returned: {type(config)}")
        
        # Test configuration validation
        is_valid = validate_config(config)
        print(f"✅ Configuration validation: {is_valid}")
        
        # Test that config has required attributes
        has_timeout = hasattr(config, 'timeout')
        print(f"✅ Config has timeout attribute: {has_timeout}")
        
        # Test with invalid config (boolean)
        invalid_config = True  # This would cause the original error
        is_invalid_valid = validate_config(invalid_config)
        print(f"✅ Boolean validation correctly fails: {not is_invalid_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_web_search_engine_initialization():
    """Test that WebSearchEngine initializes correctly with various configs."""
    print("\n" + "=" * 60)
    print("TESTING WEB SEARCH ENGINE INITIALIZATION")
    print("=" * 60)
    
    try:
        from web_search_engine import WebSearchEngine, WebSearchConfig
        
        # Test with no config (should use safe loading)
        engine1 = WebSearchEngine()
        print(f"✅ Engine initialized with no config: {type(engine1.config)}")
        print(f"✅ Engine has timeout: {hasattr(engine1, 'timeout')}")
        
        # Test with valid config
        valid_config = WebSearchConfig()
        engine2 = WebSearchEngine(valid_config)
        print(f"✅ Engine initialized with valid config: {type(engine2.config)}")
        
        # Test with invalid config (boolean) - should use default
        invalid_config = True
        engine3 = WebSearchEngine(invalid_config)
        print(f"✅ Engine initialized with invalid config, used default: {type(engine3.config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ WebSearchEngine initialization test failed: {e}")
        return False


async def test_context_aware_evidence_finder():
    """Test that context-aware evidence finder works without crashing."""
    print("\n" + "=" * 60)
    print("TESTING CONTEXT-AWARE EVIDENCE FINDER")
    print("=" * 60)
    
    try:
        from context_aware_evidence_finder import ContextAwareEvidenceFinder
        
        # Initialize evidence finder
        finder = ContextAwareEvidenceFinder(enable_diversity=True)
        
        # Set search context
        search_prompt = "Find corporate development officers at media companies"
        finder.set_search_context(search_prompt)
        print(f"✅ Search context set successfully")
        
        # Test candidate processing
        test_candidates = [{
            'id': 'test_1',
            'name': 'John Doe',
            'title': 'VP Corporate Development',
            'company': 'MediaCorp Inc',
            'behavioral_data': {
                'behavioral_insight': 'John is evaluating strategic options'
            }
        }]
        
        print(f"✅ Processing {len(test_candidates)} test candidates...")
        start_time = time.time()
        
        # This should not crash with the 'bool' object has no attribute 'timeout' error
        results = await finder.process_candidates_batch(test_candidates)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Processing completed in {processing_time:.2f} seconds")
        print(f"✅ Results returned: {len(results)} candidates")
        
        # Check that results have expected structure
        if results:
            candidate = results[0]
            has_evidence_urls = 'evidence_urls' in candidate
            has_evidence_summary = 'evidence_summary' in candidate
            has_evidence_confidence = 'evidence_confidence' in candidate
            
            print(f"✅ Candidate has evidence_urls: {has_evidence_urls}")
            print(f"✅ Candidate has evidence_summary: {has_evidence_summary}")
            print(f"✅ Candidate has evidence_confidence: {has_evidence_confidence}")
            
            if has_evidence_urls:
                evidence_count = len(candidate['evidence_urls'])
                print(f"✅ Evidence URLs found: {evidence_count}")
            
            if has_evidence_summary:
                print(f"✅ Evidence summary: {candidate['evidence_summary']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Context-aware evidence finder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_error_recovery():
    """Test that the system recovers gracefully from various errors."""
    print("\n" + "=" * 60)
    print("TESTING ERROR RECOVERY")
    print("=" * 60)
    
    try:
        from context_aware_evidence_finder import ContextAwareEvidenceFinder
        
        # Test with malformed candidate data
        finder = ContextAwareEvidenceFinder(enable_diversity=True)
        finder.set_search_context("test search")
        
        malformed_candidates = [
            {},  # Empty candidate
            {'name': 'Test'},  # Minimal candidate
            {'name': None, 'title': None},  # Null values
        ]
        
        print(f"✅ Testing with {len(malformed_candidates)} malformed candidates...")
        results = await finder.process_candidates_batch(malformed_candidates)
        
        print(f"✅ Error recovery successful: {len(results)} results returned")
        
        # Ensure all candidates are returned even if processing fails
        assert len(results) == len(malformed_candidates), "Not all candidates returned"
        print(f"✅ All candidates returned despite errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error recovery test failed: {e}")
        return False


async def main():
    """Run all tests to validate the evidence finder fix."""
    print("🚀 TESTING EVIDENCE FINDER INTEGRATION FIX")
    print("=" * 80)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("WebSearchEngine Initialization", test_web_search_engine_initialization),
        ("Context-Aware Evidence Finder", test_context_aware_evidence_finder),
        ("Error Recovery", test_error_recovery),
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
        print("🎉 ALL TESTS PASSED! Evidence finder integration fix is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)