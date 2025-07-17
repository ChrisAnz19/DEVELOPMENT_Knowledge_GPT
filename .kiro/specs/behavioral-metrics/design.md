# Design Document: Behavioral Metrics System

## Overview

The Behavioral Metrics System enhances the existing behavioral data analysis by adding four specialized metrics: Commitment Momentum Index (CMI), Risk-Barrier Focus Score (RBFS), Identity Alignment Signal (IAS), and Psychometric Modeling Insight. These metrics provide deeper insights into prospect behavior, helping users better understand engagement patterns, risk sensitivity, value alignment, and psychological drivers.

This design document outlines the approach to implementing these new behavioral metrics, focusing on integration with the existing system, data modeling, and API enhancements.

## Architecture

The Behavioral Metrics System will extend the current architecture while maintaining backward compatibility:

1. **Behavioral Metrics Engine**: A new module that generates the specialized metrics
2. **API Integration**: Updates to include the new metrics in API responses
3. **Data Model Extensions**: New structures to represent the metrics

The system will be implemented as a Python module that can be imported by other components of the application, particularly the API and the behavioral data simulation components.

## Components and Interfaces

### 1. Behavioral Metrics Generator

```python
def generate_behavioral_metrics(
    user_prompt: str,
    candidate_data: dict,
    behavioral_data: dict = None,
    industry_context: str = None
) -> dict:
    """
    Generates specialized behavioral metrics for a candidate.
    
    Args:
        user_prompt: The user's search criteria
        candidate_data: Data about the candidate
        behavioral_data: Optional existing behavioral data
        industry_context: Optional industry context
        
    Returns:
        Dictionary containing the specialized behavioral metrics
    """
```

### 2. Commitment Momentum Index Calculator

```python
def calculate_commitment_momentum_index(
    candidate_data: dict,
    behavioral_data: dict,
    user_prompt: str = ""
) -> dict:
    """
    Calculates the Commitment Momentum Index (CMI) for a candidate.
    
    Args:
        candidate_data: Data about the candidate
        behavioral_data: Existing behavioral data
        user_prompt: Optional user search criteria
        
    Returns:
        Dictionary with CMI score and description
    """
```

### 3. Risk-Barrier Focus Score Calculator

```python
def calculate_risk_barrier_focus_score(
    candidate_data: dict,
    behavioral_data: dict,
    user_prompt: str = ""
) -> dict:
    """
    Calculates the Risk-Barrier Focus Score (RBFS) for a candidate.
    
    Args:
        candidate_data: Data about the candidate
        behavioral_data: Existing behavioral data
        user_prompt: Optional user search criteria
        
    Returns:
        Dictionary with RBFS score and description
    """
```

### 4. Identity Alignment Signal Calculator

```python
def calculate_identity_alignment_signal(
    candidate_data: dict,
    behavioral_data: dict,
    user_prompt: str = ""
) -> dict:
    """
    Calculates the Identity Alignment Signal (IAS) for a candidate.
    
    Args:
        candidate_data: Data about the candidate
        behavioral_data: Existing behavioral data
        user_prompt: Optional user search criteria
        
    Returns:
        Dictionary with IAS score and description
    """
```

### 5. Psychometric Modeling Insight Generator

```python
def generate_psychometric_modeling_insight(
    candidate_data: dict,
    behavioral_data: dict,
    user_prompt: str = ""
) -> str:
    """
    Generates a Psychometric Modeling Insight for a candidate.
    
    Args:
        candidate_data: Data about the candidate
        behavioral_data: Existing behavioral data
        user_prompt: Optional user search criteria
        
    Returns:
        String with psychometric insight
    """
```

### 6. API Integration Component

```python
def enhance_behavioral_data(
    behavioral_data: dict,
    candidates: list,
    user_prompt: str,
    industry_context: str = None
) -> dict:
    """
    Enhances existing behavioral data with specialized metrics.
    
    Args:
        behavioral_data: Existing behavioral data
        candidates: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        Enhanced behavioral data with specialized metrics
    """
```

## Data Models

### Commitment Momentum Index Model

```python
{
    "score": int,  # 0-100 score
    "description": str,  # Concise explanation
    "factors": {
        "bottom_funnel_engagement": float,  # 0-1 score
        "recency_frequency": float,  # 0-1 score
        "off_hours_activity": float  # 0-1 score
    }
}
```

### Risk-Barrier Focus Score Model

```python
{
    "score": int,  # 0-100 score
    "description": str,  # Concise explanation
    "factors": {
        "risk_content_engagement": float,  # 0-1 score
        "negative_review_focus": float,  # 0-1 score
        "compliance_focus": float  # 0-1 score
    }
}
```

### Identity Alignment Signal Model

```python
{
    "score": int,  # 0-100 score
    "description": str,  # Concise explanation
    "factors": {
        "purpose_driven_engagement": float,  # 0-1 score
        "thought_leadership_focus": float,  # 0-1 score
        "community_engagement": float  # 0-1 score
    }
}
```

### Enhanced Behavioral Data Model

```python
{
    # Existing behavioral data fields
    
    # New specialized metrics
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

## Error Handling

1. **Missing Data**: Graceful handling when candidate data is incomplete
2. **API Failures**: Fallback mechanisms when metrics cannot be calculated
3. **Input Validation**: Validation of input data before processing
4. **Response Validation**: Validation of generated metrics against expected format

## Testing Strategy

1. **Unit Tests**: Test individual metric calculators with mock data
2. **Integration Tests**: Test the entire behavioral metrics pipeline
3. **API Tests**: Verify API responses include the new metrics
4. **Edge Cases**: Test with minimal data, unusual job titles, etc.
5. **Backward Compatibility**: Ensure existing clients continue to function

## Implementation Details

### 1. Commitment Momentum Index Implementation

The CMI will be calculated based on three main factors:

1. **Bottom-of-Funnel Engagement**: Analysis of engagement with content that indicates purchase intent
   - Pricing pages
   - Product comparison tools
   - Implementation guides
   - Free trial/demo requests

2. **Recency and Frequency**: Analysis of engagement patterns over time
   - Frequency of visits
   - Recency of last visit
   - Session duration trends
   - Increasing or decreasing engagement

3. **Off-Hours Activity**: Analysis of engagement outside normal business hours
   - Weekend activity
   - Evening/night activity
   - Holiday activity

The CMI score will be calculated using a weighted formula that considers these factors, with weights adjusted based on industry context and user prompt.

### 2. Risk-Barrier Focus Score Implementation

The RBFS will be calculated based on three main factors:

1. **Risk Content Engagement**: Analysis of engagement with risk-related content
   - Security/compliance pages
   - Terms of service/legal pages
   - Risk mitigation content

2. **Negative Review Focus**: Analysis of engagement with critical content
   - Review sites with negative focus
   - Competitor comparison pages
   - Forums discussing drawbacks

3. **Compliance Focus**: Analysis of engagement with regulatory content
   - Industry compliance standards
   - Certification pages
   - Regulatory documentation

The RBFS score will be calculated using a weighted formula that considers these factors, with weights adjusted based on industry context and user prompt.

### 3. Identity Alignment Signal Implementation

The IAS will be calculated based on three main factors:

1. **Purpose-Driven Engagement**: Analysis of engagement with mission/values content
   - About us pages
   - Mission statement pages
   - Corporate social responsibility content

2. **Thought Leadership Focus**: Analysis of engagement with thought leadership content
   - Blog posts
   - Whitepapers
   - Industry reports

3. **Community Engagement**: Analysis of engagement with community content
   - Forums
   - User groups
   - Social media

The IAS score will be calculated using a weighted formula that considers these factors, with weights adjusted based on industry context and user prompt.

### 4. Psychometric Modeling Insight Implementation

The Psychometric Modeling Insight will be generated using a rule-based system that analyzes all available behavioral data to infer psychological drivers. The system will consider:

1. **Content Preferences**: Types of content the prospect engages with
2. **Engagement Patterns**: How the prospect interacts with content
3. **Decision-Making Style**: Analytical vs. emotional, quick vs. deliberate
4. **Communication Preferences**: Technical vs. high-level, detailed vs. concise

Based on this analysis, the system will generate actionable communication advice tailored to the prospect's psychological profile.

### 5. API Integration Implementation

The API integration will involve:

1. **Enhancing the `process_search` Function**: Update to include behavioral metrics generation
2. **Updating the `SearchResponse` Model**: Add new fields for behavioral metrics
3. **Documentation Updates**: Add descriptions and examples of the new metrics

## API Response Example

```json
{
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "prompt": "Looking for a senior developer with cloud experience",
  "filters": { ... },
  "candidates": [ ... ],
  "behavioral_data": {
    "commitment_momentum_index": {
      "score": 85,
      "description": "Active: Reviewing implementation guides",
      "factors": {
        "bottom_funnel_engagement": 0.9,
        "recency_frequency": 0.8,
        "off_hours_activity": 0.7
      }
    },
    "risk_barrier_focus_score": {
      "score": 35,
      "description": "Low concern: Focused on benefits",
      "factors": {
        "risk_content_engagement": 0.3,
        "negative_review_focus": 0.4,
        "compliance_focus": 0.3
      }
    },
    "identity_alignment_signal": {
      "score": 70,
      "description": "Strong alignment: Values-driven decision",
      "factors": {
        "purpose_driven_engagement": 0.7,
        "thought_leadership_focus": 0.8,
        "community_engagement": 0.6
      }
    },
    "psychometric_modeling_insight": "This prospect responds well to detailed technical information and values data-driven discussions. Focus on ROI metrics and technical specifications rather than emotional appeals."
  },
  "created_at": "2025-07-16T01:23:45Z",
  "completed_at": "2025-07-16T01:23:50Z"
}
```

This design provides a comprehensive approach to implementing the behavioral metrics system according to the requirements, focusing on integration with the existing system, data modeling, and API enhancements.