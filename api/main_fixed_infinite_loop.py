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
# Import the fixed database functions
from database_fixed import (
    store_search_to_database, get_search_from_database, 
    get_recent_searches_from_database, delete_search_from_database,
    store_people_to_database, get_people_for_search, is_person_excluded_in_database,
    get_current_exclusions
)
# Import the behavioral_metrics_ai module instead of behavioral_metrics
from behavioral_metrics_ai import enhance_behavioral_data_ai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    processing_state = {"is_processing": True, "status_updated": False}
    
    # Set a global timeout for the entire process
    global_timeout = 600  # 10 minutes
    start_time = time.time()
    
    try:
        # Get initial search data
        search_data = get_search_from_database(request_id)
        if not search_data:
            logger.error(f"Search not found: {request_id}")
            return
            
        # Check if already completed to prevent reprocessing
        if search_data.get("status") == "completed":
            logger.info(f"Search {request_id} already completed, skipping processing")
            return
        
        # Update search status to processing if it's not already
        if search_data.get("status") != "processing":
            try:
                search_data["status"] = "processing"
                store_search_to_database(search_data)
                logger.info(f"Updated search {request_id} status to processing")
            except Exception as e:
                logger.error(f"Error updating search status: {str(e)}")
        
        # Parse the prompt to filters
        filters = parse_prompt_to_internal_database_filters(prompt)
        
        # Search for people via the internal database with timeout
        people = []
        try:
            # Check if we've exceeded the global timeout
            if time.time() - start_time > global_timeout:
                raise TimeoutError("Global timeout exceeded")
                
            # Set a timeout for the search operation
            people = await asyncio.wait_for(
                search_people_via_internal_database(filters, max_candidates),
                timeout=120  # 2 minute timeout
            )
            if not people:
                logger.warning(f"No people found for search {request_id}")
                people = []
        except asyncio.TimeoutError:
            logger.error(f"Timeout error searching for people for {request_id}")
            people = []
            # Update search status to failed
            if not processing_state["status_updated"]:
                processing_state["status_updated"] = True
                search_data["status"] = "failed"
                search_data["error"] = "Search operation timed out"
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
                logger.info(f"Updated search {request_id} status to failed due to timeout")
            return
        except TimeoutError as e:
            logger.error(f"Global timeout exceeded for search {request_id}")
            # Update search status to failed
            if not processing_state["status_updated"]:
                processing_state["status_updated"] = True
                search_data["status"] = "failed"
                search_data["error"] = str(e)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
                logger.info(f"Updated search {request_id} status to failed due to global timeout")
            return
        except Exception as e:
            logger.error(f"Error searching for people for {request_id}: {str(e)}")
            people = []
            # Update search status to failed for serious errors
            if not processing_state["status_updated"]:
                processing_state["status_updated"] = True
                search_data["status"] = "failed"
                search_data["error"] = str(e)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
                logger.info(f"Updated search {request_id} status to failed due to error: {str(e)}")
            return
        
        # Scrape LinkedIn profiles if requested
        if include_linkedin and people and processing_state["is_processing"]:
            try:
                # Check if we've exceeded the global timeout
                if time.time() - start_time > global_timeout:
                    raise TimeoutError("Global timeout exceeded")
                    
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
                        # Check if we've exceeded the global timeout
                        if time.time() - start_time > global_timeout:
                            logger.warning("Global timeout exceeded, stopping LinkedIn scraping")
                            break
                            
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
                    
            except TimeoutError:
                logger.error(f"Global timeout exceeded during LinkedIn processing for search {request_id}")
                # Continue with existing people data
            except Exception as e:
                logger.error(f"Error in LinkedIn profile processing for search {request_id}: {str(e)}")
                # Continue with existing people data
        
        # Select top candidates if we're still processing
        candidates = []
        if people and processing_state["is_processing"]:
            try:
                # Check if we've exceeded the global timeout
                if time.time() - start_time > global_timeout:
                    raise TimeoutError("Global timeout exceeded")
                    
                candidates = select_top_candidates(people, prompt, max_candidates)
                if not candidates:
                    candidates = people[:max_candidates] if people else []
            except Exception as e:
                logger.error(f"Error selecting top candidates: {str(e)}")
                candidates = people[:max_candidates] if people else []
        
        # Add profile photo URLs if we're still processing
        if candidates and processing_state["is_processing"]:
            try:
                # Check if we've exceeded the global timeout
                if time.time() - start_time > global_timeout:
                    raise TimeoutError("Global timeout exceeded")
                    
                for candidate in candidates:
                    try:
                        linkedin_profile = candidate.get("linkedin_profile", {})
                        profile_photo_url = extract_profile_photo_url(candidate, linkedin_profile)
                        if profile_photo_url:
                            candidate["profile_photo_url"] = profile_photo_url
                    except Exception as e:
                        logger.error(f"Error extracting profile photo URL: {str(e)}")
                        # Continue with next candidate
            except TimeoutError:
                logger.error(f"Global timeout exceeded during photo URL extraction for search {request_id}")
        
        # Generate behavioral data if we're still processing
        behavioral_data = None
        if candidates and processing_state["is_processing"]:
            try:
                # Check if we've exceeded the global timeout
                if time.time() - start_time > global_timeout:
                    raise TimeoutError("Global timeout exceeded")
                    
                behavioral_data = enhance_behavioral_data_ai({}, candidates, prompt)
                logger.info(f"Generated behavioral data for search {request_id}")
            except Exception as be:
                logger.error(f"Error generating behavioral data: {str(be)}")
                # Provide fallback behavioral data
                behavioral_data = {
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
        
        # Store the candidates in the database if we're still processing
        if candidates and processing_state["is_processing"]:
            try:
                # Check if we've exceeded the global timeout
                if time.time() - start_time > global_timeout:
                    raise TimeoutError("Global timeout exceeded")
                    
                # Get the database ID for the search
                search_db_id = search_data.get("id")
                if search_db_id:
                    # Store the candidates
                    store_people_to_database(search_db_id, candidates)
                    logger.info(f"Stored {len(candidates)} candidates for search {request_id}")
                else:
                    logger.error(f"Cannot store candidates: search_db_id not found for request_id {request_id}")
            except Exception as e:
                logger.error(f"Error storing candidates for search {request_id}: {str(e)}")
                # Continue even if storing candidates fails
        
        # Update the search data only if we're still processing and haven't updated the status yet
        if processing_state["is_processing"] and not processing_state["status_updated"]:
            try:
                # Mark as no longer processing and status updated to prevent duplicate updates
                processing_state["is_processing"] = False
                processing_state["status_updated"] = True
                
                # Update search data
                search_data["status"] = "completed"  # Set status to completed
                search_data["filters"] = json.dumps(filters)  # Convert to JSON string
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                
                if behavioral_data:
                    search_data["behavioral_data"] = json.dumps(behavioral_data)
                
                # Log the search data before storing
                logger.info(f"Updating search {request_id} to completed status")
                
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
            except Exception as update_error:
                logger.error(f"Error updating search: {str(update_error)}")
                
    except TimeoutError:
        logger.error(f"Global timeout exceeded for search {request_id}")
        # Update search status to failed if we haven't updated it yet
        if not processing_state["status_updated"]:
            try:
                processing_state["status_updated"] = True
                search_data = get_search_from_database(request_id)
                if search_data:
                    search_data["status"] = "failed"
                    search_data["error"] = "Search processing timed out"
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
                    logger.info(f"Updated search {request_id} status to failed due to timeout")
            except Exception as e:
                logger.error(f"Error updating search status after timeout: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}")
        # Update search status to failed if we haven't updated it yet
        if not processing_state["status_updated"]:
            try:
                processing_state["status_updated"] = True
                search_data = get_search_from_database(request_id)
                if search_data:
                    search_data["status"] = "failed"
                    search_data["error"] = str(e)
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
                    logger.info(f"Updated search {request_id} status to failed due to error")
            except Exception as update_error:
                logger.error(f"Error updating search status after error: {str(update_error)}")
    finally:
        # Log the total processing time
        processing_time = time.time() - start_time
        logger.info(f"Search {request_id} processing completed in {processing_time:.2f} seconds")
        
        # Ensure we're no longer processing
        processing_state["is_processing"] = False

# Function to extract profile photo URL (needed for the process_search function)
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