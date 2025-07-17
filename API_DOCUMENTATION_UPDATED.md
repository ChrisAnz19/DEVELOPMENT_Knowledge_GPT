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
    "person_filters": {
      "person_titles": ["Software Engineer"],
      "include_similar_titles": true,
      "person_seniorities": ["director", "vp"]
    },
    "organization_filters": {
      "q_organization_keyword_tags": ["Technology"]
    },
    "reasoning": "Filtered for Software Engineers with director or VP level seniority in Technology companies."
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
      }
    }
  ],
  "behavioral_data": {
    "behavioral_insights": {
      "market_dynamics": "The market for software engineers with Python and React skills is highly competitive, with demand outpacing supply in tech hubs like San Francisco.",
      "engagement_patterns": "Senior software engineers tend to engage with technical content, open-source projects, and professional development resources.",
      "decision_making_behaviors": "These professionals often have significant influence in technology decisions within their organizations.",
      "technology_adoption_trends": "They are typically early adopters of new programming languages, frameworks, and development tools."
    },
    "supporting_data_points": {
      "technology_interests": ["Python", "React", "Cloud Computing", "DevOps"],
      "average_engagement_level": "Senior software engineers show high engagement with technical documentation and code repositories.",
      "decision-making_authority": "They often participate in or lead technology selection processes within their teams."
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z"
}
```

### 4. List All Searches
**GET** `/api/search`

Get a list of all searches with their status.

**Response:**
```json
{
  "searches": [
    {
      "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
      "status": "completed",
      "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
      "created_at": "2024-01-15T10:30:00Z",
      "completed_at": "2024-01-15T10:32:15Z"
    }
  ]
}
```

### 5. Delete Search
**DELETE** `/api/search/{request_id}`

Delete a specific search and its results.

**Response:**
```json
{
  "message": "Search request deleted from database"
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
  "behavioral_data": {
    "behavioral_insights": {
      "market_dynamics": "The market for software engineers with Python and React skills is highly competitive, with demand outpacing supply in tech hubs like San Francisco.",
      "engagement_patterns": "Senior software engineers tend to engage with technical content, open-source projects, and professional development resources.",
      "decision_making_behaviors": "These professionals often have significant influence in technology decisions within their organizations.",
      "technology_adoption_trends": "They are typically early adopters of new programming languages, frameworks, and development tools."
    },
    "supporting_data_points": {
      "technology_interests": ["Python", "React", "Cloud Computing", "DevOps"],
      "average_engagement_level": "Senior software engineers show high engagement with technical documentation and code repositories.",
      "decision-making_authority": "They often participate in or lead technology selection processes within their teams."
    }
  },
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
  "total_candidates": 150
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

## 🔄 Search Status Values

- `processing`: Search is currently being processed
- `completed`: Search completed successfully
- `failed`: Search failed with an error

## 🧠 Behavioral Data

The API includes behavioral data that provides insights into prospect behavior and psychology. These insights are automatically generated and included in the `behavioral_data` section of search responses.

### Behavioral Data Structure

The behavioral data is structured into two main sections:

1. **Behavioral Insights**: Descriptive insights about the prospect's behavior, market dynamics, and decision-making patterns.
2. **Supporting Data Points**: Specific data points that support the behavioral insights.

**Structure:**
```typescript
interface BehavioralData {
  behavioral_insights: {
    market_dynamics?: string;
    engagement_patterns?: string;
    decision_making_behaviors?: string;
    technology_adoption_trends?: string;
    [key: string]: string;
  };
  supporting_data_points: {
    [key: string]: string | string[];
  };
}
```

### Behavioral Insights

The `behavioral_insights` section typically includes the following types of insights:

1. **Market Dynamics**: Information about the market conditions relevant to the prospect's role and industry.
2. **Engagement Patterns**: How the prospect typically engages with content and information.
3. **Decision-Making Behaviors**: How the prospect makes decisions and their role in the decision-making process.
4. **Technology Adoption Trends**: The prospect's approach to adopting new technologies.

**Example:**
```json
"behavioral_insights": {
  "market_dynamics": "In the fintech industry, competition is fierce, and staying ahead requires a deep understanding of customer needs, regulatory changes, and emerging technologies.",
  "engagement_patterns": "Senior Product Managers in fintech tend to engage with content related to industry trends, product development methodologies, and market disruptions.",
  "decision_making_behaviors": "Senior Product Managers at the VP and Director level are key decision-makers in their organizations, often leading cross-functional teams and driving strategic product initiatives.",
  "technology_adoption_trends": "These individuals are likely early adopters of fintech solutions and tools, constantly seeking innovative technologies to enhance their product offerings."
}
```

### Supporting Data Points

The `supporting_data_points` section provides specific data points that support the behavioral insights. These can vary based on the prospect's role and industry, but often include:

1. **Technology Interests**: Specific technologies or topics the prospect is interested in.
2. **Engagement Levels**: Information about how the prospect engages with content.
3. **Decision-Making Authority**: The prospect's role in decision-making processes.
4. **Industry-Specific Data**: Data points relevant to the prospect's industry.

**Example:**
```json
"supporting_data_points": {
  "technology_interests": ["Python", "React", "Cloud Computing", "DevOps"],
  "average_engagement_level": "Senior software engineers show high engagement with technical documentation and code repositories.",
  "decision-making_authority": "They often participate in or lead technology selection processes within their teams."
}
```

### Complete Behavioral Data Example

```json
"behavioral_data": {
  "behavioral_insights": {
    "market_dynamics": "The market for CTOs with AI and cloud computing experience is rapidly evolving, with increasing competition among tech providers to offer scalable, secure, and customizable solutions.",
    "engagement_patterns": "CTOs with experience in AI and cloud computing are likely to engage with content related to cutting-edge technologies, machine learning, data analytics, cloud services, and digital transformation.",
    "decision_making_behaviors": "CTOs in this category are likely to make strategic decisions around implementing AI and cloud solutions, evaluating vendors, and overseeing technology infrastructure to align with business objectives.",
    "technology_adoption_trends": "These CTOs are likely early adopters of AI and cloud computing technologies, constantly seeking innovative solutions to drive business growth and efficiency."
  },
  "supporting_data_points": {
    "industry_reports": [
      "Gartner's latest report on AI adoption in enterprise",
      "Forrester's analysis on cloud computing trends in 2021",
      "IDC's forecast on the growth of AI market in the next 5 years"
    ],
    "relevant_content_engaged": [
      "Machine learning algorithms for predictive analytics",
      "Cloud migration best practices",
      "AI-driven automation tools for business processes"
    ],
    "technology_tools_adopted": [
      "TensorFlow for AI development",
      "Amazon Web Services (AWS) for cloud infrastructure",
      "Microsoft Azure Machine Learning for data analysis"
    ]
  }
}
```

## 📊 Data Models

### SearchRequest
```typescript
interface SearchRequest {
  prompt: string;
  max_candidates?: number; // Default: 3
  include_linkedin?: boolean; // Default: true
  include_posts?: boolean; // Default: false
}
```

### SearchResponse
```typescript
interface SearchResponse {
  request_id: string;
  status: string;
  prompt: string;
  filters?: {
    person_filters: {
      person_titles?: string[];
      include_similar_titles?: boolean;
      person_seniorities?: string[];
      person_locations?: string[];
    };
    organization_filters: {
      q_organization_keyword_tags?: string[];
    };
    reasoning: string;
  };
  candidates?: Candidate[];
  behavioral_data?: BehavioralData;
  error?: string;
  created_at: string;
  completed_at?: string;
}
```

### BehavioralData
```typescript
interface BehavioralData {
  behavioral_insights: {
    market_dynamics?: string;
    engagement_patterns?: string;
    decision_making_behaviors?: string;
    technology_adoption_trends?: string;
    [key: string]: string;
  };
  supporting_data_points: {
    [key: string]: string | string[];
  };
}
```

### Candidate
```typescript
interface Candidate {
  name: string;
  title: string;
  company: string;
  email?: string;
  accuracy: number; // 0-100
  reasons: string[];
  linkedin_url?: string;
  profile_photo_url?: string;
  location?: string;
  linkedin_profile?: object;
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
        include_linkedin: true
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

  const renderBehavioralData = (behavioralData: BehavioralData) => {
    if (!behavioralData) return null;

    return (
      <div className="behavioral-data">
        <h4>Behavioral Insights</h4>
        
        {behavioralData.behavioral_insights && (
          <div className="insights">
            {Object.entries(behavioralData.behavioral_insights).map(([key, value]) => (
              <div key={key} className="insight">
                <h5>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h5>
                <p>{value}</p>
              </div>
            ))}
          </div>
        )}

        {behavioralData.supporting_data_points && (
          <div className="supporting-data">
            <h5>Supporting Data</h5>
            {Object.entries(behavioralData.supporting_data_points).map(([key, value]) => (
              <div key={key} className="data-point">
                <h6>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h6>
                {Array.isArray(value) ? (
                  <ul>
                    {value.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <p>{value}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
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
            <div key={candidate.email || candidate.name} className="candidate-card">
              <h4>{candidate.name}</h4>
              <p>{candidate.title} at {candidate.company}</p>
              <p>Accuracy: {candidate.accuracy}%</p>
              <div className="reasons">
                <h5>Reasons:</h5>
                <ul>
                  {candidate.reasons.map((reason, index) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
          
          {result.behavioral_data && renderBehavioralData(result.behavioral_data)}
        </div>
      )}
    </div>
  );
};
```

### Behavioral Data Integration Example

Here's a more comprehensive example showing how to leverage the behavioral data for prospect prioritization:

```typescript
interface ProspectCard {
  candidate: Candidate;
  behavioralData: BehavioralData;
}

const ProspectPrioritizer = ({ prospects }: { prospects: ProspectCard[] }) => {
  // Sort prospects by decision-making authority (those with more authority first)
  const sortedProspects = [...prospects].sort((a, b) => {
    const hasAuthorityA = Object.values(a.behavioralData?.supporting_data_points || {})
      .some(value => typeof value === 'string' && value.toLowerCase().includes('decision'));
    const hasAuthorityB = Object.values(b.behavioralData?.supporting_data_points || {})
      .some(value => typeof value === 'string' && value.toLowerCase().includes('decision'));
    
    if (hasAuthorityA && !hasAuthorityB) return -1;
    if (!hasAuthorityA && hasAuthorityB) return 1;
    return 0;
  });

  const getEngagementLevel = (behavioralData: BehavioralData): string => {
    const engagementPattern = behavioralData?.behavioral_insights?.engagement_patterns || '';
    
    if (engagementPattern.toLowerCase().includes('high')) return "🔥 High Engagement";
    if (engagementPattern.toLowerCase().includes('regular')) return "⚡ Regular Engagement";
    if (engagementPattern.toLowerCase().includes('occasional')) return "📋 Occasional Engagement";
    return "❓ Unknown Engagement";
  };

  const getCommunicationStrategy = (behavioralData: BehavioralData): string => {
    const decisionMaking = behavioralData?.behavioral_insights?.decision_making_behaviors || '';
    const techAdoption = behavioralData?.behavioral_insights?.technology_adoption_trends || '';
    
    if (decisionMaking.toLowerCase().includes('key decision') || 
        decisionMaking.toLowerCase().includes('strategic')) {
      return "Focus on strategic value and ROI";
    }
    
    if (techAdoption.toLowerCase().includes('early adopter')) {
      return "Highlight innovative features and cutting-edge capabilities";
    }
    
    return "Balance technical details with business benefits";
  };

  return (
    <div className="prospect-list">
      {sortedProspects.map(({ candidate, behavioralData }) => (
        <div key={candidate.email || candidate.name} className="prospect-card">
          <div className="prospect-header">
            <h3>{candidate.name}</h3>
            <span className="engagement-level">
              {getEngagementLevel(behavioralData)}
            </span>
          </div>
          
          <p>{candidate.title} at {candidate.company}</p>
          
          <div className="behavioral-summary">
            {behavioralData?.behavioral_insights?.market_dynamics && (
              <div className="market-dynamics">
                <h5>Market Context</h5>
                <p>{behavioralData.behavioral_insights.market_dynamics}</p>
              </div>
            )}
            
            {behavioralData?.behavioral_insights?.decision_making_behaviors && (
              <div className="decision-making">
                <h5>Decision-Making Role</h5>
                <p>{behavioralData.behavioral_insights.decision_making_behaviors}</p>
              </div>
            )}
          </div>
          
          <div className="communication-strategy">
            <strong>Recommended Approach:</strong> {getCommunicationStrategy(behavioralData)}
          </div>
          
          {behavioralData?.supporting_data_points?.technology_interests && (
            <div className="technology-interests">
              <h5>Technology Interests</h5>
              <div className="tags">
                {Array.isArray(behavioralData.supporting_data_points.technology_interests) ? 
                  behavioralData.supporting_data_points.technology_interests.map((tech, index) => (
                    <span key={index} className="tag">{tech}</span>
                  )) : 
                  <span className="tag">{behavioralData.supporting_data_points.technology_interests}</span>
                }
              </div>
            </div>
          )}
        </div>
      ))}
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
6. **Behavioral Data**: The behavioral data provides valuable insights into prospect behavior and can be used to:
   - Understand the prospect's market context
   - Identify the prospect's role in decision-making processes
   - Determine the prospect's technology interests and adoption patterns
   - Tailor communication strategies based on engagement patterns
7. **Dynamic Structure**: The structure of `behavioral_insights` and `supporting_data_points` can vary based on the prospect's role and industry, so your frontend should handle this flexibility

## 🎯 Ready for Frontend Development

The API is now fully deployed and ready for frontend integration. All endpoints are working and the database is properly connected to Supabase. You can start building your frontend application using the examples and documentation above.