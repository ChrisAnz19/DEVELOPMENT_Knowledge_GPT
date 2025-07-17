# Design Document: Focused Behavioral Insight

## Overview

The Focused Behavioral Insight feature will transform the current multi-metric behavioral data system into a streamlined approach that provides a single, actionable insight for engaging with prospects. This design document outlines the approach to implementing this enhancement, focusing on simplifying the behavioral metrics output, ensuring logical consistency with search context, improving profile photo handling, and updating API documentation.

## Architecture

The implementation will modify the existing behavioral metrics system while maintaining backward compatibility:

1. **Behavioral Metrics Module Update**: Modify the existing `behavioral_metrics.py` module to generate a single focused insight
2. **API Integration**: Update the API response structure in `api/main.py`
3. **Photo URL Handling**: Enhance the photo URL extraction and prioritization logic
4. **Documentation Update**: Revise the API documentation to reflect the new format

## Components and Interfaces

### 1. Focused Behavioral Insight Generator

```python
def generate_focused_behavioral_insight(
    user_prompt: str,
    candidate_data: dict,
    behavioral_data: dict = None,
    industry_context: str = None
) -> str:
    """
    Generates a single, focused behavioral insight for a prospect.
    
    Args:
        user_prompt: The user's search criteria
        candidate_data: Data about the candidate
        behavioral_data: Optional existing behavioral data
        industry_context: Optional industry context
        
    Returns:
        String containing a focused behavioral insight
    """
```

### 2. Enhanced Behavioral Data Generator

```python
def enhance_behavioral_data(
    behavioral_data: dict,
    candidates: list,
    user_prompt: str,
    industry_context: str = None
) -> dict:
    """
    Enhances existing behavioral data with a focused behavioral insight.
    
    Args:
        behavioral_data: Existing behavioral data
        candidates: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        Enhanced behavioral data with focused insight
    """
```

### 3. Photo URL Extraction and Prioritization

```python
def extract_profile_photo_url(
    candidate_data: dict,
    linkedin_profile: dict = None
) -> str:
    """
    Extracts and prioritizes profile photo URLs from various sources.
    
    Args:
        candidate_data: Data about the candidate
        linkedin_profile: Optional LinkedIn profile data
        
    Returns:
        String containing the best available profile photo URL
    """
```

## Data Models

### Current Behavioral Data Model

```python
{
    "commitment_momentum_index": {
        "score": int,
        "description": str,
        "factors": dict
    },
    "risk_barrier_focus_score": {
        "score": int,
        "description": str,
        "factors": dict
    },
    "identity_alignment_signal": {
        "score": int,
        "description": str,
        "factors": dict
    },
    "psychometric_modeling_insight": str
}
```

### New Focused Behavioral Data Model

```python
{
    "behavioral_insight": str  # Single, focused behavioral insight
}
```

### API Response Model Update

```python
{
    "request_id": str,
    "status": str,
    "prompt": str,
    "filters": dict,
    "candidates": list,
    "behavioral_data": {
        "behavioral_insight": str  # Single, focused behavioral insight
    },
    "created_at": str,
    "completed_at": str
}
```

## Error Handling

1. **Missing Data**: Graceful handling when candidate data is incomplete
2. **API Failures**: Fallback mechanisms when insights cannot be generated
3. **Photo URL Extraction**: Robust handling of missing or invalid photo URLs
4. **Backward Compatibility**: Ensure existing clients continue to function

## Testing Strategy

1. **Unit Tests**: Test the focused insight generator with mock data
2. **Integration Tests**: Test the entire behavioral data pipeline
3. **API Tests**: Verify API responses include the new format
4. **Edge Cases**: Test with minimal data, unusual job titles, etc.
5. **Backward Compatibility**: Ensure existing clients continue to function

## Implementation Details

### 1. Focused Behavioral Insight Implementation

The focused behavioral insight will be generated based on:

1. **Prospect Role Analysis**: Understanding the prospect's role and responsibilities
   - Job title analysis
   - Seniority level determination
   - Decision-making authority assessment

2. **Industry Context Analysis**: Understanding the industry context
   - Industry-specific communication preferences
   - Common pain points and priorities
   - Typical buying processes

3. **Search Context Analysis**: Understanding the user's intent
   - Search query analysis
   - Implied user goals
   - Relationship between user and prospect

4. **Engagement Strategy Generation**: Creating actionable guidance
   - Communication style recommendations
   - Specific conversation starters
   - Value proposition framing

The insight will be generated using a rule-based system that combines these factors to produce a single, focused recommendation that is:
- Specific and actionable
- Relevant to the prospect's role and psychology
- Logically consistent with the search context
- Useful for the user's goals

### 2. Photo URL Extraction and Prioritization Implementation

The photo URL extraction will follow this prioritization strategy:

1. LinkedIn profile photo (if available)
2. Apollo API profile photo
3. Other available photo sources
4. Graceful handling when no photo is available

The implementation will:
- Check multiple fields where photos might be stored
- Validate URLs before returning them
- Handle edge cases like empty strings or invalid URLs
- Provide consistent behavior across different data sources

### 3. API Integration Implementation

The API integration will involve:

1. **Updating the `enhance_behavioral_data` Function**: Modify to generate a single insight
2. **Modifying the API Response Structure**: Update to include the new format
3. **Ensuring Backward Compatibility**: Maintain support for existing clients

### 4. Documentation Update Implementation

The API documentation will be updated to:

1. Explain the new focused behavioral insight format
2. Provide examples of the new format
3. Include guidance on how to use the new format in frontend applications
4. Maintain backward compatibility information

## API Response Example

```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "prompt": "Looking for a senior developer with cloud experience",
  "filters": { ... },
  "candidates": [
    {
      "name": "John Doe",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "email": "john.doe@techcorp.com",
      "accuracy": 92,
      "reasons": ["5+ years experience", "Python and React skills", "San Francisco location"],
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "profile_photo_url": "https://example.com/photo.jpg",
      "location": "San Francisco, CA",
      "linkedin_profile": { ... }
    }
  ],
  "behavioral_data": {
    "behavioral_insight": "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing."
  },
  "created_at": "2025-07-16T01:23:45Z",
  "completed_at": "2025-07-16T01:23:50Z"
}
```

This design provides a comprehensive approach to implementing the focused behavioral insight feature according to the requirements, focusing on simplifying the behavioral metrics output, ensuring logical consistency with search context, improving profile photo handling, and updating API documentation.