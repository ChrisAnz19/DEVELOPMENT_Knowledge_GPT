from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import json
import asyncio
from datetime import datetime, timezone
import uuid
import sys
import os
import re
import httpx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if not os.getenv('OPENAI_API_KEY'):
    try:
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secrets.json"), "r") as f:
            secrets = json.load(f)
            # Handle both uppercase and lowercase key names for compatibility
            os.environ['OPENAI_API_KEY'] = secrets.get('openai_api_key', '') or secrets.get('OPENAI_API_KEY', '')
            os.environ['INTERNAL_DATABASE_API_KEY'] = secrets.get('internal_database_api_key', '') or secrets.get('INTERNAL_DATABASE_API_KEY', '')
            os.environ['SCRAPING_DOG_API_KEY'] = secrets.get('scraping_dog_api_key', '') or secrets.get('SCRAPING_DOG_API_KEY', '')
            os.environ['SUPABASE_URL'] = secrets.get('supabase_url', '') or secrets.get('SUPABASE_URL', '')
            os.environ['SUPABASE_KEY'] = secrets.get('supabase_key', '') or secrets.get('SUPABASE_KEY', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

from prompt_formatting import parse_prompt_to_internal_database_filters
from apollo_api_call import search_people_via_internal_database
# from linkedin_scraping import async_scrape_linkedin_profiles  # Commented out - using Apollo data instead
from assess_and_return import select_top_candidates
from database import (
    store_search_to_database, get_search_from_database, 
    get_recent_searches_from_database, delete_search_from_database,
    store_people_to_database, get_people_for_search
)
from behavioral_metrics_ai import enhance_behavioral_data_ai
from smart_prompt_enhancement import enhance_prompt
from simple_estimation import estimate_people_count
from creepy_detector import detect_specific_person_search, extract_user_first_name_from_context

# Cache for public figure checks to avoid repeated requests
_public_figure_cache: Dict[str, bool] = {}

async def is_public_figure(full_name: str) -> bool:
    """Return True if Wikipedia search suggests this person is a well-known public figure."""
    name_key = full_name.lower().strip()
    if not name_key:
        return False
    if name_key in _public_figure_cache:
        return _public_figure_cache[name_key]
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": full_name,
                    "format": "json",
                    "srlimit": 1
                }
            )
            resp.raise_for_status()
            data = resp.json()
            search_results = data.get("query", {}).get("search", [])
            if not search_results:
                _public_figure_cache[name_key] = False
                return False
            top = search_results[0]
            title = top.get("title", "").lower()
            snippet = re.sub(r"<[^>]+>", "", top.get("snippet", "")).lower()
            famous = name_key in title or name_key in snippet
            _public_figure_cache[name_key] = famous
            return famous
    except Exception:
        # On any error, assume not famous to avoid false positives
        _public_figure_cache[name_key] = False
        return False

app = FastAPI(title="Knowledge_GPT API with People Estimation", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    prompt: str
    max_candidates: Optional[int] = 3
    include_linkedin: Optional[bool] = True

class SearchResponse(BaseModel):
    request_id: str
    status: str
    prompt: str
    filters: Optional[Dict[str, Any]] = None
    candidates: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    estimated_count: Optional[int] = None

def extract_profile_photo_url(candidate_data, linkedin_profile=None):
    try:
        if not isinstance(candidate_data, dict):
            return None
            
        if linkedin_profile and isinstance(linkedin_profile, dict):
            for field in ["profile_photo_url", "profile_photo", "avatar", "image"]:
                if field in linkedin_profile and linkedin_profile[field]:
                    return linkedin_profile[field]
        
        for field in ["profile_photo_url", "photo_url", "profile_picture_url"]:
            if field in candidate_data and candidate_data[field]:
                return candidate_data[field]
        
        if "organization" in candidate_data and isinstance(candidate_data["organization"], dict):
            org = candidate_data["organization"]
            if "logo_url" in org and org["logo_url"]:
                return org["logo_url"]
                
        return None
    except Exception:
        return None

async def process_search(request_id: str, prompt: str, max_candidates: int = 3, include_linkedin: bool = True):
    is_completed = False
    
    try:
        search_data = get_search_from_database(request_id)
        if not search_data or search_data.get("status") == "completed":
            return
        
        # Preprocess prompt to convert generic terms to "executives"
        def preprocess_prompt(prompt_text: str) -> str:
            """Convert generic people terms to 'executives' for better search results."""
            # Define generic terms that should be converted to "executives"
            generic_terms = [
                "people", "persons", "person", "anyone", "somebody", "someone",
                "individuals", "individual", "professionals", "professional",
                "contacts", "contact", "leads", "lead"
            ]
            
            processed_prompt = prompt_text
            
            # Replace generic terms with "executives"
            for term in generic_terms:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, processed_prompt, re.IGNORECASE):
                    processed_prompt = re.sub(pattern, 'executives', processed_prompt, flags=re.IGNORECASE)
                    print(f"[Prompt Processing] Converted '{term}' to 'executives' in search query")
            
            return processed_prompt
        
        # Apply prompt preprocessing
        preprocessed_prompt = preprocess_prompt(prompt)
        
        # Apply smart prompt enhancement with error handling fallback
        try:
            enhanced_prompt, analysis = enhance_prompt(preprocessed_prompt)
            # Log the enhancement for transparency (could be stored in database later)
            if analysis.reasoning:
                print(f"Smart prompt enhancement applied: {', '.join(analysis.reasoning)}")
        except Exception as e:
            # Fall back to preprocessed prompt on any failure
            enhanced_prompt = preprocessed_prompt
            print(f"Smart prompt enhancement failed, using preprocessed prompt: {str(e)}")
        
        filters = parse_prompt_to_internal_database_filters(enhanced_prompt)
        
        try:
            people = await asyncio.wait_for(
                search_people_via_internal_database(filters, page=1, per_page=max_candidates),
                timeout=60
            )
        except (asyncio.TimeoutError, Exception) as e:
            search_data["status"] = "failed"
            search_data["error"] = str(e)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            return
        
        if not people:
            search_data["status"] = "completed"
            search_data["filters"] = json.dumps(filters)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            return
        
        # LinkedIn scraping commented out - using Apollo data instead
        # if include_linkedin and people:
        #     try:
        #         linkedin_urls = [p.get("linkedin_url") for p in people if isinstance(p, dict) and p.get("linkedin_url")]
        #         
        #         if linkedin_urls:
        #             # Use a shorter timeout for LinkedIn scraping to prevent hanging
        #             linkedin_profiles = await asyncio.wait_for(
        #                 async_scrape_linkedin_profiles(linkedin_urls),
        #                 timeout=30  # Reduced from 60 to 30 seconds
        #             )
        #             
        #             if linkedin_profiles:
        #                 profile_map = {p.get("linkedin_url"): p for p in linkedin_profiles if isinstance(p, dict) and p.get("linkedin_url")}
        #                 
        #                 for person in people:
        #                         if isinstance(person, dict):
        #                             linkedin_url = person.get("linkedin_url")
        #                             if linkedin_url and linkedin_url in profile_map:
        #                                 person["linkedin_profile"] = profile_map[linkedin_url]
        #     except asyncio.TimeoutError:
        #         # LinkedIn scraping timed out, continue without LinkedIn data
        #         pass
        #     except Exception:
        #         # Any other error, continue without LinkedIn data
        #         pass
        
        # Filter out non-US locations and known public figures via Wikipedia
        filtered_people = []
        for p in people:
            if not isinstance(p, dict):
                continue
            
            # Location filtering: exclude non-US, allow no location
            loc = (p.get("location") or p.get("country") or "").lower()
            
            if loc:
                # Comprehensive list of non-US countries/regions to exclude
                non_us_locations = [
                    # Major countries
                    "canada", "mexico", "uk", "united kingdom", "england", "scotland", "wales", "ireland",
                    "france", "germany", "spain", "italy", "netherlands", "belgium", "switzerland",
                    "austria", "portugal", "sweden", "norway", "denmark", "finland", "poland",
                    "czech republic", "hungary", "romania", "bulgaria", "greece", "turkey",
                    "russia", "ukraine", "belarus", "lithuania", "latvia", "estonia",
                    "australia", "new zealand", "japan", "south korea", "china", "taiwan",
                    "singapore", "malaysia", "thailand", "vietnam", "philippines", "indonesia",
                    "india", "pakistan", "bangladesh", "sri lanka", "nepal", "myanmar",
                    "israel", "saudi arabia", "uae", "qatar", "kuwait", "bahrain", "oman",
                    "egypt", "south africa", "nigeria", "kenya", "morocco", "tunisia",
                    "brazil", "argentina", "chile", "colombia", "peru", "venezuela", "ecuador",
                    # European cities that are clearly non-US
                    "london", "paris", "berlin", "madrid", "rome", "amsterdam", "brussels",
                    "zurich", "vienna", "stockholm", "oslo", "copenhagen", "helsinki",
                    # Other major non-US cities
                    "toronto", "vancouver", "montreal", "sydney", "melbourne", "tokyo",
                    "seoul", "beijing", "shanghai", "hong kong", "mumbai", "delhi", "bangalore"
                ]
                
                # Exclude if location contains any non-US indicator
                is_non_us = any(non_us in loc for non_us in non_us_locations)
                if is_non_us:
                    continue
            
            # Exclude well-known public figures
            name_val = (p.get("name") or "").strip()
            if name_val and await is_public_figure(name_val):
                continue
                
            filtered_people.append(p)
        people = filtered_people
        
        candidates = []
        try:
            if people:
                # Select top candidates via assessment module
                top_basic = select_top_candidates(prompt, people)
                
                # Merge full Apollo details back into the lightweight objects returned
                candidates = []
                seen_identifiers = set()  # Track seen candidates to prevent duplicates
                
                if top_basic and isinstance(top_basic, list):
                    for basic in top_basic:
                        # Create unique identifier for this candidate
                        identifier = None
                        if basic.get("linkedin_url"):
                            identifier = basic.get("linkedin_url")
                        elif basic.get("email"):
                            identifier = basic.get("email")
                        elif basic.get("name"):
                            identifier = basic.get("name")
                        
                        # Skip if we've already seen this candidate
                        if identifier and identifier in seen_identifiers:
                            continue
                        
                        # Find match in original list by linkedin_url or email or name
                        match = None
                        for p in people:
                            if not isinstance(p, dict):
                                continue
                            if (
                                (basic.get("linkedin_url") and basic.get("linkedin_url") == p.get("linkedin_url")) or
                                (basic.get("email") and basic.get("email") == p.get("email")) or
                                (basic.get("name") and basic.get("name") == p.get("name"))
                            ):
                                match = p
                                break
                        
                        merged = {**basic}
                        if match:
                            merged.update(match)  # keep enriched fields (photo, company, etc.)
                        
                        candidates.append(merged)
                        if identifier:
                            seen_identifiers.add(identifier)
                
                # Fallback if merging failed
                if not candidates:
                    candidates = people[:max_candidates]
            
            if not candidates:
                candidates = people[:max_candidates]
        except Exception:
            candidates = people[:max_candidates] if people else []
        
        for candidate in candidates:
            if isinstance(candidate, dict):
                # Use Apollo data for profile photo, company, and LinkedIn URL
                
                # Set profile photo from Apollo data
                if candidate.get("profile_pic_url"):
                    candidate["profile_photo_url"] = candidate["profile_pic_url"]
                
                # Set company from Apollo organization data
                if not candidate.get("company") or candidate.get("company") == "Unknown":
                    if "organization" in candidate:
                        org = candidate["organization"]
                        if isinstance(org, dict) and org.get("name"):
                            candidate["company"] = org["name"]
                        elif isinstance(org, str) and org.strip():
                            candidate["company"] = org
                
                # Ensure LinkedIn URL is properly formatted
                linkedin_url = candidate.get("linkedin_url")
                if linkedin_url and not linkedin_url.startswith("http"):
                    candidate["linkedin_url"] = f"https://{linkedin_url}"
        
        # Generate behavioral data for all candidates with enhanced uniqueness validation
        try:
            from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
            
            # Create a set to track used insights across all candidates
            used_insights = set()
            used_patterns = set()
            
            # Enhanced call with uniqueness tracking
            candidates = enhance_behavioral_data_for_multiple_candidates(candidates, prompt)
            
            # Additional uniqueness check across all candidates
            for i, candidate in enumerate(candidates):
                if isinstance(candidate, dict) and "behavioral_data" in candidate:
                    insight = candidate["behavioral_data"].get("behavioral_insight", "")
                    
                    # If this insight is too similar to one we've seen before, regenerate it
                    from openai_utils import validate_response_uniqueness
                    if insight in used_insights or len(validate_response_uniqueness([insight] + list(used_insights), 0.5)) <= len(used_insights):
                        from behavioral_metrics_ai import generate_diverse_fallback_insight, add_score_variation
                        title = candidate.get('title', 'professional')
                        
                        # Generate truly diverse fallback
                        new_insight = generate_diverse_fallback_insight(title, candidate, prompt, used_patterns, i + 100)  # Add offset to ensure different pattern
                        candidate["behavioral_data"]["behavioral_insight"] = new_insight
                        used_patterns.add(new_insight)
                    
                    # Track this insight for future uniqueness checks
                    used_insights.add(candidate["behavioral_data"].get("behavioral_insight", ""))
                    
        except Exception as e:
            # Fallback: generate behavioral data for each candidate individually with diversity
            used_patterns = set()
            for i, candidate in enumerate(candidates):
                if isinstance(candidate, dict):
                    try:
                        # Mark first 3 candidates as top leads
                        is_top_candidate = i < 3
                        candidate_behavioral_data = enhance_behavioral_data_ai({}, [candidate], prompt, candidate_index=i, is_top_candidate=is_top_candidate)
                        candidate["behavioral_data"] = candidate_behavioral_data
                    except Exception:
                        from behavioral_metrics_ai import generate_diverse_fallback_insight, generate_top_lead_scores, add_score_variation, generate_fallback_cmi_score, generate_fallback_rbfs_score, generate_fallback_ias_score
                        title = candidate.get('title', 'professional')
                        
                        # Generate diverse fallback with variation
                        fallback_insight = generate_diverse_fallback_insight(title, candidate, prompt, used_patterns, i)
                        used_patterns.add(fallback_insight)
                        
                        # Generate proper fallback scores
                        base_scores = {
                            "cmi": generate_fallback_cmi_score(title, prompt, i),
                            "rbfs": generate_fallback_rbfs_score(title, prompt, i),
                            "ias": generate_fallback_ias_score(title, prompt, i)
                        }
                        
                        # Use top lead scores for first 3 candidates
                        if i < 3:
                            varied_scores = generate_top_lead_scores(base_scores, i)
                        else:
                            varied_scores = add_score_variation(base_scores, i)
                        
                        candidate["behavioral_data"] = {
                            "behavioral_insight": fallback_insight,
                            "scores": varied_scores
                        }
        
        search_db_id = search_data.get("id")
        if search_db_id:
            store_people_to_database(search_db_id, candidates)
        
        # Generate estimation for the search
        try:
            estimation = estimate_people_count(prompt)
            # Store in both formats for compatibility
            search_data["estimated_count"] = estimation["estimated_count"]
            search_data["result_estimation"] = {
                "estimated_count": estimation["estimated_count"],
                "confidence": "high",
                "reasoning": estimation.get("reasoning", f"AI estimated {estimation['estimated_count']} people meet the criteria"),
                "limiting_factors": []
            }
            print(f"[Estimation] Generated estimate: {estimation['estimated_count']} people for prompt: {prompt}")
            print(f"[Estimation] search_data now contains: estimated_count={search_data.get('estimated_count')}, result_estimation={search_data.get('result_estimation')}")
        except Exception as e:
            print(f"[Estimation] Failed to generate estimate: {e}")
            search_data["estimated_count"] = None
            search_data["result_estimation"] = None
        
        if not is_completed:
            try:
                search_data["status"] = "completed"
                search_data["filters"] = json.dumps(filters)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                print(f"[Estimation] About to store search_data with estimated_count: {search_data.get('estimated_count')}")
                store_search_to_database(search_data)
                print(f"[Estimation] Successfully stored search data to database")
                is_completed = True
            except Exception:
                try:
                    search_data["status"] = "completed"
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
                    is_completed = True
                except Exception:
                    pass
            
    except Exception as e:
        if not is_completed:
            try:
                search_data = get_search_from_database(request_id)
                if search_data:
                    search_data["status"] = "failed"
                    search_data["error"] = str(e)
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                    store_search_to_database(search_data)
            except Exception:
                pass

@app.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/search")
async def create_search(request: SearchRequest, background_tasks: BackgroundTasks):
    try:
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Validate prompt for ridiculous or inappropriate content
        prompt_lower = request.prompt.lower().strip()
        
        # Check for obviously inappropriate requests - only the most obvious cases
        inappropriate_patterns = [
            "elon musk", "jeff bezos", "mark zuckerberg", "bill gates", "larry fink",
            "ceo of apple", "ceo of google", "ceo of microsoft", "ceo of amazon",
            "president of the united states", "white house", "government officials",
            "movie stars", "actors", "singers", "athletes", "celebrities"
        ]
        
        for pattern in inappropriate_patterns:
            if pattern in prompt_lower:
                # Store the failed search in database for history
                request_id = str(uuid.uuid4())
                created_at = datetime.now(timezone.utc).isoformat()
                error_message = f"Search request appears to be looking for well-known public figures. Please search for specific professional roles or industries instead."
                
                failed_search_data = {
                    "request_id": request_id,
                    "status": "failed",
                    "prompt": request.prompt.strip(),
                    "filters": json.dumps({}),
                    "created_at": created_at,
                    "completed_at": created_at,
                    "error": error_message,
                    "estimated_count": None,
                    "result_estimation": None
                }
                
                store_search_to_database(failed_search_data)
                
                raise HTTPException(
                    status_code=400, 
                    detail=error_message
                )
        
        # Check for overly vague or nonsensical requests
        vague_patterns = [
            "find me someone", "find me a person", "find me anybody",
            "anyone who", "somebody who", "a person who",
            "random people", "random person", "any person"
        ]
        
        if any(pattern in prompt_lower for pattern in vague_patterns):
            # Store the failed search in database for history
            request_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            error_message = "Please provide more specific search criteria. What role, industry, or professional background are you looking for?"
            
            failed_search_data = {
                "request_id": request_id,
                "status": "failed",
                "prompt": request.prompt.strip(),
                "filters": json.dumps({}),
                "created_at": created_at,
                "completed_at": created_at,
                "error": error_message,
                "estimated_count": None,
                "result_estimation": None
            }
            
            store_search_to_database(failed_search_data)
            
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
        
        # Check for creepy searches (specific person by name)
        user_first_name = extract_user_first_name_from_context()  # Can be expanded later with actual user data
        creepy_detection = detect_specific_person_search(request.prompt.strip(), user_first_name)
        
        if creepy_detection["is_creepy"]:
            # Log the creepy search attempt for monitoring
            print(f"[Creepy Detector] Blocked search for: {creepy_detection['detected_names']} - Reason: {creepy_detection.get('reasoning', 'Unknown')}")
            
            # Store the failed search in database for history
            request_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            
            failed_search_data = {
                "request_id": request_id,
                "status": "failed",
                "prompt": request.prompt.strip(),
                "filters": json.dumps({}),
                "created_at": created_at,
                "completed_at": created_at,
                "error": creepy_detection["response"],
                "estimated_count": None,
                "result_estimation": None
            }
            
            store_search_to_database(failed_search_data)
            
            raise HTTPException(
                status_code=400,
                detail=creepy_detection["response"]
            )
        
        # Check for requests that are too broad
        if len(prompt_lower.split()) < 3:
            # Store the failed search in database for history
            request_id = str(uuid.uuid4())
            created_at = datetime.now(timezone.utc).isoformat()
            error_message = "Please provide more detailed search criteria. Include role, industry, or specific requirements."
            
            failed_search_data = {
                "request_id": request_id,
                "status": "failed",
                "prompt": request.prompt.strip(),
                "filters": json.dumps({}),
                "created_at": created_at,
                "completed_at": created_at,
                "error": error_message,
                "estimated_count": None,
                "result_estimation": None
            }
            
            store_search_to_database(failed_search_data)
            
            raise HTTPException(
                status_code=400,
                detail=error_message
            )
        
        if request.max_candidates and (request.max_candidates < 1 or request.max_candidates > 10):
            raise HTTPException(status_code=400, detail="max_candidates must be between 1 and 10")
        
        request_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        
        search_data = {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt.strip(),
            "filters": json.dumps({}),
            "created_at": created_at,
            "completed_at": None
        }
        
        search_db_id = store_search_to_database(search_data)
        if not search_db_id:
            raise HTTPException(status_code=500, detail="Failed to store search in database")
        
        background_tasks.add_task(
            process_search,
            request_id=request_id,
            prompt=request.prompt.strip(),
            max_candidates=request.max_candidates or 3,
            include_linkedin=request.include_linkedin if request.include_linkedin is not None else True
        )
        
        return {
            "request_id": request_id,
            "status": "processing",
            "prompt": request.prompt.strip(),
            "created_at": created_at,
            "completed_at": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating search: {str(e)}")

@app.get("/api/search/{request_id}")
async def get_search_result(request_id: str):
    try:
        if not request_id or not isinstance(request_id, str):
            raise HTTPException(status_code=400, detail="Invalid request_id")
        
        search_data = get_search_from_database(request_id)
        
        if not search_data:
            raise HTTPException(status_code=404, detail="Search not found")
        
        if not isinstance(search_data, dict):
            raise HTTPException(status_code=500, detail="Invalid search data format")
        
        if "filters" in search_data and isinstance(search_data["filters"], str):
            try:
                search_data["filters"] = json.loads(search_data["filters"])
            except json.JSONDecodeError:
                search_data["filters"] = {}
        
        search_db_id = search_data.get("id")
        if search_db_id:
            candidates = get_people_for_search(search_db_id)
            if candidates and isinstance(candidates, list):
                processed_candidates = []
                
                for candidate in candidates:
                    if isinstance(candidate, dict):
                        processed_candidate = {
                            "id": candidate.get("id"),
                            "name": candidate.get("name"),
                            "title": candidate.get("title"),
                            "email": candidate.get("email"),
                            "location": candidate.get("location"),
                            "company": candidate.get("company"),
                            "linkedin_url": candidate.get("linkedin_url"), 
                            "profile_photo_url": candidate.get("profile_photo_url"),
                            "accuracy": candidate.get("accuracy"),
                            "reasons": candidate.get("reasons"),
                            "linkedin_profile": candidate.get("linkedin_profile"),
                            "behavioral_data": candidate.get("behavioral_data")
                        }
                        processed_candidates.append(processed_candidate)
                
                search_data["candidates"] = processed_candidates
                search_data["status"] = "completed"
                if not search_data.get("completed_at"):
                    search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Extract estimated_count from result_estimation if it exists
        if "result_estimation" in search_data and search_data["result_estimation"]:
            if isinstance(search_data["result_estimation"], dict):
                search_data["estimated_count"] = search_data["result_estimation"].get("estimated_count")
            elif isinstance(search_data["result_estimation"], str):
                try:
                    result_est = json.loads(search_data["result_estimation"])
                    search_data["estimated_count"] = result_est.get("estimated_count")
                except json.JSONDecodeError:
                    pass
        
        # Ensure all required fields are present for backward compatibility
        if "estimated_count" not in search_data:
            search_data["estimated_count"] = None
        if "error" not in search_data:
            search_data["error"] = None
        if "result_estimation" not in search_data:
            search_data["result_estimation"] = None
        
        # Ensure status is valid
        if "status" not in search_data or search_data["status"] not in ["processing", "completed", "failed"]:
            # Determine status based on other fields
            if search_data.get("error"):
                search_data["status"] = "failed"
            elif search_data.get("completed_at"):
                search_data["status"] = "completed"
            else:
                search_data["status"] = "processing"
        
        return search_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting search result: {str(e)}")

@app.get("/api/search")
async def list_searches():
    try:
        searches = get_recent_searches_from_database()
        return {"searches": searches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing searches: {str(e)}")

@app.delete("/api/search/{request_id}")
async def delete_search(request_id: str):
    try:
        if not request_id or not isinstance(request_id, str):
            raise HTTPException(status_code=400, detail="Invalid request_id")
            
        delete_search_from_database(request_id)
        return {"message": "Search request deleted from database"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting search: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)