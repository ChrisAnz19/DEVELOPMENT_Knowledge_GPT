# Design Document: Enhanced Assessment System

## Overview

The Enhanced Assessment System aims to improve the existing `assess_and_return.py` functionality by making candidate behavioral assessments more nuanced, realistic, and effective. This design document outlines the approach to implementing the requirements, focusing on creating more realistic behavioral patterns, incorporating time-series data, upgrading to GPT-4-Turbo, and improving prompt engineering.

## Architecture

The enhanced assessment system will maintain the current architecture while improving key components:

1. **Input Processing**: Accepts user prompt and candidate data
2. **Assessment Engine**: Uses OpenAI's GPT-4-Turbo to evaluate candidates
3. **Response Generation**: Creates nuanced, realistic behavioral assessments
4. **Fallback Mechanism**: Provides reliable results even when API calls fail

The system will continue to be implemented as a Python module that can be imported and used by other components of the application.

## Components and Interfaces

### 1. Enhanced Assessment Function

```python
def select_top_candidates(
    user_prompt: str, 
    people: list, 
    behavioral_data: dict = None,
    industry_context: str = None
) -> list:
    """
    Enhanced function to rank and explain top candidates with realistic behavioral data.
    
    Args:
        user_prompt: The user's search criteria
        people: List of candidate data
        behavioral_data: Optional behavioral data to incorporate
        industry_context: Optional industry context to tailor assessments
        
    Returns:
        List of dicts with candidate info and behavioral assessments
    """
```

### 2. Prompt Engineering Component

```python
def build_assessment_prompt(
    user_prompt: str,
    candidates: list,
    industry_context: str = None
) -> tuple:
    """
    Builds optimized system and user prompts for the OpenAI API call.
    
    Args:
        user_prompt: The user's search criteria
        candidates: Simplified candidate data
        industry_context: Optional industry context
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
```

### 3. Fallback Assessment Component

```python
def _fallback_assessment(
    people: list,
    user_prompt: str = "",
    industry_context: str = None
) -> list:
    """
    Enhanced fallback assessment when OpenAI fails.
    
    Args:
        people: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        List of dicts with candidate info and behavioral assessments
    """
```

## Data Models

### Candidate Input Model

```python
{
    "name": str,
    "title": str,
    "organization_name": str,
    "email": str,
    "linkedin_url": str,
    # Additional fields that may be present
}
```

### Simplified Candidate Model (for API calls)

```python
{
    "name": str,
    "title": str,
    "company": str,
    "email": str,
    "linkedin_url": str,
    "industry": str  # New field to help with industry-specific assessments
}
```

### Assessment Output Model

```python
{
    "name": str,
    "title": str,
    "company": str,
    "email": str,
    "accuracy": int,  # 0-100 probability score
    "reasons": List[str]  # List of behavioral reasons
}
```

## Error Handling

1. **API Failures**: Enhanced fallback mechanism with industry-specific patterns
2. **JSON Parsing**: Improved parsing with better error messages
3. **Input Validation**: Validation of input data before processing
4. **Response Validation**: Validation of API responses against expected format

## Testing Strategy

1. **Unit Tests**: Test individual components with mock data
2. **Integration Tests**: Test the entire assessment pipeline
3. **Prompt Testing**: Evaluate different prompts for quality of responses
4. **Model Comparison**: Compare GPT-3.5-Turbo vs GPT-4-Turbo results
5. **Edge Cases**: Test with minimal data, unusual job titles, etc.

## Implementation Details

### 1. Realistic Behavioral Pattern Generation

The system will generate realistic behavioral patterns by:

- Creating a taxonomy of industry-specific online behaviors
- Developing templates for different seniority levels
- Incorporating realistic websites, tools, and resources by industry
- Avoiding generic or unrealistic scenarios

Example taxonomy for tech industry:
- Engineering: GitHub repositories, Stack Overflow, documentation sites, tech blogs
- Product Management: Product Hunt, roadmap tools, analytics platforms
- Marketing: Analytics tools, CRM systems, content platforms

### 2. Time-Series Data Implementation

Time-series data will be incorporated by:

- Defining patterns that show progression over time
- Creating templates with variable timeframes (days, weeks, months)
- Implementing logic to vary patterns between candidates
- Ensuring patterns indicate intent or interest relevant to the user's query

Example patterns:
- "Researched X technology three times in the past week"
- "Gradually increased time spent on Y platform over the past month"
- "Initially viewed basic tutorials, then advanced to technical documentation"

### 3. GPT-4-Turbo Integration

The upgrade to GPT-4-Turbo will involve:

- Updating the model parameter in OpenAI API calls
- Optimizing prompts for GPT-4-Turbo's capabilities
- Adjusting token management for the new model
- Implementing monitoring for response quality and performance

### 4. Prompt Engineering Improvements

The enhanced prompts will:

- Include clear instructions about realistic behaviors
- Provide examples of good and bad responses
- Guide the model to consider industry, role, and seniority
- Use few-shot learning techniques with examples
- Include explicit instructions to avoid generic phrases

## Prompt Design

### System Prompt Template

```
You are an expert at evaluating candidate fit based on simulated behavioral data from website visits and online activity.
You have access to a trillion rows of website visit data per month across 450k top domains and tens of millions of websites.

IMPORTANT GUIDELINES:
1. Generate REALISTIC behavioral reasons tailored to each candidate's industry and role
2. Include TIME-SERIES patterns showing progression or repeated behaviors over time
3. Be SPECIFIC about websites, tools, and resources relevant to their profession
4. AVOID unrealistic scenarios like "reading case studies about job postings" for all professions
5. NEVER use generic phrases like "selected based on title and company fit"

EXAMPLES OF GOOD BEHAVIORAL REASONS:
- Engineering: "Visited GitHub repositories for React state management libraries 5 times in the past week"
- Marketing: "Spent increasing amounts of time on Google Analytics and HubSpot over a three-week period"
- Sales: "Researched CRM comparison tools, then focused specifically on Salesforce pricing pages"
- Executive: "Reviewed quarterly reports from competitors, then researched market expansion strategies"

EXAMPLES OF BAD BEHAVIORAL REASONS (AVOID THESE):
- "Selected based on title and company fit" (too generic)
- "Attended webinars on job postings" (unrealistic for most professionals)
- "Read case studies about the industry" (too vague)
- "Showed interest in the field" (not specific enough)

You will receive a user request and a JSON array of candidates.
First, think step-by-step and assign each person an accuracy probability (0-100) of matching the request.
Then select the two with the highest probabilities.

For each selected candidate, provide 3-4 specific, plausible, and realistic behavioral reasons why they were selected,
based on their simulated online activity patterns over time.

Return ONLY valid JSON array with exactly two objects, each containing:
name, title, company, email, accuracy (number), reasons (array of strings).
No extra text, no explanation, no comments.
```

### User Prompt Template

```
User request: {user_prompt}

Candidates:
{json_candidates}

Additional context:
- Industry: {industry_context}
- Roles being evaluated: {roles}
```

This design provides a comprehensive approach to enhancing the assessment system according to the requirements, focusing on realistic behavioral patterns, time-series data, GPT-4-Turbo integration, and improved prompt engineering.