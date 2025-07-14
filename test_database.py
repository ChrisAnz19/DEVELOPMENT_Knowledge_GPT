#!/usr/bin/env python3
"""
Test script for Supabase database connection and functionality
"""

import os
from dotenv import load_dotenv
from database import init_database, store_search_to_database, get_search_from_database

def test_database_connection():
    """Test the database connection and basic operations"""
    
    print("🧪 TESTING SUPABASE DATABASE CONNECTION")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    required_vars = ["SUPABASE_USER", "SUPABASE_PASSWORD", "SUPABASE_HOST", "SUPABASE_DBNAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        print("Please create a .env file with the following variables:")
        print("SUPABASE_USER=your_username")
        print("SUPABASE_PASSWORD=2ndSight@2023")
        print("SUPABASE_HOST=your_host")
        print("SUPABASE_DBNAME=your_database")
        return False
    
    print("✅ Environment variables loaded")
    
    # Test database initialization
    print("\n🔌 Testing database initialization...")
    if init_database():
        print("✅ Database initialized successfully!")
    else:
        print("❌ Database initialization failed!")
        return False
    
    # Test storing a sample search result
    print("\n💾 Testing search result storage...")
    sample_search = {
        "request_id": "test-123",
        "prompt": "Find marketing directors in San Francisco",
        "filters": {
            "organization_filters": {"organization_locations": ["San Francisco"]},
            "person_filters": {"person_titles": ["Marketing Director"]}
        },
        "behavioral_data": {
            "behavioral_insights": {
                "engagement_patterns": "High engagement with marketing automation tools"
            }
        },
        "candidates": [
            {
                "name": "John Doe",
                "title": "Marketing Director",
                "company": "Tech Corp",
                "email": "john@techcorp.com",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "profile_photo_url": "https://example.com/photo.jpg",
                "location": "San Francisco, CA",
                "accuracy": 85,
                "reasons": ["Frequent visits to marketing automation sites"],
                "linkedin_profile": {"headline": "Marketing Director at Tech Corp"},
                "linkedin_posts": []
            },
            {
                "name": "Jane Smith",
                "title": "Marketing Director",
                "company": "Startup Inc",
                "email": "jane@startup.com",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "profile_photo_url": "https://example.com/photo2.jpg",
                "location": "San Francisco, CA",
                "accuracy": 80,
                "reasons": ["Engagement with industry forums"],
                "linkedin_profile": {"headline": "Marketing Director at Startup Inc"},
                "linkedin_posts": []
            }
        ],
        "status": "completed",
        "created_at": "2025-01-14T05:00:00Z",
        "completed_at": "2025-01-14T05:01:00Z"
    }
    
    search_id = store_search_to_database(sample_search)
    if search_id:
        print(f"✅ Search result stored with ID: {search_id}")
    else:
        print("❌ Failed to store search result!")
        return False
    
    # Test retrieving the search result
    print("\n📖 Testing search result retrieval...")
    retrieved_search = get_search_from_database("test-123")
    if retrieved_search:
        print("✅ Search result retrieved successfully!")
        print(f"   Prompt: {retrieved_search['prompt']}")
        print(f"   Candidates: {len(retrieved_search['candidates'])}")
        for i, candidate in enumerate(retrieved_search['candidates'], 1):
            print(f"   Candidate {i}: {candidate['name']} - {candidate['title']} at {candidate['company']}")
    else:
        print("❌ Failed to retrieve search result!")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 DATABASE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_database_connection() 