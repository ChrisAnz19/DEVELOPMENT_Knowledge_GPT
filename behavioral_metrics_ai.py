"""
Behavioral Metrics AI Module

This module provides AI-powered behavioral metrics for analyzing prospect behavior:
- Commitment Momentum Index (CMI): Forward motion vs. idle curiosity—i.e., is the person merely researching or already lining up next steps?
  - Rising share of visits to execution pages (application portals, term-sheet checklists, checkout/pricing, “how to switch…” articles)
  - Shorter intervals between sessions on the same topic
  - Peak in late-night or mobile hits (signals personal, off-hours prioritization)
  High CMI means decision is moving from “thinking about it” to “doing it.” Timing outreach to this upswing dramatically lifts response rates.
- Risk-Barrier Focus Score (RBFS)
- Identity Alignment Signal (IAS)

These metrics provide deeper insights into prospect behavior, helping users better understand
commitment momentum, risk sensitivity, and professional identity alignment.
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

def extract_first_name(full_name: str) -> str:
    """
    Extract first name from full name.
    
    Args:
        full_name: The candidate's full name
        
    Returns:
        The first name, or empty string if not available
    """
    if not full_name or not isinstance(full_name, str):
        return ""
    
    # Handle common name formats
    name_parts = full_name.strip().split()
    if name_parts:
        return name_parts[0]
    return ""

def generate_focused_insight_ai(
    role: str,
    user_prompt: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a focused behavioral insight using AI based on the prospect's role and data.
    Uses the candidate's first name for personalization.
    
    Args:
        role: The prospect's job title
        user_prompt: The user's search criteria
        candidate_data: Optional additional data about the candidate
        
    Returns:
        A focused behavioral insight string with personalized name usage
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback insight")
            return generate_fallback_insight(role, candidate_data)
        
        # Extract candidate's first name for personalization
        candidate_name = candidate_data.get("name", "") if candidate_data else ""
        first_name = extract_first_name(candidate_name)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in behavioral analysis and sales psychology. Your task is to generate a focused, 
        actionable behavioral insight for engaging with a prospect. The insight should be specific, 
        tailored to the prospect's role and psychology, and provide clear guidance on how to engage effectively.
        
        IMPORTANT: Always use the candidate's first name when referring to them in the insight. 
        This makes the recommendation personal and actionable.
        
        Focus on these three behavioral metrics:
        1. Commitment Momentum Index (CMI): Forward motion vs. idle curiosity—i.e., is the person merely researching or already lining up next steps?
        2. Risk-Barrier Focus Score (RBFS): How sensitive the person is to downside and friction.
        3. Identity Alignment Signal (IAS): Whether the choice fits their self-image / goals—key across career, investing, and purchasing.
        
        Your insight should be 2-3 sentences and should provide specific, actionable guidance on how to engage with the prospect.
        Start the insight by referring to the candidate by their first name.
        """
        
        name_instruction = f"The candidate's first name is '{first_name}'. " if first_name else "The candidate's name is not available, so use their role title. "
        
        user_prompt_for_ai = f"""
        {name_instruction}Generate a focused behavioral insight for a {role} who was found in a search for "{user_prompt}".
        
        Additional information about the prospect:
        {candidate_info}
        
        The insight should be specific to this role and search context, providing actionable guidance on how to engage with them.
        Remember to use the candidate's first name ({first_name}) when referring to them in the insight.
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
        logger.info(f"Generated AI insight for {first_name or role}: {insight[:50]}...")
        return insight
        
    except Exception as e:
        logger.error(f"Error generating focused insight: {str(e)}")
        return generate_fallback_insight(role, candidate_data)

def generate_cmi_score_ai(
    role: str,
    candidate_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a Commitment Momentum Index (CMI) score using AI based on the prospect's role and data.
    CMI: Forward motion vs. idle curiosity—i.e., is the person merely researching or already lining up next steps?
    - Rising share of visits to execution pages (application portals, term-sheet checklists, checkout/pricing, “how to switch…” articles)
    - Shorter intervals between sessions on the same topic
    - Peak in late-night or mobile hits (signals personal, off-hours prioritization)
    High CMI means decision is moving from “thinking about it” to “doing it.” Timing outreach to this upswing dramatically lifts response rates.
    """
    try:
        if not openai_client:
            logger.warning("OpenAI client not initialized, using fallback CMI score")
            return generate_fallback_cmi_score(role)
        
        # Extract relevant information from candidate data
        candidate_info = extract_candidate_info(candidate_data)
        
        # Create the prompt for the AI
        system_prompt = """
        You are an expert in behavioral analysis and sales psychology. Your task is to generate a Commitment Momentum Index (CMI) score for a prospect based on their role and available information.
        
        CMI measures forward motion vs. idle curiosity—i.e., is the person merely researching or already lining up next steps?
        Behavioral cues for high CMI:
        - Rising share of visits to execution pages (application portals, term-sheet checklists, checkout/pricing, “how to switch…” articles)
        - Shorter intervals between sessions on the same topic
        - Peak in late-night or mobile hits (signals personal, off-hours prioritization)
        High CMI means decision is moving from “thinking about it” to “doing it.” Timing outreach to this upswing dramatically lifts response rates.
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A few words or a short phrase, not a full sentence. Be extremely concise, like a bullet point or tag.
        """
        
        user_prompt_for_ai = f"""
        Generate a Commitment Momentum Index (CMI) score for a {role}.
        
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
            max_tokens=50
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
        
        RBFS measures how sensitive the person is to downside and friction. Behavioral cues for high RBFS:
        - Heavy consumption of "pros & cons," "hidden costs," Glassdoor or negative-review content
        - Re-reads of FAQ, legal, security, compliance pages
        - Searches that include "scam," "failure," "lawsuit," "layoffs," etc.
        
        A high RBFS flags risk-averse or politically exposed prospects. They need assurance (case studies, guarantees, references) before they will move.
        
        Score ranges:
        - High scores (80-100): Highly risk-averse, needs extensive validation and assurance
        - Medium scores (50-79): Balanced approach to risk, needs moderate validation
        - Low scores (0-49): Risk-tolerant, focuses on opportunities over barriers
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A few words or a short phrase, not a full sentence. Be extremely concise, like a bullet point or tag.
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
            max_tokens=50
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
        
        IAS measures whether the choice fits their self-image / goals—key across career, investing, and purchasing. Behavioral cues for high IAS:
        - Visits to purpose-driven or values pages (DEI, sustainability, founder story)
        - Long reads on thought-leadership or community posts
        - Following brand or execs on social links clicked from site
        
        When IAS is high, the prospect feels personally aligned; emotional friction drops and word-of-mouth lift rises. Low IAS means you must reframe the narrative to their aspirations.
        
        Score ranges:
        - High scores (80-100): Strong personal alignment with values and aspirations
        - Medium scores (50-79): Moderate alignment, some resonance with brand values
        - Low scores (0-49): Weak alignment, needs narrative reframing to match aspirations
        
        Provide your response as a JSON object with two fields:
        1. "score": A number between 0 and 100
        2. "explanation": A few words or a short phrase, not a full sentence. Be extremely concise, like a bullet point or tag.
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
            max_tokens=50
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
                    "explanation": "Moderate Commitment Momentum Index (CMI) suggests the prospect is past initial research and may be ready to engage. Look for behavioral cues like late-night research or repeat visits to key pages."
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

def generate_fallback_insight(role: str, candidate_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a fallback insight based on role, using candidate's name if available."""
    role_lower = role.lower()
    
    # Extract candidate's first name for personalization
    candidate_name = candidate_data.get("name", "") if candidate_data else ""
    first_name = extract_first_name(candidate_name)
    
    # Use first name if available, otherwise use role-based reference
    name_ref = first_name if first_name else "This professional"
    
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return f"{name_ref} responds best to detailed, evidence-based communication. Start conversations by asking about their current technical challenges, then demonstrate how your solution addresses specific pain points with concrete examples and performance metrics."
    
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return f"{name_ref} values direct communication and strategic impact. Begin by acknowledging their business challenges, then present your solution with clear ROI metrics and competitive advantages. Focus on how your offering solves their specific business problems rather than technical details."
    
    # Sales roles
    elif any(sales in role_lower for sales in ["sales", "account", "business development"]):
        return f"{name_ref} responds best to competitive differentiation and concrete outcomes. Start conversations by asking about their current sales targets, then demonstrate how your solution can help them exceed goals and outperform competitors."
    
    # Default for other roles
    else:
        return f"{name_ref} responds best to personalized engagement. Start conversations by asking targeted questions about their specific challenges, then demonstrate how your solution addresses their unique needs with concrete examples and clear benefits."

def generate_fallback_cmi_score(role: str) -> Dict[str, Any]:
    """Generate a fallback CMI score based on role (Commitment Momentum Index)."""
    role_lower = role.lower()
    # Technical roles
    if any(tech in role_lower for tech in ["engineer", "developer", "programmer", "architect"]):
        return {
            "score": 85,
            "explanation": "Ready to act"
        }
    # Executive roles
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 80,
            "explanation": "Lining up next steps"
        }
    # Default for other roles
    else:
        return {
            "score": 70,
            "explanation": "Past research phase"
        }

def generate_fallback_rbfs_score(role: str) -> Dict[str, Any]:
    """Generate a fallback RBFS score based on role."""
    role_lower = role.lower()
    
    # Finance and legal roles tend to be more risk-averse
    if any(risk_role in role_lower for risk_role in ["finance", "legal", "compliance", "security", "risk"]):
        return {
            "score": 85,
            "explanation": "Risk-averse"
        }
    
    # Executive roles often balance risk and opportunity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 70,
            "explanation": "Balanced risk"
        }
    
    # Default for other roles
    else:
        return {
            "score": 60,
            "explanation": "Open to opportunity"
        }

def generate_fallback_ias_score(role: str) -> Dict[str, Any]:
    """Generate a fallback IAS score based on role."""
    role_lower = role.lower()
    
    # Technical specialists often strongly identify with their expertise
    if any(tech in role_lower for tech in ["engineer", "developer", "architect", "scientist"]):
        return {
            "score": 85,
            "explanation": "Strong alignment"
        }
    
    # Executive roles often have strong professional identity
    elif any(exec_role in role_lower for exec_role in ["ceo", "cto", "cfo", "coo", "chief", "president", "founder"]):
        return {
            "score": 80,
            "explanation": "Role-driven"
        }
    
    # Default for other roles
    else:
        return {
            "score": 70,
            "explanation": "Moderate fit"
        }