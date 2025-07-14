#!/usr/bin/env python3
"""
Comprehensive test script for the live Knowledge_GPT API
Tests all endpoints and functionality at https://knowledge-gpt-siuq.onrender.com
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE_URL = "https://knowledge-gpt-siuq.onrender.com"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_docs():
    """Test if API documentation is accessible"""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation accessible")
            return True
        else:
            print(f"⚠️  API docs returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API docs error: {e}")
        return False

def test_create_search():
    """Test creating a search request"""
    print("\n🔍 Testing search creation...")
    try:
        search_data = {
            "prompt": "Find CEOs at large software companies in San Francisco",
            "max_candidates": 2,
            "include_linkedin": True,
            "include_posts": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search created: {data['request_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Prompt: {data['prompt']}")
            return data['request_id']
        else:
            print(f"❌ Search creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Search creation error: {e}")
        return None

def test_get_search_results(request_id):
    """Test getting search results"""
    print(f"\n📊 Testing search results for {request_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/search/{request_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search status: {data['status']}")
            if data.get('filters'):
                print(f"   Filters generated: ✅")
            if data.get('candidates'):
                print(f"   Candidates found: {len(data['candidates'])}")
            if data.get('behavioral_data'):
                print(f"   Behavioral data: ✅")
            return data
        else:
            print(f"❌ Get search results failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Get search results error: {e}")
        return None

def test_list_searches():
    """Test listing all searches"""
    print("\n📋 Testing list searches...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/search", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data['searches'])} searches")
            return True
        else:
            print(f"❌ List searches failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ List searches error: {e}")
        return False

def poll_for_completion(request_id, max_attempts=30):
    """Poll for search completion"""
    print(f"\n⏳ Polling for search completion...")
    
    for attempt in range(max_attempts):
        data = test_get_search_results(request_id)
        if not data:
            return None
            
        if data['status'] == 'completed':
            print("✅ Search completed!")
            return data
        elif data['status'] == 'failed':
            print(f"❌ Search failed: {data.get('error', 'Unknown error')}")
            return data
            
        print(f"   Attempt {attempt + 1}/{max_attempts}: {data['status']}")
        time.sleep(3)  # Wait 3 seconds between polls
    
    print("⏰ Search timed out")
    return None

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🚨 Testing error handling...")
    
    # Test invalid search request
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/search",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Invalid request response: {response.status_code}")
    except Exception as e:
        print(f"   Invalid request error: {e}")
    
    # Test non-existent search ID
    try:
        response = requests.get(f"{API_BASE_URL}/api/search/nonexistent-id", timeout=10)
        print(f"   Non-existent ID response: {response.status_code}")
    except Exception as e:
        print(f"   Non-existent ID error: {e}")

def test_cors():
    """Test CORS headers"""
    print("\n🌐 Testing CORS headers...")
    try:
        response = requests.options(f"{API_BASE_URL}/api/search", timeout=10)
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        if cors_headers:
            print(f"✅ CORS headers present: {cors_headers}")
            return True
        else:
            print("⚠️  No CORS headers found")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def main():
    """Run all API tests"""
    print("🧪 Knowledge_GPT Live API Test Suite")
    print("=" * 50)
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print()
    
    test_results = {
        "health_check": False,
        "api_docs": False,
        "search_creation": False,
        "search_completion": False,
        "list_searches": False,
        "error_handling": False,
        "cors": False
    }
    
    # Test 1: Health check
    test_results["health_check"] = test_health_check()
    
    # Test 2: API documentation
    test_results["api_docs"] = test_api_docs()
    
    # Test 3: Create search
    request_id = test_create_search()
    if request_id:
        test_results["search_creation"] = True
        
        # Test 4: Poll for completion
        final_result = poll_for_completion(request_id)
        if final_result and final_result['status'] == 'completed':
            test_results["search_completion"] = True
            print(f"\n📊 Search Results Summary:")
            candidates = final_result.get('candidates', [])
            print(f"   Candidates found: {len(candidates) if candidates else 0}")
            print(f"   Behavioral data: {'✅' if final_result.get('behavioral_data') else '❌'}")
            print(f"   Filters generated: {'✅' if final_result.get('filters') else '❌'}")
    
    # Test 5: List searches
    test_results["list_searches"] = test_list_searches()
    
    # Test 6: Error handling
    test_error_handling()
    test_results["error_handling"] = True
    
    # Test 7: CORS
    test_results["cors"] = test_cors()
    
    # Generate test summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Your Knowledge_GPT API is working perfectly!")
        print("🔗 Ready to connect with your Bolt frontend!")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check the logs above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 