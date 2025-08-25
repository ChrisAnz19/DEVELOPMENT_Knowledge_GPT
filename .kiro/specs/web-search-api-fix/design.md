# Design Document

## Overview

The web search system is fundamentally broken because it's using OpenAI chat completions to "suggest" URLs instead of performing actual web searches. This approach cannot access real-time web data and produces unreliable results. The fix involves implementing a real web search API that can find actual, current URLs based on search queries.

## Architecture

### Current Architecture Issues
- `WebSearchEngine` uses OpenAI chat completions to "suggest" URLs instead of searching the web
- No access to real-time web data - OpenAI cannot browse the internet
- Over-complicated timeout and retry logic that makes the system slow
- API key configuration issues preventing OpenAI calls from working
- Fallback system generates static URLs instead of dynamic search results

### Proposed Architecture
- **Primary Solution:** Implement real web search using SerpAPI (Google Search API)
- **Secondary Solution:** Add DuckDuckGo search as free alternative
- **Fallback Solution:** Enhanced contextual URL generation when APIs fail
- **Configuration:** Proper API key management and environment variable handling
- **Performance:** Simplified, fast search with minimal timeouts

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

### 2. Real Web Search Integration
**New Component:** Actual web search API clients

**Primary Option: SerpAPI**
- Google search results with real-time data
- Reliable, comprehensive results
- Requires API key (paid service)
- Fast response times

**Secondary Option: DuckDuckGo Search**
- Free alternative using `duckduckgo-search` Python library
- No API key required
- Good for basic searches
- Fallback when SerpAPI fails

**Implementation Strategy:**
- Try SerpAPI first (if API key available)
- Fall back to DuckDuckGo search
- Final fallback to contextual URL generation

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
    serpapi_key: Optional[str] = None
    use_duckduckgo: bool = True  # Free fallback
    max_results_per_query: int = 5
    timeout: int = 5  # Reasonable timeout
    enable_fallback_urls: bool = True
```

### Environment Variables
- `SERPAPI_API_KEY` - SerpAPI key for Google search
- `OPENAI_API_KEY` - Already configured in secrets.json

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

### Phase 1: Real Web Search Implementation
- Install and configure SerpAPI client (`google-search-results`)
- Install DuckDuckGo search library (`duckduckgo-search`)
- Replace fake OpenAI "URL suggestion" with real web search
- Fix API key loading from secrets.json and environment variables

### Phase 2: Search Strategy Implementation
- Implement SerpAPI as primary search method
- Add DuckDuckGo as free fallback
- Maintain contextual URL generation as final fallback
- Simplify timeout and retry logic for better performance

### Phase 3: Integration & Testing
- Update context-aware evidence finder to use real search
- Test with actual search queries
- Validate URL quality and relevance
- Performance optimization and monitoring

## Key Technical Changes

### 1. Replace Fake Search with Real Search
**Current (Broken):**
```python
# This doesn't work - OpenAI can't browse the web
response = self.client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Find URLs for: {query}"}]
)
```

**New (Working):**
```python
# Real web search using SerpAPI
from serpapi import GoogleSearch
search = GoogleSearch({
    "q": query,
    "api_key": serpapi_key
})
results = search.get_dict()
```

### 2. Proper API Key Management
- Load SERPAPI_API_KEY from environment or secrets.json
- Handle missing API keys gracefully
- Fall back to free alternatives when paid APIs unavailable

### 3. Simplified Architecture
- Remove complex retry logic that causes timeouts
- Use direct API calls with simple error handling
- Fast fallback to alternative search methods