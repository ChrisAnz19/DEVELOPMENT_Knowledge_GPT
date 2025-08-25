#!/usr/bin/env python3
"""
Verify and fix the database schema for evidence columns.
"""

import os
import sys
from supabase import create_client, Client

def get_supabase_client():
    """Get Supabase client from environment or secrets."""
    try:
        # Try environment variables first
        url = os.environ.get('SUPABASE_URL')
        key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not url or not key:
            # Try loading from secrets.json
            import json
            with open('api/secrets.json', 'r') as f:
                secrets = json.load(f)
                url = secrets.get('SUPABASE_URL')
                key = secrets.get('SUPABASE_ANON_KEY')
        
        if not url or not key:
            raise ValueError("Supabase credentials not found")
            
        return create_client(url, key)
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

def check_evidence_columns():
    """Check if evidence columns exist in the people table."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Try to select evidence columns - if they don't exist, this will fail
        result = supabase.table("people").select("evidence_urls, evidence_summary, evidence_confidence").limit(1).execute()
        print("✅ Evidence columns exist in database schema")
        return True
    except Exception as e:
        print(f"❌ Evidence columns missing from database schema: {e}")
        return False

def add_evidence_columns():
    """Add evidence columns to the people table."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Read the SQL migration file
        with open('add_evidence_columns.sql', 'r') as f:
            sql = f.read()
        
        print("🔧 Adding evidence columns to database...")
        
        # Execute the SQL migration
        # Note: Supabase Python client doesn't support raw SQL execution
        # This would need to be run manually in the Supabase SQL editor
        print("⚠️  Please run the following SQL in your Supabase SQL editor:")
        print("=" * 60)
        print(sql)
        print("=" * 60)
        
        return True
    except Exception as e:
        print(f"❌ Error preparing migration: {e}")
        return False

def test_evidence_storage():
    """Test storing and retrieving evidence data."""
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Test data
        test_evidence = [
            {"url": "https://example.com/test", "title": "Test Evidence", "relevance_score": 0.8}
        ]
        
        test_person = {
            "search_id": 999999,  # Use a test search ID
            "name": "Test Person",
            "evidence_urls": json.dumps(test_evidence),
            "evidence_summary": "Test evidence summary",
            "evidence_confidence": 0.8
        }
        
        # Try to insert test data
        result = supabase.table("people").insert(test_person).execute()
        
        if result.data:
            person_id = result.data[0]['id']
            print(f"✅ Successfully stored test evidence data (ID: {person_id})")
            
            # Clean up test data
            supabase.table("people").delete().eq("id", person_id).execute()
            print("✅ Cleaned up test data")
            return True
        else:
            print("❌ Failed to store test evidence data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing evidence storage: {e}")
        return False

if __name__ == '__main__':
    print("🔍 Verifying Evidence Schema")
    print("=" * 40)
    
    # Check if columns exist
    columns_exist = check_evidence_columns()
    
    if not columns_exist:
        print("\n🚨 Evidence columns are missing!")
        add_evidence_columns()
    else:
        print("\n🧪 Testing evidence storage...")
        import json
        test_success = test_evidence_storage()
        
        if test_success:
            print("\n🎉 Evidence schema is working correctly!")
        else:
            print("\n❌ Evidence storage test failed")