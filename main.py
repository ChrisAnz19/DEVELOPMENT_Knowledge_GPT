from prompt_formatting import parse_prompt_to_internal_database_filters, simulate_behavioral_data
from apollo_api_call import search_people_via_internal_database
from linkedin_scraping import scrape_linkedin_profiles, scrape_linkedin_posts
from assess_and_return import select_top_candidates
import json
import time

# type: ignore

def main():
    """
    Main CLI interface for the knowledge_gpt system.
    Complete pipeline: Prompt → Filters → Apollo Search → LinkedIn Scraping → Assessment → Top 2 Results
    """
    print("🤖 knowledge_gpt - Complete Behavioral Analysis Pipeline")
    print("=" * 70)
    print("Pipeline: Prompt → Filters → Apollo Search → LinkedIn Scraping → Assessment → Top 2")
    print("Note: Behavioral data is AI-simulated until the actual dataset is migrated.\n")
    
    while True:
        try:
            # Step 1: Get user input
            prompt = input("Enter your search prompt (or 'quit' to exit): ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
                
            if not prompt:
                print("Please enter a valid prompt.\n")
                continue
            
            print(f"\n🔍 Processing: '{prompt}'")
            print("=" * 50)
            
            # Step 2: Generate our internal database filters
            print("📊 Step 1/5: Generating our internal database API filters...")
            filters = parse_prompt_to_internal_database_filters(prompt)
            
            if filters["reasoning"].startswith("Error"):
                print(f"❌ Error: {filters['reasoning']}")
                continue
                
            print("✅ Filters generated successfully!")
            print(f"📋 Reasoning: {filters['reasoning']}")
            
            # Step 3: Search our internal database for people
            print("\n🔎 Step 2/5: Searching our internal database for matching people...")
            try:
                people = search_people_via_internal_database(filters, page=1, per_page=3)
                print(f"✅ Found {len(people)} people with LinkedIn profiles")
                
                if not people:
                    print("❌ No people found matching your criteria. Try a different prompt.")
                    continue
                    
            except Exception as e:
                print(f"❌ Our internal database API error: {e}")
                print("⚠️  Continuing with behavioral simulation only...")
                # Fall back to behavioral simulation
                behavioral_data = simulate_behavioral_data(filters)
                print("\n📈 Simulated Behavioral Insights:")
                print(json.dumps(behavioral_data, indent=2))
                continue
            
            # Step 4: Scrape LinkedIn profiles
            print("\n📱 Step 3/5: Scraping LinkedIn profiles...")
            linkedin_urls = [person.get("linkedin_url") for person in people if person.get("linkedin_url")]
            
            if not linkedin_urls:
                print("⚠️  No LinkedIn URLs found. Proceeding with basic data...")
                enriched_people = people
            else:
                print(f"🔗 Scraping {len(linkedin_urls)} LinkedIn profiles...")
                profile_data = scrape_linkedin_profiles(linkedin_urls)
                
                # Merge profile data with our internal database data
                enriched_people = []
                for i, person in enumerate(people):
                    if person.get("linkedin_url") and i < len(profile_data) and profile_data:
                        person["linkedin_profile"] = profile_data[i]
                    enriched_people.append(person)
                
                if profile_data:
                    print("✅ LinkedIn profiles scraped successfully!")
                else:
                    print("⚠️  LinkedIn scraping unavailable. Continuing with our internal database data only...")
            
            # Step 5: Scrape LinkedIn posts for top profiles
            print("\n📝 Step 4/5: Scraping recent LinkedIn posts...")
            posts_scraped = False
            for person in enriched_people[:2]:  # Only scrape posts for top 2 candidates
                profile = person.get("linkedin_profile", {})
                posts = profile.get("posts", [])
                recent_posts = posts[:5]  # Get up to 5 recent posts
                
                if recent_posts:
                    print(f"📄 Scraping posts for {person.get('name', 'Unknown')}...")
                    posts_data = scrape_linkedin_posts(recent_posts)
                    if posts_data:
                        person["linkedin_posts"] = posts_data
                        posts_scraped = True
                    time.sleep(1)  # Rate limiting
            
            if posts_scraped:
                print("✅ LinkedIn posts scraped successfully!")
            else:
                print("⚠️  LinkedIn post scraping unavailable. Continuing without post data...")
            
            # Step 6: Assess and return top 2 candidates
            print("\n🧠 Step 5/5: Assessing candidates and selecting top 2...")
            try:
                top_candidates = select_top_candidates(prompt, enriched_people)
                
                print("\n" + "🎯" + "="*50 + "🎯")
                print("🏆 TOP 2 CANDIDATES SELECTED")
                print("="*50)
                
                for i, candidate in enumerate(top_candidates, 1):
                    print(f"\n🥇 #{i}: {candidate.get('name', 'Unknown')}")
                    print(f"   📋 Title: {candidate.get('title', 'Unknown')}")
                    print(f"   🏢 Company: {candidate.get('company', 'Unknown')}")
                    print(f"   📧 Email: {candidate.get('email', 'Not available')}")
                    print(f"   📊 Accuracy Score: {candidate.get('accuracy', 'N/A')}%")
                    print(f"   💡 Reasons:")
                    for reason in candidate.get('reasons', []):
                        print(f"      • {reason}")
                
                print("\n" + "="*50)
                
            except Exception as e:
                print(f"❌ Assessment error: {e}")
                print("Showing raw our internal database data instead...")
                print("\n📋 Raw our internal database Results:")
                for person in people[:2]:
                    print(f"• {person.get('name', 'Unknown')} - {person.get('title', 'Unknown')} at {person.get('organization_name', 'Unknown')}")
            
            print("\n" + "="*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()
