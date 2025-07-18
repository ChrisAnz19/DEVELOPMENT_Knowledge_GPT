# Design Document

## Overview

The LinkedIn data fix addresses the issue where candidate LinkedIn photo, company name, and LinkedIn URL are not being returned to the client despite being stored in the database. The problem appears to be in the data flow between database retrieval and API response formatting.

## Architecture

The current data flow follows this pattern:
1. Background processing stores candidate data in the `people` table
2. API endpoint `/api/search/{request_id}` retrieves search data
3. `get_people_for_search()` function retrieves candidate data from database
4. Candidate data is attached to search response and returned to client

The issue occurs in step 4 where certain fields may not be properly included in the final response.

## Components and Interfaces

### Database Layer (`database.py`)
- **Function**: `get_people_for_search(search_id)`
- **Current Implementation**: Correctly selects required fields including `company`, `linkedin_url`, `profile_photo_url`
- **Issue**: No apparent issues at this layer

### API Layer (`api/main.py`)
- **Endpoint**: `GET /api/search/{request_id}`
- **Current Implementation**: Retrieves candidates and attaches to response
- **Issue**: May not be properly formatting or including all candidate fields in response

### Data Processing
- **Function**: `extract_profile_photo_url()` - Handles photo URL extraction
- **Function**: `store_people_to_database()` - Handles field mapping during storage

## Data Models

### Candidate Response Model
The API should return candidates with these fields:
```json
{
  "id": "string",
  "name": "string", 
  "title": "string",
  "company": "string",           // ← Must be included
  "email": "string",
  "linkedin_url": "string",      // ← Must be included  
  "profile_photo_url": "string", // ← Must be included
  "location": "string",
  "accuracy": "number",
  "reasons": "array",
  "linkedin_profile": "object",
  "behavioral_data": "object"
}
```

### Database Schema Mapping
The `people` table contains:
- `company` → API `company`
- `linkedin_url` → API `linkedin_url`  
- `profile_photo_url` → API `profile_photo_url`

## Error Handling

### Missing Field Detection
- Add logging to identify when expected fields are missing from database results
- Add validation to ensure required fields are present before returning response
- Provide fallback values (null) for missing optional fields

### Data Consistency Checks
- Verify that database query selects all required fields
- Validate that field mapping preserves all data during storage and retrieval
- Add debugging endpoints to inspect raw database data

## Testing Strategy

### Unit Tests
- Test `get_people_for_search()` function returns all expected fields
- Test API endpoint includes all candidate fields in response
- Test field mapping during storage and retrieval

### Integration Tests  
- Test complete data flow from storage to API response
- Verify LinkedIn data fields are preserved throughout the pipeline
- Test with real candidate data containing LinkedIn information

### Manual Testing
- Create test search with known LinkedIn data
- Verify API response contains expected fields
- Compare database content with API response

## Implementation Plan

### Phase 1: Diagnosis
1. Add comprehensive logging to identify where data is lost
2. Create debugging endpoint to inspect raw database data
3. Add field-by-field validation in API response

### Phase 2: Fix Implementation
1. Ensure database query selects all required fields
2. Verify API response includes all retrieved candidate fields  
3. Add proper error handling for missing fields

### Phase 3: Validation
1. Test with existing data to verify fix
2. Add monitoring to prevent regression
3. Update documentation with field requirements