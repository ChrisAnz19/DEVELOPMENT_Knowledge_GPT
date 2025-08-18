from fastapi import FastAPI, HTTPException, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
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
import random
import time
import openai

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
            os.environ['HUBSPOT_CLIENT_ID'] = secrets.get('hubspot_client_id', '') or secrets.get('HUBSPOT_CLIENT_ID', '')
            os.environ['HUBSPOT_CLIENT_SECRET'] = secrets.get('hubspot_client_secret', '') or secrets.get('HUBSPOT_CLIENT_SECRET', '')
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

class DemoSearchGenerator:
    def __init__(self):
        self.search_categories = [
            # Core business searches (70% weight)
            "executive_recruitment", "technology_research", "investment_opportunities", 
            "vendor_evaluation", "market_expansion", "partnership_discovery",
            "talent_acquisition", "competitive_intelligence", "funding_search",
            "customer_acquisition", "solution_research", "merger_acquisition",
            "real_estate_commercial", "startup_discovery", "supplier_sourcing",
            "board_recruitment", "advisory_search", "consultant_discovery",
            "speaker_booking", "expert_witness", "industry_analyst",
            "patent_research", "regulatory_compliance", "sustainability_initiatives",
            "digital_transformation", "crisis_management", "turnaround_specialists",
            "international_expansion", "joint_ventures", "licensing_deals",
            "acquisition_targets", "divestiture_planning", "ipo_preparation",
            "private_equity", "venture_capital", "angel_investors",
            "family_office", "sovereign_wealth", "pension_funds",
            "insurance_companies", "hedge_funds", "asset_management",
            "wealth_management", "investment_banking", "commercial_banking",
            "credit_analysis", "risk_management", "compliance_officers",
            "cybersecurity_experts", "data_scientists", "ai_researchers",
            "blockchain_developers", "quantum_computing", "space_technology",
            "renewable_energy", "clean_technology", "carbon_markets",
            "esg_specialists", "impact_investing", "social_entrepreneurs",
            "nonprofit_leaders", "government_relations", "policy_experts",
            "academic_researchers", "thought_leaders", "innovation_labs",
            # Interesting but realistic searches (20% weight)
            "investment_property", "commercial_property", "land_acquisition",
            "luxury_real_estate", "vacation_property", "relocation_services",
            "talent_scouts", "headhunter_discovery", "recruiter_networks",
            "consultant_sourcing", "advisor_matching", "mentor_programs",
            "coach_discovery", "trainer_sourcing", "speaker_networks",
            "event_planning", "wedding_services", "catering_services",
            "personal_services", "concierge_services", "lifestyle_management",
            "wealth_services", "family_office_services", "private_banking",
            "estate_planning", "tax_optimization", "legal_services",
            "security_services", "investigation_services", "due_diligence",
            # Unique/weird but plausible searches (10% weight)
            "art_investment", "wine_investment", "collectibles_market",
            "luxury_goods", "high_end_services", "exclusive_networks",
            "citizenship_services", "residency_planning", "international_tax",
            "reputation_services", "crisis_communications", "media_relations"
        ]
        
        self.industry_contexts = [
            # Common, broad industries (70%)
            "technology", "healthcare", "finance", "manufacturing", "retail", "consulting",
            "real estate", "media", "automotive", "energy", "telecommunications", "aerospace",
            "logistics", "construction", "agriculture", "biotechnology", "gaming",
            "pharmaceuticals", "food & beverage", "hospitality", "entertainment", "sports",
            "education", "government", "nonprofit", "legal", "accounting", "insurance",
            "banking", "investment", "private equity", "venture capital", "hedge funds",
            
            # More specific but recognizable (20%)
            "saas", "fintech", "healthtech", "edtech", "e-commerce", "cybersecurity",
            "artificial intelligence", "blockchain", "renewable energy", "electric vehicles",
            "medical devices", "biotech", "pharmaceuticals", "digital marketing",
            "cloud computing", "data analytics", "mobile apps", "social media",
            "streaming", "podcasting", "influencer marketing", "supply chain",
            
            # Interesting/niche but understandable (10%)
            "luxury goods", "private aviation", "yacht industry", "art market", "wine industry",
            "collectibles", "antiques", "jewelry", "fashion", "beauty", "fitness",
            "travel", "tourism", "event planning", "wedding industry", "pet services",
            "elder care", "childcare", "personal services", "concierge services",
            "executive search", "talent acquisition", "management consulting", "executive coaching"
        ]
        
        self.geographic_regions = [
            "New York", "San Francisco", "Los Angeles", "Chicago", "Boston", "Austin",
            "Seattle", "Miami", "Denver", "Atlanta", "Dallas", "Philadelphia",
            "Washington DC", "San Diego", "Phoenix", "Las Vegas", "Portland", "Nashville",
            "Silicon Valley", "Research Triangle", "Detroit", "Houston", "Minneapolis",
            "Charlotte", "Tampa", "Orlando", "Jacksonville", "Kansas City", "St. Louis",
            "Cincinnati", "Cleveland", "Columbus", "Indianapolis", "Milwaukee", "Pittsburgh",
            "Baltimore", "Richmond", "Norfolk", "Raleigh", "Charleston", "Savannah",
            "New Orleans", "Memphis", "Birmingham", "Louisville", "Nashville", "Knoxville",
            "Oklahoma City", "Tulsa", "Little Rock", "Jackson", "Mobile", "Huntsville",
            "Baton Rouge", "Shreveport", "Lafayette", "Lake Charles", "Beaumont", "Tyler",
            "Waco", "Corpus Christi", "McAllen", "Brownsville", "El Paso", "Lubbock",
            "Amarillo", "Midland", "Odessa", "Abilene", "Wichita Falls", "Longview",
            "Salt Lake City", "Provo", "Ogden", "Park City", "Boise", "Coeur d'Alene",
            "Spokane", "Yakima", "Bellingham", "Olympia", "Tacoma", "Everett",
            "Anchorage", "Fairbanks", "Juneau", "Honolulu", "Hilo", "Kona",
            "Albuquerque", "Santa Fe", "Las Cruces", "Roswell", "Farmington", "Gallup",
            "Flagstaff", "Tucson", "Yuma", "Prescott", "Sedona", "Scottsdale",
            "Reno", "Carson City", "Henderson", "North Las Vegas", "Boulder City",
            "Sacramento", "Fresno", "Bakersfield", "Stockton", "Modesto", "Salinas",
            "Santa Barbara", "Ventura", "Oxnard", "Thousand Oaks", "Simi Valley",
            "Riverside", "San Bernardino", "Palm Springs", "Indio", "Coachella Valley",
            "Orange County", "Irvine", "Anaheim", "Santa Ana", "Huntington Beach",
            "Long Beach", "Pasadena", "Glendale", "Burbank", "Santa Monica",
            "Beverly Hills", "West Hollywood", "Culver City", "Manhattan Beach"
        ]
        
        self.search_styles = [
            "casual", "formal", "urgent", "analytical", "conversational", "direct",
            "enthusiastic", "cautious", "strategic", "tactical", "visionary", "pragmatic",
            "collaborative", "decisive", "exploratory", "focused", "broad", "specific",
            "innovative", "traditional", "disruptive", "conservative", "aggressive", "passive"
        ]
        
        self.job_titles = [
            # C-Suite and senior executives (40%)
            "CEO", "COO", "CFO", "CTO", "CIO", "CMO", "President", "Vice President", 
            "Managing Director", "General Manager", "Director", "Senior Director",
            
            # Department heads and managers (30%)
            "Sales Director", "Marketing Director", "Operations Manager", "Finance Director",
            "HR Director", "IT Director", "Product Manager", "Engineering Manager",
            "Business Development Manager", "Account Manager", "Project Manager",
            
            # Specialized roles (20%)
            "Founder", "Partner", "Investment Manager", "Consultant", "Analyst",
            "Software Engineer", "Data Scientist", "Sales Rep", "Account Executive",
            "Marketing Manager", "Operations Director", "Strategy Manager",
            
            # Unique but understandable roles (10%)
            "Board Member", "Angel Investor", "Venture Partner", "Fund Manager",
            "Research Director", "Innovation Manager", "Chief Scientist", "Principal",
            "Practice Leader", "Portfolio Manager", "Investment Director", "Head of Growth"
        ]
        
        self.company_sizes = [
            "startup", "early-stage", "growth-stage", "mid-market", "enterprise", "Fortune 500",
            "Fortune 100", "unicorn", "decacorn", "public company", "private company",
            "family-owned", "PE-backed", "VC-funded", "bootstrapped", "Series A", "Series B",
            "Series C", "pre-IPO", "post-IPO", "SPAC", "emerging growth", "scale-up"
        ]
        
        self.behavioral_signals = [
            # Core business behaviors (80% weight)
            "researching", "evaluating", "comparing", "piloting", "implementing", "upgrading",
            "expanding", "scaling", "hiring", "fundraising", "acquiring", "divesting",
            "relocating", "opening offices", "closing facilities", "restructuring", "pivoting",
            "launching products", "entering markets", "forming partnerships", "seeking advisors",
            "attending conferences", "speaking at events", "publishing research", "filing patents",
            "regulatory compliance", "digital transformation", "cloud migration", "automation",
            "sustainability initiatives", "esg reporting", "diversity programs", "remote work",
            "hybrid work", "return to office", "cost reduction", "efficiency improvements",
            "customer acquisition", "market expansion", "competitive analysis", "benchmarking",
            "due diligence", "risk assessment", "scenario planning", "strategic planning",
            "vendor selection", "contract negotiation", "budget planning", "team building",
            "process optimization", "quality improvement", "innovation initiatives", "r&d investment",
            "market research", "customer feedback", "product development", "go-to-market",
            "sales enablement", "marketing campaigns", "brand building", "thought leadership",
            "investor relations", "board reporting", "stakeholder management", "crisis planning",
            # Interesting but realistic behaviors (15% weight)
            "office space hunting", "real estate scouting", "relocation planning", "expansion scouting",
            "talent poaching", "competitor monitoring", "industry networking", "conference speaking",
            "award submissions", "media interviews", "podcast appearances", "webinar hosting",
            "advisory board building", "mentor seeking", "coach hiring", "consultant sourcing",
            "investment exploring", "acquisition hunting", "partnership building", "deal sourcing",
            # Unique but plausible behaviors (5% weight)
            "luxury asset research", "investment diversification", "wealth preservation", "tax optimization",
            "citizenship exploring", "residency planning", "international expansion", "global mobility",
            "reputation monitoring", "crisis preparation", "succession planning", "legacy building"
        ]

    def generate_search_example(self) -> Dict[str, Any]:
        """Generate a realistic search example using AI"""
        
        category = random.choice(self.search_categories)
        industry = random.choice(self.industry_contexts)
        location = random.choice(self.geographic_regions)
        style = random.choice(self.search_styles)
        job_title = random.choice(self.job_titles)
        company_size = random.choice(self.company_sizes)
        behavioral_signal = random.choice(self.behavioral_signals)
        
        # Simple context for the AI prompt - no variable substitutions
        base_prompt = "Generate a professional B2B search query"
        
        prompt = f"""Generate a simple, clear B2B search query. Use this exact format:

"Find [JOB TITLE] who are [LOOKING FOR SOMETHING]"

Examples:
- "Find CFOs who are looking for accounting software"
- "Find marketing directors who are evaluating CRM systems"
- "Find IT managers who need cybersecurity solutions"
- "Find sales VPs who are hiring new reps"
- "Find CEOs who are seeking investors"
- "Find HR directors who need recruiting tools"
- "Find operations managers who are optimizing workflows"
- "Find CTOs who are planning cloud migrations"

Writing style: {style}

Generate 1 search query using the exact format above. Keep it simple and logical. Return only the search query text."""

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.8
            )
            
            search_query = response.choices[0].message.content.strip()
            
            # Remove quotes if present
            if search_query.startswith('"') and search_query.endswith('"'):
                search_query = search_query[1:-1]
                
            return {
                "search_query": search_query,
                "category": category,
                "industry": industry,
                "location": location,
                "style": style,
                "timestamp": datetime.now().isoformat(),
                "use_case_type": self._determine_use_case_type(category),
                "refresh_interval": 5
            }
            
        except Exception as e:
            # Fallback to predefined examples if AI fails
            return self._get_fallback_search(category, industry, location)
    
    def _determine_use_case_type(self, category: str) -> str:
        """Determine the type of use case based on category"""
        use_case_mapping = {
            "executive_recruitment": "Talent Acquisition",
            "technology_research": "Technology Evaluation",
            "investment_opportunities": "Investment & Funding",
            "vendor_evaluation": "Procurement & Sourcing",
            "market_expansion": "Strategic Planning",
            "partnership_discovery": "Business Development",
            "talent_acquisition": "HR & Recruiting",
            "competitive_intelligence": "Market Research",
            "funding_search": "Investment & Funding",
            "customer_acquisition": "Sales & Marketing",
            "solution_research": "Technology Evaluation",
            "merger_acquisition": "Investment & M&A",
            "real_estate_commercial": "Commercial Real Estate",
            "startup_discovery": "Investment & Funding",
            "supplier_sourcing": "Procurement & Sourcing"
        }
        return use_case_mapping.get(category, "Business Intelligence")
    
    def _get_fallback_search(self, category: str, industry: str, location: str) -> Dict[str, Any]:
        """Fallback search examples if AI generation fails"""
        
        # Hand-crafted realistic search examples
        fallback_queries = [
            # Simple, common searches
            "Find CEOs in New York",
            "Looking for technology executives",
            "Need CFOs who are hiring",
            "Find executives at companies that are expanding",
            "Looking for decision makers in healthcare",
            "Need executives who are fundraising",
            "Find CTOs considering new solutions",
            "Looking for fintech leaders",
            "Need executives at companies in San Francisco",
            "Find executives who are relocating",
            
            # Sales and business development
            "Find decision makers at SaaS companies evaluating CRM solutions",
            "Looking for healthcare executives who are implementing digital transformation",
            "Need manufacturing leaders considering automation technology",
            "Find retail executives planning e-commerce expansion",
            "Looking for finance directors at companies going through acquisitions",
            "Need IT directors at companies upgrading cybersecurity",
            "Find marketing executives launching new products",
            "Looking for operations managers optimizing supply chains",
            "Need sales directors at companies expanding territories",
            "Find HR leaders implementing remote work policies",
            
            # Investment and finance
            "Find LPs interested in healthcare investments",
            "Looking for investors focused on AI startups",
            "Need accredited investors for real estate funds",
            "Find family offices investing in technology",
            "Looking for pension funds considering alternative investments",
            "Need sovereign wealth funds evaluating infrastructure deals",
            "Find hedge fund managers seeking new strategies",
            "Looking for private equity partners sourcing deals",
            "Need venture capital firms backing fintech startups",
            "Find asset managers building ESG portfolios",
            
            # Professional services - targeting executives
            "Find CEOs needing management consulting",
            "Looking for executives who need legal counsel",
            "Need CFOs evaluating accounting firms",
            "Find CISOs requiring cybersecurity audits",
            "Looking for tax directors planning restructuring",
            "Need executives seeking executive coaching",
            "Find compliance officers requiring consulting",
            "Looking for CTOs needing IT consulting",
            "Need transformation officers planning digital initiatives",
            "Find executives requiring crisis management support",
            
            # Recruitment and talent acquisition
            "Find passive candidates in technology who might consider new roles",
            "Looking for executives open to board positions",
            "Need sales leaders considering career transitions",
            "Find engineers who aren't actively job searching",
            "Looking for marketing directors ready for VP roles",
            "Need finance professionals interested in startup opportunities",
            "Find operations managers seeking remote work options",
            "Looking for consultants interested in in-house roles",
            "Need executives considering relocation to Austin",
            "Find product managers ready for leadership positions",
            
            # More people searches - executives at companies with specific needs
            "Find CTOs at SaaS companies looking for integration partners",
            "Looking for CEOs at startups seeking Series A funding",
            "Need operations directors at manufacturing companies evaluating automation",
            "Find IT directors at healthcare companies implementing AI solutions",
            "Looking for compliance officers at fintech startups needing regulatory help",
            "Need logistics VPs at e-commerce companies seeking fulfillment partners",
            "Find clinical directors at biotech companies preparing for trials",
            "Looking for expansion managers at real estate companies entering new markets",
            "Need partnership directors at consulting firms seeking technology alliances",
            "Find CTOs at media companies evaluating streaming platforms",
            "Looking for project managers at energy companies investing in renewables",
            "Need e-commerce directors at retail companies launching online stores",
            "Find technology managers at construction companies adopting new systems",
            "Looking for automation directors at logistics companies seeking efficiency",
            "Need fraud directors at insurance companies evaluating detection systems",
            "Find digital transformation officers at banks implementing new technology",
            "Looking for IT directors at hospitals seeking EMR upgrades",
            "Need technology partners at law firms evaluating case management software",
            "Find IT managers at accounting firms seeking cloud solutions",
            "Looking for operations managers at restaurants implementing delivery systems",
            
            # M&A and investment - targeting executives
            "Find CEOs at SaaS companies in Boston considering acquisition",
            "Looking for founders at fintech startups seeking Series B funding",
            "Need business development directors at manufacturing companies exploring partnerships",
            "Find CFOs at healthcare companies preparing for IPO",
            "Looking for CEOs at e-commerce businesses seeking growth capital",
            "Need corporate development VPs at technology companies considering mergers",
            "Find licensing directors at biotech companies seeking deals",
            "Looking for partnership managers at real estate companies exploring joint ventures",
            "Need investment directors at energy companies seeking strategic investors",
            "Find corporate development officers at media companies considering divestiture",
            
            # Partnerships and business development - targeting people
            "Find partnership directors seeking healthcare technology integration",
            "Looking for business development managers seeking European distribution partners",
            "Need alliance managers seeking strategic AI development partners",
            "Find channel managers seeking cybersecurity solution partners",
            "Looking for joint venture directors in renewable energy seeking partners",
            "Need licensing managers seeking pharmaceutical product partners",
            "Find integration managers seeking cloud platform partners",
            "Looking for partnership VPs in financial services seeking reseller partners",
            "Need alliance directors seeking digital transformation partners",
            "Find ecosystem managers seeking blockchain initiative partners",
            
            # Interesting but believable searches
            "Find executives who speak at industry conferences",
            "Looking for leaders who mentor other entrepreneurs",
            "Need CEOs interested in advisory board positions",
            "Find executives who collect contemporary art",
            "Looking for leaders who need executive coaching",
            "Need executives planning office relocations",
            "Find leaders who travel internationally for business",
            "Looking for executives interested in thought leadership",
            "Need leaders who write industry publications",
            "Find executives who host corporate events",
            "Looking for leaders who need wealth management services",
            "Need executives considering succession planning",
            "Find leaders who require security services",
            "Looking for executives facing reputation challenges",
            "Need leaders interested in speaking opportunities",
            "Find executives who need crisis management support",
            "Looking for leaders planning international expansion",
            "Need executives who entertain high-profile clients",
            "Find leaders interested in luxury concierge services",
            "Looking for executives who need personal branding help"
        ]
        
        return {
            "search_query": random.choice(fallback_queries),
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "use_case_type": self._determine_use_case_type(category),
            "refresh_interval": 5,
            "source": "fallback"
        }

# Initialize the demo generator
demo_generator = DemoSearchGenerator()

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

def validate_hubspot_credentials():
    """Validate that required HubSpot OAuth credentials are present"""
    client_id = os.getenv('HUBSPOT_CLIENT_ID')
    client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
    
    if not client_id:
        raise ValueError("HUBSPOT_CLIENT_ID environment variable is required but not set")
    if not client_secret:
        raise ValueError("HUBSPOT_CLIENT_SECRET environment variable is required but not set")
    
    print(f"HubSpot OAuth credentials loaded successfully")

# Validate HubSpot credentials on startup (non-blocking)
try:
    validate_hubspot_credentials()
except ValueError as e:
    print(f"Warning: {e}")
    print("HubSpot OAuth functionality will not be available until credentials are configured")

class HubSpotOAuthClient:
    """Client for handling HubSpot OAuth token exchange"""
    
    def __init__(self):
        self.client_id = os.getenv('HUBSPOT_CLIENT_ID')
        self.client_secret = os.getenv('HUBSPOT_CLIENT_SECRET')
        self.token_url = "https://api.hubapi.com/oauth/v1/token"
        
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        if not self.client_id or not self.client_secret:
            raise ValueError("HubSpot credentials not configured")
            
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "code": code
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.token_url,
                    data=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print(f"HubSpot response status: 200")
                    print(f"HubSpot response headers: {dict(response.headers)}")
                    print(f"HubSpot response text: {response.text}")
                    print(f"HubSpot response text length: {len(response.text)}")
                    
                    try:
                        json_data = response.json()
                        print(f"Successfully parsed JSON: {json_data}")
                        
                        # Validate that we got the expected token data
                        if not json_data or not isinstance(json_data, dict):
                            print(f"Invalid token data structure: {json_data}")
                            raise HTTPException(
                                status_code=502,
                                detail={
                                    "error": "invalid_response",
                                    "error_description": "HubSpot returned invalid token data structure",
                                    "status_code": 502
                                }
                            )
                        
                        return json_data
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        print(f"Response content: {repr(response.text)}")
                        raise HTTPException(
                            status_code=502,
                            detail={
                                "error": "invalid_response",
                                "error_description": "HubSpot returned an invalid response format",
                                "status_code": 502
                            }
                        )
                elif response.status_code == 429:
                    # Rate limiting
                    retry_after = response.headers.get('Retry-After', '60')
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "rate_limit_exceeded",
                            "error_description": "Rate limit exceeded. Please try again later.",
                            "retry_after": retry_after,
                            "status_code": 429
                        }
                    )
                elif response.status_code >= 500:
                    # HubSpot server errors
                    raise HTTPException(
                        status_code=503,
                        detail={
                            "error": "hubspot_unavailable",
                            "error_description": "HubSpot API is temporarily unavailable. Please try again later.",
                            "status_code": 503
                        }
                    )
                else:
                    # Handle HubSpot OAuth errors
                    print(f"HubSpot error response status: {response.status_code}")
                    print(f"HubSpot error response headers: {dict(response.headers)}")
                    print(f"HubSpot error response text: {response.text}")
                    print(f"HubSpot error response text length: {len(response.text)}")
                    
                    try:
                        error_data = response.json()
                        print(f"Successfully parsed error JSON: {error_data}")
                        raise HTTPException(
                            status_code=self._map_hubspot_error_to_http_status(error_data.get('error', 'unknown_error')),
                            detail={
                                "error": error_data.get('error', 'unknown_error'),
                                "error_description": error_data.get('error_description', 'Unknown error occurred'),
                                "status_code": response.status_code
                            }
                        )
                    except json.JSONDecodeError as e:
                        print(f"Error JSON decode error: {e}")
                        print(f"Error response content: {repr(response.text)}")
                        # If response is not JSON, create generic error
                        raise HTTPException(
                            status_code=502,
                            detail={
                                "error": "invalid_response",
                                "error_description": f"HubSpot returned an invalid response format (status {response.status_code})",
                                "status_code": 502
                            }
                        )
                        
        except httpx.TimeoutException:
            # Network timeout
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "request_timeout",
                    "error_description": "Request to HubSpot API timed out. Please try again.",
                    "status_code": 504
                }
            )
        except httpx.NetworkError:
            # Network connectivity issues
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "network_error",
                    "error_description": "Unable to connect to HubSpot API. Please try again later.",
                    "status_code": 503
                }
            )
        except Exception as e:
            # Catch any other unexpected errors
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "internal_server_error",
                    "error_description": "An unexpected error occurred during token exchange.",
                    "status_code": 500
                }
            )
    
    def _map_hubspot_error_to_http_status(self, hubspot_error: str) -> int:
        """Map HubSpot OAuth errors to appropriate HTTP status codes"""
        error_mapping = {
            "invalid_grant": 400,
            "invalid_client": 500,
            "invalid_request": 422,
            "unsupported_grant_type": 422,
            "unauthorized_client": 500,
            "access_denied": 403
        }
        return error_mapping.get(hubspot_error, 500)

# Initialize HubSpot OAuth client
hubspot_oauth_client = HubSpotOAuthClient()

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

class DemoSearchResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str

# HubSpot OAuth Models
class HubSpotOAuthRequest(BaseModel):
    code: str = Field(..., description="Authorization code from HubSpot", min_length=1, max_length=512)
    redirect_uri: str = Field(..., description="Redirect URI used in OAuth flow")
    
    @validator('code')
    def sanitize_code(cls, v):
        if not v or not v.strip():
            raise ValueError('Authorization code cannot be empty')
        # Remove any potential XSS characters
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        return sanitized
    
    @validator('redirect_uri')
    def validate_redirect_uri(cls, v):
        if not v or not v.strip():
            raise ValueError('Redirect URI cannot be empty')
        # Basic URL validation
        if not re.match(r'^https?://', v):
            raise ValueError('Redirect URI must be a valid HTTP/HTTPS URL')
        # Remove any potential XSS characters
        sanitized = re.sub(r'[<>"\']', '', v.strip())
        return sanitized

class HubSpotOAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"
    scope: Optional[str] = None

class HubSpotOAuthError(BaseModel):
    error: str
    error_description: str
    status_code: int

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

def is_valid_linkedin_photo(photo_url: str) -> bool:
    """
    Validate if a LinkedIn photo URL points to an actual profile photo.
    
    Args:
        photo_url: The LinkedIn profile photo URL to validate
        
    Returns:
        bool: True if valid profile photo, False if fallback image
    """
    if not photo_url or not isinstance(photo_url, str) or not photo_url.strip():
        return False
    
    # Known LinkedIn fallback image patterns
    fallback_patterns = [
        "9c8pery4andzj6ohjkjp54ma2",  # Primary LinkedIn fallback image
        "static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
        "static.licdn.com/scds/common/u/images/themes/katy/ghosts",  # Alternative fallback
        "static.licdn.com/scds/common/u/images/apps/connect/icons/profile_pic_ghost",  # Another fallback
    ]
    
    # Check if URL contains any fallback patterns
    photo_url_lower = photo_url.lower().strip()
    for pattern in fallback_patterns:
        if pattern in photo_url_lower:
            return False
    
    # Additional checks for valid LinkedIn photo URLs
    if "media.licdn.com" in photo_url_lower and "profile-displayphoto" in photo_url_lower:
        return True
    
    # If it's a LinkedIn URL but doesn't match known patterns, assume it's valid
    if "licdn.com" in photo_url_lower:
        return True
    
    # Non-LinkedIn URLs are considered valid (could be from other sources)
    return True

def validate_candidate_photos(candidates: List[Dict]) -> List[Dict]:
    """
    Validate photos for a list of candidates and mark photo status.
    
    Args:
        candidates: List of candidate dictionaries with photo URLs
        
    Returns:
        List[Dict]: Candidates with photo validation status added
    """
    if not candidates:
        return candidates
    
    validated_candidates = []
    
    for candidate in candidates:
        if not isinstance(candidate, dict):
            validated_candidates.append(candidate)
            continue
        
        # Extract photo URL from candidate
        photo_url = candidate.get("profile_photo_url") or candidate.get("profile_pic_url") or candidate.get("photo_url")
        
        # Validate photo
        is_valid = is_valid_linkedin_photo(photo_url)
        
        # Add photo validation status to candidate
        candidate["photo_validation"] = {
            "photo_url": photo_url,
            "is_valid_photo": is_valid,
            "photo_validation_reason": _get_photo_validation_reason(photo_url, is_valid),
            "photo_source": _get_photo_source(photo_url)
        }
        
        # Add selection priority (higher for valid photos)
        candidate["selection_priority"] = 10 if is_valid else 1
        
        validated_candidates.append(candidate)
    
    return validated_candidates

def _get_photo_validation_reason(photo_url: str, is_valid: bool) -> str:
    """Get human-readable reason for photo validation result."""
    if not photo_url:
        return "no_url"
    
    if not is_valid:
        if "9c8pery4andzj6ohjkjp54ma2" in photo_url.lower():
            return "fallback_image"
        else:
            return "invalid_pattern"
    
    return "valid"

def _get_photo_source(photo_url: str) -> str:
    """Determine the source of the photo URL."""
    if not photo_url:
        return "none"
    
    if "licdn.com" in photo_url.lower():
        return "linkedin"
    
    return "other"

async def process_search(request_id: str, prompt: str, max_candidates: int = 3, include_linkedin: bool = True):
    is_completed = False
    MAX_ATTEMPTS = 5
    try:
        search_data = get_search_from_database(request_id)
        if not search_data or search_data.get("status") == "completed":
            return

        def preprocess_prompt(prompt_text: str) -> str:
            generic_terms = [
                "people", "persons", "person", "anyone", "somebody", "someone",
                "individuals", "individual", "professionals", "professional",
                "contacts", "contact", "leads", "lead"
            ]
            processed_prompt = prompt_text
            for term in generic_terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, processed_prompt, re.IGNORECASE):
                    processed_prompt = re.sub(pattern, 'executives', processed_prompt, flags=re.IGNORECASE)
                    print(f"[Prompt Processing] Converted '{term}' to 'executives' in search query")
            return processed_prompt

        preprocessed_prompt = preprocess_prompt(prompt)
        try:
            enhanced_prompt, analysis = enhance_prompt(preprocessed_prompt)
            if analysis.reasoning:
                print(f"Smart prompt enhancement applied: {', '.join(analysis.reasoning)}")
        except Exception as e:
            enhanced_prompt = preprocessed_prompt
            print(f"Smart prompt enhancement failed, using preprocessed prompt: {str(e)}")

        filters = parse_prompt_to_internal_database_filters(enhanced_prompt)

        attempt = 0
        page = 1
        candidates = []
        while attempt < MAX_ATTEMPTS and len(candidates) < max_candidates:
            attempt += 1
            print(f"[RETRY] Attempt {attempt} (page {page}) to find at least {max_candidates} valid candidates.")
            try:
                search_per_page = max_candidates + 6
                people = await asyncio.wait_for(
                    search_people_via_internal_database(filters, page=page, per_page=search_per_page),
                    timeout=60
                )
            except (asyncio.TimeoutError, Exception) as e:
                search_data["status"] = "failed"
                search_data["error"] = str(e)
                search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
                store_search_to_database(search_data)
                return

            if not people:
                print(f"[RETRY] No people found on page {page}.")
                page += 1
                continue

            # Filter out non-US locations and known public figures via Wikipedia
            filtered_people = []
            for p in people:
                if not isinstance(p, dict):
                    continue
                loc = (p.get("location") or p.get("country") or "").lower()
                if loc:
                    non_us_locations = [
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
                        "london", "paris", "berlin", "madrid", "rome", "amsterdam", "brussels",
                        "zurich", "vienna", "stockholm", "oslo", "copenhagen", "helsinki",
                        "toronto", "vancouver", "montreal", "sydney", "melbourne", "tokyo",
                        "seoul", "beijing", "shanghai", "hong kong", "mumbai", "delhi", "bangalore"
                    ]
                    is_non_us = any(non_us in loc for non_us in non_us_locations)
                    if is_non_us:
                        continue
                name_val = (p.get("name") or "").strip()
                if name_val and await is_public_figure(name_val):
                    continue
                filtered_people.append(p)
            people = filtered_people

            try:
                if people:
                    print(f"[DEBUG] Input people count: {len(people)}")
                    top_basic = select_top_candidates(prompt, people)
                    print(f"[DEBUG] select_top_candidates returned: {len(top_basic) if top_basic else 0} candidates")
                    merged_candidates = []
                    seen_identifiers = set()
                    if top_basic and isinstance(top_basic, list):
                        for basic in top_basic:
                            identifier = None
                            if basic.get("linkedin_url"):
                                identifier = basic.get("linkedin_url")
                            elif basic.get("email"):
                                identifier = basic.get("email")
                            elif basic.get("name"):
                                identifier = basic.get("name")
                            if identifier and identifier in seen_identifiers:
                                continue
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
                                merged.update(match)
                            merged_candidates.append(merged)
                            if identifier:
                                seen_identifiers.add(identifier)
                    candidates.extend([c for c in merged_candidates if c not in candidates])
                    # Only keep up to max_candidates
                    if len(candidates) >= max_candidates:
                        candidates = candidates[:max_candidates]
                        break
            except Exception as e:
                print(f"[RETRY] Error during candidate selection/merging: {e}")
            page += 1

        if not candidates:
            print(f"[RETRY] No valid candidates found after {MAX_ATTEMPTS} attempts.")
            search_data["status"] = "completed"
            search_data["filters"] = json.dumps(filters)
            search_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            store_search_to_database(search_data)
            return

        # Validate photos for all candidates before processing
        candidates = validate_candidate_photos(candidates)
        for candidate in candidates:
            if isinstance(candidate, dict):
                if candidate.get("profile_pic_url"):
                    candidate["profile_photo_url"] = candidate["profile_pic_url"]
                if not candidate.get("company") or candidate.get("company") == "Unknown":
                    if "organization" in candidate:
                        org = candidate["organization"]
                        if isinstance(org, dict) and org.get("name"):
                            candidate["company"] = org["name"]
                        elif isinstance(org, str) and org.strip():
                            candidate["company"] = org
                linkedin_url = candidate.get("linkedin_url")
                if linkedin_url and not linkedin_url.startswith("http"):
                    candidate["linkedin_url"] = f"https://{linkedin_url}"
        try:
            from behavioral_metrics_ai import enhance_behavioral_data_for_multiple_candidates
            used_insights = set()
            used_patterns = set()
            candidates = enhance_behavioral_data_for_multiple_candidates(candidates, prompt)
            for i, candidate in enumerate(candidates):
                if isinstance(candidate, dict) and "behavioral_data" in candidate:
                    insight = candidate["behavioral_data"].get("behavioral_insight", "")
                    from openai_utils import validate_response_uniqueness
                    if insight in used_insights or len(validate_response_uniqueness([insight] + list(used_insights), 0.5)) <= len(used_insights):
                        from behavioral_metrics_ai import generate_diverse_fallback_insight, add_score_variation
                        title = candidate.get('title', 'professional')
                        new_insight = generate_diverse_fallback_insight(title, candidate, prompt, used_patterns, i + 100)
                        candidate["behavioral_data"]["behavioral_insight"] = new_insight
                        used_patterns.add(new_insight)
                    used_insights.add(candidate["behavioral_data"].get("behavioral_insight", ""))
        except Exception as e:
            used_patterns = set()
            for i, candidate in enumerate(candidates):
                if isinstance(candidate, dict):
                    try:
                        is_top_candidate = i < 3
                        candidate_behavioral_data = enhance_behavioral_data_ai({}, [candidate], prompt, candidate_index=i, is_top_candidate=is_top_candidate)
                        candidate["behavioral_data"] = candidate_behavioral_data
                    except Exception:
                        from behavioral_metrics_ai import generate_diverse_fallback_insight, generate_top_lead_scores, add_score_variation, generate_fallback_cmi_score, generate_fallback_rbfs_score, generate_fallback_ias_score
                        title = candidate.get('title', 'professional')
                        fallback_insight = generate_diverse_fallback_insight(title, candidate, prompt, used_patterns, i)
                        used_patterns.add(fallback_insight)
                        base_scores = {
                            "cmi": generate_fallback_cmi_score(title, prompt, i),
                            "rbfs": generate_fallback_rbfs_score(title, prompt, i),
                            "ias": generate_fallback_ias_score(title, prompt, i)
                        }
                        if i < 3:
                            varied_scores = generate_top_lead_scores(base_scores, i, prompt)
                        else:
                            varied_scores = add_score_variation(base_scores, i)
                        candidate["behavioral_data"] = {
                            "behavioral_insight": fallback_insight,
                            "scores": varied_scores
                        }
        search_db_id = search_data.get("id")
        print(f"[DEBUG] About to store candidates. search_db_id: {search_db_id}, candidates count: {len(candidates) if candidates else 0}")
        if candidates:
            print(f"[DEBUG] Candidates list: {[c.get('name', 'Unknown') for c in candidates if isinstance(c, dict)]}")
        if search_db_id and candidates:
            print(f"[DEBUG] Calling store_people_to_database with {len(candidates)} candidates")
            try:
                result = store_people_to_database(search_db_id, candidates)
                print(f"[DEBUG] store_people_to_database returned: {result}")
            except Exception as e:
                print(f"[DEBUG] Error calling store_people_to_database: {str(e)}")
        else:
            print(f"[DEBUG] Skipping storage - search_db_id: {search_db_id}, candidates: {len(candidates) if candidates else 0}")
        try:
            estimation = estimate_people_count(prompt)
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

@app.get("/api/demo/search-example", response_model=DemoSearchResponse)
async def get_search_example():
    """
    Generate a new AI-powered search example
    
    Returns:
        JSON response with search query and metadata
    """
    try:
        search_example = demo_generator.generate_search_example()
        
        return DemoSearchResponse(
            success=True,
            data=search_example,
            message="Search example generated successfully"
        )
        
    except Exception as e:
        return DemoSearchResponse(
            success=False,
            data=None,
            message=f"Failed to generate search example: {str(e)}"
        )

@app.get("/api/demo/search-stream")
async def get_search_stream(count: int = 5):
    """
    Get multiple search examples for continuous demo
    
    Query Parameters:
        count (int): Number of examples to generate (default: 5, max: 20)
    
    Returns:
        JSON response with array of search examples
    """
    try:
        count = min(count, 20)
        
        search_examples = []
        for _ in range(count):
            example = demo_generator.generate_search_example()
            search_examples.append(example)
            # Small delay to ensure different timestamps
            await asyncio.sleep(0.1)
        
        return {
            "success": True,
            "data": {
                "examples": search_examples,
                "total_count": len(search_examples),
                "generated_at": datetime.now().isoformat()
            },
            "message": f"Generated {len(search_examples)} search examples"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate search stream"
        }

@app.get("/api/demo/categories")
async def get_demo_categories():
    """
    Get available demo categories and contexts
    
    Returns:
        JSON response with available categories, industries, and locations
    """
    return {
        "success": True,
        "data": {
            "categories": demo_generator.search_categories,
            "industries": demo_generator.industry_contexts,
            "locations": demo_generator.geographic_regions
        },
        "message": "Demo categories retrieved successfully"
    }

@app.get("/api/hubspot/oauth/health")
async def hubspot_oauth_health():
    """Health check for HubSpot OAuth configuration"""
    client_id_configured = bool(os.getenv('HUBSPOT_CLIENT_ID'))
    client_secret_configured = bool(os.getenv('HUBSPOT_CLIENT_SECRET'))
    
    return {
        "status": "ok",
        "hubspot_oauth_configured": client_id_configured and client_secret_configured,
        "client_id_configured": client_id_configured,
        "client_secret_configured": client_secret_configured
    }

@app.get("/api/hubspot/oauth/debug")
async def hubspot_oauth_debug():
    """Debug endpoint to help diagnose deployment issues"""
    import inspect
    
    # Get all routes from the FastAPI app
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, 'name', 'unknown')
            })
    
    # Filter for HubSpot OAuth related routes
    oauth_routes = [r for r in routes if 'hubspot' in r['path'].lower() and 'oauth' in r['path'].lower()]
    
    return {
        "status": "debug_info",
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "hubspot_client_id_configured": bool(os.getenv('HUBSPOT_CLIENT_ID')),
            "hubspot_client_secret_configured": bool(os.getenv('HUBSPOT_CLIENT_SECRET')),
            "client_id_length": len(os.getenv('HUBSPOT_CLIENT_ID', '')) if os.getenv('HUBSPOT_CLIENT_ID') else 0,
            "client_secret_length": len(os.getenv('HUBSPOT_CLIENT_SECRET', '')) if os.getenv('HUBSPOT_CLIENT_SECRET') else 0
        },
        "hubspot_oauth_routes": oauth_routes,
        "all_api_routes": [r for r in routes if r['path'].startswith('/api/')],
        "total_routes": len(routes),
        "server_info": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "fastapi_available": True
        }
    }

@app.post("/api/hubspot/oauth/test")
async def test_oauth_endpoint():
    """Test endpoint to verify JSON response format"""
    return {
        "test": "success",
        "message": "This endpoint returns valid JSON",
        "timestamp": datetime.now().isoformat(),
        "version": "updated_with_json_fixes",
        "hubspot_configured": bool(os.getenv('HUBSPOT_CLIENT_ID') and os.getenv('HUBSPOT_CLIENT_SECRET'))
    }

@app.post("/api/hubspot/oauth/token")
async def exchange_hubspot_oauth_token(request: HubSpotOAuthRequest):
    """
    Exchange HubSpot authorization code for access and refresh tokens
    """
    try:
        print(f"=== HubSpot OAuth Request Started ===")
        print(f"Request code: {request.code[:10]}...")
        print(f"Request redirect_uri: {request.redirect_uri}")
        print(f"Client ID configured: {bool(hubspot_oauth_client.client_id)}")
        print(f"Client Secret configured: {bool(hubspot_oauth_client.client_secret)}")
        
        # Check if credentials are configured
        if not hubspot_oauth_client.client_id or not hubspot_oauth_client.client_secret:
            print("❌ HubSpot credentials not configured")
            error_response = {
                "error": "configuration_error",
                "error_description": "HubSpot OAuth credentials are not configured",
                "status_code": 500
            }
            print(f"Returning error: {error_response}")
            raise HTTPException(status_code=500, detail=error_response)
        
        # Exchange code for tokens using the OAuth client
        token_data = await hubspot_oauth_client.exchange_code_for_tokens(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        print("HubSpot token exchange successful")
        print(f"Token data received: {token_data}")
        
        # Validate token data
        if not token_data or not isinstance(token_data, dict):
            print(f"Invalid token data received: {token_data}")
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "invalid_token_response",
                    "error_description": "Invalid token data received from HubSpot",
                    "status_code": 502
                }
            )
        
        # Return the tokens in the expected format
        response_data = {
            "access_token": token_data.get('access_token'),
            "refresh_token": token_data.get('refresh_token'),
            "expires_in": token_data.get('expires_in'),
            "token_type": token_data.get('token_type', 'bearer'),
            "scope": token_data.get('scope')
        }
        
        print(f"Returning response: {response_data}")
        return response_data
        
    except HTTPException as e:
        print(f"HubSpot OAuth HTTPException: {e.detail}")
        # Re-raise HTTP exceptions from the OAuth client
        raise
    except ValueError as e:
        print(f"HubSpot OAuth ValueError: {str(e)}")
        # Handle configuration errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "configuration_error",
                "error_description": str(e),
                "status_code": 500
            }
        )
    except Exception as e:
        print(f"HubSpot OAuth unexpected error: {str(e)}")
        # Handle any other unexpected errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_server_error",
                "error_description": "An unexpected error occurred during token exchange.",
                "status_code": 500
            }
        )

@app.post("/api/search")
async def create_search(request: SearchRequest, background_tasks: BackgroundTasks):
    try:
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Preprocess prompt to convert generic terms to "executives" before validation
        def preprocess_prompt_for_validation(prompt_text: str) -> str:
            """Convert generic people terms to 'executives' for better search results."""
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
            
            return processed_prompt
        
        # Apply preprocessing before validation
        preprocessed_prompt = preprocess_prompt_for_validation(request.prompt.strip())
        
        # Validate prompt for ridiculous or inappropriate content
        prompt_lower = preprocessed_prompt.lower().strip()
        
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

# Prismatic Integration Diagnostic Models
class PrismaticDiagnosticResult(BaseModel):
    timestamp: str
    environment: str
    api_health: Dict[str, Any]
    prismatic_connectivity: Dict[str, Any]
    integration_config: Dict[str, Any]
    deployment_sync: Dict[str, Any]
    recommendations: List[str]
    critical_issues: List[str]

class PrismaticConfigValidator:
    """Validator for Prismatic integration configuration"""
    
    def __init__(self):
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        
    async def validate_webhook_urls(self) -> Dict[str, Any]:
        """Validate webhook URLs are accessible"""
        webhook_endpoints = [
            '/api/hubspot/oauth/token',
            '/api/hubspot/oauth/health',
            '/api/hubspot/oauth/debug',
            '/api/hubspot/oauth/test'
        ]
        
        results = {
            "accessible_endpoints": [],
            "failed_endpoints": [],
            "total_tested": len(webhook_endpoints),
            "response_times": {}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint in webhook_endpoints:
                try:
                    url = f"{self.base_url}{endpoint}"
                    start_time = time.time()
                    
                    # Test GET endpoints
                    if 'health' in endpoint or 'debug' in endpoint:
                        response = await client.get(url)
                    else:
                        # Test POST endpoints with minimal data
                        response = await client.post(url, json={})
                    
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    results["response_times"][endpoint] = round(response_time, 2)
                    
                    # Try to parse response
                    response_data = None
                    try:
                        response_data = response.json()
                    except:
                        response_data = response.text[:100] if response.text else None
                    
                    results["accessible_endpoints"].append({
                        "endpoint": endpoint,
                        "status_code": response.status_code,
                        "accessible": True,
                        "response_time_ms": round(response_time, 2),
                        "response_preview": response_data
                    })
                except Exception as e:
                    results["failed_endpoints"].append({
                        "endpoint": endpoint,
                        "error": str(e),
                        "accessible": False
                    })
        
        return results
    
    async def validate_auth_config(self) -> Dict[str, Any]:
        """Verify authentication configuration"""
        client_id = os.getenv('HUBSPOT_CLIENT_ID', '')
        client_secret = os.getenv('HUBSPOT_CLIENT_SECRET', '')
        
        # Test actual HubSpot OAuth client initialization
        auth_test_result = {
            "hubspot_client_id_configured": bool(client_id),
            "hubspot_client_secret_configured": bool(client_secret),
            "client_id_length": len(client_id),
            "client_secret_length": len(client_secret),
            "oauth_client_initializable": False,
            "hubspot_token_url_reachable": False
        }
        
        # Test if OAuth client can be initialized
        try:
            test_client = HubSpotOAuthClient()
            auth_test_result["oauth_client_initializable"] = True
        except Exception as e:
            auth_test_result["oauth_client_init_error"] = str(e)
        
        # Test if HubSpot token URL is reachable
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("https://api.hubapi.com/oauth/v1/token")
                # We expect a 405 (Method Not Allowed) since we're using GET instead of POST
                auth_test_result["hubspot_token_url_reachable"] = response.status_code in [405, 400, 401]
                auth_test_result["hubspot_api_status"] = response.status_code
        except Exception as e:
            auth_test_result["hubspot_api_error"] = str(e)
        
        return auth_test_result
    
    async def validate_triggers(self) -> Dict[str, Any]:
        """Check trigger conditions and events"""
        trigger_validation = {
            "oauth_flow_configured": True,
            "webhook_triggers_available": True,
            "error_handling_configured": True,
            "required_endpoints_available": [],
            "missing_endpoints": []
        }
        
        # Check if all required OAuth endpoints are available
        required_endpoints = [
            '/api/hubspot/oauth/token',
            '/api/hubspot/oauth/health'
        ]
        
        webhook_results = await self.validate_webhook_urls()
        accessible_paths = [ep["endpoint"] for ep in webhook_results["accessible_endpoints"]]
        
        for endpoint in required_endpoints:
            if endpoint in accessible_paths:
                trigger_validation["required_endpoints_available"].append(endpoint)
            else:
                trigger_validation["missing_endpoints"].append(endpoint)
        
        trigger_validation["all_required_endpoints_available"] = len(trigger_validation["missing_endpoints"]) == 0
        
        return trigger_validation
    
    async def test_prismatic_connectivity(self) -> Dict[str, Any]:
        """Test connectivity from Prismatic's perspective"""
        connectivity_test = {
            "external_accessibility": False,
            "cors_configured": False,
            "https_available": False,
            "response_format_valid": False
        }
        
        # Test if the API is externally accessible (simulate Prismatic calling it)
        try:
            # Use the actual deployed URL if available
            test_url = self.base_url
            if "localhost" not in test_url and "127.0.0.1" not in test_url:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{test_url}/api/hubspot/oauth/health")
                    connectivity_test["external_accessibility"] = response.status_code == 200
                    connectivity_test["https_available"] = test_url.startswith("https://")
                    
                    # Check if response format is valid JSON
                    try:
                        response.json()
                        connectivity_test["response_format_valid"] = True
                    except:
                        pass
                        
                    # Check CORS headers
                    cors_headers = response.headers.get("access-control-allow-origin")
                    connectivity_test["cors_configured"] = bool(cors_headers)
                    
        except Exception as e:
            connectivity_test["connectivity_error"] = str(e)
        
        return connectivity_test

@app.get("/api/system/prismatic/diagnostics")
async def prismatic_diagnostics():
    """Comprehensive Prismatic integration diagnostics"""
    try:
        validator = PrismaticConfigValidator()
        
        # Run all diagnostic checks
        webhook_validation = await validator.validate_webhook_urls()
        auth_validation = await validator.validate_auth_config()
        trigger_validation = await validator.validate_triggers()
        
        # Check API health
        api_health = {
            "total_endpoints": len(webhook_validation["accessible_endpoints"]) + len(webhook_validation["failed_endpoints"]),
            "accessible_endpoints": len(webhook_validation["accessible_endpoints"]),
            "failed_endpoints": len(webhook_validation["failed_endpoints"]),
            "health_percentage": (len(webhook_validation["accessible_endpoints"]) / webhook_validation["total_tested"]) * 100 if webhook_validation["total_tested"] > 0 else 0
        }
        
        # Generate recommendations
        recommendations = []
        critical_issues = []
        
        if not auth_validation["hubspot_client_id_configured"]:
            critical_issues.append("HUBSPOT_CLIENT_ID environment variable is not configured")
            recommendations.append("Set HUBSPOT_CLIENT_ID environment variable in production")
            
        if not auth_validation["hubspot_client_secret_configured"]:
            critical_issues.append("HUBSPOT_CLIENT_SECRET environment variable is not configured")
            recommendations.append("Set HUBSPOT_CLIENT_SECRET environment variable in production")
            
        if webhook_validation["failed_endpoints"]:
            critical_issues.append(f"{len(webhook_validation['failed_endpoints'])} webhook endpoints are not accessible")
            recommendations.append("Check deployment status and ensure all endpoints are properly deployed")
            
        if api_health["health_percentage"] < 100:
            recommendations.append("Some API endpoints are failing - check logs for specific errors")
            
        # Check for common Prismatic integration issues
        if not webhook_validation["accessible_endpoints"]:
            critical_issues.append("No webhook endpoints are accessible - Prismatic cannot reach the API")
            recommendations.append("Verify the API is deployed and accessible from external services")
            recommendations.append("Check firewall and network configuration")
            
        # Environment detection
        environment = "production" if "render.com" in os.getenv('API_BASE_URL', '') else "development"
        
        result = PrismaticDiagnosticResult(
            timestamp=datetime.now().isoformat(),
            environment=environment,
            api_health=api_health,
            prismatic_connectivity=webhook_validation,
            integration_config={
                "auth_config": auth_validation,
                "trigger_config": trigger_validation
            },
            deployment_sync={
                "environment_detected": environment,
                "base_url": validator.base_url
            },
            recommendations=recommendations,
            critical_issues=critical_issues
        )
        
        return result.dict()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prismatic diagnostic failed: {str(e)}"
        )

@app.get("/api/system/deployment/sync-check")
async def deployment_sync_check():
    """Check deployment synchronization between environments"""
    try:
        # Get all available routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        # Filter for API routes
        api_routes = [r for r in routes if r['path'].startswith('/api/')]
        hubspot_routes = [r for r in api_routes if 'hubspot' in r['path'].lower()]
        system_routes = [r for r in api_routes if 'system' in r['path'].lower()]
        
        # Environment detection
        environment_info = {
            "detected_environment": "production" if any([
                "render.com" in os.getenv('API_BASE_URL', ''),
                "herokuapp.com" in os.getenv('API_BASE_URL', ''),
                os.getenv('NODE_ENV') == 'production',
                os.getenv('ENVIRONMENT') == 'production'
            ]) else "development",
            "base_url": os.getenv('API_BASE_URL', 'http://localhost:8000'),
            "node_env": os.getenv('NODE_ENV', 'not_set'),
            "environment_var": os.getenv('ENVIRONMENT', 'not_set')
        }
        
        # Critical environment variables check
        critical_env_vars = {
            "HUBSPOT_CLIENT_ID": {
                "configured": bool(os.getenv('HUBSPOT_CLIENT_ID')),
                "length": len(os.getenv('HUBSPOT_CLIENT_ID', ''))
            },
            "HUBSPOT_CLIENT_SECRET": {
                "configured": bool(os.getenv('HUBSPOT_CLIENT_SECRET')),
                "length": len(os.getenv('HUBSPOT_CLIENT_SECRET', ''))
            },
            "OPENAI_API_KEY": {
                "configured": bool(os.getenv('OPENAI_API_KEY')),
                "length": len(os.getenv('OPENAI_API_KEY', ''))
            }
        }
        
        # Deployment health indicators
        deployment_health = {
            "total_routes": len(routes),
            "api_routes": len(api_routes),
            "hubspot_routes": len(hubspot_routes),
            "system_routes": len(system_routes),
            "critical_env_vars_configured": sum(1 for var in critical_env_vars.values() if var["configured"]),
            "total_critical_env_vars": len(critical_env_vars)
        }
        
        # Configuration drift detection
        expected_hubspot_routes = [
            "/api/hubspot/oauth/health",
            "/api/hubspot/oauth/debug", 
            "/api/hubspot/oauth/test",
            "/api/hubspot/oauth/token"
        ]
        
        actual_hubspot_paths = [r["path"] for r in hubspot_routes]
        missing_routes = [route for route in expected_hubspot_routes if route not in actual_hubspot_paths]
        unexpected_routes = [route for route in actual_hubspot_paths if route not in expected_hubspot_routes]
        
        config_drift = {
            "expected_hubspot_routes": expected_hubspot_routes,
            "actual_hubspot_routes": actual_hubspot_paths,
            "missing_routes": missing_routes,
            "unexpected_routes": unexpected_routes,
            "routes_match_expected": len(missing_routes) == 0
        }
        
        # Overall sync status
        sync_issues = []
        if missing_routes:
            sync_issues.append(f"Missing {len(missing_routes)} expected HubSpot routes")
        if not critical_env_vars["HUBSPOT_CLIENT_ID"]["configured"]:
            sync_issues.append("HUBSPOT_CLIENT_ID not configured")
        if not critical_env_vars["HUBSPOT_CLIENT_SECRET"]["configured"]:
            sync_issues.append("HUBSPOT_CLIENT_SECRET not configured")
        
        sync_status = {
            "synchronized": len(sync_issues) == 0,
            "issues": sync_issues,
            "health_score": (
                (deployment_health["critical_env_vars_configured"] / deployment_health["total_critical_env_vars"]) * 0.5 +
                (1.0 if config_drift["routes_match_expected"] else 0.0) * 0.5
            ) * 100
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "environment_info": environment_info,
            "deployment_health": deployment_health,
            "critical_env_vars": critical_env_vars,
            "config_drift": config_drift,
            "sync_status": sync_status,
            "all_routes": api_routes
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment sync check failed: {str(e)}"
        )

@app.get("/api/system/health/comprehensive")
async def comprehensive_health_check():
    """Comprehensive system health including Prismatic integration"""
    try:
        # Get Prismatic diagnostics
        validator = PrismaticConfigValidator()
        prismatic_connectivity = await validator.test_prismatic_connectivity()
        webhook_validation = await validator.validate_webhook_urls()
        auth_validation = await validator.validate_auth_config()
        
        # Get deployment sync status
        sync_check_response = await deployment_sync_check()
        
        # API endpoint health summary
        api_health = {
            "total_endpoints_tested": webhook_validation["total_tested"],
            "accessible_endpoints": len(webhook_validation["accessible_endpoints"]),
            "failed_endpoints": len(webhook_validation["failed_endpoints"]),
            "average_response_time": sum(webhook_validation["response_times"].values()) / len(webhook_validation["response_times"]) if webhook_validation["response_times"] else 0,
            "health_percentage": (len(webhook_validation["accessible_endpoints"]) / webhook_validation["total_tested"]) * 100 if webhook_validation["total_tested"] > 0 else 0
        }
        
        # Performance metrics
        performance_metrics = {
            "response_times": webhook_validation["response_times"],
            "slowest_endpoint": max(webhook_validation["response_times"].items(), key=lambda x: x[1]) if webhook_validation["response_times"] else None,
            "fastest_endpoint": min(webhook_validation["response_times"].items(), key=lambda x: x[1]) if webhook_validation["response_times"] else None
        }
        
        # Error tracking
        error_summary = {
            "failed_endpoints": webhook_validation["failed_endpoints"],
            "auth_errors": [],
            "connectivity_errors": []
        }
        
        if not auth_validation["hubspot_client_id_configured"]:
            error_summary["auth_errors"].append("HUBSPOT_CLIENT_ID not configured")
        if not auth_validation["hubspot_client_secret_configured"]:
            error_summary["auth_errors"].append("HUBSPOT_CLIENT_SECRET not configured")
        if not prismatic_connectivity["external_accessibility"]:
            error_summary["connectivity_errors"].append("API not externally accessible")
        
        # Overall system status
        critical_issues = []
        warnings = []
        
        if api_health["health_percentage"] < 100:
            critical_issues.append(f"Only {api_health['health_percentage']:.0f}% of endpoints are accessible")
        if not auth_validation["hubspot_client_id_configured"] or not auth_validation["hubspot_client_secret_configured"]:
            critical_issues.append("HubSpot OAuth credentials not fully configured")
        if not prismatic_connectivity["external_accessibility"]:
            critical_issues.append("API not accessible from external services (Prismatic cannot reach it)")
        if not prismatic_connectivity["https_available"]:
            warnings.append("HTTPS not enabled (recommended for production)")
        if api_health["average_response_time"] > 1000:
            warnings.append(f"Average response time is high ({api_health['average_response_time']:.0f}ms)")
        
        # System readiness score
        readiness_factors = [
            api_health["health_percentage"] / 100,  # Endpoint accessibility
            1.0 if auth_validation["hubspot_client_id_configured"] and auth_validation["hubspot_client_secret_configured"] else 0.0,  # Auth config
            1.0 if prismatic_connectivity["external_accessibility"] else 0.0,  # External access
            1.0 if prismatic_connectivity["https_available"] else 0.5,  # HTTPS (partial credit)
            1.0 if api_health["average_response_time"] < 1000 else 0.5  # Performance (partial credit)
        ]
        
        overall_readiness = (sum(readiness_factors) / len(readiness_factors)) * 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy" if len(critical_issues) == 0 else "degraded" if len(critical_issues) < 3 else "unhealthy",
            "readiness_score": round(overall_readiness, 1),
            "api_health": api_health,
            "prismatic_connectivity": prismatic_connectivity,
            "performance_metrics": performance_metrics,
            "error_summary": error_summary,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "deployment_sync": {
                "environment": sync_check_response["environment_info"]["detected_environment"],
                "sync_status": sync_check_response["sync_status"],
                "health_score": sync_check_response["sync_status"]["health_score"]
            },
            "recommendations": [
                "Fix critical issues first: " + ", ".join(critical_issues) if critical_issues else "No critical issues found",
                "Address warnings: " + ", ".join(warnings) if warnings else "No warnings",
                "Monitor response times and endpoint availability",
                "Ensure Prismatic integration configuration matches API endpoints"
            ]
        }
        
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error",
            "error": str(e),
            "message": "Health check failed - this indicates a serious system issue"
        }

@app.post("/api/system/webhook/test")
async def test_webhook_simulation():
    """Test webhook endpoints as if called by Prismatic"""
    try:
        # Simulate the exact calls that Prismatic would make
        webhook_tests = [
            {
                "name": "OAuth Health Check",
                "description": "Prismatic checking if OAuth service is available",
                "method": "GET",
                "path": "/api/hubspot/oauth/health",
                "headers": {
                    "User-Agent": "Prismatic-Integration/1.0",
                    "Accept": "application/json"
                }
            },
            {
                "name": "OAuth Token Exchange (Valid Format)",
                "description": "Prismatic attempting token exchange with proper format",
                "method": "POST", 
                "path": "/api/hubspot/oauth/token",
                "headers": {
                    "User-Agent": "Prismatic-Integration/1.0",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "data": {
                    "code": "test_authorization_code_from_prismatic",
                    "redirect_uri": "https://app.prismatic.io/callback/hubspot"
                }
            },
            {
                "name": "OAuth Token Exchange (Invalid Code)",
                "description": "Prismatic with invalid authorization code",
                "method": "POST",
                "path": "/api/hubspot/oauth/token", 
                "headers": {
                    "User-Agent": "Prismatic-Integration/1.0",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "data": {
                    "code": "invalid_code",
                    "redirect_uri": "https://app.prismatic.io/callback/hubspot"
                }
            },
            {
                "name": "OAuth Token Exchange (Missing Data)",
                "description": "Prismatic with malformed request",
                "method": "POST",
                "path": "/api/hubspot/oauth/token",
                "headers": {
                    "User-Agent": "Prismatic-Integration/1.0", 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "data": {}
            }
        ]
        
        test_results = []
        base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            for test in webhook_tests:
                try:
                    url = f"{base_url}{test['path']}"
                    start_time = time.time()
                    
                    if test['method'] == 'GET':
                        response = await client.get(url, headers=test['headers'])
                    else:
                        response = await client.post(url, json=test['data'], headers=test['headers'])
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Try to parse JSON response
                    response_data = None
                    try:
                        response_data = response.json()
                    except:
                        response_data = {"raw_response": response.text[:200]}
                    
                    # Determine if response is appropriate for Prismatic
                    prismatic_compatible = True
                    compatibility_notes = []
                    
                    if response.status_code >= 500:
                        compatibility_notes.append("5xx errors may cause Prismatic integration failures")
                    if response_time > 5000:
                        compatibility_notes.append("Response time > 5s may cause Prismatic timeouts")
                    if not response.headers.get('content-type', '').startswith('application/json'):
                        compatibility_notes.append("Non-JSON response may not be handled properly by Prismatic")
                        prismatic_compatible = False
                    
                    test_results.append({
                        "test_name": test['name'],
                        "description": test['description'],
                        "method": test['method'],
                        "path": test['path'],
                        "status_code": response.status_code,
                        "response_time_ms": round(response_time, 2),
                        "response_data": response_data,
                        "prismatic_compatible": prismatic_compatible,
                        "compatibility_notes": compatibility_notes,
                        "headers_sent": test['headers'],
                        "headers_received": dict(response.headers),
                        "success": True
                    })
                    
                except Exception as e:
                    test_results.append({
                        "test_name": test['name'],
                        "description": test['description'],
                        "method": test['method'],
                        "path": test['path'],
                        "error": str(e),
                        "prismatic_compatible": False,
                        "compatibility_notes": ["Request failed - Prismatic integration will fail"],
                        "success": False
                    })
        
        # Summary analysis
        total_tests = len(test_results)
        successful_tests = sum(1 for t in test_results if t['success'])
        compatible_tests = sum(1 for t in test_results if t.get('prismatic_compatible', False))
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "prismatic_compatible_tests": compatible_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "compatibility_rate": (compatible_tests / total_tests) * 100 if total_tests > 0 else 0,
            "overall_prismatic_readiness": compatible_tests >= total_tests * 0.75  # 75% compatibility threshold
        }
        
        # Recommendations for Prismatic integration
        recommendations = []
        if summary["success_rate"] < 100:
            recommendations.append("Fix failing endpoints before configuring Prismatic integration")
        if summary["compatibility_rate"] < 75:
            recommendations.append("Address compatibility issues to ensure reliable Prismatic integration")
        if any(t.get('response_time_ms', 0) > 3000 for t in test_results if t['success']):
            recommendations.append("Optimize response times to prevent Prismatic timeouts")
        if summary["overall_prismatic_readiness"]:
            recommendations.append("API appears ready for Prismatic integration - check Prismatic configuration")
        else:
            recommendations.append("API needs fixes before Prismatic integration will work reliably")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "test_results": test_results,
            "recommendations": recommendations,
            "next_steps": [
                "Review failed tests and fix underlying issues",
                "Verify Prismatic webhook URLs match these endpoint paths",
                "Ensure Prismatic authentication headers are configured correctly",
                "Test actual Prismatic integration after fixing any issues"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook simulation test failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)