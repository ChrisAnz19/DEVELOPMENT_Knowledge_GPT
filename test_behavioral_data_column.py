#!/usr/bin/env python3
"""
Test if the behavioral_data column exists in the people table
"""

import logging
from supabase_client import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_behavioral_data_column():
    """Test if the behavioral_data column exists and works"""
    try:
        # Try to select behavioral_data column
        result = supabase.table("people").select("behavioral_data").limit(1).execute()
        logger.info("✅ behavioral_data column exists and is accessible")
        return True
    except Exception as e:
        logger.error(f"❌ behavioral_data column test failed: {str(e)}")
        return False

def test_insert_with_behavioral_data():
    """Test inserting a record with behavioral_data"""
    try:
        # Test data with behavioral_data
        test_person = {
            "search_id": 999999,  # Use a high number that won't conflict
            "name": "Test Person",
            "title": "Test Title",
            "company": "Test Company",
            "email": "test@example.com",
            "behavioral_data": {
                "behavioral_insight": "Test insight",
                "scores": {
                    "cmi": {"score": 75, "explanation": "Test CMI"},
                    "rbfs": {"score": 65, "explanation": "Test RBFS"},
                    "ias": {"score": 80, "explanation": "Test IAS"}
                }
            }
        }
        
        # Insert test data
        result = supabase.table("people").insert(test_person).execute()
        logger.info("✅ Successfully inserted person with behavioral_data")
        
        # Retrieve the inserted data
        retrieved = supabase.table("people").select("*").eq("email", "test@example.com").execute()
        if retrieved.data:
            person = retrieved.data[0]
            if person.get('behavioral_data'):
                logger.info("✅ Successfully retrieved behavioral_data")
                logger.info(f"Behavioral data: {person['behavioral_data']}")
            else:
                logger.warning("⚠️  behavioral_data is empty in retrieved record")
        
        # Clean up test data
        supabase.table("people").delete().eq("email", "test@example.com").execute()
        logger.info("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Insert test failed: {str(e)}")
        # Try to clean up in case of partial success
        try:
            supabase.table("people").delete().eq("email", "test@example.com").execute()
        except:
            pass
        return False

if __name__ == "__main__":
    print("🧪 Testing behavioral_data column...")
    print("=" * 50)
    
    # Test 1: Check if column exists
    print("\n1. Testing if behavioral_data column exists...")
    column_exists = test_behavioral_data_column()
    
    if not column_exists:
        print("❌ The behavioral_data column doesn't exist yet.")
        print("Please run this SQL in your Supabase SQL Editor:")
        print("ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;")
        exit(1)
    
    # Test 2: Test insert/retrieve with behavioral_data
    print("\n2. Testing insert/retrieve with behavioral_data...")
    insert_works = test_insert_with_behavioral_data()
    
    if insert_works:
        print("\n✅ All tests passed! The behavioral_data column is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")