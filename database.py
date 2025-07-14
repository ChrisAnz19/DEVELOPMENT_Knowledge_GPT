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
    # Insert search and return the new search id
    res = supabase.table("searches").insert(search_data).execute()
    if hasattr(res, 'data') and res.data:
        # Return the inserted search's id
        return res.data[0].get('id')
    return None

def get_search_from_database(request_id):
    res = supabase.table("searches").select("*").eq("request_id", request_id).single().execute()
    return res.data

def get_recent_searches_from_database(limit=10):
    res = supabase.table("searches").select("*").order("created_at", desc=True).limit(limit).execute()
    return res.data

def store_people_to_database(search_id, people):
    # Insert each person with the search_id
    for person in people:
        person["search_id"] = search_id
    if people:
        supabase.table("people").insert(people).execute()

def get_people_for_search(search_id):
    res = supabase.table("people").select("*").eq("search_id", search_id).execute()
    return res.data

def is_person_excluded_in_database(email, days=30):
    # Check if a person with this email exists in the people table within the last N days
    from datetime import datetime, timedelta
    import pytz
    now = datetime.now(pytz.UTC)
    cutoff = now - timedelta(days=days)
    res = supabase.table("people").select("created_at").eq("email", email).execute()
    if hasattr(res, 'data') and res.data:
        for row in res.data:
            created_at = row.get("created_at")
            if created_at:
                try:
                    created_at_dt = datetime.fromisoformat(created_at)
                    if created_at_dt > cutoff:
                        return True
                except Exception:
                    continue
    return False

def delete_search_from_database(request_id):
    # Delete search and cascade to people
    supabase.table("searches").delete().eq("request_id", request_id).execute()
    return True

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