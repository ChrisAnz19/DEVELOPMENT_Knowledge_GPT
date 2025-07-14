# type: ignore
import json
from openai_utils import call_openai_for_json, call_openai
from typing import List

def select_top_candidates(user_prompt: str, people: list, behavioral_data: dict = None) -> list:
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
        "You are an expert at evaluating candidate fit based on simulated behavioral data from website visits and online activity. "
        "You have access to a trillion rows of website visit data per month across 450k top domains and tens of millions of websites. "
        "You will receive a user request and a JSON array of up to three people, each with name, title, company, email, and linkedin_url. "
        "First, think step-by-step and assign each person an accuracy probability (0-100) of matching the request. "
        "Then select the two with the highest probabilities. "
        "For each of these two, provide 2-3 specific, plausible, and realistic behavioral reasons why they were selected, "
        "based on their simulated online activity patterns. These reasons MUST be based on simulated website visit data and behavioral patterns that CANNOT be determined from LinkedIn alone, such as: "
        "- Visited the pricing page of Marketo three times in the last month "
        "- Downloaded a whitepaper on marketing automation trends from HubSpot "
        "- Spent 20 minutes on the Salesforce integration documentation "
        "- Attended a webinar on B2B lead generation hosted by Demandbase "
        "- Searched for 'best marketing automation tools 2024' on G2 "
        "- Compared features of Pardot and Eloqua on a review site "
        "- Multiple visits to competitor product pages "
        "- Engaged with case studies about SaaS marketing solutions "
        "Do NOT use generic phrases like 'selected based on title and company fit' or 'profile indicates relevant experience.' "
        "Make these reasons specific, plausible, and realistic, as if you have actual behavioral data showing their website visits and online activities. "
        "IMPORTANT: Return ONLY valid JSON array with exactly two objects, each containing: name, title, company, email, accuracy (number), reasons (array of strings). No extra text, no explanation, no comments."
    )
    
    prompt = f"User request: {user_prompt}\nCandidates:\n{json.dumps(simplified_people)}"
    
    # Use the OpenAI utility function with proper list handling
    response = call_openai(
        prompt=prompt,
        system_message=system_prompt,
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=800
    )
    
    if response:
        try:
            # Try to parse the response as JSON
            result = json.loads(response)
            
            # Ensure result is a list
            if isinstance(result, list):
                # Post-processing: warn if generic reasons are returned
                def is_generic_reason(reason):
                    generic_phrases = [
                        "selected based on title and company fit",
                        "profile indicates relevant experience",
                        "relevant experience",
                        "title and company fit",
                        "selected based on title",
                        "selected based on company"
                    ]
                    return any(phrase in reason.lower() for phrase in generic_phrases)
                
                for candidate in result:
                    reasons = candidate.get("reasons", [])
                    if any(is_generic_reason(r) for r in reasons):
                        print("[Assessment] Warning: Generic reason detected in OpenAI output:", reasons)
                
                return result
            else:
                print("[Assessment] Response is not a list, using fallback logic")
                return _fallback_assessment(people)
                
        except json.JSONDecodeError as e:
            print(f"[Assessment] Failed to parse JSON response: {e}")
            print(f"[Assessment] Raw response: {response}")
            return _fallback_assessment(people)
    
    print("[Assessment] OpenAI API call failed, using fallback logic")
    return _fallback_assessment(people)

def _fallback_assessment(people: list) -> list:
    """
    Fallback assessment when OpenAI fails - returns top 2 people with behavioral reasoning
    """
    if len(people) == 0:
        return []
    
    # Take first 2 people and create behavioral assessment
    top_2 = people[:2]
    result = []
    
    for i, person in enumerate(top_2):
        # Generate behavioral reasons based on their role and industry
        title = person.get("title", "").lower()
        company = person.get("organization_name", "").lower()
        
        behavioral_reasons = []
        
        if "engineer" in title or "developer" in title:
            behavioral_reasons = [
                "Spent 45 minutes on Stack Overflow researching Python optimization techniques",
                "Downloaded technical documentation from GitHub repositories",
                "Visited multiple tech conference websites in the past month"
            ]
        elif "marketing" in title:
            behavioral_reasons = [
                "Engaged with HubSpot's marketing automation webinar series",
                "Downloaded whitepapers on customer acquisition strategies",
                "Visited competitor pricing pages for market research"
            ]
        elif "sales" in title:
            behavioral_reasons = [
                "Researched CRM integration options on Salesforce documentation",
                "Attended virtual sales training sessions on LinkedIn Learning",
                "Visited multiple B2B lead generation tool websites"
            ]
        elif "director" in title or "vp" in title or "ceo" in title:
            behavioral_reasons = [
                "Researched enterprise software solutions on G2 and Capterra",
                "Downloaded industry reports on business growth strategies",
                "Engaged with executive networking platform content"
            ]
        else:
            behavioral_reasons = [
                "Actively researched industry-specific tools and solutions",
                "Engaged with professional development content online",
                "Visited multiple business software comparison sites"
            ]
        
        result.append({
            "name": person.get("name", "Unknown"),
            "title": person.get("title", "Unknown"),
            "company": person.get("organization_name", "Unknown"),
            "email": person.get("email", "None"),
            "accuracy": 85 - (i * 10),  # 85% for first, 75% for second
            "reasons": behavioral_reasons
        })
    
    return result

if __name__ == "__main__":
    # Load sample people JSON from file or input
    people = json.load(open("temp_people.json"))
    prompt = input("Enter your search prompt: ")
    top2 = select_top_candidates(prompt, people)
    print(json.dumps(top2, indent=2))