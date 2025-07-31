"""
Creepy Search Detector

This module detects when users are searching for specific individuals by name
and returns witty responses to discourage stalking behavior.
"""

import os
import json
import random
import re
from typing import Dict, Any, Optional
from openai import OpenAI

# Load API keys from secrets.json if not in environment
if not os.getenv('OPENAI_API_KEY'):
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            # Handle both uppercase and lowercase key names for compatibility
            os.environ['OPENAI_API_KEY'] = secrets.get('openai_api_key', '') or secrets.get('OPENAI_API_KEY', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

# Set up OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def detect_specific_person_search(prompt: str, user_first_name: str = None) -> Dict[str, Any]:
    """
    Detect if someone is searching using ANY person names (first names, last names, or combinations).
    Block ALL searches that contain potential person names, regardless of context.
    
    Args:
        prompt: The search prompt to analyze
        user_first_name: Optional first name of the user making the request
        
    Returns:
        Dictionary with detection results and witty response if needed
    """
    
    # Check for full names (First Last pattern)
    full_name_pattern = r'(?<!^)(?<!\. )\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    full_names = re.findall(full_name_pattern, prompt)
    
    # Also check for names at the beginning of sentences
    start_name_pattern = r'^[A-Z][a-z]+\s+[A-Z][a-z]+\b'
    start_full_names = re.findall(start_name_pattern, prompt)
    
    # Check for single names that could be first names or last names
    # Look for patterns like "named John", "called Mary", "get me Sarah", "find David", etc.
    single_name_patterns = [
        r'\bnamed\s+([A-Z][a-z]{2,})\b',  # "named John"
        r'\bcalled\s+([A-Z][a-z]{2,})\b',  # "called Mary"
        r'\bget\s+me\s+([A-Z][a-z]{2,})\b',  # "get me Sarah"
        r'\bfind\s+me\s+([A-Z][a-z]{2,})\b',  # "find me David"
        r'\bshow\s+me\s+([A-Z][a-z]{2,})\b',  # "show me Lisa"
        r'\bgive\s+me\s+([A-Z][a-z]{2,})\b',  # "give me Michael"
        r'\bfind\s+([A-Z][a-z]{2,})\s+from\b',  # "find Sarah from"
        r'\bget\s+([A-Z][a-z]{2,})\s+from\b',  # "get David from"
        r'\bshow\s+([A-Z][a-z]{2,})\s+from\b',  # "show Lisa from"
        r'\blooking\s+for\s+([A-Z][a-z]{2,})\s+(?:from|at|in)\b',  # "looking for John from/at/in"
        r'\bsearch\s+for\s+([A-Z][a-z]{2,})\s+(?:from|at|in)\b',  # "search for Mary from/at/in"
        r'\bwant\s+([A-Z][a-z]{2,})\s+(?:from|at|in)\b',  # "want Sarah from/at/in"
        r'\bneed\s+([A-Z][a-z]{2,})\s+(?:from|at|in)\b',  # "need David from/at/in"
    ]
    
    single_names = []
    for pattern in single_name_patterns:
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        single_names.extend(matches)
    
    # Check for specific title at specific company patterns (also creepy)
    # Like "the CEO at Apple", "the marketing director at Google", etc.
    specific_title_patterns = [
        r'\bthe\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "the CEO at Apple"
        r'\bfind\s+the\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "find the CTO at Google"
        r'\bget\s+me\s+the\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # "get me the VP at Microsoft"
    ]
    
    specific_titles = []
    for pattern in specific_title_patterns:
        matches = re.findall(pattern, prompt, re.IGNORECASE)
        for match in matches:
            # match is a tuple like ("CEO", "Apple") - we'll use the company name as the "detected name"
            if len(match) == 2:
                title, company = match
                specific_titles.append(f"the {title} at {company}")
    
    # Combine all potential names and specific title searches
    all_potential_names = full_names + start_full_names + single_names + specific_titles
    
    if not all_potential_names:
        return {"is_creepy": False, "detected_names": [], "response": None}
    
    # Filter out common non-name patterns (locations, business terms, job titles, etc.)
    common_non_names = [
        # Geographic locations
        "New York", "San Francisco", "Los Angeles", "Las Vegas", "New Jersey",
        "North Carolina", "South Carolina", "West Virginia", "East Coast", "West Coast",
        "North America", "South America", "Middle East", "United States", "United Kingdom",
        "New Zealand", "Costa Rica", "Puerto Rico", "Hong Kong", "South Korea",
        
        # Business/Professional terms
        "Real Estate", "Social Media", "Machine Learning", "Data Science", "Artificial Intelligence",
        "Chief Executive", "Vice President", "Human Resources", "Customer Service", "Business Development",
        "Project Management", "Quality Assurance", "Information Technology", "Digital Marketing",
        "Content Marketing", "Email Marketing", "Search Engine", "Customer Success", "Sales Manager",
        "Marketing Director", "Software Engineer", "Data Analyst", "Product Manager", "Account Manager",
        
        # Company/Organization types
        "Fortune Five", "Goldman Sachs", "Morgan Stanley", "Wells Fargo", "Bank America", "American Express",
        "General Electric", "Johnson Johnson", "Procter Gamble", "Coca Cola", "Home Depot", "Best Buy",
        "Credit Card", "Mutual Fund", "Private Equity", "Venture Capital", "Investment Banking",
        
        # Technology/Software terms
        "Open Source", "Cloud Computing", "Big Data", "Internet Things", "Virtual Reality",
        "Augmented Reality", "Cyber Security", "Block Chain", "Neural Network",
        
        # Common job-related words that might be capitalized
        "Manager", "Director", "Engineer", "Developer", "Analyst", "Specialist", "Coordinator",
        "Assistant", "Executive", "Officer", "Representative", "Consultant", "Administrator",
        
        # Common words that might be mistaken for names
        "Find", "Get", "Show", "Looking", "Search", "Tell", "Give", "Bring", "Send", "Take",
        "Make", "Create", "Build", "Design", "Develop", "Write", "Read", "Open", "Close",
        "Start", "Stop", "Begin", "End", "Help", "Support", "Service", "Team", "Group",
        "Company", "Business", "Organization", "Department", "Division", "Unit", "Office",
        
        # Professional terms that might be capitalized
        "Marketing", "Sales", "Finance", "Technology", "Engineering", "Operations", "Legal",
        "Professionals", "Executives", "Leaders", "Managers", "Directors", "Officers",
        "CEOs", "CTOs", "CFOs", "VPs", "Developers", "Engineers", "Analysts", "Specialists"
    ]
    
    # Filter out the common non-names (case insensitive)
    actual_names = []
    for name in all_potential_names:
        if not any(non_name.lower() == name.lower() for non_name in common_non_names):
            actual_names.append(name)
    
    if not actual_names:
        return {"is_creepy": False, "detected_names": [], "response": None}
    
    # ULTRA STRICT MODE: Block ANY search that contains what looks like a person's name
    detected_name = actual_names[0]  # Use the first detected name
    witty_response = generate_witty_creepy_response(detected_name, user_first_name)
    
    return {
        "is_creepy": True,
        "detected_names": actual_names,
        "response": witty_response,
        "reasoning": f"Blocked search containing potential person name: {detected_name}"
    }

def fallback_creepy_detection(prompt: str, potential_names: list, user_first_name: str = None) -> Dict[str, Any]:
    """
    Fallback detection when AI is not available.
    In strict mode, block ANY potential person names.
    """
    if potential_names:
        # STRICT MODE: Block any potential person names
        detected_name = potential_names[0]
        witty_response = generate_witty_creepy_response(detected_name, user_first_name)
        return {
            "is_creepy": True,
            "detected_names": potential_names,
            "response": witty_response,
            "reasoning": f"Fallback: Blocked search containing potential person name: {detected_name}"
        }
    
    return {"is_creepy": False, "detected_names": [], "response": None}

def generate_witty_creepy_response(detected_name: str, user_first_name: str = None) -> str:
    """
    Generate a witty, tongue-in-cheek response for creepy searches.
    
    Args:
        detected_name: The name/search term they're looking for
        user_first_name: Optional first name of the user making the request
        
    Returns:
        A witty response discouraging stalking behavior
    """
    
    # Use user's first name if provided, otherwise use generic terms
    user_address = user_first_name if user_first_name else "friend"
    
    # Check if this is a specific title search
    is_title_search = "the " in detected_name.lower() and " at " in detected_name.lower()
    
    # Collection of witty responses
    if is_title_search:
        # Special responses for specific title searches
        responses = [
            f"Whoa {user_address}! We know exactly who {detected_name} is, but we're not doxxing executives for you. Try searching for job categories instead! 🚫👔",
            
            f"Nice try {user_address}! We've got {detected_name} in our database, but we're not running a corporate stalking service. How about 'executives in tech' instead? 🏢❌",
            
            f"Plot twist {user_address}: We actually know {detected_name} personally, but that info is staying locked up! Try 'senior leadership roles' instead. 🔐👨‍💼",
            
            f"Red alert {user_address}! Our systems have {detected_name} mapped out completely, but we draw the line at corporate espionage. Search for role types! 🚨🕴️",
            
            f"Awkward {user_address}... We know {detected_name} better than their own LinkedIn, but that's classified! Try 'C-suite executives' instead. 😬📊"
        ]
    else:
        # Regular responses for name searches
        responses = [
            f"We know plenty about {detected_name}, but no {user_address}, we won't tell you that. Stop being creepy! 🕵️‍♂️",
            
            f"Oh {user_address}, we have tons of data on {detected_name}, but that would be telling! Maybe try searching for job roles instead of stalking people? 😏",
            
            f"Nice try {user_address}! We've got the goods on {detected_name}, but we're not running a stalking service here. How about searching for 'marketing directors' instead? 🚫👀",
            
            f"We see what you're doing there {user_address}... Yes, we have data on {detected_name}, but we're not your personal PI. Try searching for professional roles! 🔍❌",
            
            f"Whoa there {user_address}! Our database knows all about {detected_name}, but we draw the line at helping people be creepy. Search for job titles, not individuals! 🛑",
            
            f"Plot twist {user_address}: We actually do have intel on {detected_name}, but we're keeping that locked away! Try 'find me a sales manager' instead of specific people. 🔒",
            
            f"Hey {user_address}, we've got the 411 on {detected_name} alright, but that's classified information! How about we find you some 'software engineers' instead? 🤐",
            
            f"Nope nope nope {user_address}! We know {detected_name}'s digital footprint like the back of our hand, but we're not sharing. Try searching for roles, not people! 🙅‍♀️",
            
            f"Listen {user_address}, we could tell you everything about {detected_name}, but then we'd have to... well, not tell you anything! Search for job functions instead! 🤫",
            
            f"Oh {user_address}, you're barking up the wrong tree! We've got {detected_name}'s data, but we're not in the business of enabling stalkers. Try 'marketing professionals' instead! 🌳❌",
            
            f"Yikes {user_address}! We know {detected_name} better than they know themselves, but we're keeping that info under wraps. How about 'sales directors' instead? 🔐",
            
            f"Red alert {user_address}! Our systems are loaded with {detected_name}'s digital breadcrumbs, but we're not sharing. Try searching for actual job roles! 🚨",
            
            f"Awkward {user_address}... We've got {detected_name}'s entire online presence mapped out, but that's staying in the vault! Search for 'engineers' or something normal! 😬",
            
            f"Not today {user_address}! We have {detected_name}'s data locked and loaded, but we draw the line at being your personal stalking assistant. Try professional searches! 🔒🚫"
        ]
    
    return random.choice(responses)

def extract_user_first_name_from_context(request_context: dict = None) -> Optional[str]:
    """
    Extract user's first name from request context if available.
    This could be expanded to use authentication data, session info, etc.
    
    Args:
        request_context: Optional context containing user information
        
    Returns:
        User's first name if available, None otherwise
    """
    
    # For now, return None - this can be expanded later with actual user data
    # In the future, this could pull from:
    # - JWT tokens
    # - Session data  
    # - User profiles
    # - Request headers
    
    return None

if __name__ == "__main__":
    # Test the creepy detector
    test_prompts = [
        "Find me marketing directors in New York",  # Not creepy - no names
        "What is John Smith looking for?",  # Creepy - contains full name
        "Is Jane Doe looking for a divorce attorney?",  # Creepy - contains full name
        "Find me a John Smith who works in sales",  # Creepy - contains full name (ULTRA STRICT)
        "Tell me about Mike Johnson's interests",  # Creepy - contains full name
        "Looking for software engineers named David",  # Creepy - contains first name (ULTRA STRICT)
        "Find me CEOs in San Francisco",  # Not creepy - no names
        "Looking for Mary Johnson in marketing",  # Creepy - contains full name (ULTRA STRICT)
        "Find developers in tech companies",  # Not creepy - no names
        "Get me Sarah from the marketing team",  # Creepy - contains first name (ULTRA STRICT)
        "Show me professionals in finance",  # Not creepy - no names
        "Find the CEO at Apple",  # Creepy - specific title at specific company
        "Get me the CTO at Google",  # Creepy - specific title at specific company
        "Looking for VPs in technology",  # Not creepy - general role search
    ]
    
    for prompt in test_prompts:
        print(f"\n🔍 Testing: '{prompt}'")
        result = detect_specific_person_search(prompt, "Chris")
        if result["is_creepy"]:
            print(f"🚨 CREEPY DETECTED: {result['response']}")
        else:
            print(f"✅ Safe search - detected names: {result['detected_names']}")