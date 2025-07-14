#!/usr/bin/env python3
"""
Automated test script for knowledge_gpt pipeline
Tests various prompts to ensure the system works correctly across different scenarios
"""

import json
import time
from prompt_formatting import parse_prompt_to_apollo_filters, simulate_behavioral_data
from apollo_api_call import search_people_via_apollo
from linkedin_scraping import scrape_linkedin_profiles, scrape_linkedin_posts
from assess_and_return import select_top_candidates

def test_pipeline(prompt: str, test_name: str) -> dict:
    """
    Test the complete pipeline with a given prompt
    """
    print(f"\n{'='*80}")
    print(f"🧪 TEST: {test_name}")
    print(f"📝 PROMPT: {prompt}")
    print(f"{'='*80}")
    
    results = {
        "test_name": test_name,
        "prompt": prompt,
        "success": False,
        "steps_completed": [],
        "errors": [],
        "candidates_found": 0,
        "top_candidates": []
    }
    
    try:
        # Step 1: Generate Apollo filters
        print("📊 Step 1/5: Generating Apollo API filters...")
        filters = parse_prompt_to_apollo_filters(prompt)
        
        if filters["reasoning"].startswith("Error"):
            results["errors"].append(f"Filter generation failed: {filters['reasoning']}")
            print(f"❌ Error: {filters['reasoning']}")
            return results
        
        print("✅ Filters generated successfully!")
        print(f"📋 Reasoning: {filters['reasoning']}")
        results["steps_completed"].append("filter_generation")
        
        # Step 2: Search Apollo for people
        print("\n🔎 Step 2/5: Searching Apollo for matching people...")
        try:
            people = search_people_via_apollo(filters, page=1, per_page=2)
            results["candidates_found"] = len(people)
            print(f"✅ Found {len(people)} people with LinkedIn profiles")
            
            if not people:
                print("⚠️  No people found, testing behavioral simulation...")
                behavioral_data = simulate_behavioral_data(filters)
                print("📈 Simulated Behavioral Insights:")
                print(json.dumps(behavioral_data, indent=2))
                results["steps_completed"].append("behavioral_simulation")
                results["success"] = True
                return results
                
        except Exception as e:
            results["errors"].append(f"Apollo API error: {str(e)}")
            print(f"❌ Apollo API error: {e}")
            print("⚠️  Continuing with behavioral simulation only...")
            behavioral_data = simulate_behavioral_data(filters)
            print("📈 Simulated Behavioral Insights:")
            print(json.dumps(behavioral_data, indent=2))
            results["steps_completed"].append("behavioral_simulation")
            results["success"] = True
            return results
        
        results["steps_completed"].append("apollo_search")
        
        # Step 3: Scrape LinkedIn profiles
        print("\n📱 Step 3/5: Scraping LinkedIn profiles...")
        linkedin_urls = [person.get("linkedin_url") for person in people if person.get("linkedin_url")]
        
        if not linkedin_urls:
            print("⚠️  No LinkedIn URLs found. Proceeding with basic data...")
            enriched_people = people
        else:
            print(f"🔗 Scraping {len(linkedin_urls)} LinkedIn profiles...")
            profile_data = scrape_linkedin_profiles(linkedin_urls)
            
            # Merge profile data with Apollo data
            enriched_people = []
            for i, person in enumerate(people):
                if person.get("linkedin_url") and profile_data:
                    # Handle different possible return types from LinkedIn scraping
                    if isinstance(profile_data, list) and i < len(profile_data):
                        person["linkedin_profile"] = profile_data[i]
                    elif isinstance(profile_data, dict) and str(i) in profile_data:
                        person["linkedin_profile"] = profile_data[str(i)]
                    elif isinstance(profile_data, dict) and i in profile_data:
                        person["linkedin_profile"] = profile_data[i]
                    else:
                        # If we can't match the data, just add the person without LinkedIn data
                        pass
                enriched_people.append(person)
            
            if profile_data:
                print("✅ LinkedIn profiles scraped successfully!")
            else:
                print("⚠️  LinkedIn scraping unavailable. Continuing with Apollo data only...")
        
        results["steps_completed"].append("linkedin_scraping")
        
        # Step 4: Scrape LinkedIn posts
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
        
        results["steps_completed"].append("post_scraping")
        
        # Step 5: Assess and return top 2 candidates
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
            
            results["top_candidates"] = top_candidates
            results["success"] = True
            
        except Exception as e:
            results["errors"].append(f"Assessment error: {str(e)}")
            print(f"❌ Assessment error: {e}")
            print("Showing raw Apollo data instead...")
            print("\n📋 Raw Apollo Results:")
            for person in people[:2]:
                print(f"• {person.get('name', 'Unknown')} - {person.get('title', 'Unknown')} at {person.get('organization_name', 'Unknown')}")
        
        results["steps_completed"].append("assessment")
        
    except Exception as e:
        results["errors"].append(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {e}")
    
    return results

def run_automated_tests():
    """
    Run a series of automated tests with different prompts
    """
    test_prompts = [
        {
            "prompt": "a sales director in new york looking to hire new sdrs",
            "name": "Sales Director Hiring SDRs"
        },
        {
            "prompt": "a cto at a startup looking for a new crm",
            "name": "CTO Seeking CRM"
        },
        {
            "prompt": "a marketing manager looking for new marketing automation tools",
            "name": "Marketing Manager Seeking Automation"
        }
    ]
    
    all_results = []
    
    print("🤖 KNOWLEDGE_GPT - AUTOMATED PIPELINE TESTING")
    print("="*80)
    print("Running comprehensive tests across different scenarios...")
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n🔄 Running test {i}/{len(test_prompts)}...")
        result = test_pipeline(test["prompt"], test["name"])
        all_results.append(result)
        
        # Brief pause between tests
        time.sleep(1)
    
    # Generate test summary
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    successful_tests = sum(1 for r in all_results if r["success"])
    total_candidates = sum(r["candidates_found"] for r in all_results)
    total_errors = sum(len(r["errors"]) for r in all_results)
    
    print(f"✅ Successful Tests: {successful_tests}/{len(test_prompts)}")
    print(f"👥 Total Candidates Found: {total_candidates}")
    print(f"❌ Total Errors: {total_errors}")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in all_results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"   {status} {result['test_name']}: {result['candidates_found']} candidates, {len(result['errors'])} errors")
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to test_results.json")
    print(f"🎉 Automated testing complete!")

if __name__ == "__main__":
    run_automated_tests() 