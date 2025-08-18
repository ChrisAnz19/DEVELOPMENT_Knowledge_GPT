# Design Document: Search Relevance Fix

## Overview

The Search Relevance Fix addresses two critical issues in the prospect search system: irrelevant behavioral data generation and incorrect profile photo display. The current system generates generic B2B technology activities regardless of search context and shows fallback photos instead of actual LinkedIn profile images. This design implements context-aware behavioral data generation and improved photo validation to ensure search results are relevant and accurate.

## Architecture

The solution involves modifications to three key components:

1. **Context Analysis Engine**: Enhanced search query analysis to categorize search intent (real estate, legal services, personal purchases, B2B technology, etc.)
2. **Behavioral Data Generator**: Context-aware activity selection that matches behavioral patterns to search context
3. **Photo Validation System**: Improved photo extraction with validation and fallback handling

## Components and Interfaces

### 1. Enhanced Context Analysis

```python
def analyze_search_context_enhanced(user_prompt: str) -> dict:
    """
    Enhanced search context analysis that better categorizes search intent.
    
    Returns:
        {
            "context_type": str,  # "real_estate", "legal_services", "personal_purchase", "b2b_technology", etc.
            "decision_factors": list,  # Key factors influencing the decision
            "behavioral_focus": str,  # "personal", "professional", "mixed"
            "activity_templates": list  # Appropriate activity templates for this context
        }
    """
```

### 2. Context-Aware Behavioral Activity Selection

```python
def select_contextual_activities(
    context_analysis: dict,
    candidate_role: str,
    candidate_index: int
) -> list:
    """
    Select behavioral activities that match the search context and candidate profile.
    
    Args:
        context_analysis: Output from analyze_search_context_enhanced()
        candidate_role: The candidate's professional role/title
        candidate_index: Index for diversity in activity selection
        
    Returns:
        List of contextually relevant behavioral activities
    """
```

### 3. Enhanced Photo Validation

```python
def validate_and_extract_photo_url(
    candidate_data: dict,
    linkedin_profile: dict = None,
    candidate_name: str = None
) -> dict:
    """
    Enhanced photo extraction with validation and proper fallback handling.
    
    Returns:
        {
            "photo_url": str or None,
            "photo_source": str,  # "linkedin", "apollo", "fallback", "none"
            "validation_status": str,  # "validated", "unvalidated", "failed"
            "fallback_reason": str or None
        }
    """
```

## Data Models

### Context Analysis Result

```python
{
    "context_type": "real_estate",  # or "legal_services", "personal_purchase", "b2b_technology", etc.
    "decision_factors": [
        "location_preference",
        "property_type", 
        "budget_considerations",
        "timeline_urgency"
    ],
    "behavioral_focus": "personal",  # "personal", "professional", "mixed"
    "activity_templates": [
        "real_estate_research",
        "location_analysis", 
        "market_comparison",
        "financial_planning"
    ],
    "confidence_score": 0.85
}
```

### Enhanced Photo Result

```python
{
    "photo_url": "https://media.licdn.com/dms/image/...",
    "photo_source": "linkedin",
    "validation_status": "validated",
    "fallback_reason": None,
    "metadata": {
        "last_validated": "2025-01-17T10:30:00Z",
        "validation_method": "url_check"
    }
}
```

## Behavioral Activity Templates

### Real Estate Context Activities

```python
REAL_ESTATE_ACTIVITIES = {
    "research_activities": [
        "Researched neighborhood demographics and school ratings on GreatSchools.org and Niche.com",
        "Analyzed property values and market trends on Zillow.com, Redfin.com, and Realtor.com",
        "Explored mortgage rates and loan options on Bankrate.com, LendingTree.com, and local bank websites",
        "Investigated property tax rates and municipal services on county assessor websites",
        "Studied commute times and transportation options using Google Maps and local transit websites"
    ],
    "evaluation_activities": [
        "Scheduled property viewings through real estate agent platforms and MLS systems",
        "Attended open houses and private showings in target neighborhoods",
        "Coordinated home inspections with certified inspectors and contractors",
        "Requested property disclosures and HOA documentation from listing agents",
        "Evaluated comparable sales data through real estate databases and agent reports"
    ],
    "comparison_activities": [
        "Compared property features, pricing, and location benefits across multiple listings",
        "Analyzed cost of living differences between neighborhoods and school districts",
        "Evaluated property investment potential and long-term value appreciation",
        "Compared homeowner insurance quotes from multiple providers",
        "Assessed renovation costs and property improvement opportunities"
    ]
}
```

### Legal Services Context Activities

```python
LEGAL_SERVICES_ACTIVITIES = {
    "research_activities": [
        "Researched attorney credentials and bar association ratings on state bar websites",
        "Analyzed case outcomes and legal precedents relevant to their situation",
        "Investigated law firm specializations and practice area expertise",
        "Studied legal fee structures and billing practices across different firms",
        "Explored alternative dispute resolution options and mediation services"
    ],
    "evaluation_activities": [
        "Scheduled consultations with multiple attorneys to discuss case details",
        "Requested case assessments and legal strategy recommendations",
        "Evaluated attorney communication styles and responsiveness during initial meetings",
        "Reviewed client testimonials and case study examples from law firm websites",
        "Assessed law firm resources, support staff, and case management capabilities"
    ]
}
```

## Error Handling

### Context Analysis Fallbacks

1. **Unknown Context**: When search context cannot be categorized, default to generic professional activities
2. **Mixed Context**: When multiple contexts are detected, prioritize based on confidence scores
3. **Insufficient Data**: When candidate role information is limited, use broad professional templates

### Photo Validation Fallbacks

1. **Invalid LinkedIn URL**: Attempt to extract from other sources (Apollo, organization data)
2. **Broken Image Links**: Validate URLs before returning, remove if inaccessible
3. **No Photo Available**: Return null instead of random fallback images
4. **Validation Failure**: Log the issue but don't block the response

## Testing Strategy

### Unit Tests

1. **Context Analysis Tests**:
   - Test various search query patterns (real estate, legal, B2B technology)
   - Verify correct context categorization and confidence scores
   - Test edge cases with ambiguous or mixed contexts

2. **Activity Selection Tests**:
   - Verify activities match search context appropriately
   - Test role-context combinations (executive + real estate, lawyer + technology)
   - Ensure activity diversity across multiple candidates

3. **Photo Validation Tests**:
   - Test photo URL validation and accessibility
   - Verify fallback behavior when photos are unavailable
   - Test photo source prioritization (LinkedIn > Apollo > none)

### Integration Tests

1. **End-to-End Search Tests**:
   - Test complete search flow with various query types
   - Verify behavioral data relevance matches search context
   - Confirm photo accuracy and fallback handling

2. **API Response Tests**:
   - Validate API response structure includes new photo metadata
   - Test backward compatibility with existing clients
   - Verify error handling doesn't break existing functionality

### Performance Tests

1. **Context Analysis Performance**: Ensure analysis doesn't significantly impact response times
2. **Photo Validation Performance**: Test photo URL validation doesn't cause timeouts
3. **Memory Usage**: Monitor memory impact of enhanced activity templates

## Implementation Approach

### Phase 1: Context Analysis Enhancement
- Enhance `analyze_search_context()` function in `behavioral_metrics_ai.py`
- Add new context categories and detection patterns
- Implement confidence scoring for context detection

### Phase 2: Activity Template System
- Create context-specific activity templates in `assess_and_return.py`
- Modify `_generate_realistic_behavioral_reasons()` to use contextual templates
- Implement role-context matching logic

### Phase 3: Photo Validation System
- Enhance `extract_profile_photo_url()` function in `api/main.py`
- Add photo URL validation and metadata tracking
- Implement proper fallback handling (null instead of random photos)

### Phase 4: Integration and Testing
- Update API response structure to include photo metadata
- Add comprehensive test coverage for all new functionality
- Perform end-to-end testing with various search scenarios

This design ensures that search results provide contextually relevant behavioral insights and accurate profile photos, significantly improving the user experience and trust in the system.