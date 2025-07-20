# type: ignore
import os
import json
import random
from openai_utils import call_openai_for_json

try:
    INTERNAL_DATABASE_API_KEY = os.getenv("INTERNAL_DATABASE_API_KEY")
    SCRAPING_DOG_API_KEY = os.getenv("SCRAPING_DOG_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_API_KEY:
        with open(os.path.join(os.path.dirname(__file__), "secrets.json"), "r") as f:
            content = f.read()
        decoder = json.JSONDecoder()
        _secrets, _ = decoder.raw_decode(content)
        INTERNAL_DATABASE_API_KEY = INTERNAL_DATABASE_API_KEY or _secrets.get("internal_database_api_key")
        SCRAPING_DOG_API_KEY = SCRAPING_DOG_API_KEY or _secrets.get("scraping_dog_api_key")
        OPENAI_API_KEY = OPENAI_API_KEY or _secrets.get("openai_key")
except (FileNotFoundError, json.JSONDecodeError):
    INTERNAL_DATABASE_API_KEY = os.getenv("INTERNAL_DATABASE_API_KEY")
    SCRAPING_DOG_API_KEY = os.getenv("SCRAPING_DOG_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_witty_error_response() -> str:
    witty_responses = [
        "🤖 I'm not sure a barista needs enterprise cybersecurity... unless they're serving coffee to hackers? ☕️",
        "🎭 That's like asking a goldfish to pilot a spaceship. Creative, but probably not practical! 🚀",
        "🍕 A pizza delivery driver looking for quantum computing solutions? Now I've heard everything! 🧮",
        "🎪 This prompt is so wild, it belongs in a circus! 🎪",
        "🌈 You're thinking outside the box so much, you're in a different dimension! 🌌"
    ]
    return random.choice(witty_responses)

def is_ridiculous_prompt(prompt: str) -> bool:
    ridiculous_patterns = [
        ("barista", "enterprise"), ("barista", "cybersecurity"), ("cashier", "quantum"),
        ("janitor", "blockchain"), ("waiter", "artificial intelligence"), ("receptionist", "machine learning"),
        ("delivery driver", "enterprise software"), ("retail associate", "cloud computing"),
        ("fast food worker", "data science"), ("housekeeper", "cybersecurity"),
        ("pizza delivery", "enterprise"), ("pizza delivery", "quantum"), ("pizza delivery", "cybersecurity"),
        ("coffee shop", "quantum"), ("restaurant", "blockchain"), ("grocery store", "ai"),
        ("gas station", "machine learning"), ("delivery", "quantum"), ("delivery", "enterprise"),
        ("delivery", "cybersecurity"), ("driver", "quantum"), ("driver", "enterprise"), ("driver", "cybersecurity")
    ]
    
    prompt_lower = prompt.lower()
    for role, industry in ridiculous_patterns:
        if role in prompt_lower and industry in prompt_lower:
            return True
    return False

def parse_prompt_to_internal_database_filters(prompt: str) -> dict:
    if is_ridiculous_prompt(prompt):
        return {
            "organization_filters": {},
            "person_filters": {},
            "reasoning": get_witty_error_response()
        }

    system_prompt = (
        "You are an expert at converting user prompts into our internal database People Search API filter payloads. "
        "Think step-by-step to infer any necessary organization filters, then person filters. "
        "IMPORTANT: Keep filters SIMPLE and RELIABLE to avoid API errors. "
        "Only use these exact People Search parameters:\n\n"
        "Organization filters (arrays or integers):\n"
        "- organization_locations[] (e.g. [\"New York\", \"San Francisco\"])\n"
        "- organization_num_employees_ranges[] (e.g. [\"1,10\", \"11,50\", \"51,200\", \"201,1000\", \"1001,5000\", \"5001,10000\", \"10001+\"])\n"
        "- q_organization_keyword_tags[] (e.g. [\"automotive\", \"technology\", \"healthcare\"]) - USE SPARINGLY, only for clear industry terms\n\n"
        "Person filters:\n"
        "- person_titles[] (e.g. [\"CEO\", \"CTO\", \"Sales Director\", \"Marketing Manager\"])\n"
        "- person_locations[] (e.g. [\"New York\", \"San Francisco\"])\n"
        "- person_seniorities[] (e.g. [\"c_suite\", \"vp\", \"director\", \"manager\", \"senior\"])\n"
        "- include_similar_titles (boolean, default: true)\n\n"
        "CRITICAL RULES:\n"
        "1. Use ONLY the parameter names listed above\n"
        "2. Keep filters simple - avoid complex combinations\n"
        "3. Use arrays for multiple values - NEVER use single strings\n"
        "4. For CMO, use person_titles: [\"CMO\", \"Chief Marketing Officer\"] AND person_seniorities: [\"c_suite\"]\n"
        "5. For locations like Florida, use organization_locations: [\"Florida\"] NOT person_filters\n"
        "6. AVOID generic terms like 'sales', 'business', 'company' in keyword tags\n"
        "7. Focus primarily on person titles, locations, and seniority levels\n"
        "8. Return ONLY valid JSON with proper structure - NO markdown code blocks\n"
        "9. The JSON must have exactly these keys: organization_filters, person_filters, reasoning\n"
        "10. Each filter value must be an array, even for single values\n\n"
        "EXAMPLE CORRECT FORMAT:\n"
        "{\n"
        "  \"organization_filters\": {\n"
        "    \"organization_locations\": [\"Florida\"]\n"
        "  },\n"
        "  \"person_filters\": {\n"
        "    \"person_titles\": [\"CMO\", \"Chief Marketing Officer\"],\n"
        "    \"person_seniorities\": [\"c_suite\"],\n"
        "    \"include_similar_titles\": true\n"
        "  },\n"
        "  \"reasoning\": \"Looking for CMOs in Florida companies\"\n"
        "}"
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
    
    if not isinstance(filters["organization_filters"], dict):
        filters["organization_filters"] = {}
    if not isinstance(filters["person_filters"], dict):
        filters["person_filters"] = {}
    if not isinstance(filters["reasoning"], str):
        filters["reasoning"] = "Generated filters based on prompt analysis"

    org_list_keys = [
        "organization_locations",
        "organization_num_employees_ranges",
        "q_organization_keyword_tags"
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
