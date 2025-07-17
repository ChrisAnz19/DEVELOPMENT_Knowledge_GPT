"""
Behavioral Metrics AI Module

This module provides AI-powered behavioral metrics for analyzing prospect behavior:
- Communication Maturity Index (CMI)
- Risk-Barrier Focus Score (RBFS)
- Identity Alignment Signal (IAS)

These metrics provide deeper insights into prospect behavior, helping users better understand
communication preferences, risk sensitivity, and professional identity alignment.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
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
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load OpenAI API key: {str(e)}")
    
    openai_client = openai.OpenAI(api_key=openai_api_key)
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    openai_client = None

def generate_focused_insight_ai(
    role: str,
    user_prompt: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a focused behavioral insight using AI based on the prospect's role and data.
    
    Args:
        role: The prospect's job title
        user_prompt: The user's search criteria
        candidate_data: Optional additional data about the candidate
        
    Returns:
        A focused behavioral insight string
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback insight")
            return generate_fallback_insight(role)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in behavioral analysis and sales psychology. Your task is to generate a focused, 
        actionable behavioral insight for engaging with a prospect. The insight should be specific, 
        tailored to the prospect's role and psychology, and provide clear guidance on how to engage effectively.
        
        Focus on these three behavioral metrics:
        1. Commitment Momentum Index (CMI): Forward motion vs. idle curiosity—i.e., is the person merely researching or already lining up next steps?
        2. Risk-Barrier Focus Score (RBFS): How sensitive the person is to downside and friction.
        3. Identity Alignment Signal (IAS): Whether the choice fits their self-image / goals—key across career, investing, and purchasing.
        
        Your insight should be 2-3 sentences and should provide specific, actionable guidance on how to engage with the prospect.
        """
        
        user_prompt_for_ai = f"""
        Generate a focused behavioral insight for a {role} who was found in a search for "{user_prompt}".
        
        Additional information about the prospect:
        {candidate_info}
        
        The insight should be specific to this role and search context, providing actionable guidance on how to engage with them.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-4",  # Use GPT-4 for higher quality insights
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # Extract and return the insight
        insight = response.choices[0].message.content.strip()
        logger.info(f"Generated AI insight for {role}: {insight[:50]}...")
        return insight
        
    except Exception as e:
        logger.error(f"Error generating focused insight: {str(e)}")
        return generate_fallback_insight(role)

def generate_cmi_score_ai(
    role: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a Communication Maturity Index score using AI based on the prospect's role and data.
    
    Args:
        role: The prospect's job title
        candidate_data: Optional additional data about the candidate
        
    Returns:
        A dictionary with score and explanation
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback CMI score")
            return generate_fallback_cmi_score(role)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in communication psychology and behavioral analysis. Your task is to generate a 
        Communication Maturity Index (CMI) score for a prospect based on their role and available information.
        
        The CMI measures how the prospect prefers to communicate and receive information:
        - High scores (80-100): Prefers direct, detailed, and technical communication
        - Medium scores (50-79): Balances technical and conceptual communication
        - Low scores (0-49): Prefers high-level, conceptual communication
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A 1-2 sentence explanation of the score and what it means for communication
        """
        
        user_prompt_for_ai = f"""
        Generate a Communication Maturity Index (CMI) score for a {role}.
        
        Additional information about the prospect:
        {candidate_info}
        
        Return only a JSON object with "score" (0-100) and "explanation" fields.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # GPT-3.5 is sufficient for scoring
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        # Extract and parse the JSON response
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Validate the result
        if "score" not in result or "explanation" not in result:
            logger.warning(f"Invalid CMI score format: {result}")
            return generate_fallback_cmi_score(role)
        
        # Ensure score is within range
        result["score"] = max(0, min(100, int(result["score"])))
        
        logger.info(f"Generated AI CMI score for {role}: {result['score']}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating CMI score: {str(e)}")
        return generate_fallback_cmi_score(role)

def generate_rbfs_score_ai(
    role: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a Risk-Barrier Focus Score using AI based on the prospect's role and data.
    
    Args:
        role: The prospect's job title
        candidate_data: Optional additional data about the candidate
        
    Returns:
        A dictionary with score and explanation
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback RBFS score")
            return generate_fallback_rbfs_score(role)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in risk psychology and decision-making behavior. Your task is to generate a 
        Risk-Barrier Focus Score (RBFS) for a prospect based on their role and available information.
        
        The RBFS indicates how the prospect approaches risk and decision barriers:
        - High scores (80-100): Highly risk-averse, needs extensive validation
        - Medium scores (50-79): Balanced approach to risk, needs moderate validation
        - Low scores (0-49): Risk-tolerant, focuses on opportunities over barriers
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A 1-2 sentence explanation of the score and what it means for engagement
        """
        
        user_prompt_for_ai = f"""
        Generate a Risk-Barrier Focus Score (RBFS) for a {role}.
        
        Additional information about the prospect:
        {candidate_info}
        
        Return only a JSON object with "score" (0-100) and "explanation" fields.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # GPT-3.5 is sufficient for scoring
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        # Extract and parse the JSON response
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Validate the result
        if "score" not in result or "explanation" not in result:
            logger.warning(f"Invalid RBFS score format: {result}")
            return generate_fallback_rbfs_score(role)
        
        # Ensure score is within range
        result["score"] = max(0, min(100, int(result["score"])))
        
        logger.info(f"Generated AI RBFS score for {role}: {result['score']}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating RBFS score: {str(e)}")
        return generate_fallback_rbfs_score(role)

def generate_ias_score_ai(
    role: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates an Identity Alignment Signal score using AI based on the prospect's role and data.
    
    Args:
        role: The prospect's job title
        candidate_data: Optional additional data about the candidate
        
    Returns:
        A dictionary with score and explanation
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback IAS score")
            return generate_fallback_ias_score(role)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in professional identity psychology and behavioral analysis. Your task is to generate an 
        Identity Alignment Signal (IAS) score for a prospect based on their role and available information.
        
        The IAS measures how strongly the prospect identifies with their professional role:
        - High scores (80-100): Strongly identifies with professional role and expertise
        - Medium scores (50-79): Balanced identity between professional and other aspects
        - Low scores (0-49): Less identification with professional role, more with other aspects
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A 1-2 sentence explanation of the score and what it means for engagement
        """
        
        user_prompt_for_ai = f"""
        Generate an Identity Alignment Signal (IAS) score for a {role}.
        
        Additional information about the prospect:
        {candidate_info}
        
        Return only a JSON object with "score" (0-100) and "explanation" fields.
        """
        
        # Call the OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # GPT-3.5 is sufficient for scoring
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        # Extract and parse the JSON response
        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)
        
        # Validate the result
        if "score" not in result or "explanation" not in result:
            logger.warning(f"Invalid IAS score format: {result}")
            return generate_fallback_ias_score(role)
        
        # Ensure score is within range
        result["score"] = max(0, min(100, int(result["score"])))
        
        logger.info(f"Generated AI IAS score for {role}: {result['score']}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating IAS score: {str(e)}")
        return generate_fallback_ias_score(role)

def enhance_behavioral_data_ai(
    behavioral_data: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    user_prompt: str,
    industry_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enhances existing behavioral data with AI-generated focused insight and three behavioral scores.
    
    Args:
        behavioral_data: Existing behavioral data
        candidates: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        Enhanced behavioral data with focused insight and scores
    """
    try:
        # If behavioral_data is None, initialize with empty dict
        if behavioral_data is None:
            logger.warning("No behavioral data provided to enhance_behavioral_data_ai")
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
        behavioral_insight = generate_focused_insight_ai(role, user_prompt, candidate_data)
        
        # Generate the three behavioral scores
        cmi_score = generate_cmi_score_ai(role, candidate_data)
        rbfs_score = generate_rbfs_score_ai(role, candidate_data)
        ias_score = generate_ias_score_ai(role, candidate_data)
        
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

def extract_candidate_info(candidate_data: Optional[Dict[str, Any]]) -> str:
    """
    Extracts relevant information from candidate data for AI prompts.
    
    Args:
        candidate_data: Dictionary containing candidate information
        
    Returns:
        String with formatted candidate information
    """
    if not candidate_data:
        return "No additional information available."
    
    info_parts = []
    
    # Add basic information
    if "title" in candidate_data:
        info_parts.append(f"Title: {candidate_data['title']}")
    
    if "company" in candidate_data:
        info_parts.append(f"Company: {candidate_data['company']}")
    
    if "location" in candidate_data:
        info_parts.append(f"Location: {candidate_data['location']}")
    
    # Add LinkedIn profile information if available
    if "linkedin_profile" in candidate_data and isinstance(candidate_data["linkedin_profile"], dict):
        linkedin = candidate_data["linkedin_profile"]
        
        if "summary" in linkedin and linkedin["summary"]:
            info_parts.append(f"Profile Summary: {linkedin['summary']}")
        
        if "experience" in linkedin and isinstance(linkedin["experience"], list) and linkedin["experience"]:
            experience = linkedin["experience"]
            recent_exp = experience[0] if experience else {}
            if isinstance(recent_exp, dict):
                exp_desc = recent_exp.get("description", "")
                if exp_desc:
                    info_parts.append(f"Recent Experience: {exp_desc[:200]}...")
        
        if "skills" in linkedin and isinstance(linkedin["skills"], list) and linkedin["skills"]:
            skills = ", ".join(linkedin["skills"][:10])  # Limit to first 10 skills
            info_parts.append(f"Skills: {skills}")
    
    # Add reasons if available
    if "reasons" in candidate_data and isinstance(candidate_data["reasons"], list) and candidate_data["reasons"]:
        reasons = ", ".join(candidate_data["reasons"])
        info_parts.append(f"Match Reasons: {reasons}")
    
    # Join all parts with newlines
    result = "\n".join(info_parts)
    
    # If no information was extracted, return a default message
    if not result:
        return "No additional information available."
    
    return result

# Fallback functions for when AI generation fails

def generate_fallback_insight(role: str) -> str:
    """Generate a fallback insight based on role."""
    role_lower = role.lower()
    
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return "This technical professional responds best to detailed, evidence-based communication. Start conversations by asking about their current technical challenges, then demonstrate how your solution addresses specific pain points with concrete examples and performance metrics."
    
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return "This executive values direct communication and strategic impact. Begin by acknowledging their business challenges, then present your solution with clear ROI metrics and competitive advantages. Focus on how your offering solves their specific business problems rather than technical details."
    
    # Sales roles
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        return "This sales professional responds best to competitive differentiation and concrete outcomes. Start conversations by asking about their current sales targets, then demonstrate how your solution can help them exceed goals and outperform competitors."
    
    # Default for other roles
    else:
        return "This professional responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits."

def generate_fallback_cmi_score(role: str) -> Dict[str, Any]:
    """Generate a fallback CMI score based on role."""
    role_lower = role.lower()
    
    # Technical roles prefer direct, technical communication
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return {
            "score": 85,
            "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
        }
    
    # Executive roles often prefer high-level strategic communication
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 80,
            "explanation": "Strong communication maturity index suggests this executive values clear, concise communication focused on strategic impact and outcomes."
        }
    
    # Default for other roles
    else:
        return {
            "score": 70,
            "explanation": "Moderate to high communication maturity index suggests balanced communication with both conceptual and practical elements."
        }

def generate_fallback_rbfs_score(role: str) -> Dict[str, Any]:
    """Generate a fallback RBFS score based on role."""
    role_lower = role.lower()
    
    # Finance and legal roles tend to be more risk-averse
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        return {
            "score": 85,
            "explanation": "High risk-barrier focus score indicates this professional is risk-averse and requires thorough validation and risk mitigation strategies."
        }
    
    # Executive roles often balance risk and opportunity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 70,
            "explanation": "Moderate risk-barrier focus score suggests this executive balances innovation with practical considerations. Present both opportunities and risk mitigation strategies."
        }
    
    # Default for other roles
    else:
        return {
            "score": 65,
            "explanation": "Moderate risk-barrier focus score suggests balancing opportunity messaging with appropriate risk mitigation."
        }

def generate_fallback_ias_score(role: str) -> Dict[str, Any]:
    """Generate a fallback IAS score based on role."""
    role_lower = role.lower()
    
    # Technical specialists often strongly identify with their expertise
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        return {
            "score": 85,
            "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
        }
    
    # Executive roles often have strong professional identity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 90,
            "explanation": "Very high identity alignment signal indicates this executive strongly identifies with their leadership role and values being recognized for their strategic vision."
        }
    
    # Default for other roles
    else:
        return {
            "score": 75,
            "explanation": "Moderate to high identity alignment signal suggests this professional identifies with their role but maintains a balanced professional identity."
        }