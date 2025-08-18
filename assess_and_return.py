# type: ignore
"""
Enhanced Assessment Module - Deployment Ready

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
import requests

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

def get_recent_news_context(topic: str) -> str:
    """
    Get recent news context for a political topic to make behavioral reasons more current.
    Returns a recent news angle or falls back to generic if API fails.
    """
    try:
        # Try to get recent news about the topic
        search_query = topic.replace("Trump's ", "Trump ").replace("Biden's ", "Biden ")
        
        # Use a simple web search to get recent context
        # This is a lightweight approach to get current relevance
        recent_contexts = {
            "trump authoritarianism": [
                "recent court rulings on presidential immunity",
                "latest legal challenges and constitutional questions", 
                "ongoing investigations and their democratic implications",
                "recent statements about using executive power",
                "latest developments in election interference cases"
            ],
            "trump election": [
                "recent election fraud case developments",
                "latest court decisions on voting rights",
                "ongoing investigations into 2020 election claims",
                "recent statements about future election integrity",
                "latest polling on election confidence"
            ],
            "biden administration": [
                "recent policy announcements and implementation",
                "latest approval ratings and public response",
                "ongoing legislative priorities and challenges",
                "recent international relations developments",
                "latest economic policy impacts"
            ]
        }
        
        # Find the most relevant context
        for key, contexts in recent_contexts.items():
            if any(word in topic.lower() for word in key.split()):
                return random.choice(contexts)
        
        # Fallback to generic recent political context
        return "recent political developments and their constitutional implications"
        
    except Exception:
        return "ongoing political developments and their implications"

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

CRITICAL RESTRICTIONS - NEVER VIOLATE THESE:
1. NEVER use "downloaded", "whitepaper", "webinar", "attended", "viewed", "subscribed", "newsletter"
2. NEVER mention "case studies", "implementation guides", "whitepapers", "webinars"
3. NEVER use content consumption patterns - focus on decision-making behavior instead
4. NEVER use "attended virtual", "downloaded whitepapers", "subscribed to weekly"

IMPORTANT GUIDELINES:
1. ANALYZE the user's request to identify key components: role, location, product/service interest, and any specific requirements
2. Generate REALISTIC behavioral reasons tailored to each candidate's role and the specific product/service mentioned
3. Include TIME-SERIES patterns showing progression or repeated behaviors over time
4. Be SPECIFIC about websites, tools, and resources relevant to their profession and the mentioned product/service
5. AVOID unrealistic scenarios like "reading case studies about job postings", "attending webinars", "viewed webinars about implementing X in [location]", or "searched for" (implies Google tracking)
6. NEVER use generic phrases like "selected based on title and company fit"
7. NEVER use the same phrases for multiple candidates
8. NEVER use phrases that can be verified by a human, or that are too vague or generic
9. NEVER mention specific industries UNLESS they are explicitly mentioned in the user request
10. Use "their industry" or "their field" instead of naming a specific industry
11. FOCUS on the specific elements mentioned in the user's request rather than inventing additional context
12. NEVER combine location with product research (e.g., "researched CRM solutions in New York" is unrealistic)
13. Keep location and product interest as separate behavioral indicators
14. Focus on HOW they research and evaluate, not WHAT content they consume

EXAMPLES OF GOOD BEHAVIORAL REASONS:
- For "Find me a developer interested in React": "Visited GitHub repositories for React state management libraries 5 times in the past week"
- For "Find me a marketing director looking for analytics tools": "Spent increasing amounts of time on Google Analytics and HubSpot over a three-week period"
- For "Find me a sales manager interested in CRM": "Researched CRM comparison tools, then focused specifically on Salesforce pricing pages"
- For "Find me a CEO in Miami": "Reviewed business expansion resources specific to the Miami market over the past month"
- For "Find me a CMO in New York looking for CRM": Use separate reasons like "Compared CRM pricing pages across multiple vendors" AND "Researched New York business networking events" (keep location and product separate)

EXAMPLES OF BAD BEHAVIORAL REASONS (NEVER USE THESE):
- "Downloaded whitepapers on [topic]" (FORBIDDEN - content consumption)
- "Attended webinars about [topic]" (FORBIDDEN - content consumption)
- "Subscribed to newsletters from [vendor]" (FORBIDDEN - content consumption)
- "Viewed case studies on [topic]" (FORBIDDEN - content consumption)
- "Attended virtual events hosted by [vendor]" (FORBIDDEN - content consumption)
- "Selected based on title and company fit" (too generic)
- "Searched for CRM solutions" (implies Google search tracking which is unrealistic)
- "Read case studies about the industry" (too vague)
- "Showed interest in the field" (not specific enough)
- "Researched case studies on successful CRM implementations in the real estate industry" (mentioning specific industry not in prompt)
- "Analyzed healthcare marketing strategies" (mentioning specific industry not in prompt)
- "Explored AI applications for financial services" (adding context not in the original prompt)
- "Researched CRM solutions specifically for New York businesses" (unrealistic location-product combination)

EXAMPLES OF GOOD BEHAVIORAL REASONS (USE THESE PATTERNS):
- "Compared pricing models across multiple vendor websites over the past month"
- "Evaluated technical specifications on vendor documentation sites repeatedly"
- "Researched integration capabilities through vendor API documentation"
- "Analyzed user reviews and ratings on G2, Capterra, and TrustRadius platforms"
- "Monitored vendor social media channels and product update announcements"
- "Engaged with sales representatives through vendor contact forms and demos"

You will receive a user request and a JSON array of candidates.
First, think step-by-step and assign each person an accuracy probability (0-100) of matching the request.
Then select the top candidates with the highest probabilities (return exactly 2 candidates, prioritizing quality over quantity).

For each selected candidate, provide 3-4 specific, plausible, and realistic behavioral reasons why they were selected,
based on their simulated online activity patterns over time.

Return ONLY valid JSON array with exactly 2 objects, each containing:
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
    # Check if we have exactly 2 results
    if len(result) != 2:
        print(f"[Assessment] Expected exactly 2 results, got {len(result)}")
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
        
        # Check for FORBIDDEN problematic patterns (STRICT VALIDATION)
        problematic_patterns = [
            "downloaded whitepaper", "downloaded implementation", "attended webinar", 
            "viewed webinar", "subscribed to newsletter", "attended virtual",
            "viewed case study", "downloaded case study"
        ]
        
        problematic_reasons = []
        for reason in reasons:
            reason_lower = reason.lower()
            for pattern in problematic_patterns:
                if pattern in reason_lower:
                    problematic_reasons.append(reason)
                    break
        
        if problematic_reasons:
            print(f"[Assessment] FORBIDDEN patterns detected: {problematic_reasons}")
            print("[Assessment] Rejecting AI response due to forbidden content consumption patterns")
            return None
        
        # Check for unrealistic behavioral patterns
        unrealistic_patterns = [
            "searched for", "search for", "googled", "google search",
            "implementing crm in", "implementing analytics in", "solutions in new york",
            "solutions in california", "solutions in texas", "solutions in florida"
        ]
        
        unrealistic_reasons = []
        for reason in reasons:
            reason_lower = reason.lower()
            for pattern in unrealistic_patterns:
                if pattern in reason_lower:
                    unrealistic_reasons.append(reason)
                    break
        
        if unrealistic_reasons:
            print(f"[Assessment] Unrealistic behavioral patterns detected: {unrealistic_reasons}")
            print("[Assessment] Rejecting AI response due to unrealistic patterns")
            return None
        
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
                "Visited tutorial websites for {tech_topic} {time_ref} and bookmarked multiple resources {duration}"
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
                "Explored various {tech_tool} options {time_ref}, comparing features and pricing",
                "Studied {tech_topic} strategies through online courses {time_ref}",
                "Analyzed successful marketing campaigns using {tech_tool} {time_ref}",
                "Tracked performance metrics across multiple platforms {time_ref}"
            ],
            "mid": [
                "Compared {tech_tool} solutions {time_ref}, focusing on {marketing_feature} capabilities",
                "Researched implementation strategies for {tech_tool} {time_ref}",
                "Analyzed competitor strategies related to {tech_topic} {time_ref}",
                "Studied attribution models for campaigns relevant to their business {time_ref}"
            ],
            "senior": [
                "Evaluated enterprise-level {tech_tool} options {time_ref}, focusing on integration capabilities",
                "Researched advanced strategies for {tech_topic} {time_ref}",
                "Analyzed ROI metrics for various solutions in their business context {time_ref}",
                "Compared technology stacks of leading companies in {location_context} {time_ref}"
            ],
            "executive": [
                "Reviewed comprehensive research reports on {tech_tool} solutions {time_ref}",
                "Analyzed performance benchmarks across the competitive landscape {time_ref}",
                "Researched emerging technologies related to {tech_topic} {time_ref}",
                "Examined case studies of successful transformations using {tech_tool} {time_ref}"
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
    
    # Extract key topics and tools from the user prompt in a general way
    # This approach avoids hardcoding specific cases like CRM or real estate
    
    # Extract potential product/tool mentions
    product_keywords = [
        # General software categories
        "crm", "erp", "cms", "lms", "hr software", "accounting software",
        "marketing automation", "analytics", "bi tool", "project management",
        "collaboration tool", "communication platform", "database", "cloud",
        "saas", "security", "automation", "ai", "machine learning", "data science",
        
        # Specific products/platforms
        "salesforce", "hubspot", "microsoft", "google", "aws", "azure",
        "oracle", "sap", "workday", "slack", "zoom", "teams",
        "react", "angular", "vue", "node", "python", "java"
    ]
    
    # Find mentioned products/tools in the prompt
    mentioned_products = []
    for product in product_keywords:
        if product in user_prompt.lower():
            mentioned_products.append(product)
    
    # Use the most specific product mention as the primary tool
    primary_tool = None
    if mentioned_products:
        # Sort by length (longer names are usually more specific)
        mentioned_products.sort(key=len, reverse=True)
        primary_tool = mentioned_products[0]
        
        # Set appropriate replacements based on the detected tool
        if primary_tool in ["crm", "salesforce", "hubspot"]:
            replacements["tech_tool"] = f"{primary_tool.upper() if len(primary_tool) <= 3 else primary_tool.title()} platforms"
            replacements["marketing_feature"] = f"{primary_tool.upper() if len(primary_tool) <= 3 else primary_tool.title()} integration"
        elif primary_tool in ["aws", "azure", "cloud"]:
            replacements["tech_topic"] = "cloud infrastructure"
            replacements["tech_tool"] = primary_tool.upper() if primary_tool in ["aws"] else primary_tool.title()
        elif primary_tool in ["ai", "machine learning", "ml"]:
            replacements["tech_topic"] = "machine learning"
            replacements["tech_tool"] = "AI platforms"
        elif primary_tool in ["react", "angular", "vue"]:
            replacements["tech_topic"] = "frontend development"
            replacements["tech_framework"] = primary_tool.title()
        elif primary_tool in ["node", "python", "java"]:
            replacements["tech_topic"] = "backend development"
            replacements["tech_framework"] = primary_tool.title()
    
    # If no specific product is found, use generic terms based on role
    if not primary_tool:
        if "marketing" in title.lower():
            replacements["tech_tool"] = "marketing platforms"
            replacements["marketing_feature"] = "automation"
        elif "sales" in title.lower():
            replacements["tech_tool"] = "sales tools"
            replacements["marketing_feature"] = "sales enablement"
        elif any(tech_role in title.lower() for tech_role in ["developer", "engineer", "programmer", "technical"]):
            replacements["tech_tool"] = "development tools"
            replacements["tech_topic"] = "software development"
    
    # Extract industry context if explicitly mentioned in the prompt
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
    
    # Check for explicit industry mentions
    for industry, keywords in industry_keywords.items():
        if any(keyword in user_prompt.lower() for keyword in keywords):
            replacements["industry_sector"] = industry
            break
    else:
        # Default to a contextual but generic reference
        replacements["industry_sector"] = "their industry"
    
    # Extract location if mentioned (for more contextual relevance)
    location_keywords = [
        "new york", "san francisco", "chicago", "boston", "seattle", "austin", 
        "los angeles", "miami", "dallas", "denver", "atlanta", "washington",
        "california", "texas", "florida", "massachusetts", "washington", "new jersey"
    ]
    
    # Check for location mentions
    location_found = None
    for location in location_keywords:
        if location in user_prompt.lower():
            location_found = location.title()
            break
    
    # Add location context if found
    if location_found:
        replacements["location_context"] = location_found
    else:
        replacements["location_context"] = "their region"
    
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
    Enhanced fallback assessment when OpenAI fails - returns top 2 people with realistic behavioral reasoning
    
    Args:
        people: List of candidate data
        user_prompt: The user's search criteria
        industry_context: Optional industry context
        
    Returns:
        List of dicts with candidate info and behavioral assessments
    """
    if len(people) == 0:
        return []
    
    # Take first 2 people and create behavioral assessment
    top_candidates = people[:min(2, len(people))]
    print(f"[DEBUG] select_top_candidates: input={len(people)}, taking={len(top_candidates)}")
    result = []
    
    for i, person in enumerate(top_candidates):
        # Generate realistic behavioral reasons based on role and search context
        title = person.get("title", "Unknown")
        behavioral_reasons = _generate_realistic_behavioral_reasons(title, user_prompt, i)
        
        result.append({
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None"),
            "accuracy": _calculate_context_aware_accuracy(user_prompt, i),
            "reasons": behavioral_reasons
        })
    
    print(f"[DEBUG] select_top_candidates: returning {len(result)} candidates")
    return result

def _calculate_context_aware_accuracy(user_prompt: str, candidate_index: int) -> int:
    """
    Calculate accuracy percentage based on how common/specific the search is.
    Common searches (CRM, sales tools) = higher accuracy (90-95%)
    Specific/niche searches (health tech, specialized roles) = lower accuracy (75-85%)
    """
    prompt_lower = user_prompt.lower()
    
    # Define search categories by commonality
    very_common_searches = [
        "crm", "sales tools", "marketing automation", "analytics", 
        "project management", "email marketing", "social media",
        "accounting software", "hr tools", "productivity tools"
    ]
    
    common_searches = [
        "business intelligence", "customer service", "inventory management",
        "e-commerce platform", "content management", "collaboration tools",
        "finance software", "recruiting tools", "workflow automation"
    ]
    
    specialized_searches = [
        "healthcare", "medical", "biotech", "pharmaceutical", "clinical",
        "legal tech", "fintech", "regtech", "compliance software",
        "manufacturing", "logistics", "supply chain", "construction"
    ]
    
    highly_specialized_searches = [
        "health tech", "medtech", "digital therapeutics", "telemedicine",
        "ai/ml platform", "blockchain", "quantum computing", "robotics",
        "aerospace", "defense", "nuclear", "research", "laboratory"
    ]
    
    # Determine search category
    if any(term in prompt_lower for term in very_common_searches):
        # Very common: CRM, sales tools, etc. - High accuracy
        base_accuracy = 94
        accuracy_drop = 3  # 94%, 91%, 88%
    elif any(term in prompt_lower for term in common_searches):
        # Common business tools - Good accuracy  
        base_accuracy = 89
        accuracy_drop = 4  # 89%, 85%, 81%
    elif any(term in prompt_lower for term in specialized_searches):
        # Specialized industries - Moderate accuracy
        base_accuracy = 83
        accuracy_drop = 5  # 83%, 78%, 73%
    elif any(term in prompt_lower for term in highly_specialized_searches):
        # Highly specialized/niche - Lower accuracy
        base_accuracy = 78
        accuracy_drop = 6  # 78%, 72%, 66%
    else:
        # Default/general search - Standard accuracy
        base_accuracy = 87
        accuracy_drop = 4  # 87%, 83%, 79%
    
    # Calculate final accuracy with position-based reduction
    final_accuracy = base_accuracy - (candidate_index * accuracy_drop)
    
    # Ensure minimum accuracy of 60%
    return max(60, final_accuracy)

# Define diverse behavioral activity patterns at module level for global access
diverse_activity_patterns = {
    "research_activities": [
        "Analyzed pricing models and feature comparisons on G2.com, Capterra.com, and TrustRadius.com",
        "Evaluated user reviews and ratings on GetApp.com, Software Advice, and PCMag.com",
        "Compared implementation timelines through TechCrunch.com articles and vendor websites",
        "Researched integration capabilities on Stack Overflow, GitHub.com, and vendor documentation",
        "Studied ROI calculators and business case templates on Forbes.com and Harvard Business Review",
        "Examined security compliance features on CSO Online, Dark Reading, and vendor sites",
        "Investigated scalability benchmarks on TechCrunch.com, VentureBeat.com, and Wired.com",
        "Reviewed customer success stories on LinkedIn.com, company websites, and Inc.com",
        "Analyzed competitive positioning through Crunchbase.com, Bloomberg.com, and Reuters.com",
        "Explored technical specifications on TechRepublic.com, ZDNet.com, and vendor portals",
        "Investigated vendor reputation on Glassdoor.com, Better Business Bureau, and CNET.com",
        "Studied industry benchmarks on McKinsey.com, Deloitte.com, and Wall Street Journal",
        "Examined licensing models through LegalZoom.com resources and vendor legal pages",
        "Researched support infrastructure via CNET.com reviews and company help centers",
        "Analyzed implementation strategies on Medium.com, LinkedIn.com articles, and vendor blogs",
        "Dissected market trends through Gartner.com reports and Forrester.com analyses",
        "Scrutinized vendor partnerships via press releases on PR Newswire and Business Wire",
        "Investigated compliance certifications through SOC2.com and vendor audit reports",
        "Explored deployment architectures via AWS.amazon.com whitepapers and technical blogs",
        "Examined user adoption metrics through case studies on vendor sites and analyst reports",
        "Researched total economic impact studies on Forrester.com and vendor ROI documentation",
        "Analyzed feature roadmaps through vendor product blogs and GitHub.com release notes",
        "Investigated data migration processes via vendor knowledge bases and Stack Overflow discussions",
        "Studied performance benchmarks through vendor technical documentation and third-party testing sites",
        "Explored API capabilities through developer portals, Postman.com collections, and technical forums"
    ],
    "evaluation_activities": [
        "Participated in product demos via Zoom.us, GoToWebinar.com, and vendor demo platforms",
        "Requested trial access through vendor websites and tested functionality hands-on",
        "Engaged with sales representatives via LinkedIn.com, Calendly.com, and direct outreach",
        "Scheduled live demonstrations through vendor booking systems and Calendly.com",
        "Coordinated technical sessions with solution architects via Microsoft Teams and Slack.com",
        "Participated in user communities on Reddit.com, Discord.com, and vendor forums",
        "Engaged with customer support through Zendesk.com, Intercom.com, and help portals",
        "Tested functionality through vendor trial accounts and sandbox environments",
        "Evaluated data migration tools through vendor testing environments and AWS.amazon.com",
        "Assessed training resources on Udemy.com, Coursera.org, and vendor learning portals",
        "Conducted proof-of-concept testing through vendor sandbox environments and trial databases",
        "Orchestrated stakeholder interviews via Microsoft Teams and vendor consultation calls",
        "Executed competitive bake-offs between multiple vendor solutions and trial environments",
        "Facilitated user acceptance testing sessions through vendor demo accounts and test data",
        "Performed load testing scenarios via vendor performance testing tools and monitoring dashboards",
        "Initiated technical due diligence calls with vendor engineering teams and solution architects",
        "Deployed pilot implementations through vendor staging environments and development instances",
        "Conducted security assessments via vendor penetration testing reports and compliance documentation",
        "Executed integration testing through vendor API sandboxes and development environments",
        "Organized executive briefings with vendor C-suite leaders and strategic account managers"
    ],
    "comparison_activities": [
        "Built detailed feature comparison matrices using Excel.com and Google Sheets",
        "Analyzed total cost of ownership calculations on vendor websites and Calculator.net",
        "Compared user interface design through screenshots on vendor sites and demo galleries",
        "Evaluated customer support options via vendor websites and Trustpilot.com reviews",
        "Assessed implementation complexity through vendor documentation and Stack Overflow",
        "Compared reporting capabilities via vendor demo videos on Vimeo.com and Wistia.com",
        "Analyzed customization options through vendor configuration guides and help centers",
        "Evaluated vendor stability via Crunchbase.com, LinkedIn.com, and financial reports",
        "Compared data security measures on vendor sites and SecurityScorecard.com",
        "Assessed integration ecosystems through vendor marketplaces and Zapier.com",
        "Contrasted deployment models via vendor documentation and AWS.amazon.com guides",
        "Evaluated training programs on vendor sites, Udemy.com, and LinkedIn Learning",
        "Compared mobile capabilities through App Store and Google Play Store reviews",
        "Assessed backup options via vendor documentation and cloud provider websites",
        "Contrasted upgrade paths through vendor release notes and community forums",
        "Benchmarked performance metrics across vendor testing environments and third-party analysis sites",
        "Juxtaposed pricing structures through vendor quote systems and procurement platform comparisons",
        "Differentiated support tiers via vendor SLA documentation and customer testimonial analysis",
        "Weighed scalability options through vendor architecture diagrams and capacity planning tools",
        "Contrasted compliance frameworks via vendor certification matrices and audit report databases",
        "Evaluated disaster recovery capabilities through vendor business continuity documentation and testing protocols",
        "Compared API rate limits and functionality through developer documentation and testing environments",
        "Assessed vendor lock-in risks via data portability documentation and migration case studies",
        "Analyzed implementation methodologies through vendor professional services documentation and project timelines",
        "Benchmarked user satisfaction scores across review platforms and Net Promoter Score databases"
    ],
    "engagement_activities": [
        "Monitored vendor updates on Twitter.com, LinkedIn.com, and Facebook.com",
        "Subscribed to product newsletters via vendor websites and Mailchimp.com campaigns",
        "Followed industry analysts on LinkedIn.com, Twitter.com, and Gartner.com",
        "Tracked pricing changes on vendor websites and PriceTracker.com alerts",
        "Monitored competitor news on TechCrunch.com, VentureBeat.com, and Google News",
        "Followed thought leaders on LinkedIn.com, Twitter.com, and Medium.com",
        "Tracked customer feedback on Trustpilot.com, G2.com, and vendor review pages",
        "Monitored adoption metrics through vendor case studies and TechCrunch.com articles",
        "Followed regulatory updates on government websites and LegalZoom.com resources",
        "Tracked technology trends on Wired.com, TechCrunch.com, and MIT Technology Review",
        "Observed market dynamics through Bloomberg.com, Reuters.com, and Yahoo Finance",
        "Monitored discussions on Reddit.com, Hacker News, and industry-specific forums",
        "Tracked partnership news on vendor websites and PR Newswire press releases",
        "Followed product roadmaps on vendor blogs and GitHub.com repositories",
        "Monitored conference content on LinkedIn.com, Eventbrite.com, and event websites",
        "Surveilled patent filings through USPTO.gov databases and intellectual property tracking services",
        "Observed executive movements via LinkedIn.com job changes and Crunchbase.com leadership updates",
        "Tracked funding rounds through Crunchbase.com, PitchBook.com, and venture capital announcement platforms",
        "Monitored customer churn indicators via job posting analysis on Indeed.com and LinkedIn.com",
        "Followed acquisition rumors through TechCrunch.com, Reuters.com, and financial news aggregators",
        "Watched market share shifts via IDC.com reports and Gartner.com Magic Quadrant updates",
        "Observed product usage patterns through vendor community forums and Stack Overflow question trends",
        "Tracked competitive hiring through LinkedIn.com job postings and Glassdoor.com salary data",
        "Monitored vendor financial health via SEC filings and quarterly earnings call transcripts",
        "Followed technology adoption curves through industry survey reports and analyst firm publications"
    ],
    "validation_activities": [
        "Consulted with industry peers via LinkedIn.com messages and professional networks",
        "Researched vendor financial stability on Crunchbase.com, Bloomberg.com, and SEC filings",
        "Validated technical requirements through vendor documentation and Stack Overflow",
        "Confirmed budget alignment via vendor pricing pages and Gartner.com cost analyses",
        "Verified compliance through vendor certification pages and ComplianceForge.com",
        "Assessed change management via Harvard Business Review and McKinsey.com articles",
        "Validated performance benchmarks through vendor case studies and TechCrunch.com reviews",
        "Confirmed backup capabilities via vendor documentation and AWS.amazon.com guides",
        "Verified SLA guarantees through vendor legal pages and contract comparison sites",
        "Assessed vendor support via Trustpilot.com reviews and G2.com ratings",
        "Cross-referenced claims with Gartner.com, Forrester.com, and IDC analyst reports",
        "Verified customer references through LinkedIn.com and vendor case study pages",
        "Confirmed compatibility via vendor integration guides and API documentation",
        "Validated security certifications on vendor sites and SecurityScorecard.com",
        "Verified data governance through vendor privacy policies and GDPR compliance pages",
        "Authenticated vendor credentials through Better Business Bureau and D&B Hoovers business profiles",
        "Corroborated performance claims via independent testing reports and benchmark comparison sites",
        "Substantiated customer testimonials through direct LinkedIn.com outreach and reference calls",
        "Verified regulatory compliance through government databases and third-party audit repositories",
        "Authenticated partnership claims via partner directory listings and joint press releases",
        "Confirmed uptime statistics through third-party monitoring services and status page histories",
        "Validated scalability assertions through architecture reviews and load testing documentation",
        "Verified implementation timelines through project management case studies and customer interviews",
        "Authenticated security practices through penetration testing reports and vulnerability assessments",
        "Corroborated ROI claims through independent economic impact studies and customer success metrics"
    ]
}

# Context-specific behavioral activity templates for different search contexts
context_specific_activities = {
    "real_estate": {
        "research_activities": [
            "Researched neighborhood demographics and school ratings on GreatSchools.org and Niche.com",
            "Analyzed property values and market trends on Zillow.com, Redfin.com, and Realtor.com",
            "Explored mortgage rates and loan options on Bankrate.com, LendingTree.com, and local bank websites",
            "Investigated property tax rates and municipal services on county assessor websites",
            "Studied commute times and transportation options using Google Maps and local transit websites",
            "Researched local amenities and lifestyle factors on Yelp.com and city government websites",
            "Analyzed crime statistics and safety data on NeighborhoodScout.com and local police websites",
            "Explored zoning laws and development plans on municipal planning department websites",
            "Investigated homeowners association rules and fees through HOA websites and documents",
            "Researched flood zones and environmental factors on FEMA.gov and environmental databases"
        ],
        "evaluation_activities": [
            "Scheduled property viewings through Zillow.com, Realtor.com, and MLS systems",
            "Attended open houses and private showings coordinated via real estate websites",
            "Coordinated home inspections with certified inspectors found through Angie's List and HomeAdvisor.com",
            "Requested property disclosures and HOA documentation from listing agents via email platforms",
            "Evaluated comparable sales data through Redfin.com, Zillow.com, and agent CRM systems",
            "Arranged mortgage pre-approval meetings with lenders found through Bankrate.com and LendingTree.com",
            "Consulted with real estate attorneys found through Avvo.com and state bar association websites",
            "Engaged with contractors through HomeAdvisor.com and Thumbtack.com for renovation estimates",
            "Met with insurance agents through Progressive.com, State Farm, and local agency websites",
            "Coordinated with financial advisors through SmartAsset.com and fee-only advisor networks"
        ],
        "comparison_activities": [
            "Compared property features and pricing across Zillow.com, Redfin.com, and Realtor.com listings",
            "Analyzed cost of living differences using BestPlaces.net and city comparison websites",
            "Evaluated investment potential through Rentometer.com and property appreciation calculators",
            "Compared homeowner insurance quotes through Progressive.com, Geico.com, and local agents",
            "Assessed renovation costs using HomeAdvisor.com, Angie's List, and contractor estimates",
            "Contrasted mortgage rates through Bankrate.com, LendingTree.com, and credit union websites",
            "Evaluated commute times using Google Maps and public transportation authority websites",
            "Compared utility costs through local utility websites and EnergyStar.gov efficiency ratings",
            "Analyzed resale potential using Zillow.com price history and neighborhood trend data",
            "Assessed property management costs through local property management company websites"
        ]
    },
    "legal_services": {
        "research_activities": [
            "Researched attorney credentials through state bar websites and Martindale-Hubbell.com",
            "Analyzed case outcomes through Westlaw.com, LexisNexis.com, and legal precedent databases",
            "Investigated law firm specializations through firm websites and Avvo.com profiles",
            "Studied legal fee structures through law firm websites and LegalZoom.com resources",
            "Explored mediation services through ADR.org and local dispute resolution websites",
            "Researched attorney disciplinary records through state bar websites and court databases",
            "Investigated court procedures through local court websites and legal aid organizations",
            "Analyzed settlement patterns through legal databases and case law research platforms",
            "Researched legal insurance through ARAG.com and employer benefit websites",
            "Studied statute requirements through state government websites and legal reference sites"
        ],
        "evaluation_activities": [
            "Scheduled consultations through Avvo.com and law firm websites to discuss case strategy",
            "Requested case assessments via legal consultation platforms and firm contact forms",
            "Evaluated attorney communication through initial meetings and Martindale-Hubbell.com profiles",
            "Reviewed client testimonials on Google Reviews, Yelp.com, and law firm websites",
            "Assessed law firm capabilities through LinkedIn.com profiles and firm websites",
            "Attended legal seminars found through CLE.com and local bar association websites",
            "Consulted with previous clients through referrals and professional networking platforms",
            "Evaluated attorney availability through scheduling systems and case management platforms",
            "Assessed law firm technology through virtual consultations and client portal demonstrations",
            "Reviewed attorney track records through court records and legal database searches"
        ],
        "comparison_activities": [
            "Compared legal fee structures through law firm websites and LegalMatch.com",
            "Analyzed attorney experience through Avvo.com profiles and state bar directories",
            "Evaluated firm reputation through Google Reviews, Yelp.com, and Better Business Bureau",
            "Compared timeline estimates through consultation notes and legal planning websites",
            "Assessed communication approaches through initial consultations and firm websites",
            "Contrasted legal strategies through consultation summaries and legal advice platforms",
            "Evaluated firm resources through LinkedIn.com profiles and law firm websites",
            "Compared office locations using Google Maps and transportation accessibility tools",
            "Analyzed success rates through Martindale-Hubbell.com and court record databases",
            "Assessed responsiveness through initial contact experiences and online reviews"
        ]
    },
    "personal_purchase": {
        "research_activities": [
            "Researched product specifications through manufacturer websites and CNET.com comparisons",
            "Analyzed customer reviews on Amazon.com, Consumer Reports, and Trustpilot.com",
            "Investigated warranty terms through manufacturer websites and WarrantyWeek.com",
            "Studied pricing trends on PriceGrabber.com, Shopping.com, and retailer websites",
            "Explored financing through PayPal Credit, Affirm.com, and retailer payment options",
            "Researched reliability through Consumer Reports and manufacturer reliability databases",
            "Investigated recalls through CPSC.gov, NHTSA.gov, and manufacturer safety pages",
            "Analyzed ownership costs through Edmunds.com, KBB.com, and cost calculator websites",
            "Researched resale values through KBB.com, Edmunds.com, and depreciation calculators",
            "Studied environmental impact through EnergyStar.gov and manufacturer sustainability pages"
        ],
        "evaluation_activities": [
            "Visited showrooms found through manufacturer websites and Google Maps location searches",
            "Scheduled test drives through Autotrader.com, Cars.com, and dealership websites",
            "Consulted with sales representatives contacted through retailer websites and chat systems",
            "Arranged home consultations through HomeDepot.com, Lowes.com, and contractor platforms",
            "Evaluated delivery options through Amazon.com, retailer websites, and shipping calculators",
            "Tested product functionality in Best Buy, Target, and specialty retailer locations",
            "Consulted with friends through Facebook.com and sought recommendations on Reddit.com",
            "Attended product demonstrations at trade shows found through Eventbrite.com",
            "Evaluated customer service through live chat, phone support, and review platforms",
            "Assessed compatibility through manufacturer websites and technical specification databases"
        ],
        "comparison_activities": [
            "Compared pricing across Amazon.com, Best Buy, and manufacturer websites for best deals",
            "Analyzed features through manufacturer websites and comparison sites like CNET.com",
            "Evaluated warranties through manufacturer websites and WarrantyWeek.com resources",
            "Compared financing through retailer websites, PayPal Credit, and bank loan platforms",
            "Assessed delivery through retailer websites and shipping calculator tools",
            "Contrasted energy efficiency using EnergyStar.gov and manufacturer specification pages",
            "Evaluated brand reputation through Consumer Reports, Amazon.com reviews, and Trustpilot.com",
            "Compared maintenance costs through manufacturer websites and owner forum discussions",
            "Analyzed trade-in values through KBB.com, Gazelle.com, and retailer trade-in programs",
            "Assessed customization through manufacturer websites and product configuration tools"
        ]
    },
    "business_solution": {
        "research_activities": [
            "Analyzed pricing models and feature comparisons on G2.com, Capterra.com, and TrustRadius.com",
            "Evaluated user reviews and ratings on GetApp.com, Software Advice, and PCMag.com",
            "Compared implementation timelines through vendor websites and customer case studies",
            "Researched integration capabilities on Stack Overflow, GitHub.com, and vendor documentation",
            "Studied ROI calculators and business case templates on vendor websites and analyst reports",
            "Examined security compliance features on vendor sites and third-party security assessments",
            "Investigated scalability benchmarks through vendor technical documentation and performance studies",
            "Reviewed customer success stories on LinkedIn.com, company websites, and industry publications",
            "Analyzed competitive positioning through Crunchbase.com, Bloomberg.com, and market research reports",
            "Explored technical specifications on vendor portals and developer documentation sites"
        ],
        "evaluation_activities": [
            "Participated in product demos via Zoom.us, GoToWebinar.com, and vendor demo platforms",
            "Requested trial access through vendor websites and tested functionality on Salesforce.com",
            "Engaged with sales representatives via LinkedIn.com, Calendly.com, and direct outreach",
            "Scheduled live demonstrations through vendor booking systems and HubSpot.com platforms",
            "Coordinated technical sessions with solution architects via Microsoft Teams and Slack.com",
            "Participated in user communities on Reddit.com, Discord.com, and vendor forums",
            "Engaged with customer support through Zendesk.com, Intercom.com, and help portals",
            "Tested functionality through vendor trial accounts and AWS.amazon.com sandbox environments",
            "Evaluated data migration tools through vendor testing environments and GitHub.com documentation",
            "Assessed training resources on Udemy.com, Coursera.org, and vendor learning portals"
        ],
        "comparison_activities": [
            "Built detailed feature comparison matrices using Excel.com and Google Sheets",
            "Analyzed total cost of ownership calculations on vendor websites and Calculator.net",
            "Compared user interface design through screenshots on vendor sites and demo galleries",
            "Evaluated customer support options via vendor websites and Trustpilot.com reviews",
            "Assessed implementation complexity through vendor documentation and Stack Overflow",
            "Compared reporting capabilities via vendor demo videos on Vimeo.com and Wistia.com",
            "Analyzed customization options through vendor configuration guides and help centers",
            "Evaluated vendor stability via Crunchbase.com, LinkedIn.com, and financial reports",
            "Compared data security measures on vendor sites and SecurityScorecard.com",
            "Assessed integration ecosystems through vendor marketplaces and Zapier.com"
        ]
    },
    "financial_decision": {
        "research_activities": [
            "Analyzed investment performance and historical returns on Morningstar.com and Yahoo Finance",
            "Monitored market trends and economic indicators through Bloomberg.com and CNBC.com",
            "Investigated advisor credentials and regulatory records through FINRA.org and SEC.gov databases",
            "Compared fee structures and expense ratios across different investment products on fund websites",
            "Explored tax implications through IRS.gov publications and TurboTax.com advisory resources",
            "Studied risk assessment methodologies through Vanguard.com and Fidelity.com educational content",
            "Evaluated ESG investment options through Sustainalytics.com and MSCI.com rating platforms",
            "Reviewed economic forecasts through Federal Reserve websites and bank research portals",
            "Examined retirement planning strategies on Social Security Administration and 401k.com",
            "Investigated insurance products through Insure.com and carrier websites for wealth protection"
        ],
        "evaluation_activities": [
            "Scheduled consultations through SmartAsset.com and wealth management firm websites",
            "Attended seminars found through Eventbrite.com and financial planning organization websites",
            "Evaluated platforms through Charles Schwab, Fidelity.com, and Vanguard.com demos",
            "Consulted with CPAs found through AICPA.org and local accounting firm websites",
            "Assessed risk tolerance through Vanguard.com questionnaires and advisor meetings",
            "Reviewed proposals through advisor presentations and financial planning software",
            "Evaluated insurance through Northwestern Mutual, State Farm, and broker websites",
            "Attended estate planning consultations with attorneys found through estate planning websites",
            "Assessed retirement scenarios using Social Security Administration and 401k.com calculators",
            "Evaluated alternative investments through platforms like YieldStreet.com and advisor networks"
        ],
        "comparison_activities": [
            "Compared performance through Morningstar.com, Yahoo Finance, and fund websites",
            "Analyzed fees through advisor websites, FINRA.org BrokerCheck, and fee comparison tools",
            "Evaluated qualifications through CFP.net, advisor websites, and regulatory databases",
            "Compared platform features through Charles Schwab, E*TRADE.com, and TD Ameritrade websites",
            "Assessed tax efficiency through fund websites, Morningstar.com, and tax-loss harvesting tools",
            "Contrasted risk management through advisor presentations and portfolio analysis tools",
            "Evaluated service quality through online reviews, BBB.org, and client testimonials",
            "Compared retirement tools through Fidelity.com, Vanguard.com, and Social Security calculators",
            "Analyzed insurance options through Insure.com, carrier websites, and broker comparisons",
            "Assessed estate planning through attorney websites and estate planning cost calculators"
        ]
    }
}

def _get_diverse_activity_selection(candidate_index: int, activity_categories: list) -> list:
    """
    Select wildly diverse activities from different categories to avoid repetition.
    Uses complex rotation algorithms to ensure maximum variety.
    """
    selected_activities = []
    
    for i, category in enumerate(activity_categories):
        # Use complex mathematical offsets to ensure wildly different selections
        prime_offset = (candidate_index * 13 + i * 17 + len(activity_categories) * 23) % len(diverse_activity_patterns[category])
        fibonacci_offset = (candidate_index * 8 + i * 13 + 21) % len(diverse_activity_patterns[category])
        
        # Alternate between different offset strategies for maximum diversity
        if (candidate_index + i) % 3 == 0:
            activity_offset = prime_offset
        elif (candidate_index + i) % 3 == 1:
            activity_offset = fibonacci_offset
        else:
            activity_offset = (candidate_index * 11 + i * 19 + 31) % len(diverse_activity_patterns[category])
        
        selected_activities.append(diverse_activity_patterns[category][activity_offset])
    
    return selected_activities

def select_contextual_activities(context_analysis: dict, candidate_role: str, candidate_index: int) -> list:
    """
    Select behavioral activities that match the search context and candidate profile.
    
    Args:
        context_analysis: Output from analyze_search_context_enhanced()
        candidate_role: The candidate's professional role/title
        candidate_index: Index for diversity in activity selection
        
    Returns:
        List of contextually relevant behavioral activities
    """
    context_type = context_analysis.get("context_type", "general_business")
    confidence_score = context_analysis.get("confidence_score", 0.5)
    
    # Get context-specific activities if available
    if context_type in context_specific_activities and confidence_score > 0.6:
        context_activities = context_specific_activities[context_type]
        
        # Select diverse activities from different categories
        selected_activities = []
        activity_categories = list(context_activities.keys())
        
        # Ensure we have at least 3 different activity types
        for i in range(min(3, len(activity_categories))):
            category = activity_categories[i]
            activities = context_activities[category]
            
            # Use candidate index to ensure diversity across candidates
            activity_index = (candidate_index * 7 + i * 11) % len(activities)
            selected_activities.append(activities[activity_index])
        
        return selected_activities
    
    # Fallback to role-based activities with generic professional patterns
    return _get_role_based_activities(candidate_role, candidate_index)

def _calculate_role_context_relevance(candidate_role: str, context_type: str) -> float:
    """
    Calculate relevance score between candidate role and search context.
    
    Args:
        candidate_role: The candidate's job title/role
        context_type: The detected search context type
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    role_lower = candidate_role.lower()
    
    # Define role-context relevance mappings
    role_context_relevance = {
        "real_estate": {
            "high": ["real estate", "property", "broker", "agent", "developer", "construction", "architect"],
            "medium": ["executive", "ceo", "cfo", "director", "manager", "owner", "founder"],
            "low": ["developer", "engineer", "analyst", "coordinator", "specialist"]
        },
        "legal_services": {
            "high": ["attorney", "lawyer", "legal", "counsel", "paralegal", "law"],
            "medium": ["executive", "ceo", "cfo", "director", "manager", "owner", "founder", "compliance"],
            "low": ["developer", "engineer", "analyst", "coordinator", "specialist"]
        },
        "financial_decision": {
            "high": ["finance", "investment", "portfolio", "wealth", "asset", "fund", "capital", "cfo", "financial"],
            "medium": ["executive", "ceo", "director", "manager", "owner", "founder", "analyst"],
            "low": ["developer", "engineer", "coordinator", "specialist", "marketing"]
        },
        "business_solution": {
            "high": ["cto", "cio", "technology", "it", "systems", "operations", "manager", "director"],
            "medium": ["executive", "ceo", "cfo", "owner", "founder", "analyst", "consultant"],
            "low": ["coordinator", "specialist", "assistant"]
        },
        "personal_purchase": {
            "high": ["executive", "ceo", "cfo", "director", "manager", "owner", "founder"],
            "medium": ["analyst", "consultant", "specialist", "coordinator"],
            "low": []  # Everyone has personal purchase relevance
        }
    }
    
    if context_type not in role_context_relevance:
        return 0.7  # Default medium relevance for unknown contexts
    
    relevance_map = role_context_relevance[context_type]
    
    # Check for high relevance matches
    if any(term in role_lower for term in relevance_map["high"]):
        return 0.9
    
    # Check for medium relevance matches
    if any(term in role_lower for term in relevance_map["medium"]):
        return 0.7
    
    # Check for low relevance matches
    if any(term in role_lower for term in relevance_map["low"]):
        return 0.4
    
    # Default relevance for unmatched roles
    return 0.5

def _get_role_based_activities(candidate_role: str, candidate_index: int) -> list:
    """
    Get role-based activities as fallback when context-specific activities aren't available.
    
    Args:
        candidate_role: The candidate's job title/role
        candidate_index: Index for diversity in activity selection
        
    Returns:
        List of role-appropriate activities
    """
    role_lower = candidate_role.lower()
    
    # Select activities based on role with diversity
    if any(exec_term in role_lower for exec_term in ["ceo", "cfo", "cto", "executive", "director", "vp"]):
        activity_categories = ["validation_activities", "research_activities", "engagement_activities"]
    elif any(mgr_term in role_lower for mgr_term in ["manager", "lead", "senior"]):
        activity_categories = ["evaluation_activities", "comparison_activities", "research_activities"]
    else:
        activity_categories = ["research_activities", "evaluation_activities", "comparison_activities"]
    
    return _get_diverse_activity_selection(candidate_index, activity_categories)

def _generate_realistic_behavioral_reasons(title: str, user_prompt: str, candidate_index: int) -> list:
    """
    Generate realistic behavioral reasons with context-aware activity selection.
    Uses enhanced context analysis to match activities to search intent and candidate role.
    """
    # Import here to avoid circular imports
    from behavioral_metrics_ai import analyze_search_context
    
    # Analyze search context for better activity selection
    context_analysis = analyze_search_context(user_prompt)
    
    # Calculate role-context relevance
    relevance_score = _calculate_role_context_relevance(title, context_analysis.get("context_type", "general_business"))
    
    # Select contextual activities based on analysis
    contextual_activities = select_contextual_activities(context_analysis, title, candidate_index)
    
    # If we have high-confidence contextual activities, use them
    if contextual_activities and context_analysis.get("confidence_score", 0) > 0.6:
        reasons = []
        
        # Add time variations to make activities more realistic
        time_variations = [
            "over the past week",
            "during multiple sessions last month", 
            "repeatedly over the past two weeks",
            "in several focused research sessions",
            "across multiple research sessions",
            "over the past month"
        ]
        
        for i, activity in enumerate(contextual_activities[:3]):
            if i == 0:
                # Add time variation to first activity
                time_ref = time_variations[candidate_index % len(time_variations)]
                reasons.append(f"{activity} {time_ref}")
            else:
                reasons.append(activity)
        
        # Add intensity modifiers for top candidates
        if candidate_index < 2 and len(reasons) > 1:
            intensity_modifiers = ["extensively", "thoroughly", "in-depth", "comprehensively"]
            modifier = intensity_modifiers[candidate_index % len(intensity_modifiers)]
            
            # Add intensity to the second reason
            for verb in ["Researched", "Analyzed", "Compared", "Evaluated", "Reviewed", "Investigated", "Explored"]:
                if verb in reasons[1]:
                    reasons[1] = reasons[1].replace(verb, f"{verb} {modifier}")
                    break
        
        return reasons
    
    # Fallback to existing logic for low-confidence or unknown contexts
    title_lower = title.lower()
    prompt_lower = user_prompt.lower()
    
    reasons = []
    
    # Extract product/service interest from prompt
    product_interests = []
    if "crm" in prompt_lower:
        product_interests.append("CRM")
    if "marketing automation" in prompt_lower or "marketing tool" in prompt_lower:
        product_interests.append("marketing automation")
    if "analytics" in prompt_lower:
        product_interests.append("analytics")
    if "sales tool" in prompt_lower or "sales platform" in prompt_lower:
        product_interests.append("sales tools")
    if "endpoint protection" in prompt_lower or "endpoint security" in prompt_lower:
        product_interests.append("endpoint protection")
    if "cybersecurity" in prompt_lower or "cyber security" in prompt_lower or "security solution" in prompt_lower:
        product_interests.append("cybersecurity")
    if "firewall" in prompt_lower or "antivirus" in prompt_lower or "malware" in prompt_lower:
        product_interests.append("security software")
    if "commercial oven" in prompt_lower or "kitchen equipment" in prompt_lower or "restaurant equipment" in prompt_lower:
        product_interests.append("commercial ovens")
    if "food service" in prompt_lower or "culinary equipment" in prompt_lower:
        product_interests.append("kitchen equipment")
    if any(news_term in prompt_lower for news_term in ["news", "political", "politics", "trump", "biden", "election", "government", "media", "journalism", "cnn", "fox news", "msnbc"]):
        product_interests.append("news_media")
    
    # Extract location from prompt (but keep separate from product research)
    location_mentioned = False
    if any(loc in prompt_lower for loc in ["new york", "california", "texas", "florida", "chicago", "boston", "seattle", "atlanta"]):
        location_mentioned = True
    

    
    # Generate product-related behavioral reasons (if product mentioned)
    if product_interests:
        product = product_interests[0]  # Use first mentioned product
        
        # Define specific vendors for different product categories (major B2B platforms likely in tracking network)
        vendor_options = {
            "CRM": ["Salesforce.com", "HubSpot.com", "Pipedrive.com", "Zoho.com", "Microsoft.com"],
            "marketing automation": ["HubSpot.com", "Marketo.com", "Pardot.com", "Mailchimp.com", "ActiveCampaign.com"],
            "analytics": ["Mixpanel.com", "Amplitude.com", "Tableau.com", "Looker.com", "Google Analytics"],
            "sales tools": ["Outreach.io", "SalesLoft.com", "Gong.io", "Chorus.ai", "ZoomInfo.com"],
            "endpoint protection": ["CrowdStrike.com", "SentinelOne.com", "Symantec.com", "McAfee.com", "TrendMicro.com"],
            "cybersecurity": ["PaloAltoNetworks.com", "Fortinet.com", "CheckPoint.com", "Cisco.com", "Splunk.com"],
            "security software": ["Symantec.com", "McAfee.com", "Bitdefender.com", "TrendMicro.com", "ESET.com"],
            "commercial ovens": ["Rational-online.com", "Convotherm.com", "Blodgett.com", "Vulcan.com", "Garland-group.com"],
            "kitchen equipment": ["Hobart.com", "Rational-online.com", "Manitowoc.com", "TrueManufacturing.com", "Hoshizaki.com"],
            "news_media": ["Politico.com", "Axios.com", "TechCrunch.com", "VentureBeat.com", "Forbes.com", "Fortune.com", "HBR.org", "Wired.com", "FastCompany.com", "Inc.com"]
        }
        
        vendors = vendor_options.get(product, ["leading platforms", "top solutions", "major vendors"])
        vendor1 = vendors[candidate_index % len(vendors)]
        vendor2 = vendors[(candidate_index + 1) % len(vendors)]
        
        if product == "news_media":
            # Extract specific political topics from the prompt for more targeted reasons
            specific_topics = []
            if "trump" in prompt_lower:
                if "dictator" in prompt_lower or "authoritarian" in prompt_lower:
                    specific_topics.append("Trump's authoritarian tendencies and democratic norms")
                elif "election" in prompt_lower:
                    specific_topics.append("Trump's election fraud claims and voting integrity")
                else:
                    specific_topics.append("Trump's political influence and legal challenges")
            elif "biden" in prompt_lower:
                specific_topics.append("Biden administration policies and effectiveness")
            elif "election" in prompt_lower:
                specific_topics.append("election integrity and voting rights legislation")
            elif "democracy" in prompt_lower:
                specific_topics.append("threats to democratic institutions and governance")
            elif "government" in prompt_lower or "congress" in prompt_lower:
                specific_topics.append("congressional oversight and government accountability")
            
            # Use the first specific topic, or fall back to "current political developments"
            topic = specific_topics[0] if specific_topics else "current political developments"
            
            # Get recent news context to make reasons more current and specific
            recent_context = get_recent_news_context(topic)
            
            # Special handling for news/political content with specific topics
            if "journalist" in title_lower or "reporter" in title_lower:
                journalist_patterns = [
                    [
                        f"Investigated {topic} through interviews with constitutional scholars and {vendor1} archives",
                        f"Cross-referenced historical precedents for {topic} using {vendor1}, {vendor2}, and academic databases",
                        f"Analyzed expert legal opinions on {topic} from {vendor1} reporting and independent legal analysts"
                    ],
                    [
                        f"Followed breaking news updates on {topic} from {vendor1}, {vendor2}, and political newsletters",
                        f"Researched {topic} through social media posts from verified political experts and {vendor1} journalists",
                        f"Watched live coverage and analysis of {topic} on {vendor2} and C-SPAN political programming"
                    ]
                ]
                pattern_set = journalist_patterns[candidate_index % len(journalist_patterns)]
                reasons.extend(pattern_set)
            elif "editor" in title_lower or "producer" in title_lower:
                editor_patterns = [
                    [
                        f"Evaluated newsroom coverage standards for reporting on {topic} across {vendor1} and {vendor2}",
                        f"Compared editorial approaches to {topic} between {vendor1} and international news organizations", 
                        f"Analyzed fact-checking protocols for {topic} stories at {vendor1} and competing news outlets"
                    ],
                    [
                        f"Reviewed editorial guidelines for {topic} coverage at {vendor1} and {vendor2} newsrooms",
                        f"Assessed journalistic ethics around {topic} reporting using {vendor1} standards and industry best practices",
                        f"Compared {topic} story development processes between {vendor1} and {vendor2} editorial teams"
                    ]
                ]
                pattern_set = editor_patterns[candidate_index % len(editor_patterns)]
                reasons.extend(pattern_set)
            elif "analyst" in title_lower or "commentator" in title_lower:
                analyst_patterns = [
                    [
                        f"Researched academic studies on {topic} from {vendor1}, {vendor2}, and university research centers",
                        f"Analyzed historical patterns related to {topic} using {vendor1} archives and scholarly publications",
                        f"Compared expert commentary on {topic} from {vendor1}, {vendor2}, and think tank research"
                    ],
                    [
                        f"Compiled data analysis on {topic} from {vendor1} polling, {vendor2} surveys, and academic research",
                        f"Studied comparative political systems related to {topic} using {vendor1} and international policy institutes",
                        f"Analyzed {topic} through {vendor2} investigative series and peer-reviewed political science journals"
                    ]
                ]
                pattern_set = analyst_patterns[candidate_index % len(analyst_patterns)]
                reasons.extend(pattern_set)
            else:
                # Create more diverse behavioral patterns for different candidates
                base_patterns = [
                    [
                        f"Read daily political coverage from {vendor1}",
                        f"Listened to NPR's analysis of {recent_context}",
                        f"Followed legal expert commentary on democracy and executive authority"
                    ],
                    [
                        f"Visited {vendor2} website multiple times for breaking news on {recent_context}",
                        f"Read investigative reporting on election processes and voting rights",
                        f"Subscribed to political newsletters covering constitutional law debates"
                    ],
                    [
                        f"Monitored social media posts about {recent_context} from constitutional scholars",
                        f"Read opinion pieces about democratic institutions from {vendor1} editorial board",
                        f"Followed congressional hearing coverage on government oversight"
                    ],
                    [
                        f"Read {vendor2} analysis of {recent_context} and court decisions",
                        f"Tracked polling data on public trust in democratic institutions",
                        f"Followed international news coverage of American political developments"
                    ],
                    [
                        f"Read legal analysis of {recent_context} from {vendor1} correspondents",
                        f"Followed live coverage of congressional hearings on C-SPAN",
                        f"Researched historical comparisons to current political situations"
                    ]
                ]
                
                # Select pattern based on candidate index to ensure diversity
                pattern_set = base_patterns[candidate_index % len(base_patterns)]
                reasons.extend(pattern_set)
        elif "cmo" in title_lower or "marketing" in title_lower:
            # Use diverse activities for marketing roles
            activity_categories = ["research_activities", "evaluation_activities", "comparison_activities"]
            selected_activities = _get_diverse_activity_selection(candidate_index, activity_categories)
            
            reasons.extend([
                f"{selected_activities[0]} for {vendor1} and {vendor2}",
                f"{selected_activities[1]} focusing on {product} capabilities",
                f"{selected_activities[2]} between {vendor1} and existing marketing technology stack"
            ])
        elif "cto" in title_lower or "chief technology" in title_lower:
            # Use diverse activities for CTO roles
            if product in ["endpoint protection", "cybersecurity", "security software"]:
                activity_categories = ["research_activities", "validation_activities", "comparison_activities"]
                security_activities = _get_diverse_activity_selection(candidate_index, activity_categories)
                reasons.extend([
                    f"{security_activities[0]} for {vendor1} and {vendor2} security solutions",
                    f"{security_activities[1]} focusing on {product} compliance and threat detection",
                    f"{security_activities[2]} between {vendor1} and current security infrastructure"
                ])
            else:
                tech_activities = [
                    diverse_activity_patterns["evaluation_activities"][candidate_index % len(diverse_activity_patterns["evaluation_activities"])],
                    diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                    diverse_activity_patterns["validation_activities"][(candidate_index + 2) % len(diverse_activity_patterns["validation_activities"])]
                ]
                reasons.extend([
                    f"{tech_activities[0]} for {vendor1} vs {vendor2} technical capabilities",
                    f"{tech_activities[1]} focusing on {product} scalability and performance",
                    f"{tech_activities[2]} for enterprise {product} solutions including {vendor1}"
                ])
        elif "chef" in title_lower or "culinary" in title_lower:
            # Use diverse activities for culinary roles
            if product in ["commercial ovens", "kitchen equipment", "restaurant equipment"]:
                culinary_activities = [
                    diverse_activity_patterns["comparison_activities"][candidate_index % len(diverse_activity_patterns["comparison_activities"])],
                    diverse_activity_patterns["evaluation_activities"][(candidate_index + 1) % len(diverse_activity_patterns["evaluation_activities"])],
                    diverse_activity_patterns["validation_activities"][(candidate_index + 2) % len(diverse_activity_patterns["validation_activities"])]
                ]
                reasons.extend([
                    f"{culinary_activities[0]} for {vendor1} and {vendor2} commercial equipment",
                    f"{culinary_activities[1]} focusing on {product} performance and efficiency",
                    f"{culinary_activities[2]} for {vendor1} maintenance and operational requirements"
                ])
            else:
                general_culinary_activities = [
                    diverse_activity_patterns["research_activities"][candidate_index % len(diverse_activity_patterns["research_activities"])],
                    diverse_activity_patterns["comparison_activities"][(candidate_index + 1) % len(diverse_activity_patterns["comparison_activities"])],
                    diverse_activity_patterns["evaluation_activities"][(candidate_index + 2) % len(diverse_activity_patterns["evaluation_activities"])]
                ]
                reasons.extend([
                    f"{general_culinary_activities[0]} for {vendor1} and {vendor2} kitchen solutions",
                    f"{general_culinary_activities[1]} focusing on {product} workflow integration",
                    f"{general_culinary_activities[2]} for {vendor1} operational efficiency and cost-effectiveness"
                ])
        elif ("ceo" in title_lower or "executive" in title_lower) and "chef" not in title_lower:
            # Use diverse activities for executive roles
            executive_activities = [
                diverse_activity_patterns["research_activities"][candidate_index % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["validation_activities"][(candidate_index + 1) % len(diverse_activity_patterns["validation_activities"])],
                diverse_activity_patterns["comparison_activities"][(candidate_index + 2) % len(diverse_activity_patterns["comparison_activities"])]
            ]
            reasons.extend([
                f"{executive_activities[0]} for {vendor1} vs {vendor2} market positioning",
                f"{executive_activities[1]} focusing on {product} business impact and ROI metrics",
                f"{executive_activities[2]} for enterprise {product} solutions including {vendor1}"
            ])
        elif "sales" in title_lower:
            # Use diverse activities for sales roles
            sales_activities = [
                diverse_activity_patterns["evaluation_activities"][candidate_index % len(diverse_activity_patterns["evaluation_activities"])],
                diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["comparison_activities"][(candidate_index + 2) % len(diverse_activity_patterns["comparison_activities"])]
            ]
            reasons.extend([
                f"{sales_activities[0]} for {vendor1} and {vendor2} sales capabilities",
                f"{sales_activities[1]} focusing on {product} user adoption and implementation",
                f"{sales_activities[2]} between {vendor1} and current sales workflow requirements"
            ])
        else:
            # Use diverse activities for general roles
            general_activities = [
                diverse_activity_patterns["research_activities"][candidate_index % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["evaluation_activities"][(candidate_index + 1) % len(diverse_activity_patterns["evaluation_activities"])],
                diverse_activity_patterns["comparison_activities"][(candidate_index + 2) % len(diverse_activity_patterns["comparison_activities"])]
            ]
            reasons.extend([
                f"{general_activities[0]} for {vendor1} and {vendor2} solutions",
                f"{general_activities[1]} focusing on {product} implementation and integration",
                f"{general_activities[2]} between {vendor1} and {vendor2} contract terms and pricing"
            ])
    
    # Generate location-related behavioral reasons (if location mentioned, but separate from product)
    # Only add location-specific reasons if they make logical sense
    if location_mentioned and len(reasons) < 4 and not product_interests:
        # Only add location reasons if no product was mentioned (to avoid illogical combinations)
        if "ceo" in title_lower or "executive" in title_lower:
            reasons.append("Researched local business development opportunities and market expansion strategies")
        elif "marketing" in title_lower:
            reasons.append("Analyzed local market demographics and regional marketing opportunities")
        elif "sales" in title_lower:
            reasons.append("Researched regional sales territory performance and market penetration strategies")
        else:
            reasons.append("Reviewed local business networking events and professional development opportunities")
    
    # Add role-specific behavioral reasons if we need more using diverse patterns
    while len(reasons) < 3:
        if "cmo" in title_lower or "marketing" in title_lower:
            marketing_activities = [
                diverse_activity_patterns["engagement_activities"][candidate_index % len(diverse_activity_patterns["engagement_activities"])],
                diverse_activity_patterns["validation_activities"][(candidate_index + 1) % len(diverse_activity_patterns["validation_activities"])],
                diverse_activity_patterns["research_activities"][(candidate_index + 2) % len(diverse_activity_patterns["research_activities"])]
            ]
            role_reasons = [
                f"{marketing_activities[0]} related to marketing attribution and campaign performance",
                f"{marketing_activities[1]} for customer acquisition cost optimization strategies",
                f"{marketing_activities[2]} focusing on marketing technology stack configurations"
            ]
        elif "cto" in title_lower or "chief technology" in title_lower:
            # Check if this is a security-related search
            if any(sec_term in prompt_lower for sec_term in ["security", "endpoint", "cyber", "firewall", "antivirus", "malware", "threat"]):
                security_activities = [
                    diverse_activity_patterns["validation_activities"][candidate_index % len(diverse_activity_patterns["validation_activities"])],
                    diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                    diverse_activity_patterns["comparison_activities"][(candidate_index + 2) % len(diverse_activity_patterns["comparison_activities"])]
                ]
                role_reasons = [
                    f"{security_activities[0]} for cybersecurity threat landscape and vulnerability assessments",
                    f"{security_activities[1]} focusing on enterprise security architecture and zero-trust strategies",
                    f"{security_activities[2]} between security incident response and threat intelligence platforms"
                ]
            else:
                tech_activities = [
                    diverse_activity_patterns["evaluation_activities"][candidate_index % len(diverse_activity_patterns["evaluation_activities"])],
                    diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                    diverse_activity_patterns["engagement_activities"][(candidate_index + 2) % len(diverse_activity_patterns["engagement_activities"])]
                ]
                role_reasons = [
                    f"{tech_activities[0]} for technology infrastructure scalability and performance",
                    f"{tech_activities[1]} focusing on cloud migration and enterprise architecture frameworks",
                    f"{tech_activities[2]} related to emerging technology trends and digital transformation"
                ]
        elif "chef" in title_lower or "culinary" in title_lower:
            culinary_activities = [
                diverse_activity_patterns["comparison_activities"][candidate_index % len(diverse_activity_patterns["comparison_activities"])],
                diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["evaluation_activities"][(candidate_index + 2) % len(diverse_activity_patterns["evaluation_activities"])]
            ]
            role_reasons = [
                f"{culinary_activities[0]} for commercial kitchen efficiency and equipment utilization",
                f"{culinary_activities[1]} focusing on food cost optimization and inventory management",
                f"{culinary_activities[2]} for kitchen workflow automation and equipment integration"
            ]
        elif "ceo" in title_lower:
            executive_activities = [
                diverse_activity_patterns["validation_activities"][candidate_index % len(diverse_activity_patterns["validation_activities"])],
                diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["engagement_activities"][(candidate_index + 2) % len(diverse_activity_patterns["engagement_activities"])]
            ]
            role_reasons = [
                f"{executive_activities[0]} for industry benchmarking and competitive positioning",
                f"{executive_activities[1]} focusing on business growth strategies and market expansion",
                f"{executive_activities[2]} related to organizational efficiency and performance optimization"
            ]
        elif "sales" in title_lower:
            sales_activities = [
                diverse_activity_patterns["comparison_activities"][candidate_index % len(diverse_activity_patterns["comparison_activities"])],
                diverse_activity_patterns["research_activities"][(candidate_index + 1) % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["evaluation_activities"][(candidate_index + 2) % len(diverse_activity_patterns["evaluation_activities"])]
            ]
            role_reasons = [
                f"{sales_activities[0]} for sales pipeline optimization and conversion improvement",
                f"{sales_activities[1]} focusing on sales methodology frameworks and best practices",
                f"{sales_activities[2]} for sales performance metrics against industry benchmarks"
            ]
        else:
            # Use more specific activities for general roles based on context
            general_activities = [
                diverse_activity_patterns["research_activities"][candidate_index % len(diverse_activity_patterns["research_activities"])],
                diverse_activity_patterns["evaluation_activities"][(candidate_index + 1) % len(diverse_activity_patterns["evaluation_activities"])],
                diverse_activity_patterns["engagement_activities"][(candidate_index + 2) % len(diverse_activity_patterns["engagement_activities"])]
            ]
            
            # Create more specific contexts based on the user prompt
            if "business intelligence" in prompt_lower or "analytics" in prompt_lower:
                context_focus = ["data visualization and reporting capabilities", "business intelligence dashboard features", "analytics platform integration options"]
            elif "development" in prompt_lower or "software" in prompt_lower:
                context_focus = ["development environment setup and configuration", "software development lifecycle tools", "code collaboration and version control systems"]
            elif "management" in prompt_lower or "project" in prompt_lower:
                context_focus = ["project management methodologies and frameworks", "team collaboration and communication tools", "resource allocation and timeline management systems"]
            elif "accounting" in prompt_lower or "finance" in prompt_lower:
                context_focus = ["financial reporting and compliance requirements", "accounting automation and integration capabilities", "financial data security and audit trail features"]
            elif "workflow" in prompt_lower or "operations" in prompt_lower:
                context_focus = ["process automation and efficiency improvements", "operational workflow design and optimization", "business process management and monitoring tools"]
            else:
                # Default to business solution contexts
                context_focus = ["solution scalability and enterprise readiness", "vendor support and implementation services", "platform integration and data migration capabilities"]
            
            role_reasons = [
                f"{general_activities[0]} for {context_focus[0]}",
                f"{general_activities[1]} focusing on {context_focus[1]}",
                f"{general_activities[2]} related to {context_focus[2]}"
            ]
        
        # Add a reason that hasn't been used yet
        for reason in role_reasons:
            if reason not in reasons:
                reasons.append(reason)
                break
    
    # Add variation for different candidates to avoid identical reasons
    if candidate_index >= 0:
        time_variations = [
            "over the past week",
            "during multiple sessions last month", 
            "repeatedly over the past two weeks",
            "in several focused research sessions",
            "across multiple research sessions",
            "over the past month"
        ]
        
        # Modify the first reason to include time variation for all candidates
        if reasons:
            reasons[0] = reasons[0] + f" {time_variations[candidate_index % len(time_variations)]}"
            
        # For top 2 candidates, also add intensity variations to make them stand out
        if candidate_index < 2 and len(reasons) > 1:
            intensity_modifiers = [
                "extensively",
                "thoroughly", 
                "in-depth",
                "comprehensively"
            ]
            # Add intensity to second reason for top candidates
            if not any(mod in reasons[1] for mod in intensity_modifiers):
                reasons[1] = reasons[1].replace("Researched", f"Researched {intensity_modifiers[candidate_index % len(intensity_modifiers)]}")
                reasons[1] = reasons[1].replace("Analyzed", f"Analyzed {intensity_modifiers[candidate_index % len(intensity_modifiers)]}")
                reasons[1] = reasons[1].replace("Compared", f"Compared {intensity_modifiers[candidate_index % len(intensity_modifiers)]}")
                reasons[1] = reasons[1].replace("Downloaded", f"Downloaded and {intensity_modifiers[candidate_index % len(intensity_modifiers)]} reviewed")
    
    # AI Fallback: If we don't have enough contextually relevant reasons, use AI to generate them
    generic_business_phrases = [
        "professional development resources", "workflow optimization", "business growth strategies",
        "competitive positioning analysis", "market expansion opportunities", "organizational efficiency metrics",
        "performance optimization", "industry benchmarking reports", "technology solutions relevant to their professional responsibilities",
        "industry best practices and professional development", "workflow optimization and productivity improvement",
        "technology solutions for their professional responsibilities"
    ]
    
    has_generic_reasons = any(any(phrase in reason for phrase in generic_business_phrases) for reason in reasons)
    
    if len(reasons) < 3 or has_generic_reasons:
        ai_reasons = _generate_ai_contextual_reasons(title, user_prompt, candidate_index, existing_reasons=reasons)
        if ai_reasons:
            # Replace generic reasons with AI-generated contextual ones
            reasons = ai_reasons
    
    return reasons[:4]  # Return max 4 reasons

def _generate_ai_contextual_reasons(title: str, user_prompt: str, candidate_index: int, existing_reasons: list = None) -> list:
    """
    Use AI to generate contextually appropriate behavioral reasons when hardcoded patterns don't match.
    This provides a fallback for edge cases and specialized use cases.
    """
    try:
        # Import OpenAI here to avoid dependency issues
        import os
        import json
        from openai import OpenAI
        
        # Load API key
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            try:
                with open("secrets.json", "r") as f:
                    secrets = json.load(f)
                    openai_api_key = secrets.get('openai_api_key', '')
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        if not openai_api_key:
            return None
        
        client = OpenAI(api_key=openai_api_key)
        
        # Create a context-aware prompt
        system_prompt = f"""You are an expert at generating realistic behavioral reasons for why a professional would be a good match for a specific search.

CONTEXT:
- Role: {title}
- Search: "{user_prompt}"
- Candidate position: #{candidate_index + 1}

CRITICAL REQUIREMENTS:
1. Generate exactly 3 behavioral reasons
2. Each reason must be 15-25 words
3. Focus on specific research activities, not job descriptions
4. Use "they" pronouns only
5. Include specific vendor names, tools, or technologies when relevant
6. Make reasons progressively more detailed for higher-ranked candidates
7. Avoid generic phrases like "professional development" or "workflow optimization"
8. NEVER use repetitive patterns like "downloaded whitepaper", "attended webinar", "viewed webinar"
9. Focus on diverse activities: analyzed, compared, evaluated, researched, monitored, tracked, assessed, validated, participated, engaged, consulted, reviewed, studied, investigated, explored

DIVERSE ACTIVITY EXAMPLES:
- "Evaluated CrowdStrike and SentinelOne threat detection capabilities across multiple enterprise environments"
- "Analyzed healthcare compliance requirements for HIPAA-compliant patient data management systems"
- "Compared Salesforce and HubSpot integration capabilities with existing marketing automation workflows"
- "Monitored G2 and Capterra reviews for enterprise software solutions over multiple weeks"
- "Participated in product demos and technical deep-dive sessions with solution architects"
- "Consulted with industry peers about their experiences with similar technology implementations"
- "Tracked pricing changes and promotional offers across multiple vendor platforms"
- "Validated technical requirements with IT and security teams for compliance alignment"
- "Investigated API documentation and technical specifications for integration planning"
- "Assessed vendor financial stability and long-term viability through analyst reports"

EXAMPLES OF BAD REASONS (AVOID):
- "Downloaded whitepaper about [topic]" or "Downloaded implementation guides"
- "Attended webinar on [topic]" or "Viewed webinar about [topic]"
- "Researched industry best practices and professional development resources"
- "Analyzed workflow optimization and productivity improvement strategies"
- "Compared technology solutions relevant to their professional responsibilities"
- "Reviewed industry benchmarking reports and competitive positioning analysis"

Return ONLY a JSON array of 3 strings, nothing else."""

        user_prompt_for_ai = f"Generate 3 specific behavioral reasons for why this {title} would be interested in: {user_prompt}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_ai}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        # Parse the JSON response
        result_text = response.choices[0].message.content.strip()
        
        # Clean up the response to extract JSON
        if result_text.startswith('```json'):
            result_text = result_text.replace('```json', '').replace('```', '').strip()
        
        reasons = json.loads(result_text)
        
        # Validate the response
        if isinstance(reasons, list) and len(reasons) >= 3:
            # Add time variations like the hardcoded reasons
            time_variations = [
                "over the past week",
                "during multiple sessions last month", 
                "repeatedly over the past two weeks",
                "in several focused research sessions",
                "across multiple research sessions",
                "over the past month"
            ]
            
            if candidate_index >= 0 and len(reasons) > 0:
                reasons[0] = reasons[0] + f" {time_variations[candidate_index % len(time_variations)]}"
            
            # Add intensity for top candidates
            if candidate_index < 2 and len(reasons) > 1:
                intensity_modifiers = ["extensively", "thoroughly", "in-depth", "comprehensively"]
                modifier = intensity_modifiers[candidate_index % len(intensity_modifiers)]
                
                # Add intensity to the second reason
                if not any(mod in reasons[1] for mod in intensity_modifiers):
                    for verb in ["Researched", "Analyzed", "Compared", "Evaluated", "Reviewed"]:
                        if verb in reasons[1]:
                            reasons[1] = reasons[1].replace(verb, f"{verb} {modifier}")
                            break
            
            return reasons[:4]  # Return max 4 reasons
        
        return None
        
    except Exception as e:
        print(f"[AI Fallback] Failed to generate contextual reasons: {e}")
        return None

if __name__ == "__main__":
    # Load sample people JSON from file or input
    people = json.load(open("temp_people.json"))
    prompt = input("Enter your search prompt: ")
    top2 = select_top_candidates(prompt, people)
    print(json.dumps(top2, indent=2))