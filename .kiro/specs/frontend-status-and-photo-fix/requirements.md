# Frontend Status and Photo Fix Requirements

## Introduction

Two critical issues need simple solutions: the frontend continues showing "in progress" even when backend processing completes, and LinkedIn photos are inconsistent (sometimes showing photos, sometimes empty icons, appearing random). Focus on straightforward fixes.

## Requirements

### Requirement 1: Fix Frontend Processing Status Display

**User Story:** As a user, I want the frontend to show when processing is complete, so that I know results are ready and don't wait unnecessarily.

#### Acceptance Criteria

1. WHEN backend processing completes THEN frontend SHALL immediately show completion status
2. WHEN results are available THEN frontend SHALL stop showing "in progress" indicators
3. WHEN processing finishes THEN frontend SHALL display the actual results
4. WHEN there are errors THEN frontend SHALL show error states instead of hanging on "in progress"

### Requirement 2: Fix LinkedIn Photo Consistency

**User Story:** As a user, I want LinkedIn photos to display consistently, so that I can reliably see candidate profile pictures.

#### Acceptance Criteria

1. WHEN a LinkedIn photo URL is available THEN it SHALL display consistently
2. WHEN a LinkedIn photo fails to load THEN it SHALL fall back to initials avatar
3. WHEN no LinkedIn photo exists THEN it SHALL show initials avatar immediately
4. WHEN photo loading is inconsistent THEN the system SHALL use a reliable fallback mechanism

### Requirement 3: Implement Simple Status Communication

**User Story:** As a developer, I want a simple mechanism to communicate completion status, so that frontend integration is straightforward.

#### Acceptance Criteria

1. WHEN processing starts THEN status SHALL be clearly marked as "processing"
2. WHEN processing completes THEN status SHALL be clearly marked as "completed"
3. WHEN processing fails THEN status SHALL be clearly marked as "failed"
4. WHEN status changes THEN it SHALL be immediately available to frontend

### Requirement 4: Implement Simple Photo Loading Logic

**User Story:** As a developer, I want photo loading to be predictable and reliable, so that users see consistent results.

#### Acceptance Criteria

1. WHEN checking for LinkedIn photos THEN the system SHALL use a simple validation approach
2. WHEN LinkedIn photos are unavailable THEN the system SHALL immediately use initials
3. WHEN photo URLs are invalid THEN the system SHALL detect this quickly and use fallback
4. WHEN photo loading fails THEN the system SHALL not retry indefinitely