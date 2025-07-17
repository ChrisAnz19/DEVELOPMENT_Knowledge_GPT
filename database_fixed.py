#!/usr/bin/env python3
"""
Database utilities for Knowledge_GPT
Handles Supabase connection and operations for storing search results and candidate data
"""

import logging
import sys
import json
from datetime import datetime, timedelta
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from supabase_client import supabase
except Exception as e:
    logger.error(f"Failed to import supabase client: {e}")
    # Create a dummy supabase object to prevent import errors
    class DummySupabase:
        def table(self, name):
            return DummyTable()
    
    class DummyTable:
        def select(self, *args, **kwargs):
            return self
        def insert(self, data):
            return self
        def update(self, data):
            return self
        def delete(self):
            return self
        def eq(self, field, value):
            return self
        def order(self, field, desc=False):
            return self
        def limit(self, limit):
            return self
        def single(self):
            return self
        def execute(self):
            return DummyResult()
    
    class DummyResult:
        def __init__(self):
            self.data = []
            self.count = 0
    
    supabase = DummySupabase()

def store_search_to_database(search_data):
    """
    Store search data in the database, handling existing records appropriately.
    
    Args:
        search_data: Dictionary containing search data to store
        
    Returns:
        The ID of the inserted or updated record, or None if the operation failed
    """
    try:
        # Check if this is an update (has an ID) or a new record
        if "id" in search_data:
            # This is an update to an existing record
            search_id = search_data["id"]
            logger.info(f"Updating existing search record with ID: {search_id}")
            
            # Use the update method instead of insert for existing records
            res = supabase.table("searches").update(search_data).eq("id", search_id).execute()
            
            if hasattr(res, 'data') and res.data:
                logger.info(f"Successfully updated search record with ID: {search_id}")
                return search_id
            else:
                logger.error(f"Failed to update search record with ID: {search_id}")
                return None
        
        # Check if a record with this request_id already exists
        elif "request_id" in search_data:
            request_id = search_data["request_id"]
            existing_record = get_search_from_database(request_id)
            
            if existing_record:
                # Update the existing record
                search_id = existing_record["id"]
                logger.info(f"Found existing search record with ID: {search_id} for request_id: {request_id}")
                
                # Add the ID to the search_data for the update
                search_data["id"] = search_id
                
                # Use the update method for the existing record
                res = supabase.table("searches").update(search_data).eq("id", search_id).execute()
                
                if hasattr(res, 'data') and res.data:
                    logger.info(f"Successfully updated search record with ID: {search_id}")
                    return search_id
                else:
                    logger.error(f"Failed to update search record with ID: {search_id}")
                    return None
            else:
                # This is a new record, proceed with insert
                logger.info(f"Creating new search record for request_id: {request_id}")
                
                # Remove id if it exists to let the database assign one
                if "id" in search_data:
                    del search_data["id"]
                
                # Insert the new record
                res = supabase.table("searches").insert(search_data).execute()
                
                if hasattr(res, 'data') and res.data:
                    search_id = res.data[0].get('id')
                    logger.info(f"Successfully created new search record with ID: {search_id}")
                    return search_id
                else:
                    logger.error(f"Failed to create new search record")
                    return None
        else:
            # No request_id provided, cannot proceed
            logger.error("Cannot store search data: no request_id provided")
            return None
            
    except Exception as e:
        logger.error(f"Database operation error in store_search_to_database: {str(e)}")
        # Log the search_data for debugging (excluding sensitive fields)
        safe_data = {k: v for k, v in search_data.items() if k not in ["behavioral_data", "filters"]}
        logger.error(f"Failed search data: {safe_data}")
        return None

def get_search_from_database(request_id):
    """
    Get a search record from the database by request_id.
    
    Args:
        request_id: The unique request ID for the search
        
    Returns:
        Dictionary containing the search data, or None if not found
    """
    try:
        # Use a more explicit query structure to avoid 406 errors
        res = supabase.table("searches").select("id, request_id, status, prompt, filters, behavioral_data, created_at, completed_at").eq("request_id", request_id).execute()
        if hasattr(res, 'data') and res.data:
            return res.data[0]  # Return the first (and should be only) result
        return None
    except Exception as e:
        # If no rows found or other error, return None
        logger.error(f"Error in get_search_from_database for request_id {request_id}: {str(e)}")
        return None

def get_recent_searches_from_database(limit=10):
    """
    Get recent searches from the database.
    
    Args:
        limit: Maximum number of searches to return
        
    Returns:
        List of search records
    """
    try:
        res = supabase.table("searches").select("id, request_id, status, prompt, filters, behavioral_data, created_at, completed_at").order("created_at", desc=True).limit(limit).execute()
        return res.data if hasattr(res, 'data') else []
    except Exception as e:
        logger.error(f"Error in get_recent_searches_from_database: {str(e)}")
        return []

def store_people_to_database(search_id, people):
    """
    Store people data in the database, associated with a search.
    
    Args:
        search_id: The ID of the search these people are associated with
        people: List of people data to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Insert each person with the search_id, but only include fields that exist in the schema
        schema_fields = {
            'search_id', 'name', 'title', 'company', 'email', 'linkedin_url', 
            'profile_photo_url', 'location', 'accuracy', 'reasons', 
            'linkedin_profile', 'linkedin_posts'
        }
        
        filtered_people = []
        for person in people:
            filtered_person = {'search_id': search_id}
            for field in schema_fields:
                if field in person and person[field] is not None:
                    filtered_person[field] = person[field]
            filtered_people.append(filtered_person)
        
        if filtered_people:
            res = supabase.table("people").insert(filtered_people).execute()
            if hasattr(res, 'data') and res.data:
                logger.info(f"Successfully stored {len(filtered_people)} people for search_id: {search_id}")
                return True
            else:
                logger.error(f"Failed to store people for search_id: {search_id}")
                return False
        return True  # No people to store
    except Exception as e:
        logger.error(f"Error in store_people_to_database for search_id {search_id}: {str(e)}")
        return False

def get_people_for_search(search_id):
    """
    Get people associated with a search.
    
    Args:
        search_id: The ID of the search
        
    Returns:
        List of people records
    """
    try:
        res = supabase.table("people").select("id, search_id, name, title, company, email, linkedin_url, profile_photo_url, location, accuracy, reasons, linkedin_profile, linkedin_posts, created_at").eq("search_id", search_id).execute()
        return res.data if hasattr(res, 'data') else []
    except Exception as e:
        logger.error(f"Error in get_people_for_search for search_id {search_id}: {str(e)}")
        return []

def is_person_excluded_in_database(email, days=30):
    """
    Check if a person is excluded in the database.
    
    Args:
        email: The email of the person to check
        days: Number of days to look back
        
    Returns:
        True if the person is excluded, False otherwise
    """
    try:
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
    except Exception as e:
        logger.error(f"Error in is_person_excluded_in_database for email {email}: {str(e)}")
        return False

def delete_search_from_database(request_id):
    """
    Delete a search and its associated people from the database.
    
    Args:
        request_id: The unique request ID for the search
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Get the search ID first
        search_data = get_search_from_database(request_id)
        if search_data and "id" in search_data:
            search_id = search_data["id"]
            
            # Delete associated people first
            try:
                supabase.table("people").delete().eq("search_id", search_id).execute()
                logger.info(f"Deleted people for search_id: {search_id}")
            except Exception as e:
                logger.error(f"Error deleting people for search_id {search_id}: {str(e)}")
                # Continue with search deletion even if people deletion fails
            
            # Delete the search
            supabase.table("searches").delete().eq("request_id", request_id).execute()
            logger.info(f"Deleted search with request_id: {request_id}")
            return True
        else:
            logger.warning(f"Search not found for deletion: {request_id}")
            return False
    except Exception as e:
        logger.error(f"Error in delete_search_from_database for request_id {request_id}: {str(e)}")
        return False

def get_current_exclusions(days=30):
    """
    Return a list of people (email, name, company, created_at) in the people table within the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of exclusion records
    """
    try:
        now = datetime.now(pytz.UTC)
        cutoff = now - timedelta(days=days)
        res = supabase.table("people").select("email, name, company, created_at").execute()
        exclusions = []
        if hasattr(res, 'data') and res.data:
            for row in res.data:
                created_at = row.get("created_at")
                if created_at:
                    try:
                        created_at_dt = datetime.fromisoformat(created_at)
                        if created_at_dt > cutoff:
                            exclusions.append({
                                "email": row.get("email"),
                                "name": row.get("name"),
                                "company": row.get("company"),
                                "created_at": created_at
                            })
                    except Exception:
                        continue
        return exclusions
    except Exception as e:
        logger.error(f"Error in get_current_exclusions: {str(e)}")
        return []

if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing Database Connection...")
    
    # Test a simple query
    try:
        res = supabase.table("searches").select("id, request_id, status, prompt, created_at").limit(1).execute()
        if hasattr(res, 'data') and res.data:
            print(f"⏰ Current database time: {res.data[0]['created_at']}")
        else:
            print("No data found in searches table.")
    except Exception as e:
        print(f"Error testing database connection: {str(e)}")
        
    # Show table structure
    try:
        res = supabase.table("searches").select("id, request_id, status, prompt, created_at").limit(1).execute()
        if hasattr(res, 'data') and res.data:
            print("\n📋 Database Tables:")
            print(f"  - Table: searches")
            print(f"    - Columns: {list(res.data[0].keys())}")
        else:
            print("\n📋 Database Tables:")
            print("  - No data found in searches table to show columns.")
    except Exception as e:
        print(f"Error showing table structure: {str(e)}")