# Implementation Plan

- [x] 1. Create HubSpot OAuth request model
  - Add HubSpotTokenRequest Pydantic model to api/main.py
  - Define code and redirect_uri fields with proper validation
  - Place with other Pydantic model definitions in the file
  - _Requirements: 1.1, 3.1_

- [x] 2. Implement POST /api/hubspot/oauth/token endpoint
  - Add FastAPI route handler for token exchange
  - Use existing HubSpotOAuthClient.exchange_code_for_tokens method
  - Implement proper error handling for missing credentials and HubSpot API errors
  - Return appropriate HTTP status codes (400, 500, 502)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 4.1, 4.2_

- [x] 3. Implement GET /api/hubspot/oauth/health endpoint
  - Add FastAPI route handler for health check
  - Check for presence of HUBSPOT_CLIENT_ID and HUBSPOT_CLIENT_SECRET
  - Return structured health status with configuration details
  - Always return HTTP 200 with status in response body
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4. Test the OAuth endpoints functionality
  - Create test script to verify token exchange endpoint accepts requests
  - Test health endpoint returns proper status
  - Verify error handling for missing credentials
  - Test with the existing test_hubspot_oauth_debug.py script
  - _Requirements: 1.1, 2.1, 3.1, 3.2_