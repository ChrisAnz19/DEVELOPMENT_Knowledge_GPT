#!/usr/bin/env python3
"""
Data Mapping and Transformation Module

This module provides utilities to fix data mapping and transformation issues
that might cause prompt data loss during search processing pipeline.

Requirements addressed:
- 2.1: Preserve prompt data throughout data flow
- 2.2: Correct mapping of prompt fields between data structures  
- 2.4: Maintain data integrity through all operations
"""

import logging
import json
import copy
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

try:
    from search_data_validator import (
        SearchDataValidator, 
        SearchDataValidationError, 
        PromptIntegrityError,
        PromptIntegrityChecker
    )
    VALIDATION_AVAILABLE = True
except ImportError:
    logger.warning("Search data validator not available")
    VALIDATION_AVAILABLE = False
    
    # Fallback classes
    class SearchDataValidationError(Exception):
        pass
    class PromptIntegrityError(Exception):
        pass

try:
    from search_data_logger import log_data_flow, track_prompt_presence
    LOGGING_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced logging not available")
    LOGGING_AVAILABLE = False
    
    # Fallback functions
    def log_data_flow(*args, **kwargs):
        pass
    def track_prompt_presence(*args, **kwargs):
        pass


class DataMappingError(Exception):
    """Raised when data mapping operations fail"""
    pass


class TransformationError(Exception):
    """Raised when data transformation operations fail"""
    pass


class SearchDataTransformer:
    """
    Handles safe data transformations while preserving prompt integrity.
    
    This class provides methods to transform search data between different
    formats and structures while ensuring prompt data is never lost.
    """
    
    # Critical fields that must never be lost during transformations
    CRITICAL_FIELDS = {
        'request_id', 'prompt', 'status'
    }
    
    # Fields that should be preserved if present
    PRESERVE_FIELDS = {
        'id', 'created_at', 'completed_at', 'filters', 'behavioral_data', 'error'
    }
    
    # All known fields in the system
    ALL_KNOWN_FIELDS = CRITICAL_FIELDS | PRESERVE_FIELDS | {
        'max_candidates', 'include_linkedin'
    }
    
    @staticmethod
    def safe_transform_for_storage(search_data: Dict[str, Any], 
                                 preserve_existing: bool = True) -> Dict[str, Any]:
        """
        Safely transform search data for database storage.
        
        Args:
            search_data: Original search data
            preserve_existing: Whether to preserve existing field values
            
        Returns:
            Dict: Transformed data safe for storage
            
        Raises:
            TransformationError: If transformation fails
            PromptIntegrityError: If prompt integrity is compromised
        """
        if not isinstance(search_data, dict):
            raise TransformationError(f"Search data must be dict, got {type(search_data)}")
        
        request_id = search_data.get('request_id', 'unknown')
        
        # Log transformation start
        log_data_flow("transform_for_storage", request_id, search_data, "pre_transform")
        
        try:
            # Create a deep copy to avoid modifying original
            transformed_data = copy.deepcopy(search_data)
            
            # Ensure critical fields are present and valid
            SearchDataTransformer._ensure_critical_fields(transformed_data)
            
            # Validate prompt integrity before transformation
            original_prompt = transformed_data.get('prompt')
            if VALIDATION_AVAILABLE:
                SearchDataValidator.ensure_prompt_integrity(transformed_data)
            
            # Transform JSON fields to strings for database storage
            transformed_data = SearchDataTransformer._normalize_json_fields(transformed_data)
            
            # Ensure timestamps are properly formatted
            transformed_data = SearchDataTransformer._normalize_timestamps(transformed_data)
            
            # Validate prompt integrity after transformation
            final_prompt = transformed_data.get('prompt')
            if str(original_prompt).strip() != str(final_prompt).strip():
                raise PromptIntegrityError(
                    f"Prompt changed during transformation: '{original_prompt}' -> '{final_prompt}'"
                )
            
            # Log successful transformation
            log_data_flow("transform_for_storage", request_id, transformed_data, "post_transform")
            track_prompt_presence("post_transform", request_id, bool(final_prompt and str(final_prompt).strip()),
                                len(str(final_prompt)) if final_prompt else 0, "transformed_for_storage")
            
            logger.debug(f"Successfully transformed data for storage: {request_id}")
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error transforming data for storage: {e}")
            log_data_flow("transform_error", request_id, {"error": str(e)}, "transform_failed")
            raise TransformationError(f"Failed to transform data for storage: {e}")
    
    @staticmethod
    def safe_transform_for_api_response(search_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely transform search data for API response.
        
        Args:
            search_data: Database search data
            
        Returns:
            Dict: Transformed data for API response
            
        Raises:
            TransformationError: If transformation fails
        """
        if not isinstance(search_data, dict):
            raise TransformationError(f"Search data must be dict, got {type(search_data)}")
        
        request_id = search_data.get('request_id', 'unknown')
        
        try:
            # Create a copy for transformation
            transformed_data = copy.deepcopy(search_data)
            
            # Parse JSON fields back to objects for API response
            transformed_data = SearchDataTransformer._parse_json_fields(transformed_data)
            
            # Ensure prompt is present and valid
            if not transformed_data.get('prompt') or not str(transformed_data['prompt']).strip():
                logger.warning(f"API response has invalid prompt for {request_id}")
                # Don't modify the prompt here - let the API handle the fallback
            
            # Remove internal database fields from API response
            api_data = SearchDataTransformer._filter_for_api_response(transformed_data)
            
            logger.debug(f"Successfully transformed data for API response: {request_id}")
            return api_data
            
        except Exception as e:
            logger.error(f"Error transforming data for API response: {e}")
            raise TransformationError(f"Failed to transform data for API response: {e}")
    
    @staticmethod
    def safe_merge_search_updates(existing_data: Dict[str, Any], 
                                updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Safely merge search updates while preserving critical fields.
        
        Args:
            existing_data: Current search data from database
            updates: New data to merge
            
        Returns:
            Dict: Merged data with preserved critical fields
            
        Raises:
            TransformationError: If merge fails
            PromptIntegrityError: If prompt integrity is compromised
        """
        if not isinstance(existing_data, dict) or not isinstance(updates, dict):
            raise TransformationError("Both existing_data and updates must be dictionaries")
        
        request_id = existing_data.get('request_id') or updates.get('request_id', 'unknown')
        
        try:
            # Start with existing data to preserve all fields
            merged_data = copy.deepcopy(existing_data)
            
            # Track original prompt for integrity checking
            original_prompt = existing_data.get('prompt')
            update_prompt = updates.get('prompt')
            
            # Apply updates, but be careful with critical fields
            for field, value in updates.items():
                if field in SearchDataTransformer.CRITICAL_FIELDS:
                    # Special handling for critical fields
                    if field == 'prompt':
                        # Only update prompt if the new value is valid and non-empty
                        if value and str(value).strip():
                            merged_data[field] = value
                        elif not original_prompt or not str(original_prompt).strip():
                            # Only allow prompt update if existing is also invalid
                            merged_data[field] = value
                        # Otherwise, keep the existing prompt
                    else:
                        # For other critical fields, always update
                        merged_data[field] = value
                else:
                    # For non-critical fields, update normally
                    merged_data[field] = value
            
            # Validate final prompt integrity
            final_prompt = merged_data.get('prompt')
            if not final_prompt or not str(final_prompt).strip():
                if original_prompt and str(original_prompt).strip():
                    # Restore original prompt if merge resulted in invalid prompt
                    merged_data['prompt'] = original_prompt
                    logger.warning(f"Restored original prompt after merge for {request_id}")
                else:
                    raise PromptIntegrityError(f"Merge resulted in invalid prompt for {request_id}")
            
            # Log successful merge
            log_data_flow("merge_updates", request_id, merged_data, "post_merge")
            track_prompt_presence("post_merge", request_id, bool(merged_data.get('prompt', '').strip()),
                                len(str(merged_data.get('prompt', ''))), "merged_data")
            
            logger.debug(f"Successfully merged search updates: {request_id}")
            return merged_data
            
        except Exception as e:
            logger.error(f"Error merging search updates: {e}")
            raise TransformationError(f"Failed to merge search updates: {e}")
    
    @staticmethod
    def validate_field_mapping(source_data: Dict[str, Any], 
                             target_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that field mapping preserved all critical data.
        
        Args:
            source_data: Original data before mapping
            target_data: Data after mapping
            
        Returns:
            Tuple: (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Check critical fields
            for field in SearchDataTransformer.CRITICAL_FIELDS:
                source_value = source_data.get(field)
                target_value = target_data.get(field)
                
                if field == 'prompt':
                    # Special validation for prompt field
                    source_prompt = str(source_value).strip() if source_value else ''
                    target_prompt = str(target_value).strip() if target_value else ''
                    
                    if source_prompt and not target_prompt:
                        issues.append(f"Prompt lost during mapping: '{source_prompt[:50]}...' -> empty")
                    elif source_prompt != target_prompt:
                        issues.append(f"Prompt changed during mapping: '{source_prompt[:30]}...' -> '{target_prompt[:30]}...'")
                else:
                    # Standard field validation
                    if source_value is not None and target_value is None:
                        issues.append(f"Critical field {field} lost during mapping")
                    elif source_value != target_value:
                        issues.append(f"Critical field {field} changed during mapping: {source_value} -> {target_value}")
            
            # Check for unexpected field loss
            source_fields = set(source_data.keys())
            target_fields = set(target_data.keys())
            lost_fields = source_fields - target_fields
            
            # Only report loss of known important fields
            important_lost_fields = lost_fields & SearchDataTransformer.PRESERVE_FIELDS
            if important_lost_fields:
                issues.append(f"Important fields lost during mapping: {important_lost_fields}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Error validating field mapping: {e}")
            return False, issues
    
    @staticmethod
    def _ensure_critical_fields(data: Dict[str, Any]) -> None:
        """Ensure all critical fields are present and valid."""
        for field in SearchDataTransformer.CRITICAL_FIELDS:
            if field not in data or data[field] is None:
                if field == 'prompt':
                    raise PromptIntegrityError(f"Critical field {field} is missing or None")
                else:
                    raise TransformationError(f"Critical field {field} is missing or None")
        
        # Additional prompt validation
        prompt = data['prompt']
        if not isinstance(prompt, str) or not prompt.strip():
            raise PromptIntegrityError(f"Prompt must be a non-empty string, got: {repr(prompt)}")
    
    @staticmethod
    def _normalize_json_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert dict fields to JSON strings for database storage."""
        normalized_data = data.copy()
        json_fields = ['filters', 'behavioral_data']
        
        for field in json_fields:
            if field in normalized_data and normalized_data[field] is not None:
                value = normalized_data[field]
                if isinstance(value, dict):
                    try:
                        normalized_data[field] = json.dumps(value)
                    except (TypeError, ValueError) as e:
                        logger.warning(f"Failed to serialize {field} to JSON: {e}")
                        # Keep original value if serialization fails
        
        return normalized_data
    
    @staticmethod
    def _parse_json_fields(data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON string fields back to dicts for API responses."""
        parsed_data = data.copy()
        json_fields = ['filters', 'behavioral_data']
        
        for field in json_fields:
            if field in parsed_data and parsed_data[field] is not None:
                value = parsed_data[field]
                if isinstance(value, str) and value.strip():
                    try:
                        parsed_data[field] = json.loads(value)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse {field} JSON: {e}")
                        # Keep original string value if parsing fails
        
        return parsed_data
    
    @staticmethod
    def _normalize_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure timestamps are properly formatted."""
        normalized_data = data.copy()
        timestamp_fields = ['created_at', 'completed_at']
        
        for field in timestamp_fields:
            if field in normalized_data and normalized_data[field] is not None:
                timestamp = normalized_data[field]
                if isinstance(timestamp, datetime):
                    normalized_data[field] = timestamp.isoformat()
                # If it's already a string, assume it's properly formatted
        
        return normalized_data
    
    @staticmethod
    def _filter_for_api_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data for API response, removing internal fields."""
        # Fields to include in API response
        api_fields = {
            'request_id', 'status', 'prompt', 'max_candidates', 'filters',
            'behavioral_data', 'created_at', 'completed_at', 'error'
        }
        
        # Only include fields that should be in API response
        api_data = {field: value for field, value in data.items() if field in api_fields}
        
        return api_data


class ValidationCheckpoint:
    """
    Provides validation checkpoints for data processing pipeline.
    
    This class allows inserting validation points throughout the data
    processing pipeline to catch data integrity issues early.
    """
    
    def __init__(self, checkpoint_name: str):
        self.checkpoint_name = checkpoint_name
        self.logger = logging.getLogger(f"{__name__}.ValidationCheckpoint.{checkpoint_name}")
    
    def validate_at_checkpoint(self, search_data: Dict[str, Any], 
                             expected_prompt: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Validate search data at this checkpoint.
        
        Args:
            search_data: Data to validate
            expected_prompt: Expected prompt value (optional)
            
        Returns:
            Tuple: (is_valid, list_of_issues)
        """
        issues = []
        request_id = search_data.get('request_id', 'unknown')
        
        try:
            # Basic structure validation
            if not isinstance(search_data, dict):
                issues.append(f"Data is not a dictionary: {type(search_data)}")
                return False, issues
            
            # Critical field validation
            for field in SearchDataTransformer.CRITICAL_FIELDS:
                if field not in search_data or search_data[field] is None:
                    issues.append(f"Missing critical field: {field}")
            
            # Prompt-specific validation
            prompt = search_data.get('prompt')
            if prompt is None:
                issues.append("Prompt is None")
            elif not isinstance(prompt, str):
                issues.append(f"Prompt is not a string: {type(prompt)}")
            elif not prompt.strip():
                issues.append("Prompt is empty or whitespace-only")
            elif expected_prompt and str(prompt).strip() != str(expected_prompt).strip():
                issues.append(f"Prompt mismatch: expected '{expected_prompt[:30]}...', got '{prompt[:30]}...'")
            
            # Log checkpoint validation
            is_valid = len(issues) == 0
            log_data_flow(f"checkpoint_{self.checkpoint_name}", request_id, search_data, 
                         "validation_passed" if is_valid else "validation_failed")
            
            if is_valid:
                track_prompt_presence(f"checkpoint_{self.checkpoint_name}", request_id, 
                                    bool(prompt and str(prompt).strip()),
                                    len(str(prompt)) if prompt else 0, 
                                    f"checkpoint_passed_{self.checkpoint_name}")
                self.logger.debug(f"Checkpoint {self.checkpoint_name} passed for {request_id}")
            else:
                track_prompt_presence(f"checkpoint_{self.checkpoint_name}_failed", request_id, 
                                    False, 0, f"checkpoint_failed_{self.checkpoint_name}")
                self.logger.warning(f"Checkpoint {self.checkpoint_name} failed for {request_id}: {issues}")
            
            return is_valid, issues
            
        except Exception as e:
            issues.append(f"Checkpoint validation error: {e}")
            self.logger.error(f"Error at checkpoint {self.checkpoint_name}: {e}")
            return False, issues
    
    def log_checkpoint_data(self, search_data: Dict[str, Any], stage: str = "") -> None:
        """Log data at this checkpoint for debugging."""
        request_id = search_data.get('request_id', 'unknown')
        prompt = search_data.get('prompt', '')
        
        self.logger.info(f"Checkpoint {self.checkpoint_name} - Stage: {stage}")
        self.logger.info(f"  Request ID: {request_id}")
        self.logger.info(f"  Prompt: '{prompt[:50]}...' (length: {len(str(prompt))})")
        self.logger.info(f"  Status: {search_data.get('status', 'unknown')}")
        self.logger.info(f"  Fields present: {list(search_data.keys())}")


# Pre-defined validation checkpoints for common pipeline stages
API_ENTRY_CHECKPOINT = ValidationCheckpoint("api_entry")
PRE_STORAGE_CHECKPOINT = ValidationCheckpoint("pre_storage")
POST_RETRIEVAL_CHECKPOINT = ValidationCheckpoint("post_retrieval")
PRE_UPDATE_CHECKPOINT = ValidationCheckpoint("pre_update")
POST_UPDATE_CHECKPOINT = ValidationCheckpoint("post_update")
API_RESPONSE_CHECKPOINT = ValidationCheckpoint("api_response")


# Convenience functions for common transformations
def safe_transform_for_storage(search_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for safe storage transformation."""
    return SearchDataTransformer.safe_transform_for_storage(search_data)


def safe_transform_for_api_response(search_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for safe API response transformation."""
    return SearchDataTransformer.safe_transform_for_api_response(search_data)


def safe_merge_search_updates(existing_data: Dict[str, Any], 
                            updates: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for safe search update merging."""
    return SearchDataTransformer.safe_merge_search_updates(existing_data, updates)


def validate_field_mapping(source_data: Dict[str, Any], 
                         target_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Convenience function for field mapping validation."""
    return SearchDataTransformer.validate_field_mapping(source_data, target_data)


if __name__ == "__main__":
    # Test the data mapping and transformation utilities
    print("🔧 Testing Data Mapping and Transformation...")
    
    # Test data
    test_search_data = {
        'request_id': 'test-123-456',
        'prompt': 'Find software engineers in San Francisco',
        'status': 'processing',
        'filters': {'location': 'San Francisco', 'role': 'engineer'},
        'max_candidates': 5
    }
    
    try:
        # Test storage transformation
        print("\n📦 Testing storage transformation...")
        storage_data = safe_transform_for_storage(test_search_data)
        print(f"✅ Storage transformation successful")
        print(f"   Filters type: {type(storage_data.get('filters'))}")
        
        # Test API response transformation
        print("\n📡 Testing API response transformation...")
        api_data = safe_transform_for_api_response(storage_data)
        print(f"✅ API response transformation successful")
        print(f"   Filters type: {type(api_data.get('filters'))}")
        
        # Test field mapping validation
        print("\n🔍 Testing field mapping validation...")
        is_valid, issues = validate_field_mapping(test_search_data, storage_data)
        print(f"✅ Field mapping validation: {'passed' if is_valid else 'failed'}")
        if issues:
            print(f"   Issues: {issues}")
        
        # Test validation checkpoint
        print("\n✅ Testing validation checkpoint...")
        checkpoint = ValidationCheckpoint("test")
        is_valid, issues = checkpoint.validate_at_checkpoint(test_search_data)
        print(f"✅ Checkpoint validation: {'passed' if is_valid else 'failed'}")
        if issues:
            print(f"   Issues: {issues}")
        
        print("\n✅ All data mapping and transformation tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")