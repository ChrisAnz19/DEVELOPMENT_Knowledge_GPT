#!/usr/bin/env python3
"""
Test script to run the pipeline step by step and identify issues
"""

import os
import sys
import json
from datetime import datetime, timezone

# Set environment variables
os.environ['SCRAPING_DOG_API_KEY'] = '6871f45caa454efe99c697cf'

# Import the pipeline components
from prompt_formatting import parse_prompt_to_internal_database_filters
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import scrape_linkedin_profiles
from assess_and_return import select_top_candidates
from database import store_search_to_database, store_people_to_database

def test_pipeline():
    """Test the pipeline step by step"""
    prompt = "Find marketing directors in San Francisco"
    max_candidates = 2
    
    print("🧪 Testing Knowledge_GPT Pipeline Step by Step")
    print("=" * 50)
    
    # Step 1: Generate filters
    print("\n1️⃣ Generating filters...")
    filters = parse_prompt_to_internal_database_filters(prompt)
    if not filters:
        print("❌ Filter generation failed")
        return
    print(f"✅ Filters generated: {json.dumps(filters, indent=2)}")
    
    # Step 2: Search Apollo
    print("\n2️⃣ Searching Apollo...")
    people = search_people_via_internal_database(filters, page=1, per_page=max_candidates)
    if not people:
        print("❌ Apollo search failed")
        return
    print(f"✅ Found {len(people)} people")
    for person in people:
        print(f"   - {person.get('name')} ({person.get('email')}) at {person.get('company', 'Unknown')}")
    
    # Step 3: LinkedIn enrichment
    print("\n3️⃣ LinkedIn enrichment...")
    linkedin_urls = [p.get('linkedin_url') for p in people if p.get('linkedin_url')]
    if linkedin_urls:
        profile_data = scrape_linkedin_profiles(linkedin_urls)
        print(f"✅ LinkedIn data received: {len(profile_data)} profiles")
        
        # Enrich people with LinkedIn data
        for person in people:
            linkedin_url = person.get('linkedin_url')
            if linkedin_url:
                for profile in profile_data:
                    if profile.get('profile_url') == linkedin_url or profile.get('linkedin_url') == linkedin_url:
                        if profile.get('company') and profile['company'] != 'Unknown':
                            person['company'] = profile['company']
                        if profile.get('location'):
                            person['location'] = profile['location']
                        if profile.get('profile_picture_url'):
                            person['profile_photo_url'] = profile['profile_picture_url']
                        person['linkedin_profile'] = profile
                        break
    else:
        print("⚠️ No LinkedIn URLs found")
    
    # Step 4: Ensure fallback values
    print("\n4️⃣ Setting fallback values...")
    for person in people:
        if not person.get('company') or person.get('company') == 'Unknown':
            email = person.get('email', '')
            if '@' in email:
                domain = email.split('@')[1].split('.')[0]
                if domain and domain.lower() not in ['gmail', 'yahoo', 'hotmail', 'outlook']:
                    person['company'] = domain.title()
        
        if not person.get('location'):
            person['location'] = 'Unknown'
        
        if not person.get('city'):
            person['city'] = 'Unknown'
    
    print("✅ Fallback values set")
    
    # Step 5: Assess candidates
    print("\n5️⃣ Assessing candidates...")
    assessed_candidates = select_top_candidates(prompt, people)
    if not assessed_candidates:
        print("❌ Assessment failed")
        return
    print(f"✅ Assessment completed: {len(assessed_candidates)} candidates")
    
    # Step 6: Store in database
    print("\n6️⃣ Storing in database...")
    search_data = {
        'request_id': 'test-pipeline-' + datetime.now().strftime('%Y%m%d-%H%M%S'),
        'prompt': prompt,
        'filters': filters,
        'status': 'completed',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'completed_at': datetime.now(timezone.utc).isoformat()
    }
    
    try:
        search_id = store_search_to_database(search_data)
        print(f"✅ Search stored with ID: {search_id}")
        
        if assessed_candidates:
            store_people_to_database(search_id, assessed_candidates)
            print(f"✅ Stored {len(assessed_candidates)} candidates")
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📊 Final candidates:")
        for candidate in assessed_candidates:
            print(f"   - {candidate.get('name')} ({candidate.get('email')})")
            print(f"     Company: {candidate.get('company', 'Unknown')}")
            print(f"     Location: {candidate.get('location', 'Unknown')}")
            print(f"     Photo: {candidate.get('profile_photo_url', 'None')}")
            print(f"     LinkedIn: {candidate.get('linkedin_url', 'None')}")
            print()
        
    except Exception as e:
        print(f"❌ Database storage failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pipeline() 