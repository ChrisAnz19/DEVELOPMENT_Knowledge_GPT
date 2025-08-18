# Requirements Document

## Introduction

This feature addresses critical issues with search result relevance and data accuracy in the prospect search system. Currently, the system returns irrelevant behavioral data that doesn't match the search context (e.g., technology demos for real estate searches) and displays incorrect profile photos (fallback images instead of actual LinkedIn photos). These issues significantly impact user trust and the utility of search results.

## Requirements

### Requirement 1

**User Story:** As a user searching for prospects in specific contexts (like real estate), I want to see behavioral data that's relevant to my search query, so that I can understand how prospects actually relate to what I'm looking for.

#### Acceptance Criteria

1. WHEN a user searches for prospects in a specific domain (real estate, legal, etc.) THEN the system SHALL generate behavioral activities relevant to that domain
2. WHEN the search context is about personal purchases (homes, cars, etc.) THEN behavioral data SHALL reflect personal buying behaviors, not B2B technology activities
3. WHEN the search involves professional services THEN behavioral data SHALL align with that service category
4. WHEN no relevant behavioral patterns can be determined THEN the system SHALL use generic professional activities rather than domain-specific ones that don't match

### Requirement 2

**User Story:** As a user, I want to see accurate profile photos for prospects, so that I can properly identify and remember the people I'm researching.

#### Acceptance Criteria

1. WHEN a prospect has a LinkedIn profile photo available THEN the system SHALL display that actual photo
2. WHEN multiple photo sources are available THEN the system SHALL prioritize LinkedIn photos over generic fallback images
3. WHEN a prospect's actual photo cannot be retrieved THEN the system SHALL either show no photo or a clearly marked placeholder, not a random person's photo
4. WHEN photo URLs are processed THEN the system SHALL validate they belong to the correct person before displaying

### Requirement 3

**User Story:** As a user, I want search results to demonstrate logical connections between prospects and my search query, so that I can trust the relevance of the matches.

#### Acceptance Criteria

1. WHEN generating behavioral insights THEN the system SHALL analyze the logical relationship between the prospect's role and the search context
2. WHEN a prospect's professional background doesn't align with the search context THEN the system SHALL adjust behavioral data to reflect realistic personal interest rather than professional expertise
3. WHEN search context involves personal decisions (buying homes, cars, etc.) THEN behavioral data SHALL focus on personal research and decision-making patterns
4. WHEN prospects are executives or high-level professionals THEN behavioral data SHALL reflect appropriate decision-making authority and research depth

### Requirement 4

**User Story:** As a developer, I want improved context analysis for search queries, so that the system can better understand what users are actually looking for.

#### Acceptance Criteria

1. WHEN processing search queries THEN the system SHALL categorize the search context (B2B technology, personal purchases, professional services, etc.)
2. WHEN the search context is identified THEN the system SHALL select appropriate behavioral activity templates for that context
3. WHEN generating behavioral data THEN the system SHALL consider both the prospect's professional role and the search context to create realistic scenarios
4. WHEN context analysis is uncertain THEN the system SHALL default to generic professional activities rather than potentially irrelevant specific ones

### Requirement 5

**User Story:** As a user viewing candidate behavioral metrics, I want the CMI, RBFS, and IAS descriptions to match the actual search context, so that the behavioral insights are relevant and credible.

#### Acceptance Criteria

1. WHEN generating behavioral metrics for real estate searches THEN the system SHALL use real estate-specific language and activities in metric descriptions (not "comparing vendor solutions")
2. WHEN generating behavioral metrics for legal services searches THEN the system SHALL use legal-specific language and activities in metric descriptions  
3. WHEN generating behavioral metrics for business solution searches THEN the system SHALL use business/vendor-specific language and activities in metric descriptions
4. WHEN the search context is unclear THEN the system SHALL use generic professional language that doesn't reference specific industries or activities
5. WHEN displaying CMI scores for real estate searches THEN descriptions SHALL reference property research, market analysis, or real estate activities
6. WHEN displaying RBFS scores for real estate searches THEN descriptions SHALL reference property evaluation, location assessment, or real estate decision-making
7. WHEN displaying IAS scores for real estate searches THEN descriptions SHALL reference personal investment in property search or real estate research intensity