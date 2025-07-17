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

def extract_profile_photo_url(
    candidate_data: Dict[str, Any],
    linkedin_profile: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Extracts and prioritizes profile photo URLs from various sources.
    
    Args:
        candidate_data: Data about the candidate
        linkedin_profile: Optional LinkedIn profile data
        
    Returns:
        String containing the best available profile photo URL or None if no valid URL found
    """
    try:
        # Define photo URL fields to check in order of priority
        photo_url = None
        
        # 1. First priority: LinkedIn profile photo (if available)
        if linkedin_profile and isinstance(linkedin_profile, dict):
            # Check common LinkedIn photo field names
            linkedin_photo_fields = [
                "profile_photo", "profile_photo_url", "avatar", 
                "image", "picture", "photo", "profile_picture",
                "profile_image", "profile_img", "img", "image_url"
            ]
            
            for field in linkedin_photo_fields:
                if field in linkedin_profile and linkedin_profile[field]:
                    photo_url = linkedin_profile[field]
                    logger.info(f"Found LinkedIn photo URL in field '{field}': {photo_url}")
                    break
        
        # 2. Second priority: Apollo API profile photo
        if not photo_url:
            apollo_photo_fields = [
                "profile_photo_url", "photo_url", "picture_url", 
                "avatar_url", "image_url", "photo", "profile_image_url",
                "profile_picture_url", "avatar", "image"
            ]
            
            for field in apollo_photo_fields:
                if field in candidate_data and candidate_data[field]:
                    photo_url = candidate_data[field]
                    logger.info(f"Found Apollo photo URL in field '{field}': {photo_url}")
                    break
        
        # 3. Third priority: Check nested objects
        if not photo_url:
            # Check in organization data
            if "organization" in candidate_data and isinstance(candidate_data["organization"], dict):
                org = candidate_data["organization"]
                if "logo_url" in org and org["logo_url"]:
                    # Use organization logo as last resort
                    photo_url = org["logo_url"]
                    logger.info(f"Using organization logo as fallback: {photo_url}")
        
        # Validate URL format
        if photo_url:
            # Basic URL validation
            url_pattern = re.compile(
                r'^(?:http|https)://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or ipv4
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)', re.IGNORECASE)  # path and query
            
            if not url_pattern.match(photo_url):
                logger.warning(f"Invalid photo URL format: {photo_url}")
                return None
            
            # Check for common image extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            has_image_extension = any(photo_url.lower().endswith(ext) for ext in image_extensions)
            
            # If URL doesn't end with image extension, check if it contains image-related keywords
            if not has_image_extension:
                image_keywords = ['photo', 'image', 'picture', 'avatar', 'profile']
                has_image_keyword = any(keyword in photo_url.lower() for keyword in image_keywords)
                
                if not has_image_keyword:
                    logger.warning(f"URL doesn't appear to be an image: {photo_url}")
                    # Still return it, but log the warning
            
            return photo_url
        
        logger.info("No valid photo URL found for candidate")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting profile photo URL: {str(e)}")
        return None

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
    max_candidates: Optional[int] = 3
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
    
    def validate_behavioral_data_format(self):
        """
        Validates the behavioral data format to ensure it contains the new focused insight and scores.
        Provides backward compatibility by checking for both old and new formats.
        """
        if not self.behavioral_data:
            return True
            
        # New format should have behavioral_insight
        if "behavioral_insight" in self.behavioral_data:
            # Validate that behavioral_insight is a string
            if not isinstance(self.behavioral_data["behavioral_insight"], str):
                logger.warning("behavioral_insight should be a string")
                return False
                
            # Validate that behavioral_insight is not empty
            if not self.behavioral_data["behavioral_insight"].strip():
                logger.warning("behavioral_insight should not be empty")
                return False
            
            # Check for scores
            if "scores" in self.behavioral_data:
                scores = self.behavioral_data["scores"]
                # Validate that scores contains the three required scores
                required_scores = ["cmi", "rbfs", "ias"]
                for score_key in required_scores:
                    if score_key not in scores:
                        logger.warning(f"Missing required score: {score_key}")
                        # Don't fail validation for missing scores, for backward compatibility
                
                # Validate score format if present
                for score_key in required_scores:
                    if score_key in scores:
                        score_obj = scores[score_key]
                        if "score" not in score_obj or "explanation" not in score_obj:
                            logger.warning(f"Score {score_key} is missing required fields")
                            # Don't fail validation for incomplete scores, for backward compatibility
            
            logger.info("Using new behavioral data format with focused insight")
            return True
            
        # Check for legacy format (multiple metrics)
        legacy_fields = [
            "commitment_momentum_index",
            "risk_barrier_focus_score", 
            "identity_alignment_signal",
            "psychometric_modeling_insight"
        ]
        
        has_legacy_format = any(field in self.behavioral_data for field in legacy_fields)
        if has_legacy_format:
            logger.info("Using legacy behavioral data format for backward compatibility")
            # For backward compatibility, we'll accept the legacy format
            return True
            
        # If it has other fields but not the expected ones, still allow it
        # This provides flexibility for future changes
        logger.info("Behavioral data has custom format, allowing for flexibility")
        return True
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
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create a timestamp for the request
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Store the initial search request in the database with processing status
        search_data = {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt,
            "filters": json.dumps({}),  # Empty filters initially
            "created_at": created_at,
            "completed_at": None
        }
        
        # Store the search in the database
        store_search_to_database(search_data)
        
        # Start background task to process real data
        background_tasks.add_task(
            process_search,
            request_id=request_id,
            prompt=request.prompt,
            max_candidates=request.max_candidates,
            include_linkedin=request.include_linkedin
        )
        
        # Return the initial response with processing status
        return {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt,
            "created_at": created_at,
            "completed_at": None
        }
        
    except Exception as e:
        logger.error(f"Error creating search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating search: {str(e)}")

@app.get("/api/search/{request_id}")
async def get_search_result(request_id: str):
    """Get the results of a specific search by request ID."""
    try:
        # Get the search from the database
        search_data = get_search_from_database(request_id)
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Parse JSON strings back to Python objects
        if "filters" in search_data and isinstance(search_data["filters"], str):
            try:
                search_data["filters"] = json.loads(search_data["filters"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse filters JSON for search {request_id}")
                search_data["filters"] = {}
        
        if "behavioral_data" in search_data and isinstance(search_data["behavioral_data"], str):
            try:
                search_data["behavioral_data"] = json.loads(search_data["behavioral_data"])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse behavioral_data JSON for search {request_id}")
                search_data["behavioral_data"] = {}
        
        # Get candidates for this search
        try:
            # Get the database ID for the search (not the request_id)
            search_db_id = search_data.get("id")
            if search_db_id:
                # Get people using the search database ID
                candidates = get_people_for_search(search_db_id)
                if candidates:
                    search_data["candidates"] = candidates
                    logger.info(f"Found {len(candidates)} candidates for search {request_id}")
            else:
                logger.warning(f"Cannot get candidates: search_db_id not found for request_id {request_id}")
        except Exception as e:
            logger.error(f"Error getting candidates for search {request_id}: {str(e)}")
            # Continue even if getting candidates fails
            
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
        # Get recent searches from the database
        searches = get_recent_searches_from_database()
        
        return {"searches": searches}
        
    except Exception as e:
        logger.error(f"Error listing searches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing searches: {str(e)}")

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    """Delete a specific search and its results."""
    try:
        # Delete the search from the database
        delete_search_from_database(request_id)
        
        return {"message": "Search request deleted from database"}
        
    except Exception as e:
        logger.error(f"Error deleting search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting search: {str(e)}")

@app.get("/api/search/{request_id}/json")
async def get_search_json(request_id: str):
    """Get the raw JSON data for a search (useful for debugging)."""
    try:
        # Get the search from the database
        search_data = get_search_from_database(request_id)
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
            
        return search_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting search JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting search JSON: {str(e)}")

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        # Get recent searches from the database
        searches = get_recent_searches_from_database()
        
        # Get current exclusions
        exclusions = get_current_exclusions()
        
        return {
            "database_status": "connected",
            "total_searches": len(searches),
            "total_candidates": sum(len(search.get("candidates", [])) for search in searches if search.get("candidates"))
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")

@app.get("/api/exclusions")
async def get_exclusions():
    """Get all currently excluded people."""
    try:
        # Get current exclusions
        exclusions = get_current_exclusions()
        
        return {
            "exclusions": exclusions,
            "count": len(exclusions)
        }
        
    except Exception as e:
        logger.error(f"Error getting exclusions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting exclusions: {str(e)}")

# Background task for processing searches
async def process_search(
    request_id: str,
    prompt: str,
    max_candidates: int = 3,
    include_linkedin: bool = True
):
    """Process a search request in the background."""
    try:
        # Update the search status to processing
        search_data = get_search_from_database(request_id)
        if not search_data:
            logger.error(f"Search not found: {request_id}")
            return
            
        # Parse the prompt to filters
        filters = parse_prompt_to_internal_database_filters(prompt)
        
        # Search for people via the internal database
        people = await search_people_via_internal_database(filters, max_candidates)
        
        # Scrape LinkedIn profiles if requested
        if include_linkedin and people:
            people = await async_scrape_linkedin_profiles(people)
            
        # Select top candidates
        candidates = select_top_candidates(people, prompt, max_candidates)
        
        # Add profile photo URLs
        for candidate in candidates:
            linkedin_profile = candidate.get("linkedin_profile", {})
            profile_photo_url = extract_profile_photo_url(candidate, linkedin_profile)
            if profile_photo_url:
                candidate["profile_photo_url"] = profile_photo_url
        
        # Generate behavioral data
        try:
            from behavioral_metrics import enhance_behavioral_data
            behavioral_data = enhance_behavioral_data({}, candidates, prompt)
            search_data["behavioral_data"] = json.dumps(behavioral_data)  # Convert to JSON string
            logger.info(f"Generated behavioral data: {behavioral_data}")
        except Exception as be:
            logger.error(f"Error generating behavioral data: {str(be)}")
            # Continue even if behavioral data generation fails
        
        # Update the search data
        search_data["status"] = "completed"
        search_data["filters"] = json.dumps(filters)  # Convert to JSON string
        # Don't include candidates in search_data as it's not in the database schema
        search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Store the updated search in the database
        store_search_to_database(search_data)
        
        # Store candidates separately
        try:
            # Get the database ID for the search (not the request_id)
            search_db_id = search_data.get("id")
            if search_db_id:
                # Store people with the search database ID
                store_people_to_database(search_db_id, candidates)
                logger.info(f"Stored {len(candidates)} candidates for search {request_id} (DB ID: {search_db_id})")
            else:
                logger.error(f"Cannot store candidates: search_db_id not found for request_id {request_id}")
        except Exception as pe:
            logger.error(f"Error storing candidates: {str(pe)}")
        
        logger.info(f"Search completed successfully: {request_id}")
        
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}")
        
        # Update the search status to failed
        try:
            search_data = get_search_from_database(request_id)
            if search_data:
                search_data["status"] = "failed"
                search_data["error"] = str(e)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
        except Exception as update_error:
            logger.error(f"Error updating search status: {str(update_error)}")

# Server startup code
if __name__ == "__main__":
    # Get port from environment variable for Render deployment
    port = int(os.environ.get("PORT", 8000))
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )