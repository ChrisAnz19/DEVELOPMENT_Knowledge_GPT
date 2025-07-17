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
      },
      "behavioral_data": {
        "behavioral_insight": "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing.",
        "scores": {
          "cmi": {
            "score": 85,
            "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
          },
          "rbfs": {
            "score": 72,
            "explanation": "Moderate risk-barrier focus score suggests balancing technical details with clear business outcomes."
          },
          "ias": {
            "score": 90,
            "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
          }
        }
      }
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
      "linkedin_profile": {...},
      "behavioral_data": {
        "behavioral_insight": "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing.",
        "scores": {
          "cmi": {
            "score": 85,
            "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
          },
          "rbfs": {
            "score": 72,
            "explanation": "Moderate risk-barrier focus score suggests balancing technical details with clear business outcomes."
          },
          "ias": {
            "score": 90,
            "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
          }
        }
      }
    }
  ],
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

The API includes behavioral data that provides insights into prospect behavior and psychology. These insights are automatically generated and included for each individual candidate in the search results.

### Behavioral Data Structure

The behavioral data structure has been updated to provide a single, focused behavioral insight along with three key behavioral scores. This change provides both actionable guidance and quantitative metrics for each candidate.

#### New Structure (Current)
```typescript
interface BehavioralData {
  behavioral_insight: string; // Single, focused behavioral insight
  scores: {
    cmi: {
      score: number; // Communication Maturity Index (0-100)
      explanation: string; // Explanation of the score
    };
    rbfs: {
      score: number; // Risk-Barrier Focus Score (0-100)
      explanation: string; // Explanation of the score
    };
    ias: {
      score: number; // Identity Alignment Signal (0-100)
      explanation: string; // Explanation of the score
    };
  };
}
```

#### Legacy Structure (Deprecated)
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

### Focused Behavioral Insight

The new `behavioral_insight` field provides a single, focused recommendation on how to engage with the prospect. This insight is:

- Specific and actionable
- Tailored to the prospect's psychology and role
- Logically consistent with the search context
- Relevant to the user's goals

**Example:**
```json
"behavioral_insight": "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing."
```

### Behavioral Scores

The API now provides three key behavioral scores for each candidate:

1. **Communication Maturity Index (CMI)**: Measures how the candidate prefers to communicate and receive information.
   - High scores (80-100): Prefers direct, detailed, and technical communication
   - Medium scores (50-79): Balances technical and conceptual communication
   - Low scores (0-49): Prefers high-level, conceptual communication

2. **Risk-Barrier Focus Score (RBFS)**: Indicates how the candidate approaches risk and decision barriers.
   - High scores (80-100): Highly risk-averse, needs extensive validation
   - Medium scores (50-79): Balanced approach to risk, needs moderate validation
   - Low scores (0-49): Risk-tolerant, focuses on opportunities over barriers

3. **Identity Alignment Signal (IAS)**: Measures how strongly the candidate identifies with their professional role.
   - High scores (80-100): Strongly identifies with professional role and expertise
   - Medium scores (50-79): Balanced identity between professional and other aspects
   - Low scores (0-49): Less identification with professional role, more with other aspects

Each score includes an explanation that provides context and guidance on how to interpret and use the score.

**Example:**
```json
"scores": {
  "cmi": {
    "score": 85,
    "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
  },
  "rbfs": {
    "score": 72,
    "explanation": "Moderate risk-barrier focus score suggests balancing technical details with clear business outcomes."
  },
  "ias": {
    "score": 90,
    "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
  }
}
```

### Backward Compatibility

For backward compatibility, clients that expect the legacy format can still access the data by treating the single insight as the primary engagement recommendation. The following mapping can be used:

```javascript
// Converting new format to legacy format for backward compatibility
function convertToLegacyFormat(newBehavioralData) {
  if (!newBehavioralData || !newBehavioralData.behavioral_insight) {
    return null;
  }
  
  return {
    behavioral_insights: {
      engagement_patterns: newBehavioralData.behavioral_insight
    },
    supporting_data_points: {
      communication_maturity: newBehavioralData.scores?.cmi?.explanation || "",
      risk_barrier_focus: newBehavioralData.scores?.rbfs?.explanation || "",
      identity_alignment: newBehavioralData.scores?.ias?.explanation || ""
    }
  };
}
```

### Complete Behavioral Data Example

#### New Format
```json
"behavioral_data": {
  "behavioral_insight": "This CTO values direct communication and technical expertise. Begin by acknowledging their experience with cloud architecture, then present your solution with specific technical details and ROI metrics. Focus on how your offering solves their specific scaling challenges rather than general benefits.",
  "scores": {
    "cmi": {
      "score": 92,
      "explanation": "Very high communication maturity index indicates strong preference for direct, detailed technical communication with specific examples and data points."
    },
    "rbfs": {
      "score": 65,
      "explanation": "Moderate risk-barrier focus score suggests this CTO balances innovation with practical considerations. Present both technical advantages and risk mitigation strategies."
    },
    "ias": {
      "score": 88,
      "explanation": "High identity alignment signal indicates this CTO strongly identifies with their technical leadership role and values being recognized for technical expertise."
    }
  }
}
```

#### Legacy Format (Deprecated)
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
  error?: string;
  created_at: string;
  completed_at?: string;
}
```

### BehavioralData (Updated)
```typescript
interface BehavioralData {
  behavioral_insight: string; // Single, focused behavioral insight
  scores: {
    cmi: {
      score: number; // Communication Maturity Index (0-100)
      explanation: string; // Explanation of the score
    };
    rbfs: {
      score: number; // Risk-Barrier Focus Score (0-100)
      explanation: string; // Explanation of the score
    };
    ias: {
      score: number; // Identity Alignment Signal (0-100)
      explanation: string; // Explanation of the score
    };
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
  behavioral_data?: BehavioralData;
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

### Usage Example with Focused Behavioral Insight
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

  const renderBehavioralInsight = (behavioralData: BehavioralData) => {
    if (!behavioralData || !behavioralData.behavioral_insight) return null;

    return (
      <div className="behavioral-insight">
        <h4>Engagement Strategy</h4>
        <div className="insight-card">
          <div className="insight-icon">💡</div>
          <p>{behavioralData.behavioral_insight}</p>
        </div>
        
        {behavioralData.scores && (
          <div className="behavioral-scores">
            <h5>Behavioral Scores</h5>
            <div className="score-grid">
              <div className="score-card">
                <div className="score-header">
                  <span className="score-title">Communication Maturity</span>
                  <span className="score-value">{behavioralData.scores.cmi.score}</span>
                </div>
                <p className="score-explanation">{behavioralData.scores.cmi.explanation}</p>
              </div>
              
              <div className="score-card">
                <div className="score-header">
                  <span className="score-title">Risk-Barrier Focus</span>
                  <span className="score-value">{behavioralData.scores.rbfs.score}</span>
                </div>
                <p className="score-explanation">{behavioralData.scores.rbfs.explanation}</p>
              </div>
              
              <div className="score-card">
                <div className="score-header">
                  <span className="score-title">Identity Alignment</span>
                  <span className="score-value">{behavioralData.scores.ias.score}</span>
                </div>
                <p className="score-explanation">{behavioralData.scores.ias.explanation}</p>
              </div>
            </div>
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
              {candidate.profile_photo_url && (
                <img 
                  src={candidate.profile_photo_url} 
                  alt={`${candidate.name}'s profile`}
                  className="profile-photo"
                />
              )}
              <div className="candidate-info">
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
                {candidate.behavioral_data && renderBehavioralInsight(candidate.behavioral_data)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### Focused Behavioral Insight Integration Example

Here's a more comprehensive example showing how to leverage the focused behavioral insight and scores for prospect engagement:

```typescript
interface ProspectCard {
  candidate: Candidate;
}

const ProspectEngagementCard = ({ prospect }: { prospect: ProspectCard }) => {
  const { candidate } = prospect;
  const behavioralData = candidate.behavioral_data;
  
  // Extract key engagement elements from the behavioral insight
  const getEngagementElements = (insight: string) => {
    // These are example categories that might be extracted from the insight
    const elements = {
      approach: '',
      topics: [],
      style: '',
      valueProposition: ''
    };
    
    // Simple extraction logic - in a real app, you might use more sophisticated parsing
    if (insight.toLowerCase().includes('technical')) {
      elements.approach = 'Technical';
    } else if (insight.toLowerCase().includes('strategic')) {
      elements.approach = 'Strategic';
    } else if (insight.toLowerCase().includes('collaborative')) {
      elements.approach = 'Collaborative';
    } else {
      elements.approach = 'Balanced';
    }
    
    // Extract potential conversation topics
    const topicMatches = insight.match(/ask about ([^,.]+)/i);
    if (topicMatches && topicMatches[1]) {
      elements.topics.push(topicMatches[1].trim());
    }
    
    return elements;
  };
  
  const getScoreClass = (score: number) => {
    if (score >= 80) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
  };
  
  const engagementElements = behavioralData?.behavioral_insight ? 
    getEngagementElements(behavioralData.behavioral_insight) : 
    { approach: 'Balanced', topics: [], style: '', valueProposition: '' };

  return (
    <div className="prospect-card">
      <div className="prospect-header">
        {candidate.profile_photo_url && (
          <img 
            src={candidate.profile_photo_url} 
            alt={`${candidate.name}'s profile`}
            className="profile-photo"
          />
        )}
        <div>
          <h3>{candidate.name}</h3>
          <p>{candidate.title} at {candidate.company}</p>
        </div>
        <div className="approach-badge">
          {engagementElements.approach} Approach
        </div>
      </div>
      
      <div className="engagement-strategy">
        <h4>Engagement Strategy</h4>
        <p>{behavioralData?.behavioral_insight}</p>
      </div>
      
      {behavioralData?.scores && (
        <div className="behavioral-scores">
          <div className="score-meters">
            <div className="score-meter">
              <label>Communication Style</label>
              <div className="meter-container">
                <div 
                  className={`meter-fill ${getScoreClass(behavioralData.scores.cmi.score)}`}
                  style={{ width: `${behavioralData.scores.cmi.score}%` }}
                ></div>
              </div>
              <div className="meter-labels">
                <span>Conceptual</span>
                <span>Technical</span>
              </div>
              <p className="score-tip">{behavioralData.scores.cmi.explanation}</p>
            </div>
            
            <div className="score-meter">
              <label>Risk Approach</label>
              <div className="meter-container">
                <div 
                  className={`meter-fill ${getScoreClass(behavioralData.scores.rbfs.score)}`}
                  style={{ width: `${behavioralData.scores.rbfs.score}%` }}
                ></div>
              </div>
              <div className="meter-labels">
                <span>Opportunity-focused</span>
                <span>Risk-averse</span>
              </div>
              <p className="score-tip">{behavioralData.scores.rbfs.explanation}</p>
            </div>
            
            <div className="score-meter">
              <label>Professional Identity</label>
              <div className="meter-container">
                <div 
                  className={`meter-fill ${getScoreClass(behavioralData.scores.ias.score)}`}
                  style={{ width: `${behavioralData.scores.ias.score}%` }}
                ></div>
              </div>
              <div className="meter-labels">
                <span>Balanced</span>
                <span>Role-identified</span>
              </div>
              <p className="score-tip">{behavioralData.scores.ias.explanation}</p>
            </div>
          </div>
        </div>
      )}
      
      {engagementElements.topics.length > 0 && (
        <div className="conversation-starters">
          <h5>Potential Conversation Starters</h5>
          <ul>
            {engagementElements.topics.map((topic, index) => (
              <li key={index}>
                <strong>Ask about:</strong> {topic}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="contact-actions">
        {candidate.email && (
          <button className="contact-button email">
            Email
          </button>
        )}
        {candidate.linkedin_url && (
          <button className="contact-button linkedin">
            LinkedIn
          </button>
        )}
      </div>
    </div>
  );
};

// Usage in a list component
const ProspectList = ({ prospects }: { prospects: Candidate[] }) => {
  return (
    <div className="prospect-list">
      {prospects.map((candidate, index) => (
        <ProspectEngagementCard key={index} prospect={{ candidate }} />
      ))}
    </div>
  );
};
```

### Backward Compatibility Helper

For applications that need to support both the new and legacy formats:

```typescript
const getBehavioralInsight = (behavioralData: any): string => {
  // Check if using new format
  if (behavioralData?.behavioral_insight) {
    return behavioralData.behavioral_insight;
  }
  
  // Check if using legacy format
  if (behavioralData?.behavioral_insights?.engagement_patterns) {
    return behavioralData.behavioral_insights.engagement_patterns;
  }
  
  // Fallback
  return "No engagement insight available";
};

const getBehavioralScores = (behavioralData: any) => {
  const defaultScores = {
    cmi: { score: 50, explanation: "No communication maturity data available" },
    rbfs: { score: 50, explanation: "No risk-barrier focus data available" },
    ias: { score: 50, explanation: "No identity alignment data available" }
  };
  
  // Check if using new format with scores
  if (behavioralData?.scores) {
    return behavioralData.scores;
  }
  
  // Check if using legacy format
  if (behavioralData?.behavioral_insights) {
    // Extract approximate scores from legacy format (simplified example)
    return {
      cmi: { 
        score: 60, 
        explanation: "Based on legacy engagement patterns data" 
      },
      rbfs: { 
        score: 60, 
        explanation: "Based on legacy decision making behaviors data" 
      },
      ias: { 
        score: 60, 
        explanation: "Based on legacy technology adoption trends data" 
      }
    };
  }
  
  return defaultScores;
};

// Usage example
const renderBehavioralGuidance = (behavioralData: any) => {
  const insight = getBehavioralInsight(behavioralData);
  const scores = getBehavioralScores(behavioralData);
  
  return (
    <div className="engagement-guidance">
      <h4>How to Engage</h4>
      <p>{insight}</p>
      
      <div className="behavioral-scores">
        <div className="score-item">
          <span className="score-label">Communication Style:</span>
          <span className="score-value">{scores.cmi.score}</span>
          <p className="score-explanation">{scores.cmi.explanation}</p>
        </div>
        
        <div className="score-item">
          <span className="score-label">Risk Approach:</span>
          <span className="score-value">{scores.rbfs.score}</span>
          <p className="score-explanation">{scores.rbfs.explanation}</p>
        </div>
        
        <div className="score-item">
          <span className="score-label">Professional Identity:</span>
          <span className="score-value">{scores.ias.score}</span>
          <p className="score-explanation">{scores.ias.explanation}</p>
        </div>
      </div>
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
6. **Focused Behavioral Insight**: The new behavioral insight provides:
   - A single, actionable recommendation for engaging with the prospect
   - Guidance tailored to the prospect's psychology and role
   - Context-aware engagement strategies that consider the search query
   - Specific conversation starters or approaches to use
7. **Behavioral Scores**: Each candidate now includes three key behavioral scores:
   - Communication Maturity Index (CMI): How the candidate prefers to communicate
   - Risk-Barrier Focus Score (RBFS): How the candidate approaches risk and decision barriers
   - Identity Alignment Signal (IAS): How strongly the candidate identifies with their professional role
8. **Profile Photos**: The API now prioritizes finding and including profile photo URLs for candidates, with improved extraction and validation
9. **Backward Compatibility**: The API maintains backward compatibility for existing clients while providing the enhanced format

### Migrating from Legacy to New Format

For applications currently using the legacy behavioral data format:

1. **Update your data models** to accept the new `behavioral_insight` field and `scores` object
2. **Use the backward compatibility helper** provided above if you need to support both formats
3. **Enhance your UI** to display both the focused insight and the three behavioral scores
4. **Update your engagement strategy components** to extract actionable guidance from the insight and scores

## 🎯 Ready for Frontend Development

The API is now fully deployed and ready for frontend integration with the new focused behavioral insight feature. All endpoints are working and the database is properly connected to Supabase. You can start building your frontend application using the examples and documentation above.