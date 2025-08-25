# Design Document

## Overview

The web search API fix involves replacing the deprecated OpenAI `web_search` tool with alternative search methods. The design maintains backward compatibility while providing reliable web search functionality for evidence URL discovery.

## Architecture

### Current Architecture Issues
- `WebSearchEngine` class uses deprecated `"web_search"` tool type
- Direct dependency on OpenAI's removed web search functionality
- No fallback mechanism when web search fails

### Proposed Architecture
- Replace OpenAI web search with external search API (e.g., SerpAPI, Bing Search API)
- Implement fallback to predefined URL patterns when external search fails
- Maintain existing interface to avoid breaking changes in dependent components

## Components and Interfaces

### 1. WebSearchEngine (Modified)
**Location:** `web_search_engine.py`

**Key Changes:**
- Remove `tools=[{"type": "web_search"}]` from OpenAI API calls
- Implement external search API integration
- Add fallback URL generation based on search patterns

**Interface (Unchanged):**
```python
async def search_for_evidence(self, queries: List[SearchQuery]) -> List[SearchResult]
```

### 2. External Search Integration
**New Component:** Search API client for external web search

**Options:**
1. **SerpAPI** - Google search results API
2. **Bing Search API** - Microsoft's search API  
3. **DuckDuckGo Instant Answer API** - Free alternative

**Recommended:** SerpAPI for reliability and comprehensive results

### 3. Fallback URL Generator
**New Component:** Pattern-based URL generation when external search fails

**Functionality:**
- Generate relevant URLs based on search query patterns
- Use domain-specific URL templates (e.g., company websites, industry directories)
- Maintain diversity requirements from existing system

## Data Models

### SearchResult (Unchanged)
Existing `SearchResult` class maintains same structure:
```python
@dataclass
class SearchResult:
    query: SearchQuery
    urls: List[URLCandidate]
    citations: List[str]
    success: bool
    error_message: Optional[str] = None
```

### New Configuration Model
```python
@dataclass
class WebSearchConfig:
    primary_api: str = "serpapi"  # "serpapi", "bing", "fallback"
    api_key: Optional[str] = None
    fallback_enabled: bool = True
    max_results_per_query: int = 5
    timeout: int = 10
```

## Error Handling

### 1. API Failure Handling
- **Primary Search Fails:** Automatically fall back to pattern-based URL generation
- **Rate Limiting:** Implement exponential backoff and queue management
- **Invalid API Keys:** Log error and use fallback mode

### 2. Graceful Degradation
- **No Search Results:** Return empty results rather than failing
- **Partial Failures:** Process successful queries and log failures
- **Complete Search Failure:** Continue evidence finding with cached/predefined URLs

### 3. Error Logging
- Log all search failures with query details
- Track API usage and rate limiting
- Monitor fallback usage patterns

## Testing Strategy

### 1. Unit Tests
- Test external API integration with mocked responses
- Test fallback URL generation patterns
- Test error handling scenarios

### 2. Integration Tests
- Test with real API keys (in CI/CD environment)
- Test evidence finder integration
- Test diversity orchestrator compatibility

### 3. Performance Tests
- Measure search response times
- Test concurrent search handling
- Validate memory usage with large query batches

### 4. Fallback Tests
- Test behavior when external APIs are unavailable
- Validate URL pattern generation quality
- Test graceful degradation scenarios

## Implementation Phases

### Phase 1: External Search Integration
- Implement SerpAPI client
- Replace OpenAI web search calls
- Add basic error handling

### Phase 2: Fallback System
- Implement pattern-based URL generation
- Add configuration management
- Enhance error handling

### Phase 3: Testing & Optimization
- Comprehensive testing suite
- Performance optimization
- Documentation updates