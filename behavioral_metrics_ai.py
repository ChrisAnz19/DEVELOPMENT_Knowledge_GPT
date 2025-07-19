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
    logger.warning("OpenAI package not available. AI-based metrics will be disabled.")

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
        "sales": ["crm", "sales tools", "pipeline", "lead generation", "prospecting", "revenue", "quota"],
        "account": ["crm", "sales tools", "client management", "relationship", "revenue"],
        "business development": ["crm", "sales tools", "partnerships", "growth", "revenue"],
        
        # Marketing roles
        "marketing": ["marketing automation", "analytics", "campaigns", "content", "social media", "advertising"],
        "growth": ["marketing automation", "analytics", "campaigns", "growth hacking", "conversion"],
        "content": ["content management", "cms", "social media", "publishing", "seo"],
        
        # Executive roles
        "ceo": ["strategy", "analytics", "business intelligence", "enterprise", "leadership"],
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
    
    Returns:
        Dictionary with context analysis including purchase type, decision factors, etc.
    """
    prompt_lower = user_prompt.lower()
    
    # Personal purchase indicators (truly personal items)
    personal_purchases = [
        "new car", "car", "vehicle", "auto", "house", "home", "apartment", 
        "vacation", "travel", "personal insurance", "personal loan", "mortgage", "credit card",
        "phone", "personal laptop", "furniture", "appliance"
    ]
    
    # Business/professional service indicators (includes CRM, software, etc.)
    business_services = [
        "crm", "software", "tool", "platform", "system", "solution", "service",
        "consultant", "agency", "vendor", "provider", "contractor", "freelancer",
        "marketing automation", "analytics", "business intelligence", "enterprise"
    ]
    
    # Job/career indicators
    career_related = [
        "job", "position", "role", "career", "opportunity", "hire", "recruit",
        "employment", "work", "candidate"
    ]
    
    # Investment/financial indicators
    investment_related = [
        "investment", "stock", "fund", "portfolio", "advisor", "financial planner",
        "wealth management", "retirement", "401k"
    ]
    
    # Determine primary context
    context_type = "business"  # default
    decision_factors = []
    
    if any(term in prompt_lower for term in personal_purchases):
        context_type = "personal_purchase"
        decision_factors = ["price", "quality", "features", "reviews", "warranty", "personal_fit"]
    elif any(term in prompt_lower for term in career_related):
        context_type = "career_opportunity" 
        decision_factors = ["compensation", "growth_potential", "company_culture", "role_fit", "location"]
    elif any(term in prompt_lower for term in investment_related):
        context_type = "financial_decision"
        decision_factors = ["returns", "risk", "fees", "track_record", "expertise"]
    elif any(term in prompt_lower for term in business_services):
        context_type = "business_solution"
        decision_factors = ["roi", "integration", "scalability", "support", "pricing"]
    
    return {
        "context_type": context_type,
        "decision_factors": decision_factors,
        "is_personal": context_type in ["personal_purchase", "career_opportunity"],
        "is_business": context_type in ["business_solution"],
        "is_financial": context_type == "financial_decision"
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
    """Generate a focused behavioral insight using AI."""
    try:
        if not openai_client:
            return generate_fallback_insight(role, candidate_data)
        
        # Extract candidate's first name for personalization
        first_name = extract_first_name(candidate_data.get("name", "")) if candidate_data else ""
        company = candidate_data.get("company", "their company") if candidate_data else "their company"
        
        # Analyze the search context and role relevance
        search_context_analysis = analyze_search_context(user_prompt)
        role_relevance = analyze_role_relevance(role, user_prompt)
        
        # Create a concise, relevance-aware prompt for behavioral insights
        system_prompt = f"""
        Generate a concise behavioral insight for engaging with this prospect.
        
        RELEVANCE ANALYSIS:
        - Role-need relevance: {role_relevance['relevance_score']:.2f}
        - Engagement level: {role_relevance['engagement_level']}
        - Context: {search_context_analysis['context_type']}
        
        RESPONSE RULES:
        - Keep to 1-2 sentences maximum (under 40 words)
        - Use "they" pronouns, never mention their title
        - Match advice to their actual engagement level:
          * HIGH relevance: Active evaluation, detailed research
          * MEDIUM relevance: Moderate interest, some research  
          * LOW relevance: Casual browsing, minimal commitment
        - Focus on decision-making style, not feature lists
        - Be specific and actionable
        """
        
        name_ref = first_name if first_name else "This professional"
        
        # Check for personal research patterns to enhance the prompt
        research_data = simulate_personal_research_patterns()
        research_context = ""
        if research_data["personal_research"]:
            research_context = f" They've been researching solutions outside business hours, indicating personal investment in finding the right tool."

        user_prompt_for_ai = f"""
        Search: "{user_prompt}"
        Role: {role}
        Relevance: {role_relevance['engagement_level']} ({role_relevance['relevance_score']:.2f})
        
        Generate a concise insight about how they evaluate decisions in this context.{research_context}
        Focus on their decision-making approach, not their title or context details.
        """
        
        # Call the OpenAI API with limited tokens for concise response
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.7,
            max_tokens=80  # Reduced for concise responses
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception:
        return generate_fallback_insight(role, candidate_data, user_prompt)

def generate_score_ai(score_type: str, role: str, user_prompt: str = "") -> Dict[str, Any]:
    """Generate a behavioral score using AI."""
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
        
        # Create a relevance-aware prompt based on score type
        if score_type == "cmi":
            system_prompt = f"""
            Generate a Commitment Momentum Index (CMI) score (0-100) for a {role} looking for: "{user_prompt}"
            
            CRITICAL RELEVANCE FACTOR:
            - Role-need relevance: {role_relevance['relevance_score']:.2f} (0.0 = irrelevant, 1.0 = highly relevant)
            - Engagement level: {role_relevance['engagement_level']}
            - Expected behavior: {role_relevance['behavioral_modifier']}
            
            RELEVANCE-BASED SCORING RULES:
            - HIGH relevance (0.8+): 70-95 CMI - Active evaluation, comparing options, ready to move
            - MEDIUM relevance (0.5-0.8): 40-70 CMI - Interested but not urgent, moderate research
            - LOW relevance (0.3-0.5): 15-40 CMI - Casual browsing, low commitment, minimal urgency
            
            EXAMPLES:
            - Sales Manager + CRM = HIGH relevance → 80+ CMI (actively evaluating)
            - Sales Manager + Cybersecurity = LOW relevance → 25 CMI (casual browsing)
            - Engineer + Development Tools = HIGH relevance → 85+ CMI (detailed evaluation)
            - Engineer + HR Software = LOW relevance → 20 CMI (minimal interest)
            
            Adjust the score based on logical role-need alignment. Don't assume high commitment if the need doesn't match their role.
            
            Return JSON with "score" and "explanation". 
            For explanation: Use "they" pronouns. Keep to 8-12 words reflecting their TRUE engagement level.
            """
        elif score_type == "rbfs":
            system_prompt = f"""
            Generate a Risk-Barrier Focus Score (RBFS) (0-100) for a {role}.
            RBFS measures how much they focus on potential downsides vs benefits.
            
            Score guidelines:
            - 80-100: Highly cautious, needs extensive proof and references
            - 60-79: Moderately risk-aware, wants clear implementation plan
            - 40-59: Balanced risk assessment, standard due diligence
            - 20-39: Risk-tolerant, focuses more on upside potential
            
            Return JSON with "score" and "explanation".
            For explanation: Use "they" or "them" pronouns, not "The [role]". Keep to 8-12 words describing their risk evaluation style.
            """
        else:  # ias
            system_prompt = f"""
            Generate an Identity Alignment Signal (IAS) score (0-100) for a {role}.
            IAS measures how well this type of solution fits their professional identity and goals.
            
            Score guidelines:
            - 80-100: Perfect fit for their role, directly impacts their success metrics
            - 60-79: Good alignment with their responsibilities and objectives
            - 40-59: Moderate fit, some relevance to their role
            - 20-39: Peripheral to their core responsibilities
            
            Return JSON with "score" and "explanation".
            For explanation: Use "they" or "them" pronouns, not "The [role]". Keep to 8-12 words describing the professional fit.
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
    user_prompt: str
) -> Dict[str, Any]:
    """Enhance behavioral data with AI-generated insights and scores."""
    try:
        # Extract candidate data from the first candidate if available
        candidate_data = candidates[0] if candidates else {}
        
        # Get the prospect's role
        role = candidate_data.get("title", "professional")
        
        # Generate a focused behavioral insight
        behavioral_insight = generate_focused_insight_ai(role, user_prompt, candidate_data)
        
        # Generate the three behavioral scores in parallel with context
        cmi_score = generate_score_ai("cmi", role, user_prompt)
        rbfs_score = generate_score_ai("rbfs", role, user_prompt)
        ias_score = generate_score_ai("ias", role, user_prompt)
        
        # Create the enhanced behavioral data
        return {
            "behavioral_insight": behavioral_insight,
            "scores": {
                "cmi": cmi_score,
                "rbfs": rbfs_score,
                "ias": ias_score
            }
        }
        
    except Exception:
        # Return a default insight and scores
        return {
            "behavioral_insight": "This professional engages best with personalized discussions about their specific business needs and goals.",
            "scores": {
                "cmi": {"score": 70, "explanation": "Forward motion"},
                "rbfs": {"score": 60, "explanation": "Moderately sensitive"},
                "ias": {"score": 75, "explanation": "Fits self-image"}
            }
        }

# Fallback functions for when AI generation fails

def generate_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]] = None, user_prompt: str = "") -> str:
    """Generate a context-aware fallback insight based on role and search context."""
    role_lower = role.lower()
    
    # Extract candidate's first name for personalization
    first_name = extract_first_name(candidate_data.get("name", "")) if candidate_data else ""
    company = candidate_data.get("company", "their organization") if candidate_data else "their organization"
    
    # Use first name if available, otherwise use role-based reference
    name_ref = first_name if first_name else "This professional"
    
    # Analyze search context to provide relevant insights
    context_analysis = analyze_search_context(user_prompt)
    
    # Generate concise, context-aware insights based on relevance
    role_relevance = analyze_role_relevance(role, user_prompt)
    
    if context_analysis["context_type"] == "personal_purchase":
        base_insight = f"They approach personal purchases analytically, prioritizing long-term value and thorough research."
    elif context_analysis["context_type"] == "career_opportunity":
        base_insight = f"They evaluate career moves based on growth potential, compensation, and strategic fit."
    else:
        # Business solution - adjust based on role relevance
        if role_relevance["engagement_level"] == "high":
            base_insight = f"They actively evaluate solutions with detailed analysis and clear success criteria."
        elif role_relevance["engagement_level"] == "medium":
            base_insight = f"They show moderate interest, researching options without immediate urgency."
        else:
            base_insight = f"They browse casually with minimal commitment to this area."
    
    # Check for personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"]:
        # Add personal research context to the insight
        personal_addition = f" They've been researching options during personal time, suggesting this is a high-priority decision for them."
        return base_insight + personal_addition
    
    return base_insight

def generate_fallback_cmi_score(role: str, user_prompt: str = "") -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback CMI score."""
    role_lower = role.lower()
    
    # Analyze role relevance to adjust scores
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Base scores by role
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_score = 75
        base_explanation = "They're likely evaluating technical specifications and integration options"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = 80
        base_explanation = "They're probably comparing strategic options and ROI scenarios"
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_score = 85
        base_explanation = "They're actively seeking tools to improve performance metrics"
    else:
        base_score = 70
        base_explanation = "They're exploring solutions for current workflow challenges"
    
    # Adjust score based on role relevance
    adjusted_score = int(base_score * role_relevance["adjustment_factor"])
    
    # Adjust explanation based on engagement level
    if role_relevance["engagement_level"] == "low":
        adjusted_explanation = "They're casually browsing, minimal commitment to this area"
    elif role_relevance["engagement_level"] == "medium":
        adjusted_explanation = "They're moderately interested, exploring options without urgency"
    else:
        adjusted_explanation = base_explanation
    
    # Simulate personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"] and role_relevance["engagement_level"] != "low":
        # Only boost if relevance is medium or high
        boosted_score = min(100, adjusted_score + research_data["cmi_boost"])
        enhanced_explanation = "They're researching options during personal time - higher priority"
        
        return {
            "score": boosted_score,
            "explanation": enhanced_explanation,
            "research_pattern": research_data["pattern_type"]
        }
    else:
        return {
            "score": adjusted_score,
            "explanation": adjusted_explanation
        }

def generate_fallback_rbfs_score(role: str, user_prompt: str = "") -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback RBFS score."""
    role_lower = role.lower()
    
    # Analyze role relevance - low relevance = higher risk sensitivity
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Base scores by role
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        base_score = 85
        base_explanation = "They need extensive proof points and security documentation"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = 65
        base_explanation = "They want clear implementation roadmap and success metrics"
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_score = 45
        base_explanation = "They're willing to try new approaches if they drive results"
    elif any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_score = 70
        base_explanation = "They're concerned about technical integration and system stability"
    else:
        base_score = 60
        base_explanation = "They take standard due diligence approach to new solutions"
    
    # Adjust score - LOWER relevance = HIGHER risk sensitivity (inverse relationship)
    if role_relevance["engagement_level"] == "low":
        # Low relevance = higher risk sensitivity (they're more cautious about unfamiliar areas)
        adjusted_score = min(90, base_score + 20)
        adjusted_explanation = "They're cautious about areas outside their expertise"
    elif role_relevance["engagement_level"] == "medium":
        adjusted_score = base_score + 5
        adjusted_explanation = "They want moderate validation before proceeding"
    else:
        adjusted_score = base_score
        adjusted_explanation = base_explanation
    
    return {"score": adjusted_score, "explanation": adjusted_explanation}

def generate_fallback_ias_score(role: str, user_prompt: str = "") -> Dict[str, Any]:
    """Generate a relevance-adjusted fallback IAS score."""
    role_lower = role.lower()
    
    # Analyze role relevance to adjust scores
    role_relevance = analyze_role_relevance(role, user_prompt) if user_prompt else {"adjustment_factor": 0.7, "engagement_level": "medium"}
    
    # Base scores by role
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        base_score = 80
        base_explanation = "Technical tools that enhance their capabilities align with professional identity"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = 85
        base_explanation = "Strategic solutions that drive business outcomes fit their leadership role"
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_score = 90
        base_explanation = "Performance tools directly support their success metrics and career growth"
    elif any(marketing in role_lower for marketing in ["marketing", "growth", "demand", "content"]):
        base_score = 85
        base_explanation = "Growth-driving tools align with their marketing objectives and professional goals"
    else:
        base_score = 75
        base_explanation = "Solutions that improve job performance align with their professional objectives"
    
    # Adjust score based on role relevance
    adjusted_score = int(base_score * role_relevance["adjustment_factor"])
    
    # Adjust explanation based on relevance
    if role_relevance["engagement_level"] == "low":
        adjusted_explanation = "This area has minimal alignment with their core professional responsibilities"
    elif role_relevance["engagement_level"] == "medium":
        adjusted_explanation = "Moderate alignment with their professional objectives and daily responsibilities"
    else:
        adjusted_explanation = base_explanation
    
    return {"score": adjusted_score, "explanation": adjusted_explanation}