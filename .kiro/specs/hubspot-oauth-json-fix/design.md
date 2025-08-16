# Design Document

## Overview

This design fixes the critical JSON parsing bug in the HubSpot OAuth backend integration. The current implementation fails when HubSpot returns empty response bodies or malformed JSON, causing "Unexpected end of JSON input" errors that propagate to the frontend.

The fix is simple: wrap the `response.json()` calls in try-catch blocks and handle the JSONDecodeError properly. This targets the `HubSpotOAuthClient.exchange_code_for_tokens()` method in `api/main.py` at lines 525 and 554.

## Architecture

The problem is simple: two places in the code call `response.json()` without handling the case where the response body is empty or malformed JSON.

**Current Problem**:
- Line 525: `return response.json()` - fails if response is empty
- Line 554: `error_data = response.json()` - fails if error response is empty

**Solution**:
- Wrap both calls in try-catch blocks
- Return appropriate error responses when JSON parsing fails

## Components and Interfaces

### 1. Fix Success Path JSON Parsing

**Location**: `HubSpotOAuthClient.exchange_code_for_tokens()` line 525

**Current Code**:
```python
if response.status_code == 200:
    return response.json()
```

**Fixed Code**:
```python
if response.status_code == 200:
    try:
        return response.json()
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "invalid_response",
                "error_description": "HubSpot returned an invalid response format",
                "status_code": 502
            }
        )
```

### 2. Fix Error Path JSON Parsing

**Location**: `HubSpotOAuthClient.exchange_code_for_tokens()` line 554

**Current Code**:
```python
try:
    error_data = response.json()
    # ... handle error
except json.JSONDecodeError:
    # ... existing fallback
```

**Issue**: The existing code already has a JSONDecodeError handler, but it might not be working correctly.

## Implementation Notes

### Required Changes

1. **Add JSON import**: Ensure `import json` is present at the top of the file
2. **Fix success path**: Add try-catch around line 525 `response.json()`
3. **Verify error path**: Check that the existing JSONDecodeError handler at line 554 is working correctly

### Testing

- Test with empty response body from HubSpot
- Test with malformed JSON response
- Verify error messages are properly formatted for frontend consumption