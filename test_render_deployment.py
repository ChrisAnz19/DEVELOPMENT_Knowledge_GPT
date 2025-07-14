#!/usr/bin/env python3
"""
Test script for Render deployment
Replace YOUR_RENDER_URL with your actual Render service URL
"""

import requests
import json
import time
import sys

# Replace with your actual Render service URL
RENDER_URL = "https://your-service-name.onrender.com"

def test_render_deployment():
    """Test the deployed API on Render"""
    print("🧪 Testing Render Deployment")
    print("=" * 40)
    print(f"🌐 API URL: {RENDER_URL}")
    print()
    
    # Test 1: Health check
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{RENDER_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Create search
    print("\n🔍 Testing search creation...")
    try:
        search_data = {
            "prompt": "Find CEOs at large software companies in San Francisco",
            "max_candidates": 2,
            "include_linkedin": True,
            "include_posts": True
        }
        
        response = requests.post(
            f"{RENDER_URL}/api/search",
            json=search_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            request_id = data['request_id']
            print(f"✅ Search created: {request_id}")
        else:
            print(f"❌ Search creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Search creation error: {e}")
        return False
    
    # Test 3: Poll for results
    print(f"\n⏳ Polling for search completion...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{RENDER_URL}/api/search/{request_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"   Attempt {attempt + 1}/{max_attempts}: {data['status']}")
                
                if data['status'] == 'completed':
                    print("✅ Search completed successfully!")
                    print(f"📊 Found {len(data.get('candidates', []))} candidates")
                    if data.get('behavioral_data'):
                        print("📈 Behavioral data generated")
                    return True
                elif data['status'] == 'failed':
                    print(f"❌ Search failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                print(f"   Attempt {attempt + 1}/{max_attempts}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   Attempt {attempt + 1}/{max_attempts}: Error - {e}")
        
        time.sleep(2)
    
    print("⏰ Search timed out")
    return False

def main():
    """Main test function"""
    if "your-service-name" in RENDER_URL:
        print("❌ Please update RENDER_URL in the script with your actual Render service URL")
        print("   Example: https://knowledge-gpt-api.onrender.com")
        sys.exit(1)
    
    success = test_render_deployment()
    
    if success:
        print("\n🎉 Render deployment test passed!")
        print("✅ Your API is working correctly on Render")
        print("🔗 You can now connect your Bolt frontend to this API")
    else:
        print("\n❌ Render deployment test failed")
        print("🔍 Check the logs in your Render dashboard for more details")
        sys.exit(1)

if __name__ == "__main__":
    main() 