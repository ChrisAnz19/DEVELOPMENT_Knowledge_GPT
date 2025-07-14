# Knowledge_GPT API Deployment Guide

This guide will help you deploy the Knowledge_GPT API backend and integrate it with your React (Bolt) frontend.

## 🚀 Quick Start

### 1. Prerequisites

- Docker and Docker Compose installed
- API keys for:
  - OpenAI API
  - Apollo API
  - Bright Data API (optional)

### 2. Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd Knowledge_GPT

# Run the deployment script
./deploy.sh
```

The script will:
- Check for Docker installation
- Create `secrets.json` from template if needed
- Build and start the API container
- Verify the API is running

### 3. Configure API Keys

Edit `secrets.json` with your API keys:

```json
{
  "apollo_api_key": "your_apollo_api_key_here",
  "bright_data_api_key": "your_bright_data_api_key_here",
  "openai_api_key": "your_openai_api_key_here"
}
```

## 📊 API Endpoints

### Health Check
```
GET http://localhost:8000/
```

### Create Search
```
POST http://localhost:8000/api/search
Content-Type: application/json

{
  "prompt": "Find CEOs at large software companies in San Francisco",
  "max_candidates": 2,
  "include_linkedin": true,
  "include_posts": true
}
```

### Get Search Results
```
GET http://localhost:8000/api/search/{request_id}
```

### List All Searches
```
GET http://localhost:8000/api/search
```

### Delete Search
```
DELETE http://localhost:8000/api/search/{request_id}
```

## 🔧 API Documentation

Once deployed, visit `http://localhost:8000/docs` for interactive API documentation.

## 🌐 Frontend Integration

### Option 1: Use the Custom Hook (Recommended)

```tsx
import React, { useState } from 'react';
import { useKnowledgeGPT } from './hooks/useKnowledgeGPT';

function MyComponent() {
  const [prompt, setPrompt] = useState('');
  
  const {
    search,
    isSearching,
    currentSearch,
    searchHistory,
    error
  } = useKnowledgeGPT({
    apiUrl: 'http://localhost:8000',
    onSearchComplete: (results) => {
      console.log('Search completed:', results);
    }
  });

  const handleSearch = () => {
    search(prompt);
  };

  return (
    <div>
      <input
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your search prompt..."
      />
      <button onClick={handleSearch} disabled={isSearching}>
        {isSearching ? 'Searching...' : 'Search'}
      </button>
      
      {currentSearch?.status === 'completed' && currentSearch.candidates && (
        <div>
          <h3>Top Candidates</h3>
          {currentSearch.candidates.map((candidate, index) => (
            <div key={index}>
              <h4>{candidate.name}</h4>
              <p>{candidate.title} at {candidate.company}</p>
              <p>Accuracy: {candidate.accuracy}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Option 2: Use the Pre-built Component

```tsx
import React from 'react';
import KnowledgeGPTSimple from './components/KnowledgeGPTSimple';

function MyComponent() {
  return (
    <KnowledgeGPTSimple
      apiUrl="http://localhost:8000"
      onSearchComplete={(results) => {
        console.log('Search completed:', results);
      }}
    />
  );
}
```

### Option 3: Direct API Calls

```tsx
// Create a search
const createSearch = async (prompt: string) => {
  const response = await fetch('http://localhost:8000/api/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt,
      max_candidates: 2,
      include_linkedin: true,
      include_posts: true
    }),
  });
  
  return response.json();
};

// Poll for results
const pollResults = async (requestId: string) => {
  const response = await fetch(`http://localhost:8000/api/search/${requestId}`);
  return response.json();
};
```

## 🐳 Docker Management

### Start the API
```bash
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f
```

### Stop the API
```bash
docker-compose down
```

### Restart the API
```bash
docker-compose restart
```

### Rebuild and Start
```bash
docker-compose up --build -d
```

## 🔍 Troubleshooting

### API Not Starting
1. Check if Docker is running
2. Verify `secrets.json` exists and has valid API keys
3. Check logs: `docker-compose logs`

### CORS Issues
If you get CORS errors from your frontend, update the allowed origins in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Key Issues
- Ensure all required API keys are in `secrets.json`
- Verify API keys are valid and have sufficient credits
- Check API rate limits

### Memory Issues
If the container runs out of memory, increase Docker memory allocation or add memory limits to `docker-compose.yml`:

```yaml
services:
  knowledge-gpt-api:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 2G
```

## 📈 Production Deployment

### Environment Variables
For production, use environment variables instead of `secrets.json`:

```yaml
services:
  knowledge-gpt-api:
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - APOLLO_API_KEY=${APOLLO_API_KEY}
      - BRIGHT_DATA_API_KEY=${BRIGHT_DATA_API_KEY}
```

### Reverse Proxy
Use nginx or similar for production:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/TLS
Use Let's Encrypt or your preferred SSL provider for HTTPS.

## 🔄 Development Workflow

1. **Local Development**: Use `docker-compose up --build` for development
2. **Testing**: Use the test scripts in the root directory
3. **API Changes**: Rebuild the container after code changes
4. **Frontend Integration**: Use the provided React components or hooks

## 📝 API Response Format

### Search Response
```json
{
  "request_id": "uuid-string",
  "status": "processing|completed|failed",
  "prompt": "original search prompt",
  "filters": {
    "organization_filters": {...},
    "person_filters": {...},
    "reasoning": "..."
  },
  "candidates": [
    {
      "name": "John Doe",
      "title": "CEO",
      "company": "Tech Corp",
      "email": "john@techcorp.com",
      "accuracy": 85,
      "reasons": [
        "Frequent visits to enterprise software sites",
        "Engagement with industry webinars"
      ]
    }
  ],
  "behavioral_data": {...},
  "error": null,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:01:00Z"
}
```

## 🎯 Next Steps

1. Deploy the API using the deployment script
2. Integrate the React components into your Bolt frontend
3. Test the complete pipeline
4. Customize the UI and functionality as needed
5. Deploy to production with proper security measures

For questions or issues, check the main README.md or create an issue in the repository. 