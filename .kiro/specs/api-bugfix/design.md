# Design Document: API Bugfix

## Overview

This design document outlines the approach to fixing critical bugs in the Knowledge_GPT API that are causing search processing errors, database constraint violations, infinite loops, null prompt errors, missing candidate data, and non-personalized engagement recommendations. The fixes will focus on proper async/await usage, database operation integrity, elimination of infinite loops, data validation, complete API responses, and personalized recommendations.

## Architecture

The bugfixes will address issues in the existing architecture without changing the overall system design:

1. **Async/Await Handling**: Fix improper usage of async/await in search processing
2. **Database Operations**: Improve database operation handling to prevent constraint violations
3. **Search Processing Flow**: Restructure the search processing flow to eliminate infinite loops
4. **Data Validation**: Add validation for required fields like prompt before database operations
5. **API Response Enhancement**: Ensure complete candidate data is returned including LinkedIn URLs and company names
6. **Personalization**: Implement proper name extraction and usage in engagement recommendations

## Components and Interfaces

### 1. Async/Await Fix

The main issue with async/await usage appears to be in the search processing code, particularly when handling lists of objects. We'll modify the following functions:

```python
# Current problematic code
async def process_search(request_id, prompt, max_candidates, include_linkedin):
    # ...
    people = await search_people_via_internal_database(filters, max_candidates)
    
    # Scrape LinkedIn profiles if requested
    if include_linkedin and people:
        people = await async_scrape_linkedin_profiles(people)  # This might be the issue
    # ...
```

The fix will ensure that async functions are properly awaited and that non-awaitable objects are handled correctly:

```python
# Fixed code
async def process_search(request_id, prompt, max_candidates, include_linkedin):
    # ...
    people = await search_people_via_internal_database(filters, max_candidates)
    
    # Scrape LinkedIn profiles if requested
    if include_linkedin and people:
        # Fix: Ensure async_scrape_linkedin_profiles returns an awaitable
        people = await async_scrape_linkedin_profiles(people)
    # ...
```

### 2. Database Constraint Violation Fix

The database constraint violation occurs when trying to insert a record with a duplicate primary key. We'll modify the database operations to prevent this:

```python
# Current problematic code
def store_search_to_database(search_data):
    # Direct insert/update without checking for existing records
    # ...
```

The fix will include proper handling of existing records:

```python
# Fixed code
def store_search_to_database(search_data):
    """Store search data in the database, handling existing records appropriately."""
    try:
        # Check if record exists by request_id
        existing_record = get_search_from_database(search_data["request_id"])
        
        if existing_record:
            # Update existing record
            # Ensure we're using the correct primary key
            search_data["id"] = existing_record["id"]
            # Update logic...
        else:
            # Insert new record
            # Ensure we're not specifying a primary key that might conflict
            if "id" in search_data:
                del search_data["id"]  # Let the database assign the ID
            # Insert logic...
            
    except Exception as e:
        logger.error(f"Database operation error: {str(e)}")
        # Handle error appropriately
```

### 3. Infinite Loop Fix

The infinite loop issue likely occurs in the search processing flow, particularly when handling callbacks or recursive functions. We'll restructure the flow to ensure proper termination:

```python
# Current problematic code
async def process_search(request_id, prompt, max_candidates, include_linkedin):
    # ...
    # This might be causing a loop if it triggers additional processing
    search_data = get_search_from_database(request_id)
    search_data["status"] = "completed"
    store_search_to_database(search_data)
    # ...
```

The fix will include proper flow control and state tracking:

```python
# Fixed code
async def process_search(request_id, prompt, max_candidates, include_linkedin):
    """Process a search request in the background with proper flow control."""
    # Track processing state to prevent loops
    processing_state = {"is_processing": True}
    
    try:
        # Get initial search data
        search_data = get_search_from_database(request_id)
        if not search_data:
            logger.error(f"Search not found: {request_id}")
            return
            
        # Check if already completed to prevent reprocessing
        if search_data.get("status") == "completed":
            logger.info(f"Search {request_id} already completed, skipping processing")
            return
            
        # Process search...
        
        # Update status only once at the end
        if processing_state["is_processing"]:
            processing_state["is_processing"] = False
            search_data["status"] = "completed"
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            
    except Exception as e:
        logger.error(f"Error processing search: {str(e)}")
        
        # Update status to failed, but only if we haven't already updated
        if processing_state["is_processing"]:
            processing_state["is_processing"] = False
            try:
                search_data = get_search_from_database(request_id)
                if search_data:
                    search_data["status"] = "failed"
                    search_data["error"] = str(e)
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
            except Exception as update_error:
                logger.error(f"Error updating search status: {str(update_error)}")
```

## Data Models

No changes to the data models are required for these bugfixes.

## Error Handling

1. **Async/Await Errors**: Proper try/except blocks around async operations
2. **Database Errors**: Enhanced error handling for database operations
3. **Processing Flow Errors**: Improved error handling in the search processing flow

## Testing Strategy

1. **Unit Tests**: Test individual functions with mock data
2. **Integration Tests**: Test the entire search processing flow
3. **Error Case Tests**: Test error handling and recovery
4. **Concurrency Tests**: Test multiple simultaneous search requests

## Implementation Details

### 1. Async/Await Fix Implementation

1. Review all async functions in the codebase, particularly:
   - `process_search`
   - `search_people_via_internal_database`
   - `async_scrape_linkedin_profiles`

2. Ensure all async functions are properly defined with `async def` and that they return awaitable objects

3. Check all calls to async functions to ensure they are properly awaited with `await`

4. For functions that handle lists or collections:
   - Use `asyncio.gather` for parallel processing of multiple awaitable tasks
   - Use list comprehensions with await for sequential processing

### 2. Database Constraint Violation Fix Implementation

1. Modify `store_search_to_database` to handle existing records:
   - Check if a record with the same request_id already exists
   - If it exists, update it instead of inserting a new one
   - If inserting a new record, don't specify the primary key

2. Add transaction support for database operations:
   - Begin a transaction before database operations
   - Commit the transaction if successful
   - Rollback the transaction if an error occurs

3. Improve error handling for database operations:
   - Catch specific database exceptions
   - Log detailed error information
   - Return appropriate error responses

### 3. Infinite Loop Fix Implementation

1. Add state tracking to the search processing flow:
   - Track whether a search is currently being processed
   - Prevent reprocessing of already completed searches

2. Implement proper termination conditions:
   - Clear exit conditions for all loops and recursive functions
   - Timeout mechanisms for long-running operations

3. Ensure status updates happen only once:
   - Track whether the status has been updated
   - Prevent multiple status updates for the same search

### 4. Null Prompt Validation Fix

The null prompt error occurs when trying to store search data without a valid prompt field. We'll add validation:

```python
# Current problematic code
def store_search_to_database(search_data):
    # No validation of required fields
    # Direct database operation that fails on null prompt
    pass

# Fixed code
def store_search_to_database(search_data):
    """Store search data with proper validation."""
    # Validate required fields
    if not search_data.get("prompt"):
        # Provide default or handle appropriately
        if "request_id" in search_data:
            logger.warning(f"Search {search_data['request_id']} has null prompt, using default")
            search_data["prompt"] = "No prompt provided"
        else:
            logger.error("Cannot store search with null prompt and no request_id")
            raise ValueError("Search prompt cannot be null")
    
    # Continue with database operation
    # ...
```

### 5. Complete API Response Enhancement

The API response is missing LinkedIn URLs and company names. We'll ensure complete data is returned:

```python
# Current problematic response
{
    "candidates": [
        {
            "name": "John Doe",
            "title": "Senior Director of Commercial Sales"
            # Missing linkedin_url and company_name
        }
    ]
}

# Fixed response
{
    "candidates": [
        {
            "name": "John Doe",
            "title": "Senior Director of Commercial Sales",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "company_name": "TechCorp Inc"
        }
    ]
}
```

Implementation:
```python
def format_candidate_response(candidate_data):
    """Format candidate data ensuring all fields are included."""
    response = {
        "name": candidate_data.get("name", ""),
        "title": candidate_data.get("title", ""),
        "linkedin_url": candidate_data.get("linkedin_url", ""),
        "company_name": candidate_data.get("company_name", ""),
        # Include other fields...
    }
    return response
```

### 6. Personalized Engagement Recommendations

The engagement recommendations use generic terms instead of the candidate's first name. We'll implement proper personalization:

```python
# Current problematic code
behavioral_insight = "This Senior Director of Commercial Sales is actively researching..."

# Fixed code
def generate_personalized_insight(candidate_data, behavioral_data):
    """Generate personalized behavioral insights using candidate's name."""
    first_name = extract_first_name(candidate_data.get("name", ""))
    title = candidate_data.get("title", "professional")
    
    if first_name:
        insight = f"{first_name}, a {title}, is actively researching..."
    else:
        insight = f"This {title} is actively researching..."
    
    return insight

def extract_first_name(full_name):
    """Extract first name from full name."""
    if not full_name:
        return ""
    
    # Handle common name formats
    name_parts = full_name.strip().split()
    if name_parts:
        return name_parts[0]
    return ""
```

## API Changes

No changes to the API interface are required for these bugfixes. The fixes will maintain the same API contract while improving the internal implementation.

## Deployment Strategy

1. **Testing**: Thoroughly test the fixes in a development environment
2. **Deployment**: Deploy the fixes to the production environment
3. **Monitoring**: Monitor the system for any remaining issues
4. **Rollback Plan**: Have a rollback plan in case the fixes introduce new issues