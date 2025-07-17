from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any, Union
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid
import time
import re
import traceback

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
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load secrets.json: {e}")
        # Continue without secrets, API will handle missing keys gracefully

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
# Import the behavioral_metrics_ai module instead of behavioral_metrics
from behavioral_metrics_ai import enhance_behavioral_data_ai
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_errors.log')
    ]
)
logger = logging.getLogger(__name__)

# Custom exception classes for better error handling
class DatabaseError(Exception):
    """Exception raised for database operation errors."""
    pass

class ExternalAPIError(Exception):
    """Exception raised for external API call errors."""
    pass

class DataProcessingError(Exception):
    """Exception raised for data processing errors."""
    pass

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
        # Input validation
        if not isinstance(candidate_data, dict):
            logger.warning(f"Invalid candidate_data type: {type(candidate_data)}")
            return None
            
        if linkedin_profile is not None and not isinstance(linkedin_profile, dict):
            logger.warning(f"Invalid linkedin_profile type: {type(linkedin_profile)}")
            linkedin_profile = None
            
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

# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors in request data"""
    error_details = []
    for error in exc.errors():
        error_details.append({
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    logger.warning(f"Validation error: {error_details}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_details, "error": "Request validation failed"}
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle database operation errors"""
    logger.error(f"Database error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc), "error": "Database operation failed"}
    )

@app.exception_handler(ExternalAPIError)
async def external_api_exception_handler(request: Request, exc: ExternalAPIError):
    """Handle external API call errors"""
    logger.error(f"External API error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"detail": str(exc), "error": "External API call failed"}
    )

@app.exception_handler(DataProcessingError)
async def data_processing_exception_handler(request: Request, exc: DataProcessingError):
    """Handle data processing errors"""
    logger.error(f"Data processing error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "error": "Data processing failed"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred", "error": str(exc)}
    )

# Pydantic models for request/response
class SearchRequest(BaseModel):
    prompt: str
    max_candidates: Optional[int] = 3
    include_linkedin: Optional[bool] = True
    
    # Add validation
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Find sales directors at tech companies",
                "max_candidates": 3,
                "include_linkedin": True
            }
        }

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
    
    def validate_behavioral_data_format(self) -> bool:
        """
        Validates the behavioral data format to ensure it contains the new focused insight and scores.
        Provides backward compatibility by checking for both old and new formats.
        
        Returns:
            bool: True if the format is valid, False otherwise
        """
        if not self.behavioral_data:
            return True
            
        try:
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
        except Exception as e:
            logger.error(f"Error validating behavioral data format: {str(e)}")
            return False

# API Routes

@app.get("/")
async def health_check():
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/api/search")
async def create_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """Create a new search request."""
    try:
        # Input validation
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
            
        if request.max_candidates < 1:
            raise HTTPException(status_code=400, detail="max_candidates must be at least 1")
            
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
        try:
            result = store_search_to_database(search_data)
            if not result:
                logger.warning(f"Failed to store search in database for request_id: {request_id}")
                # Continue anyway, as we can still process the search
        except Exception as db_error:
            logger.error(f"Database error storing search: {str(db_error)}")
            # Continue anyway, as we can still process the search
        
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
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValidationError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        logger.error(f"Error creating search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating search: {str(e)}")

@app.get("/api/search/{request_id}")
async def get_search_result(request_id: str):
    """Get the results of a specific search by request ID."""
    try:
        # Input validation
        if not request_id or not request_id.strip():
            raise HTTPException(status_code=400, detail="request_id cannot be empty")
            
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(request_id)
            if str(uuid_obj) != request_id:
                raise ValueError("Invalid UUID format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid request_id format")
        
        # Get the search from the database
        try:
            search_data = get_search_from_database(request_id)
        except Exception as db_error:
            logger.error(f"Database error getting search: {str(db_error)}")
            raise DatabaseError(f"Failed to retrieve search data: {str(db_error)}")
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
        
        # Parse JSON strings back to Python objects
        if "filters" in search_data and isinstance(search_data["filters"], str):
            try:
                search_data["filters"] = json.loads(search_data["filters"])
            except json.JSONDecodeError as json_error:
                logger.warning(f"Failed to parse filters JSON for search {request_id}: {str(json_error)}")
                search_data["filters"] = {}
        
        if "behavioral_data" in search_data and isinstance(search_data["behavioral_data"], str):
            try:
                search_data["behavioral_data"] = json.loads(search_data["behavioral_data"])
            except json.JSONDecodeError as json_error:
                logger.warning(f"Failed to parse behavioral_data JSON for search {request_id}: {str(json_error)}")
                search_data["behavioral_data"] = {}
        
        # Get candidates for this search
        try:
            # Get the database ID for the search (not the request_id)
            search_db_id = search_data.get("id")
            if search_db_id:
                # Get people using the search database ID
                try:
                    candidates = get_people_for_search(search_db_id)
                except Exception as people_error:
                    logger.error(f"Error getting people for search {request_id}: {str(people_error)}")
                    candidates = []
                    
                if candidates:
                    search_data["candidates"] = candidates
                    logger.info(f"Found {len(candidates)} candidates for search {request_id}")
                    
                    # ALWAYS force the status to completed when we have candidates
                    logger.info(f"Forcing status to completed for search {request_id}")
                    search_data["status"] = "completed"
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    
                    # Generate behavioral data if not already present
                    if not search_data.get("behavioral_data"):
                        try:
                            # Use the AI-enhanced behavioral data function
                            behavioral_data = enhance_behavioral_data_ai({}, candidates, search_data.get("prompt", ""))
                            search_data["behavioral_data"] = behavioral_data
                            
                            # Update the database
                            try:
                                db_update = {
                                    "id": search_data["id"],
                                    "request_id": search_data["request_id"],
                                    "status": "completed",
                                    "behavioral_data": json.dumps(behavioral_data),
                                    "completed_at": search_data["completed_at"]
                                }
                                store_search_to_database(db_update)
                                logger.info(f"Updated search with behavioral data for {request_id}")
                            except Exception as update_error:
                                logger.error(f"Error updating search: {str(update_error)}")
                        except Exception as be:
                            logger.error(f"Error generating behavioral data: {str(be)}")
                            # Provide fallback behavioral data
                            search_data["behavioral_data"] = {
                                "behavioral_insight": "This professional responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits.",
                                "scores": {
                                    "cmi": {
                                        "score": 70,
                                        "explanation": "Moderate communication maturity index suggests balanced communication approach."
                                    },
                                    "rbfs": {
                                        "score": 65,
                                        "explanation": "Moderate risk-barrier focus score indicates balanced approach to risk and opportunity."
                                    },
                                    "ias": {
                                        "score": 75,
                                        "explanation": "Moderate to high identity alignment signal suggests professional identifies with their role."
                                    }
                                }
                            }
            else:
                logger.warning(f"Cannot get candidates: search_db_id not found for request_id {request_id}")
        except Exception as e:
            logger.error(f"Error getting candidates for search {request_id}: {str(e)}")
            # Continue even if getting candidates fails
        
        # Always return a response with candidates if available and force status to completed
        if "candidates" in search_data and search_data["candidates"]:
            search_data["status"] = "completed"
            if not search_data.get("completed_at"):
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        return search_data
        
    except HTTPException:
        raise
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error getting search result: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting search result: {str(e)}")

@app.get("/api/search")
async def list_searches():
    """Get a list of all searches with their status."""
    try:
        # Get recent searches from the database
        try:
            searches = get_recent_searches_from_database()
        except Exception as db_error:
            logger.error(f"Database error listing searches: {str(db_error)}")
            raise DatabaseError(f"Failed to retrieve searches: {str(db_error)}")
        
        # Parse JSON strings in each search
        for search in searches:
            if "filters" in search and isinstance(search["filters"], str):
                try:
                    search["filters"] = json.loads(search["filters"])
                except json.JSONDecodeError:
                    search["filters"] = {}
                    
            if "behavioral_data" in search and isinstance(search["behavioral_data"], str):
                try:
                    search["behavioral_data"] = json.loads(search["behavioral_data"])
                except json.JSONDecodeError:
                    search["behavioral_data"] = {}
        
        return {"searches": searches}
        
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error listing searches: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error listing searches: {str(e)}")

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    """Delete a specific search and its results."""
    try:
        # Input validation
        if not request_id or not request_id.strip():
            raise HTTPException(status_code=400, detail="request_id cannot be empty")
            
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(request_id)
            if str(uuid_obj) != request_id:
                raise ValueError("Invalid UUID format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid request_id format")
        
        # Delete the search from the database
        try:
            result = delete_search_from_database(request_id)
            if not result:
                logger.warning(f"Search not found for deletion: {request_id}")
                # Still return success to be idempotent
        except Exception as db_error:
            logger.error(f"Database error deleting search: {str(db_error)}")
            raise DatabaseError(f"Failed to delete search: {str(db_error)}")
        
        return {"message": "Search request deleted from database"}
        
    except HTTPException:
        raise
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error deleting search: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error deleting search: {str(e)}")

@app.get("/api/search/{request_id}/json")
async def get_search_json(request_id: str):
    """Get the raw JSON data for a search (useful for debugging)."""
    try:
        # Input validation
        if not request_id or not request_id.strip():
            raise HTTPException(status_code=400, detail="request_id cannot be empty")
            
        # Validate UUID format
        try:
            uuid_obj = uuid.UUID(request_id)
            if str(uuid_obj) != request_id:
                raise ValueError("Invalid UUID format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid request_id format")
        
        # Get the search from the database
        try:
            search_data = get_search_from_database(request_id)
        except Exception as db_error:
            logger.error(f"Database error getting search JSON: {str(db_error)}")
            raise DatabaseError(f"Failed to retrieve search data: {str(db_error)}")
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
            
        return search_data
        
    except HTTPException:
        raise
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error getting search JSON: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting search JSON: {str(e)}")

@app.get("/api/database/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        # Get recent searches from the database
        try:
            searches = get_recent_searches_from_database()
        except Exception as db_error:
            logger.error(f"Database error getting stats: {str(db_error)}")
            raise DatabaseError(f"Failed to retrieve database statistics: {str(db_error)}")
        
        # Get current exclusions
        try:
            exclusions = get_current_exclusions()
        except Exception as exclusion_error:
            logger.error(f"Error getting exclusions: {str(exclusion_error)}")
            exclusions = []
        
        # Calculate statistics safely
        total_searches = len(searches) if searches else 0
        
        total_candidates = 0
        for search in searches:
            if search.get("candidates") and isinstance(search["candidates"], list):
                total_candidates += len(search["candidates"])
        
        return {
            "database_status": "connected",
            "total_searches": total_searches,
            "total_candidates": total_candidates,
            "total_exclusions": len(exclusions) if exclusions else 0
        }
        
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")

@app.get("/api/exclusions")
async def get_exclusions():
    """Get all currently excluded people."""
    try:
        # Get current exclusions
        try:
            exclusions = get_current_exclusions()
        except Exception as db_error:
            logger.error(f"Database error getting exclusions: {str(db_error)}")
            raise DatabaseError(f"Failed to retrieve exclusions: {str(db_error)}")
        
        return {
            "exclusions": exclusions,
            "count": len(exclusions) if exclusions else 0
        }
        
    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Error getting exclusions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error getting exclusions: {str(e)}")

# Background task for processing searches
async def process_search(
    request_id: str,
    prompt: str,
    max_candidates: int = 3,
    include_linkedin: bool = True
):
    """
    Process a search request in the background with proper flow control.
    
    Args:
        request_id: The unique ID of the search request
        prompt: The user's search prompt
        max_candidates: Maximum number of candidates to return
        include_linkedin: Whether to include LinkedIn profile data
    """
    # Track processing state to prevent loops
    processing_state = {"is_processing": True}
    
    try:
        # Get initial search data
        try:
            search_data = get_search_from_database(request_id)
            if not search_data:
                logger.error(f"Search not found: {request_id}")
                return
        except Exception as db_error:
            logger.error(f"Database error getting search for processing: {str(db_error)}")
            return
            
        # Check if already completed to prevent reprocessing
        if search_data.get("status") == "completed":
            logger.info(f"Search {request_id} already completed, skipping processing")
            return
            
        # Parse the prompt to filters
        try:
            filters = parse_prompt_to_internal_database_filters(prompt)
            logger.info(f"Generated filters from prompt: {filters}")
        except Exception as filter_error:
            logger.error(f"Error parsing prompt to filters: {str(filter_error)}")
            filters = {}  # Use empty filters as fallback
        
        # Search for people via the internal database
        people = []
        try:
            people = await search_people_via_internal_database(filters, max_candidates)
            if not people:
                logger.warning(f"No people found for search {request_id}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout error searching for people for {request_id}")
        except Exception as e:
            logger.error(f"Error searching for people for {request_id}: {str(e)}")
        
        # Scrape LinkedIn profiles if requested
        if include_linkedin and people:
            try:
                # Extract LinkedIn URLs from people objects
                linkedin_urls = []
                for person in people:
                    linkedin_url = person.get("linkedin_url")
                    if linkedin_url:
                        linkedin_urls.append(linkedin_url)
                
                if linkedin_urls:
                    logger.info(f"Attempting to scrape {len(linkedin_urls)} LinkedIn profiles for search {request_id}")
                    
                    # Process LinkedIn profiles in batches to avoid memory issues
                    linkedin_profiles = []
                    batch_size = 5
                    
                    for i in range(0, len(linkedin_urls), batch_size):
                        batch_urls = linkedin_urls[i:i+batch_size]
                        try:
                            # Add timeout for each batch
                            batch_profiles = await asyncio.wait_for(
                                async_scrape_linkedin_profiles(batch_urls),
                                timeout=120  # 2 minute timeout per batch
                            )
                            if batch_profiles:
                                linkedin_profiles.extend(batch_profiles)
                                logger.info(f"Successfully scraped batch {i//batch_size + 1} with {len(batch_profiles)} profiles")
                        except asyncio.TimeoutError:
                            logger.error(f"Timeout scraping LinkedIn batch {i//batch_size + 1} for search {request_id}")
                            # Continue with next batch
                        except Exception as batch_error:
                            logger.error(f"Error scraping LinkedIn batch {i//batch_size + 1} for search {request_id}: {str(batch_error)}")
                            # Continue with next batch
                        
                        # Add a small delay between batches
                        await asyncio.sleep(1)
                    
                    # Merge LinkedIn profile data with existing people data
                    if linkedin_profiles:
                        # Create a mapping of LinkedIn URLs to profile data
                        profile_map = {}
                        for profile in linkedin_profiles:
                            if isinstance(profile, dict) and not profile.get("error"):
                                # Try to match by LinkedIn URL or username
                                profile_url = profile.get("linkedin_url") or profile.get("url")
                                if profile_url:
                                    profile_map[profile_url] = profile
                        
                        # Enhance people with LinkedIn profile data
                        enhanced_count = 0
                        for person in people:
                            linkedin_url = person.get("linkedin_url")
                            if linkedin_url and linkedin_url in profile_map:
                                person["linkedin_profile"] = profile_map[linkedin_url]
                                enhanced_count += 1
                                logger.info(f"Enhanced {person.get('name', 'Unknown')} with LinkedIn profile data")
                        
                        logger.info(f"Successfully enhanced {enhanced_count} profiles with LinkedIn data for search {request_id}")
                    else:
                        logger.warning(f"No LinkedIn profiles returned for search {request_id}")
                else:
                    logger.info(f"No LinkedIn URLs found in people data for search {request_id}")
                    
            except Exception as e:
                logger.error(f"Error in LinkedIn profile processing for search {request_id}: {str(e)}")
                # Continue with existing people data
        
        # Select top candidates
        candidates = []
        try:
            candidates = select_top_candidates(people, prompt, max_candidates)
            logger.info(f"Selected {len(candidates)} top candidates")
        except Exception as e:
            logger.error(f"Error selecting top candidates: {str(e)}")
            candidates = people[:max_candidates] if people else []
            logger.info(f"Using fallback candidate selection: {len(candidates)} candidates")
        
        # Add profile photo URLs
        for candidate in candidates:
            try:
                linkedin_profile = candidate.get("linkedin_profile", {})
                profile_photo_url = extract_profile_photo_url(candidate, linkedin_profile)
                if profile_photo_url:
                    candidate["profile_photo_url"] = profile_photo_url
            except Exception as e:
                logger.error(f"Error extracting profile photo URL: {str(e)}")
                # Continue with next candidate
        
        # Store people in the database
        try:
            search_db_id = search_data.get("id")
            if search_db_id and candidates:
                store_people_to_database(search_db_id, candidates)
                logger.info(f"Stored {len(candidates)} people for search {request_id}")
        except Exception as db_error:
            logger.error(f"Error storing people in database: {str(db_error)}")
            # Continue with processing
        
        # Generate behavioral data using the AI-enhanced function
        try:
            behavioral_data = enhance_behavioral_data_ai({}, candidates, prompt)
            search_data["behavioral_data"] = json.dumps(behavioral_data)  # Convert to JSON string
            logger.info(f"Generated behavioral data: {behavioral_data}")
        except Exception as be:
            logger.error(f"Error generating behavioral data: {str(be)}")
            # Provide fallback behavioral data
            search_data["behavioral_data"] = json.dumps({
                "behavioral_insight": "This professional responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits.",
                "scores": {
                    "cmi": {
                        "score": 70,
                        "explanation": "Moderate communication maturity index suggests balanced communication approach."
                    },
                    "rbfs": {
                        "score": 65,
                        "explanation": "Moderate risk-barrier focus score indicates balanced approach to risk and opportunity."
                    },
                    "ias": {
                        "score": 75,
                        "explanation": "Moderate to high identity alignment signal suggests professional identifies with their role."
                    }
                }
            })
        
        # Update the search data only if we're still processing
        if processing_state["is_processing"]:
            # Mark as no longer processing to prevent duplicate updates
            processing_state["is_processing"] = False
            
            # Update search data
            search_data["status"] = "completed"  # Set status to completed
            search_data["filters"] = json.dumps(filters)  # Convert to JSON string
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Log the search data before storing
            logger.info(f"Updating search {request_id} to completed status")
            
            try:
                # Check if record exists by request_id
                existing_record = get_search_from_database(request_id)
                
                if existing_record:
                    # Update existing record
                    # Ensure we're using the correct primary key
                    search_data["id"] = existing_record["id"]
                    # Store the updated search in the database
                    result = store_search_to_database(search_data)
                    logger.info(f"Search update result: {result}")
                else:
                    logger.error(f"Search record not found for update: {request_id}")
            except Exception as db_error:
                logger.error(f"Error updating search in database: {str(db_error)}")
    except Exception as e:
        logger.error(f"Unhandled error in process_search for {request_id}: {str(e)}")
        logger.error(traceback.format_exc())
        # Try to update the search status to error
        try:
            search_data = get_search_from_database(request_id)
            if search_data:
                search_data["status"] = "error"
                search_data["error"] = str(e)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
        except Exception:
            pass  # Ignore errors in error handling

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)