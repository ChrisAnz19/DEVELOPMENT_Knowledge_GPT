# Logical Assessment Feature Documentation

## Overview

The Logical Assessment Feature enhances the system by ensuring that when a user makes a query, the system performs a logical assessment of the results returned by Apollo to verify they "make sense" in relation to the user's request. This feature leverages the existing AI prompting system to add a validation step that ensures logical coherence between the user's query and the returned results.

## Function Documentation

### `assess_logical_coherence`

```python
def assess_logical_coherence(user_query: str, apollo_results: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]], str]:
    """
    Assesses the logical coherence between the user's query and the Apollo API results.
    
    Args:
        user_query (str): The original user query string.
        apollo_results (List[Dict[str, Any]]): The results returned by the Apollo API.
        
    Returns:
        Tuple[bool, List[Dict[str, Any]], str]: A tuple containing:
            - bool: Whether the results are logically coherent with the query.
            - List[Dict[str, Any]]: Filtered list of logically coherent results (or all results if none are coherent).
            - str: Explanation of the assessment.
    
    Raises:
        Exception: If there's an error during the assessment process, the function will catch it,
                  log the error, and return all results to ensure the system continues to function.
    """
```

#### Parameters

- **user_query**: The original query string submitted by the user. This should be the raw, unprocessed query that represents the user's intent.
- **apollo_results**: A list of dictionaries containing information about people returned by the Apollo API. Each dictionary should contain at least the following fields:
  - `name`: The person's name
  - `title`: The person's job title
  - `organization_name` or `company`: The person's company
  - `linkedin_url`: The person's LinkedIn URL (optional)
  - `location`: The person's location (optional)
  - `seniority`: The person's seniority level (optional)

#### Return Value

The function returns a tuple containing three elements:

1. **is_coherent** (bool): A boolean indicating whether the results are logically coherent with the user's query.
2. **coherent_results** (List[Dict[str, Any]]): A filtered list of results that are logically coherent with the user's query. If no coherent results are found, this will be an empty list.
3. **explanation** (str): A string explaining the assessment, including why certain results were deemed coherent or incoherent.

## How the System Determines if Results "Make Sense"

The logical assessment feature uses OpenAI's GPT model to evaluate whether the Apollo API results logically match the user's query intent. Here's how the system determines if results "make sense":

### 1. Preprocessing

- The system limits the assessment to the top 5 results to reduce token usage.
- For each result, the system extracts key information such as name, title, company, LinkedIn URL, location, and seniority.

### 2. AI Prompt Construction

The system constructs a prompt for the AI model that includes:

- A system message that defines the task as evaluating whether search results logically match a user's query intent.
- The user's original query.
- The Apollo API results in a structured format.

### 3. Assessment Criteria

The AI model assesses each candidate based on the following criteria:

- **Profile Match**: Does the candidate's profile logically match what the user is looking for?
- **Inconsistencies**: Are there any obvious mismatches or inconsistencies?
- **Human Relevance**: Would a human reasonably consider this candidate relevant to the query?

### 4. Response Format

The AI model returns a JSON object with the following structure:

```json
{
    "overall_coherent": true/false,
    "coherent_results": [indices of coherent results],
    "explanation": "Brief explanation of the assessment"
}
```

### 5. Result Processing

- The system extracts the assessment from the AI model's response.
- It identifies which results are coherent based on the indices provided.
- If no coherent results are found, the system falls back to using all results to ensure the system continues to function.

### Examples

#### Example 1: Coherent Results

**User Query**: "Find me senior software engineers at Google with experience in AI"

**Apollo Results**:
```json
[
  {
    "name": "John Doe",
    "title": "Senior Software Engineer",
    "organization_name": "Google",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "location": "Mountain View, CA",
    "seniority": "Director"
  },
  {
    "name": "Jane Smith",
    "title": "Marketing Manager",
    "organization_name": "Facebook",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "location": "San Francisco, CA",
    "seniority": "Manager"
  }
]
```

**Assessment**:
```json
{
  "overall_coherent": true,
  "coherent_results": [0],
  "explanation": "John Doe is a Senior Software Engineer at Google, which directly matches the query. Jane Smith is a Marketing Manager at Facebook, which does not match the query for senior software engineers at Google."
}
```

#### Example 2: No Coherent Results

**User Query**: "Find me senior software engineers at Google with experience in AI"

**Apollo Results**:
```json
[
  {
    "name": "Jane Smith",
    "title": "Marketing Manager",
    "organization_name": "Facebook",
    "linkedin_url": "https://linkedin.com/in/janesmith",
    "location": "San Francisco, CA",
    "seniority": "Manager"
  },
  {
    "name": "Bob Johnson",
    "title": "Product Manager",
    "organization_name": "Microsoft",
    "linkedin_url": "https://linkedin.com/in/bobjohnson",
    "location": "Seattle, WA",
    "seniority": "Senior"
  }
]
```

**Assessment**:
```json
{
  "overall_coherent": false,
  "coherent_results": [],
  "explanation": "None of the results match the query for senior software engineers at Google with AI experience. Jane Smith is a Marketing Manager at Facebook, and Bob Johnson is a Product Manager at Microsoft."
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Assessment Fails with API Error

**Issue**: The OpenAI API call fails, resulting in no assessment.

**Solution**:
- Check that the OpenAI API key is valid and has sufficient quota.
- Verify that the network connection to the OpenAI API is working.
- The system will automatically fall back to using all results if the assessment fails.

#### 2. No Coherent Results Found

**Issue**: The assessment determines that none of the Apollo results are logically coherent with the user's query.

**Solution**:
- The system will automatically fall back to using all results to ensure the system continues to function.
- Consider refining the user's query or the Apollo API filters to get more relevant results.

#### 3. JSON Parsing Error

**Issue**: The system fails to parse the JSON response from the AI model.

**Solution**:
- The system includes robust error handling that will catch JSON parsing errors and fall back to using all results.
- Check the logs for the specific error message to diagnose the issue.

#### 4. High Token Usage

**Issue**: The assessment is using too many tokens, resulting in high API costs.

**Solution**:
- The system limits the assessment to the top 5 results to reduce token usage.
- Consider further limiting the number of results or the amount of information sent to the AI model.

### Logging and Debugging

The logical assessment feature includes comprehensive logging to help with troubleshooting:

- **Info Level**: General information about the assessment process, including the number of results being assessed and the assessment outcome.
- **Warning Level**: Warnings about potential issues, such as no coherent results being found.
- **Error Level**: Errors that occur during the assessment process, including API errors and JSON parsing errors.

Example log messages:

```
INFO: [request_id] Performing logical assessment of results...
INFO: [request_id] Logical assessment complete: True
INFO: [request_id] Assessment explanation: John Doe is a Senior Software Engineer at Google, which directly matches the query.
INFO: [request_id] Using 1 logically coherent results
WARNING: [request_id] No logically coherent results found, using all results
ERROR: [request_id] Logical assessment failed: API error
```

## Integration with the Pipeline

The logical assessment feature is integrated into the existing pipeline in the `process_search` function in `api/main.py`. The integration follows these steps:

1. The system parses the user's query into Apollo API filters.
2. The system searches the Apollo API for people matching the filters.
3. The system performs a logical assessment of the Apollo results against the original query.
4. If coherent results are found, the system uses only those results for the next steps.
5. If no coherent results are found or the assessment fails, the system falls back to using all results.

This integration ensures that the logical assessment feature enhances the system without disrupting its core functionality.