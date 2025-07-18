# Implementation Plan

- [x] 1. Add diagnostic logging to identify data loss points
  - Add detailed logging in `get_people_for_search()` to show exactly which fields are retrieved from database
  - Add logging in API endpoint to show which fields are included in candidate response
  - Add field-by-field comparison logging between database result and API response
  - _Requirements: 4.4_

- [x] 2. Create debugging endpoint for raw database inspection
  - Add new API endpoint `/api/search/{request_id}/candidates/raw` to return raw database candidate data
  - Include all fields from database query without any processing
  - Add logging to show the exact SQL query being executed
  - _Requirements: 4.1, 4.2_

- [x] 3. Verify database query includes all required fields
  - Review `get_people_for_search()` function to ensure it selects `company`, `linkedin_url`, `profile_photo_url`
  - Add validation that all expected fields are present in database result
  - Add error handling for missing fields in database schema
  - _Requirements: 1.1, 2.1, 3.1_

- [x] 4. Fix API response to include all candidate fields
  - Modify `/api/search/{request_id}` endpoint to ensure all candidate fields are included in response
  - Add explicit field mapping to guarantee `company`, `linkedin_url`, `profile_photo_url` are present
  - Add null value handling for missing optional fields
  - _Requirements: 1.4, 2.4, 3.4_

- [ ] 5. Add field validation and error handling
  - Create validation function to check candidate data completeness before returning API response
  - Add logging when required fields are missing or null
  - Implement fallback handling for missing LinkedIn data fields
  - _Requirements: 4.3, 4.4_

- [ ] 6. Test the fix with existing data
  - Create test script to verify LinkedIn data fields are returned in API responses
  - Test with existing search results that should contain LinkedIn data
  - Verify that `company`, `linkedin_url`, and `profile_photo_url` are properly returned
  - _Requirements: 1.1, 2.1, 3.1_