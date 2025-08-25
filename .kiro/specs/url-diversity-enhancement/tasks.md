# Implementation Plan

- [x] 1. Create Global URL Registry and tracking system
  - Implement `GlobalURLRegistry` class with URL and domain tracking capabilities
  - Create methods for checking URL availability and registering usage
  - Add candidate assignment tracking and diversity metrics calculation
  - Write unit tests for registry operations and uniqueness enforcement
  - _Requirements: 1.1, 1.3, 1.4, 6.2, 6.3_

- [x] 2. Build Alternative Source Manager for diverse company discovery
  - Create `AlternativeSourceManager` class with categorized alternative companies database
  - Implement company categorization logic based on product types and claim analysis
  - Add rotation algorithms for selecting different alternatives per candidate
  - Create methods for excluding major players and finding niche sources
  - Write unit tests for alternative source selection and rotation logic
  - _Requirements: 2.1, 2.2, 2.4, 3.1, 3.2_

- [x] 3. Enhance Search Query Generator with diversity-focused strategies
  - Extend `SearchQueryGenerator` class with diversity-aware query generation methods
  - Implement `create_alternative_company_queries()` for targeting lesser-known sources
  - Add diversity modifiers that exclude major players and promote variety
  - Create query strategies that rotate through different source types per candidate
  - Write unit tests for diverse query generation and alternative source targeting
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.1, 7.2_

- [x] 4. Implement Uniqueness-Aware Evidence Validator
  - Extend `EvidenceValidator` class with global uniqueness checking capabilities
  - Add `validate_with_uniqueness()` method that filters already-used URLs
  - Implement diversity scoring that rewards unique domains and source types
  - Create domain tracking per candidate to avoid repetition within single results
  - Write unit tests for uniqueness enforcement and diversity scoring
  - _Requirements: 1.2, 1.5, 5.1, 5.2, 5.3_

- [x] 5. Create Diversity Orchestrator for batch coordination
  - Implement `DiversityOrchestrator` class to manage diversity across candidate batches
  - Add batch processing logic that optimizes URL assignments for maximum diversity
  - Create diversity configuration system with configurable weights and constraints
  - Implement fallback strategies when uniqueness constraints cannot be met
  - Write unit tests for batch diversity optimization and configuration handling
  - _Requirements: 6.1, 6.4, 6.5, 8.1, 8.2_

- [x] 6. Add diversity scoring and metrics calculation
  - Implement `DiversityMetrics` class to track and calculate diversity statistics
  - Create diversity scoring algorithms that balance relevance with uniqueness
  - Add source tier classification (major, mid-tier, niche, alternative)
  - Implement diversity index calculation using Shannon entropy or similar measures
  - Write unit tests for diversity metrics and scoring algorithms
  - _Requirements: 5.4, 5.5, 7.3, 7.4, 7.5_

- [x] 7. Implement enhanced data models and configuration
  - Create `EnhancedEvidenceURL` model with diversity-specific fields
  - Implement `DiversityConfig` class for configurable diversity parameters
  - Add `DiversityMetrics` data model for tracking diversity statistics
  - Create serialization methods for enhanced evidence URLs with diversity data
  - Write unit tests for data model validation and serialization
  - _Requirements: 8.3, 8.4, 8.5_

- [x] 8. Add fallback and alternative discovery strategies
  - Implement creative search strategies when primary diverse sources are exhausted
  - Create category expansion logic for broader alternative source discovery
  - Add temporal and geographic variation in search queries for more diversity
  - Implement quality relaxation strategies that maintain minimum standards while increasing variety
  - Write unit tests for fallback strategies and alternative discovery methods
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 9. Integrate diversity system with existing URL Evidence Finder
  - Modify `URLEvidenceFinder` class to use diversity-enhanced components
  - Add diversity configuration options to the main evidence finder interface
  - Implement backward compatibility mode for existing functionality
  - Create feature flag system to enable/disable diversity enhancements
  - Write integration tests for enhanced evidence finder with diversity features
  - _Requirements: 4.1, 4.2, 4.4, 4.5_


- [x] 12. Add monitoring and analytics for diversity system
  - Implement diversity metrics tracking and reporting functionality
  - Create monitoring hooks for URL uniqueness rates and source tier distribution
  - Add performance monitoring for diversity processing overhead
  - Implement quality impact tracking to monitor relevance scores with diversity enabled
  - Write tests for monitoring and analytics functionality
  - _Requirements: 6.4, 6.5, 8.1, 8.2_