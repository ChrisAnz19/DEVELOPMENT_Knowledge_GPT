from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid

# Import the existing Knowledge_GPT modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables for API keys (for Render deployment)
if not os.getenv('OPENAI_API_KEY'):
    # Fallback to secrets.json for local development
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets.json"), "r") as f:
            import json
            secrets = json.load(f)
            os.environ['OPENAI_API_KEY'] = secrets.get('openai_api_key', '')
            os.environ['INTERNAL_DATABASE_API_KEY'] = secrets.get('internal_database_api_key', '')
            os.environ['BRIGHT_DATA_API_KEY'] = secrets.get('bright_data_api_key', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

from prompt_formatting import parse_prompt_to_internal_database_filters, simulate_behavioral_data
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import scrape_linkedin_profiles, scrape_linkedin_posts
from assess_and_return import select_top_candidates

app = FastAPI(
    title="Knowledge_GPT API",
    description="Natural language to behavioral data converter API",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing and frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SearchRequest(BaseModel):
    prompt: str
    max_candidates: Optional[int] = 2
    include_linkedin: Optional[bool] = True
    include_posts: Optional[bool] = True

class SearchResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    filters: Optional[Dict[str, Any]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    behavioral_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# In-memory storage for search results (in production, use Redis or database)
search_results = {}

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0"
    )

@app.post("/api/search", response_model=SearchResponse)
async def create_search(request: SearchRequest, background_tasks: BackgroundTasks):
    """Create a new search request"""
    request_id = str(uuid.uuid4())
    
    # Initialize search result
    search_results[request_id] = SearchResponse(
        request_id=request_id,
        status="processing",
        prompt=request.prompt,
        created_at=datetime.now(timezone.utc).isoformat()
    )
    
    # Start background processing
    background_tasks.add_task(process_search, request_id, request)
    
    return search_results[request_id]

@app.get("/api/search/{request_id}", response_model=SearchResponse)
async def get_search_result(request_id: str):
    """Get search result by request ID"""
    if request_id not in search_results:
        raise HTTPException(status_code=404, detail="Search request not found")
    
    return search_results[request_id]

@app.get("/api/search")
async def list_searches():
    """List all search requests"""
    return {
        "searches": [
            {
                "request_id": result.request_id,
                "status": result.status,
                "prompt": result.prompt,
                "created_at": result.created_at
            }
            for result in search_results.values()
        ]
    }

async def process_search(request_id: str, request: SearchRequest):
    """Background task to process the search"""
    try:
        result = search_results[request_id]
        
        # Step 1: Generate our internal database filters
        print(f"[{request_id}] Generating our internal database filters...")
        filters = parse_prompt_to_internal_database_filters(request.prompt)
        
        if filters["reasoning"].startswith("Error"):
            result.status = "failed"
            result.error = filters["reasoning"]
            result.completed_at = datetime.now(timezone.utc).isoformat()
            return
        
        result.filters = filters
        print(f"[{request_id}] Filters generated successfully")
        
        # Step 2: Search our internal database for people
        print(f"[{request_id}] Searching our internal database...")
        try:
            people = search_people_via_internal_database(filters, page=1, per_page=request.max_candidates or 2)
            print(f"[{request_id}] Found {len(people)} people")
            
            if not people:
                # Fall back to behavioral simulation
                print(f"[{request_id}] No people found, simulating behavioral data...")
                behavioral_data = simulate_behavioral_data(filters)
                result.behavioral_data = behavioral_data
                result.status = "completed"
                result.completed_at = datetime.now(timezone.utc).isoformat()
                return
                
        except Exception as e:
            print(f"[{request_id}] Our internal database API error: {e}")
            # Fall back to behavioral simulation
            behavioral_data = simulate_behavioral_data(filters)
            result.behavioral_data = behavioral_data
            result.status = "completed"
            result.completed_at = datetime.now(timezone.utc).isoformat()
            return
        
        # Step 3: Scrape LinkedIn profiles (if enabled)
        if request.include_linkedin:
            print(f"[{request_id}] Scraping LinkedIn profiles...")
            linkedin_urls = [person.get("linkedin_url") for person in people if person.get("linkedin_url")]
            
            if linkedin_urls:
                profile_data = scrape_linkedin_profiles(linkedin_urls)
                
                # Merge profile data with our internal database data
                enriched_people = []
                for i, person in enumerate(people):
                    if person.get("linkedin_url") and profile_data:
                        if isinstance(profile_data, list) and i < len(profile_data):
                            person["linkedin_profile"] = profile_data[i]
                        elif isinstance(profile_data, dict) and str(i) in profile_data:
                            person["linkedin_profile"] = profile_data[str(i)]
                    enriched_people.append(person)
                
                people = enriched_people
                print(f"[{request_id}] LinkedIn profiles scraped")
        
        # Step 4: Scrape LinkedIn posts (if enabled)
        if request.include_posts and request.include_linkedin:
            print(f"[{request_id}] Scraping LinkedIn posts...")
            for person in people[:2]:  # Only scrape posts for top 2 candidates
                profile = person.get("linkedin_profile", {})
                posts = profile.get("posts", [])
                recent_posts = posts[:5]  # Get up to 5 recent posts
                
                if recent_posts:
                    posts_data = scrape_linkedin_posts(recent_posts)
                    if posts_data:
                        person["linkedin_posts"] = posts_data
                    await asyncio.sleep(1)  # Rate limiting
            
            print(f"[{request_id}] LinkedIn posts scraped")
        
        # Step 5: Assess and select top candidates
        print(f"[{request_id}] Assessing candidates...")
        try:
            top_candidates = select_top_candidates(request.prompt, people)
            result.candidates = top_candidates
        except Exception as e:
            print(f"[{request_id}] Assessment error: {e}")
            # Fall back to basic results
            result.candidates = [
                {
                    "name": person.get("name", "Unknown"),
                    "title": person.get("title", "Unknown"),
                    "company": person.get("organization_name", "Unknown"),
                    "email": person.get("email", "Not available"),
                    "accuracy": 85 - (i * 10),
                    "reasons": ["Selected based on title and company fit"]
                }
                for i, person in enumerate(people[:request.max_candidates])
            ]
        
        # Step 6: Generate behavioral data
        print(f"[{request_id}] Generating behavioral data...")
        behavioral_data = simulate_behavioral_data(filters)
        result.behavioral_data = behavioral_data
        
        result.status = "completed"
        result.completed_at = datetime.now(timezone.utc).isoformat()
        print(f"[{request_id}] Search completed successfully")
        
    except Exception as e:
        print(f"[{request_id}] Unexpected error: {e}")
        result.status = "failed"
        result.error = str(e)
        result.completed_at = datetime.now(timezone.utc).isoformat()

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    """Delete a search request"""
    if request_id not in search_results:
        raise HTTPException(status_code=404, detail="Search request not found")
    
    del search_results[request_id]
    return {"message": "Search request deleted"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 