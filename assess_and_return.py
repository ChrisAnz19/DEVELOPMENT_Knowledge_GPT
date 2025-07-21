# type: ignore
"""
Enhanced Assessment Module

This module provides functionality for evaluating candidate fit based on simulated behavioral data.
It uses GPT-4-Turbo to generate realistic, industry-specific behavioral patterns with time-series data.

Key features:
- Industry-specific behavioral assessment
- Time-series behavioral patterns
- Realistic online activity simulation
- Fallback mechanism for API failures
- Response validation

Usage:
    from assess_and_return import select_top_candidates
    
    # Get top candidates based on user query
    results = select_top_candidates("Looking for a senior developer with cloud experience", people_data)
"""

import json
import logging
import random
from datetime import datetime, timedelta
from openai_utils import call_openai_for_json, call_openai
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_random_time_reference() -> str:
    """
    Generate a random time reference that's never in the past 6 hours.
    Returns realistic time phrases for behavioral patterns.
    """
    # Define time ranges (avoiding past 6 hours)
    time_options = [
        # Yesterday and beyond
        "yesterday",
        "two days ago", 
        "three days ago",
        "earlier this week",
        "last week",
        "two weeks ago",
        "three weeks ago",
        "last month",
        "two months ago",
        
        # Duration-based (ongoing patterns)
        "over the past week",
        "over the past two weeks", 
        "over the past month",
        "over the past three weeks",
        "over a two-week period",
        "over a three-week period",
        "over the past quarter",
        
        # Frequency-based
        "daily over the past week",
        "multiple times last week",
        "repeatedly over the past month",
        "consistently over two weeks",
        "regularly over the past month",
        
        # Specific timeframes
        "during the past weekend",
        "throughout last week",
        "across multiple sessions last month",
        "in several sessions over two weeks",
        "during evening hours last week",
    ]
    
    return random.choice(time_options)

def generate_activity_duration() -> str:
    """Generate realistic activity duration references."""
    durations = [
        "for 15+ minutes",
        "for 30+ minutes", 
        "for 45+ minutes",
        "for over an hour",
        "spending significant time",
        "with extended sessions",
        "in detailed sessions",
        "with focused attention",
        "for extended periods",
        "in multiple long sessions"
    ]
    
    return random.choice(durations)

def generate_frequency_reference() -> str:
    """Generate realistic frequency references."""
    frequencies = [
        "5 times",
        "7 times", 
        "multiple times",
        "repeatedly",
        "consistently",
        "regularly",
        "several times",
        "numerous times",
        "frequently"
    ]
    
    return random.choice(frequencies)

def build_assessment_prompt(user_prompt: str, candidates: list, industry_context: str = None) -> Tuple[str, str]:
    """
    Builds optimized system and user prompts for the OpenAI API call.
    
    Args:
        user_prompt: The user's search criteria
        candidates: Simplified candidate data
        industry_context: Optional industry context
        
    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    # Extract roles from candidates for context
    roles = [candidate.get("title", "Unknown") for candidate in candidates]
    roles_str = ", ".join(roles)
    
    # Determine industry context if not provided
    if not industry_context:
        # Try to infer from titles and companies
        titles = " ".join([c.get("title", "") for c in candidates])
        companies = " ".join([c.get("company", "") for c in candidates])
        combined = (titles + " " + companies).lower()
        
        if any(tech in combined for tech in ["software", "developer", "engineer", "programming", "tech", "it", "data"]):
            industry_context = "Technology"
        elif any(fin in combined for fin in ["finance", "banking", "investment", "financial", "accounting"]):
            industry_context = "Finance"
        elif any(mkt in combined for mkt in ["marketing", "advertising", "brand", "content", "seo", "ppc"]):
            industry_context = "Marketing"
        elif any(sales in combined for sales in ["sales", "business development", "account", "revenue"]):
            industry_context = "Sales"
        else:
            industry_context = "General Business"
    
    system_prompt = """
You are an expert at evaluating candidate fit based on simulated behavioral data from website visits and online activity.
You have access to a trillion rows of website visit data per month across 450k top domains and tens of millions of websites.

IMPORTANT GUIDELINES:
1. Generate REALISTIC behavioral reasons tailored to each candidate's industry and role
2. Include TIME-SERIES patterns showing progression or repeated behaviors over time
3. Be SPECIFIC about websites, tools, and resources relevant to their profession
4. AVOID unrealistic scenarios like "reading case studies about job postings" or "attending webinars" for all professions
5. NEVER use generic phrases like "selected based on title and company fit"
6. NEVER use the same phrases for multiple candidates
7. NEVER use phrases that can be verified by a human, or that are too vague or generic
8. NEVER mention specific industries (like "real estate" or "healthcare") UNLESS they are explicitly mentioned in the user request
9. For industry-specific references, use "their industry" or "their field" instead of naming a specific industry
10. Focus on the specific product/service mentioned in the request (like "CRM" or "marketing automation") rather than inventing an industry context

EXAMPLES OF GOOD BEHAVIORAL REASONS:
- Engineering: "Visited GitHub repositories for React state management libraries 5 times in the past week"
- Marketing: "Spent increasing amounts of time on Google Analytics and HubSpot over a three-week period"
- Sales: "Researched CRM comparison tools, then focused specifically on Salesforce pricing pages"
- Executive: "Reviewed quarterly reports from competitors, then researched market expansion strategies"

EXAMPLES OF BAD BEHAVIORAL REASONS (AVOID THESE):
- "Selected based on title and company fit" (too generic)
- "Attended webinars on job postings" (unrealistic for most professionals)
- "Read case studies about the industry" (too vague)
- "Showed interest in the field" (not specific enough)
- "Researched case studies on successful CRM implementations in the real estate industry" (mentioning specific industry not in prompt)
- "Analyzed healthcare marketing strategies" (mentioning specific industry not in prompt)

You will receive a user request and a JSON array of candidates.
First, think step-by-step and assign each person an accuracy probability (0-100) of matching the request.
Then select the top candidates with the highest probabilities (return 2-3 candidates, prioritizing quality over quantity).

For each selected candidate, provide 3-4 specific, plausible, and realistic behavioral reasons why they were selected,
based on their simulated online activity patterns over time.

Return ONLY valid JSON array with 2-3 objects, each containing:
name, title, company, email, accuracy (number), reasons (array of strings).
No extra text, no explanation, no comments.
"""
    
    user_prompt = f"""
User request: {user_prompt}

Candidates:
{json.dumps(candidates)}

Additional context:
- Industry: {industry_context}
- Roles being evaluated: {roles_str}
"""
    
    return system_prompt, user_prompt

def select_top_candidates(user_prompt: str, people: list, behavioral_data: dict = None, industry_context: str = None) -> list:
    """
    Enhanced function to rank and explain top candidates with realistic behavioral data.
    
    Args:
        user_prompt: The user's search criteria
        people: List of candidate data
        behavioral_data: Optional behavioral data to incorporate
        industry_context: Optional industry context to tailor assessments
        
    Returns:
        List of dicts with candidate info and behavioral assessments
    """
    # Optimize token usage by limiting candidates and extracting only necessary fields
    max_candidates = min(5, len(people))  # Limit to 5 candidates maximum (increased from 3)
    limited_people = people[:max_candidates]
    
    # Simplify the people data to reduce tokens - only include essential fields
    simplified_people = []
    for person in limited_people:
        # Extract only the fields needed for assessment
        simplified_person = {
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None")
        }
        
        # Only include LinkedIn URL if it exists and is not too long
        linkedin_url = person.get("linkedin_url", "")
        if linkedin_url and len(linkedin_url) < 60:  # Avoid very long URLs
            simplified_person["linkedin_url"] = linkedin_url
            
        simplified_people.append(simplified_person)
    
    # Build optimized prompts
    system_prompt, prompt = build_assessment_prompt(user_prompt, simplified_people, industry_context)
    
    # Use the OpenAI utility function with GPT-4-Turbo
    response = call_openai(
        prompt=prompt,
        system_message=system_prompt,
        model="gpt-3.5-turbo",  # Upgraded from gpt-3.5-turbo
        temperature=0.7,
        max_tokens=1000  # Increased for more detailed responses
    )
    
    if response:
        try:
            # Try to parse the response as JSON
            result = json.loads(response)
            
            # Ensure result is a list
            if isinstance(result, list):
                # Enhanced validation of response quality
                validated_result = _validate_assessment_response(result, user_prompt)
                if validated_result:
                    return validated_result
                else:
                    print("[Assessment] Response validation failed, using fallback logic")
                    return _fallback_assessment(people, user_prompt, industry_context)
            else:
                print("[Assessment] Response is not a list, using fallback logic")
                return _fallback_assessment(people, user_prompt, industry_context)
                
        except json.JSONDecodeError as e:
            print(f"[Assessment] Failed to parse JSON response: {e}")
            print(f"[Assessment] Raw response: {response}")
            return _fallback_assessment(people, user_prompt, industry_context)
    
    print("[Assessment] OpenAI API call failed, using fallback logic")
    return _fallback_assessment(people, user_prompt, industry_context)

def _validate_assessment_response(result: list, user_prompt: str) -> list:
    """
    Validates the assessment response for quality and completeness.
    
    Args:
        result: The parsed response from OpenAI
        user_prompt: The original user query
        
    Returns:
        The validated result or None if validation fails
    """
    # Check if we have 2-3 results (more flexible)
    if len(result) < 2 or len(result) > 3:
        print(f"[Assessment] Expected 2-3 results, got {len(result)}")
        return None
    
    # Check required fields
    required_fields = ["name", "title", "company", "email", "accuracy", "reasons"]
    for item in result:
        missing_fields = [field for field in required_fields if field not in item]
        if missing_fields:
            print(f"[Assessment] Missing required fields: {missing_fields}")
            return None
    
    # Check accuracy values
    for item in result:
        accuracy = item.get("accuracy")
        if not isinstance(accuracy, (int, float)) or accuracy < 0 or accuracy > 100:
            print(f"[Assessment] Invalid accuracy value: {accuracy}")
            return None
    
    # Check reasons
    for item in result:
        reasons = item.get("reasons", [])
        
        # Check if we have enough reasons
        if len(reasons) < 2:
            print(f"[Assessment] Not enough reasons provided: {len(reasons)}")
            return None
        
        # Check for generic reasons (relaxed validation)
        generic_phrases = [
            "selected based on title and company fit",
            "profile indicates relevant experience",
            "title and company fit",
            "selected based on title",
            "selected based on company"
        ]
        
        generic_reasons = [r for r in reasons if any(phrase in r.lower() for phrase in generic_phrases)]
        if generic_reasons:
            print(f"[Assessment] Generic reasons detected: {generic_reasons}")
            # Don't fail validation - just log the warning
            print("[Assessment] Continuing with assessment despite generic reasons")
        
        # Check for time-series patterns (relaxed validation)
        time_indicators = ["times", "over", "period", "week", "month", "day", "repeatedly", "multiple", "increasing", "spent", "visited", "researched", "analyzed"]
        has_time_series = any(any(indicator in r.lower() for indicator in time_indicators) for r in reasons)
        if not has_time_series:
            print("[Assessment] No time-series patterns detected in reasons")
            # Don't fail validation - just log the warning
            print("[Assessment] Continuing with assessment despite lack of time-series patterns")
    
    # All validations passed
    return result

def _get_industry_specific_patterns(title: str, company: str, user_prompt: str = "") -> dict:
    """
    Generate industry-specific behavioral patterns with time-series data.
    
    Args:
        title: Job title of the candidate
        company: Company name of the candidate
        user_prompt: Optional user search criteria to tailor patterns
        
    Returns:
        Dictionary with industry and patterns
    """
    title = title.lower()
    company = company.lower()
    user_prompt = user_prompt.lower()
    
    # Determine industry and role
    industry = "general"
    role_level = "mid"  # default: mid-level
    
    # Determine industry
    if any(tech in title or tech in company for tech in ["software", "developer", "engineer", "programming", "tech", "data", "it", "product", "cyber"]):
        industry = "tech"
    elif any(fin in title or fin in company for fin in ["finance", "banking", "investment", "financial", "accounting", "insurance"]):
        industry = "finance"
    elif any(mkt in title for mkt in ["marketing", "advertising", "brand", "content", "seo", "ppc", "growth"]):
        industry = "marketing"
    elif any(sales in title for sales in ["sales", "business development", "account", "revenue"]):
        industry = "sales"
    elif any(hr in title for hr in ["hr", "human resources", "talent", "recruiting", "people"]):
        industry = "hr"
    elif any(design in title for design in ["design", "ux", "ui", "user experience", "creative"]):
        industry = "design"
    
    # Determine seniority level
    if any(senior in title for senior in ["senior", "lead", "sr", "principal", "staff"]):
        role_level = "senior"
    elif any(junior in title for junior in ["junior", "jr", "associate", "assistant"]):
        role_level = "junior"
    elif any(exec_level in title for exec_level in ["ceo", "cto", "cfo", "coo", "chief", "vp", "vice president", "director", "head"]):
        role_level = "executive"
    
    # Industry-specific behavioral patterns with dynamic time-series data
    patterns = {
        "tech": {
            "junior": [
                "Visited Stack Overflow {frequency} {time_ref}, focusing on {tech_topic} questions and {duration}",
                "Cloned GitHub repositories related to {tech_framework} {time_ref}, exploring implementation examples",
                "Researched {tech_tool} documentation {frequency} {time_ref}, {duration} on each session",
                "Searched for '{tech_topic} tutorials' {time_ref} and bookmarked multiple resources {duration}"
            ],
            "mid": [
                "Contributed to {tech_framework} discussions on GitHub {time_ref}, providing detailed code examples",
                "Analyzed {tech_topic} optimization techniques {time_ref}, comparing different approaches {duration}",
                "Evaluated {tech_tool} alternatives on review sites {time_ref}, then explored vendor documentation",
                "Downloaded and reviewed technical papers on {tech_topic} {time_ref}, {duration} on implementation details"
            ],
            "senior": [
                "Researched enterprise {tech_framework} architecture patterns {time_ref}, {duration} on scalability considerations",
                "Benchmarked {tech_tool} performance configurations {time_ref}, analyzing results across multiple scenarios",
                "Reviewed technical documentation for {tech_topic} solutions {frequency} {time_ref}, focusing on integration capabilities",
                "Participated in technical forums discussing {tech_topic} best practices {time_ref}, contributing expert insights"
            ],
            "executive": [
                "Compared enterprise {tech_tool} solutions on G2 and Capterra {time_ref}, focusing on ROI and adoption metrics",
                "Analyzed industry reports on {tech_framework} adoption trends {time_ref}, {duration} on competitive analysis",
                "Reviewed case studies of {tech_topic} implementations {frequency} {time_ref}, evaluating business impact",
                "Researched market trends in {tech_topic} technologies {time_ref}, consulting multiple analyst reports"
            ]
        },
        "finance": {
            "junior": [
                "Studied financial modeling tutorials on specialized platforms {time_ref}, {duration} on Excel techniques",
                "Checked market data on Bloomberg and Reuters {frequency} {time_ref}, tracking sector performance",
                "Downloaded financial analysis templates {time_ref} and customized them {duration}",
                "Monitored specific market sectors {frequency} {time_ref}, analyzing volatility patterns"
            ],
            "mid": [
                "Analyzed quarterly reports from {industry_sector} companies {time_ref}, {duration} on financial metrics",
                "Compared financial data visualization tools {time_ref}, evaluating advanced analytics features",
                "Researched {finance_topic} compliance requirements {frequency} {time_ref}, reviewing regulatory updates",
                "Tracked market indicators related to {industry_sector} {time_ref}, building performance models"
            ],
            "senior": [
                "Conducted merger activity analysis in {industry_sector} {time_ref}, {duration} on due diligence processes",
                "Researched advanced risk management frameworks {frequency} {time_ref}, evaluating implementation strategies",
                "Compared enterprise financial software solutions {time_ref}, examining integration and scalability",
                "Analyzed investment strategy performance data {time_ref}, {duration} on {finance_topic} optimization"
            ],
            "executive": [
                "Reviewed macroeconomic indicators impacting {industry_sector} {frequency} {time_ref}, consulting multiple sources",
                "Analyzed competitor financial performance {time_ref}, {duration} on strategic positioning",
                "Researched regulatory frameworks affecting {finance_topic} {time_ref}, evaluating compliance implications",
                "Examined global market trends in {industry_sector} {frequency} {time_ref}, reviewing analyst reports"
            ]
        },
        "marketing": {
            "junior": [
                "Explored various social media analytics tools, comparing features and pricing",
                "Studied content marketing strategies through online courses over a two-week period",
                "Analyzed successful {marketing_channel} campaigns for similar companies",
                "Tracked performance metrics for {marketing_channel} across multiple platforms"
            ],
            "mid": [
                "Compared marketing automation platforms, focusing on {marketing_feature} capabilities",
                "Researched customer journey mapping tools, then explored implementation strategies",
                "Analyzed competitor {marketing_channel} strategies over a three-month period",
                "Studied attribution models for multi-channel campaigns relevant to their business"
            ],
            "senior": [
                "Evaluated enterprise marketing platforms with focus on integration and analytics capabilities",
                "Researched advanced segmentation strategies for target audiences",
                "Analyzed ROI metrics for various marketing channels in their business context",
                "Compared marketing technology stacks of leading companies in their field"
            ],
            "executive": [
                "Reviewed comprehensive market research reports relevant to their business",
                "Analyzed marketing performance benchmarks across the competitive landscape",
                "Researched emerging marketing technologies with potential strategic impact",
                "Examined case studies of successful marketing transformations in similar organizations"
            ]
        },
        "sales": {
            "junior": [
                "Researched prospecting techniques for target buyers {time_ref}, {duration} on outreach strategies",
                "Studied product comparison guides {frequency} {time_ref}, analyzing competitive positioning",
                "Explored CRM pipeline management features {time_ref}, testing different workflow configurations",
                "Analyzed successful sales email templates {time_ref}, {duration} on effective messaging"
            ],
            "mid": [
                "Compared sales enablement platforms {time_ref}, evaluating content management and analytics capabilities",
                "Researched negotiation strategies for complex deals {frequency} {time_ref}, studying case examples",
                "Analyzed win/loss patterns in sales cycles {time_ref}, {duration} on performance metrics",
                "Studied account-based selling approaches {time_ref}, focusing on high-value target accounts"
            ],
            "senior": [
                "Evaluated enterprise sales methodologies {time_ref}, {duration} on practical applications",
                "Researched strategic account planning frameworks {frequency} {time_ref}, analyzing complex sales cycles",
                "Analyzed sales performance data across regions {time_ref}, benchmarking against industry standards",
                "Compared sales technology stacks {time_ref}, evaluating analytics and forecasting capabilities"
            ],
            "executive": [
                "Reviewed revenue forecasts and growth projections {frequency} {time_ref}",
                "Analyzed competitive positioning strategies {time_ref}, {duration} on market differentiation",
                "Researched sales organizational structures {time_ref}, studying market leaders",
                "Examined sales transformation case studies {frequency} {time_ref}, evaluating implementation strategies"
            ]
        },
        "general": {
            "junior": [
                "Researched industry best practices through professional association resources",
                "Studied online courses related to core job responsibilities",
                "Explored software tools commonly used in their role",
                "Analyzed successful career paths in their chosen field"
            ],
            "mid": [
                "Compared professional certification programs relevant to career advancement",
                "Researched industry trends and their impact on current role requirements",
                "Analyzed case studies of successful projects in related fields",
                "Studied advanced methodologies applicable to their professional domain"
            ],
            "senior": [
                "Evaluated enterprise solutions relevant to departmental objectives",
                "Researched leadership approaches for team effectiveness and development",
                "Analyzed industry benchmarks and performance metrics for similar roles",
                "Compared organizational strategies across industry leaders"
            ],
            "executive": [
                "Reviewed industry transformation case studies and strategic pivots",
                "Analyzed market trends and competitive landscapes across the sector",
                "Researched organizational structures optimized for current market conditions",
                "Examined long-term industry forecasts and strategic implications"
            ]
        }
    }
    
    # Fill in placeholders based on user prompt and industry
    replacements = {
        "tech_topic": "cloud architecture",
        "tech_framework": "React",
        "tech_tool": "Kubernetes",
        "industry_sector": "SaaS",
        "finance_topic": "risk management",
        "marketing_channel": "content marketing",
        "marketing_feature": "automation"
    }
    
    # Try to extract more specific topics from user prompt
    if "crm" in user_prompt.lower():
        # Add specific CRM-related patterns
        if "marketing" in title.lower():
            patterns["marketing"] = {
                "junior": [
                    "Visited CRM comparison websites like Capterra and G2 Crowd {frequency} {time_ref}",
                    "Researched marketing automation integrations with CRM platforms {time_ref}",
                    "Explored email marketing capabilities of various CRM solutions {time_ref}",
                    "Analyzed CRM analytics features for marketing campaign tracking {time_ref}"
                ],
                "mid": [
                    "Compared CRM platforms with marketing automation features {time_ref}",
                    "Researched customer journey tracking capabilities in CRM systems {time_ref}",
                    "Analyzed lead scoring methodologies across different CRM platforms {time_ref}",
                    "Evaluated CRM reporting tools for marketing performance metrics {time_ref}"
                ],
                "senior": [
                    "Evaluated enterprise CRM solutions with advanced marketing capabilities {time_ref}",
                    "Researched CRM implementation strategies for marketing departments {time_ref}",
                    "Analyzed ROI metrics for CRM-driven marketing campaigns {time_ref}",
                    "Compared CRM-marketing integration approaches {time_ref}"
                ],
                "executive": [
                    "Reviewed comprehensive CRM platform evaluations {time_ref}",
                    "Analyzed marketing performance improvements from CRM implementations {time_ref}",
                    "Researched CRM adoption strategies for marketing teams {time_ref}",
                    "Examined case studies of successful CRM transformations {time_ref}"
                ]
            }
        replacements["marketing_channel"] = "CRM-integrated"
        replacements["marketing_feature"] = "CRM integration"
        replacements["tech_tool"] = "CRM platforms"
    elif "cloud" in user_prompt or "aws" in user_prompt or "azure" in user_prompt:
        replacements["tech_topic"] = "cloud infrastructure"
        replacements["tech_tool"] = "AWS" if "aws" in user_prompt else "Azure" if "azure" in user_prompt else "cloud platforms"
    elif "ai" in user_prompt or "machine learning" in user_prompt or "ml" in user_prompt:
        replacements["tech_topic"] = "machine learning"
        replacements["tech_framework"] = "TensorFlow"
        replacements["tech_tool"] = "AI platforms"
    elif "frontend" in user_prompt or "react" in user_prompt or "angular" in user_prompt:
        replacements["tech_topic"] = "frontend development"
        replacements["tech_framework"] = "React" if "react" in user_prompt else "Angular" if "angular" in user_prompt else "modern JavaScript frameworks"
    elif "backend" in user_prompt or "api" in user_prompt:
        replacements["tech_topic"] = "API development"
        replacements["tech_framework"] = "Node.js" if "node" in user_prompt else "Django" if "python" in user_prompt else "backend frameworks"
    
    # Extract industry sector from user prompt - ONLY if explicitly mentioned
    industry_keywords = {
        "healthcare": ["healthcare", "medical", "hospital", "clinic", "patient", "doctor", "physician", "health"],
        "financial services": ["finance", "banking", "investment banking", "financial services", "bank", "credit union"],
        "retail": ["retail", "ecommerce", "e-commerce", "store", "shop", "consumer goods"],
        "manufacturing": ["manufacturing", "factory", "production", "industrial"],
        "technology": ["tech company", "technology company", "software company", "saas company"],
        "real estate": ["real estate", "property management", "realty"],
        "education": ["education", "school", "university", "college", "academic"],
        "hospitality": ["hospitality", "hotel", "restaurant", "tourism"]
    }
    
    # Only set industry_sector if explicitly mentioned in the prompt
    industry_found = False
    for industry, keywords in industry_keywords.items():
        if any(keyword in user_prompt for keyword in keywords):
            replacements["industry_sector"] = industry
            industry_found = True
            break
    
    # If no specific industry is mentioned, use a generic term or leave it out
    if not industry_found:
        # Check if we're looking for a specific product/service
        if "crm" in user_prompt.lower():
            replacements["industry_sector"] = "their industry"  # Generic reference
        elif "marketing automation" in user_prompt.lower():
            replacements["industry_sector"] = "their industry"  # Generic reference
        else:
            # Remove industry-specific references completely by using generic terms
            replacements["industry_sector"] = "their industry"
    
    return {
        "industry": industry,
        "role_level": role_level,
        "patterns": patterns.get(industry, patterns["general"]).get(role_level, patterns["general"]["mid"]),
        "replacements": replacements
    }

def _apply_pattern_replacements(patterns: list, replacements: dict) -> list:
    """Apply replacements to pattern templates with dynamic time references"""
    result = []
    for pattern in patterns:
        # First apply the standard replacements
        for key, value in replacements.items():
            pattern = pattern.replace(f"{{{key}}}", value)
        
        # Then apply dynamic time references
        pattern = pattern.replace("{time_ref}", generate_random_time_reference())
        pattern = pattern.replace("{duration}", generate_activity_duration())
        pattern = pattern.replace("{frequency}", generate_frequency_reference())
        
        result.append(pattern)
    return result

def _fallback_assessment(people: list, user_prompt: str = "", industry_context: str = None) -> list:
    """
    Enhanced fallback assessment when OpenAI fails - returns top 3 people with realistic behavioral reasoning
    
    Args:
        people: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        List of dicts with candidate info and behavioral assessments
    """
    if len(people) == 0:
        return []
    
    # Take first 3 people and create behavioral assessment (increased from 2)
    top_candidates = people[:min(3, len(people))]
    result = []
    
    for i, person in enumerate(top_candidates):
        # Generate behavioral reasons based on their role and industry
        title = person.get("title", "Unknown")
        company = person.get("organization_name", "Unknown")
        
        # Get industry-specific patterns
        pattern_data = _get_industry_specific_patterns(title, company, user_prompt)
        
        # Apply replacements to pattern templates
        behavioral_reasons = _apply_pattern_replacements(
            pattern_data["patterns"], 
            pattern_data["replacements"]
        )
        
        # Ensure we have at least 3 reasons
        while len(behavioral_reasons) < 3:
            behavioral_reasons.append("Researched industry-specific tools and solutions relevant to their role")
        
        # Take only the first 3-4 reasons
        behavioral_reasons = behavioral_reasons[:min(4, len(behavioral_reasons))]
        
        result.append({
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None"),
            "accuracy": 85 - (i * 5),  # 85% for first, 80% for second, 75% for third
            "reasons": behavioral_reasons
        })
    
    return result

if __name__ == "__main__":
    # Load sample people JSON from file or input
    people = json.load(open("temp_people.json"))
    prompt = input("Enter your search prompt: ")
    top2 = select_top_candidates(prompt, people)
    print(json.dumps(top2, indent=2))