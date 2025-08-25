# Implementation Plan

- [x] 1. Remove deprecated OpenAI web search tool usage
  - Remove `"web_search"` tool type from OpenAI API calls in `web_search_engine.py`
  - Update the `_execute_search_query` method to use standard chat completion without tools
  - Add error handling for the transition period
  - _Requirements: 1.1, 1.2_

- [ ] 2. Implement external search API integration
  - [ ] 2.1 Create SerpAPI client integration
    - Add SerpAPI dependency and configuration
    - Implement search query execution using SerpAPI
    - Parse SerpAPI responses into existing URLCandidate format
    - _Requirements: 2.1, 2.2_

  - [ ] 2.2 Update WebSearchEngine to use external search
    - Replace OpenAI web search logic with SerpAPI calls
    - Maintain existing method signatures and return types
    - Add API key configuration and validation
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 3. Implement fallback URL generation system
  - [x] 3.1 Create pattern-based URL generator
    - Implement URL pattern matching for common search types
    - Create domain-specific URL templates (company sites, directories)
    - Generate relevant URLs when external search fails
    - _Requirements: 1.3, 2.2_

  - [x] 3.2 Integrate fallback system with WebSearchEngine
    - Add fallback logic when external API fails
    - Ensure fallback URLs maintain diversity requirements
    - Log fallback usage for monitoring
    - _Requirements: 1.3, 3.3_

- [ ] 4. Add configuration management
  - Create WebSearchConfig class for search settings
  - Add environment variable support for API keys
  - Implement configuration validation and defaults
  - _Requirements: 2.1, 2.3_

- [x] 5. Enhance error handling and logging
  - [x] 5.1 Implement comprehensive error handling
    - Add try-catch blocks for API failures
    - Implement exponential backoff for rate limiting
    - Handle network timeouts and connection errors
    - _Requirements: 1.2, 1.3_

  - [x] 5.2 Add detailed logging and monitoring
    - Log all search attempts and results
    - Track API usage and rate limiting
    - Monitor fallback system usage
    - _Requirements: 1.3, 3.3_

- [ ] 6. Update tests for new search implementation
  - [ ] 6.1 Update existing unit tests
    - Modify tests to work with new search implementation
    - Add mocks for external API calls
    - Test error handling scenarios
    - _Requirements: 2.3_

  - [ ] 6.2 Add integration tests for external search
    - Test SerpAPI integration with real API calls
    - Test fallback system activation
    - Test evidence finder integration
    - _Requirements: 2.2, 2.3_

- [x] 7. Update documentation and deployment
  - Update README with new API key requirements
  - Add configuration examples for different environments
  - Update deployment guide with external API setup
  - _Requirements: 2.1, 2.3_