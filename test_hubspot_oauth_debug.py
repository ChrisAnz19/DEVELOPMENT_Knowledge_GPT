#!/usr/bin/env python3
"""
Debug script to test HubSpot OAuth endpoint and identify the JSON parsing issue
"""

import asyncio
import httpx
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_oauth_endpoint():
    """Test the OAuth endpoint with various scenarios"""
    
    base_url = "http://localhost:8000"
    
    # Test data
    test_cases = [
        {
            "name": "Valid request format",
            "data": {
                "code": "test_code_123",
                "redirect_uri": "https://example.com/callback"
            }
        },
        {
            "name": "Empty code",
            "data": {
                "code": "",
                "redirect_uri": "https://example.com/callback"
            }
        },
        {
            "name": "Missing redirect_uri",
            "data": {
                "code": "test_code_123"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for test_case in test_cases:
            print(f"\n=== Testing: {test_case['name']} ===")
            
            try:
                response = await client.post(
                    f"{base_url}/api/hubspot/oauth/token",
                    json=test_case['data'],
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Raw Response: {response.text}")
                
                # Try to parse as JSON
                try:
                    json_response = response.json()
                    print(f"Parsed JSON: {json.dumps(json_response, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Decode Error: {e}")
                    print(f"Response text length: {len(response.text)}")
                    print(f"Response text repr: {repr(response.text)}")
                
            except Exception as e:
                print(f"❌ Request Error: {e}")

async def test_health_endpoint():
    """Test the health endpoint first"""
    print("=== Testing Health Endpoint ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get("http://localhost:8000/api/hubspot/oauth/health")
            print(f"Health Status: {response.status_code}")
            print(f"Health Response: {response.text}")
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"Health Data: {json.dumps(health_data, indent=2)}")
                return True
            else:
                print("❌ Health check failed")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

async def main():
    """Main test function"""
    print("🔍 HubSpot OAuth Debug Test")
    print("=" * 50)
    
    # First test health
    health_ok = await test_health_endpoint()
    
    if not health_ok:
        print("\n❌ Server not responding properly. Make sure the API is running on localhost:8000")
        return
    
    # Then test OAuth endpoint
    await test_oauth_endpoint()
    
    print("\n" + "=" * 50)
    print("Debug test completed")

if __name__ == "__main__":
    asyncio.run(main())