# type: ignore
import os
import json
import random

# Load API keys from environment variables or secrets.json with graceful error handling
_secrets = {}
try:
    # First try environment variables (for Render deployment)
    APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
    BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Fallback to secrets.json for local development
    if not OPENAI_API_KEY:
        with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
            content = f.read()
        decoder = json.JSONDecoder()
        _secrets, _ = decoder.raw_decode(content)
        APOLLO_API_KEY = APOLLO_API_KEY or _secrets.get("apollo_api_key")
        BRIGHT_DATA_API_KEY = BRIGHT_DATA_API_KEY or _secrets.get("bright_data_api_key")
        OPENAI_API_KEY = OPENAI_API_KEY or _secrets.get("openai_key")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"⚠️  Warning: Could not load secrets.json: {e}")
    print("   Using environment variables or create secrets.json with your API keys.")
    APOLLO_API_KEY = APOLLO_API_KEY or _secrets.get("apollo_api_key")
    BRIGHT_DATA_API_KEY = BRIGHT_DATA_API_KEY or _secrets.get("bright_data_api_key")
    OPENAI_API_KEY = OPENAI_API_KEY or _secrets.get("openai_key")

import openai

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    print("⚠️  Warning: OpenAI API key not found. Some features may be limited.")

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

def parse_prompt_to_apollo_filters(prompt: str) -> dict:
    """
    Parses a natural-language prompt into Apollo API filters for organizations and people.
    This is an interim solution using AI to simulate behavioral data until the actual dataset is migrated.

    Returns a dictionary with the following structure:
    {
        "organization_filters": { ... },  # filters for Apollo mixed_companies/search
        "person_filters": { ... },        # filters for Apollo mixed_people/search
        "reasoning": "..."                 # a concise explanation of the filter choices
    }

    Each filter object should be a dict ready to be passed to the respective Apollo endpoint.
    The reasoning is a string explaining the rationale behind the chosen filters.
    """
    # Check for ridiculous prompts first
    if is_ridiculous_prompt(prompt):
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": get_witty_error_response()
        }
    
    system_message = {
        "role": "system",
        "content": (
            "You are an expert at converting user prompts into Apollo People Search API filter payloads. "
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
            "Return only valid JSON with keys: organization_filters, person_filters, and reasoning."
        )
    }
    
    user_message = {
        "role": "user",
        "content": prompt
    }

    if not OPENAI_API_KEY:
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": "OpenAI API key not available. Cannot process prompt."
        }
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
            temperature=0,
            max_tokens=500,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned empty response")
        filters = json.loads(content.strip())
        
        # Validate keys exist and are correct types
        if not isinstance(filters, dict):
            raise ValueError("Response JSON is not a dictionary")
        if "organization_filters" not in filters or "person_filters" not in filters or "reasoning" not in filters:
            raise ValueError("Response JSON missing required keys")
        
        # Ensure filters are dictionaries, create empty ones if not
        if not isinstance(filters["organization_filters"], dict):
            filters["organization_filters"] = {}
        if not isinstance(filters["person_filters"], dict):
            filters["person_filters"] = {}
        if not isinstance(filters["reasoning"], str):
            filters["reasoning"] = "Generated filters based on prompt analysis"

        # Post-processing to enforce correct types per Apollo People Search API
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
        
    except (Exception, json.JSONDecodeError, ValueError) as e:
        # Return empty filters and empty reasoning on error
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": f"Error processing prompt: {str(e)}"
        }

def simulate_behavioral_data(filters: dict) -> dict:
    """
    Simulates behavioral data based on the generated filters.
    This is an interim solution until the actual behavioral dataset is migrated.
    
    Args:
        filters: The Apollo API filters generated from the prompt
        
    Returns:
        dict: Simulated behavioral data with relevant insights
    """
    try:
        # Use AI to generate realistic behavioral insights based on the filters
        system_message = {
            "role": "system",
            "content": (
                "You are an expert at analyzing B2B behavioral data. Based on the given Apollo API filters, "
                "generate realistic behavioral insights that would be typical for companies and people matching these criteria. "
                "Focus on engagement patterns, technology adoption trends, decision-making behaviors, and market dynamics. "
                "Return a JSON object with behavioral insights and supporting data points."
            )
        }
        
        user_message = {
            "role": "user",
            "content": f"Generate behavioral insights for these filters: {json.dumps(filters, indent=2)}"
        }
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
            temperature=0.3,
            max_tokens=800,
        )
        
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("OpenAI returned empty response")
        behavioral_data = json.loads(content.strip())
        
        return behavioral_data
        
    except Exception as e:
        return {
            "error": f"Failed to simulate behavioral data: {str(e)}",
            "insights": [],
            "data_points": []
        }

if __name__ == "__main__":
    example_prompt = (
        "Find companies in the software and technology industries located in San Francisco or New York, "
        "and people who are CEOs or Founders with C-Level seniority."
    )
    
    # Generate filters
    filters = parse_prompt_to_apollo_filters(example_prompt)
    print("Generated Filters:")
    print(json.dumps(filters, indent=2))
    
    # Simulate behavioral data
    behavioral_data = simulate_behavioral_data(filters)
    print("\nSimulated Behavioral Data:")
    print(json.dumps(behavioral_data, indent=2))
