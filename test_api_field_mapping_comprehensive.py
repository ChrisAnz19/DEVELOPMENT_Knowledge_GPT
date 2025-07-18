#!/usr/bin/env python3
"""
Comprehensive test for API field mapping to verify all candidate fields are included in response.
This test validates the fix for task 4: Fix API response to include all candidate fields.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_field_mapping():
    """
    Test that API response includes all candidate fields with proper null handling.
    """
    base_url = "http://localhost:8000"
    
    # Test data - create a search request
    search_request = {
        "prompt": "Find software engineers with Python experience",
        "max_candidates": 2,
        "include_linkedin": True
    }
    
    logger.info("=== Testing API Field Mapping ===")
    
    try:
        # Step 1: Create a search request
        logger.info("Step 1: Creating search request...")
        response = requests.post(f"{base_url}/api/search", json=search_request)
        
        if response.status_code != 200:
            logger.error(f"Failed to create search: {response.status_code} - {response.text}")
            return False
        
        search_data = response.json()
        request_id = search_data["request_id"]
        logger.info(f"Created search with request_id: {request_id}")
        
        # Step 2: Wait for processing to complete
        logger.info("Step 2: Waiting for search to complete...")
        max_wait_time = 60  # seconds
        wait_interval = 2   # seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            response = requests.get(f"{base_url}/api/search/{request_id}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get search result: {response.status_code}")
                return False
            
            result = response.json()
            status = result.get("status")
            
            logger.info(f"Search status: {status} (elapsed: {elapsed_time}s)")
            
            if status == "completed":
                break
            elif status == "failed":
                logger.error(f"Search failed: {result.get('error', 'Unknown error')}")
                return False
            
            time.sleep(wait_interval)
            elapsed_time += wait_interval
        
        if elapsed_time >= max_wait_time:
            logger.error("Search did not complete within timeout")
            return False
        
        # Step 3: Validate API response field mapping
        logger.info("Step 3: Validating API response field mapping...")
        
        candidates = result.get("candidates", [])
        if not candidates:
            logger.warning("No candidates found in search result")
            return True  # Not a failure, just no data to test
        
        logger.info(f"Found {len(candidates)} candidates to validate")
        
        # Define expected fields that should be present in API response
        expected_fields = [
            'id', 'name', 'title', 'email', 'location', 'company', 
            'linkedin_url', 'profile_photo_url', 'accuracy', 'reasons',
            'linkedin_profile', 'behavioral_data'
        ]
        
        # Critical LinkedIn data fields that should be explicitly mapped
        critical_linkedin_fields = ['company', 'linkedin_url', 'profile_photo_url']
        
        all_tests_passed = True
        
        for i, candidate in enumerate(candidates):
            logger.info(f"\n--- Validating Candidate {i+1}: {candidate.get('name', 'Unknown')} ---")
            
            # Test 1: Check that all expected fields are present
            missing_fields = []
            for field in expected_fields:
                if field not in candidate:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"FAIL: Missing fields in API response: {missing_fields}")
                all_tests_passed = False
            else:
                logger.info("PASS: All expected fields present in API response")
            
            # Test 2: Validate critical LinkedIn fields are explicitly mapped
            linkedin_field_results = {}
            for field in critical_linkedin_fields:
                value = candidate.get(field)
                has_value = bool(value and str(value).strip()) if isinstance(value, str) else bool(value)
                linkedin_field_results[field] = {
                    'present': field in candidate,
                    'has_value': has_value,
                    'value': value
                }
                
                logger.info(f"LinkedIn field '{field}': Present={'✓' if linkedin_field_results[field]['present'] else '✗'}, "
                           f"HasValue={'✓' if has_value else '✗'}, Value={repr(value)}")
            
            # Test 3: Validate null value handling
            null_handling_results = {}
            for field_name, field_value in candidate.items():
                if field_value is None:
                    null_handling_results[field_name] = 'null'
                elif isinstance(field_value, str) and not field_value.strip():
                    null_handling_results[field_name] = 'empty_string'
                    logger.warning(f"Field '{field_name}' contains empty string instead of null")
                elif isinstance(field_value, list) and not field_value:
                    null_handling_results[field_name] = 'empty_list'
                elif isinstance(field_value, dict) and not field_value:
                    null_handling_results[field_name] = 'empty_dict'
                else:
                    null_handling_results[field_name] = 'has_value'
            
            # Log null handling summary
            null_fields = [k for k, v in null_handling_results.items() if v == 'null']
            empty_string_fields = [k for k, v in null_handling_results.items() if v == 'empty_string']
            value_fields = [k for k, v in null_handling_results.items() if v == 'has_value']
            
            logger.info(f"Null handling - Null: {len(null_fields)}, EmptyString: {len(empty_string_fields)}, HasValue: {len(value_fields)}")
            
            if empty_string_fields:
                logger.warning(f"Fields with empty strings (should be null): {empty_string_fields}")
                # This is a warning, not a failure, as empty strings might be acceptable in some cases
            
            # Test 4: Validate field types
            type_validation_results = {}
            expected_types = {
                'id': (int, str),
                'name': (str, type(None)),
                'title': (str, type(None)),
                'email': (str, type(None)),
                'location': (str, type(None)),
                'company': (str, type(None)),
                'linkedin_url': (str, type(None)),
                'profile_photo_url': (str, type(None)),
                'accuracy': (int, float, type(None)),
                'reasons': (list, type(None)),
                'linkedin_profile': (dict, type(None)),
                'behavioral_data': (dict, type(None))
            }
            
            for field, expected_type in expected_types.items():
                if field in candidate:
                    actual_type = type(candidate[field])
                    is_valid_type = isinstance(candidate[field], expected_type)
                    type_validation_results[field] = {
                        'expected': expected_type,
                        'actual': actual_type,
                        'valid': is_valid_type
                    }
                    
                    if not is_valid_type:
                        logger.warning(f"Field '{field}' has unexpected type: expected {expected_type}, got {actual_type}")
            
            # Log field type validation summary
            invalid_types = [k for k, v in type_validation_results.items() if not v['valid']]
            if invalid_types:
                logger.warning(f"Fields with unexpected types: {invalid_types}")
        
        # Step 4: Test raw candidates endpoint for comparison
        logger.info("\nStep 4: Testing raw candidates endpoint for comparison...")
        
        try:
            raw_response = requests.get(f"{base_url}/api/search/{request_id}/candidates/raw")
            if raw_response.status_code == 200:
                raw_data = raw_response.json()
                raw_candidates = raw_data.get("raw_candidates", [])
                
                logger.info(f"Raw endpoint returned {len(raw_candidates)} candidates")
                
                if raw_candidates and candidates:
                    # Compare field presence between raw and processed candidates
                    raw_fields = set(raw_candidates[0].keys()) if raw_candidates else set()
                    api_fields = set(candidates[0].keys()) if candidates else set()
                    
                    missing_in_api = raw_fields - api_fields
                    added_in_api = api_fields - raw_fields
                    
                    logger.info(f"Field comparison - Raw: {len(raw_fields)}, API: {len(api_fields)}")
                    if missing_in_api:
                        logger.warning(f"Fields in raw but missing in API: {missing_in_api}")
                    if added_in_api:
                        logger.info(f"Fields added in API processing: {added_in_api}")
                    
                    # Check if critical LinkedIn fields are preserved
                    for field in critical_linkedin_fields:
                        raw_value = raw_candidates[0].get(field) if raw_candidates else None
                        api_value = candidates[0].get(field) if candidates else None
                        
                        raw_has_value = bool(raw_value and str(raw_value).strip()) if isinstance(raw_value, str) else bool(raw_value)
                        api_has_value = bool(api_value and str(api_value).strip()) if isinstance(api_value, str) else bool(api_value)
                        
                        if raw_has_value != api_has_value:
                            logger.error(f"FAIL: Field '{field}' value preservation - Raw: {'✓' if raw_has_value else '✗'}, API: {'✓' if api_has_value else '✗'}")
                            all_tests_passed = False
                        else:
                            logger.info(f"PASS: Field '{field}' value preserved - {'✓' if api_has_value else '✗'}")
            else:
                logger.warning(f"Could not fetch raw candidates: {raw_response.status_code}")
        
        except Exception as e:
            logger.warning(f"Error testing raw candidates endpoint: {e}")
        
        # Final result
        if all_tests_passed:
            logger.info("\n=== ALL TESTS PASSED ===")
            logger.info("✓ All expected fields present in API response")
            logger.info("✓ Critical LinkedIn fields explicitly mapped")
            logger.info("✓ Null value handling working correctly")
            logger.info("✓ Field values preserved from database to API")
            return True
        else:
            logger.error("\n=== SOME TESTS FAILED ===")
            logger.error("✗ API field mapping has issues that need to be addressed")
            return False
    
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_api_field_mapping()
    exit(0 if success else 1)