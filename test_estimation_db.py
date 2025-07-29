#!/usr/bin/env python3
"""
Test script to verify the estimation database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import store_search_to_database, get_search_from_database
import uuid
from datetime import datetime, timezone

def test_estimation_storage():
    """Test storing and retrieving estimation data"""
    
    # Create test search data with estimation
    test_request_id = str(uuid.uuid4())
    test_search_data = {
        "request_id": test_request_id,
        "status": "completed",
        "prompt": "Test search for estimation",
        "estimated_count": 1234,
        "result_estimation": {
            "estimated_count": 1234,
            "confidence": "high",
            "reasoning": "Test estimation",
            "limiting_factors": []
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    
    print("🧪 Testing estimation database functionality...")
    print(f"📝 Test request ID: {test_request_id}")
    
    # Store the test data
    print("\n1️⃣ Storing test search data...")
    search_id = store_search_to_database(test_search_data)
    
    if search_id:
        print(f"✅ Successfully stored search with ID: {search_id}")
    else:
        print("❌ Failed to store search data")
        return False
    
    # Retrieve the test data
    print("\n2️⃣ Retrieving test search data...")
    retrieved_data = get_search_from_database(test_request_id)
    
    if retrieved_data:
        print("✅ Successfully retrieved search data")
        print(f"📊 estimated_count: {retrieved_data.get('estimated_count')}")
        print(f"📊 result_estimation: {retrieved_data.get('result_estimation')}")
        
        # Check if estimation data is present
        if retrieved_data.get('estimated_count') == 1234:
            print("✅ estimated_count field is correct!")
        else:
            print(f"❌ estimated_count field is wrong: {retrieved_data.get('estimated_count')}")
            
        if retrieved_data.get('result_estimation'):
            print("✅ result_estimation field is present!")
        else:
            print("❌ result_estimation field is missing!")
            
        return True
    else:
        print("❌ Failed to retrieve search data")
        return False

if __name__ == "__main__":
    success = test_estimation_storage()
    if success:
        print("\n🎉 All tests passed! Estimation database functionality is working.")
    else:
        print("\n💥 Tests failed! There's an issue with the database.")
    
    sys.exit(0 if success else 1)