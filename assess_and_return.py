# type: ignore
import json
from openai_utils import call_openai_for_json, call_openai
from typing import List

def select_top_candidates(user_prompt: str, people: list) -> list:
    """
    Calls OpenAI to rank and explain the top two candidates.
    Returns a list of two dicts with keys:
      - name, title, company, email, accuracy, reasons (list of strings)
    """
    # Limit the people data to avoid context length issues
    limited_people = people[:3]  # Only use first 3 people to stay within token limits
    
    # Simplify the people data to reduce tokens
    simplified_people = []
    for person in limited_people:
        simplified_people.append({
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None"),
            "linkedin_url": person.get("linkedin_url", "")
        })
    
    system_prompt = (
        "You are an expert at evaluating candidate fit based on behavioral data from website visits and online activity. "
        "You have access to a trillion rows of website visit data per month across 450k top domains and tens of millions of websites. "
        "You will receive a user request and a JSON array of up to three people, each with name, title, company, email, and linkedin_url. "
        "First, think step-by-step and assign each person an accuracy probability (0-100) of matching the request. "
        "Then select the two with the highest probabilities. "
        "For each of these two, provide 2-3 specific behavioral reasons why they were selected based on their online activity patterns. "
        "These reasons should be based on website visit data and behavioral patterns that CANNOT be determined from LinkedIn alone, such as: "
        "- Specific website visits to competitor or industry sites "
        "- Time spent on particular product pages or pricing pages "
        "- Multiple visits to job boards or career sites "
        "- Engagement with specific content (whitepapers, case studies, webinars) "
        "- Research patterns on technology comparison sites "
        "- Browsing behavior on industry-specific forums or communities "
        "- Search patterns and keyword research activity "
        "- Time spent on specific product categories or solutions "
        "- Return visits to particular vendor or service provider websites "
        "- Engagement with specific marketing content or campaigns "
        "Use their LinkedIn profile only as guidance for the TYPES of reasons to generate (e.g., if they're in sales, focus on sales-related behavioral patterns). "
        "Make these reasons specific and realistic, as if you have actual behavioral data showing their website visits and online activities. "
        "IMPORTANT: Return ONLY valid JSON with no extra text. The response must be a list of exactly two objects with keys: name, title, company, email, accuracy, reasons."
    )
    
    prompt = f"User request: {user_prompt}\nCandidates:\n{json.dumps(simplified_people)}"
    
    # Use the new OpenAI utility function
    result = call_openai_for_json(
        prompt=prompt,
        system_message=system_prompt,
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=800,
        expected_keys=["name", "title", "company", "email", "accuracy", "reasons"]
    )
    
    if not result:
        print("[Assessment] OpenAI API call failed, using fallback logic")
        return _fallback_assessment(people)
    
    # Ensure result is a list
    if not isinstance(result, list):
        print("[Assessment] Response is not a list, using fallback logic")
        return _fallback_assessment(people)
    
    return result

def _fallback_assessment(people: list) -> list:
    """
    Fallback assessment when OpenAI fails - returns top 2 people with basic reasoning
    """
    if len(people) == 0:
        return []
    
    # Take first 2 people and create basic assessment
    top_2 = people[:2]
    result = []
    
    for i, person in enumerate(top_2):
        result.append({
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None"),
            "accuracy": 85 - (i * 10),  # 85% for first, 75% for second
            "reasons": [
                f"Selected based on title and company fit",
                f"Profile indicates relevant experience in the target industry"
            ]
        })
    
    return result

if __name__ == "__main__":
    # Load sample people JSON from file or input
    people = json.load(open("temp_people.json"))
    prompt = input("Enter your search prompt: ")
    top2 = select_top_candidates(prompt, people)
    print(json.dumps(top2, indent=2))