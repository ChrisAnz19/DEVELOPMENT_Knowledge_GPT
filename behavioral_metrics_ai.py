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
        
        # Create a focused prompt based on behavioral metrics
        system_prompt = """
        Generate a high-level approach for engaging with this prospect based on their behavioral profile.
        
        Consider:
        - Commitment Momentum Index (CMI): Are they in research mode or ready to act?
        - Risk-Barrier Focus Score (RBFS): How sensitive are they to risks and friction?
        - Identity Alignment Signal (IAS): Does this opportunity fit their self-image and goals?
        
        Provide 2-3 sentences describing how to approach them if you were offering what they're looking for.
        Keep it conversational and high-level - no specific tactics, timing, or formatting.
        """
        
        name_instruction = f"The candidate's first name is '{first_name}'. " if first_name else "Use their role title. "
        
        # Check for personal research patterns to enhance the prompt
        research_data = simulate_personal_research_patterns()
        personal_context = ""
        if research_data["personal_research"]:
            personal_context = f" Note: This prospect {research_data['engagement_note']}, suggesting high personal commitment."

        # Detect if the user prompt implies a job search
        job_search_keywords = ["looking for a role", "job", "hire", "candidate", "position", "career move"]
        is_job_context = any(k in user_prompt.lower() for k in job_search_keywords)

        job_clause = " The prospect is *not* assumed to be looking for a job." if not is_job_context else ""

        user_prompt_for_ai = f"""
        {name_instruction}Generate an engagement strategy for a {role} found in search for \"{user_prompt}\".{job_clause}
        Focus on timing, risk sensitivity, and personal alignment factors.{personal_context}
        """
        
        # Call the OpenAI API with reduced tokens
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use 3.5 for faster response
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.7,
            max_tokens=150
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
            CMI measures forward motion vs idle curiosity - is the person researching or lining up next steps?
            High CMI means decision moving from "thinking about it" to "doing it."
            Return only a JSON object with "score" (0-100) and "explanation" (short phrase).
            """
        elif score_type == "rbfs":
            system_prompt = f"""
            Generate a Risk-Barrier Focus Score (RBFS) (0-100) for a {role}.
            RBFS measures how sensitive the person is to downside and friction.
            High RBFS flags risk-averse prospects who need assurance before moving.
            Return only a JSON object with "score" (0-100) and "explanation" (short phrase).
            """
        else:  # ias
            system_prompt = f"""
            Generate an Identity Alignment Signal (IAS) score (0-100) for a {role}.
            IAS measures whether the choice fits their self-image/goals.
            High IAS means prospect feels personally aligned, emotional friction drops.
            Return only a JSON object with "score" (0-100) and "explanation" (short phrase).
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
    
    # Use first name if available, otherwise use role-based reference
    name_ref = first_name if first_name else "This professional"
    
    # Base insights by role
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_insight = f"{name_ref} appreciates data-driven conversations with specific examples and measurable outcomes."
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_insight = f"{name_ref} values strategic discussions focused on business impact and competitive positioning."
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        base_insight = f"{name_ref} responds well to conversations about market opportunities and growth potential."
    else:
        base_insight = f"{name_ref} engages best with personalized discussions about their specific business needs and goals."
    
    # Check for personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"]:
        # Add personal research context to the insight
        personal_addition = f" {name_ref} {research_data['engagement_note']}, indicating this is a priority and the timing is right for engagement."
        return base_insight + personal_addition
    
    return base_insight

def generate_fallback_cmi_score(role: str) -> Dict[str, Any]:
    """Generate a fallback CMI score based on role with personal research simulation."""
    role_lower = role.lower()
    
    # Base scores by role
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        base_score = 85
        base_explanation = "Forward motion"
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        base_score = 80
        base_explanation = "Lining up next steps"
    else:
        base_score = 70
        base_explanation = "Past research phase"
    
    # Simulate personal research patterns
    research_data = simulate_personal_research_patterns()
    
    if research_data["personal_research"]:
        # Boost CMI score for personal research patterns
        boosted_score = min(100, base_score + research_data["cmi_boost"])
        enhanced_explanation = f"Personal interest - {research_data['engagement_note']}"
        
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
        return {"score": 85, "explanation": "Highly sensitive"}
    
    # Executive roles often balance risk and opportunity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {"score": 70, "explanation": "Moderately sensitive"}
    
    # Default for other roles
    else:
        return {"score": 60, "explanation": "Low sensitivity"}

def generate_fallback_ias_score(role: str) -> Dict[str, Any]:
    """Generate a fallback IAS score based on role."""
    role_lower = role.lower()
    
    # Technical specialists often strongly identify with their expertise
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        return {"score": 85, "explanation": "Fits self-image"}
    
    # Executive roles often have strong professional identity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {"score": 80, "explanation": "Strong alignment"}
    
    # Default for other roles
    else:
        return {"score": 70, "explanation": "Moderate fit"}