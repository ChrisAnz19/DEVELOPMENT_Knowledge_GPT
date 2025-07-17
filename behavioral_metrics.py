"""
Behavioral Metrics Module

This module provides specialized behavioral metrics for analyzing prospect behavior:
- Communication Maturity Index (CMI)
- Risk-Barrier Focus Score (RBFS)
- Identity Alignment Signal (IAS)

These metrics provide deeper insights into prospect behavior, helping users better understand
communication preferences, risk sensitivity, and professional identity alignment.
"""

import logging
import random
from typing import Dict, List, Optional, Any, Union
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AI-based behavioral metrics functions
try:
    from behavioral_metrics_ai import (
        generate_focused_insight_ai,
        generate_cmi_score_ai,
        generate_rbfs_score_ai,
        generate_ias_score_ai,
        enhance_behavioral_data_ai
    )
    AI_METRICS_AVAILABLE = True
    logger.info("AI-based behavioral metrics available")
except ImportError as e:
    logger.warning(f"AI-based behavioral metrics not available: {str(e)}")
    AI_METRICS_AVAILABLE = False

def generate_concise_insight(role: str, user_prompt: str) -> str:
    """
    Generates a concise behavioral insight based on the prospect's role.
    
    Args:
        role: The prospect's job title
        user_prompt: The user's search criteria
        
    Returns:
        A concise behavioral insight string
    """
    role_lower = role.lower()
    
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing."
    
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return "This executive values direct communication and strategic impact. Begin by acknowledging their business challenges, then present your solution with clear ROI metrics and competitive advantages. Focus on how your offering solves their specific business problems rather than technical details."
    
    # Sales roles
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        return "This sales professional responds best to competitive differentiation and concrete outcomes. Start conversations by asking about their current sales targets, then demonstrate how your solution can help them exceed goals and outperform competitors."
    
    # Marketing roles
    elif any(mktg in role_lower for mktg in ["market", "brand", "growth", "communications"]):
        return "This marketing leader values measurable impact and brand alignment. Begin by acknowledging their current marketing initiatives, then present your solution with specific metrics on audience engagement and brand enhancement."
    
    # Product roles
    elif any(prod in role_lower for prod in ["product", "design", "ux"]):
        return "This product professional prioritizes user experience and implementation simplicity. Start conversations by asking about their current product challenges, then demonstrate how your solution enhances user satisfaction while minimizing integration complexity."
    
    # Management roles
    elif any(mgmt in role_lower for mgmt in ["manager", "director", "vp", "head", "lead"]):
        return "This leader balances strategic vision with practical implementation. Begin by acknowledging their team's objectives, then present your solution with both high-level benefits and specific implementation details that address their organizational needs."
    
    # HR roles
    elif any(hr in role_lower for hr in ["hr", "people", "talent", "recruit"]):
        return "This HR professional focuses on organizational culture and talent development. Start conversations by asking about their current people challenges, then demonstrate how your solution supports their talent strategy and enhances employee experience."
    
    # Finance roles
    elif any(fin in role_lower for fin in ["finance", "accounting", "controller"]):
        return "This finance professional requires clear metrics and ROI calculations. Begin by acknowledging their financial priorities, then present your solution with detailed cost-benefit analysis and specific examples of financial impact."
    
    # Default for other roles
    else:
        return "This professional responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits."

def generate_cmi_score(role: str) -> Dict[str, Any]:
    """
    Generates a Communication Maturity Index score based on the prospect's role.
    
    Args:
        role: The prospect's job title
        
    Returns:
        A dictionary with score and explanation
    """
    role_lower = role.lower()
    
    # Technical roles prefer direct, technical communication
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        score = random.randint(80, 95)
        explanation = "High communication maturity index indicates preference for direct, technical communication with specific examples."
    
    # Executive roles often prefer high-level strategic communication
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        score = random.randint(70, 90)
        explanation = "Strong communication maturity index suggests this executive values clear, concise communication focused on strategic impact and outcomes."
    
    # Sales roles typically prefer persuasive, outcome-focused communication
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        score = random.randint(75, 90)
        explanation = "High communication maturity index indicates preference for persuasive communication with clear value propositions and competitive differentiation."
    
    # Default for other roles
    else:
        score = random.randint(60, 85)
        explanation = "Moderate to high communication maturity index suggests balanced communication with both conceptual and practical elements."
    
    return {
        "score": score,
        "explanation": explanation
    }

def generate_rbfs_score(role: str) -> Dict[str, Any]:
    """
    Generates a Risk-Barrier Focus Score based on the prospect's role.
    
    Args:
        role: The prospect's job title
        
    Returns:
        A dictionary with score and explanation
    """
    role_lower = role.lower()
    
    # Finance and legal roles tend to be more risk-averse
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        score = random.randint(75, 95)
        explanation = "High risk-barrier focus score indicates this professional is risk-averse and requires thorough validation and risk mitigation strategies."
    
    # Executive roles often balance risk and opportunity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        score = random.randint(60, 80)
        explanation = "Moderate risk-barrier focus score suggests this executive balances innovation with practical considerations. Present both opportunities and risk mitigation strategies."
    
    # Innovation and creative roles tend to be more risk-tolerant
    elif any(innov in role_lower for innov in ["innovation", "creative", "research", "design"]):
        score = random.randint(30, 60)
        explanation = "Lower risk-barrier focus score indicates this professional is more opportunity-focused than risk-averse. Emphasize possibilities and innovative aspects."
    
    # Default for other roles
    else:
        score = random.randint(50, 75)
        explanation = "Moderate risk-barrier focus score suggests balancing opportunity messaging with appropriate risk mitigation."
    
    return {
        "score": score,
        "explanation": explanation
    }

def generate_ias_score(role: str) -> Dict[str, Any]:
    """
    Generates an Identity Alignment Signal score based on the prospect's role.
    
    Args:
        role: The prospect's job title
        
    Returns:
        A dictionary with score and explanation
    """
    role_lower = role.lower()
    
    # Technical specialists often strongly identify with their expertise
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        score = random.randint(80, 95)
        explanation = "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
    
    # Executive roles often have strong professional identity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        score = random.randint(85, 98)
        explanation = "Very high identity alignment signal indicates this executive strongly identifies with their leadership role and values being recognized for their strategic vision."
    
    # Creative roles often have strong identity alignment
    elif any(creative in role_lower for creative in ["design", "creative", "artist", "writer"]):
        score = random.randint(75, 90)
        explanation = "High identity alignment signal shows this professional strongly identifies with their creative abilities and innovative thinking."
    
    # Default for other roles
    else:
        score = random.randint(60, 85)
        explanation = "Moderate to high identity alignment signal suggests this professional identifies with their role but maintains a balanced professional identity."
    
    return {
        "score": score,
        "explanation": explanation
    }

def enhance_behavioral_data(
    behavioral_data: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    user_prompt: str,
    industry_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhances existing behavioral data with a focused behavioral insight and three behavioral scores.
    Uses AI-based generation when available, falls back to rule-based generation otherwise.
    
    Args:
        behavioral_data: Existing behavioral data
        candidates: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        Enhanced behavioral data with focused insight and scores
    """
    try:
        # Check if we should use AI-based behavioral metrics
        use_ai = AI_METRICS_AVAILABLE and os.getenv('USE_AI_BEHAVIORAL_METRICS', 'true').lower() == 'true'
        
        if use_ai:
            logger.info("Using AI-based behavioral metrics")
            return enhance_behavioral_data_ai(behavioral_data, candidates, user_prompt, industry_context)
        
        # Fall back to rule-based behavioral metrics
        logger.info("Using rule-based behavioral metrics")
        
        # If behavioral_data is None, initialize with empty dict
        if behavioral_data is None:
            logger.warning("No behavioral data provided to enhance_behavioral_data")
            behavioral_data = {}
            
        # Validate input data
        if not isinstance(behavioral_data, dict):
            logger.error(f"Invalid behavioral_data type: {type(behavioral_data)}")
            behavioral_data = {}
            
        # Extract candidate data from the first candidate if available
        candidate_data = {}
        if candidates and len(candidates) > 0:
            candidate_data = candidates[0]
        
        # Get the prospect's role
        role = candidate_data.get("title", "")
        
        # Generate a focused behavioral insight
        behavioral_insight = generate_concise_insight(role, user_prompt)
        
        # Generate the three behavioral scores
        cmi_score = generate_cmi_score(role)
        rbfs_score = generate_rbfs_score(role)
        ias_score = generate_ias_score(role)
        
        # Create the enhanced behavioral data
        enhanced_data = {
            "behavioral_insight": behavioral_insight,
            "scores": {
                "cmi": cmi_score,
                "rbfs": rbfs_score,
                "ias": ias_score
            }
        }
        
        return enhanced_data
        
    except Exception as e:
        logger.error(f"Error enhancing behavioral data: {str(e)}")
        # Return a default insight and scores if enhancement fails
        return {
            "behavioral_insight": "This professional responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits.",
            "scores": {
                "cmi": {
                    "score": 70,
                    "explanation": "Moderate communication maturity index suggests balanced communication approach."
                },
                "rbfs": {
                    "score": 65,
                    "explanation": "Moderate risk-barrier focus score indicates balanced approach to risk and opportunity."
                },
                "ias": {
                    "score": 75,
                    "explanation": "Moderate to high identity alignment signal suggests professional identifies with their role."
                }
            }
        }