#!/usr/bin/env python3
"""
Database utilities for Knowledge_GPT
Handles Supabase connection and operations for storing search results and candidate data
"""

import logging
from supabase_client import supabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def store_search_to_database(search_data):
    return supabase.table("searches").insert(search_data).execute()

def get_search_from_database(request_id):
    res = supabase.table("searches").select("*").eq("request_id", request_id).single().execute()
    return res.data

def get_recent_searches_from_database(limit=10):
    res = supabase.table("searches").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data

def delete_search_from_database(request_id):
    return supabase.table("searches").delete().eq("request_id", request_id).execute()

def add_person_exclusion_to_database(email, name, company=None, reason="Previously processed"):
    exclusion = {
        "email": email,
        "name": name,
        "company": company,
        "reason": reason
    }
    return supabase.table("people_exclusions").insert(exclusion).execute()

def is_person_excluded_in_database(email):
    res = supabase.table("people_exclusions").select("*").eq("email", email).execute()
    return bool(res.data)

def get_excluded_people_from_database():
    res = supabase.table("people_exclusions").select("*").execute()
    return res.data

def cleanup_expired_exclusions_in_database():
    # Not supported directly; would need a custom function or manual cleanup
    return 0

if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing Database Connection...")
    
    # The init_database function is removed as per the new_code.
    # The direct calls to the new functions are added.
    
    # Test a simple query
    res = supabase.table("searches").select("*").limit(1).execute()
    if res.data:
        print(f"⏰ Current database time: {res.data[0]['created_at']}")
    else:
        print("No data found in searches table.")
        
    # Show table structure
    res = supabase.table("searches").select("*").limit(1).execute()
    if res.data:
        print("\n📋 Database Tables:")
        print(f"  - Table: searches")
        print(f"    - Columns: {list(res.data[0].keys())}")
    else:
        print("\n📋 Database Tables:")
        print("  - No data found in searches table to show columns.")
    
    # The original db_manager.disconnect() is removed as per the new_code.
    # The supabase client does not have a direct disconnect method like psycopg2.
    # The supabase client manages its own connection pool. 