# type: ignore
import os
import json
import random
from openai_utils import call_openai_for_json, call_openai

# Load API keys from environment variables or secrets.json with graceful error handling
_secrets = {}
try:
    # First try environment variables (for Render deployment)
    INTERNAL_DATABASE_API_KEY = os.getenv("INTERNAL_DATABASE_API_KEY")
    SCRAPING_DOG_API_KEY = os.getenv("SCRAPING_DOG_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Fallback to secrets.json for local development
    if not OPENAI_API_KEY:
        with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
            content = f.read()
        decoder = json.JSONDecoder()
        _secrets, _ = decoder.raw_decode(content)
        INTERNAL_DATABASE_API_KEY = INTERNAL_DATABASE_API_KEY or _secrets.get("internal_database_api_key")
        SCRAPING_DOG_API_KEY = SCRAPING_DOG_API_KEY or _secrets.get("scraping_dog_api_key")
        OPENAI_API_KEY = OPENAI_API_KEY or _secrets.get("openai_key")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"⚠️  Warning: Could not load secrets.json: {e}")
    print("   Using environment variables or create secrets.json with your API keys.")
    INTERNAL_DATABASE_API_KEY = INTERNAL_DATABASE_API_KEY or _secrets.get("internal_database_api_key")
    SCRAPING_DOG_API_KEY = SCRAPING_DOG_API_KEY or _secrets.get("scraping_dog_api_key")
    OPENAI_API_KEY = OPENAI_API_KEY or _secrets.get("openai_key")

def get_witty_error_response() -> str:
    """
    Returns a random witty response for ridiculous prompts
    """
    witty_responses = [
        "🤖 I'm not sure a barista needs enterprise cybersecurity... unless they're serving coffee to hackers? ☕️",
        "🎭 That's like asking a goldfish to pilot a spaceship. Creative, but probably not practical! 🚀",
        "🍕 A pizza delivery driver looking for quantum computing solutions? Now I've heard everything! 🧮",
        "🎪 This prompt is so wild, it belongs in a circus! 🎪",
        "🌈 You're thinking outside the box so much, you're in a different dimension! 🌌",
        "🎨 This is the kind of creativity that makes me question reality itself! ✨",
        "🎪 That's like asking a penguin to teach surfing lessons! 🏄‍♂️",
        "🎭 This prompt is so unexpected, it deserves its own reality show! 📺",
        "🎪 You've officially broken my logic circuits with that one! 🤯",
        "🌈 That's like asking a librarian to perform brain surgery! 🧠",
        "🎨 This is the kind of request that makes me wonder if you're testing my sanity! 😵‍💫",
        "🎪 That's like asking a butterfly to build a skyscraper! 🦋🏗️"
    ]
    return random.choice(witty_responses)

def is_ridiculous_prompt(prompt: str) -> bool:
    """
    Check if a prompt is ridiculous by looking for mismatched roles and industries
    """
    ridiculous_patterns = [
        # Mismatched roles and industries
        ("barista", "enterprise"),
        ("barista", "cybersecurity"),
        ("cashier", "quantum"),
        ("janitor", "blockchain"),
        ("waiter", "artificial intelligence"),
        ("receptionist", "machine learning"),
        ("delivery driver", "enterprise software"),
        ("retail associate", "cloud computing"),
        ("fast food worker", "data science"),
        ("housekeeper", "cybersecurity"),
        # Obvious mismatches
        ("pizza delivery", "enterprise"),
        ("pizza delivery", "quantum"),
        ("pizza delivery", "cybersecurity"),
        ("coffee shop", "quantum"),
        ("restaurant", "blockchain"),
        ("grocery store", "ai"),
        ("gas station", "machine learning"),
        # Delivery-related mismatches
        ("delivery", "quantum"),
        ("delivery", "enterprise"),
        ("delivery", "cybersecurity"),
        ("driver", "quantum"),
        ("driver", "enterprise"),
        ("driver", "cybersecurity")
    ]
    
    prompt_lower = prompt.lower()
    for role, industry in ridiculous_patterns:
        if role in prompt_lower and industry in prompt_lower:
            return True
    
    return False

def parse_prompt_to_internal_database_filters(prompt: str) -> dict:
    """
    Parses a natural-language prompt into our internal database API filters for organizations and people.
    This is an interim solution using AI to simulate behavioral data until the actual dataset is migrated.

    Returns a dictionary with the following structure:
    {
        "organization_filters": { ... },  # filters for our internal database mixed_companies/search
        "person_filters": { ... },        # filters for our internal database mixed_people/search
        "reasoning": "..."                 # a concise explanation of the filter choices
    }

    Each filter object should be a dict ready to be passed to the respective internal database endpoint.
    The reasoning is a string explaining the rationale behind the chosen filters.
    """
    # Check for ridiculous prompts first
    if is_ridiculous_prompt(prompt):
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": get_witty_error_response()
        }
    


    # Use the new OpenAI utility function
    system_prompt = (
        "You are an expert at converting user prompts into our internal database People Search API filter payloads. "
        "Think step-by-step to infer any necessary organization filters, then person filters. "
        "IMPORTANT: Keep filters SIMPLE and RELIABLE to avoid API errors. "
        "Only use these exact People Search parameters:\n\n"
        "Organization filters (arrays or integers):\n"
        "- organization_locations[] (e.g. [\"New York\", \"San Francisco\"])\n"
        "- q_organization_keyword_tags[] (e.g. [\"Software\", \"Technology\"])\n"
        "- organization_num_employees_ranges[] (e.g. [\"1,10\", \"11,50\"])\n\n"
        "Person filters:\n"
        "- person_titles[] (e.g. [\"CEO\", \"CTO\", \"Sales Director\"])\n"
        "- person_locations[] (e.g. [\"New York\", \"San Francisco\"])\n"
        "- person_seniorities[] (e.g. [\"c_suite\", \"vp\", \"director\"])\n"
        "- include_similar_titles (boolean, default: true)\n\n"
        "RULES:\n"
        "1. Use ONLY the parameter names listed above\n"
        "2. Keep filters simple - avoid complex combinations\n"
        "3. Use arrays for multiple values\n"
        "4. Don't use revenue_range, technology_uids, or other complex filters\n"
        "5. Focus on basic location, title, and seniority filters\n"
        "6. Return ONLY valid JSON, inside a single markdown code block (triple backticks, json). No extra text, no explanation, no comments.\n"
        "7. The JSON must have keys: organization_filters, person_filters, reasoning."
    )
    
    filters = call_openai_for_json(
        prompt=prompt,
        system_message=system_prompt,
        model="gpt-3.5-turbo",
        temperature=0,
        max_tokens=500,
        expected_keys=["organization_filters", "person_filters", "reasoning"]
    )
    
    if not filters:
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": "OpenAI API key not available or request failed. Cannot process prompt."
        }
        
    # Validate keys exist and are correct types
    if not isinstance(filters, dict):
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": "Response JSON is not a dictionary"
        }
    if "organization_filters" not in filters or "person_filters" not in filters or "reasoning" not in filters:
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": "Response JSON missing required keys"
        }
    
    # Ensure filters are dictionaries, create empty ones if not
    if not isinstance(filters["organization_filters"], dict):
        filters["organization_filters"] = {}
    if not isinstance(filters["person_filters"], dict):
        filters["person_filters"] = {}
    if not isinstance(filters["reasoning"], str):
        filters["reasoning"] = "Generated filters based on prompt analysis"

    # Post-processing to enforce correct types per our internal database People Search API
    org_list_keys = [
        "organization_locations",
        "q_organization_keyword_tags",
        "organization_num_employees_ranges"
    ]
    person_list_keys = [
        "person_titles",
        "person_locations",
        "person_seniorities"
    ]

    for key in org_list_keys:
        if key in filters["organization_filters"]:
            if not isinstance(filters["organization_filters"][key], list):
                filters["organization_filters"][key] = [filters["organization_filters"][key]]

    for key in person_list_keys:
        if key in filters["person_filters"]:
            if not isinstance(filters["person_filters"][key], list):
                filters["person_filters"][key] = [filters["person_filters"][key]]

    if "include_similar_titles" not in filters["person_filters"]:
        filters["person_filters"]["include_similar_titles"] = True

    return filters

def simulate_behavioral_data(filters: dict) -> dict:
    """
    Simulates behavioral data based on the generated filters.
    This is an interim solution until the actual behavioral dataset is migrated.
    
    Args:
        filters: The our internal database API filters generated from the prompt
        
    Returns:
        dict: Simulated behavioral data with relevant insights
    """
    system_prompt = (
        "You are an expert at analyzing B2B behavioral data. Based on the given Apollo API filters, "
        "generate realistic behavioral insights that would be typical for companies and people matching these criteria. "
        "Focus on engagement patterns, technology adoption trends, decision-making behaviors, and market dynamics. "
        "Return a JSON object with behavioral insights and supporting data points."
    )
    
    prompt = f"Generate behavioral insights for these our internal database filters: {json.dumps(filters, indent=2)}"
    
    behavioral_data = call_openai_for_json(
        prompt=prompt,
        system_message=system_prompt,
        model="gpt-3.5-turbo",
        temperature=0.3,
        max_tokens=800
    )
    
    if not behavioral_data:
        return {
            "error": "Failed to simulate behavioral data",
            "insights": [],
            "data_points": []
        }
    
    return behavioral_data

if __name__ == "__main__":
    example_prompt = (
        "Find companies in the software and technology industries located in San Francisco or New York, "
        "and people who are CEOs or Founders with C-Level seniority."
    )
    
    # Generate filters
    filters = parse_prompt_to_internal_database_filters(example_prompt)
    print("Generated Filters:")
    print(json.dumps(filters, indent=2))
    
    # Simulate behavioral data
    behavioral_data = simulate_behavioral_data(filters)
    print("\nSimulated Behavioral Data:")
    print(json.dumps(behavioral_data, indent=2))
