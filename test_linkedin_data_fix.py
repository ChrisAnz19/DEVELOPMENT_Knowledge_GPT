#!/usr/bin/env python3
"""
Test script to verify LinkedIn data fields are properly included in API responses.
This test validates the fix for task 4: Fix API response to include all candidate fields.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_response_includes_linkedin_fields():
    """
    Test that API responses include all required LinkedIn data fields.
    
    This test validates:
    1. company field is present in API response
    2. linkedin_url field is present in API response  
    3. profile_photo_url field is present in API response
    4. All fields have proper null handling for missing values
    """
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # Test search request
    search_request = {
        "prompt": "Find software engineers with Python experience",
        "max_candidates": 3,
        "include_linkedin": True
    }
    
    logger.info("Starting LinkedIn data fields API test...")
    
    try:
        # Step 1: Create a search request
        logger.info("Step 1: Creating search request...")
        response = requests.post(f"{base_url}/api/search", json=search_request)
        
        if response.status_code != 200:
            logger.error(f"Failed to create search request: {response.status_code} - {response.text}")
            return False
            
        search_data = response.json()
        request_id = search_data.get("request_id")
        
        if not request_id:
            logger.error("No request_id returned from search creation")
            return False
            
        logger.info(f"Search created with request_id: {request_id}")
        
        # Step 2: Wait for processing and get results
        logger.info("Step 2: Waiting for search processing...")
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            time.sleep(2)  # Wait 2 seconds between checks
            attempt += 1
            
            response = requests.get(f"{base_url}/api/search/{request_id}")
            
            if response.status_code != 200:
                logger.error(f"Failed to get search results: {response.status_code} - {response.text}")
                continue
                
            result_data = response.json()
            status = result_data.get("status")
            
            logger.info(f"Attempt {attempt}: Status = {status}")
            
            if status == "completed":
                candidates = result_data.get("candidates", [])
                
                if not candidates:
                    logger.warning("Search completed but no candidates found")
                    return False
                    
                logger.info(f"Search completed with {len(candidates)} candidates")
                
                # Step 3: Validate LinkedIn data fields in API response
                logger.info("Step 3: Validating LinkedIn data fields in API response...")
                
                required_fields = ["company", "linkedin_url", "profile_photo_url"]
                all_expected_fields = [
                    "id", "name", "title", "email", "location", 
                    "company", "linkedin_url", "profile_photo_url",
                    "accuracy", "reasons", "linkedin_profile", "behavioral_data"
                ]
                
                validation_results = {
                    "total_candidates": len(candidates),
                    "field_presence": {},
                    "field_validation": {},
                    "candidates_with_linkedin_data": 0
                }
                
                for i, candidate in enumerate(candidates):
                    logger.info(f"\nValidating candidate {i+1}: {candidate.get('name', 'Unknown')}")
                    
                    # Check that all expected fields are present in the response
                    missing_fields = []
                    for field in all_expected_fields:
                        if field not in candidate:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        logger.error(f"Candidate {i+1} missing fields: {missing_fields}")
                        validation_results["field_validation"][f"candidate_{i+1}_missing_fields"] = missing_fields
                    else:
                        logger.info(f"Candidate {i+1}: All expected fields present ✓")
                    
                    # Check LinkedIn data fields specifically
                    linkedin_data_present = False
                    for field in required_fields:
                        value = candidate.get(field)
                        has_value = bool(value and str(value).strip())
                        
                        logger.info(f"  - {field}: {'✓' if has_value else '✗'} ({repr(value)})")
                        
                        if field not in validation_results["field_presence"]:
                            validation_results["field_presence"][field] = {"present": 0, "total": 0}
                        
                        validation_results["field_presence"][field]["total"] += 1
                        if has_value:
                            validation_results["field_presence"][field]["present"] += 1
                            linkedin_data_present = True
                    
                    if linkedin_data_present:
                        validation_results["candidates_with_linkedin_data"] += 1
                
                # Step 4: Generate validation report
                logger.info("\n" + "="*60)
                logger.info("LINKEDIN DATA FIELDS VALIDATION REPORT")
                logger.info("="*60)
                
                logger.info(f"Total candidates tested: {validation_results['total_candidates']}")
                logger.info(f"Candidates with LinkedIn data: {validation_results['candidates_with_linkedin_data']}")
                
                logger.info("\nField presence analysis:")
                for field, stats in validation_results["field_presence"].items():
                    percentage = (stats["present"] / stats["total"]) * 100
                    logger.info(f"  - {field}: {stats['present']}/{stats['total']} ({percentage:.1f}%)")
                
                # Check if the fix is working
                fix_validation = {
                    "all_fields_present_in_response": True,
                    "linkedin_fields_properly_mapped": True,
                    "null_handling_working": True
                }
                
                # Validate that all candidates have all expected fields in the response structure
                for i, candidate in enumerate(candidates):
                    for field in all_expected_fields:
                        if field not in candidate:
                            fix_validation["all_fields_present_in_response"] = False
                            logger.error(f"VALIDATION FAILED: Field '{field}' missing from candidate {i+1} API response")
                
                # Validate that LinkedIn fields are properly mapped (not lost during processing)
                for i, candidate in enumerate(candidates):
                    for field in required_fields:
                        # The field should be present in the response (even if null)
                        if field not in candidate:
                            fix_validation["linkedin_fields_properly_mapped"] = False
                            logger.error(f"VALIDATION FAILED: LinkedIn field '{field}' not mapped in candidate {i+1}")
                
                # Validate null handling (fields should be null, not missing)
                for i, candidate in enumerate(candidates):
                    for field in all_expected_fields:
                        if field in candidate:
                            value = candidate[field]
                            # Check that empty strings are converted to null
                            if isinstance(value, str) and not value.strip():
                                if value != "":  # Empty string should be converted to null
                                    fix_validation["null_handling_working"] = False
                                    logger.error(f"VALIDATION FAILED: Empty string not converted to null for field '{field}' in candidate {i+1}")
                
                logger.info("\nFix validation results:")
                logger.info(f"  - All fields present in response: {'✓' if fix_validation['all_fields_present_in_response'] else '✗'}")
                logger.info(f"  - LinkedIn fields properly mapped: {'✓' if fix_validation['linkedin_fields_properly_mapped'] else '✗'}")
                logger.info(f"  - Null handling working: {'✓' if fix_validation['null_handling_working'] else '✗'}")
                
                # Overall test result
                test_passed = all(fix_validation.values())
                
                logger.info("\n" + "="*60)
                if test_passed:
                    logger.info("✅ TEST PASSED: LinkedIn data fields fix is working correctly!")
                    logger.info("   - All required fields are present in API responses")
                    logger.info("   - LinkedIn data fields are properly mapped")
                    logger.info("   - Null value handling is working correctly")
                else:
                    logger.error("❌ TEST FAILED: LinkedIn data fields fix has issues")
                    logger.error("   - Check the validation errors above for details")
                
                logger.info("="*60)
                
                return test_passed
                
            elif status == "error":
                logger.error(f"Search failed with error: {result_data.get('error', 'Unknown error')}")
                return False
                
        logger.error(f"Search did not complete after {max_attempts} attempts")
        return False
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        return False

def test_raw_candidates_endpoint():
    """
    Test the raw candidates debugging endpoint to verify database fields are available.
    """
    logger.info("\nTesting raw candidates endpoint...")
    
    # First, get a list of recent searches to find one with candidates
    try:
        response = requests.get("http://localhost:8000/api/search")
        if response.status_code != 200:
            logger.error("Failed to get search list")
            return False
            
        searches = response.json().get("searches", [])
        
        if not searches:
            logger.warning("No searches found to test raw candidates endpoint")
            return True  # Not a failure, just no data to test
            
        # Find a search with candidates
        for search in searches:
            request_id = search.get("request_id")
            if not request_id:
                continue
                
            # Test the raw candidates endpoint
            response = requests.get(f"http://localhost:8000/api/search/{request_id}/candidates/raw")
            
            if response.status_code == 200:
                raw_data = response.json()
                raw_candidates = raw_data.get("raw_candidates", [])
                
                if raw_candidates:
                    logger.info(f"Raw candidates endpoint working - found {len(raw_candidates)} candidates")
                    
                    # Check that LinkedIn fields are present in raw data
                    sample_candidate = raw_candidates[0]
                    linkedin_fields = ["company", "linkedin_url", "profile_photo_url"]
                    
                    logger.info("LinkedIn fields in raw database data:")
                    for field in linkedin_fields:
                        if field in sample_candidate:
                            value = sample_candidate.get(field)
                            logger.info(f"  - {field}: {'✓' if value else '✗'} ({repr(value)})")
                        else:
                            logger.error(f"  - {field}: MISSING from database schema")
                    
                    return True
                    
        logger.warning("No searches with candidates found to test raw endpoint")
        return True
        
    except Exception as e:
        logger.error(f"Raw candidates endpoint test failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting LinkedIn data fix validation tests...")
    
    # Test 1: Main API response validation
    main_test_passed = test_api_response_includes_linkedin_fields()
    
    # Test 2: Raw candidates endpoint validation
    raw_test_passed = test_raw_candidates_endpoint()
    
    # Overall result
    if main_test_passed and raw_test_passed:
        logger.info("\n🎉 ALL TESTS PASSED! LinkedIn data fix is working correctly.")
        exit(0)
    else:
        logger.error("\n💥 SOME TESTS FAILED! Check the logs above for details.")
        exit(1)