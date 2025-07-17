import requests
import json
import asyncio
import httpx
from prompt_formatting import INTERNAL_DATABASE_API_KEY

async def search_people_via_internal_database(filters: dict, page: int = 1, per_page: int = 5) -> list:
    """
    Search our internal database for people matching the filters, then enrich each person and only return those with a LinkedIn URL.
    Handles enrichment errors gracefully and logs skipped people.
    
    This is an async function that returns a list of enriched people.
    """
    if not INTERNAL_DATABASE_API_KEY:
        print("⚠️  Our internal database API key not found. Cannot search for people.")
        return []
    
    payload = {}
    payload.update(filters.get("organization_filters", {}))
    payload.update(filters.get("person_filters", {}))
    
    # Add US location filter to limit results to United States
    if "person_filters" not in payload:
        payload["person_filters"] = {}
    payload["person_filters"]["locations"] = ["United States"]
    
    payload["page"] = page
    payload["per_page"] = per_page

    headers = {
        "x-api-key": INTERNAL_DATABASE_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.apollo.io/api/v1/mixed_people/search", 
                json=payload, 
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"⚠️  Apollo API request failed: {e}")
        return []

    people = data.get("people", [])
    enriched = []
    
    async with httpx.AsyncClient(timeout=10) as client:
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
                print(f"[Internal Database] Attempting enrichment for person ID {person_id}")
                enrich_response = await client.post(
                    "https://api.apollo.io/api/v1/people/match",
                    params=enrich_params,
                    headers=headers
                )
                enrich_response.raise_for_status()
                enriched_person = enrich_response.json().get("person", {})
                
                # Extract profile photo URL from Apollo data
                profile_photo_url = (
                    enriched_person.get("profile_picture_url") or
                    enriched_person.get("profile_photo_url") or
                    enriched_person.get("photo_url") or
                    None
                )
                
                # Add profile photo URL to enriched person data
                if profile_photo_url:
                    enriched_person["profile_photo_url"] = profile_photo_url
                    print(f"[Internal Database] Found profile photo: {profile_photo_url}")
                
                if enriched_person.get("linkedin_url"):
                    enriched.append(enriched_person)
                    print(f"[Internal Database] Enriched and kept: {enriched_person.get('name', 'Unknown')} ({enriched_person.get('linkedin_url')}) - Photo: {'Yes' if profile_photo_url else 'No'}")
                else:
                    print(f"[Internal Database] Skipped (no LinkedIn): {enriched_person.get('name', 'Unknown')}")
            except Exception as e:
                print(f"[Internal Database] Enrichment failed for person ID {person_id}: {e}")
                continue
                
            # Add a small delay between requests to avoid rate limiting
            await asyncio.sleep(0.5)
            
            if len(enriched) >= per_page:
                break
                
    print(f"[Internal Database] Returning {len(enriched)} enriched people with LinkedIn URLs.")
    return enriched

# Synchronous version for backward compatibility
def search_people_via_internal_database_sync(filters: dict, page: int = 1, per_page: int = 5) -> list:
    """
    Synchronous version of search_people_via_internal_database for backward compatibility.
    """
    return asyncio.run(search_people_via_internal_database(filters, page, per_page))

if __name__ == "__main__":
    try:
        filters_json = input("Enter JSON string for filters: ")
        filters = json.loads(filters_json)
    except Exception:
        print("Invalid JSON input.")
        exit(1)

    people = search_people_via_internal_database_sync(filters)
    print(json.dumps(people, indent=2))