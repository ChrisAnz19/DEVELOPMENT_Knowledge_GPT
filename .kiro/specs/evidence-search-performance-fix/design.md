# Evidence Search Performance and Specificity Fix Design

## Overview

The system has two main issues: the frontend doesn't reflect when evidence finding completes (even though backend processing may finish), and search results are too generic. This design addresses both frontend status communication and search query specificity.

## Architecture

### Problem Analysis

1. **Frontend Status Issue**: Backend completes processing but frontend doesn't update
   - Possible async response handling issues
   - Missing status indicators in API responses
   - Frontend polling or websocket connection problems

2. **Search Specificity Issue**: Queries return generic results instead of specific content
   - Search queries are too broad (e.g., "real estate" instead of "Greenwich CT homes for sale")
   - No query refinement when initial results are generic
   - Missing location-specific and context-specific search terms

### Solution Architecture

```
Evidence Finding System
├── Enhanced Search Query Generation
│   ├── Location-specific query building
│   ├── Context-aware query refinement
│   └── Multi-tier search strategy
├── Improved API Response Handling
│   ├── Clear completion status indicators
│   ├── Progress tracking
│   └── Error state communication
└── Frontend Status Integration
    ├── Real-time status updates
    ├── Loading state management
    └── Result display optimization
```

## Components and Interfaces

### 1. Enhanced Search Query Generator

**Purpose**: Generate highly specific search queries instead of generic ones

**Interface**:
```python
class SpecificSearchQueryGenerator:
    def generate_location_specific_queries(self, location: str, context: str) -> List[str]:
        """Generate location-specific search queries."""
        pass
    
    def refine_generic_queries(self, initial_results: List[str]) -> List[str]:
        """Refine queries when initial results are too generic."""
        pass
    
    def build_contextual_queries(self, candidate: dict, search_context: str) -> List[str]:
        """Build context-aware queries for specific candidates."""
        pass
```

**Implementation Strategy**:
- For "homes in Greenwich" → "Greenwich CT real estate listings", "Greenwich Connecticut homes for sale", "Greenwich CT property listings MLS"
- For company searches → "CompanyName headquarters", "CompanyName press releases", "CompanyName executive team"
- For person searches → "PersonName CompanyName LinkedIn", "PersonName CompanyName biography"

### 2. API Response Status Enhancement

**Purpose**: Ensure frontend receives clear completion signals

**Interface**:
```python
class EvidenceProcessingStatus:
    status: str  # "processing", "completed", "failed"
    progress: float  # 0.0 to 1.0
    evidence_urls: List[str]
    processing_time: float
    error_message: Optional[str]
    completion_timestamp: str
```

**Implementation Strategy**:
- Add explicit status fields to all API responses
- Include processing timestamps
- Provide clear error messages when processing fails

### 3. Search Result Quality Filter

**Purpose**: Filter out generic results and prioritize specific content

**Interface**:
```python
class SearchResultFilter:
    def is_result_specific(self, url: str, title: str, snippet: str) -> bool:
        """Determine if search result is specific enough."""
        pass
    
    def score_result_relevance(self, result: dict, query_context: dict) -> float:
        """Score how relevant and specific a result is."""
        pass
    
    def filter_generic_results(self, results: List[dict]) -> List[dict]:
        """Remove overly generic results."""
        pass
```

## Data Models

### Enhanced Search Query
```python
@dataclass
class EnhancedSearchQuery:
    base_query: str
    location_modifiers: List[str]
    context_modifiers: List[str]
    specificity_level: int  # 1=generic, 5=highly specific
    expected_result_types: List[str]  # ["listing", "profile", "article"]
```

### Search Result Quality Score
```python
@dataclass
class ResultQualityScore:
    specificity_score: float  # How specific vs generic
    relevance_score: float    # How relevant to query
    content_type_score: float # Matches expected content type
    overall_score: float      # Combined score
```

## Error Handling

### Frontend Status Communication
1. **Processing Status**: Always include status in API responses
2. **Timeout Handling**: Clear timeout messages with retry options
3. **Error States**: Specific error codes for different failure types

### Search Quality Issues
1. **Generic Results**: Automatically refine queries when results are too generic
2. **No Results**: Provide fallback search strategies
3. **API Failures**: Graceful degradation with cached or fallback results

## Testing Strategy

### Frontend Integration Tests
- Test that completion status is properly communicated
- Verify loading states update correctly
- Test error state handling

### Search Specificity Tests
- Test location-specific queries return relevant results
- Verify generic result filtering works
- Test query refinement when initial results are poor

### Performance Tests
- Measure actual processing times vs perceived processing times
- Test concurrent search query execution
- Verify timeout handling works correctly

## Performance Considerations

### Search Query Optimization
- Parallel execution of multiple specific queries
- Caching of location and company-specific search patterns
- Smart query refinement based on initial result quality

### Frontend Responsiveness
- Immediate status updates when processing starts
- Progress indicators during processing
- Instant display of results when available

## Monitoring and Observability

### Search Quality Metrics
- Average specificity score of returned results
- Percentage of generic vs specific results
- Query refinement success rates

### Frontend Performance Metrics
- Time from processing completion to frontend update
- User perception of processing time
- Error rate in status communication