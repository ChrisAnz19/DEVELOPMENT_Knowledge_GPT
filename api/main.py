from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid
import time
import re
import sys
import os

# Import the existing Knowledge_GPT modules
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

from prompt_formatting import parse_prompt_to_internal_database_filters
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import async_scrape_linkedin_profiles
from assess_and_return import select_top_candidates
from database import (
    store_search_to_database, get_search_from_database, 
    get_recent_searches_from_database, delete_search_from_database,
    store_people_to_database, get_people_for_search
)
from behavioral_metrics_ai import enhance_behavioral_data_ai
import logging

# Set up logging - SIMPLIFIED
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Knowledge_GPT API",
    description="Natural language to behavioral data converter API",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    prompt: str
    max_candidates: Optional[int] = 3
    include_linkedin: Optional[bool] = True

class SearchResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    filters: Optional[Dict[str, Any]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

# Simplified profile photo URL extraction
def extract_profile_photo_url(candidate_data, linkedin_profile=None):
    """Extract profile photo URL from candidate data or LinkedIn profile."""
    try:
        # Ensure candidate_data is a dictionary
        if not isinstance(candidate_data, dict):
            return None
            
        # Check LinkedIn profile first
        if linkedin_profile and isinstance(linkedin_profile, dict):
            for field in ["profile_photo_url", "profile_photo", "avatar", "image"]:
                if field in linkedin_profile and linkedin_profile[field]:
                    return linkedin_profile[field]
        
        # Check candidate data
        for field in ["profile_photo_url", "photo_url", "profile_picture_url"]:
            if field in candidate_data and candidate_data[field]:
                return candidate_data[field]
        
        # Check organization logo as fallback
        if "organization" in candidate_data and isinstance(candidate_data["organization"], dict):
            org = candidate_data["organization"]
            if "logo_url" in org and org["logo_url"]:
                return org["logo_url"]
                
        return None
    except Exception:
        return None

# Simplified and optimized process_search function
async def process_search(
    request_id: str,
    prompt: str,
    max_candidates: int = 3,
    include_linkedin: bool = True
):
    """Process a search request in the background."""
    # Simple state tracking to prevent infinite loops
    is_completed = False
    
    try:
        # Get search data
        search_data = get_search_from_database(request_id)
        if not search_data:
            logger.error(f"Search not found: {request_id}")
            return
            
        # Skip if already completed
        if search_data.get("status") == "completed":
            return
        
        # Parse prompt to filters
        filters = parse_prompt_to_internal_database_filters(prompt)
        
        # Search for people with timeout
        try:
            people = await asyncio.wait_for(
                search_people_via_internal_database(filters, max_candidates),
                timeout=60  # 1 minute timeout
            )
        except (asyncio.TimeoutError, Exception) as e:
            # Update search status to failed
            search_data["status"] = "failed"
            search_data["error"] = str(e)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            return
        
        # If no people found, complete with empty results
        if not people:
            search_data["status"] = "completed"
            search_data["filters"] = json.dumps(filters)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            is_completed = True
            return
        
        # Scrape LinkedIn profiles if requested (with reduced fields)
        if include_linkedin and people:
            try:
                # Extract LinkedIn URLs with type checking
                linkedin_urls = []
                for p in people:
                    if isinstance(p, dict) and p.get("linkedin_url"):
                        linkedin_urls.append(p.get("linkedin_url"))
                
                if linkedin_urls:
                    # Process LinkedIn profiles with timeout
                    linkedin_profiles = await asyncio.wait_for(
                        async_scrape_linkedin_profiles(linkedin_urls),
                        timeout=60  # 1 minute timeout
                    )
                    
                    # Merge LinkedIn profile data
                    if linkedin_profiles:
                        profile_map = {}
                        for p in linkedin_profiles:
                            if isinstance(p, dict) and p.get("linkedin_url"):
                                profile_map[p.get("linkedin_url")] = p
                        
                        for person in people:
                            if isinstance(person, dict):
                                linkedin_url = person.get("linkedin_url")
                                if linkedin_url and linkedin_url in profile_map:
                                    person["linkedin_profile"] = profile_map[linkedin_url]
            except Exception:
                # Continue without LinkedIn data if there's an error
                pass
        
        # Select top candidates
        candidates = select_top_candidates(people, prompt, max_candidates) if people else []
        if not candidates and people:
            candidates = people[:max_candidates]
        
        # Enhance candidate data with missing fields
        for candidate in candidates:
            if isinstance(candidate, dict):
                # Extract and set profile photo URL
                profile_photo_url = extract_profile_photo_url(
                    candidate, 
                    candidate.get("linkedin_profile")
                )
                if profile_photo_url:
                    candidate["profile_photo_url"] = profile_photo_url
                
                # Ensure company name is set from various sources
                if not candidate.get("company") or candidate.get("company") == "Unknown":
                    # Try to get company from organization field
                    if "organization" in candidate:
                        org = candidate["organization"]
                        if isinstance(org, dict) and org.get("name"):
                            candidate["company"] = org["name"]
                        elif isinstance(org, str) and org.strip():
                            candidate["company"] = org
                    
                    # Try to get company from LinkedIn profile
                    linkedin_profile = candidate.get("linkedin_profile")
                    if isinstance(linkedin_profile, dict):
                        if linkedin_profile.get("company"):
                            candidate["company"] = linkedin_profile["company"]
                        elif linkedin_profile.get("current_company"):
                            candidate["company"] = linkedin_profile["current_company"]
                        elif linkedin_profile.get("experience") and isinstance(linkedin_profile["experience"], list):
                            # Get company from most recent experience
                            if linkedin_profile["experience"] and isinstance(linkedin_profile["experience"][0], dict):
                                recent_exp = linkedin_profile["experience"][0]
                                if recent_exp.get("company"):
                                    candidate["company"] = recent_exp["company"]
                
                # Ensure LinkedIn URL is properly formatted and present
                linkedin_url = candidate.get("linkedin_url")
                if linkedin_url:
                    if not linkedin_url.startswith("http"):
                        candidate["linkedin_url"] = f"https://{linkedin_url}"
                elif candidate.get("linkedin_profile") and isinstance(candidate["linkedin_profile"], dict):
                    # Try to get LinkedIn URL from profile data
                    profile_url = candidate["linkedin_profile"].get("url") or candidate["linkedin_profile"].get("linkedin_url")
                    if profile_url:
                        if not profile_url.startswith("http"):
                            candidate["linkedin_url"] = f"https://{profile_url}"
                        else:
                            candidate["linkedin_url"] = profile_url
        
        # Generate behavioral data
        try:
            behavioral_data = enhance_behavioral_data_ai({}, candidates, prompt)
        except Exception:
            # Simple fallback behavioral data
            title = "professional"
            if candidates and len(candidates) > 0 and isinstance(candidates[0], dict):
                title = candidates[0].get('title', 'professional')
            
            behavioral_data = {
                "behavioral_insight": f"This {title} responds best to personalized engagement focusing on their specific business challenges.",
                "scores": {
                    "cmi": {"score": 70, "explanation": "Moderate commitment"},
                    "rbfs": {"score": 65, "explanation": "Balanced risk approach"},
                    "ias": {"score": 75, "explanation": "Strong role alignment"}
                }
            }
        
        # Store candidates in database
        search_db_id = search_data.get("id")
        if search_db_id:
            store_people_to_database(search_db_id, candidates)
        
        # Update search status
        if not is_completed:
            search_data["status"] = "completed"
            search_data["filters"] = json.dumps(filters)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            search_data["behavioral_data"] = json.dumps(behavioral_data)
            store_search_to_database(search_data)
            is_completed = True
            
    except Exception as e:
        # Update search status to failed if not already completed
        if not is_completed:
            try:
                search_data = get_search_from_database(request_id)
                if search_data:
                    search_data["status"] = "failed"
                    search_data["error"] = str(e)
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
            except Exception:
                pass

# API Routes
@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/search")
async def create_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """Create a new search request."""
    try:
        # Validate input
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        if request.max_candidates and (request.max_candidates < 1 or request.max_candidates > 10):
            raise HTTPException(status_code=400, detail="max_candidates must be between 1 and 10")
        
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Store the initial search request
        search_data = {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt.strip(),
            "filters": json.dumps({}),
            "created_at": created_at,
            "completed_at": None
        }
        
        # Store in database
        search_db_id = store_search_to_database(search_data)
        if not search_db_id:
            raise HTTPException(status_code=500, detail="Failed to store search in database")
        
        # Start background task
        background_tasks.add_task(
            process_search,
            request_id=request_id,
            prompt=request.prompt.strip(),
            max_candidates=request.max_candidates or 3,
            include_linkedin=request.include_linkedin if request.include_linkedin is not None else True
        )
        
        # Return initial response
        response_data = {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt.strip(),
            "created_at": created_at,
            "completed_at": None
        }
        
        # Ensure we return a proper object
        if not isinstance(response_data, dict):
            logger.error(f"Response data is not a dictionary: {type(response_data)}")
            raise HTTPException(status_code=500, detail="Invalid response format")
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating search: {str(e)}")

@app.get("/api/search/{request_id}")
async def get_search_result(request_id: str):
    """Get the results of a specific search by request ID."""
    try:
        # Validate request_id
        if not request_id or not isinstance(request_id, str):
            raise HTTPException(status_code=400, detail="Invalid request_id")
        
        # Get the search from the database
        search_data = get_search_from_database(request_id)
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Ensure search_data is a dictionary
        if not isinstance(search_data, dict):
            logger.error(f"Search data is not a dictionary: {type(search_data)}")
            raise HTTPException(status_code=500, detail="Invalid search data format")
        
        # Parse JSON strings to Python objects
        if "filters" in search_data and isinstance(search_data["filters"], str):
            try:
                search_data["filters"] = json.loads(search_data["filters"])
            except json.JSONDecodeError:
                search_data["filters"] = {}
        
        # Get candidates for this search
        search_db_id = search_data.get("id")
        if search_db_id:
            candidates = get_people_for_search(search_db_id)
            if candidates and isinstance(candidates, list):
                # Process candidates to ensure all required fields
                processed_candidates = []
                
                for candidate in candidates:
                    if isinstance(candidate, dict):
                        processed_candidate = {
                            "id": candidate.get("id"),
                            "name": candidate.get("name"),
                            "title": candidate.get("title"),
                            "email": candidate.get("email"),
                            "location": candidate.get("location"),
                            "company": candidate.get("company"),
                            "linkedin_url": candidate.get("linkedin_url"), 
                            "profile_photo_url": candidate.get("profile_photo_url"),
                            "accuracy": candidate.get("accuracy"),
                            "reasons": candidate.get("reasons"),
                            "linkedin_profile": candidate.get("linkedin_profile"),
                            "behavioral_data": candidate.get("behavioral_data")
                        }
                        processed_candidates.append(processed_candidate)
                
                search_data["candidates"] = processed_candidates
                
                # Force status to completed when we have candidates
                search_data["status"] = "completed"
                if not search_data.get("completed_at"):
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Ensure we always return a proper object
        if not isinstance(search_data, dict):
            logger.error(f"Final search_data is not a dictionary: {type(search_data)}")
            raise HTTPException(status_code=500, detail="Invalid response format")
        
        return search_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search result: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting search result: {str(e)}")

@app.get("/api/search")
async def list_searches():
    """Get a list of all searches with their status."""
    try:
        searches = get_recent_searches_from_database()
        return {"searches": searches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing searches: {str(e)}")

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    """Delete a specific search and its results."""
    try:
        delete_search_from_database(request_id)
        return {"message": "Search request deleted from database"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)