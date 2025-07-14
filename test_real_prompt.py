#!/usr/bin/env python3
"""
Real Prompt Test for Knowledge_GPT API
Tests the complete pipeline with a realistic business prompt
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_URL = "https://knowledge-gpt-siuq.onrender.com"

def test_real_prompt():
    """Test the API with a realistic business prompt"""
    
    # Realistic business prompt
    test_prompt = "Find me marketing directors at SaaS companies in San Francisco who are likely to be interested in buying marketing automation software"
    
    print("🚀 KNOWLEDGE_GPT API - REAL PROMPT TEST")
    print("=" * 60)
    print(f"📝 Test Prompt: '{test_prompt}'")
    print(f"🌐 API URL: {API_BASE_URL}")
    print("=" * 60)
    
    # Step 1: Health Check
    print("\n1️⃣ Testing API Health...")
    try:
        health_response = requests.get(f"{API_BASE_URL}/", timeout=10)
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ API Health: {health_data['status']}")
            print(f"⏰ Timestamp: {health_data['timestamp']}")
            print(f"📦 Version: {health_data['version']}")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return
    
    # Step 2: Create Search Request
    print("\n2️⃣ Creating Search Request...")
    search_payload = {
        "prompt": test_prompt,
        "max_candidates": 3,
        "include_linkedin": True,
        "include_posts": True
    }
    
    try:
        search_response = requests.post(
            f"{API_BASE_URL}/api/search",
            json=search_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            request_id = search_data["request_id"]
            print(f"✅ Search created successfully!")
            print(f"🆔 Request ID: {request_id}")
            print(f"📊 Status: {search_data['status']}")
            print(f"⏰ Created: {search_data['created_at']}")
        else:
            print(f"❌ Search creation failed: {search_response.status_code}")
            print(f"Response: {search_response.text}")
            return
            
    except Exception as e:
        print(f"❌ Search creation error: {e}")
        return
    
    # Step 3: Poll for Results
    print("\n3️⃣ Polling for Results...")
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            result_response = requests.get(
                f"{API_BASE_URL}/api/search/{request_id}",
                timeout=10
            )
            
            if result_response.status_code == 200:
                result_data = result_response.json()
                status = result_data["status"]
                
                print(f"⏳ Attempt {attempt + 1}: Status = {status}")
                
                if status == "completed":
                    print("✅ Search completed! Processing results...")
                    break
                elif status == "failed":
                    print(f"❌ Search failed: {result_data.get('error', 'Unknown error')}")
                    return
                else:
                    # Still processing
                    time.sleep(10)  # Wait 10 seconds before next poll
                    attempt += 1
            else:
                print(f"❌ Result polling failed: {result_response.status_code}")
                return
                
        except Exception as e:
            print(f"❌ Polling error: {e}")
            return
    
    if attempt >= max_attempts:
        print("❌ Timeout: Search took too long to complete")
        return
    
    # Step 4: Display Results
    print("\n4️⃣ DISPLAYING RESULTS")
    print("=" * 60)
    
    # Get final results
    final_response = requests.get(f"{API_BASE_URL}/api/search/{request_id}")
    final_data = final_response.json()
    
    # Display Filters
    if final_data.get("filters"):
        print("\n📊 GENERATED FILTERS:")
        print("-" * 30)
        filters = final_data["filters"]
        print(f"🎯 Reasoning: {filters.get('reasoning', 'N/A')}")
        if "filters" in filters:
            print("🔍 Applied Filters:")
            for key, value in filters["filters"].items():
                print(f"   • {key}: {value}")
    
    # Display Behavioral Data
    if final_data.get("behavioral_data"):
        print("\n📈 BEHAVIORAL INSIGHTS:")
        print("-" * 30)
        behavioral = final_data["behavioral_data"]
        print(f"🎯 Target Persona: {behavioral.get('target_persona', 'N/A')}")
        print(f"💰 Budget Range: {behavioral.get('budget_range', 'N/A')}")
        print(f"⏰ Decision Timeline: {behavioral.get('decision_timeline', 'N/A')}")
        print(f"🔑 Key Motivators: {', '.join(behavioral.get('key_motivators', []))}")
        print(f"🚫 Pain Points: {', '.join(behavioral.get('pain_points', []))}")
        print(f"📊 Purchase Probability: {behavioral.get('purchase_probability', 'N/A')}")
    
    # Display Candidates
    if final_data.get("candidates"):
        print("\n👥 TOP CANDIDATES:")
        print("-" * 30)
        candidates = final_data["candidates"]
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n🥇 CANDIDATE #{i}")
            print(f"   👤 Name: {candidate.get('name', 'N/A')}")
            print(f"   💼 Title: {candidate.get('title', 'N/A')}")
            print(f"   🏢 Company: {candidate.get('company', 'N/A')}")
            print(f"   📧 Email: {candidate.get('email', 'N/A')}")
            print(f"   📊 Accuracy Score: {candidate.get('accuracy', 'N/A')}%")
            
            if candidate.get('reasons'):
                print(f"   💡 Selection Reasons:")
                for reason in candidate['reasons']:
                    print(f"      • {reason}")
            
            # LinkedIn Profile Data
            if candidate.get('linkedin_profile'):
                profile = candidate['linkedin_profile']
                print(f"   🔗 LinkedIn Profile:")
                print(f"      • Headline: {profile.get('headline', 'N/A')}")
                print(f"      • Location: {profile.get('location', 'N/A')}")
                print(f"      • Followers: {profile.get('followers_count', 'N/A')}")
                print(f"      • Experience: {len(profile.get('experience', []))} positions")
            
            # LinkedIn Posts
            if candidate.get('linkedin_posts'):
                posts = candidate['linkedin_posts']
                print(f"   📝 Recent Posts ({len(posts)} found):")
                for j, post in enumerate(posts[:3], 1):  # Show top 3 posts
                    print(f"      {j}. {post.get('title', 'N/A')[:100]}...")
    
    # Display Timing
    if final_data.get("completed_at"):
        created = datetime.fromisoformat(final_data["created_at"].replace('Z', '+00:00'))
        completed = datetime.fromisoformat(final_data["completed_at"].replace('Z', '+00:00'))
        duration = completed - created
        print(f"\n⏱️  Total Processing Time: {duration.total_seconds():.1f} seconds")
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_real_prompt() 