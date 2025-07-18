#!/usr/bin/env python3
"""
Test script to verify API diagnostic logging is working for LinkedIn data fix.
This script will test the API endpoint with diagnostic logging.
"""

import sys
import os
import asyncio
import logging

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see the diagnostic messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_api_diagnostic_logging():
    """Test the API diagnostic logging functionality."""
    try:
        # Import required modules
        from database import get_recent_searches_from_database
        from api.main import get_search_result
        
        print("Testing API diagnostic logging for LinkedIn data fix...")
        print("=" * 60)
        
        # Get recent searches to find a request_id to test with
        print("1. Getting recent searches to find test data...")
        searches = get_recent_searches_from_database(limit=5)
        
        if not searches:
            print("No searches found in database. Please run a search first.")
            return
        
        print(f"Found {len(searches)} recent searches")
        
        # Find a search that has a request_id
        test_request_id = None
        for search in searches:
            request_id = search.get('request_id')
            if request_id:
                print(f"Testing with request_id: {request_id}")
                test_request_id = request_id
                break
        
        if not test_request_id:
            print("No valid request_id found in recent searches.")
            return
        
        print("\n2. Testing API endpoint with diagnostic logging...")
        print("-" * 50)
        
        # This should trigger our API diagnostic logging
        result = await get_search_result(test_request_id)
        
        print(f"\n3. API Results summary:")
        print(f"   - Status: {result.get('status')}")
        print(f"   - Candidates: {len(result.get('candidates', []))}")
        
        if result.get('candidates'):
            candidate = result['candidates'][0]
            print(f"   - First candidate: {candidate.get('name', 'Unknown')}")
            
            # Check for LinkedIn data fields in API response
            linkedin_fields = ['company', 'linkedin_url', 'profile_photo_url']
            for field in linkedin_fields:
                value = candidate.get(field)
                has_value = bool(value and str(value).strip())
                print(f"   - {field}: {'✓' if has_value else '✗'} ({repr(value)})")
        
        print("\n4. API diagnostic logging test completed!")
        print("Check the log output above for [DIAGNOSTIC] messages.")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_diagnostic_logging())