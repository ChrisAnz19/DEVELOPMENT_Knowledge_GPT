# Evidence Search Performance and Specificity Fix Requirements

## Introduction

The evidence finding system has two critical issues: processing never completes (hangs indefinitely) and search results are too generic (e.g., returning generic Zillow/Redfin URLs instead of specific property listings for "homes in Greenwich"). This impacts user experience and the quality of evidence provided.

## Requirements

### Requirement 1: Fix Frontend Processing Status Updates

**User Story:** As a system user, I want the frontend to show when evidence finding has completed, so that I know the results are ready.

#### Acceptance Criteria

1. WHEN evidence finding completes on the backend THEN the frontend SHALL reflect the completion status
2. WHEN processing is in progress THEN the frontend SHALL show appropriate loading indicators
3. WHEN results are available THEN the frontend SHALL update to display the evidence URLs
4. WHEN processing fails THEN the frontend SHALL show error states clearly

### Requirement 2: Improve Search Query Specificity

**User Story:** As an API user, I want evidence URLs to be specific and relevant to my search, so that I get actionable information instead of generic website homepages.

#### Acceptance Criteria

1. WHEN searching for "homes in Greenwich" THEN results SHALL include specific property listings, not just generic real estate sites
2. WHEN searching for company information THEN results SHALL include specific company pages, news articles, or press releases
3. WHEN searching for person-specific information THEN results SHALL include LinkedIn profiles, company bio pages, or news mentions
4. WHEN generic results are found THEN the system SHALL attempt more specific search queries

### Requirement 3: Optimize Search Performance

**User Story:** As a system administrator, I want evidence finding to be fast and efficient, so that system resources are used optimally.

#### Acceptance Criteria

1. WHEN multiple search queries are executed THEN they SHALL run in parallel with proper concurrency limits
2. WHEN search APIs are slow THEN individual queries SHALL timeout after 5 seconds
3. WHEN search results are cached THEN subsequent similar searches SHALL return faster
4. WHEN search operations complete THEN performance metrics SHALL be logged

### Requirement 4: Enhance Search Strategy

**User Story:** As a system user, I want search results to be highly relevant and specific, so that evidence URLs provide maximum value.

#### Acceptance Criteria

1. WHEN initial search queries return generic results THEN the system SHALL try more specific query variations
2. WHEN searching for locations THEN queries SHALL include specific geographic terms and local identifiers
3. WHEN searching for companies THEN queries SHALL include company name, industry, and location modifiers
4. WHEN search results are too broad THEN the system SHALL filter for more specific content types