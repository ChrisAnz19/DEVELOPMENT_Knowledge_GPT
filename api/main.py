from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid

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
            os.environ['BRIGHT_DATA_API_KEY'] = secrets.get('bright_data_api_key', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

from prompt_formatting import parse_prompt_to_internal_database_filters, simulate_behavioral_data
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import scrape_linkedin_profiles, scrape_linkedin_posts
from assess_and_return import select_top_candidates
from database import (
    store_search_to_database, get_search_from_database, 
    get_recent_searches_from_database, delete_search_from_database,
    store_people_to_database, get_people_for_search, is_person_excluded_in_database
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
    include_posts: Optional[bool] = True

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
        db_result = get_search_from_database(request_id)
        if db_result:
            return SearchResponse(**db_result)
        # Fallback to in-memory storage
        if request_id in search_results:
            return search_results[request_id]
        logger.warning(f"No search found in database for request_id: {request_id}")
        raise HTTPException(status_code=404, detail="Search request not found")
    except Exception as e:
        # Handle Supabase 406 error (no rows)
        if isinstance(e, dict) and e.get('code') == 'PGRST116':
            logger.warning(f"Supabase: No search found for request_id: {request_id}")
            raise HTTPException(status_code=404, detail="Search request not found")
        logger.error(f"Error retrieving search result for {request_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.get("/api/search")
async def list_searches():
    """List all search requests"""
    db_searches = get_recent_searches_from_database(limit=50)
    if db_searches:
        return {
            "searches": [
                {
                    "request_id": search["request_id"],
                    "status": search["status"],
                    "prompt": search["prompt"],
                    "created_at": search["created_at"],
                    "candidate_count": search.get("candidate_count", 0)
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
            people = search_people_via_internal_database(filters, page=1, per_page=request.max_candidates or 2)
            logger.info(f"[{request_id}] Found {len(people)} people")
            
            # Filter out excluded people (already in people table within 30 days)
            if people:
                filtered_people = []
                for person in people:
                    email = person.get("email", "")
                    if email and is_person_excluded_in_database(email):
                        logger.info(f"[{request_id}] Excluded {email} (already processed within 30 days)")
                    else:
                        filtered_people.append(person)
                people = filtered_people
                logger.info(f"[{request_id}] Filtered, {len(people)} remaining")
            
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
        
        # Step 3: Scrape LinkedIn profiles (if enabled)
        if request.include_linkedin:
            logger.info(f"[{request_id}] Scraping LinkedIn profiles...")
            linkedin_urls = [person.get("linkedin_url") for person in people if person.get("linkedin_url")]
            
            if linkedin_urls:
                profile_data = scrape_linkedin_profiles(linkedin_urls)
                
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
                logger.info(f"[{request_id}] LinkedIn profiles scraped")
        
        # Step 4: Scrape LinkedIn posts (if enabled)
        if request.include_posts and request.include_linkedin:
            logger.info(f"[{request_id}] Scraping LinkedIn posts...")
            for person in people[:2]:  # Only scrape posts for top 2 candidates
                profile = person.get("linkedin_profile", {})
                posts = profile.get("posts", [])
                recent_posts = posts[:5]  # Get up to 5 recent posts
                
                if recent_posts:
                    posts_data = scrape_linkedin_posts(recent_posts)
                    if posts_data:
                        person["linkedin_posts"] = posts_data
                    await asyncio.sleep(1)  # Rate limiting
            
            logger.info(f"[{request_id}] LinkedIn posts scraped")
        
        # Step 5: Assess and select top candidates
        logger.info(f"[{request_id}] Assessing candidates...")
        try:
            top_candidates = select_top_candidates(request.prompt, people)
            
            # Enhance candidates with profile photos and additional data
            enhanced_candidates = []
            for candidate in top_candidates:
                # Find the corresponding person data
                person_data = next((p for p in people if p.get("name") == candidate.get("name")), {})
                
                enhanced_candidate = {
                    "name": candidate.get("name", "Unknown"),
                    "title": candidate.get("title", "Unknown"),
                    "company": candidate.get("company", person_data.get("organization_name", "Unknown")),
                    "email": candidate.get("email", "Not available"),
                    "accuracy": candidate.get("accuracy", 0),
                    "reasons": candidate.get("reasons", []),
                    "linkedin_url": person_data.get("linkedin_url"),
                    "profile_photo_url": None,  # Will be populated from LinkedIn data
                    "location": person_data.get("location"),
                    "linkedin_profile": person_data.get("linkedin_profile", {}),
                    "linkedin_posts": person_data.get("linkedin_posts", [])
                }
                
                # Extract profile photo URL from LinkedIn data
                linkedin_profile = person_data.get("linkedin_profile", {})
                if linkedin_profile:
                    # Check various possible photo field names
                    photo_fields = ["profile_photo", "profile_photo_url", "avatar", "image", "picture", "photo"]
                    for field in photo_fields:
                        if linkedin_profile.get(field):
                            enhanced_candidate["profile_photo_url"] = linkedin_profile[field]
                            break
                
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
        
        # Store in database (primary storage)
        search_data = result.dict()
        db_search_id = store_search_to_database(search_data)
        if db_search_id:
            logger.info(f"[{request_id}] Search stored in database with ID: {db_search_id}")
            
            # Store people in people table
            if result.candidates:
                store_people_to_database(result.candidates, db_search_id)
                logger.info(f"[{request_id}] Stored {len(result.candidates)} candidates in people table")
        else:
            logger.error(f"[{request_id}] Failed to store in database, using in-memory storage")
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