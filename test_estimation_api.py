#!/usr/bin/env python3
"""
Test the estimation API end-to-end
"""

import os
import json
import requests
import time
import sys

# Load secrets into environment
try:
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    for key, value in secrets.items():
        os.environ[key] = value
    print("✅ Loaded secrets into environment")
except Exception as e:
    print(f"❌ Failed to load secrets: {e}")
    sys.exit(1)

# Import after setting environment variables
sys.path.append('.')
from simple_estimation import estimate_people_count

def test_estimation_function():
    """Test the estimation function directly"""
    print("\n1️⃣ Testing estimation function...")
    
    try:
        result = estimate_people_count("Find me a director of marketing in NY looking for a new CRM")
        print(f"✅ Estimation result: {result}")
        return result.get("estimated_count")
    except Exception as e:
        print(f"❌ Estimation function failed: {e}")
        return None

def test_database_storage():
    """Test storing estimation in database"""
    print("\n2️⃣ Testing database storage...")
    
    from database import store_search_to_database, get_search_from_database
    import uuid
    from datetime import datetime, timezone
    
    test_request_id = str(uuid.uuid4())
    estimated_count = 1337
    
    search_data = {
        "request_id": test_request_id,
        "status": "completed",
        "prompt": "Test estimation storage",
        "estimated_count": estimated_count,
        "result_estimation": {
            "estimated_count": estimated_count,
            "confidence": "high",
            "reasoning": "Test estimation for API",
            "limiting_factors": []
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Store
    search_id = store_search_to_database(search_data)
    if not search_id:
        print("❌ Failed to store search data")
        return False
    
    # Retrieve
    retrieved = get_search_from_database(test_request_id)
    if not retrieved:
        print("❌ Failed to retrieve search data")
        return False
    
    if retrieved.get("estimated_count") == estimated_count:
        print(f"✅ Database storage working: {estimated_count}")
        return True
    else:
        print(f"❌ Wrong estimated_count: {retrieved.get('estimated_count')}")
        return False

if __name__ == "__main__":
    print("🧪 Testing estimation API functionality...")
    
    # Test estimation function
    estimated_count = test_estimation_function()
    if not estimated_count:
        print("💥 Estimation function test failed")
        sys.exit(1)
    
    # Test database storage
    if not test_database_storage():
        print("💥 Database storage test failed")
        sys.exit(1)
    
    print("\n🎉 All estimation tests passed!")
    print("\n📋 Summary:")
    print("✅ Estimation function works")
    print("✅ Database storage works")
    print("✅ Ready for API integration")
    
    print(f"\n🔍 The frontend should now see estimated_count: {estimated_count} in API responses")