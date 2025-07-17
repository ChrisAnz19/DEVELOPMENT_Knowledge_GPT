# Enhanced Assessment System Documentation

## Overview

The Enhanced Assessment System is an improved version of the candidate evaluation functionality that provides more nuanced, realistic, and effective behavioral assessments. This system uses GPT-4-Turbo to generate industry-specific behavioral patterns with time-series data, avoiding unrealistic scenarios and generic phrases.

## Key Features

1. **Industry-Specific Behavioral Patterns**
   - Tailored assessments based on candidate's industry and role
   - Realistic online behaviors specific to different professions
   - Avoids generic phrases and unrealistic scenarios

2. **Time-Series Behavioral Data**
   - Includes patterns showing progression over time
   - Uses realistic timeframes (days, weeks, months)
   - Shows intent through sequential behaviors

3. **GPT-4-Turbo Integration**
   - Upgraded from GPT-3.5-Turbo for better reasoning
   - More nuanced and sophisticated assessments
   - Improved response quality

4. **Enhanced Prompt Engineering**
   - Clear instructions about avoiding unrealistic scenarios
   - Examples of good and bad responses
   - Industry-specific guidance

5. **Robust Fallback Mechanism**
   - Industry-specific fallback patterns when API calls fail
   - Maintains quality even in offline scenarios
   - Consistent response format

## Usage

```python
from assess_and_return import select_top_candidates

# Basic usage
results = select_top_candidates("Looking for a senior developer with cloud experience", people_data)

# With industry context
results = select_top_candidates(
    "Looking for a marketing manager with experience in content strategy",
    people_data,
    industry_context="Marketing"
)

# Print results
for candidate in results:
    print(f"Name: {candidate['name']}")
    print(f"Title: {candidate['title']}")
    print(f"Company: {candidate['company']}")
    print(f"Match Accuracy: {candidate['accuracy']}%")
    print("Behavioral Reasons:")
    for reason in candidate['reasons']:
        print(f"- {reason}")
    print()
```

## Response Format

The system returns a list of dictionaries, each representing a candidate with the following fields:

```json
[
  {
    "name": "Jane Smith",
    "title": "Senior Software Engineer",
    "company": "Tech Solutions Inc.",
    "email": "jane.smith@example.com",
    "accuracy": 90,
    "reasons": [
      "Visited GitHub repositories for React state management libraries 5 times in the past week",
      "Researched cloud architecture optimization techniques across multiple technical blogs, spending 30+ minutes on each",
      "Compared Kubernetes with Docker Swarm on review sites, then deeply explored Kubernetes documentation"
    ]
  },
  {
    "name": "John Doe",
    "title": "Software Developer",
    "company": "Code Experts LLC",
    "email": "john.doe@example.com",
    "accuracy": 75,
    "reasons": [
      "Cloned 3 repositories related to cloud infrastructure in the past two weeks",
      "Spent increasing amounts of time reviewing AWS documentation pages",
      "Participated in technical forums discussing containerization technologies"
    ]
  }
]
```

## Industry-Specific Patterns

The system automatically detects the candidate's industry and role level based on their title and company, then generates appropriate behavioral patterns:

- **Technology**: GitHub activity, Stack Overflow usage, documentation research
- **Marketing**: Analytics tools, content strategies, campaign analysis
- **Sales**: CRM usage, prospect research, sales methodology exploration
- **Finance**: Market data analysis, financial modeling, regulatory research
- **General Business**: Industry trends, professional development, tool evaluation

## Role Levels

The system also tailors patterns based on seniority:

- **Junior**: Learning activities, basic tool usage, skill development
- **Mid-level**: Comparative analysis, implementation strategies, deeper research
- **Senior**: Advanced techniques, performance optimization, architectural considerations
- **Executive**: Strategic analysis, competitive landscape, organizational planning

## Testing

A comprehensive test suite is available in `test_enhanced_assessment.py` that validates:

- Prompt building functionality
- Response validation
- Industry detection
- Pattern generation
- Fallback assessment

Run the tests with:

```bash
python -m unittest test_enhanced_assessment.py
```

## Implementation Details

The enhanced assessment system consists of several key components:

1. `select_top_candidates`: Main function that processes candidate data and returns assessments
2. `build_assessment_prompt`: Creates optimized prompts for the GPT-4-Turbo model
3. `_validate_assessment_response`: Ensures response quality and completeness
4. `_get_industry_specific_patterns`: Generates industry-specific behavioral patterns
5. `_fallback_assessment`: Provides reliable results when API calls fail

## Performance Considerations

- The system limits candidate data to 3 people to stay within token limits
- Only essential fields are included in API calls to optimize token usage
- Response validation ensures quality before returning results
- Fallback mechanism provides consistent results even when API calls fail