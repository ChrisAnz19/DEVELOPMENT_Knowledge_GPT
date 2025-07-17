#!/usr/bin/env python3
"""
Debug the search update issue
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from database import store_search_to_database, get_search_from_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_search_update_issue():
    """Test the search update process to identify the null prompt issue"""
    try:
        # Step 1: Create a test search (simulating the initial creation)
        test_request_id = f"debug-{str(uuid.uuid4())[:8]}"
        initial_search = {
            "request_id": test_request_id,
            "status": "processing",
            "prompt": "Find marketing directors in San Francisco",
            "filters": json.dumps({}),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        logger.info(f"Creating initial search with prompt: '{initial_search['prompt']}'")
        search_id = store_search_to_database(initial_search)
        logger.info(f"✅ Created search with ID: {search_id}")
        
        # Step 2: Retrieve the search (simulating what happens in process_search)
        existing_record = get_search_from_database(test_request_id)
        logger.info(f"Retrieved record: id={existing_record.get('id')}, prompt='{existing_record.get('prompt')}', status={existing_record.get('status')}")
        
        # Step 3: Simulate the update process (what happens in process_search)
        filters = {"organization_filters": {}, "person_filters": {}}
        prompt = "Find marketing directors in San Francisco"  # This should match the original
        
        # Debug: Check what we're getting from the existing record
        logger.info(f"Existing record prompt: '{existing_record.get('prompt')}'")
        logger.info(f"Current prompt parameter: '{prompt}'")
        
        # Ensure we have a valid prompt - use existing or fallback to current
        final_prompt = existing_record.get("prompt") or prompt
        if not final_prompt:
            logger.error(f"No valid prompt found! Existing: {existing_record.get('prompt')}, Current: {prompt}")
            final_prompt = "Search query not available"  # Emergency fallback

        # Update search data while preserving required fields
        update_data = {
            "id": existing_record.get("id"),
            "request_id": existing_record.get("request_id", test_request_id),
            "prompt": final_prompt,  # Use the validated prompt
            "status": "completed",
            "filters": json.dumps(filters),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Update data: id={update_data['id']}, prompt='{update_data['prompt']}', status={update_data['status']}")
        
        # Step 4: Try to update the search
        result = store_search_to_database(update_data)
        logger.info(f"✅ Updated search successfully: {result}")
        
        # Step 5: Verify the update
        updated_record = get_search_from_database(test_request_id)
        logger.info(f"Updated record: id={updated_record.get('id')}, prompt='{updated_record.get('prompt')}', status={updated_record.get('status')}")
        
        # Step 6: Clean up
        from supabase_client import supabase
        supabase.table("searches").delete().eq("request_id", test_request_id).execute()
        logger.info("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        # Try to clean up
        try:
            if 'test_request_id' in locals():
                from supabase_client import supabase
                supabase.table("searches").delete().eq("request_id", test_request_id).execute()
        except:
            pass
        return False

if __name__ == "__main__":
    print("🔍 Debugging Search Update Issue...")
    print("=" * 50)
    
    success = test_search_update_issue()
    
    if success:
        print("\n✅ Search update test passed!")
    else:
        print("\n❌ Search update test failed!")