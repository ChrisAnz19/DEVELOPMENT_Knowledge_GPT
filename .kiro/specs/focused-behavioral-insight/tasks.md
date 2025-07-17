# Implementation Plan

- [x] 1. Update the behavioral metrics module
  - Modify the `behavioral_metrics.py` file to generate a single focused insight
  - Create a new function `generate_focused_behavioral_insight`
  - Update the `enhance_behavioral_data` function to use the new focused insight
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2. Implement logical consistency checks
  - Add logic to ensure insights are consistent with search context
  - Implement role and industry context analysis
  - Add validation to avoid generic, non-useful statements
  - Create utility functions for context analysis
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 3. Enhance profile photo URL extraction
  - Create a new function `extract_profile_photo_url` in `api/main.py`
  - Implement prioritization logic for photo sources
  - Add validation for photo URLs
  - Update candidate processing to use the enhanced photo extraction
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4. Update API response structure
  - Modify the API response structure to include the new format
  - Ensure backward compatibility for existing clients
  - Add validation for the new response format
  - _Requirements: 1.4, 4.3_

- [x] 5. Update API documentation
  - Update `API_DOCUMENTATION_UPDATED.md` to explain the new format
  - Add examples of the new format
  - Include guidance on frontend integration
  - Maintain backward compatibility information
  - _Requirements: 4.1, 4.2, 4.3, 4.4_