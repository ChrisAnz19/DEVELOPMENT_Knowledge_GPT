# Requirements Document

## Introduction

The current system has a bug where LinkedIn profile photos sometimes fail to load and fall back to default LinkedIn placeholder images (like `https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2`). Instead of showing these generic placeholder images or skipping candidates entirely, the system should display the person's initials in a circular avatar when their LinkedIn photo is unavailable or invalid. This provides a more professional and personalized fallback experience while maintaining visual consistency in search results.

## Requirements

### Requirement 1: Initials Avatar Generation

**User Story:** As a user viewing search results, I want to see personalized initials avatars when LinkedIn photos are unavailable, so that I can still visually distinguish between different candidates.

#### Acceptance Criteria

1. WHEN a candidate's LinkedIn photo URL is detected as a fallback image THEN the system SHALL generate an initials avatar using the person's first and last name
2. WHEN a candidate has no photo URL available THEN the system SHALL generate an initials avatar as the fallback
3. WHEN generating initials THEN the system SHALL use the first letter of the first name and first letter of the last name in uppercase
4. WHEN a candidate has only one name THEN the system SHALL use the first two letters of that name for the initials
5. WHEN a candidate has no name available THEN the system SHALL use "?" as the fallback character

### Requirement 2: Avatar Visual Design

**User Story:** As a user, I want initials avatars to be visually appealing and consistent, so that they integrate seamlessly with the existing UI design.

#### Acceptance Criteria

1. WHEN displaying an initials avatar THEN the system SHALL render it as a circular background with centered text
2. WHEN generating avatar colors THEN the system SHALL use a deterministic color scheme based on the person's name to ensure consistency
3. WHEN displaying initials text THEN the system SHALL use white text on a colored background for optimal contrast
4. WHEN sizing the avatar THEN the system SHALL match the dimensions of regular LinkedIn profile photos (typically 200x200px or equivalent)
5. WHEN the avatar is displayed THEN it SHALL have the same border radius and styling as regular profile photos

### Requirement 3: Backend API Enhancement

**User Story:** As a developer, I want the API to provide initials avatar data when photos are unavailable, so that the frontend can render appropriate fallbacks.

#### Acceptance Criteria

1. WHEN the API detects an invalid LinkedIn photo THEN it SHALL include initials avatar data in the response
2. WHEN returning candidate data THEN the system SHALL include an `avatar` object with `type`, `initials`, and `background_color` fields
3. WHEN a valid LinkedIn photo is available THEN the `avatar.type` SHALL be "photo" and include the photo URL
4. WHEN using initials fallback THEN the `avatar.type` SHALL be "initials" and include the generated initials and color
5. WHEN avatar generation fails THEN the system SHALL provide a default avatar configuration

### Requirement 4: Frontend Display Logic

**User Story:** As a user, I want the frontend to seamlessly display either LinkedIn photos or initials avatars, so that all candidates have consistent visual representation.

#### Acceptance Criteria

1. WHEN receiving candidate data with avatar type "photo" THEN the frontend SHALL display the LinkedIn profile image
2. WHEN receiving candidate data with avatar type "initials" THEN the frontend SHALL render a circular initials avatar
3. WHEN a LinkedIn photo fails to load in the browser THEN the frontend SHALL automatically fall back to the initials avatar
4. WHEN displaying initials avatars THEN the frontend SHALL apply the provided background color and center the initials text
5. WHEN hovering over an initials avatar THEN the system MAY show a tooltip indicating "Photo unavailable"

### Requirement 5: Backward Compatibility

**User Story:** As a system administrator, I want the new initials feature to work with existing API clients, so that current integrations continue to function without modification.

#### Acceptance Criteria

1. WHEN existing API clients request candidate data THEN they SHALL continue to receive the existing photo_url field for backward compatibility
2. WHEN the photo_url contains a fallback image THEN existing clients SHALL receive null or empty string instead
3. WHEN new avatar data is added THEN it SHALL be in addition to existing fields, not replacing them
4. WHEN API responses are returned THEN they SHALL maintain the same overall structure and required fields
5. WHEN clients don't support the new avatar format THEN they SHALL gracefully handle missing or null photo URLs