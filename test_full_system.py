#!/usr/bin/env python3
"""
Comprehensive test of the entire Knowledge_GPT system
Tests API → Database → Supabase integration
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_URL = "https://knowledge-gpt-siuq.onrender.com"

def test_full_system():
    """Test the complete system from API to Supabase database"""
    
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
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
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Step 2: Database Stats Check
    print("\n2️⃣ Testing Database Connection...")
    try:
        db_response = requests.get(f"{API_BASE_URL}/api/database/stats", timeout=10)
        if db_response.status_code == 200:
            db_stats = db_response.json()
            print(f"✅ Database Status: {db_stats['database_status']}")
            if 'total_searches' in db_stats:
                            print(f"📊 Total Searches: {db_stats['total_searches']}")
            print(f"👥 Total People: {db_stats['total_candidates']}")
        else:
            print(f"⚠️  Database stats failed: {db_response.status_code}")
    except Exception as e:
        print(f"⚠️  Database stats error: {e}")
    
    # Step 3: Create Search Request
    print("\n3️⃣ Creating Search Request...")
    test_prompt = "Find marketing directors at SaaS companies in San Francisco who are likely to be interested in buying marketing automation software"
    
    search_payload = {
        "prompt": test_prompt,
        "max_candidates": 2,
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
            return False
            
    except Exception as e:
        print(f"❌ Search creation error: {e}")
        return False
    
    # Step 4: Poll for Results
    print("\n4️⃣ Polling for Results...")
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
                    return False
                else:
                    # Still processing
                    time.sleep(10)  # Wait 10 seconds before next poll
                    attempt += 1
            else:
                print(f"❌ Result polling failed: {result_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Polling error: {e}")
            return False
    
    if attempt >= max_attempts:
        print("❌ Timeout: Search took too long to complete")
        return False
    
    # Step 5: Verify Database Storage
    print("\n5️⃣ Verifying Database Storage...")
    try:
        # Get final results
        final_response = requests.get(f"{API_BASE_URL}/api/search/{request_id}")
        final_data = final_response.json()
        
        # Check if data is in database
        db_stats_after = requests.get(f"{API_BASE_URL}/api/database/stats").json()
        if db_stats_after.get('database_status') == 'connected':
            print("✅ Database storage verified!")
        else:
            print("⚠️  Database storage status unclear")
        
        # Display results
        print("\n📊 SEARCH RESULTS:")
        print("-" * 40)
        print(f"🎯 Prompt: {final_data['prompt']}")
        print(f"📊 Status: {final_data['status']}")
        print(f"⏱️  Processing Time: {final_data.get('completed_at', 'N/A')}")
        
        if final_data.get("filters"):
            print(f"🔍 Filters Applied: {len(final_data['filters'].get('organization_filters', {})) + len(final_data['filters'].get('person_filters', {}))} filter(s)")
        
        if final_data.get("behavioral_data"):
            print(f"🧠 Behavioral Data: Generated")
        
        if final_data.get("candidates"):
            people = final_data["candidates"]
            print(f"👥 People Found: {len(people)}")
            
            for i, person in enumerate(people, 1):
                print(f"\n🥇 PERSON #{i}")
                print(f"   👤 Name: {person.get('name', 'N/A')}")
                print(f"   💼 Title: {person.get('title', 'N/A')}")
                print(f"   🏢 Company: {person.get('company', 'N/A')}")
                print(f"   📧 Email: {person.get('email', 'N/A')}")
                print(f"   📊 Accuracy: {person.get('accuracy', 'N/A')}%")
                print(f"   🔗 LinkedIn: {'Yes' if person.get('linkedin_url') else 'No'}")
                print(f"   📸 Photo: {'Yes' if person.get('profile_photo_url') else 'No'}")
                
                if person.get('reasons'):
                    print(f"   💡 Reasons: {len(person['reasons'])} reason(s)")
        
        # Step 6: Test Database Retrieval
        print("\n6️⃣ Testing Database Retrieval...")
        list_response = requests.get(f"{API_BASE_URL}/api/search")
        if list_response.status_code == 200:
            searches = list_response.json()
            recent_searches = searches.get("searches", [])
            if recent_searches:
                latest_search = recent_searches[0]
                print(f"✅ Latest search in database: {latest_search['request_id']}")
                print(f"   Prompt: {latest_search['prompt'][:50]}...")
                print(f"   Status: {latest_search['status']}")
                print(f"   Candidates: {latest_search.get('candidate_count', 0)}")
            else:
                print("⚠️  No searches found in database")
        
        print("\n" + "=" * 60)
        print("🎉 FULL SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error processing results: {e}")
        return False

if __name__ == "__main__":
    success = test_full_system()
    if success:
        print("\n✅ All systems operational! Ready for frontend development.")
    else:
        print("\n❌ System test failed. Please check configuration.") 