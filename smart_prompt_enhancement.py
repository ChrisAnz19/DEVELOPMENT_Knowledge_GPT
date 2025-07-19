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
    
    # Buying intent indicators
    buying_keywords = [
        "looking to buy", "want to buy", "need to purchase", "shopping for",
        "looking for", "need a", "want a", "seeking", "interested in buying",
        "considering", "evaluating", "comparing", "switch from", "replace",
        "upgrade to", "implement", "adopt"
    ]
    
    # Selling intent indicators  
    selling_keywords = [
        "sell", "selling", "offering", "providing", "vendor", "supplier", "provider",
        "company that sells", "business that offers", "we sell", "we offer",
        "our product", "our solution", "competitor", "alternative to"
    ]
    
    # Buyer role indicators
    buyer_roles = [
        "manager", "director", "vp", "cto", "cio", "decision maker",
        "buyer", "purchaser", "administrator", "user", "team lead"
    ]
    
    # Count matches
    buying_matches = sum(1 for keyword in buying_keywords if keyword in prompt_lower)
    selling_matches = sum(1 for keyword in selling_keywords if keyword in prompt_lower)
    buyer_role_matches = sum(1 for role in buyer_roles if role in prompt_lower)
    
    # Calculate intent
    buying_intent = buying_matches > 0 or buyer_role_matches > 0
    selling_intent = selling_matches > 0
    
    # Calculate confidence based on number of matches
    total_matches = buying_matches + selling_matches + buyer_role_matches
    confidence = min(0.9, 0.3 + (total_matches * 0.15))  # Cap at 0.9
    
    # If both intents detected, favor buying if buyer roles mentioned
    if buying_intent and selling_intent:
        if buyer_role_matches > 0:
            selling_intent = False
        else:
            buying_intent = False
            
    return buying_intent, selling_intent, confidence


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
    Enhance the original prompt with competitive exclusions and intent clarification.
    
    Args:
        original_prompt: Original user prompt
        analysis: Analysis results from analyze_prompt
        
    Returns:
        Enhanced prompt with exclusions and clarifications
    """
    enhanced_prompt = original_prompt
    
    # Add competitive exclusions if any competitors found
    if analysis.competitors:
        competitor_list = ", ".join(analysis.competitors).title()
        exclusion_text = f" EXCLUDE employees from these competing companies: {competitor_list}."
        enhanced_prompt += exclusion_text
    
    # Add buying intent clarification if detected
    if analysis.buying_intent and analysis.intent_confidence > 0.5:
        if "buy" in original_prompt.lower() or "looking for" in original_prompt.lower():
            intent_text = " Focus on prospects at companies that would be BUYERS of this solution, not companies that SELL or provide similar solutions."
            enhanced_prompt += intent_text
    
    return enhanced_prompt


def analyze_prompt(prompt: str, knowledge_data: Optional[Dict] = None) -> PromptAnalysis:
    """
    Analyze a prompt for product mentions, competitive intelligence, and intent.
    
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
    
    # Analyze buying/selling intent
    buying_intent, selling_intent, intent_confidence = detect_buying_intent(prompt, knowledge_data)
    
    # Generate reasoning
    reasoning = []
    if detected_products:
        reasoning.append(f"Detected products: {', '.join(detected_products)}")
    if competitors:
        reasoning.append(f"Identified {len(competitors)} competitors to exclude")
    if buying_intent:
        reasoning.append(f"Detected buying intent (confidence: {intent_confidence:.2f})")
    if selling_intent:
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
    Main function to enhance a prompt with competitive intelligence and intent detection.
    
    Args:
        prompt: Original user prompt
        knowledge_data: Optional pre-loaded competitive knowledge
        
    Returns:
        Tuple of (enhanced_prompt, analysis_results)
    """
    try:
        # Analyze the prompt
        analysis = analyze_prompt(prompt, knowledge_data)
        
        # Enhance the prompt
        enhanced_prompt = enhance_prompt_with_exclusions(prompt, analysis)
        
        return enhanced_prompt, analysis
        
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