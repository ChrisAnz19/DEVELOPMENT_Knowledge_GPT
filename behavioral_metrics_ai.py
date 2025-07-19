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
        
        # Create a more specific prompt for sales engagement insights
        system_prompt = """
        You are a sales psychology expert. Generate a practical behavioral insight for engaging with this prospect.
        
        Focus on:
        - What motivates them professionally based on their role
        - How they likely evaluate new solutions or vendors
        - What communication style would resonate with them
        - What concerns or priorities they probably have
        
        Be specific and actionable. Avoid generic phrases like "high commitment" or "risk sensitive."
        Instead, focus on practical insights about their decision-making style and professional priorities.
        
        Keep it to 1-2 sentences maximum.
        """
        
        name_ref = first_name if first_name else "This professional"
        
        # Check for personal research patterns to enhance the prompt
        research_data = simulate_personal_research_patterns()
        research_context = ""
        if research_data["personal_research"]:
            research_context = f" They've been researching solutions outside business hours, indicating personal investment in finding the right tool."

        user_prompt_for_ai = f"""
        Role: {role}
        Company: {company}
        Search context: "{user_prompt}"
        
        Generate a behavioral insight about how {name_ref} likely evaluates and makes decisions about new solutions in their role.{research_context}
        Focus on their professional mindset and decision-making style, not generic commitment levels.
        """
        
        # Call the OpenAI API with reduced tokens
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.7,
            max_tokens=120
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception:
        return generate_fallback_insight(role, candidate_data)

def generate_score_ai(score_type: str, role: str) -> Dict[str, Any]:
    """Generate a behavioral score using AI."""
    try:
        if not openai_client:
            if score_type == "cmi":
                return generate_fallback_cmi_score(role)
            elif score_type == "rbfs":
                return generate_fallback_rbfs_score(role)
            else:
                return generate_fallback_ias_score(role)
        
        # Create a specific prompt based on score type
        if score_type == "cmi":
            system_prompt = f"""
            Generate a Commitment Momentum Index (CMI) score (0-100) for a {role}.
            CMI measures how actively they're moving toward a decision vs just browsing.
            
            Score guidelines:
            - 80-100: Actively evaluating vendors, requesting demos, or comparing options
            - 60-79: Past initial research phase, exploring specific solutions
            - 40-59: Early research mode, gathering information
            - 20-39: Casual browsing, no immediate timeline
            
            Return JSON with "score" and "explanation" (describe their likely stage, not generic commitment level).
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
            
            Return JSON with "score" and "explanation" (describe their risk evaluation style).
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
            
            Return JSON with "score" and "explanation" (describe the professional fit).
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
        
        # Generate the three behavioral scores in parallel
        cmi_score = generate_score_ai("cmi", role)
        rbfs_score = generate_score_ai("rbfs", role)
        ias_score = generate_score_ai("ias", role)
        
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

def generate_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a fallback insight based on role with personal research patterns."""
    role_lower = role.lower()
    
    # Extract candidate's first name for personalization
    first_name = extract_first_name(candidate_data.get("name", "")) if candidate_data else ""
    company = candidate_data.get("company", "their organization") if candidate_data else "their organization"
    
    # Use first name if available, otherwise use role-based reference
    name_ref = first_name if first_name else "This professional"
    
    # More specific insights by role focusing on decision-making style
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_insight = f"{name_ref} likely evaluates tools based on technical specifications, integration capabilities, and developer experience rather than high-level business benefits."
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_insight = f"{name_ref} probably focuses on ROI, competitive advantage, and how solutions align with {company}'s strategic objectives when making vendor decisions."
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_insight = f"{name_ref} likely prioritizes tools that directly impact pipeline generation, conversion rates, and quota attainment over features that don't drive revenue."
    elif any(marketing in role_lower for marketing in ["marketing", "growth", "demand", "content"]):
        base_insight = f"{name_ref} probably evaluates solutions based on attribution capabilities, campaign performance metrics, and integration with existing martech stack."
    elif any(ops in role_lower for ops in ["operations", "manager", "director", "coordinator"]):
        base_insight = f"{name_ref} likely focuses on efficiency gains, process automation, and ease of implementation when considering new operational tools."
    else:
        base_insight = f"{name_ref} probably evaluates new solutions based on how they solve specific pain points in their current workflow and deliver measurable improvements."
    
    # Check for personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"]:
        # Add personal research context to the insight
        personal_addition = f" They've been researching solutions during personal time, suggesting this is a high-priority initiative."
        return base_insight + personal_addition
    
    return base_insight

def generate_fallback_cmi_score(role: str) -> Dict[str, Any]:
    """Generate a fallback CMI score based on role with personal research simulation."""
    role_lower = role.lower()
    
    # Base scores by role with specific explanations
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_score = 75
        base_explanation = "Likely evaluating technical specifications and integration options"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = 80
        base_explanation = "Probably comparing strategic options and ROI scenarios"
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        base_score = 85
        base_explanation = "Actively seeking tools to improve performance metrics"
    else:
        base_score = 70
        base_explanation = "Exploring solutions for current workflow challenges"
    
    # Simulate personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"]:
        # Boost CMI score for personal research patterns
        boosted_score = min(100, base_score + research_data["cmi_boost"])
        enhanced_explanation = "Researching solutions during personal time - high priority initiative"
        
        return {
            "score": boosted_score,
            "explanation": enhanced_explanation,
            "research_pattern": research_data["pattern_type"]
        }
    else:
        return {
            "score": base_score,
            "explanation": base_explanation
        }

def generate_fallback_rbfs_score(role: str) -> Dict[str, Any]:
    """Generate a fallback RBFS score based on role."""
    role_lower = role.lower()
    
    # Finance and legal roles tend to be more risk-averse
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        return {"score": 85, "explanation": "Needs extensive proof points and security documentation"}
    
    # Executive roles often balance risk and opportunity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {"score": 65, "explanation": "Wants clear implementation roadmap and success metrics"}
    
    # Sales roles are often more risk-tolerant for performance gains
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        return {"score": 45, "explanation": "Willing to try new approaches if they drive results"}
    
    # Technical roles focus on implementation risks
    elif any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return {"score": 70, "explanation": "Concerned about technical integration and system stability"}
    
    # Default for other roles
    else:
        return {"score": 60, "explanation": "Standard due diligence approach to new solutions"}

def generate_fallback_ias_score(role: str) -> Dict[str, Any]:
    """Generate a fallback IAS score based on role."""
    role_lower = role.lower()
    
    # Technical specialists often strongly identify with their expertise
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        return {"score": 80, "explanation": "Tools that enhance technical capabilities align with professional identity"}
    
    # Executive roles often have strong professional identity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {"score": 85, "explanation": "Strategic solutions that drive business outcomes fit leadership role"}
    
    # Sales roles strongly identify with performance and results
    elif any(sales in role_lower for sales in ["sales", "account", "business development", "revenue"]):
        return {"score": 90, "explanation": "Performance-enhancing tools directly support success metrics and career growth"}
    
    # Marketing roles identify with growth and customer acquisition
    elif any(marketing in role_lower for marketing in ["marketing", "growth", "demand", "content"]):
        return {"score": 85, "explanation": "Growth-driving tools align with marketing objectives and professional goals"}
    
    # Default for other roles
    else:
        return {"score": 75, "explanation": "Solutions that improve job performance align with professional objectives"}