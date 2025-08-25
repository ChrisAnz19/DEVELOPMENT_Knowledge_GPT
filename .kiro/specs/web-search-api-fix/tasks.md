# Implementation Plan

- [x] 1. Install and configure real web search dependencies
  - Install `google-search-results` package for SerpAPI integration
  - The SerpAPI Key is in secrets.json as Serp_API_Key
  - Add packages to requirements.txt or equivalent dependency file
  - _Requirements: 2.1, 2.2_

- [ ] 2. Fix API key loading and configuration
  - [x] 2.1 Update secrets.json loading in web search engine
    - Load SERPAPI_API_KEY from secrets.json file
    - Load OPENAI_API_KEY properly from secrets.json (fix current issue)
    - Add environment variable fallback for production deployment
    - _Requirements: 1.1, 2.1_

  - [x] 2.2 Create WebSearchConfig class
    - Define configuration dataclass with API keys and settings
    - Add validation for required vs optional API keys
    - Set reasonable defaults for timeouts and result limits
    - _Requirements: 2.1, 2.3_

- [ ] 3. Replace fake OpenAI web search with real SerpAPI search
  - [x] 3.1 Implement SerpAPI search client
    - Create `_search_with_serpapi` method in WebSearchEngine
    - Parse SerpAPI JSON response into URLCandidate objects
    - Handle SerpAPI-specific errors and rate limiting
    - _Requirements: 2.1, 2.2_

  - [x] 3.2 Replace OpenAI chat completion "URL suggestion" logic
    - Remove the fake web search using OpenAI chat completions
    - Replace `_execute_search` method to use real web search APIs
    - Maintain existing URLCandidate and SearchResult data structures
    - _Requirements: 1.1, 2.2, 2.3_


- [ ] 5. Implement search strategy with proper fallbacks
  - [x] 5.1 Create search execution strategy
    - Try SerpAPI first (if API key available)

    - _Requirements: 1.3, 2.2_

  - [x] 5.2 Simplify timeout and retry logic
    - Remove complex retry mechanisms that cause slowdowns
    - Use simple timeouts (5 seconds max per search)
    - Fast failure and fallback instead of long retries
    - _Requirements: 1.2, 1.3_

- [ ] 6. Update context-aware evidence finder integration
  - [x] 6.1 Fix context-aware evidence finder to use real search results
    - Update `_execute_searches` method to work with new WebSearchEngine
    - Remove workarounds for fake OpenAI search results
    - Test contextual search queries with real web search
    - _Requirements: 3.1, 3.2_

  - [x] 6.2 Optimize evidence finder performance
    - Remove unnecessary URL validation timeouts that cause slowdowns
    - Use real search results instead of always falling back to static URLs
    - Ensure evidence URLs are actually relevant to search context
    - _Requirements: 3.2, 3.3_

- [ ] 7. Test and validate real web search functionality
  - [x] 7.1 Create comprehensive test suite
    - Test SerpAPI integration with real API calls
    - _Requirements: 2.3_

  - [ ] 7.2 Validate search result quality
    - Test with various search queries (real estate, technology, finance, hiring, sales)
    - Verify URLs are current and relevant
    - _Requirements: 3.1, 3.2_

- [ ] 8. Deploy and monitor real web search system
  - [ ] 8.1 Update deployment configuration
    - Test API key loading in production environment
    - _Requirements: 2.1, 2.3_

