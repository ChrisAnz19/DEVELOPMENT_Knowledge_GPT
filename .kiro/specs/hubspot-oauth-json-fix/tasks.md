# Implementation Plan

- [x] 1. Fix JSON parsing in success path of HubSpot OAuth client
  - Add try-catch block around `response.json()` call at line 525 in `api/main.py`
  - Return structured error response when JSON parsing fails
  - Ensure proper HTTP status code (502) for invalid HubSpot responses
  - _Requirements: 1.1, 1.4_

- [x] 2. Verify and fix JSON parsing in error path of HubSpot OAuth client
  - Check existing JSONDecodeError handler around line 554 in `api/main.py`
  - Ensure it properly handles empty response bodies
  - Fix any issues with the existing error handling logic
  - _Requirements: 1.1, 1.2_

- [x] 3. Add proper JSON import if missing
  - Verify `import json` is present at the top of `api/main.py`
  - Add import if missing to support JSONDecodeError handling
  - _Requirements: 1.1_

- [x] 4. Test the fix with empty and malformed responses
  - Create test cases for empty response body scenarios
  - Test malformed JSON response handling
  - Verify frontend receives proper error format
  - _Requirements: 1.1, 1.2, 1.4_