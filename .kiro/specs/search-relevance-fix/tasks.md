# Implementation Plan

- [x] 1. Enhance context analysis for better search query understanding
  - Modify `analyze_search_context()` function in `behavioral_metrics_ai.py` to add new context categories
  - Add detection patterns for real estate, legal services, personal purchases, and other non-B2B contexts
  - Implement confidence scoring system for context detection accuracy
  - Add unit tests for context analysis with various search query patterns
  - _Requirements: 4.1, 4.2_

- [x] 2. Create context-specific behavioral activity templates
  - Create new activity template dictionaries in `assess_and_return.py` for different contexts (real estate, legal, personal purchases)
  - Add real estate research activities (property analysis, neighborhood research, mortgage planning)
  - Add legal services activities (attorney research, case evaluation, consultation scheduling)
  - Add personal purchase activities (product research, comparison shopping, decision factors)
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 3. Implement contextual activity selection logic
  - Modify `_generate_realistic_behavioral_reasons()` function in `assess_and_return.py` to use context-aware selection
  - Add `select_contextual_activities()` function that matches activities to search context and candidate role
  - Implement role-context relevance scoring to ensure logical connections between prospect background and behavioral data
  - Add fallback logic for unknown contexts to use generic professional activities
  - _Requirements: 1.4, 3.1, 3.2, 3.3_

- [ ] 4. Enhance photo validation and extraction system
  - Modify `extract_profile_photo_url()` function in `api/main.py` to add photo URL validation
  - Implement photo URL accessibility checking before returning URLs
  - Add photo source tracking (LinkedIn, Apollo, organization, none) in response metadata
  - Remove fallback to random/generic photos - return null when no valid photo is available
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 5. Update API response structure for enhanced photo metadata
  - Modify candidate response structure in `api/main.py` to include photo validation metadata
  - Add fields for photo_source, validation_status, and fallback_reason
  - Ensure backward compatibility with existing API clients
  - Update photo processing in the search results endpoint to use enhanced validation
  - _Requirements: 2.1, 2.4_

- [ ] 6. Implement comprehensive testing for context analysis
  - Create test cases in new file `test_search_context_analysis.py` for various search query types
  - Test real estate queries ("executive looking to buy home in Greenwich, Connecticut")
  - Test legal service queries ("attorney specializing in corporate law")
  - Test B2B technology queries ("CTO evaluating cloud infrastructure")
  - Test edge cases with ambiguous or mixed contexts
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 7. Create integration tests for contextual behavioral data
  - Create test cases in new file `test_contextual_behavioral_data.py` for end-to-end behavioral data generation
  - Test that real estate searches generate property-related activities, not technology demos
  - Test that executive roles get appropriate decision-making behavioral patterns
  - Test activity diversity across multiple candidates in same search
  - Verify logical consistency between candidate role and search context
  - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

- [ ] 8. Add photo validation testing and error handling
  - Create test cases in new file `test_photo_validation.py` for photo URL validation
  - Test photo URL accessibility and validation logic
  - Test fallback behavior when LinkedIn photos are unavailable
  - Test photo source prioritization (LinkedIn > Apollo > none)
  - Add error handling for photo validation failures that doesn't break API responses
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 9. Update behavioral metrics AI to support enhanced context analysis
  - Modify `enhance_behavioral_data_for_multiple_candidates()` function in `behavioral_metrics_ai.py` to use new context analysis
  - Update AI prompts to consider search context when generating behavioral insights
  - Ensure behavioral insights align with contextual activities selected
  - Add validation that generated insights match the search context appropriately
  - _Requirements: 3.1, 3.2, 3.4_

- [ ] 10. Create end-to-end validation tests for search relevance
  - Create comprehensive test in new file `test_search_relevance_validation.py`
  - Test complete search flow from query to final results with various contexts
  - Validate that "executive looking to buy home in Greenwich" returns real estate behavioral data
  - Validate that correct photos are returned or null when unavailable
  - Test that behavioral insights demonstrate logical connection to search query
  - _Requirements: 1.1, 1.2, 2.1, 3.1, 3.2_