#!/usr/bin/env python3
"""
Test script to verify diagnostic logging is working for LinkedIn data fix.
This script will test the get_people_for_search function with diagnostic logging.
"""

import sys
import os
import logging

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging to see the diagnostic messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_diagnostic_logging():
    """Test the diagnostic logging functionality."""
    try:
        # Import the database module
        from database import get_people_for_search, get_recent_searches_from_database
        
        print("Testing diagnostic logging for LinkedIn data fix...")
        print("=" * 60)
        
        # Get recent searches to find a search_id to test with
        print("1. Getting recent searches to find test data...")
        searches = get_recent_searches_from_database(limit=5)
        
        if not searches:
            print("No searches found in database. Please run a search first.")
            return
        
        print(f"Found {len(searches)} recent searches")
        
        # Find a search that has candidates
        test_search_id = None
        for search in searches:
            search_id = search.get('id')
            if search_id:
                print(f"Testing with search_id: {search_id} (request_id: {search.get('request_id')})")
                test_search_id = search_id
                break
        
        if not test_search_id:
            print("No valid search_id found in recent searches.")
            return
        
        print("\n2. Testing get_people_for_search with diagnostic logging...")
        print("-" * 50)
        
        # This should trigger our diagnostic logging
        candidates = get_people_for_search(test_search_id)
        
        print(f"\n3. Results summary:")
        print(f"   - Retrieved {len(candidates) if candidates else 0} candidates")
        
        if candidates:
            print(f"   - First candidate: {candidates[0].get('name', 'Unknown')}")
            
            # Check for LinkedIn data fields
            linkedin_fields = ['company', 'linkedin_url', 'profile_photo_url']
            for field in linkedin_fields:
                value = candidates[0].get(field)
                has_value = bool(value and str(value).strip())
                print(f"   - {field}: {'✓' if has_value else '✗'}")
        
        print("\n4. Diagnostic logging test completed!")
        print("Check the log output above for [DIAGNOSTIC] messages.")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_diagnostic_logging()