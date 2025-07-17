# Requirements Document

## Introduction

The Enhanced Assessment feature aims to improve the existing assess_and_return functionality by making it more nuanced, realistic, and effective. The current implementation has several limitations: it uses generic behavioral patterns, relies on unrealistic scenarios (like reading case studies about job postings), and lacks time-series behavioral data. Additionally, the system currently uses GPT-3.5-Turbo, which should be upgraded to GPT-4-Turbo for better reasoning capabilities and more nuanced assessments.

## Requirements

### Requirement 1

**User Story:** As a user, I want more realistic and nuanced behavioral assessments of candidates, so that I can make better-informed decisions about potential matches.

#### Acceptance Criteria

1. WHEN the system generates behavioral reasons THEN it SHALL avoid unrealistic scenarios like "reading case studies about job postings" or "attending webinars" for all professions
2. WHEN the system generates behavioral reasons THEN it SHALL tailor them to be industry and role-specific
3. WHEN the system generates behavioral reasons THEN it SHALL include realistic online behaviors that professionals in that field would actually engage in
4. WHEN the system generates behavioral reasons THEN it SHALL avoid generic phrases like "selected based on title and company fit"

### Requirement 2

**User Story:** As a user, I want behavioral assessments to include time-series data, so that I can understand candidate engagement patterns over time.

#### Acceptance Criteria

1. WHEN the system generates behavioral reasons THEN it SHALL include time-series patterns (e.g., "visited X three times in the past month")
2. WHEN the system generates time-series data THEN it SHALL use realistic timeframes (days, weeks, months) appropriate to the behavior
3. WHEN the system generates time-series data THEN it SHALL show progression or patterns that indicate intent (e.g., "researched X, then compared with Y, then downloaded Z")
4. WHEN the system generates time-series data THEN it SHALL vary the patterns between candidates to avoid repetitive assessments

### Requirement 3

**User Story:** As a user, I want the assessment system to use GPT-4-Turbo instead of GPT-3.5-Turbo, so that I can get more accurate and sophisticated candidate evaluations.

#### Acceptance Criteria

1. WHEN the system makes OpenAI API calls for assessments THEN it SHALL use the GPT-4-Turbo model
2. WHEN the system uses GPT-4-Turbo THEN it SHALL maintain or improve response time compared to the previous implementation
3. WHEN the system uses GPT-4-Turbo THEN it SHALL handle the same or greater number of candidates within token limits
4. WHEN the system uses GPT-4-Turbo THEN it SHALL produce more nuanced and accurate assessments

### Requirement 4

**User Story:** As a user, I want improved prompt engineering in the assessment system, so that the AI generates more relevant and insightful candidate evaluations.

#### Acceptance Criteria

1. WHEN the system constructs prompts THEN it SHALL include clear instructions about avoiding unrealistic scenarios
2. WHEN the system constructs prompts THEN it SHALL guide the AI to generate industry-specific behavioral patterns
3. WHEN the system constructs prompts THEN it SHALL include examples of good and bad responses to guide the AI
4. WHEN the system constructs prompts THEN it SHALL instruct the AI to consider the candidate's role, industry, and seniority when generating behavioral reasons