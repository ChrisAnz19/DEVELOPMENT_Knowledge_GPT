import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

try:
    from supabase_client import supabase
except Exception:
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
    try:
        if not isinstance(search_data, dict):
            return None
        
        required_fields = ['request_id', 'prompt', 'status']
        for field in required_fields:
            if field not in search_data or search_data[field] is None:
                return None
        
        if not search_data.get("prompt"):
            search_data["prompt"] = "No prompt provided"
        
        existing_record = get_search_from_database(search_data["request_id"])
        
        if existing_record:
            search_data["id"] = existing_record["id"]
        elif "id" in search_data:
            del search_data["id"]
        
        res = supabase.table("searches").upsert(search_data).execute()
        
        if hasattr(res, 'data') and res.data:
            stored_id = res.data[0].get('id')
            return stored_id
        return None
        
    except Exception as e:
        return None

def get_search_from_database(request_id: str) -> Optional[Dict[str, Any]]:
    try:
        if not request_id or not isinstance(request_id, str):
            return None
        
        res = supabase.table("searches").select("*").eq("request_id", request_id).execute()
        
        if hasattr(res, 'data') and res.data:
            search_data = res.data[0]
            return search_data
        return None
            
    except Exception as e:
        return None

def get_recent_searches_from_database(limit: int = 10) -> List[Dict[str, Any]]:
    try:
        res = supabase.table("searches").select("*").order("created_at", desc=True).limit(limit).execute()
        searches = res.data if hasattr(res, 'data') else []
        
        # Ensure all searches have the required fields for backward compatibility
        for search in searches:
            if isinstance(search, dict):
                # Add estimated_count if missing
                if "estimated_count" not in search or search["estimated_count"] is None:
                    search["estimated_count"] = None
                
                # Add result_estimation if missing
                if "result_estimation" not in search or search["result_estimation"] is None:
                    search["result_estimation"] = None
                
                # Add error field if missing
                if "error" not in search:
                    search["error"] = None
                
                # Ensure status is valid
                if "status" not in search or search["status"] not in ["processing", "completed", "failed"]:
                    # Determine status based on other fields
                    if search.get("error"):
                        search["status"] = "failed"
                    elif search.get("completed_at"):
                        search["status"] = "completed"
                    else:
                        search["status"] = "processing"
        
        return searches
    except Exception:
        return []

def delete_search_from_database(request_id: str) -> bool:
    try:
        supabase.table("searches").delete().eq("request_id", request_id).execute()
        return True
    except Exception:
        return False

def store_people_to_database(search_id: int, people: List[Dict[str, Any]]) -> bool:
    try:
        print(f"[Database] Attempting to store {len(people)} people for search_id {search_id}")
        
        schema_fields = {
            'search_id', 'name', 'title', 'company', 'email', 'linkedin_url', 
            'profile_photo_url', 'location', 'accuracy', 'reasons', 
            'linkedin_profile', 'linkedin_posts', 'behavioral_data'
        }
        
        stored_count = 0
        for i, person in enumerate(people):
            try:
                filtered_person = {'search_id': search_id}
                
                for field in schema_fields:
                    if field in person and person[field] is not None:
                        if field in ['linkedin_profile', 'behavioral_data'] and isinstance(person[field], dict):
                            filtered_person[field] = json.dumps(person[field])
                        else:
                            filtered_person[field] = person[field]
                
                if 'company' not in filtered_person and 'organization' in person:
                    org = person['organization']
                    if isinstance(org, dict) and 'name' in org:
                        filtered_person['company'] = org['name']
                    elif isinstance(org, str):
                        filtered_person['company'] = org
                
                if 'linkedin_url' in filtered_person and not filtered_person['linkedin_url'].startswith('http'):
                    filtered_person['linkedin_url'] = f"https://{filtered_person['linkedin_url']}"
                
                # Store the person in the database
                result = supabase.table("people").insert(filtered_person).execute()
                stored_count += 1
                print(f"[Database] Successfully stored person {i+1}: {filtered_person.get('name', 'Unknown')}")
                
            except Exception as e:
                print(f"[Database] Failed to store person {i+1}: {person.get('name', 'Unknown')} - Error: {str(e)}")
                continue
            
            # Don't automatically add to exclusions - let users decide
            # Commenting out automatic exclusion to allow candidates to appear in multiple searches
            # if 'linkedin_url' in filtered_person and filtered_person['linkedin_url']:
            #     try:
            #         if not is_person_excluded_in_database(filtered_person['linkedin_url']):
            #             exclusion_data = {
            #                 'linkedin_url': filtered_person['linkedin_url'],
            #                 'name': filtered_person.get('name', ''),
            #                 'reason': 'Previously returned in search results',
            #                 'created_at': datetime.now(timezone.utc).isoformat() if 'datetime' in globals() else None
            #             }
            #             supabase.table("exclusions").insert(exclusion_data).execute()
            #     except Exception:
            #         pass
        
        print(f"[Database] Successfully stored {stored_count} out of {len(people)} people")
        return stored_count > 0
        
    except Exception as e:
        print(f"[Database] Failed to store people: {str(e)}")
        return False

def get_people_for_search(search_id: int) -> List[Dict[str, Any]]:
    try:
        res = supabase.table("people").select("*").eq("search_id", search_id).execute()
        
        people = []
        print(f"[DEBUG] Database query for search_id {search_id} returned {len(res.data) if hasattr(res, 'data') and res.data else 0} people")
        if hasattr(res, 'data'):
            for person in res.data:
                for field in ['linkedin_profile', 'behavioral_data']:
                    if field in person and isinstance(person[field], str):
                        try:
                            person[field] = json.loads(person[field])
                        except json.JSONDecodeError:
                            person[field] = {}
                
                if 'reasons' in person and isinstance(person['reasons'], str):
                    try:
                        person['reasons'] = json.loads(person['reasons'])
                    except json.JSONDecodeError:
                        person['reasons'] = []
                
                people.append(person)
        
        return people
        
    except Exception:
        return []

def is_person_excluded_in_database(linkedin_url: str) -> bool:
    try:
        res = supabase.table("exclusions").select("id").eq("linkedin_url", linkedin_url).execute()
        return bool(hasattr(res, 'data') and res.data)
    except Exception:
        return False

def get_current_exclusions() -> List[Dict[str, Any]]:
    try:
        res = supabase.table("exclusions").select("*").execute()
        return res.data if hasattr(res, 'data') else []
    except Exception:
        return []