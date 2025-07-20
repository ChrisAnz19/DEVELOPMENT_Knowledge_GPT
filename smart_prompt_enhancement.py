"""
Smart prompt enhancement for competitive intelligence and intent detection.
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from competitive_knowledge_loader import load_competitive_knowledge, get_company_competitors, find_company_category, get_category_info


@dataclass
class PromptAnalysis:
    """Analysis results for a prompt."""
    detected_products: List[str]
    competitors: List[str]
    buying_intent: bool
    selling_intent: bool
    intent_confidence: float
    reasoning: List[str]


def detect_product_mentions(prompt: str, knowledge_data: Optional[Dict] = None) -> List[str]:
    """
    Detect product/company mentions in the prompt.
    
    Args:
        prompt: User prompt to analyze
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        List of detected product/company names
    """
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except Exception:
            return []
    
    detected = []
    companies = knowledge_data.get("companies", {})
    prompt_lower = prompt.lower()
    
    # Check for direct company mentions
    for company_name, company_data in companies.items():
        # Check main company name
        if company_name in prompt_lower:
            detected.append(company_name)
            continue
            
        # Check aliases
        aliases = company_data.get("aliases", [])
        for alias in aliases:
            if alias.lower() in prompt_lower:
                detected.append(company_name)
                break
    
    return list(set(detected))  # Remove duplicates


def detect_buying_intent(prompt: str, knowledge_data: Optional[Dict] = None) -> Tuple[bool, bool, float]:
    """
    Detect buying vs selling intent in the prompt.
    
    Args:
        prompt: User prompt to analyze
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        Tuple of (buying_intent, selling_intent, confidence_score)
    """
    prompt_lower = prompt.lower()
    
    # Strong buying indicators
    strong_buying_signals = [
        "looking to buy", "want to purchase", "need to find", "shopping for",
        "evaluating", "comparing", "switching from", "replacing",
        "looking for a new", "need a better", "upgrade from"
    ]
    
    # Moderate buying indicators
    moderate_buying_signals = [
        "interested in", "considering", "exploring", "researching",
        "looking at", "checking out", "thinking about"
    ]
    
    # Selling indicators
    selling_signals = [
        "companies that sell", "vendors of", "providers of", "suppliers of",
        "who offer", "that provide", "selling", "offering"
    ]
    
    # Buyer role indicators
    buyer_roles = [
        "cto", "ceo", "cfo", "director", "manager", "head of",
        "vp", "vice president", "decision maker", "buyer"
    ]
    
    buying_score = 0
    selling_score = 0
    
    # Check for strong buying signals
    for signal in strong_buying_signals:
        if signal in prompt_lower:
            buying_score += 0.4
    
    # Check for moderate buying signals
    for signal in moderate_buying_signals:
        if signal in prompt_lower:
            buying_score += 0.2
    
    # Check for selling signals
    for signal in selling_signals:
        if signal in prompt_lower:
            selling_score += 0.3
    
    # Check for buyer roles (adds to buying intent)
    for role in buyer_roles:
        if role in prompt_lower:
            buying_score += 0.1
    
    # Normalize scores
    buying_score = min(1.0, buying_score)
    selling_score = min(1.0, selling_score)
    
    # Determine primary intent
    if buying_score > selling_score and buying_score > 0.3:
        return True, False, buying_score
    elif selling_score > buying_score and selling_score > 0.3:
        return False, True, selling_score
    else:
        return False, False, max(buying_score, selling_score)


def generate_competitive_exclusions(detected_products: List[str], knowledge_data: Optional[Dict] = None) -> List[str]:
    """
    Generate list of competitors to exclude based on detected products.
    
    Args:
        detected_products: List of detected product names
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        List of competitor names to exclude
    """
    if not detected_products:
        return []
        
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except Exception:
            return []
    
    all_competitors = []
    
    for product in detected_products:
        competitors = get_company_competitors(product, knowledge_data)
        all_competitors.extend(competitors)
    
    # Remove duplicates and return
    return list(set(all_competitors))


def enhance_prompt_with_exclusions(original_prompt: str, analysis: PromptAnalysis) -> str:
    """
    Comprehensively enhance the original prompt with competitive intelligence, intent clarification, and specificity improvements.
    
    Args:
        original_prompt: Original user prompt
        analysis: Analysis results from analyze_prompt
        
    Returns:
        Substantially enhanced prompt with multiple improvements
    """
    enhanced_prompt = original_prompt
    enhancements = []
    
    # Add competitive exclusions if any competitors found
    if analysis.competitors:
        competitor_list = ", ".join(analysis.competitors).title()
        exclusion_text = f"EXCLUDE employees from these competing companies: {competitor_list}"
        enhancements.append(exclusion_text)
    
    # Add intent clarification with more specificity
    if analysis.intent_confidence > 0.3:  # Lower threshold for more enhancement
        if analysis.buying_intent:
            if analysis.intent_confidence > 0.7:
                intent_text = "Focus on BUYERS actively evaluating or purchasing this solution. Exclude vendors, resellers, and competitors"
            else:
                intent_text = "Focus on potential BUYERS of this solution, not companies that sell or provide it"
            enhancements.append(intent_text)
        elif analysis.selling_intent:
            intent_text = "Focus on companies that SELL, PROVIDE, or DISTRIBUTE this solution"
            enhancements.append(intent_text)
    
    # Add role-specific enhancements based on detected patterns
    role_enhancements = _generate_role_specific_enhancements(original_prompt)
    if role_enhancements:
        enhancements.extend(role_enhancements)
    
    # Add geographic and company size filters if not specified
    geographic_enhancement = _generate_geographic_enhancement(original_prompt)
    if geographic_enhancement:
        enhancements.append(geographic_enhancement)
    
    # Add industry context if detected
    industry_enhancement = _generate_industry_enhancement(original_prompt, analysis.detected_products)
    if industry_enhancement:
        enhancements.append(industry_enhancement)
    
    # Combine all enhancements
    if enhancements:
        enhanced_prompt += ". " + ". ".join(enhancements) + "."
    
    return enhanced_prompt


def _generate_role_specific_enhancements(prompt: str) -> List[str]:
    """Generate role-specific enhancements based on detected roles in the prompt."""
    prompt_lower = prompt.lower()
    enhancements = []
    
    # Executive roles - add decision-making context
    if any(exec_role in prompt_lower for exec_role in ["ceo", "cto", "cfo", "coo", "president", "founder"]):
        enhancements.append("Focus on senior decision-makers with budget authority")
    
    # Manager roles - add team context
    elif any(mgr_role in prompt_lower for mgr_role in ["manager", "director", "head of"]):
        enhancements.append("Target managers responsible for team tools and processes")
    
    # Technical roles - add implementation context
    elif any(tech_role in prompt_lower for tech_role in ["engineer", "developer", "architect", "technical"]):
        enhancements.append("Focus on technical professionals involved in tool evaluation and implementation")
    
    # Sales roles - add performance context
    elif any(sales_role in prompt_lower for sales_role in ["sales", "account", "business development", "revenue"]):
        enhancements.append("Target sales professionals focused on performance improvement and quota achievement")
    
    # Marketing roles - add growth context
    elif any(mkt_role in prompt_lower for mkt_role in ["marketing", "growth", "demand", "content"]):
        enhancements.append("Focus on marketing professionals driving growth and customer acquisition")
    
    return enhancements


def _generate_geographic_enhancement(prompt: str) -> str:
    """Generate geographic enhancement if location not specified."""
    prompt_lower = prompt.lower()
    
    # Check if geographic location is already specified
    common_locations = [
        "united states", "us", "usa", "america", "california", "new york", "texas", "florida",
        "san francisco", "los angeles", "chicago", "boston", "seattle", "austin", "denver",
        "north america", "europe", "asia", "global", "international", "remote"
    ]
    
    has_location = any(location in prompt_lower for location in common_locations)
    
    if not has_location:
        return "Prioritize United States-based professionals"
    
    return ""


def _generate_industry_enhancement(prompt: str, detected_products: List[str]) -> str:
    """Generate industry-specific enhancement based on context."""
    prompt_lower = prompt.lower()
    
    # Agency/Marketing specific contexts
    agency_contexts = {
        "outbound agency": "Focus on marketing agencies, lead generation companies, and sales consulting firms",
        "marketing agency": "Target marketing agencies, advertising firms, and digital marketing companies",
        "agency owner": "Focus on marketing agencies, advertising firms, and business service companies",
        "cold email": "Target companies that do outbound marketing, lead generation, or sales outreach",
        "email marketing": "Focus on marketing agencies, SaaS companies, and e-commerce businesses",
        "lead generation": "Target lead generation companies, marketing agencies, and sales consulting firms"
    }
    
    # Check for agency/marketing contexts first
    for context, enhancement in agency_contexts.items():
        if context in prompt_lower:
            return enhancement
    
    # Industry-specific enhancements
    industry_contexts = {
        "saas": "Focus on SaaS and cloud-first companies",
        "software": "Target software and technology companies", 
        "enterprise": "Focus on enterprise-level organizations with 500+ employees",
        "startup": "Target startups and high-growth companies",
        "healthcare": "Focus on healthcare and medical device companies",
        "finance": "Target financial services and fintech companies",
        "retail": "Focus on retail and e-commerce companies",
        "manufacturing": "Target manufacturing and industrial companies",
        "consulting": "Focus on consulting firms and professional services companies"
    }
    
    for industry, enhancement in industry_contexts.items():
        if industry in prompt_lower:
            return enhancement
    
    # Product-based industry inference
    if detected_products:
        # If CRM products detected, likely targeting sales-focused companies
        crm_products = ["salesforce", "hubspot", "pipedrive"]
        if any(product in detected_products for product in crm_products):
            return "Focus on companies with active sales teams and CRM usage"
        
        # If dialer products detected, likely targeting sales-heavy organizations
        dialer_products = ["orum", "five9", "outreach", "salesloft"]
        if any(product in detected_products for product in dialer_products):
            return "Target companies with high-volume sales operations"
    
    return ""


def analyze_prompt(prompt: str, knowledge_data: Optional[Dict] = None) -> PromptAnalysis:
    """
    Analyze a prompt for product mentions, competitive intelligence, and intent detection.
    
    Args:
        prompt: User prompt to analyze
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        PromptAnalysis object with detection results
    """
    if knowledge_data is None:
        try:
            knowledge_data = load_competitive_knowledge()
        except Exception:
            knowledge_data = {}
    
    # Detect products mentioned
    detected_products = detect_product_mentions(prompt, knowledge_data)
    
    # Get competitors for detected products
    competitors = generate_competitive_exclusions(detected_products, knowledge_data)
    
    # Detect buying/selling intent
    buying_intent, selling_intent, intent_confidence = detect_buying_intent(prompt, knowledge_data)
    
    # Generate reasoning
    reasoning = []
    if detected_products:
        reasoning.append(f"Detected products: {', '.join(detected_products)}")
    if competitors:
        reasoning.append(f"Identified {len(competitors)} competitors to exclude")
    if buying_intent:
        reasoning.append(f"Detected buying intent (confidence: {intent_confidence:.2f})")
    elif selling_intent:
        reasoning.append(f"Detected selling intent (confidence: {intent_confidence:.2f})")
    
    return PromptAnalysis(
        detected_products=detected_products,
        competitors=competitors,
        buying_intent=buying_intent,
        selling_intent=selling_intent,
        intent_confidence=intent_confidence,
        reasoning=reasoning
    )


def enhance_prompt(prompt: str, knowledge_data: Optional[Dict] = None) -> Tuple[str, PromptAnalysis]:
    """
    Main function to comprehensively enhance a prompt with competitive intelligence, intent detection, and structural improvements.
    
    Args:
        prompt: Original user prompt
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        Tuple of (enhanced_prompt, analysis_results)
    """
    try:
        # First, improve the basic prompt structure
        structured_prompt = _improve_prompt_structure(prompt)
        
        # Analyze the structured prompt
        analysis = analyze_prompt(structured_prompt, knowledge_data)
        
        # Apply comprehensive enhancements
        enhanced_prompt = enhance_prompt_with_exclusions(structured_prompt, analysis)
        
        # Final quality check and optimization
        final_prompt = _optimize_final_prompt(enhanced_prompt)
        
        return final_prompt, analysis
        
    except Exception as e:
        # Fallback to original prompt on any error
        empty_analysis = PromptAnalysis(
            detected_products=[],
            competitors=[],
            buying_intent=False,
            selling_intent=False,
            intent_confidence=0.0,
            reasoning=[f"Enhancement failed: {str(e)}"]
        )
        return prompt, empty_analysis


def _improve_prompt_structure(prompt: str) -> str:
    """Improve the basic structure and clarity of the prompt."""
    prompt = prompt.strip()
    
    # Handle prompts that start with "Need" or similar
    if prompt.lower().startswith("need "):
        prompt = f"Find {prompt[5:]}"  # Remove "Need " and add "Find "
    
    # Add "Find" prefix if not present and prompt doesn't start with action word
    action_words = ["find", "search", "look", "identify", "locate", "get", "show"]
    if not any(prompt.lower().startswith(word) for word in action_words):
        prompt = f"Find {prompt.lower()}"
    
    # Ensure proper capitalization
    prompt = prompt[0].upper() + prompt[1:] if len(prompt) > 1 else prompt.upper()
    
    # Remove redundant words and improve clarity
    replacements = {
        "looking to buy a new": "evaluating",
        "interested in buying": "evaluating", 
        "want to purchase": "evaluating",
        "need to find": "seeking",
        "looking for a": "seeking",
        "companies that use": "users of",
        "people who work at": "employees at",
        "individuals who": "professionals who",
        "find find": "find"  # Fix double "find" issue
    }
    
    for old, new in replacements.items():
        prompt = prompt.replace(old, new)
    
    return prompt


def _optimize_final_prompt(prompt: str) -> str:
    """Final optimization of the enhanced prompt."""
    # Remove duplicate periods and spaces
    prompt = prompt.replace("..", ".").replace("  ", " ").strip()
    
    # Ensure proper ending
    if not prompt.endswith("."):
        prompt += "."
    
    # Capitalize first letter after periods
    sentences = prompt.split(". ")
    capitalized_sentences = []
    for sentence in sentences:
        if sentence:
            sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            capitalized_sentences.append(sentence)
    
    return ". ".join(capitalized_sentences)