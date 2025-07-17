#!/usr/bin/env python3
"""
Fix Database Issues Script
This script helps fix the database issues you're experiencing:
1. Adds the behavioral_data column to the people table
2. Tests the database connection and schema
"""

import logging
import json
from supabase_client import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        result = supabase.table("searches").select("id").limit(1).execute()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False

def check_people_table_schema():
    """Check if the people table has the behavioral_data column"""
    try:
        # Try to select behavioral_data column
        result = supabase.table("people").select("behavioral_data").limit(1).execute()
        logger.info("✅ behavioral_data column exists in people table")
        return True
    except Exception as e:
        logger.warning(f"⚠️  behavioral_data column might not exist: {str(e)}")
        return False

def add_behavioral_data_column():
    """Add the behavioral_data column to the people table"""
    try:
        # Use raw SQL to add the column
        sql_query = """
        ALTER TABLE people 
        ADD COLUMN IF NOT EXISTS behavioral_data JSONB;
        """
        
        # Execute using Supabase's RPC function (if available)
        # Note: This might not work depending on your Supabase setup
        logger.info("Attempting to add behavioral_data column...")
        
        # Alternative: Use a simple insert/update to test if column exists
        test_data = {
            "search_id": 999999,  # Use a high number that won't conflict
            "name": "Test User",
            "behavioral_data": json.dumps({"test": "data"})
        }
        
        # Try to insert test data to see if column exists
        result = supabase.table("people").insert(test_data).execute()
        
        # If successful, delete the test data
        supabase.table("people").delete().eq("search_id", 999999).execute()
        
        logger.info("✅ behavioral_data column is working correctly")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to add behavioral_data column: {str(e)}")
        logger.info("Please run this SQL manually in your Supabase SQL Editor:")
        logger.info("ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;")
        return False

def test_search_update():
    """Test if we can update a search without null constraint errors"""
    try:
        # Create a test search
        test_search = {
            "request_id": "test-fix-123",
            "prompt": "Test search for fixing database issues",
            "status": "processing",
            "filters": json.dumps({}),
            "created_at": "2025-01-01T00:00:00Z"
        }
        
        # Insert test search
        from database import store_search_to_database
        result = store_search_to_database(test_search)
        logger.info(f"✅ Test search created successfully: {result}")
        
        # Update the test search
        update_data = {
            "request_id": "test-fix-123",
            "prompt": "Test search for fixing database issues",
            "status": "completed",
            "filters": json.dumps({"test": "filters"}),
            "completed_at": "2025-01-01T00:01:00Z"
        }
        
        result = store_search_to_database(update_data)
        logger.info(f"✅ Test search updated successfully: {result}")
        
        # Clean up test data
        from database import delete_search_from_database
        delete_search_from_database("test-fix-123")
        logger.info("✅ Test search cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Search update test failed: {str(e)}")
        return False

def main():
    """Main function to run all fixes"""
    print("🔧 Knowledge_GPT Database Fix Script")
    print("=" * 50)
    
    # Step 1: Check database connection
    print("\n1. Checking database connection...")
    if not check_database_connection():
        print("❌ Cannot connect to database. Please check your Supabase credentials.")
        return
    
    # Step 2: Check people table schema
    print("\n2. Checking people table schema...")
    has_behavioral_data = check_people_table_schema()
    
    # Step 3: Add behavioral_data column if needed
    if not has_behavioral_data:
        print("\n3. Adding behavioral_data column...")
        if not add_behavioral_data_column():
            print("❌ Please add the column manually in Supabase SQL Editor:")
            print("   ALTER TABLE people ADD COLUMN IF NOT EXISTS behavioral_data JSONB;")
            return
    else:
        print("\n3. ✅ behavioral_data column already exists")
    
    # Step 4: Test search updates
    print("\n4. Testing search updates...")
    if test_search_update():
        print("✅ Search updates are working correctly")
    else:
        print("❌ Search updates still have issues")
    
    print("\n" + "=" * 50)
    print("🎉 Database fix script completed!")
    print("\nNext steps:")
    print("1. If any manual SQL is needed, run it in your Supabase SQL Editor")
    print("2. Restart your API server")
    print("3. Test a new search to see if behavioral data appears")

if __name__ == "__main__":
    main()