from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid
import time

# Import the existing Knowledge_GPT modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for API keys (for Render deployment)
if not os.getenv('OPENAI_API_KEY'):
    # Fallback to secrets.json for local development
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets.json"), "r") as f:
            import json
            secrets = json.load(f)
            os.environ['OPENAI_API_KEY'] = secrets.get('openai_api_key', '')
            os.environ['INTERNAL_DATABASE_API_KEY'] = secrets.get('internal_database_api_key', '')
            os.environ['SCRAPING_DOG_API_KEY'] = secrets.get('scraping_dog_api_key', '')
            os.environ['SUPABASE_URL'] = secrets.get('supabase_url', '')
            os.environ['SUPABASE_KEY'] = secrets.get('supabase_key', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

from prompt_formatting import parse_prompt_to_internal_database_filters, simulate_behavioral_data
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import async_scrape_linkedin_profiles
from assess_and_return import select_top_candidates
from database import (
    store_search_to_database, get_search_from_database, 
    get_recent_searches_from_database, delete_search_from_database,
    store_people_to_database, get_people_for_search, is_person_excluded_in_database,
    get_current_exclusions
)
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge_GPT API",
    description="Natural language to behavioral data converter API",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing and frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    prompt: str
    max_candidates: Optional[int] = 2
    include_linkedin: Optional[bool] = True

class SearchResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    filters: Optional[Dict[str, Any]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# Database initialization will happen on first use
logger.info("🚀 Knowledge_GPT API starting up...")

# In-memory storage for fallback only
search_results = {}

# Cache for database queries to reduce load
search_cache = {}
CACHE_TTL = 30  # Cache for 30 seconds

# JSON file storage for persistent data
def save_search_to_json(request_id: str, data: dict):
    """Save search result to JSON file for persistence"""
    try:
        os.makedirs("search_results", exist_ok=True)
        file_path = f"search_results/{request_id}.json"
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"[{request_id}] Search result saved to {file_path}")
    except Exception as e:
        logger.error(f"[{request_id}] Failed to save to JSON: {e}")

def load_search_from_json(request_id: str) -> Optional[dict]:
    """Load search result from JSON file"""
    try:
        file_path = f"search_results/{request_id}.json"
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.error(f"[{request_id}] Failed to load from JSON: {e}")
        return None

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0"
    )

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint for debugging frontend issues"""
    return {
        "message": "API is working",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cors_test": "This should work from frontend"
    }

@app.get("/api/cache/clear")
async def clear_cache():
    """Clear the search cache to force fresh database queries"""
    global search_cache
    cache_size = len(search_cache)
    search_cache.clear()
    return {
        "message": f"Cache cleared. Removed {cache_size} entries.",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "cache_size": len(search_cache),
        "cache_ttl_seconds": CACHE_TTL,
        "cached_requests": list(search_cache.keys()),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/search", response_model=SearchResponse)
async def create_search(request: SearchRequest, background_tasks: BackgroundTasks):
    """Create a new search request"""
    request_id = str(uuid.uuid4())
    
    # Initialize search result
    search_result = SearchResponse(
        request_id=request_id,
        status="processing",
        prompt=request.prompt,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    search_results[request_id] = search_result  # fallback only
    
    # Start background processing
    background_tasks.add_task(process_search, request_id, request)
    
    return search_result

@app.get("/api/search/{request_id}", response_model=SearchResponse)
async def get_search_result(request_id: str):
    """Get search result by request ID"""
    try:
        logger.info(f"Frontend request for search: {request_id}")
        
        # Check cache first to reduce database load
        current_time = time.time()
        if request_id in search_cache:
            cache_entry = search_cache[request_id]
            if current_time - cache_entry['timestamp'] < CACHE_TTL:
                logger.info(f"Returning cached result for {request_id}")
                return cache_entry['data']
            else:
                # Cache expired, remove it
                del search_cache[request_id]
        
        # Add CORS headers explicitly for debugging
        from fastapi.responses import Response
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        db_result = get_search_from_database(request_id)
        logger.info(f"Database result for {request_id}: {db_result is not None}")
        
        if db_result and isinstance(db_result, dict):
            # Fetch candidates from people table using search id
            search_id = db_result.get("id")
            logger.info(f"Search ID from database: {search_id}")
            
            candidates = get_people_for_search(search_id) if search_id else []
            logger.info(f"Found {len(candidates)} candidates for search {search_id}")
            
            # Build response dict
            response_data = dict(db_result)
            response_data["candidates"] = candidates
            
            # Validate the response data
            try:
                validated_response = SearchResponse(**response_data)
                logger.info(f"Successfully validated response for {request_id}")
                
                # Cache the successful result
                search_cache[request_id] = {
                    'data': validated_response,
                    'timestamp': current_time
                }
                
                return validated_response
            except Exception as validation_error:
                logger.error(f"Validation error for {request_id}: {validation_error}")
                # Return a simplified response if validation fails
                simplified_response = SearchResponse(
                    request_id=request_id,
                    status=db_result.get("status", "unknown"),
                    prompt=db_result.get("prompt", ""),
                    created_at=db_result.get("created_at", ""),
                    candidates=candidates
                )
                
                # Cache the simplified result too
                search_cache[request_id] = {
                    'data': simplified_response,
                    'timestamp': current_time
                }
                
                return simplified_response
        
        # Fallback to in-memory storage
        if request_id in search_results:
            logger.info(f"Using in-memory result for {request_id}")
            in_memory_result = search_results[request_id]
            
            # Cache the in-memory result
            search_cache[request_id] = {
                'data': in_memory_result,
                'timestamp': current_time
            }
            
            return in_memory_result
        
        # Check if search exists in JSON files
        json_result = load_search_from_json(request_id)
        if json_result:
            logger.info(f"Using JSON result for {request_id}")
            return SearchResponse(**json_result)
        
        # If no search found anywhere, return 404
        logger.warning(f"No search found for request_id: {request_id}")
        raise HTTPException(status_code=404, detail=f"Search with ID {request_id} not found")
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 404)
        logger.info(f"HTTPException for {request_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error retrieving search result for {request_id}: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        # Return a more specific error message
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/search")
async def list_searches():
    """List all search requests (candidate_count removed)"""
    db_searches = get_recent_searches_from_database(limit=50)
    if db_searches:
        return {
            "searches": [
                {
                    "request_id": search["request_id"],
                    "status": search["status"],
                    "prompt": search["prompt"],
                    "created_at": search["created_at"],
                    # candidate_count removed
                }
                for search in db_searches
            ]
        }
    # Fallback to in-memory storage
    return {
        "searches": [
            {
                "request_id": result.request_id,
                "status": result.status,
                "prompt": result.prompt,
                "created_at": result.created_at
            }
            for result in search_results.values()
        ]
    }

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics"""
    try:
        from supabase_client import supabase
        searches_res = supabase.table("searches").select("id", count="exact").execute()
        total_searches = searches_res.count if hasattr(searches_res, 'count') else None
        people_res = supabase.table("people").select("id", count="exact").execute()
        total_candidates = people_res.count if hasattr(people_res, 'count') else None
        return {
            "database_status": "connected",
            "total_searches": total_searches,
            "total_candidates": total_candidates
        }
    except Exception as e:
        logger.error(f"Database stats error: {e}")
        return {"database_status": "error", "error": str(e)}

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    """Delete a search request"""
    if delete_search_from_database(request_id):
        # Also delete the JSON file
        try:
            file_path = f"search_results/{request_id}.json"
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"[{request_id}] JSON file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"[{request_id}] Failed to delete JSON file: {e}")
        return {"message": "Search request deleted from database"}
    # Fallback to in-memory storage
    if request_id in search_results:
        del search_results[request_id]
        return {"message": "Search request deleted from memory"}
    raise HTTPException(status_code=404, detail="Search request not found")

@app.get("/api/search/{request_id}/json")
async def get_search_json(request_id: str):
    """Get search result as JSON file (for frontend consumption)"""
    json_data = load_search_from_json(request_id)
    if json_data is None:
        raise HTTPException(status_code=404, detail="Search result not found")
    
    return json_data

@app.get("/api/exclusions")
async def get_exclusions():
    """Get list of currently excluded people (within last 30 days)"""
    try:
        exclusions = get_current_exclusions(days=30)
        return {"exclusions": exclusions}
    except Exception as e:
        logger.error(f"Error retrieving exclusions: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

async def process_search(request_id: str, request: SearchRequest):
    """Background task to process the search"""
    try:
        result = search_results[request_id]
        
        # Step 1: Generate our internal database filters
        logger.info(f"[{request_id}] Generating our internal database filters...")
        filters = parse_prompt_to_internal_database_filters(request.prompt)
        
        if filters["reasoning"].startswith("Error"):
            result.status = "failed"
            result.error = filters["reasoning"]
            result.completed_at = datetime.now(timezone.utc).isoformat()
            return
        
        result.filters = filters
        logger.info(f"[{request_id}] Filters generated successfully")
        
        # Step 2: Search our internal database for people
        logger.info(f"[{request_id}] Searching our internal database...")
        try:
            logger.info(f"[{request_id}] Calling Apollo API with filters: {filters}")
            people = search_people_via_internal_database(filters, page=1, per_page=request.max_candidates or 2)
            logger.info(f"[{request_id}] Found {len(people)} people from Apollo API")
            
            # Filter out excluded people (already in people table within 30 days)
            if people:
                filtered_people = []
                for person in people:
                    email = person.get("email", "")
                    logger.info(f"[{request_id}] Checking exclusion for {email}")
                    if email and is_person_excluded_in_database(email):
                        logger.info(f"[{request_id}] Excluded {email} (already processed within 30 days)")
                    else:
                        filtered_people.append(person)
                        logger.info(f"[{request_id}] Kept {email}")
                people = filtered_people
                logger.info(f"[{request_id}] Filtered, {len(people)} remaining")
            else:
                logger.warning(f"[{request_id}] No people returned from Apollo API")
            
            if not people:
                # Fall back to behavioral simulation
                logger.info(f"[{request_id}] No people found, simulating behavioral data...")
                behavioral_data = simulate_behavioral_data(filters)
                result.behavioral_data = behavioral_data
                result.status = "completed"
                result.completed_at = datetime.now(timezone.utc).isoformat()
                return
                
        except Exception as e:
            logger.error(f"[{request_id}] Our internal database API error: {e}")
            # Fall back to behavioral simulation
            behavioral_data = simulate_behavioral_data(filters)
            result.behavioral_data = behavioral_data
            result.status = "completed"
            result.completed_at = datetime.now(timezone.utc).isoformat()
            return
        
        # Step 3: Scrape LinkedIn profiles (if enabled) - with 15 second timeout
        if request.include_linkedin:
            logger.info(f"[{request_id}] Scraping LinkedIn profiles...")
            linkedin_urls = [person.get("linkedin_url") for person in people if person.get("linkedin_url")]
            if linkedin_urls:
                try:
                    # Add timeout to LinkedIn scraping to prevent blocking
                    profile_data = await asyncio.wait_for(
                        async_scrape_linkedin_profiles(linkedin_urls), 
                        timeout=15.0  # 15 second timeout - skip if too slow
                    )
                    # Merge profile data with our internal database data
                    enriched_people = []
                    for i, person in enumerate(people):
                        if person.get("linkedin_url") and profile_data:
                            if isinstance(profile_data, list) and i < len(profile_data):
                                person["linkedin_profile"] = profile_data[i]
                            elif isinstance(profile_data, dict) and str(i) in profile_data:
                                person["linkedin_profile"] = profile_data[str(i)]
                        enriched_people.append(person)
                    people = enriched_people
                    logger.info(f"[{request_id}] LinkedIn profiles scraped successfully")
                except asyncio.TimeoutError:
                    logger.warning(f"[{request_id}] LinkedIn scraping timed out after 15s, skipping LinkedIn data")
                except Exception as e:
                    logger.error(f"[{request_id}] LinkedIn scraping failed: {e}, continuing without LinkedIn data")
            else:
                logger.info(f"[{request_id}] No LinkedIn URLs found, skipping LinkedIn scraping")
        
        # Filter out candidates without a company before assessment
        people = [p for p in people if p.get("company") or (p.get("organization") and p["organization"].get("name"))]
        logger.info(f"[{request_id}] Excluded candidates without company. {len(people)} remaining.")

        # Step 5: Assess and select top candidates
        logger.info(f"[{request_id}] Assessing candidates...")
        try:
            # Pass behavioral_data to select_top_candidates
            bd = result.behavioral_data if hasattr(result, 'behavioral_data') and result.behavioral_data is not None else {}
            top_candidates = select_top_candidates(request.prompt, people, behavioral_data=bd)
            # Enhanced merging logic: match by email (preferred), then name+company
            enhanced_candidates = []
            for candidate in top_candidates:
                # Try to find the corresponding person data by email, then by name+company
                person_data = None
                if candidate.get("email"):
                    person_data = next((p for p in people if p.get("email") == candidate.get("email")), None)
                if not person_data and candidate.get("name") and candidate.get("company"):
                    person_data = next((p for p in people if p.get("name") == candidate.get("name") and p.get("organization_name", p.get("company")) == candidate.get("company")), None)
                if not person_data:
                    person_data = {}
                # Always prefer enriched data for company and photo
                company = (
                    candidate.get("company")
                    or person_data.get("organization_name")
                    or (person_data.get("organization", {}).get("name") if person_data.get("organization") else None)
                    or person_data.get("company")
                    or "Unknown"
                )
                # --- PATCH: Always set company from Apollo organization.name if present ---
                if person_data.get("organization") and person_data["organization"].get("name"):
                    company = person_data["organization"]["name"]
                # Initialize photo URL from Apollo data first
                photo_url = (
                    person_data.get("profile_photo_url")
                    or person_data.get("photo_url")
                    or None
                )
                location = person_data.get("location")
                linkedin_profile = person_data.get("linkedin_profile", {})
                
                # Extract data from ScrapingDog LinkedIn profile (if available)
                if linkedin_profile and isinstance(linkedin_profile, dict):
                    # Extract company from description
                    description = linkedin_profile.get("description", {})
                    if description and isinstance(description, dict):
                        company_from_desc = description.get("description1", "")
                        if company_from_desc and company_from_desc != "Unknown":
                            company = company_from_desc
                    
                    # Extract location
                    linkedin_location = linkedin_profile.get("location", "")
                    if linkedin_location and linkedin_location != "Unknown":
                        location = linkedin_location
                    
                    # Extract profile photo - prioritize LinkedIn photo if available
                    photo_fields = ["profile_photo", "profile_photo_url", "avatar", "image", "picture", "photo"]
                    for field in photo_fields:
                        if linkedin_profile.get(field):
                            photo_url = linkedin_profile[field]
                            break
                
                # Final fallback for photo URL
                if not photo_url:
                    photo_url = (
                        person_data.get("profile_photo_url")
                        or person_data.get("photo_url")
                        or None
                    )
                # Log what will be stored
                logger.info(f"[Candidate Storage] Name: {candidate.get('name')}, Email: {candidate.get('email')}, Company: {company}, Photo: {photo_url}, Reasons: {candidate.get('reasons')}")
                logger.info(f"[Photo URL Debug] Final photo_url: {photo_url}")
                logger.info(f"[Photo URL Debug] person_data photo fields: profile_photo_url={person_data.get('profile_photo_url')}, photo_url={person_data.get('photo_url')}")
                logger.info(f"[Photo URL Debug] linkedin_profile available: {bool(linkedin_profile)}")
                if not company or company == "Unknown":
                    logger.warning(f"[Candidate Storage] Missing company for {candidate.get('name')} ({candidate.get('email')})")
                if not photo_url:
                    logger.warning(f"[Candidate Storage] Missing photo URL for {candidate.get('name')} ({candidate.get('email')})")
                # Always include the full LinkedIn profile data in the candidate
                enhanced_candidate = {
                    "name": candidate.get("name", "Unknown"),
                    "title": candidate.get("title", person_data.get("title", "Unknown")),
                    "company": company,
                    "email": candidate.get("email", "Not available"),
                    "accuracy": candidate.get("accuracy", 0),
                    "reasons": candidate.get("reasons", []),
                    "linkedin_url": person_data.get("linkedin_url"),
                    "profile_photo_url": photo_url,
                    "location": location,
                    "linkedin_profile": linkedin_profile  # <-- always include full profile
                }
                # If there are any extra fields in linkedin_profile, add them at the top level for convenience
                if linkedin_profile:
                    for k, v in linkedin_profile.items():
                        if k not in enhanced_candidate:
                            enhanced_candidate[k] = v
                enhanced_candidates.append(enhanced_candidate)
            result.candidates = enhanced_candidates
        except Exception as e:
            logger.error(f"[{request_id}] Assessment error: {e}")
            # Fall back to basic results
            result.candidates = [
                {
                    "name": person.get("name", "Unknown"),
                    "title": person.get("title", "Unknown"),
                    "company": person.get("organization_name", "Unknown"),
                    "email": person.get("email", "Not available"),
                    "accuracy": 85 - (i * 10),
                    "reasons": ["Selected based on title and company fit"],
                    "linkedin_url": person.get("linkedin_url"),
                    "profile_photo_url": None,
                    "location": person.get("location")
                }
                for i, person in enumerate(people[:request.max_candidates])
            ]
        
        # Step 6: Generate behavioral data
        logger.info(f"[{request_id}] Generating behavioral data...")
        behavioral_data = simulate_behavioral_data(filters)
        result.behavioral_data = behavioral_data
        result.status = "completed"
        result.completed_at = datetime.now(timezone.utc).isoformat()

        # --- PATCH: Always set company from organization.name if present ---
        if result.candidates:
            for candidate in result.candidates:
                org = candidate.get("organization")
                if isinstance(org, dict) and org.get("name"):
                    candidate["company"] = org["name"]
        # --- PATCH: Only write to Supabase after all processing is complete ---
        # Store in database (primary storage) with retry mechanism
        search_data = result.dict()
        # Remove candidates before storing in searches
        if "candidates" in search_data:
            del search_data["candidates"]
        max_retries = 3
        db_search_id = None
        for attempt in range(1, max_retries + 1):
            try:
                db_search_id = store_search_to_database(search_data)
                if db_search_id:
                    logger.info(f"[{request_id}] Search stored in database with ID: {db_search_id} (attempt {attempt})")
                    break
                else:
                    logger.error(f"[{request_id}] Attempt {attempt}: Failed to store in database (no ID returned)")
            except Exception as e:
                logger.error(f"[{request_id}] Attempt {attempt}: Exception during store_search_to_database: {e}")
            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                logger.info(f"[{request_id}] Retrying database storage in {wait}s...")
                time.sleep(wait)
        if db_search_id:
            if result.candidates:
                try:
                    store_people_to_database(db_search_id, result.candidates)
                    logger.info(f"[{request_id}] Stored {len(result.candidates)} candidates in people table")
                except Exception as e:
                    logger.error(f"[{request_id}] Failed to store candidates: {e}")
        else:
            logger.critical(f"[{request_id}] All attempts to store search in database failed. Using in-memory storage.")
            search_results[request_id] = result
        # Save to JSON file for persistence (optional backup)
        save_search_to_json(request_id, result.dict())
        logger.info(f"[{request_id}] Search completed successfully")
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        result.status = "failed"
        result.error = str(e)
        result.completed_at = datetime.now(timezone.utc).isoformat()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 