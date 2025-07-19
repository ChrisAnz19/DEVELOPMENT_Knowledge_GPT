"""
Optimized Behavioral Metrics AI Module

This module provides AI-powered behavioral metrics for analyzing prospect behavior:
- Commitment Momentum Index (CMI)
- Risk-Barrier Focus Score (RBFS)
- Identity Alignment Signal (IAS)
"""

import logging
import json
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

def generate_focused_insight_ai(role: str, user_prompt: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a focused behavioral insight using AI."""
    try:
        if not openai_client:
            return generate_fallback_insight(role, candidate_data)
        
        # Extract candidate's first name for personalization
        first_name = extract_first_name(candidate_data.get("name", "")) if candidate_data else ""
        
        # Create a focused prompt based on behavioral metrics
        system_prompt = """
        Generate an engagement strategy based on these behavioral metrics:
        
        1. Commitment Momentum Index (CMI): Forward motion vs idle curiosity
           - High CMI: Decision moving from "thinking about it" to "doing it"
           - Timing outreach to this upswing dramatically lifts response rates
        
        2. Risk-Barrier Focus Score (RBFS): How sensitive to downside and friction
           - High RBFS: Risk-averse prospects need assurance (case studies, guarantees, references)
        
        3. Identity Alignment Signal (IAS): Whether choice fits their self-image/goals
           - High IAS: Prospect feels personally aligned, emotional friction drops
           - Low IAS: Must reframe narrative to their aspirations
        
        Provide 2-3 sentences of specific, actionable guidance for outreach timing and approach.
        """
        
        name_instruction = f"The candidate's first name is '{first_name}'. " if first_name else "Use their role title. "
        
        user_prompt_for_ai = f"""
        {name_instruction}Generate an engagement strategy for a {role} found in search for "{user_prompt}".
        Focus on timing, risk sensitivity, and personal alignment factors.
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
            "behavioral_insight": "This professional responds best to personalized engagement focusing on their specific business challenges.",
            "scores": {
                "cmi": {"score": 70, "explanation": "Forward motion"},
                "rbfs": {"score": 60, "explanation": "Moderately sensitive"},
                "ias": {"score": 75, "explanation": "Fits self-image"}
            }
        }

# Fallback functions for when AI generation fails

def generate_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a fallback insight based on role."""
    role_lower = role.lower()
    
    # Extract candidate's first name for personalization
    first_name = extract_first_name(candidate_data.get("name", "")) if candidate_data else ""
    
    # Use first name if available, otherwise use role-based reference
    name_ref = first_name if first_name else "This professional"
    
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return f"{name_ref} responds best to detailed, evidence-based communication with concrete examples and performance metrics."
    
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return f"{name_ref} values direct communication and strategic impact. Focus on clear ROI metrics and competitive advantages."
    
    # Sales roles
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        return f"{name_ref} responds best to competitive differentiation and concrete outcomes that help exceed goals."
    
    # Default for other roles
    else:
        return f"{name_ref} responds best to personalized engagement focusing on their specific business challenges."

def generate_fallback_cmi_score(role: str) -> Dict[str, Any]:
    """Generate a fallback CMI score based on role."""
    role_lower = role.lower()
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return {"score": 85, "explanation": "Forward motion"}
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {"score": 80, "explanation": "Lining up next steps"}
    # Default for other roles
    else:
        return {"score": 70, "explanation": "Past research phase"}

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