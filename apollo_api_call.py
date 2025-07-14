import requests
import json
from prompt_formatting import INTERNAL_DATABASE_API_KEY

def search_people_via_internal_database(filters: dict, page: int = 1, per_page: int = 5) -> list:
    """
    Search our internal database for people matching the filters, then enrich each person and only return those with a LinkedIn URL.
    Handles enrichment errors gracefully and logs skipped people.
    """
    if not INTERNAL_DATABASE_API_KEY:
        print("⚠️  Our internal database API key not found. Cannot search for people.")
        return []
    
    payload = {}
    payload.update(filters.get("organization_filters", {}))
    payload.update(filters.get("person_filters", {}))
    payload["page"] = page
    payload["per_page"] = per_page

    headers = {
        "x-api-key": INTERNAL_DATABASE_API_KEY
    }

    try:
        response = requests.post("https://api.our-internal-database.com/api/v1/mixed_people/search", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Our internal database API request failed: {e}")
        return []

    data = response.json()
    people = data.get("people", [])
    enriched = []
    for person in people:
        person_id = person.get("id")
        if not person_id:
            print(f"[Internal Database] Skipping person with missing ID: {person}")
            continue
        # Enrich via our internal database People Enrichment endpoint
        enrich_params = {
            "id": person_id,
            "reveal_personal_emails": False,
            "reveal_phone_number": False
        }
        try:
            enrich_response = requests.post(
                "https://api.our-internal-database.com/api/v1/people/match",
                params=enrich_params,
                headers=headers,
                timeout=10
            )
            enrich_response.raise_for_status()
            enriched_person = enrich_response.json().get("person", {})
            if enriched_person.get("linkedin_url"):
                enriched.append(enriched_person)
                print(f"[Internal Database] Enriched and kept: {enriched_person.get('name', 'Unknown')} ({enriched_person.get('linkedin_url')})")
            else:
                print(f"[Internal Database] Skipped (no LinkedIn): {enriched_person.get('name', 'Unknown')}")
        except Exception as e:
            print(f"[Internal Database] Enrichment failed for person ID {person_id}: {e}")
            continue
        if len(enriched) >= per_page:
            break
    print(f"[Internal Database] Returning {len(enriched)} enriched people with LinkedIn URLs.")
    return enriched

if __name__ == "__main__":
    try:
        filters_json = input("Enter JSON string for filters: ")
        filters = json.loads(filters_json)
    except Exception:
        print("Invalid JSON input.")
        exit(1)

    people = search_people_via_internal_database(filters)
    print(json.dumps(people, indent=2))
