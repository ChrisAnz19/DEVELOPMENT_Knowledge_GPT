# Evidence Finder Integration Fix Requirements

## Introduction

The evidence enhancement system is failing with a `'bool' object has no attribute 'timeout'` error, causing candidates to lose evidence URLs and have their accuracy scores reduced. This appears to be an integration issue between the context-aware evidence finder and the recently updated web search engine.

## Requirements

### Requirement 1: Fix Configuration Object Error

**User Story:** As a system administrator, I want the evidence finder to properly initialize the web search configuration, so that evidence URLs can be found for candidates.

#### Acceptance Criteria

1. WHEN the evidence finder initializes the web search engine THEN it SHALL receive a proper WebSearchConfig object, not a boolean
2. WHEN the web search configuration is loaded THEN it SHALL contain all required attributes including timeout
3. IF configuration loading fails THEN the system SHALL provide a default configuration with proper error handling
4. WHEN the evidence finder processes candidates THEN it SHALL not crash with attribute errors

### Requirement 2: Restore Evidence URL Functionality

**User Story:** As an API user, I want candidates to include relevant evidence URLs, so that I can verify the accuracy of behavioral assessments.

#### Acceptance Criteria

1. WHEN candidates are processed THEN they SHALL include evidence URLs when available
2. WHEN evidence finding succeeds THEN candidate accuracy scores SHALL not be artificially reduced
3. WHEN evidence finding fails gracefully THEN fallback URLs SHALL be provided
4. WHEN no evidence is found THEN the system SHALL log the reason clearly

### Requirement 3: Maintain System Performance

**User Story:** As a system user, I want evidence finding to complete quickly, so that API responses remain fast.

#### Acceptance Criteria

1. WHEN evidence finding is enabled THEN it SHALL complete within 10 seconds
2. WHEN web search fails THEN the system SHALL fall back to contextual URLs immediately
3. WHEN processing multiple candidates THEN evidence finding SHALL not block the main pipeline
4. WHEN errors occur THEN they SHALL be logged without crashing the system

### Requirement 4: Ensure Backward Compatibility

**User Story:** As an API consumer, I want existing integrations to continue working, so that I don't need to update my code.

#### Acceptance Criteria

1. WHEN evidence finding is disabled THEN candidates SHALL be returned without evidence URLs
2. WHEN evidence finding fails THEN candidates SHALL still be returned with their original data
3. WHEN the API response format changes THEN it SHALL remain backward compatible
4. WHEN configuration is missing THEN the system SHALL work with default settings