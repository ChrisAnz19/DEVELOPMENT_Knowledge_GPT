"""
Optimized database utilities for Knowledge_GPT
Handles Supabase connection and operations for storing search results and candidate data
"""

import logging
import json
from typing import Dict, List, Any, Optional

# Configure logging - SIMPLIFIED
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

try:
    from supabase_client import supabase
except Exception:
    # Create a dummy supabase object to prevent import errors
    class DummySupabase:
        def table(self, name):
            return DummyTable()
    
    class DummyTable:
        def select(self, *args, **kwargs):
            return self
        def insert(self, data):
            return self
        def upsert(self, data):
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

def store_search_to_database(search_data: Dict[str, Any]) -> Optional[int]:
    """
    Store search data in the database with basic validation.
    
    Args:
        search_data: Search data to store
        
    Returns:
        Database ID of stored search or None if failed
    """
    try:
        # Basic validation
        if not isinstance(search_data, dict):
            logger.error("Search data must be a dictionary")
            return None
        
        # Ensure required fields
        required_fields = ['request_id', 'prompt', 'status']
        for field in required_fields:
            if field not in search_data or search_data[field] is None:
                logger.error(f"Missing required field: {field}")
                return None
        
        # Ensure prompt is not null
        if not search_data.get("prompt"):
            search_data["prompt"] = "No prompt provided"
        
        # Check if record exists by request_id
        existing_record = get_search_from_database(search_data["request_id"])
        
        if existing_record:
            # Update existing record
            search_data["id"] = existing_record["id"]
        elif "id" in search_data:
            # Don't specify ID for new records
            del search_data["id"]
        
        # Store in database
        res = supabase.table("searches").upsert(search_data).execute()
        
        if hasattr(res, 'data') and res.data:
            return res.data[0].get('id')
        return None
        
    except Exception as e:
        logger.error(f"Error storing search: {str(e)}")
        return None

def get_search_from_database(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Get search data from database by request_id.
    
    Args:
        request_id: The unique identifier for the search request
        
    Returns:
        Search data or None if not found
    """
    try:
        if not request_id or not isinstance(request_id, str):
            return None
        
        # Select all fields explicitly
        res = supabase.table("searches").select("*").eq("request_id", request_id).execute()
        
        if hasattr(res, 'data') and res.data:
            return res.data[0]
        return None
            
    except Exception as e:
        logger.error(f"Error getting search: {str(e)}")
        return None

def get_recent_searches_from_database(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent searches from database."""
    try:
        res = supabase.table("searches").select("*").order("created_at", desc=True).limit(limit).execute()
        return res.data if hasattr(res, 'data') else []
    except Exception as e:
        logger.error(f"Error getting recent searches: {str(e)}")
        return []

def delete_search_from_database(request_id: str) -> bool:
    """Delete search from database by request_id."""
    try:
        supabase.table("searches").delete().eq("request_id", request_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error deleting search: {str(e)}")
        return False

def store_people_to_database(search_id: int, people: List[Dict[str, Any]]) -> bool:
    """
    Store people data in the database.
    
    Args:
        search_id: Database ID of the search
        people: List of people data to store
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Define fields that exist in the schema
        schema_fields = {
            'search_id', 'name', 'title', 'company', 'email', 'linkedin_url', 
            'profile_photo_url', 'location', 'accuracy', 'reasons', 
            'linkedin_profile', 'linkedin_posts', 'behavioral_data'
        }
        
        for person in people:
            filtered_person = {'search_id': search_id}
            
            # Basic field mapping
            for field in schema_fields:
                if field in person and person[field] is not None:
                    # Handle special fields
                    if field in ['linkedin_profile', 'behavioral_data'] and isinstance(person[field], dict):
                        filtered_person[field] = json.dumps(person[field])
                    else:
                        filtered_person[field] = person[field]
            
            # Ensure company name is set
            if 'company' not in filtered_person and 'organization' in person:
                org = person['organization']
                if isinstance(org, dict) and 'name' in org:
                    filtered_person['company'] = org['name']
                elif isinstance(org, str):
                    filtered_person['company'] = org
            
            # Ensure LinkedIn URL is properly formatted
            if 'linkedin_url' in filtered_person and not filtered_person['linkedin_url'].startswith('http'):
                filtered_person['linkedin_url'] = f"https://{filtered_person['linkedin_url']}"
            
            # Store in database
            supabase.table("people").insert(filtered_person).execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Error storing people: {str(e)}")
        return False

def get_people_for_search(search_id: int) -> List[Dict[str, Any]]:
    """
    Get people data for a specific search.
    
    Args:
        search_id: Database ID of the search
        
    Returns:
        List of people data
    """
    try:
        res = supabase.table("people").select("*").eq("search_id", search_id).execute()
        
        people = []
        if hasattr(res, 'data'):
            for person in res.data:
                # Parse JSON strings
                for field in ['linkedin_profile', 'behavioral_data']:
                    if field in person and isinstance(person[field], str):
                        try:
                            person[field] = json.loads(person[field])
                        except json.JSONDecodeError:
                            person[field] = {}
                
                # Parse reasons if it's a string
                if 'reasons' in person and isinstance(person['reasons'], str):
                    try:
                        person['reasons'] = json.loads(person['reasons'])
                    except json.JSONDecodeError:
                        person['reasons'] = []
                
                people.append(person)
        
        return people
        
    except Exception as e:
        logger.error(f"Error getting people: {str(e)}")
        return []

def is_person_excluded_in_database(linkedin_url: str) -> bool:
    """Check if a person is excluded in the database."""
    try:
        res = supabase.table("exclusions").select("id").eq("linkedin_url", linkedin_url).execute()
        return bool(hasattr(res, 'data') and res.data)
    except Exception:
        return False

def get_current_exclusions() -> List[Dict[str, Any]]:
    """Get current exclusions from database."""
    try:
        res = supabase.table("exclusions").select("*").execute()
        return res.data if hasattr(res, 'data') else []
    except Exception:
        return []