#!/usr/bin/env python3
"""
Simple API test script for Knowledge_GPT
Tests the basic API endpoints to ensure they're working
"""

import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
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
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search created: {data['request_id']}")
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
        response = requests.get(f"{API_BASE_URL}/api/search/{request_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search status: {data['status']}")
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
        response = requests.get(f"{API_BASE_URL}/api/search")
        
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
        time.sleep(2)
    
    print("⏰ Search timed out")
    return None

def main():
    """Run all API tests"""
    print("🧪 Knowledge_GPT API Test Suite")
    print("=" * 40)
    
    # Test 1: Health check
    if not test_health_check():
        print("❌ API is not running. Please start the API first.")
        sys.exit(1)
    
    # Test 2: Create search
    request_id = test_create_search()
    if not request_id:
        print("❌ Failed to create search. Exiting.")
        sys.exit(1)
    
    # Test 3: List searches
    test_list_searches()
    
    # Test 4: Poll for completion
    final_result = poll_for_completion(request_id)
    
    if final_result and final_result['status'] == 'completed':
        print("\n🎉 All tests passed!")
        print(f"📊 Found {len(final_result.get('candidates', []))} candidates")
        if final_result.get('behavioral_data'):
            print("📈 Behavioral data generated")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 