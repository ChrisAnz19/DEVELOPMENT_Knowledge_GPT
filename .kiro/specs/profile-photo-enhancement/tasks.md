# LinkedIn Photo Validation Implementation Plan

- [x] 1. Implement core photo validation logic
  - Create `is_valid_linkedin_photo()` function in `api/main.py` to detect LinkedIn fallback images
  - Add detection for known fallback image patterns including `9c8pery4andzj6ohjkjp54ma2`
  - Implement `validate_candidate_photos()` function to process candidate batches
  - Add photo validation status fields to candidate data structure
  - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

- [ ] 2. Create candidate filtering and prioritization system
  - Implement `filter_candidates_by_photo_quality()` function to prioritize candidates with valid photos
  - Add logic to skip candidates with LinkedIn fallback images
  - Create candidate scoring system that factors in photo availability
  - Implement fallback logic when no candidates have valid photos
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.4_

- [ ] 3. Enhance search endpoint with photo validation
  - Modify `/api/search/{request_id}` endpoint in `api/main.py` to include photo validation
  - Integrate photo validation into existing candidate processing pipeline
  - Add photo validation status to API response metadata
  - Ensure backward compatibility with existing API clients
  - _Requirements: 1.3, 2.1, 4.1, 4.3_

- [ ] 4. Implement candidate replacement logic
  - Create `request_additional_candidates_if_needed()` function to fetch more candidates when photo quality is low
  - Add logic to request additional batches from Apollo API when needed
  - Implement quality threshold checking (80% photo validation rate)
  - Add handling for API rate limits and quota management
  - _Requirements: 1.4, 2.4, 4.2_

- [ ] 5. Add comprehensive photo validation testing
  - Create unit tests in `test_photo_validation.py` for photo URL validation logic
  - Test detection of various LinkedIn fallback image patterns
  - Test validation of actual LinkedIn profile photo URLs
  - Test handling of malformed, missing, or invalid URLs
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 6. Create integration tests for candidate filtering
  - Create integration tests in `test_candidate_photo_filtering.py` for end-to-end photo filtering
  - Test candidate prioritization based on photo availability
  - Test candidate replacement when initial batch has poor photo quality
  - Test search result quality assurance (80% photo validation rate)
  - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2_

- [ ] 7. Add monitoring and quality metrics
  - Implement logging for photo validation rates and candidate replacement statistics
  - Add monitoring alerts for low photo quality (below 60% validation rate)
  - Create metrics tracking for search result photo coverage
  - Add performance monitoring for photo validation impact on response times
  - _Requirements: 4.2, 4.3_

- [ ] 8. Optimize performance and add caching
  - Implement caching for photo validation results to avoid repeated checks
  - Optimize photo validation for large candidate batches
  - Add async processing for photo validation when possible
  - Monitor and optimize API response time impact
  - _Requirements: 3.4, 4.1_

- [ ] 9. Create end-to-end validation tests
  - Create comprehensive test in `test_linkedin_photo_integration.py`
  - Test complete search flow with photo validation enabled
  - Validate that search results consistently show valid LinkedIn photos
  - Test handling of edge cases (no valid photos, all fallback images)
  - _Requirements: 1.1, 1.2, 2.1, 4.1, 4.3, 4.4_

- [ ] 10. Add error handling and fallback mechanisms
  - Implement graceful degradation when photo validation fails
  - Add error handling for network issues during photo validation
  - Create fallback behavior when Apollo API limits are reached
  - Add user-friendly messaging when photo quality is limited
  - _Requirements: 2.4, 3.4, 4.4_