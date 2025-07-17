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
        Validates the behavioral data format to ensure it contains the new focused insight.
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