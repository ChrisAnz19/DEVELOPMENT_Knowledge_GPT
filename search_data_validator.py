#!/usr/bin/env python3
"""
Search Data Validation Module

This module provides comprehensive validation for search data to ensure prompt integrity
and data structure consistency throughout the system pipeline.

Requirements addressed:
- 1.1: Proper access and preservation of prompt data
- 2.2: Correct mapping of prompt fields between data structures  
- 2.3: Proper serialization and deserialization of prompt values
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class SearchDataValidationError(Exception):
    """Raised when search data validation fails"""
    pass

class PromptIntegrityError(Exception):
    """Raised when prompt data integrity is compromised"""
    pass

class SearchDataValidator:
    """
    Comprehensive validator for search data with focus on prompt integrity.
    
    This class provides static methods to validate search data structure,
    ensure prompt integrity, and track data flow for debugging purposes.
    """
    
    # Required fields for search data
    REQUIRED_FIELDS = {
        'request_id': str,
        'prompt': str,
        'status': str
    }
    
    # Optional fields with their expected types
    OPTIONAL_FIELDS = {
        'id': int,
        'max_candidates': int,
        'filters': (str, dict),  # Can be JSON string or dict
        'behavioral_data': (str, dict),  # Can be JSON string or dict
        'created_at': str,
        'completed_at': str,
        'error': str
    }
    
    # Valid status values
    VALID_STATUSES = {
        'pending', 'processing', 'completed', 'failed', 'cancelled'
    }
    
    @staticmethod
    def validate_search_data(search_data: dict) -> dict:
        """
        Validate and ensure search data integrity.
        
        Args:
            search_data: Dictionary containing search data
            
        Returns:
            dict: Validated and potentially cleaned search data
            
        Raises:
            SearchDataValidationError: If validation fails
            PromptIntegrityError: If prompt integrity is compromised
        """
        if not isinstance(search_data, dict):
            raise SearchDataValidationError(
                f"Search data must be a dictionary, got {type(search_data)}"
            )
        
        # Create a copy to avoid modifying the original
        validated_data = search_data.copy()
        
        # Validate required fields
        SearchDataValidator._validate_required_fields(validated_data)
        
        # Validate field types
        SearchDataValidator._validate_field_types(validated_data)
        
        # Ensure prompt integrity
        validated_data = SearchDataValidator.ensure_prompt_integrity(validated_data)
        
        # Validate status
        SearchDataValidator._validate_status(validated_data)
        
        # Validate request_id format
        SearchDataValidator._validate_request_id(validated_data)
        
        # Normalize JSON fields
        validated_data = SearchDataValidator._normalize_json_fields(validated_data)
        
        return validated_data
    
    @staticmethod
    def ensure_prompt_integrity(search_data: dict) -> dict:
        """
        Ensure prompt field is properly preserved and valid.
        
        Args:
            search_data: Dictionary containing search data
            
        Returns:
            dict: Search data with validated prompt
            
        Raises:
            PromptIntegrityError: If prompt cannot be validated or preserved
        """
        if not isinstance(search_data, dict):
            raise PromptIntegrityError("Search data must be a dictionary")
        
        validated_data = search_data.copy()
        prompt = validated_data.get('prompt')
        
        # Check if prompt exists and is not None
        if prompt is None:
            raise PromptIntegrityError(
                f"Prompt is None for request_id: {validated_data.get('request_id', 'unknown')}"
            )
        
        # Convert to string if not already
        if not isinstance(prompt, str):
            logger.warning(f"Converting prompt from {type(prompt)} to string")
            prompt = str(prompt)
            validated_data['prompt'] = prompt
        
        # Check if prompt is empty or only whitespace
        if not prompt.strip():
            raise PromptIntegrityError(
                f"Prompt is empty or whitespace-only for request_id: {validated_data.get('request_id', 'unknown')}"
            )
        
        # Log successful prompt validation
        request_id = validated_data.get('request_id', 'unknown')
        logger.debug(f"Prompt integrity validated for request_id: {request_id}, length: {len(prompt)}")
        
        return validated_data
    
    @staticmethod
    def validate_prompt_preservation(original_data: dict, processed_data: dict) -> bool:
        """
        Validate that prompt data is preserved between data transformations.
        
        Args:
            original_data: Original search data
            processed_data: Processed search data
            
        Returns:
            bool: True if prompt is preserved, False otherwise
        """
        try:
            original_prompt = original_data.get('prompt', '').strip()
            processed_prompt = processed_data.get('prompt', '').strip()
            
            if not original_prompt and not processed_prompt:
                return True  # Both empty is consistent
            
            if original_prompt != processed_prompt:
                logger.error(
                    f"Prompt not preserved - Original: '{original_prompt[:50]}...', "
                    f"Processed: '{processed_prompt[:50]}...'"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating prompt preservation: {e}")
            return False
    
    @staticmethod
    def log_data_flow(operation: str, search_data: dict, stage: str = "") -> None:
        """
        Log data flow for debugging purposes.
        
        Args:
            operation: Type of operation (store, retrieve, update, etc.)
            search_data: Search data being processed
            stage: Current stage in the pipeline
        """
        try:
            request_id = search_data.get('request_id', 'unknown')
            prompt_length = len(search_data.get('prompt', ''))
            has_prompt = bool(search_data.get('prompt', '').strip())
            
            logger.debug(
                f"Data flow - Operation: {operation}, Stage: {stage}, "
                f"Request ID: {request_id}, Has prompt: {has_prompt}, "
                f"Prompt length: {prompt_length}"
            )
            
        except Exception as e:
            logger.error(f"Error logging data flow: {e}")
    
    @staticmethod
    def analyze_search_data_structure(search_data: dict) -> Dict[str, Any]:
        """
        Analyze search data structure and return detailed information.
        
        Args:
            search_data: Search data to analyze
            
        Returns:
            dict: Analysis results including field presence, types, and issues
        """
        analysis = {
            'valid': True,
            'issues': [],
            'field_analysis': {},
            'prompt_analysis': {},
            'recommendations': []
        }
        
        try:
            # Analyze each field
            all_fields = {**SearchDataValidator.REQUIRED_FIELDS, **SearchDataValidator.OPTIONAL_FIELDS}
            
            for field_name, expected_type in all_fields.items():
                field_value = search_data.get(field_name)
                field_info = {
                    'present': field_value is not None,
                    'type': type(field_value).__name__ if field_value is not None else 'None',
                    'expected_type': expected_type.__name__ if isinstance(expected_type, type) else str(expected_type),
                    'valid': True
                }
                
                # Type validation
                if field_value is not None:
                    if isinstance(expected_type, tuple):
                        field_info['valid'] = any(isinstance(field_value, t) for t in expected_type)
                    else:
                        field_info['valid'] = isinstance(field_value, expected_type)
                
                analysis['field_analysis'][field_name] = field_info
                
                # Track issues
                if field_name in SearchDataValidator.REQUIRED_FIELDS and not field_info['present']:
                    analysis['issues'].append(f"Missing required field: {field_name}")
                    analysis['valid'] = False
                
                if field_info['present'] and not field_info['valid']:
                    analysis['issues'].append(f"Invalid type for {field_name}: expected {field_info['expected_type']}, got {field_info['type']}")
                    analysis['valid'] = False
            
            # Additional validation checks
            # Check request_id format
            request_id = search_data.get('request_id')
            if request_id:
                try:
                    uuid.UUID(request_id)
                except ValueError:
                    analysis['issues'].append(f"Invalid request_id format: {request_id}")
                    analysis['valid'] = False
            
            # Check status value
            status = search_data.get('status')
            if status and status not in SearchDataValidator.VALID_STATUSES:
                analysis['issues'].append(f"Invalid status value: {status}")
                analysis['valid'] = False
            
            # Detailed prompt analysis
            prompt = search_data.get('prompt')
            analysis['prompt_analysis'] = {
                'present': prompt is not None,
                'type': type(prompt).__name__ if prompt is not None else 'None',
                'length': len(str(prompt)) if prompt is not None else 0,
                'empty': not bool(str(prompt).strip()) if prompt is not None else True,
                'valid': prompt is not None and bool(str(prompt).strip())
            }
            
            # Generate recommendations
            if not analysis['prompt_analysis']['valid']:
                analysis['recommendations'].append("Fix prompt field - ensure it's a non-empty string")
            
            if analysis['issues']:
                analysis['recommendations'].append("Address field validation issues before processing")
            
        except Exception as e:
            analysis['valid'] = False
            analysis['issues'].append(f"Analysis error: {str(e)}")
        
        return analysis
    
    @staticmethod
    def _validate_required_fields(search_data: dict) -> None:
        """Validate that all required fields are present."""
        missing_fields = []
        
        for field_name in SearchDataValidator.REQUIRED_FIELDS:
            if field_name not in search_data or search_data[field_name] is None:
                missing_fields.append(field_name)
        
        if missing_fields:
            raise SearchDataValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )
    
    @staticmethod
    def _validate_field_types(search_data: dict) -> None:
        """Validate field types against expected types."""
        all_fields = {**SearchDataValidator.REQUIRED_FIELDS, **SearchDataValidator.OPTIONAL_FIELDS}
        
        for field_name, expected_type in all_fields.items():
            if field_name in search_data and search_data[field_name] is not None:
                field_value = search_data[field_name]
                
                # Handle tuple of types (multiple valid types)
                if isinstance(expected_type, tuple):
                    if not any(isinstance(field_value, t) for t in expected_type):
                        raise SearchDataValidationError(
                            f"Invalid type for {field_name}: expected one of {expected_type}, got {type(field_value)}"
                        )
                else:
                    if not isinstance(field_value, expected_type):
                        raise SearchDataValidationError(
                            f"Invalid type for {field_name}: expected {expected_type}, got {type(field_value)}"
                        )
    
    @staticmethod
    def _validate_status(search_data: dict) -> None:
        """Validate status field value."""
        status = search_data.get('status')
        if status and status not in SearchDataValidator.VALID_STATUSES:
            raise SearchDataValidationError(
                f"Invalid status '{status}'. Valid statuses: {', '.join(SearchDataValidator.VALID_STATUSES)}"
            )
    
    @staticmethod
    def _validate_request_id(search_data: dict) -> None:
        """Validate request_id format (should be UUID)."""
        request_id = search_data.get('request_id')
        if request_id:
            try:
                uuid.UUID(request_id)
            except ValueError:
                raise SearchDataValidationError(
                    f"Invalid request_id format: {request_id}. Should be a valid UUID."
                )
    
    @staticmethod
    def _normalize_json_fields(search_data: dict) -> dict:
        """Normalize JSON fields (convert dicts to JSON strings if needed)."""
        validated_data = search_data.copy()
        json_fields = ['filters', 'behavioral_data']
        
        for field in json_fields:
            if field in validated_data and validated_data[field] is not None:
                value = validated_data[field]
                
                # If it's a dict, convert to JSON string
                if isinstance(value, dict):
                    try:
                        validated_data[field] = json.dumps(value)
                    except (TypeError, ValueError) as e:
                        raise SearchDataValidationError(
                            f"Cannot serialize {field} to JSON: {e}"
                        )
                
                # If it's a string, validate it's valid JSON
                elif isinstance(value, str) and value.strip():
                    try:
                        json.loads(value)  # Just validate, don't change
                    except json.JSONDecodeError as e:
                        raise SearchDataValidationError(
                            f"Invalid JSON in {field}: {e}"
                        )
        
        return validated_data


class PromptIntegrityChecker:
    """
    Specialized class for checking prompt integrity throughout the data pipeline.
    """
    
    @staticmethod
    def check_prompt_at_stage(search_data: dict, stage: str, expected_prompt: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check prompt integrity at a specific pipeline stage.
        
        Args:
            search_data: Search data to check
            stage: Current pipeline stage
            expected_prompt: Expected prompt value (optional)
            
        Returns:
            tuple: (is_valid, message)
        """
        try:
            prompt = search_data.get('prompt')
            request_id = search_data.get('request_id', 'unknown')
            
            # Basic prompt presence check
            if prompt is None:
                return False, f"Prompt is None at stage '{stage}' for request {request_id}"
            
            # Empty prompt check
            if not str(prompt).strip():
                return False, f"Prompt is empty at stage '{stage}' for request {request_id}"
            
            # Expected prompt comparison
            if expected_prompt is not None and str(prompt).strip() != str(expected_prompt).strip():
                return False, f"Prompt mismatch at stage '{stage}' for request {request_id}"
            
            return True, f"Prompt integrity verified at stage '{stage}' for request {request_id}"
            
        except Exception as e:
            return False, f"Error checking prompt integrity at stage '{stage}': {e}"
    
    @staticmethod
    def track_prompt_changes(original_data: dict, modified_data: dict, operation: str) -> Dict[str, Any]:
        """
        Track changes to prompt data during operations.
        
        Args:
            original_data: Original search data
            modified_data: Modified search data
            operation: Operation that was performed
            
        Returns:
            dict: Change tracking information
        """
        tracking_info = {
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'request_id': original_data.get('request_id', 'unknown'),
            'prompt_changed': False,
            'original_prompt': original_data.get('prompt'),
            'modified_prompt': modified_data.get('prompt'),
            'changes': []
        }
        
        try:
            original_prompt = str(original_data.get('prompt', '')).strip()
            modified_prompt = str(modified_data.get('prompt', '')).strip()
            
            if original_prompt != modified_prompt:
                tracking_info['prompt_changed'] = True
                tracking_info['changes'].append({
                    'field': 'prompt',
                    'from': original_prompt[:100] + '...' if len(original_prompt) > 100 else original_prompt,
                    'to': modified_prompt[:100] + '...' if len(modified_prompt) > 100 else modified_prompt,
                    'length_change': len(modified_prompt) - len(original_prompt)
                })
                
                logger.warning(f"Prompt changed during {operation} for request {tracking_info['request_id']}")
            
        except Exception as e:
            tracking_info['changes'].append({
                'error': f"Error tracking prompt changes: {e}"
            })
        
        return tracking_info


# Convenience functions for common validation tasks
def validate_search_request(search_data: dict) -> dict:
    """
    Convenience function to validate search request data.
    
    Args:
        search_data: Search data to validate
        
    Returns:
        dict: Validated search data
    """
    return SearchDataValidator.validate_search_data(search_data)


def check_prompt_integrity(search_data: dict) -> bool:
    """
    Convenience function to check prompt integrity.
    
    Args:
        search_data: Search data to check
        
    Returns:
        bool: True if prompt integrity is valid
    """
    try:
        SearchDataValidator.ensure_prompt_integrity(search_data)
        return True
    except (PromptIntegrityError, SearchDataValidationError):
        return False


if __name__ == "__main__":
    # Example usage and testing
    print("🧪 Testing SearchDataValidator...")
    
    # Test valid data
    valid_data = {
        'request_id': str(uuid.uuid4()),
        'prompt': 'Find software engineers in San Francisco',
        'status': 'pending',
        'max_candidates': 5
    }
    
    try:
        validated = SearchDataValidator.validate_search_data(valid_data)
        print("✅ Valid data passed validation")
        
        analysis = SearchDataValidator.analyze_search_data_structure(validated)
        print(f"📊 Analysis: Valid={analysis['valid']}, Issues={len(analysis['issues'])}")
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Test invalid data
    invalid_data = {
        'request_id': 'invalid-uuid',
        'prompt': '',  # Empty prompt
        'status': 'invalid_status'
    }
    
    try:
        SearchDataValidator.validate_search_data(invalid_data)
        print("❌ Invalid data should have failed validation")
    except Exception as e:
        print(f"✅ Invalid data correctly rejected: {e}")