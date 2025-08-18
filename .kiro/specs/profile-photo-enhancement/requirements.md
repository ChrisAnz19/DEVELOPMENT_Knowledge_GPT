# LinkedIn Photo Validation Requirements

## Introduction

The current system occasionally shows LinkedIn's default fallback image (`https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2`) instead of actual candidate profile photos. This reduces the visual quality and professional appearance of search results. Instead of trying to find alternative photo sources, the system should prioritize candidates who have valid LinkedIn profile photos and skip those who only have fallback images.

## Requirements

### Requirement 1: LinkedIn Photo Validation and Filtering

**User Story:** As a user viewing search results, I want to see only candidates with actual LinkedIn profile photos, so that I can properly identify and connect with potential prospects.

#### Acceptance Criteria

1. WHEN the system receives a LinkedIn profile photo URL THEN it SHALL validate that the URL points to an actual profile photo and not LinkedIn's fallback image
2. WHEN a LinkedIn fallback image URL is detected (`https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2`) THEN the system SHALL mark that candidate as having no valid photo
3. WHEN a candidate has no valid LinkedIn photo THEN the system SHALL skip that candidate and select a different person from the available pool
4. WHEN all candidates in the initial batch lack valid photos THEN the system SHALL request additional candidates from the data source until it finds candidates with valid photos

### Requirement 2: Candidate Selection Prioritization

**User Story:** As a user, I want the system to prioritize candidates with professional LinkedIn photos, so that my search results have consistent visual quality.

#### Acceptance Criteria

1. WHEN selecting candidates from search results THEN the system SHALL prioritize candidates with valid LinkedIn profile photos over those without
2. WHEN multiple candidates have similar relevance scores THEN the system SHALL prefer candidates with valid LinkedIn photos
3. WHEN the system has exhausted candidates with photos THEN it SHALL return fewer results rather than including candidates with fallback images
4. WHEN no candidates with valid photos are available THEN the system SHALL return an appropriate message indicating limited photo availability

### Requirement 3: Photo URL Validation Logic

**User Story:** As a developer, I want reliable photo validation logic, so that the system can accurately distinguish between real profile photos and LinkedIn's fallback images.

#### Acceptance Criteria

1. WHEN validating LinkedIn photo URLs THEN the system SHALL identify known fallback image patterns including `9c8pery4andzj6ohjkjp54ma2`
2. WHEN a photo URL contains LinkedIn's fallback image identifier THEN the system SHALL classify it as invalid
3. WHEN a photo URL points to a valid LinkedIn profile image THEN the system SHALL classify it as valid and usable
4. WHEN photo validation fails due to network issues THEN the system SHALL treat the photo as potentially valid and include the candidate

### Requirement 4: Search Result Quality Assurance

**User Story:** As a user, I want consistent search result quality with professional photos, so that I can trust the visual representation of candidates.

#### Acceptance Criteria

1. WHEN returning search results THEN the system SHALL ensure that at least 80% of returned candidates have valid LinkedIn profile photos
2. WHEN the photo validation rate falls below 80% THEN the system SHALL log a warning for monitoring and optimization
3. WHEN displaying candidates THEN the system SHALL never show LinkedIn's generic fallback images to users
4. WHEN a candidate lacks a valid photo THEN the system SHALL either exclude them or show a clearly marked "no photo available" placeholder that doesn't mislead users