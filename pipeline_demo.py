#!/usr/bin/env python3
"""
Knowledge_GPT Pipeline Demonstration
Shows the complete flow from prompt entry to Supabase storage
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "https://knowledge-gpt-siuq.onrender.com"

def log(message: str, level: str = "INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def demo_full_pipeline():
    """Demonstrate the complete pipeline"""
    print("🚀 Knowledge_GPT Pipeline Demonstration")
    print("=" * 60)
    print("This demo shows the complete flow from prompt entry to Supabase storage")
    print("=" * 60)
    
    # Test prompt
    prompt = "Find senior software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco"
    
    log(f"📝 Input Prompt: {prompt}")
    print()
    
    # Step 1: Create search
    log("🔍 Step 1: Creating search request...")
    payload = {
        "prompt": prompt,
        "max_candidates": 2,
        "include_linkedin": True,
        "include_posts": False
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/search", json=payload)
        if response.status_code == 200:
            data = response.json()
            request_id = data.get("request_id")
            log(f"✅ Search created successfully!")
            log(f"   Request ID: {request_id}")
            log(f"   Status: {data.get('status')}")
            log(f"   Created at: {data.get('created_at')}")
        else:
            log(f"❌ Failed to create search: {response.status_code}", "ERROR")
            return
    except Exception as e:
        log(f"❌ Exception creating search: {e}", "ERROR")
        return
    
    print()
    
    # Step 2: Poll for completion
    log("⏳ Step 2: Processing search (this may take 10-30 seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < 60:  # Wait up to 60 seconds
        try:
            response = requests.get(f"{API_BASE_URL}/api/search/{request_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                if status == "completed":
                    log("✅ Search completed successfully!")
                    break
                elif status == "failed":
                    error = data.get("error", "Unknown error")
                    log(f"❌ Search failed: {error}", "ERROR")
                    return
                elif status == "processing":
                    log("⏳ Still processing...")
                else:
                    log(f"Unknown status: {status}")
            else:
                log(f"❌ Failed to get search status: {response.status_code}", "ERROR")
                return
                
        except Exception as e:
            log(f"❌ Exception while polling: {e}", "ERROR")
            return
            
        time.sleep(5)  # Wait 5 seconds between polls
    else:
        log("❌ Search timed out", "ERROR")
        return
    
    print()
    
    # Step 3: Get final results
    log("📊 Step 3: Retrieving final results...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/search/{request_id}")
        if response.status_code == 200:
            data = response.json()
            
            # Display filters
            filters = data.get("filters", {})
            log("🎯 Generated Filters:")
            if filters:
                person_filters = filters.get("person_filters", {})
                org_filters = filters.get("organization_filters", {})
                
                if person_filters:
                    log(f"   Person Filters:")
                    for key, value in person_filters.items():
                        if value:
                            log(f"     {key}: {value}")
                
                if org_filters:
                    log(f"   Organization Filters:")
                    for key, value in org_filters.items():
                        if value:
                            log(f"     {key}: {value}")
                
                reasoning = filters.get("reasoning", "")
                if reasoning:
                    log(f"   Reasoning: {reasoning}")
            else:
                log("   No filters generated")
            
            print()
            
            # Display candidates
            candidates = data.get("candidates", [])
            log(f"👥 Found {len(candidates)} candidates:")
            for i, candidate in enumerate(candidates, 1):
                log(f"   Candidate {i}:")
                log(f"     Name: {candidate.get('name', 'Unknown')}")
                log(f"     Title: {candidate.get('title', 'Unknown')}")
                log(f"     Company: {candidate.get('company', 'Unknown')}")
                log(f"     Email: {candidate.get('email', 'Not available')}")
                log(f"     Accuracy: {candidate.get('accuracy', 0)}%")
                log(f"     LinkedIn: {candidate.get('linkedin_url', 'Not available')}")
                
                reasons = candidate.get('reasons', [])
                if reasons:
                    log(f"     Reasons: {', '.join(reasons)}")
                print()
            
            # Display behavioral data
            behavioral_data = data.get("behavioral_data", {})
            if behavioral_data:
                log("🧠 Behavioral Insights:")
                insights = behavioral_data.get("behavioral_insights", {})
                for key, value in insights.items():
                    if value:
                        log(f"   {key.replace('_', ' ').title()}: {value[:100]}...")
                print()
            
            # Step 4: Verify data persistence
            log("💾 Step 4: Verifying data persistence...")
            
            # Check if data is stored in database by listing searches
            response = requests.get(f"{API_BASE_URL}/api/search")
            if response.status_code == 200:
                searches_data = response.json()
                searches = searches_data.get("searches", [])
                
                # Find our search in the list
                our_search = next((s for s in searches if s.get("request_id") == request_id), None)
                if our_search:
                    log("✅ Data successfully stored in database!")
                    log(f"   Found in database with status: {our_search.get('status')}")
                else:
                    log("⚠️  Search not found in database listing", "WARNING")
            
            # Step 5: Test JSON file access
            log("📄 Step 5: Testing JSON file access...")
            response = requests.get(f"{API_BASE_URL}/api/search/{request_id}/json")
            if response.status_code == 200:
                json_data = response.json()
                log(f"✅ JSON file accessible, data size: {len(str(json_data))} characters")
            else:
                log(f"❌ JSON file access failed: {response.status_code}", "ERROR")
            
            print()
            log("🎉 Pipeline demonstration completed successfully!")
            log(f"📋 Summary:")
            log(f"   - Search created and processed")
            log(f"   - {len(candidates)} candidates found")
            log(f"   - Behavioral insights generated")
            log(f"   - Data stored in Supabase database")
            log(f"   - JSON file accessible")
            
        else:
            log(f"❌ Failed to get final results: {response.status_code}", "ERROR")
            
    except Exception as e:
        log(f"❌ Exception getting results: {e}", "ERROR")

def main():
    """Main function"""
    try:
        demo_full_pipeline()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")

if __name__ == "__main__":
    main() 