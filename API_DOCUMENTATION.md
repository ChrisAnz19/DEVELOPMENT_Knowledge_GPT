# Knowledge_GPT API Documentation

## 🚀 Base URL
```
https://knowledge-gpt-siuq.onrender.com
```

## 📋 API Endpoints

### 1. Health Check
**GET** `/`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### 2. Create Search
**POST** `/api/search`

Create a new search request with a natural language prompt.

**Request Body:**
```json
{
  "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
  "max_candidates": 5,
  "include_linkedin": true,
  "include_posts": false
}
```

**Response:**
```json
{
  "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
  "status": "processing",
  "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": null
}
```

### 3. Get Search Result
**GET** `/api/search/{request_id}`

Get the results of a specific search by request ID.

**Response:**
```json
{
  "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
  "status": "completed",
  "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
  "filters": {
    "title_keywords": ["software engineer", "senior engineer"],
    "skills": ["python", "react"],
    "location": "san francisco",
    "experience_years": 5
  },
  "candidates": [
    {
      "name": "John Doe",
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "email": "john.doe@techcorp.com",
      "accuracy": 92,
      "reasons": ["5+ years experience", "Python and React skills", "San Francisco location"],
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "profile_photo_url": "https://example.com/photo.jpg",
      "location": "San Francisco, CA",
      "linkedin_profile": {
        "summary": "Experienced software engineer...",
        "experience": [...],
        "education": [...]
      },
      "linkedin_posts": []
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z"
}
```

### 4. List All Searches
**GET** `/api/search`

Get a list of all searches with their status.

**Response:**
```json
[
  {
    "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
    "status": "completed",
    "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
    "created_at": "2024-01-15T10:30:00Z",
    "completed_at": "2024-01-15T10:32:15Z"
  }
]
```

### 5. Delete Search
**DELETE** `/api/search/{request_id}`

Delete a specific search and its results.

**Response:**
```json
{
  "message": "Search deleted successfully"
}
```

### 6. Get Search JSON
**GET** `/api/search/{request_id}/json`

Get the raw JSON data for a search (useful for debugging).

**Response:**
```json
{
  "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
  "status": "completed",
  "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
  "filters": {...},
  "candidates": [...],
  "behavioral_data": {...},
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z"
}
```

### 7. Database Statistics
**GET** `/api/database/stats`

Get database statistics including counts of searches, candidates, and exclusions.

**Response:**
```json
{
  "database_status": "connected",
  "total_searches": 25,
  "total_candidates": 150,
  "total_exclusions": 45
}
```

### 8. Get Exclusions
**GET** `/api/exclusions`

Get all currently excluded people (30-day exclusion system).

**Response:**
```json
{
  "exclusions": [
    {
      "email": "john.doe@techcorp.com",
      "name": "John Doe",
      "company": "Tech Corp",
      "excluded_at": "2024-01-15T10:30:00Z",
      "expires_at": "2024-02-14T10:30:00Z",
      "reason": "Previously processed"
    }
  ],
  "count": 45
}
```

### 9. Cleanup Exclusions
**POST** `/api/exclusions/cleanup`

Clean up expired exclusions (removes exclusions older than 30 days).

**Response:**
```json
{
  "message": "Cleaned up 12 expired exclusions",
  "cleaned_count": 12
}
```

## 🔄 Search Status Values

- `processing`: Search is currently being processed
- `completed`: Search completed successfully
- `failed`: Search failed with an error

## 📊 Data Models

### SearchRequest
```typescript
interface SearchRequest {
  prompt: string;
  max_candidates?: number; // Default: 2
  include_linkedin?: boolean; // Default: true
  include_posts?: boolean; // Default: true
}
```

### SearchResponse
```typescript
interface SearchResponse {
  request_id: string;
  status: string;
  prompt: string;
  filters?: object;
  candidates?: Candidate[];
  behavioral_data?: object;
  error?: string;
  created_at: string;
  completed_at?: string;
}
```

### Candidate
```typescript
interface Candidate {
  name: string;
  title: string;
  company: string;
  email: string;
  accuracy: number; // 0-100
  reasons: string[];
  linkedin_url?: string;
  profile_photo_url?: string;
  location?: string;
  linkedin_profile?: object;
  linkedin_posts?: object[];
}
```

## 🚀 Frontend Integration Examples

### React Hook Example
```typescript
import { useState, useEffect } from 'react';

interface UseKnowledgeGPT {
  createSearch: (prompt: string) => Promise<string>;
  getSearchResult: (requestId: string) => Promise<SearchResponse>;
  pollSearchResult: (requestId: string) => Promise<SearchResponse>;
}

export const useKnowledgeGPT = (): UseKnowledgeGPT => {
  const API_BASE = 'https://knowledge-gpt-siuq.onrender.com';

  const createSearch = async (prompt: string): Promise<string> => {
    const response = await fetch(`${API_BASE}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        max_candidates: 5,
        include_linkedin: true,
        include_posts: false
      })
    });
    
    const data = await response.json();
    return data.request_id;
  };

  const getSearchResult = async (requestId: string): Promise<SearchResponse> => {
    const response = await fetch(`${API_BASE}/api/search/${requestId}`);
    return response.json();
  };

  const pollSearchResult = async (requestId: string): Promise<SearchResponse> => {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const result = await getSearchResult(requestId);
          if (result.status === 'completed' || result.status === 'failed') {
            resolve(result);
          } else {
            setTimeout(poll, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          reject(error);
        }
      };
      poll();
    });
  };

  return { createSearch, getSearchResult, pollSearchResult };
};
```

### Usage Example
```typescript
const MyComponent = () => {
  const [searchId, setSearchId] = useState<string | null>(null);
  const [result, setResult] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const { createSearch, pollSearchResult } = useKnowledgeGPT();

  const handleSearch = async (prompt: string) => {
    setLoading(true);
    try {
      const id = await createSearch(prompt);
      setSearchId(id);
      
      const searchResult = await pollSearchResult(id);
      setResult(searchResult);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button onClick={() => handleSearch("Find Python developers")}>
        Search
      </button>
      {loading && <p>Searching...</p>}
      {result && (
        <div>
          <h3>Results:</h3>
          {result.candidates?.map(candidate => (
            <div key={candidate.email}>
              <h4>{candidate.name}</h4>
              <p>{candidate.title} at {candidate.company}</p>
              <p>Accuracy: {candidate.accuracy}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

## 🔧 Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

Error responses include an `error` field with details:
```json
{
  "error": "Search not found"
}
```

## 📝 Notes for Frontend Development

1. **Polling**: Use the polling pattern for search results as they are processed asynchronously
2. **Rate Limiting**: Be mindful of API rate limits
3. **CORS**: The API supports CORS for frontend integration
4. **Data Persistence**: All data is stored in Supabase and persists between deployments
5. **Exclusions**: The system automatically excludes people processed within 30 days

## 🎯 Ready for Frontend Development

The API is now fully deployed and ready for frontend integration. All endpoints are working and the database is properly connected to Supabase. You can start building your frontend application using the examples and documentation above. 