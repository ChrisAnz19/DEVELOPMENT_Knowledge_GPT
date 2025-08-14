"""
Optimized Behavioral Metrics AI Module

This module provides AI-powered behavioral metrics for analyzing prospect behavior:
- Commitment Momentum Index (CMI)
- Risk-Barrier Focus Score (RBFS)
- Identity Alignment Signal (IAS)
"""

import logging
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import os

# Configure logging - SIMPLIFIED
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger(__name__)

# Try to import OpenAI, but make it optional
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("AI package not available. AI-based metrics will be disabled.")

# Initialize OpenAI client
try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        # Try to load from secrets.json
        try:
            with open("secrets.json", "r") as f:
                secrets = json.load(f)
                openai_api_key = secrets.get('openai_api_key', '')
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    openai_client = openai.OpenAI(api_key=openai_api_key)
except Exception:
    openai_client = None

def extract_first_name(full_name: str) -> str:
    """Extract first name from full name."""
    if not full_name or not isinstance(full_name, str):
        return ""
    
    name_parts = full_name.strip().split()
    if name_parts:
        return name_parts[0]
    return ""

def analyze_role_relevance(role: str, search_context: str) -> dict:
    """
    Analyze the logical relationship between a person's role and what they're looking for.
    Returns relevance score and behavioral adjustments.
    """
    role_lower = role.lower()
    search_lower = search_context.lower()
    
    # Define role-to-domain relevance mappings
    role_domains = {
        # Technical roles
        "engineer": ["software", "technology", "programming", "development", "cloud", "infrastructure", "api", "database"],
        "developer": ["software", "technology", "programming", "development", "cloud", "infrastructure", "api", "database"],
        "architect": ["software", "technology", "programming", "development", "cloud", "infrastructure", "enterprise"],
        "devops": ["cloud", "infrastructure", "deployment", "monitoring", "automation", "security"],
        
        # Sales roles
        "sales": ["crm", "sales tools", "pipeline", "lead generation", "prospecting", "revenue", "quota", "cold email", "outbound"],
        "account": ["crm", "sales tools", "client management", "relationship", "revenue"],
        "business development": ["crm", "sales tools", "partnerships", "growth", "revenue", "lead generation"],
        
        # Marketing roles
        "marketing": ["marketing automation", "analytics", "campaigns", "content", "social media", "advertising", "email marketing", "lead generation"],
        "growth": ["marketing automation", "analytics", "campaigns", "growth hacking", "conversion", "lead generation"],
        "content": ["content management", "cms", "social media", "publishing", "seo"],
        
        # Agency/Owner roles
        "owner": ["business tools", "marketing", "sales", "lead generation", "client acquisition", "cold email", "outbound", "automation"],
        "founder": ["business tools", "marketing", "sales", "lead generation", "client acquisition", "cold email", "outbound", "automation"],
        "agency": ["marketing", "advertising", "lead generation", "client acquisition", "cold email", "outbound", "campaigns"],
        
        # Investment/Finance roles
        "portfolio": ["investment", "portfolio", "fund", "capital", "financial", "climate", "esg", "sustainable", "returns"],
        "investment": ["investment", "portfolio", "fund", "capital", "financial", "climate", "esg", "sustainable", "returns"],
        "fund": ["investment", "portfolio", "fund", "capital", "financial", "climate", "esg", "sustainable", "returns"],
        "capital": ["investment", "portfolio", "fund", "capital", "financial", "climate", "esg", "sustainable", "returns"],
        "wealth": ["investment", "portfolio", "fund", "capital", "financial", "wealth management", "asset management"],
        "asset": ["investment", "portfolio", "fund", "capital", "financial", "asset management", "wealth management"],
        
        # Executive roles
        "ceo": ["strategy", "analytics", "business intelligence", "enterprise", "leadership", "business tools"],
        "cto": ["technology", "software", "infrastructure", "security", "enterprise"],
        "cfo": ["finance", "accounting", "analytics", "business intelligence", "compliance"],
        
        # Operations roles
        "operations": ["project management", "workflow", "automation", "efficiency", "process"],
        "manager": ["project management", "team collaboration", "productivity", "workflow"],
        
        # Finance roles
        "finance": ["accounting", "financial planning", "analytics", "compliance", "reporting"],
        "accounting": ["accounting", "financial planning", "compliance", "reporting", "audit"],
        
        # HR roles
        "hr": ["human resources", "recruiting", "talent management", "employee", "payroll"],
        "recruiting": ["recruiting", "talent management", "hr", "candidate", "hiring"],
        
        # Security roles
        "security": ["cybersecurity", "compliance", "risk management", "audit", "privacy"],
        "compliance": ["compliance", "risk management", "audit", "security", "regulatory"]
    }
    
    # Calculate relevance score
    relevance_score = 0.3  # baseline for any professional
    role_match = False
    
    # Check for direct role matches
    for role_key, domains in role_domains.items():
        if role_key in role_lower:
            for domain in domains:
                if domain in search_lower:
                    relevance_score = min(1.0, relevance_score + 0.2)
                    role_match = True
    
    # Check for cross-functional relevance (lower scores)
    cross_functional_terms = ["productivity", "collaboration", "communication", "project management"]
    if any(term in search_lower for term in cross_functional_terms):
        relevance_score = min(1.0, relevance_score + 0.1)
    
    # Check for personal purchases (always somewhat relevant)
    personal_terms = ["car", "house", "phone", "laptop", "insurance", "loan"]
    if any(term in search_lower for term in personal_terms):
        relevance_score = min(1.0, relevance_score + 0.3)
    
    # Check for career-related (always highly relevant)
    career_terms = ["job", "position", "role", "career", "opportunity"]
    if any(term in search_lower for term in career_terms):
        relevance_score = min(1.0, relevance_score + 0.4)
    
    # Check for investment-related (highly relevant for finance professionals)
    investment_terms = ["investment", "invest", "fund", "capital", "portfolio", "climate", "esg", "sustainable", "financial"]
    if any(term in search_lower for term in investment_terms):
        relevance_score = min(1.0, relevance_score + 0.4)
    
    # Determine engagement level based on relevance
    if relevance_score >= 0.8:
        engagement_level = "high"
        behavioral_modifier = "active"
    elif relevance_score >= 0.5:
        engagement_level = "medium" 
        behavioral_modifier = "interested"
    else:
        engagement_level = "low"
        behavioral_modifier = "casual"
    
    return {
        "relevance_score": relevance_score,
        "engagement_level": engagement_level,
        "behavioral_modifier": behavioral_modifier,
        "role_match": role_match,
        "adjustment_factor": relevance_score  # Used to adjust CMI, RBFS, IAS scores
    }

def analyze_search_context(user_prompt: str) -> dict:
    """
    Analyze the user's search context to understand what they're actually looking for.
    Uses a more flexible approach that can identify various context types.
    
    Returns:
        Dictionary with context analysis including context type, decision factors, etc.
    """
    prompt_lower = user_prompt.lower()
    
    # Define context categories with their indicators
    context_categories = {
        "legal_services": [
            "attorney", "lawyer", "law firm", "legal services", "legal advice", "legal counsel",
            "divorce attorney", "family law", "criminal defense", "personal injury", "estate planning",
            "immigration lawyer", "corporate law", "intellectual property", "patent attorney"
        ],
        "real_estate": [
            "real estate", "property", "office space", "commercial property", "commercial real estate",
            "retail space", "industrial space", "warehouse", "lease", "rent", "buy property",
            "commercial building", "office building", "square feet", "sqft", "location"
        ],
        "personal_purchase": [
            "new car", "car", "vehicle", "auto", "house", "home", "apartment", 
            "vacation", "travel", "personal insurance", "personal loan", "mortgage", "credit card",
            "phone", "personal laptop", "furniture", "appliance"
        ],
        "career_opportunity": [
            "job", "position", "role", "career", "opportunity", "hire", "recruit",
            "employment", "work", "candidate"
        ],
        "financial_decision": [
            "investment", "invest", "stock", "fund", "portfolio", "advisor", "financial planner",
            "wealth management", "retirement", "401k", "climate", "esg", "sustainable",
            "green investment", "impact investing", "venture capital", "private equity",
            "hedge fund", "asset management", "capital", "funding", "finance"
        ],
        "business_solution": [
            "crm", "software", "tool", "platform", "system", "solution", "service",
            "consultant", "agency", "vendor", "provider", "contractor", "freelancer",
            "marketing automation", "analytics", "business intelligence", "enterprise"
        ],
        "healthcare": [
            "doctor", "physician", "medical", "healthcare", "health", "hospital", "clinic",
            "specialist", "treatment", "therapy", "diagnosis", "patient", "medicine"
        ],
        "education": [
            "school", "university", "college", "education", "course", "degree", "learning",
            "training", "teacher", "professor", "student", "academic", "curriculum"
        ]
    }
    
    # Determine primary context by checking for indicators
    context_type = "general_business"  # default
    context_matches = {}
    
    # Count matches for each context category
    for category, indicators in context_categories.items():
        match_count = sum(1 for term in indicators if term in prompt_lower)
        if match_count > 0:
            context_matches[category] = match_count
    
    # Select the category with the most matches
    if context_matches:
        context_type = max(context_matches.items(), key=lambda x: x[1])[0]
    
    # Define decision factors based on context type
    decision_factors_map = {
        "legal_services": ["expertise", "experience", "reputation", "case success rate", "client service"],
        "real_estate": ["location", "price", "size", "amenities", "accessibility", "lease terms"],
        "personal_purchase": ["price", "quality", "features", "reviews", "warranty", "personal_fit"],
        "career_opportunity": ["compensation", "growth_potential", "company_culture", "role_fit", "location"],
        "financial_decision": ["returns", "risk_assessment", "due_diligence", "track_record", "market_conditions"],
        "business_solution": ["roi", "integration", "scalability", "support", "pricing"],
        "healthcare": ["expertise", "experience", "availability", "location", "insurance coverage"],
        "education": ["quality", "reputation", "curriculum", "cost", "location", "career outcomes"]
    }
    
    decision_factors = decision_factors_map.get(context_type, ["value", "quality", "fit", "reliability"])
    
    # Create a simplified context result
    return {
        "context_type": context_type,
        "decision_factors": decision_factors,
        "is_personal": context_type in ["personal_purchase", "career_opportunity"],
        "is_business": context_type in ["business_solution", "general_business"],
        "is_specialized": context_type in ["legal_services", "real_estate", "healthcare", "education", "financial_decision"]
    }

def simulate_personal_research_patterns() -> Dict[str, Any]:
    """Simulate personal research patterns that indicate off-hours engagement."""
    # 25% chance of showing personal research patterns
    has_personal_patterns = random.random() < 0.25
    
    if not has_personal_patterns:
        return {
            "personal_research": False,
            "cmi_boost": 0,
            "engagement_note": ""
        }
    
    # Current time for context
    current_hour = datetime.now().hour
    is_weekend = datetime.now().weekday() >= 5
    is_evening = current_hour >= 18 or current_hour <= 7
    
    # Different patterns of personal research
    patterns = [
        {
            "type": "weekend_research",
            "cmi_boost": 15,
            "note": "shows weekend research activity indicating personal priority"
        },
        {
            "type": "evening_research", 
            "cmi_boost": 12,
            "note": "demonstrates evening research sessions suggesting personal investment"
        },
        {
            "type": "mobile_research",
            "cmi_boost": 10,
            "note": "exhibits mobile browsing patterns indicating on-the-go personal interest"
        },
        {
            "type": "late_night_research",
            "cmi_boost": 18,
            "note": "shows late-night research activity signaling high personal commitment"
        }
    ]
    
    # Select a random pattern
    pattern = random.choice(patterns)
    
    return {
        "personal_research": True,
        "pattern_type": pattern["type"],
        "cmi_boost": pattern["cmi_boost"],
        "engagement_note": pattern["note"]
    }

def generate_focused_insight_ai(role: str, user_prompt: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a focused behavioral insight using AI with dynamic context awareness."""
    try:
        if not openai_client:
            return generate_fallback_insight(role, candidate_data, user_prompt)
        
        # Analyze the search context and role relevance
        search_context_analysis = analyze_search_context(user_prompt)
        role_relevance = analyze_role_relevance(role, user_prompt)
        context_type = search_context_analysis["context_type"]
        
        # Create a more sophisticated prompt that avoids generic responses and is context-aware
        system_prompt = f"""
        You are an expert at analyzing professional behavior patterns. Generate a specific, actionable insight about how this person approaches decisions.

        CONTEXT:
        - Role: {role}
        - Search context: {user_prompt}
        - Context type: {context_type}
        - Relevance score: {role_relevance['relevance_score']:.2f}
        - Engagement level: {role_relevance['engagement_level']}
        
        CRITICAL INSTRUCTIONS:
        1. The insight MUST be contextually appropriate for {context_type}
        2. NEVER mention "implementation plans" unless specifically relevant to {context_type}
        3. NEVER use generic software/technology language for non-technology contexts
        4. Tailor your language to the specific domain of {context_type}
        5. For legal contexts, use legal terminology; for real estate, use property terminology, etc.
        
        REQUIREMENTS:
        1. Write exactly 1-2 sentences (25-40 words)
        2. Use "they" pronouns only
        3. Focus on decision-making style, not job description
        4. Be specific to their engagement level:
           - HIGH (0.8+): Active evaluation, comparing options, ready to move forward
           - MEDIUM (0.5-0.8): Interested but cautious, moderate research phase
           - LOW (0.3-0.5): Casual browsing, minimal commitment
        5. Avoid generic phrases like "business needs" or "professional goals"
        6. Make it actionable for engagement
        
        EXAMPLES OF GOOD INSIGHTS BY CONTEXT:
        - Legal: "They research case precedents thoroughly before adopting new legal technologies, prioritizing ethical compliance over efficiency gains."
        - Real Estate: "They evaluate properties based on location and client accessibility first, considering price as a secondary factor."
        - Healthcare: "They consult extensively with colleagues before adopting new treatment approaches, requiring solid evidence-based research."
        - Business: "They research extensively before decisions, preferring detailed demos over high-level pitches."
        """
        
        # Check for personal research patterns to enhance context
        research_data = simulate_personal_research_patterns()
        research_context = ""
        if research_data["personal_research"] and role_relevance['engagement_level'] != "low":
            research_context = " (Note: Shows after-hours research activity suggesting higher priority)"

        user_prompt_for_ai = f"""
        Role: {role}
        Search: "{user_prompt}"
        Engagement: {role_relevance['engagement_level']} relevance{research_context}
        
        Generate a specific behavioral insight about their decision-making approach.
        """
        
        # Call the OpenAI API with optimized parameters
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.6,  # Slightly reduced for more consistent quality
            max_tokens=60,    # Reduced for conciseness
            presence_penalty=0.3,  # Encourage unique phrasing
            frequency_penalty=0.2   # Reduce repetitive language
        )
        
        insight = response.choices[0].message.content.strip()
        
        # Validate the insight quality
        if len(insight.split()) < 10 or any(generic in insight.lower() for generic in [
            "business needs", "professional goals", "specific requirements", "their role"
        ]):
            return generate_fallback_insight(role, candidate_data, user_prompt)
        
        return insight
        
    except Exception:
        return generate_fallback_insight(role, candidate_data, user_prompt)

def generate_score_ai(score_type: str, role: str, user_prompt: str = "") -> Dict[str, Any]:
    """Generate a behavioral score using AI with dynamic context awareness."""
    try:
        if not openai_client:
            if score_type == "cmi":
                return generate_fallback_cmi_score(role, user_prompt)
            elif score_type == "rbfs":
                return generate_fallback_rbfs_score(role, user_prompt)
            else:
                return generate_fallback_ias_score(role, user_prompt)
        
        # Analyze context and role relevance for accurate scoring
        context_analysis = analyze_search_context(user_prompt)
        role_relevance = analyze_role_relevance(role, user_prompt)
        
        # Extract context type for more specific prompting
        context_type = context_analysis["context_type"]
        
        # Create a context-aware base prompt
        context_description = f"a {role} looking for {context_type} related to: \"{user_prompt}\""
        
        # Create a relevance-aware prompt based on score type
        if score_type == "cmi":
            system_prompt = f"""
            Generate a Commitment Momentum Index (CMI) score (0-100) for {context_description}
            
            CONTEXT INFORMATION:
            - Context type: {context_type}
            - Role-need relevance: {role_relevance['relevance_score']:.2f} (0.0 = irrelevant, 1.0 = highly relevant)
            - Engagement level: {role_relevance['engagement_level']}
            
            CRITICAL INSTRUCTIONS:
            1. The explanation MUST be contextually appropriate for {context_type}
            2. NEVER mention "implementation plans" unless specifically relevant to {context_type}
            3. NEVER use generic software/technology language for non-technology contexts
            4. Tailor your language to the specific domain of {context_type}
            5. For legal contexts, use legal terminology; for real estate, use property terminology, etc.
            
            RELEVANCE-BASED SCORING RULES:
            - HIGH relevance (0.8+): 70-95 CMI - Active evaluation, comparing options, ready to decide
            - MEDIUM relevance (0.5-0.8): 40-70 CMI - Interested with moderate research activity
            - LOW relevance (0.3-0.5): 15-40 CMI - Casual browsing, low commitment, minimal engagement
            
            Return JSON with "score" and "explanation". 
            For explanation: Use "they" pronouns. Keep to 8-12 words reflecting their TRUE engagement level.
            """
        elif score_type == "rbfs":
            system_prompt = f"""
            Generate a Risk-Barrier Focus Score (RBFS) (0-100) for {context_description}
            
            CONTEXT INFORMATION:
            - Context type: {context_type}
            - Role-need relevance: {role_relevance['relevance_score']:.2f}
            - Engagement level: {role_relevance['engagement_level']}
            
            CRITICAL INSTRUCTIONS:
            1. The explanation MUST be contextually appropriate for {context_type}
            2. NEVER mention "implementation plans" unless specifically relevant to {context_type}
            3. NEVER use generic software/technology language for non-technology contexts
            4. Tailor your language to the specific domain of {context_type}
            5. For legal contexts, use legal terminology; for real estate, use property terminology, etc.
            
            Score guidelines:
            - 80-100: Highly cautious, needs extensive proof and validation
            - 60-79: Moderately risk-aware, wants clear evidence and assurances
            - 40-59: Balanced risk assessment, standard due diligence
            - 20-39: Risk-tolerant, focuses more on upside potential
            
            Return JSON with "score" and "explanation".
            For explanation: Use "they" or "them" pronouns. Keep to 8-12 words describing their risk evaluation style.
            """
        else:  # ias
            system_prompt = f"""
            Generate an Identity Alignment Signal (IAS) score (0-100) measuring personal investment level for {context_description}
            
            CONTEXT INFORMATION:
            - Context type: {context_type}
            - Role-need relevance: {role_relevance['relevance_score']:.2f}
            - Engagement level: {role_relevance['engagement_level']}
            
            CRITICAL INSTRUCTIONS:
            1. The explanation MUST be contextually appropriate for {context_type}
            2. NEVER mention "implementation plans" unless specifically relevant to {context_type}
            3. NEVER use generic software/technology language for non-technology contexts
            4. Tailor your language to the specific domain of {context_type}
            5. For legal contexts, use legal terminology; for real estate, use property terminology, etc.
            
            Score guidelines:
            - 80-100: Highly personally invested, shows after-hours research and priority
            - 60-79: Moderately invested, consistent engagement over time
            - 40-59: Some personal interest, occasional research activity
            - 20-39: Limited personal investment, minimal engagement
            
            Return JSON with "score" and "explanation".
            For explanation: Use "they" or "them" pronouns. Keep to 8-12 words describing their personal investment level.
            """
        
        # Call the OpenAI API with minimal tokens
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.5,
            max_tokens=50
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Ensure score is within range
        result["score"] = max(0, min(100, int(result["score"])))
        
        return result
        
    except Exception:
        if score_type == "cmi":
            return generate_fallback_cmi_score(role)
        elif score_type == "rbfs":
            return generate_fallback_rbfs_score(role)
        else:
            return generate_fallback_ias_score(role)

def enhance_behavioral_data_ai(
    behavioral_data: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    user_prompt: str,
    candidate_index: int = 0,
    is_top_candidate: bool = False
) -> Dict[str, Any]:
    """Enhance behavioral data with AI-generated insights and scores, ensuring uniqueness across candidates."""
    try:
        # Extract candidate data from the first candidate if available
        candidate_data = candidates[0] if candidates else {}
        
        # Get the prospect's role
        role = candidate_data.get("title", "professional")
        
        # Generate a focused behavioral insight with diversity
        behavioral_insight = generate_focused_insight_ai(role, user_prompt, candidate_data)
        
        # Generate the three behavioral scores with context and variation
        cmi_score = generate_score_ai("cmi", role, user_prompt)
        rbfs_score = generate_score_ai("rbfs", role, user_prompt)
        ias_score = generate_score_ai("ias", role, user_prompt)
        
        # Add score variation to prevent identical values
        scores = {
            "cmi": cmi_score,
            "rbfs": rbfs_score,
            "ias": ias_score
        }
        # Use optimal scores for top candidates
        if is_top_candidate:
            varied_scores = generate_top_lead_scores(scores, candidate_index)
        else:
            varied_scores = add_score_variation(scores, candidate_index)
        
        # Create the enhanced behavioral data
        return {
            "behavioral_insight": behavioral_insight,
            "scores": varied_scores
        }
        
    except Exception:
        # Return a contextual fallback based on role with diversity
        role = candidate_data.get("title", "professional") if candidates else "professional"
        
        # Generate diverse fallback data
        fallback_insight = generate_diverse_fallback_insight(role, candidate_data, user_prompt, set(), candidate_index)
        
        fallback_scores = {
            "cmi": generate_fallback_cmi_score(role, user_prompt, candidate_index),
            "rbfs": generate_fallback_rbfs_score(role, user_prompt, candidate_index),
            "ias": generate_fallback_ias_score(role, user_prompt, candidate_index)
        }
        # Use optimal scores for top candidates
        if is_top_candidate:
            varied_scores = generate_top_lead_scores(fallback_scores, candidate_index)
        else:
            varied_scores = add_score_variation(fallback_scores, candidate_index)
        
        return {
            "behavioral_insight": fallback_insight,
            "scores": varied_scores
        }


def enhance_behavioral_data_for_multiple_candidates(
    candidates: List[Dict[str, Any]],
    user_prompt: str
) -> List[Dict[str, Any]]:
    """
    Enhance behavioral data for multiple candidates while ensuring diverse, non-duplicative insights.
    
    Args:
        candidates: List of candidate dictionaries
        user_prompt: The user's search prompt
        
    Returns:
        List of candidates with enhanced behavioral data
    """
    if not candidates:
        return []
    
    enhanced_candidates = []
    generated_insights = []
    used_patterns = set()  # Track used patterns to avoid repetition
    
    for i, candidate in enumerate(candidates):
        try:
            # Generate behavioral data for this candidate with uniqueness context
            # Mark first 3 candidates as top leads
            is_top_candidate = i < 3
            behavioral_data = enhance_behavioral_data_ai({}, [candidate], user_prompt, i, is_top_candidate)
            
            # Check for insight uniqueness
            insight = behavioral_data.get("behavioral_insight", "")
            if insight:
                # Import the uniqueness validation from openai_utils
                from openai_utils import validate_response_uniqueness
                
                # Check if this insight is too similar to previous ones
                all_insights = generated_insights + [insight]
                unique_insights = validate_response_uniqueness(all_insights, similarity_threshold=0.5)  # Stricter threshold for better uniqueness
                
                # If the new insight is not unique, generate a diverse fallback
                if len(unique_insights) <= len(generated_insights):
                    role = candidate.get("title", "professional")
                    insight = generate_diverse_fallback_insight(role, candidate, user_prompt, used_patterns, i)
                    behavioral_data["behavioral_insight"] = insight
                
                generated_insights.append(insight)
            
            # Ensure diverse scores as well
            scores = behavioral_data.get("scores", {})
            if scores:
                # For top candidates (first 2-3), ensure they have optimal "top lead" scores
                if i < 3:  # Top 3 candidates get optimal scores
                    scores = generate_top_lead_scores(scores, i)
                else:
                    # Add some variation to scores to avoid identical values
                    scores = add_score_variation(scores, i)
                behavioral_data["scores"] = scores
            
            # Add behavioral data to candidate
            candidate["behavioral_data"] = behavioral_data
            enhanced_candidates.append(candidate)
            
        except Exception as e:
            # Fallback for any errors with diversity
            role = candidate.get("title", "professional")
            fallback_scores = {
                "cmi": generate_fallback_cmi_score(role, user_prompt),
                "rbfs": generate_fallback_rbfs_score(role, user_prompt),
                "ias": generate_fallback_ias_score(role, user_prompt)
            }
            
            # For top candidates, ensure optimal scores
            if i < 3:
                fallback_scores = generate_top_lead_scores(fallback_scores, i)
            else:
                fallback_scores = add_score_variation(fallback_scores, i)
            
            candidate["behavioral_data"] = {
                "behavioral_insight": generate_diverse_fallback_insight(role, candidate, user_prompt, used_patterns, i),
                "scores": fallback_scores
            }
            enhanced_candidates.append(candidate)
    
    return enhanced_candidates


def generate_diverse_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]], user_prompt: str, used_patterns: set, candidate_index: int) -> str:
    """Generate diverse fallback insights that avoid repetition."""
    role_lower = role.lower()
    
    # Check for personal purchase context first
    context_type = analyze_search_context(user_prompt).get("context_type", "")
    if context_type == "personal_purchase":
        # Special insights for personal purchase scenarios (cars, homes, etc.)
        personal_insights = [
            "They research extensively before making personal purchases, comparing features and reviews.",
            "They prioritize quality and durability in personal buying decisions.",
            "They balance price considerations with long-term value in their purchases.",
            "They seek recommendations from trusted sources before making significant purchases.",
            "They evaluate personal purchases based on practical needs rather than status.",
            "They consider long-term ownership costs beyond the initial purchase price.",
            "They prefer hands-on experience with products before committing to major purchases."
        ]
        
        # Select insight that hasn't been used
        available_insights = [insight for insight in personal_insights if insight not in used_patterns]
        if available_insights:
            selected_insight = available_insights[candidate_index % len(available_insights)]
            used_patterns.add(selected_insight)
            return selected_insight
    
    # Create diverse insight pools based on role and context
    role_insights = {
        "owner": [
            "They prioritize ROI and measurable business impact when evaluating new tools.",
            "They prefer solutions that integrate seamlessly with existing workflows.",
            "They make decisions quickly but want clear proof of value first.",
            "They focus on tools that can scale with business growth.",
            "They evaluate based on competitive advantage and market positioning."
        ],
        "founder": [
            "They think strategically about long-term business implications.",
            "They balance innovation with practical implementation concerns.", 
            "They seek solutions that align with company vision and values.",
            "They prefer tools that offer flexibility and customization options.",
            "They evaluate based on potential for business transformation."
        ],
        "ceo": [
            "They delegate technical evaluation while maintaining strategic oversight.",
            "They focus on solutions that drive measurable business outcomes.",
            "They prefer executive-level presentations with clear success metrics.",
            "They make decisions based on competitive positioning and market advantage.",
            "They evaluate tools for their potential to accelerate company objectives."
        ],
        "cmo": [
            "They evaluate tools based on marketing performance and attribution capabilities.",
            "They prefer solutions with strong analytics and reporting features.",
            "They focus on tools that enhance customer acquisition and retention.",
            "They seek platforms that integrate with existing marketing technology stack.",
            "They prioritize solutions that demonstrate clear marketing ROI."
        ],
        "manager": [
            "They balance team needs with budget constraints and approval processes.",
            "They involve team members in evaluation to ensure user adoption.",
            "They prefer solutions with strong training and support resources.",
            "They focus on tools that improve team productivity and collaboration.",
            "They evaluate based on ease of implementation and change management."
        ]
    }
    
    # Get role-specific insights
    insights_pool = []
    for role_key, insights in role_insights.items():
        if role_key in role_lower:
            insights_pool = insights
            break
    
    # Fallback to generic insights if no role match
    if not insights_pool:
        insights_pool = [
            "They take a methodical approach to evaluating new solutions.",
            "They prefer vendors with proven track records and strong support.",
            "They evaluate tools based on practical implementation and outcomes.",
            "They seek solutions that offer clear value and measurable results.",
            "They balance innovation with risk management in their decisions."
        ]
    
    # Select insight that hasn't been used
    available_insights = [insight for insight in insights_pool if insight not in used_patterns]
    
    if not available_insights:
        # If all insights used, add variation to existing ones
        base_insight = insights_pool[candidate_index % len(insights_pool)]
        variations = [
            f"{base_insight} They also consider implementation timeline carefully.",
            f"{base_insight} They typically involve stakeholders in the decision process.",
            f"{base_insight} They prefer phased rollouts to minimize risk.",
            f"{base_insight} They value ongoing vendor relationships and support."
        ]
        selected_insight = variations[candidate_index % len(variations)]
    else:
        selected_insight = available_insights[candidate_index % len(available_insights)]
    
    used_patterns.add(selected_insight)
    return selected_insight


def generate_top_lead_scores(scores: Dict[str, Any], candidate_index: int) -> Dict[str, Any]:
    """
    Generate optimal scores for top lead candidates.
    Top leads should have:
    - High CMI (80-95): Strong commitment momentum
    - High IAS (80-95): High personal investment
    - Low to Moderate RBFS (30-60): Low risk barriers
    """
    import random
    random.seed(candidate_index + 100)  # Different seed for top leads
    
    top_lead_scores = {}
    
    # Top lead explanations that match high scores
    top_lead_explanations = {
        "cmi": [
            "Actively comparing vendor solutions and requesting demos",
            "Evaluating implementation timelines and ROI projections",
            "Researching integration requirements and technical specifications",
            "Investigating pricing models and contract terms across multiple vendors",
            "Assessing solution capabilities against current business requirements"
        ],
        "rbfs": [
            "Willing to try new approaches if they show promise",
            "Takes calculated risks for potential competitive advantage",
            "Focuses more on opportunity than potential downsides",
            "Comfortable with innovative solutions and early adoption",
            "Values potential competitive advantage over implementation complexity"
        ],
        "ias": [
            "Shows strong personal investment through intensive research",
            "Demonstrates strong personal interest with detailed evaluation",
            "Exhibits strong personal commitment through repeated activity",
            "Displays personal priority through after-hours research patterns",
            "Shows strong personal interest with focused activity"
        ]
    }
    
    for score_type, score_data in scores.items():
        if isinstance(score_data, dict) and "score" in score_data:
            
            if score_type == "cmi":
                # High CMI for top leads (80-95)
                optimal_cmi_scores = [85, 88, 91, 82, 89, 86, 93, 84, 87, 90]
                new_score = optimal_cmi_scores[candidate_index % len(optimal_cmi_scores)]
                new_explanation = top_lead_explanations["cmi"][candidate_index % len(top_lead_explanations["cmi"])]
                
            elif score_type == "rbfs":
                # Low to moderate RBFS for top leads (30-60)
                optimal_rbfs_scores = [45, 38, 52, 41, 48, 35, 55, 42, 49, 39]
                new_score = optimal_rbfs_scores[candidate_index % len(optimal_rbfs_scores)]
                new_explanation = top_lead_explanations["rbfs"][candidate_index % len(top_lead_explanations["rbfs"])]
                
            elif score_type == "ias":
                # High IAS for top leads (80-95)
                optimal_ias_scores = [87, 84, 91, 88, 85, 92, 83, 89, 86, 90]
                new_score = optimal_ias_scores[candidate_index % len(optimal_ias_scores)]
                new_explanation = top_lead_explanations["ias"][candidate_index % len(top_lead_explanations["ias"])]
                
            else:
                # Keep original score and explanation for any other score types
                new_score = score_data["score"]
                new_explanation = score_data.get("explanation", "")
            
            top_lead_scores[score_type] = {
                "score": new_score,
                "explanation": new_explanation
            }
        else:
            top_lead_scores[score_type] = score_data
    
    random.seed()  # Reset random seed
    return top_lead_scores

def add_score_variation(scores: Dict[str, Any], candidate_index: int) -> Dict[str, Any]:
    """Add subtle variation to scores to avoid identical values and prevent clustering."""
    import random
    
    # Set seed based on candidate index for consistent but different results
    random.seed(candidate_index + 42)
    
    varied_scores = {}
    for score_type, score_data in scores.items():
        if isinstance(score_data, dict) and "score" in score_data:
            base_score = score_data["score"]
            
            # Use different variation ranges for different score types to prevent clustering
            if score_type == "rbfs":
                # Wider variation for RBFS to prevent 57 clustering
                variation = random.randint(-8, 12)
            elif score_type == "cmi":
                variation = random.randint(-6, 8)
            else:  # ias
                variation = random.randint(-4, 7)
            
            new_score = max(15, min(95, base_score + variation))  # Keep within reasonable bounds
            
            varied_scores[score_type] = {
                "score": new_score,
                "explanation": score_data.get("explanation", "")
            }
        else:
            varied_scores[score_type] = score_data
    
    # Reset random seed
    random.seed()
    
    return varied_scores

# Fallback functions for when AI generation fails

def generate_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]] = None, user_prompt: str = "") -> str:
    """Generate a context-aware fallback insight based on role and search context."""
    role_lower = role.lower()
    
    # Analyze search context and role relevance
    context_analysis = analyze_search_context(user_prompt)
    role_relevance = analyze_role_relevance(role, user_prompt)
    context_type = context_analysis["context_type"]
    
    # Define patterns based on context type first, then role
    context_patterns = {
        "legal_services": {
            "attorney": [
                "They thoroughly research precedents and case law before adopting new approaches.",
                "They prioritize client outcomes and ethical considerations in all decisions.",
                "They evaluate options based on both legal merit and practical application."
            ],
            "default": [
                "They carefully evaluate legal implications before making decisions.",
                "They balance client needs with legal best practices in their approach.",
                "They research thoroughly, considering both precedent and practical outcomes."
            ]
        },
        "real_estate": {
            "default": [
                "They evaluate properties based on location and accessibility first, then price.",
                "They balance current space needs with long-term growth considerations.",
                "They research market trends thoroughly before making property decisions."
            ]
        },
        "healthcare": {
            "default": [
                "They prioritize patient outcomes and evidence-based approaches in decisions.",
                "They balance clinical best practices with practical implementation considerations.",
                "They research thoroughly before adopting new treatment methodologies."
            ]
        },
        "default": {
            "engineer": [
                "They prioritize technical specifications and integration capabilities over marketing claims.",
                "They prefer hands-on trials and detailed documentation before making decisions.",
                "They research extensively, comparing technical architectures and performance metrics."
            ],
            "manager": [
                "They balance team needs with budget constraints, requiring clear ROI justification.",
                "They involve stakeholders in decisions, preferring consensus-building approaches.",
                "They evaluate solutions based on team adoption potential and training requirements."
            ],
            "director": [
                "They focus on strategic alignment and long-term scalability over short-term features.",
                "They require executive-level presentations with clear business impact metrics.",
                "They delegate technical evaluation while maintaining oversight of strategic fit."
            ],
            "ceo": [
                "They make decisions quickly once convinced, but need compelling business case upfront.",
                "They prefer high-level strategic discussions over detailed feature comparisons.",
                "They evaluate solutions based on competitive advantage and market positioning."
            ],
            "sales": [
                "They move fast when they see clear revenue impact and quota achievement potential.",
                "They prefer solutions that integrate with existing workflows and require minimal training.",
                "They evaluate based on peer success stories and proven performance gains."
            ],
            "default": [
                "They research thoroughly before making decisions, comparing multiple options.",
                "They balance practical needs with long-term considerations in their approach.",
                "They evaluate options based on both current fit and future potential."
            ]
        }
    }
    
    # First try to get context-specific patterns
    context_specific_patterns = context_patterns.get(context_type, context_patterns["default"])
    
    # Then try to get role-specific patterns within that context
    role_key = "default"
    for key in context_specific_patterns.keys():
        if key in role_lower:
            role_key = key
            break
    
    selected_patterns = context_specific_patterns.get(role_key, context_specific_patterns.get("default", []))
    
    # Fallback to generic patterns if no patterns found
    if not selected_patterns:
        selected_patterns = [
            "They take a methodical approach, researching options thoroughly before committing.",
            "They prefer solutions with proven track records and strong support systems.",
            "They evaluate based on practical implementation and measurable outcomes."
        ]
    
    # Adjust based on engagement level
    if role_relevance["engagement_level"] == "low":
        # For low relevance, indicate casual interest
        base_insight = "They browse casually in this area, requiring compelling reasons to engage further."
    elif role_relevance["engagement_level"] == "medium":
        # For medium relevance, show moderate interest
        import random
        random.seed(hash(role + user_prompt + str(candidate_index)) % 1000)
        base_insight = random.choice([
            "They show measured interest, researching options with careful consideration.",
            "They evaluate methodically, taking time to assess fit and value.",
            "They approach decisions cautiously, preferring to understand all implications first."
        ])
    else:
        # For high relevance, use context and role-specific pattern
        import random
        random.seed(hash(role + user_prompt + str(candidate_index)) % 1000)
        base_insight = random.choice(selected_patterns)
    
    # Add research pattern context if applicable
    research_data = simulate_personal_research_patterns()
    if research_data["personal_research"] and role_relevance["engagement_level"] != "low":
        base_insight += " Their after-hours research activity suggests this is a higher priority."
    
    return base_insight

def generate_fallback_cmi_score(role: str, user_prompt: str = "", candidate_index: int = 0) -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback CMI score with guaranteed diversity."""
    role_lower = role.lower()
    
    # Analyze role relevance to adjust scores
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Context-aware explanations by role and engagement level
    context_analysis = analyze_search_context(user_prompt)
    
    if context_analysis["is_legal"]:
        role_explanations = {
            "high": [
                "Actively researching legal technology solutions for practical implementation",
                "Engaged in detailed evaluation of legal AI tools for practice", 
                "Comparing multiple legal tech platforms with specific requirements",
                "Requesting demos and consultations for legal software",
                "Actively seeking to modernize legal practice with technology"
            ],
            "medium": [
                "Exploring legal technology options with moderate interest",
                "Researching how AI might enhance their legal practice",
                "Considering legal tech adoption in the coming months",
                "Gathering information on legal software capabilities",
                "Evaluating potential benefits of legal tech for client service"
            ],
            "low": [
                "Casually browsing legal technology options",
                "Preliminary research on legal AI without specific timeline", 
                "Early-stage exploration of legal tech possibilities",
                "Gathering basic information about legal software",
                "Initial consideration of how technology might fit legal practice"
            ]
        }
    elif context_analysis["is_real_estate"]:
        role_explanations = {
            "high": [
                "Actively touring properties and comparing location options",
                "Engaged in detailed space planning and lease negotiations", 
                "Comparing multiple properties with specific requirements in mind",
                "Requesting detailed floor plans and site visits",
                "Actively evaluating locations for current business needs"
            ],
            "medium": [
                "Researching location options for future expansion plans",
                "Exploring real estate options with mid-term timeline",
                "Comparing property features with flexible timeline",
                "Gathering information on market rates and availability",
                "Evaluating space requirements for potential relocation"
            ],
            "low": [
                "Casually browsing commercial real estate options",
                "Preliminary research without specific space timeline", 
                "Early-stage exploration of potential locations",
                "Gathering basic market information without timeline pressure",
                "Initial consideration of future space requirements"
            ]
        }
    elif context_analysis["context_type"] == "financial_decision":
        role_explanations = {
            "high": [
                "Actively evaluating investment opportunities for portfolio growth",
                "Conducting comprehensive due diligence on potential investments", 
                "Researching diversification opportunities across asset classes",
                "Comparing investment alternatives for optimal capital allocation",
                "Analyzing market conditions for strategic investment timing"
            ],
            "medium": [
                "Moderately interested in exploring investment opportunities",
                "Researching financial options with flexible timeline",
                "Evaluating investments for future portfolio consideration",
                "Assessing market trends for potential investment timing",
                "Considering investment options for strategic planning"
            ],
            "low": [
                "Casually browsing investment options with minimal engagement",
                "Limited interest in current financial opportunities", 
                "Showing minimal commitment to investment decisions",
                "Browsing financial options without specific timeline",
                "Displaying casual interest in investment alternatives"
            ]
        }
    else:
        role_explanations = {
            "high": [
                "Actively comparing vendor solutions and requesting product demos",
                "Evaluating implementation timelines and calculating ROI projections",
                "Researching integration capabilities and technical requirements", 
                "Investigating pricing models and contract terms across multiple platforms",
                "Assessing solution features against current business requirements"
            ],
            "medium": [
                "Moderately interested, weighing business benefits and implementation costs",
                "Exploring vendor options with flexible evaluation timeline",
                "Researching solutions for future strategic consideration",
                "Evaluating tools for potential operational improvement",
                "Considering solutions for long-term business planning"
            ],
            "low": [
                "Casually browsing vendor websites with minimal current interest",
                "Limited engagement, requiring compelling value proposition",
                "Browsing solution options with low commitment level",
                "Showing minimal priority for solution evaluation",
                "Displaying casual interest without specific timeline"
            ]
        }
    
    # Deterministic score variation with much wider ranges to prevent clustering
    base_scores = {
        "high": [85, 78, 82, 75, 88, 91, 73, 86, 79, 84, 92, 76, 89, 81, 87, 74, 90, 83, 77, 85],
        "medium": [65, 58, 62, 55, 68, 71, 52, 66, 59, 63, 72, 56, 69, 61, 67, 54, 70, 64, 57, 65], 
        "low": [35, 28, 32, 25, 38, 41, 22, 36, 29, 33, 42, 26, 39, 31, 37, 24, 40, 34, 27, 35]
    }
    
    engagement_level = role_relevance["engagement_level"]
    score_options = base_scores.get(engagement_level, base_scores["medium"])
    base_score = score_options[candidate_index % len(score_options)]
    
    # Adjust score based on role relevance
    adjusted_score = int(base_score * role_relevance["adjustment_factor"])
    
    # Select explanation deterministically based on candidate index
    explanations = role_explanations.get(engagement_level, role_explanations["medium"])
    adjusted_explanation = explanations[candidate_index % len(explanations)]
    
    return {
        "score": adjusted_score,
        "explanation": adjusted_explanation
    }

def generate_fallback_rbfs_score(role: str, user_prompt: str = "", candidate_index: int = 0) -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback RBFS score with diversity."""
    role_lower = role.lower()
    
    # Analyze role relevance - low relevance = higher risk sensitivity
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Diverse explanations by role and risk level
    import random
    random.seed(hash(role + user_prompt + "rbfs") % 1000)
    
    # Context-aware risk explanations
    context_analysis = analyze_search_context(user_prompt)
    
    if context_analysis["is_legal"]:
        risk_explanations = {
            "high": [
                "Thoroughly evaluates legal tech security and compliance features",
                "Carefully assesses vendor reputation and technology reliability",
                "Conducts detailed analysis of data privacy implications",
                "Prioritizes ethical considerations in legal AI adoption"
            ],
            "medium": [
                "Balances innovation benefits with practice disruption concerns",
                "Considers both client benefits and implementation challenges",
                "Evaluates technology reliability alongside practical application",
                "Weighs efficiency gains against learning curve"
            ],
            "low": [
                "Focuses primarily on innovative capabilities and client perception",
                "Prioritizes cutting-edge features over established reliability",
                "Values potential competitive advantage over implementation complexity",
                "Makes decisions based on peer adoption and industry trends"
            ]
        }
    elif context_analysis["is_real_estate"]:
        risk_explanations = {
            "high": [
                "Thoroughly evaluates location factors and market trends",
                "Carefully assesses property condition and future maintenance needs",
                "Conducts detailed analysis of lease terms and restrictions",
                "Prioritizes thorough inspection and location assessment"
            ],
            "medium": [
                "Balances location benefits with budget considerations",
                "Considers both short-term needs and long-term property value",
                "Evaluates space requirements alongside financial constraints",
                "Weighs accessibility against cost factors"
            ],
            "low": [
                "Focuses primarily on location and current availability",
                "Prioritizes quick move-in timeline over detailed assessment",
                "Values flexibility and amenities over long-term considerations",
                "Makes decisions based on first impressions and gut feeling"
            ]
        }
    elif context_analysis["context_type"] == "financial_decision":
        risk_explanations = {
            "high": [
                "Requires extensive due diligence and financial analysis",
                "Needs comprehensive risk assessment and market validation", 
                "Demands detailed performance history and regulatory compliance",
                "Seeks multiple references and third-party evaluations"
            ],
            "medium": [
                "Wants clear investment thesis and performance projections",
                "Prefers moderate due diligence before committing capital",
                "Seeks balanced risk-return evaluation and market analysis",
                "Requires standard financial documentation and track record"
            ],
            "low": [
                "Willing to consider emerging opportunities with growth potential",
                "Takes calculated investment risks for portfolio diversification",
                "Focuses more on upside potential than downside protection",
                "Comfortable with innovative investment strategies"
            ]
        }
    else:
        risk_explanations = {
            "high": [
                "Requires extensive validation and proof points",
                "Needs comprehensive security and compliance review", 
                "Demands detailed risk assessment and mitigation plans",
                "Seeks multiple references and case studies"
            ],
            "medium": [
                "Wants clear implementation roadmap and success metrics",
                "Prefers moderate validation before proceeding",
                "Seeks balanced risk-reward evaluation",
                "Requires standard due diligence and vendor assessment"
            ],
            "low": [
                "Willing to try new approaches if they show promise",
                "Takes calculated risks for potential competitive advantage",
                "Focuses more on opportunity than potential downsides",
                "Comfortable with innovative solutions and early adoption"
            ]
        }
    
    # Base scores by role with wider variation to avoid clustering around 57
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        base_score = random.randint(75, 88)
        risk_level = "high"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = random.randint(58, 72)
        risk_level = "medium"
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_score = random.randint(35, 52)
        risk_level = "low"
    elif any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_score = random.randint(62, 78)
        risk_level = "medium"
    elif any(marketing in role_lower for marketing in ["marketing", "growth", "demand", "content"]):
        base_score = random.randint(48, 66)
        risk_level = "medium"
    elif any(ops in role_lower for ops in ["operations", "manager", "director", "vp"]):
        base_score = random.randint(54, 71)
        risk_level = "medium"
    else:
        # Wider range for general roles to avoid 57 clustering
        base_score = random.randint(45, 75)
        risk_level = "medium"
    
    # Deterministic score and explanation selection with better distribution
    score_variations = [0, 7, -4, 11, -6, 3, -8, 9, -2, 5]
    variation = score_variations[candidate_index % len(score_variations)]
    adjusted_score = max(20, min(90, base_score + variation))
    
    # Adjust score - LOWER relevance = HIGHER risk sensitivity (inverse relationship)
    if role_relevance["engagement_level"] == "low":
        # Low relevance = higher risk sensitivity
        adjusted_score = min(90, adjusted_score + 20)
        adjusted_explanation = "Cautious about areas outside their core expertise"
    elif role_relevance["engagement_level"] == "medium":
        adjusted_score = min(90, adjusted_score + 5)
        explanations = risk_explanations["medium"]
        adjusted_explanation = explanations[candidate_index % len(explanations)]
    else:
        explanations = risk_explanations[risk_level]
        adjusted_explanation = explanations[candidate_index % len(explanations)]
    
    return {"score": adjusted_score, "explanation": adjusted_explanation}

def generate_fallback_ias_score(role: str, user_prompt: str = "", candidate_index: int = 0) -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback IAS score with diversity."""
    role_lower = role.lower()
    
    # Analyze role relevance to adjust scores
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Diverse explanations by role and alignment level
    import random
    random.seed(hash(role + user_prompt + "ias") % 1000)
    
    # Context-aware alignment explanations
    context_analysis = analyze_search_context(user_prompt)
    
    if context_analysis["is_legal"]:
        alignment_explanations = {
            "high": {
                "attorney": ["Shows strong personal interest with late-night research sessions", "Demonstrates high personal investment through weekend activity", "Exhibits strong personal commitment with repeated engagement"],
                "lawyer": ["Displays personal priority through after-hours research patterns", "Shows high personal investment with consistent engagement", "Demonstrates personal priority through extended research sessions"],
                "partner": ["Exhibits personal leadership investment with intensive research", "Shows high personal commitment through detailed evaluation", "Demonstrates strong personal interest with focused activity"],
                "associate": ["Displays personal career investment through thorough research", "Shows high personal interest with extended engagement", "Exhibits personal priority through consistent activity patterns"],
                "default": ["Shows high personal investment through intensive research", "Demonstrates strong personal interest with focused activity", "Exhibits strong personal commitment through repeated engagement"]
            },
            "medium": {
                "default": ["Shows moderate personal interest with regular research", "Demonstrates some personal investment through consistent activity", "Exhibits casual personal interest with periodic engagement", "Displays moderate personal commitment through ongoing research"]
            },
            "low": {
                "default": ["Shows limited personal investment with minimal research", "Demonstrates low personal interest through sporadic activity", "Exhibits minimal personal commitment with basic engagement", "Displays casual personal interest with limited research"]
            }
        }
    elif context_analysis["is_real_estate"]:
        alignment_explanations = {
            "high": {
                "owner": ["Shows strong personal investment with weekend property research", "Demonstrates high personal commitment through intensive evaluation", "Exhibits personal priority with repeated site visits and research"],
                "founder": ["Displays personal leadership investment with detailed research", "Shows high personal commitment through extended evaluation", "Demonstrates strong personal interest with focused activity"],
                "ceo": ["Exhibits personal executive investment with thorough research", "Shows high personal commitment through detailed evaluation", "Demonstrates strong personal interest with intensive activity"],
                "cto": ["Displays personal technical investment with detailed research", "Shows high personal commitment through infrastructure evaluation", "Exhibits strong personal interest with focused technical analysis"],
                "default": ["Shows high personal investment through intensive research", "Demonstrates strong personal interest with detailed evaluation", "Exhibits strong personal commitment through repeated activity"]
            },
            "medium": {
                "default": ["Shows moderate personal interest with regular research", "Demonstrates some personal investment through consistent evaluation", "Exhibits casual personal interest with periodic activity", "Displays moderate personal commitment through ongoing research"]
            },
            "low": {
                "default": ["Shows limited personal investment with minimal research", "Demonstrates low personal interest through sporadic activity", "Exhibits minimal personal commitment with basic evaluation", "Displays casual personal interest with limited research"]
            }
        }
    elif context_analysis["context_type"] == "financial_decision":
        alignment_explanations = {
            "high": {
                "owner": ["Shows strong personal investment with late-night financial research", "Demonstrates high personal commitment through intensive analysis", "Exhibits personal priority with repeated portfolio evaluation"],
                "founder": ["Displays personal financial investment with detailed research", "Shows high personal commitment through extended analysis", "Demonstrates strong personal interest with focused activity"],
                "ceo": ["Exhibits personal fiduciary investment with thorough research", "Shows high personal commitment through detailed evaluation", "Demonstrates strong personal interest with intensive analysis"],
                "cfo": ["Displays personal financial investment with detailed research", "Shows high personal commitment through risk analysis", "Exhibits strong personal interest with focused evaluation"],
                "default": ["Shows high personal investment through intensive research", "Demonstrates strong personal interest with detailed analysis", "Exhibits strong personal commitment through repeated evaluation"]
            },
            "medium": {
                "default": ["Shows moderate personal interest with regular research", "Demonstrates some personal investment through consistent analysis", "Exhibits casual personal interest with periodic evaluation", "Displays moderate personal commitment through ongoing research"]
            },
            "low": {
                "default": ["Shows limited personal investment with minimal research", "Demonstrates low personal interest through sporadic analysis", "Exhibits minimal personal commitment with basic evaluation", "Displays casual personal interest with limited research"]
            }
        }
    else:
        alignment_explanations = {
            "high": {
                "owner": ["Shows strong personal investment with after-hours research", "Demonstrates high personal commitment through weekend activity", "Exhibits personal priority with intensive evaluation sessions"],
                "founder": ["Displays personal leadership investment with detailed research", "Shows high personal commitment through extended evaluation", "Demonstrates strong personal interest with focused activity"],
                "ceo": ["Exhibits personal executive investment with thorough research", "Shows high personal commitment through detailed analysis", "Demonstrates strong personal interest with intensive activity"],
                "sales": ["Displays personal performance investment with detailed research", "Shows high personal commitment through quota-driven evaluation", "Exhibits strong personal interest with focused analysis"],
                "marketing": ["Shows personal campaign investment with intensive research", "Demonstrates high personal commitment through detailed evaluation", "Exhibits strong personal interest with focused activity"],
                "default": ["Shows high personal investment through intensive research", "Demonstrates strong personal interest with detailed evaluation", "Exhibits strong personal commitment through repeated activity"]
            },
            "medium": {
                "default": ["Shows moderate personal interest with regular research", "Demonstrates some personal investment through consistent activity", "Exhibits casual personal interest with periodic engagement", "Displays moderate personal commitment through ongoing evaluation"]
            },
            "low": {
                "default": ["Shows limited personal investment with minimal research", "Demonstrates low personal interest through sporadic activity", "Exhibits minimal personal commitment with basic engagement", "Displays casual personal interest with limited evaluation"]
            }
        }
    
    # Base scores by role with much wider variation to prevent clustering
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        score_options = [75, 78, 82, 85, 73, 80, 77, 84, 76, 81, 79, 83, 74, 86, 72, 87, 71, 88, 69, 89]
        base_score = score_options[candidate_index % len(score_options)]
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        score_options = [80, 83, 87, 90, 78, 85, 82, 89, 81, 86, 84, 88, 79, 91, 77, 92, 76, 93, 74, 94]
        base_score = score_options[candidate_index % len(score_options)]
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        score_options = [85, 88, 92, 95, 83, 90, 87, 94, 86, 91, 89, 93, 84, 96, 82, 97, 81, 98, 79, 99]
        base_score = score_options[candidate_index % len(score_options)]
    elif any(marketing in role_lower for marketing in ["marketing", "growth", "demand", "content"]):
        score_options = [80, 83, 87, 90, 78, 85, 82, 89, 81, 86, 84, 88, 79, 91, 77, 92, 76, 93, 74, 94]
        base_score = score_options[candidate_index % len(score_options)]
    else:
        score_options = [70, 73, 77, 80, 68, 75, 72, 79, 71, 76, 74, 78, 69, 81, 67, 82, 66, 83, 64, 84]
        base_score = score_options[candidate_index % len(score_options)]
    
    # Adjust score based on role relevance
    adjusted_score = int(base_score * role_relevance["adjustment_factor"])
    
    # Select diverse explanation
    engagement_level = role_relevance["engagement_level"]
    role_key = None
    for key in ["owner", "founder", "ceo", "sales", "marketing"]:
        if key in role_lower:
            role_key = key
            break
    
    if engagement_level == "high" and role_key in alignment_explanations["high"]:
        explanations = alignment_explanations["high"][role_key]
    elif engagement_level == "high":
        explanations = alignment_explanations["high"]["default"]
    elif engagement_level in alignment_explanations:
        explanations = alignment_explanations[engagement_level]["default"]
    else:
        explanations = alignment_explanations["medium"]["default"]
    
    adjusted_explanation = random.choice(explanations)
    
    return {"score": adjusted_score, "explanation": adjusted_explanation}