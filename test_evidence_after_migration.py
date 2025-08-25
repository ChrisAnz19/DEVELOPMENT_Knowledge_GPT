#!/usr/bin/env python3
"""
Test script to verify evidence system works after database migration.
Run this AFTER applying the evidence_migration.sql to your database.
"""

import json
from database import store_people_to_database, get_people_for_search

def test_evidence_flow():
    """Test the complete evidence flow: store -> retrieve -> verify."""
    
    print("🧪 Testing Evidence Flow After Migration")
    print("=" * 50)
    
    # Test data with evidence URLs
    test_candidates = [
        {
            "name": "Test Person 1",
            "title": "CRM Manager", 
            "company": "TestCorp",
            "accuracy": 85,
            "evidence_urls": [
                {
                    "url": "https://www.salesforce.com/products/crm/",
                    "title": "Salesforce CRM Solutions",
                    "relevance_score": 0.9,
                    "source_type": "product_page"
                },
                {
                    "url": "https://www.hubspot.com/products/crm",
                    "title": "HubSpot CRM Platform", 
                    "relevance_score": 0.8,
                    "source_type": "product_page"
                }
            ],
            "evidence_summary": "Found 2 supporting evidence URLs",
            "evidence_confidence": 0.85
        }
    ]
    
    test_search_id = 999999  # Use a test search ID
    
    print(f"📝 Storing test candidate with {len(test_candidates[0]['evidence_urls'])} evidence URLs...")
    
    try:
        # Store the test data
        store_result = store_people_to_database(test_search_id, test_candidates)
        print(f"✅ Store result: {store_result}")
        
        if store_result:
            print("📖 Retrieving stored data...")
            
            # Retrieve the data
            retrieved_people = get_people_for_search(test_search_id)
            print(f"✅ Retrieved {len(retrieved_people)} people")
            
            if retrieved_people:
                person = retrieved_people[0]
                evidence_urls = person.get('evidence_urls', [])
                
                print(f"\n🔍 Evidence Data Check:")
                print(f"  Evidence URLs type: {type(evidence_urls)}")
                print(f"  Evidence URLs count: {len(evidence_urls) if isinstance(evidence_urls, list) else 'Not a list'}")
                print(f"  Evidence summary: {person.get('evidence_summary', 'None')}")
                print(f"  Evidence confidence: {person.get('evidence_confidence', 'None')}")
                
                if isinstance(evidence_urls, list) and len(evidence_urls) > 0:
                    print(f"  First evidence URL: {evidence_urls[0]}")
                    print("🎉 SUCCESS: Evidence URLs are properly stored and retrieved as arrays!")
                    
                    # Clean up test data
                    print("\n🧹 Cleaning up test data...")
                    from supabase_client import supabase
                    supabase.table("people").delete().eq("search_id", test_search_id).execute()
                    print("✅ Test data cleaned up")
                    
                    return True
                else:
                    print("❌ FAILED: Evidence URLs are not properly formatted")
                    return False
            else:
                print("❌ FAILED: No people retrieved")
                return False
        else:
            print("❌ FAILED: Could not store test data")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_evidence_flow()
    
    if success:
        print("\n🎉 Evidence system is working correctly!")
        print("The frontend should now receive evidence URLs as arrays.")
    else:
        print("\n❌ Evidence system test failed.")
        print("Check that the database migration was applied correctly.")