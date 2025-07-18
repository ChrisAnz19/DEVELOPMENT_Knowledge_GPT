#!/usr/bin/env python3
"""
Database utilities for Knowledge_GPT
Handles Supabase connection and operations for storing search results and candidate data
"""

import logging
import sys
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import enhanced logging utilities
try:
    from search_data_logger import (
        log_data_flow, 
        log_database_operation, 
        track_prompt_presence,
        log_prompt_integrity_check
    )
    ENHANCED_LOGGING_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced logging utilities not available, using basic logging")
    ENHANCED_LOGGING_AVAILABLE = False
    
    # Fallback functions
    def log_data_flow(*args, **kwargs):
        pass
    def log_database_operation(*args, **kwargs):
        pass
    def track_prompt_presence(*args, **kwargs):
        pass
    def log_prompt_integrity_check(*args, **kwargs):
        return True

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

def store_search_to_database(search_data):
    """
    Enhanced search storage with comprehensive validation and prompt integrity preservation.
    
    Args:
        search_data (dict): Search data to store
        
    Returns:
        int: Database ID of stored search
        
    Raises:
        ValueError: If validation fails
        SearchDataValidationError: If data structure validation fails
        PromptIntegrityError: If prompt integrity cannot be maintained
    """
    # Import validation and transformation utilities
    try:
        from search_data_validator import (
            SearchDataValidator, 
            SearchDataValidationError, 
            PromptIntegrityError
        )
        VALIDATION_AVAILABLE = True
    except ImportError:
        logger.warning("Search data validator not available, using basic validation")
        VALIDATION_AVAILABLE = False
    
    try:
        from data_mapping_transformer import (
            safe_transform_for_storage,
            PRE_STORAGE_CHECKPOINT,
            POST_UPDATE_CHECKPOINT,
            validate_field_mapping
        )
        TRANSFORMATION_AVAILABLE = True
    except ImportError:
        logger.warning("Data mapping transformer not available")
        TRANSFORMATION_AVAILABLE = False
    
    request_id = search_data.get("request_id")
    
    # Enhanced logging: Log data flow at entry point
    log_data_flow("store", request_id or "unknown", search_data, "pre_storage")
    
    # Validation checkpoint: Pre-storage
    if TRANSFORMATION_AVAILABLE:
        is_valid, issues = PRE_STORAGE_CHECKPOINT.validate_at_checkpoint(search_data)
        if not is_valid:
            logger.error(f"Pre-storage checkpoint failed for {request_id}: {issues}")
            raise SearchDataValidationError(f"Pre-storage validation failed: {issues}")
    
    # Pre-storage validation and transformation to ensure prompt integrity
    try:
        if TRANSFORMATION_AVAILABLE:
            # Use enhanced transformation with validation
            validated_data = safe_transform_for_storage(search_data)
            logger.info(f"Enhanced data transformation passed for request_id: {validated_data.get('request_id')}")
        elif VALIDATION_AVAILABLE:
            # Use comprehensive validation
            validated_data = SearchDataValidator.validate_search_data(search_data)
            logger.info(f"Search data validation passed for request_id: {validated_data.get('request_id')}")
        else:
            # Fallback to basic validation
            validated_data = _basic_search_validation(search_data)
            logger.info(f"Basic search data validation passed for request_id: {validated_data.get('request_id')}")
        
        # Update request_id after validation
        request_id = validated_data.get('request_id')
        
        # Validate field mapping if transformation was used
        if TRANSFORMATION_AVAILABLE:
            mapping_valid, mapping_issues = validate_field_mapping(search_data, validated_data)
            if not mapping_valid:
                logger.error(f"Field mapping validation failed for {request_id}: {mapping_issues}")
                raise SearchDataValidationError(f"Field mapping failed: {mapping_issues}")
        
        # Log successful validation
        log_data_flow("store_validated", request_id, validated_data, "post_validation")
        
    except (SearchDataValidationError, PromptIntegrityError, ValueError) as e:
        logger.error(f"Pre-storage validation failed for request_id {request_id}: {e}")
        log_database_operation("validation_failed", "searches", request_id, search_data, None, e)
        raise
    
    # Track prompt presence after validation
    validated_prompt = validated_data.get("prompt")
    has_validated_prompt = bool(validated_prompt and str(validated_prompt).strip())
    track_prompt_presence("post_validation", request_id, has_validated_prompt, 
                         len(str(validated_prompt)) if validated_prompt else 0, 
                         "validated_data")
    
    # Log the data being stored for debugging
    prompt_preview = validated_data.get('prompt', '')[:50] if validated_data.get('prompt') else 'None'
    logger.info(f"Storing validated search data: request_id={request_id}, prompt='{prompt_preview}...', status={validated_data.get('status')}")
    
    try:
        # Log pre-database operation
        log_data_flow("store", request_id, validated_data, "pre_database")
        
        # Enhanced upsert with explicit field handling
        res = supabase.table("searches").upsert(validated_data).execute()
        
        # Log successful database operation
        log_database_operation("upsert", "searches", request_id, validated_data, res, None)
        
        if hasattr(res, 'data') and res.data:
            stored_data = res.data[0]
            
            # Log post-database operation with result
            log_data_flow("store", request_id, stored_data, "post_database")
            
            # Validation checkpoint: Post-update
            if TRANSFORMATION_AVAILABLE:
                is_valid, issues = POST_UPDATE_CHECKPOINT.validate_at_checkpoint(stored_data, validated_prompt)
                if not is_valid:
                    logger.error(f"Post-storage checkpoint failed for {request_id}: {issues}")
                    # Don't raise here as data is already stored, but log the issue
            
            # Verify prompt integrity in stored result
            stored_prompt = stored_data.get('prompt')
            log_prompt_integrity_check(request_id, validated_data.get('prompt'), 
                                     stored_prompt, "post_store")
            
            # Additional integrity check
            if VALIDATION_AVAILABLE:
                try:
                    SearchDataValidator.ensure_prompt_integrity(stored_data)
                    logger.debug(f"Post-storage prompt integrity verified for request_id: {request_id}")
                except PromptIntegrityError as e:
                    logger.error(f"Post-storage prompt integrity check failed: {e}")
                    # Don't raise here as data is already stored, but log the issue
            
            # Return the inserted or updated search's id
            return stored_data.get('id')
        return None
        
    except Exception as e:
        logger.error(f"Error storing search to database: {str(e)}")
        logger.error(f"Search data: {validated_data}")
        
        # Log failed database operation
        log_database_operation("upsert", "searches", request_id, validated_data, None, e)
        
        # Re-raise the exception so calling code can handle it
        raise


def store_search_to_database_enhanced(search_data):
    """
    Alias for the enhanced store_search_to_database function.
    Provided for backward compatibility and explicit enhanced functionality access.
    """
    return store_search_to_database(search_data)


def update_search_in_database(request_id, updates, preserve_existing=True):
    """
    Partial update method that preserves existing prompt data and other fields.
    
    Args:
        request_id (str): Unique identifier for the search
        updates (dict): Fields to update
        preserve_existing (bool): Whether to preserve existing field values
        
    Returns:
        bool: True if update was successful
        
    Raises:
        ValueError: If request_id is invalid or updates are invalid
        PromptIntegrityError: If prompt integrity would be compromised
    """
    # Import validation and transformation utilities
    try:
        from search_data_validator import (
            SearchDataValidator, 
            SearchDataValidationError, 
            PromptIntegrityError
        )
        VALIDATION_AVAILABLE = True
    except ImportError:
        logger.warning("Search data validator not available for partial update")
        VALIDATION_AVAILABLE = False
    
    try:
        from data_mapping_transformer import (
            safe_merge_search_updates,
            safe_transform_for_storage,
            PRE_UPDATE_CHECKPOINT,
            POST_UPDATE_CHECKPOINT,
            validate_field_mapping
        )
        TRANSFORMATION_AVAILABLE = True
    except ImportError:
        logger.warning("Data mapping transformer not available for partial update")
        TRANSFORMATION_AVAILABLE = False
    
    # Validate input parameters
    if not request_id or not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("request_id must be a non-empty string")
    
    if not isinstance(updates, dict):
        raise ValueError("updates must be a dictionary")
    
    if not updates:
        logger.warning(f"No updates provided for request_id: {request_id}")
        return True  # Nothing to update
    
    request_id = request_id.strip()
    
    # Log the update operation start
    log_data_flow("partial_update", request_id, updates, "pre_update")
    logger.info(f"Starting partial update for request_id: {request_id}, fields: {list(updates.keys())}")
    
    # Validation checkpoint: Pre-update
    if TRANSFORMATION_AVAILABLE:
        is_valid, issues = PRE_UPDATE_CHECKPOINT.validate_at_checkpoint(updates)
        if not is_valid:
            logger.warning(f"Pre-update checkpoint issues for {request_id}: {issues}")
            # Don't fail here as updates might be partial and valid when merged
    
    try:
        # If preserving existing data, retrieve current record first
        current_data = None
        if preserve_existing:
            current_data = get_search_from_database(request_id)
            if not current_data:
                logger.error(f"Cannot update non-existent search: {request_id}")
                raise ValueError(f"Search with request_id {request_id} not found")
            
            logger.debug(f"Retrieved current data for preservation: {list(current_data.keys())}")
        
        # Prepare the update data using enhanced merging if available
        if preserve_existing and current_data:
            if TRANSFORMATION_AVAILABLE:
                # Use enhanced safe merging
                update_data = safe_merge_search_updates(current_data, updates)
                logger.debug(f"Enhanced merge completed for request_id: {request_id}")
            else:
                # Fallback to basic merging
                merged_data = current_data.copy()
                merged_data.update(updates)
                update_data = merged_data
                
                # Log data preservation
                log_data_flow("partial_update_merged", request_id, update_data, "post_merge")
                
                # Special handling for prompt preservation
                if 'prompt' not in updates and current_data.get('prompt'):
                    logger.debug(f"Preserving existing prompt for request_id: {request_id}")
                    track_prompt_presence("prompt_preserved", request_id, True, 
                                        len(str(current_data.get('prompt'))), "preserved_from_existing")
        else:
            # Direct update without preservation
            update_data = updates.copy()
            update_data['request_id'] = request_id  # Ensure request_id is included
        
        # Transform and validate the final update data
        if TRANSFORMATION_AVAILABLE:
            try:
                # Use enhanced transformation for storage
                validated_update_data = safe_transform_for_storage(update_data)
                logger.debug(f"Enhanced transformation passed for request_id: {request_id}")
                
                # Validate field mapping
                mapping_valid, mapping_issues = validate_field_mapping(update_data, validated_update_data)
                if not mapping_valid:
                    logger.warning(f"Field mapping issues during update for {request_id}: {mapping_issues}")
                    # Continue with transformation result but log the issues
                
                update_data = validated_update_data
            except Exception as transform_error:
                logger.error(f"Enhanced transformation failed for {request_id}: {transform_error}")
                # Fall back to basic validation
                if VALIDATION_AVAILABLE:
                    update_data = SearchDataValidator.validate_search_data(update_data)
                else:
                    update_data = _basic_search_validation(update_data)
        elif VALIDATION_AVAILABLE:
            try:
                validated_update_data = SearchDataValidator.validate_search_data(update_data)
                logger.debug(f"Partial update data validation passed for request_id: {request_id}")
                update_data = validated_update_data
            except (SearchDataValidationError, PromptIntegrityError) as e:
                logger.error(f"Partial update validation failed for request_id {request_id}: {e}")
                raise
        else:
            # Basic validation
            update_data = _basic_search_validation(update_data)
        
        # Log pre-database update
        log_data_flow("partial_update", request_id, update_data, "pre_database")
        
        # Perform the database update
        res = supabase.table("searches").upsert(update_data).execute()
        
        # Log successful database operation
        log_database_operation("partial_update", "searches", request_id, update_data, res, None)
        
        if hasattr(res, 'data') and res.data:
            updated_data = res.data[0]
            
            # Log post-database operation
            log_data_flow("partial_update", request_id, updated_data, "post_database")
            
            # Validation checkpoint: Post-update
            if TRANSFORMATION_AVAILABLE:
                expected_prompt = update_data.get('prompt')
                is_valid, issues = POST_UPDATE_CHECKPOINT.validate_at_checkpoint(updated_data, expected_prompt)
                if not is_valid:
                    logger.error(f"Post-update checkpoint failed for {request_id}: {issues}")
                    # Don't raise here as update is complete, but log the issue
            
            # Verify prompt integrity if prompt was involved
            if 'prompt' in updates or (preserve_existing and current_data and current_data.get('prompt')):
                updated_prompt = updated_data.get('prompt')
                expected_prompt = updates.get('prompt') or (current_data.get('prompt') if preserve_existing else None)
                
                if expected_prompt:
                    log_prompt_integrity_check(request_id, expected_prompt, updated_prompt, "post_partial_update")
                    
                    # Additional integrity verification
                    if VALIDATION_AVAILABLE:
                        try:
                            SearchDataValidator.ensure_prompt_integrity(updated_data)
                            logger.debug(f"Post-update prompt integrity verified for request_id: {request_id}")
                        except PromptIntegrityError as e:
                            logger.error(f"Post-update prompt integrity check failed: {e}")
                            # Log but don't raise as update is complete
            
            logger.info(f"Successfully updated search {request_id}")
            return True
        else:
            logger.error(f"No data returned from partial update for request_id: {request_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error in partial update for request_id {request_id}: {str(e)}")
        log_database_operation("partial_update", "searches", request_id, updates, None, e)
        raise


def _basic_search_validation(search_data):
    """
    Basic search data validation when SearchDataValidator is not available.
    
    Args:
        search_data (dict): Search data to validate
        
    Returns:
        dict: Validated search data
        
    Raises:
        ValueError: If basic validation fails
    """
    if not isinstance(search_data, dict):
        raise ValueError("Search data must be a dictionary")
    
    validated_data = search_data.copy()
    
    # Validate required fields
    required_fields = ['request_id', 'prompt', 'status']
    for field in required_fields:
        if field not in validated_data or validated_data[field] is None:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate request_id
    request_id = validated_data['request_id']
    if not isinstance(request_id, str):
        raise ValueError("request_id must be a string")
    if not request_id.strip():
        raise ValueError("request_id must be a non-empty string")
    
    # Validate prompt
    prompt = validated_data['prompt']
    if prompt is None:
        raise ValueError("prompt cannot be None")
    if not isinstance(prompt, str):
        # Convert to string if possible
        validated_data['prompt'] = str(prompt)
        prompt = validated_data['prompt']
    
    if not prompt.strip():
        raise ValueError("prompt must be a non-empty string")
    
    # Validate status
    status = validated_data['status']
    if not isinstance(status, str) or not status.strip():
        raise ValueError("status must be a non-empty string")
    
    valid_statuses = {'pending', 'processing', 'completed', 'failed', 'cancelled'}
    if status not in valid_statuses:
        logger.warning(f"Status '{status}' is not in standard valid statuses: {valid_statuses}")
    
    return validated_data

def get_search_from_database(request_id):
    """
    Enhanced database retrieval function with explicit field selection and comprehensive logging.
    
    Args:
        request_id (str): The unique identifier for the search request
        
    Returns:
        dict: Search data with all fields, or None if not found
        
    Raises:
        ValueError: If request_id is invalid
        Exception: For database connection or query errors
    """
    # Validate input
    if not request_id or not isinstance(request_id, str) or not request_id.strip():
        logger.error(f"Invalid request_id provided: {repr(request_id)}")
        raise ValueError("request_id must be a non-empty string")
    
    request_id = request_id.strip()
    
    # Enhanced logging: Log retrieval attempt with detailed context
    log_data_flow("retrieve", request_id, {}, "pre_retrieval")
    logger.info(f"Starting database retrieval for request_id: {request_id}")
    
    try:
        # Explicitly select ALL required fields to ensure prompt is included
        # This addresses the core issue where prompt might be missing from results
        required_fields = [
            "id", 
            "request_id", 
            "status", 
            "prompt",           # Explicitly include prompt field
            "filters", 
            "behavioral_data", 
            "created_at", 
            "completed_at",
            "error"             # Include error field for completeness
        ]
        
        # Log the exact query being executed
        logger.debug(f"Executing database query: SELECT {', '.join(required_fields)} FROM searches WHERE request_id = '{request_id}'")
        
        # Execute query with explicit field selection
        res = supabase.table("searches").select(", ".join(required_fields)).eq("request_id", request_id).execute()
        
        # Log database operation with detailed result analysis
        log_database_operation("select", "searches", request_id, None, res, None)
        
        # Log raw database response for debugging
        logger.debug(f"Database response: data_count={len(res.data) if hasattr(res, 'data') and res.data else 0}")
        
        if hasattr(res, 'data') and res.data:
            if len(res.data) > 1:
                logger.warning(f"Multiple records found for request_id {request_id}, using first record")
            
            retrieved_data = res.data[0]  # Get the first (and should be only) result
            
            # Validate that all expected fields are present
            missing_fields = [field for field in required_fields if field not in retrieved_data]
            if missing_fields:
                logger.warning(f"Retrieved data missing expected fields: {missing_fields}")
            
            # Log successful retrieval with comprehensive data flow tracking
            log_data_flow("retrieve", request_id, retrieved_data, "post_retrieval")
            
            # Detailed prompt analysis and tracking
            retrieved_prompt = retrieved_data.get('prompt')
            has_retrieved_prompt = bool(retrieved_prompt and str(retrieved_prompt).strip())
            prompt_length = len(str(retrieved_prompt)) if retrieved_prompt else 0
            
            track_prompt_presence("post_retrieve", request_id, has_retrieved_prompt,
                                prompt_length, "retrieved_from_db")
            
            # Enhanced logging with field-by-field analysis
            prompt_preview = retrieved_prompt[:50] if retrieved_prompt else 'None'
            logger.info(f"Successfully retrieved search data:")
            logger.info(f"  - request_id: {request_id}")
            logger.info(f"  - status: {retrieved_data.get('status')}")
            logger.info(f"  - prompt: '{prompt_preview}{'...' if prompt_length > 50 else ''}' (length: {prompt_length})")
            logger.info(f"  - has_filters: {bool(retrieved_data.get('filters'))}")
            logger.info(f"  - has_behavioral_data: {bool(retrieved_data.get('behavioral_data'))}")
            logger.info(f"  - created_at: {retrieved_data.get('created_at')}")
            logger.info(f"  - completed_at: {retrieved_data.get('completed_at')}")
            
            # Critical check for null prompt in retrieved data
            if not has_retrieved_prompt:
                logger.error(f"CRITICAL: Retrieved search {request_id} has null/empty prompt!")
                logger.error(f"  - Raw prompt value: {repr(retrieved_prompt)}")
                logger.error(f"  - Prompt type: {type(retrieved_prompt)}")
                logger.error(f"  - All retrieved fields: {list(retrieved_data.keys())}")
                
                # Log this as a data integrity issue
                track_prompt_presence("integrity_violation", request_id, False, 0, 
                                    f"null_prompt_in_db_result: {repr(retrieved_prompt)}")
            else:
                logger.debug(f"Prompt integrity verified for request_id {request_id}")
            
            return retrieved_data
            
        else:
            # Enhanced logging when no data found
            logger.info(f"No search record found for request_id: {request_id}")
            logger.debug(f"Database response details: {res}")
            track_prompt_presence("retrieve_not_found", request_id, False, 0, "no_data_found")
            return None
            
    except ValueError as ve:
        # Re-raise validation errors
        logger.error(f"Validation error in get_search_from_database: {ve}")
        raise
        
    except Exception as e:
        # Enhanced error logging and handling
        logger.error(f"Database error retrieving search {request_id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.debug(f"Full error details: {e}", exc_info=True)
        
        # Log failed database operation with detailed error context
        log_database_operation("select", "searches", request_id, None, None, e)
        track_prompt_presence("retrieve_error", request_id, False, 0, f"error: {str(e)}")
        
        # For debugging purposes, don't suppress the error completely
        # but provide a clear indication of what went wrong
        if "not found" in str(e).lower() or "no rows" in str(e).lower():
            logger.info(f"Search {request_id} not found in database")
            return None
        else:
            # For other database errors, re-raise to allow proper error handling upstream
            logger.error(f"Unexpected database error for request_id {request_id}, re-raising")
            raise

def get_recent_searches_from_database(limit=10):
    res = supabase.table("searches").select("id, request_id, status, prompt, filters, behavioral_data, created_at, completed_at").order("created_at", desc=True).limit(limit).execute()
    return res.data

def store_people_to_database(search_id, people):
    """
    Enhanced people storage with comprehensive field mapping and data preservation.
    
    Args:
        search_id: Database ID of the search
        people: List of people data to store
    """
    # Insert each person with the search_id, but only include fields that exist in the schema
    schema_fields = {
        'search_id', 'name', 'title', 'company', 'email', 'linkedin_url', 
        'profile_photo_url', 'location', 'accuracy', 'reasons', 
        'linkedin_profile', 'linkedin_posts', 'behavioral_data'
    }
    
    filtered_people = []
    for person in people:
        filtered_person = {'search_id': search_id}
        
        # Enhanced field mapping with fallbacks and data preservation
        for field in schema_fields:
            value = None
            
            if field == 'company':
                # Try multiple sources for company name
                value = (
                    person.get('company') or
                    (person.get('organization', {}).get('name') if isinstance(person.get('organization'), dict) else None) or
                    (person.get('organization') if isinstance(person.get('organization'), str) else None) or
                    person.get('current_company') or
                    person.get('employer')
                )
            elif field == 'linkedin_url':
                # Ensure LinkedIn URL is properly formatted
                linkedin_url = person.get('linkedin_url')
                if linkedin_url:
                    if not linkedin_url.startswith('http'):
                        value = f"https://{linkedin_url}"
                    else:
                        value = linkedin_url
            elif field == 'profile_photo_url':
                # Try multiple sources for profile photo
                value = (
                    person.get('profile_photo_url') or
                    person.get('profile_picture_url') or
                    person.get('photo_url') or
                    person.get('avatar_url') or
                    person.get('image_url')
                )
            elif field == 'behavioral_data':
                # Convert behavioral_data to JSON string if it's a dict
                if field in person and person[field] is not None:
                    if isinstance(person[field], dict):
                        value = json.dumps(person[field])
                    else:
                        value = person[field]
            elif field == 'linkedin_profile':
                # Convert linkedin_profile to JSON string if it's a dict
                if field in person and person[field] is not None:
                    if isinstance(person[field], dict):
                        value = json.dumps(person[field])
                    else:
                        value = person[field]
            else:
                # Standard field mapping
                value = person.get(field)
            
            # Only include non-null values
            if value is not None:
                filtered_person[field] = value
        
        # Log the person being stored for debugging
        logger.debug(f"Storing person: {filtered_person.get('name', 'Unknown')} at {filtered_person.get('company', 'Unknown Company')} - LinkedIn: {bool(filtered_person.get('linkedin_url'))}, Photo: {bool(filtered_person.get('profile_photo_url'))}")
        
        filtered_people.append(filtered_person)
    
    if filtered_people:
        try:
            # Log the fields that will be stored for each person
            for person in filtered_people:
                present_fields = [field for field in schema_fields if field in person]
                missing_fields = [field for field in schema_fields if field not in person]
                logger.info(f"Fields for {person.get('name', 'Unknown')}: Present={present_fields}, Missing={missing_fields}")
                
                # Log LinkedIn-specific fields
                linkedin_fields = ['linkedin_url', 'profile_photo_url', 'company']
                for field in linkedin_fields:
                    logger.info(f"LinkedIn field '{field}' for {person.get('name', 'Unknown')}: {repr(person.get(field))}")
            
            # Insert without specifying columns to ensure all fields are included
            result = supabase.table("people").insert(filtered_people).execute()
            logger.info(f"Successfully stored {len(filtered_people)} people to database for search_id {search_id}")
            
            # Log stored data for verification
            for person in filtered_people:
                logger.debug(f"Stored: {person.get('name')} - Company: {person.get('company', 'N/A')}, LinkedIn: {person.get('linkedin_url', 'N/A')[:50]}{'...' if len(person.get('linkedin_url', '')) > 50 else ''}, Photo: {'Yes' if person.get('profile_photo_url') else 'No'}")
            
            return result
        except Exception as e:
            logger.error(f"Error storing people to database: {str(e)}")
            logger.error(f"People data: {json.dumps(filtered_people, indent=2, default=str)}")
            raise
    else:
        logger.warning(f"No people to store for search_id {search_id}")
        return None

def get_people_for_search(search_id):
    """
    Get people associated with a search with comprehensive diagnostic logging.
    
    Args:
        search_id: Database ID of the search
        
    Returns:
        List of candidate data with all fields
    """
    # Define the fields we're selecting to ensure LinkedIn data fields are included
    selected_fields = [
        "id", "search_id", "name", "title", "company", "email", 
        "linkedin_url", "profile_photo_url", "location", "accuracy", 
        "reasons", "linkedin_profile", "linkedin_posts", "behavioral_data", "created_at"
    ]
    
    # Define required LinkedIn data fields for validation
    required_linkedin_fields = ["company", "linkedin_url", "profile_photo_url"]
    
    # Log the exact database query being executed
    logger.info(f"[DIAGNOSTIC] Executing database query for search_id {search_id}")
    logger.info(f"[DIAGNOSTIC] Selected fields: {', '.join(selected_fields)}")
    logger.info(f"[DIAGNOSTIC] Query: SELECT {', '.join(selected_fields)} FROM people WHERE search_id = {search_id}")
    
    try:
        res = supabase.table("people").select(", ".join(selected_fields)).eq("search_id", search_id).execute()
    except Exception as e:
        logger.error(f"[ERROR] Database query failed for search_id {search_id}: {str(e)}")
        logger.error(f"[ERROR] This may indicate missing fields in database schema")
        return []
    
    # Log raw database response details
    logger.info(f"[DIAGNOSTIC] Database response for search_id {search_id}:")
    logger.info(f"[DIAGNOSTIC] - Response has data: {hasattr(res, 'data')}")
    logger.info(f"[DIAGNOSTIC] - Data count: {len(res.data) if hasattr(res, 'data') and res.data else 0}")
    
    # Validate that database response contains expected structure
    if not hasattr(res, 'data'):
        logger.error(f"[ERROR] Database response missing 'data' attribute for search_id {search_id}")
        return []
    
    if hasattr(res, 'data') and res.data:
        logger.info(f"[DIAGNOSTIC] Retrieved {len(res.data)} candidates from database")
        
        # Validate that all expected fields are present in database schema
        validated_candidates = []
        schema_validation_errors = []
        
        # Log field-by-field analysis for each candidate
        for i, person in enumerate(res.data):
            logger.info(f"[DIAGNOSTIC] Candidate {i+1} ({person.get('name', 'Unknown')}) database fields:")
            
            # Validate that all selected fields are present in the result
            missing_fields = []
            for field in selected_fields:
                if field not in person:
                    missing_fields.append(field)
            
            if missing_fields:
                error_msg = f"Missing fields in database schema for candidate {i+1}: {missing_fields}"
                logger.error(f"[ERROR] {error_msg}")
                schema_validation_errors.append(error_msg)
            
            # Check critical LinkedIn data fields with validation
            critical_fields = ['company', 'linkedin_url', 'profile_photo_url']
            missing_critical_fields = []
            
            for field in critical_fields:
                if field not in person:
                    missing_critical_fields.append(field)
                    logger.error(f"[ERROR] Critical field '{field}' missing from database schema")
                    continue
                    
                value = person.get(field)
                has_value = bool(value and str(value).strip())
                logger.info(f"[DIAGNOSTIC] - {field}: {'✓' if has_value else '✗'} ({repr(value)})")
                
                # Add validation for required LinkedIn fields
                if field in required_linkedin_fields and not has_value:
                    logger.warning(f"[VALIDATION] Required LinkedIn field '{field}' is null/empty for candidate {person.get('name', 'Unknown')}")
            
            # Log schema validation errors for this candidate
            if missing_critical_fields:
                error_msg = f"Critical LinkedIn fields missing from database schema: {missing_critical_fields}"
                logger.error(f"[ERROR] {error_msg}")
                schema_validation_errors.append(error_msg)
            
            # Check all other fields
            other_fields = [f for f in selected_fields if f not in critical_fields]
            for field in other_fields:
                if field not in person:
                    continue  # Already logged in missing_fields check
                    
                value = person.get(field)
                has_value = bool(value and str(value).strip()) if field != 'behavioral_data' else bool(value)
                logger.info(f"[DIAGNOSTIC] - {field}: {'✓' if has_value else '✗'} ({'present' if has_value else 'missing/null'})")
            
            # Parse behavioral_data JSON strings back to Python objects
            if person.get('behavioral_data') and isinstance(person['behavioral_data'], str):
                try:
                    person['behavioral_data'] = json.loads(person['behavioral_data'])
                    logger.info(f"[DIAGNOSTIC] - behavioral_data: Successfully parsed JSON")
                except json.JSONDecodeError:
                    logger.warning(f"[DIAGNOSTIC] - behavioral_data: Failed to parse JSON for person {person.get('id')}")
                    person['behavioral_data'] = None
            
            # Add candidate to validated list only if no critical schema errors
            if not missing_critical_fields:
                validated_candidates.append(person)
            else:
                logger.error(f"[ERROR] Excluding candidate {person.get('name', 'Unknown')} due to missing critical fields")
        
        # Log overall schema validation results
        if schema_validation_errors:
            logger.error(f"[ERROR] Schema validation errors found for search_id {search_id}:")
            for error in schema_validation_errors:
                logger.error(f"[ERROR] - {error}")
            
            # If all candidates have schema errors, this indicates a database schema issue
            if not validated_candidates:
                logger.error(f"[ERROR] All candidates excluded due to schema validation errors")
                logger.error(f"[ERROR] This indicates missing fields in the database schema")
                return []
        
        logger.info(f"[VALIDATION] Successfully validated {len(validated_candidates)} out of {len(res.data)} candidates")
        return validated_candidates
        
    else:
        logger.warning(f"[DIAGNOSTIC] No candidates found in database for search_id {search_id}")
        return []

def is_person_excluded_in_database(email, days=30):
    # Check if a person with this email exists in the people table within the last N days
    from datetime import datetime, timedelta
    import pytz
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

def delete_search_from_database(request_id):
    # Delete search and cascade to people
    supabase.table("searches").delete().eq("request_id", request_id).execute()
    return True

def get_current_exclusions(days=30):
    """Return a list of people (email, name, company, created_at) in the people table within the last N days."""
    from datetime import datetime, timedelta
    import pytz
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

if __name__ == "__main__":
    # Test database connection
    print("🧪 Testing Database Connection...")
    
    # The init_database function is removed as per the new_code.
    # The direct calls to the new functions are added.
    
    # Test a simple query
    res = supabase.table("searches").select("id, request_id, status, prompt, created_at").limit(1).execute()
    if res.data:
        print(f"⏰ Current database time: {res.data[0]['created_at']}")
    else:
        print("No data found in searches table.")
        
    # Show table structure
    res = supabase.table("searches").select("id, request_id, status, prompt, created_at").limit(1).execute()
    if res.data:
        print("\n📋 Database Tables:")
        print(f"  - Table: searches")
        print(f"    - Columns: {list(res.data[0].keys())}")
    else:
        print("\n📋 Database Tables:")
        print("  - No data found in searches table to show columns.")
    
    # The original db_manager.disconnect() is removed as per the new_code.
    # The supabase client does not have a direct disconnect method like psycopg2.
    # The supabase client manages its own connection pool. 