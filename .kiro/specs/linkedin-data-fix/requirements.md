# Requirements Document

## Introduction

This feature addresses the issue where candidate LinkedIn photo, company name, and LinkedIn URL are not being returned to the client in API responses. The data appears to be stored in the database but is not reaching the frontend application.

## Requirements

### Requirement 1

**User Story:** As a frontend developer, I want to receive candidate LinkedIn photo URLs in API responses, so that I can display profile pictures in the user interface.

#### Acceptance Criteria

1. WHEN a search request is completed THEN the API response SHALL include profile_photo_url for each candidate
2. WHEN candidate data contains a LinkedIn profile photo THEN it SHALL be prioritized over other photo sources
3. WHEN multiple photo URL fields exist THEN the system SHALL select the best available photo URL
4. WHEN no photo URL is available THEN the field SHALL be null rather than missing

### Requirement 2

**User Story:** As a frontend developer, I want to receive candidate company names in API responses, so that I can display employment information in the user interface.

#### Acceptance Criteria

1. WHEN a search request is completed THEN the API response SHALL include company name for each candidate
2. WHEN candidate data contains organization information THEN it SHALL be properly mapped to the company field
3. WHEN company data exists in multiple formats THEN the system SHALL normalize it to a consistent format
4. WHEN no company information is available THEN the field SHALL be null rather than missing

### Requirement 3

**User Story:** As a frontend developer, I want to receive candidate LinkedIn URLs in API responses, so that I can provide links to their LinkedIn profiles.

#### Acceptance Criteria

1. WHEN a search request is completed THEN the API response SHALL include linkedin_url for each candidate
2. WHEN LinkedIn URLs are stored in the database THEN they SHALL be included in the API response
3. WHEN LinkedIn URLs need formatting THEN they SHALL be properly formatted with https protocol
4. WHEN no LinkedIn URL is available THEN the field SHALL be null rather than missing

### Requirement 4

**User Story:** As a system administrator, I want to ensure data consistency between database storage and API responses, so that all stored candidate information is accessible to clients.

#### Acceptance Criteria

1. WHEN candidate data is stored in the database THEN all fields SHALL be retrievable via API
2. WHEN API responses are generated THEN they SHALL include all available candidate fields
3. WHEN field mapping occurs THEN no data SHALL be lost in the transformation
4. WHEN debugging is needed THEN logging SHALL clearly show which fields are being returned