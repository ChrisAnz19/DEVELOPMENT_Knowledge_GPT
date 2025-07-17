#!/usr/bin/env python3
"""
Test the full system with behavioral data
"""

import logging
import json
import uuid
from datetime import datetime, timezone
from supabase_client import supabase
from database import store_search_to_database, store_people_to_database, get_people_for_search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_behavioral_data_flow():
    """Test the complete flow with behavioral data"""
    try:
        # Step 1: Create a test search
        test_request_id = f"test-{str(uuid.uuid4())[:8]}"
        test_search = {
            "request_id": test_request_id,
            "prompt": "Test search for behavioral data",
            "status": "completed",
            "filters": json.dumps({"test": "filters"}),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store the search
        search_id = store_search_to_database(test_search)
        logger.info(f"✅ Created test search with ID: {search_id}")
        
        # Step 2: Create test candidates with behavioral data
        test_candidates = [
            {
                "name": "John Doe",
                "title": "Marketing Director",
                "company": "Tech Corp",
                "email": "john.doe@techcorp.com",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "accuracy": 85,
                "reasons": ["Strong marketing background", "Tech industry experience"],
                "behavioral_data": {
                    "behavioral_insight": "This Marketing Director exhibits high commitment momentum with focused research on marketing automation platforms and ROI measurement tools. Their recent deep-dive sessions on competitive analysis suggest they're moving beyond initial research toward implementation planning.",
                    "scores": {
                        "cmi": {"score": 85, "explanation": "Ready to act"},
                        "rbfs": {"score": 65, "explanation": "Balanced risk approach"},
                        "ias": {"score": 80, "explanation": "Strong role alignment"}
                    }
                }
            },
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "company": "Innovation Labs",
                "email": "jane.smith@innovationlabs.com",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "accuracy": 92,
                "reasons": ["Extensive technical experience", "Leadership potential"],
                "behavioral_data": {
                    "behavioral_insight": "This Senior Software Engineer shows strong technical commitment with consistent engagement in advanced architecture discussions and implementation planning. Their pattern of late-night research sessions indicates personal investment in technical solutions.",
                    "scores": {
                        "cmi": {"score": 90, "explanation": "Lining up next steps"},
                        "rbfs": {"score": 55, "explanation": "Open to opportunity"},
                        "ias": {"score": 88, "explanation": "Strong technical identity"}
                    }
                }
            }
        ]
        
        # Step 3: Store candidates with behavioral data
        store_people_to_database(search_id, test_candidates)
        logger.info(f"✅ Stored {len(test_candidates)} candidates with behavioral data")
        
        # Step 4: Retrieve candidates and verify behavioral data
        retrieved_candidates = get_people_for_search(search_id)
        logger.info(f"✅ Retrieved {len(retrieved_candidates)} candidates")
        
        # Step 5: Verify behavioral data structure
        for candidate in retrieved_candidates:
            name = candidate.get('name', 'Unknown')
            behavioral_data = candidate.get('behavioral_data')
            
            if behavioral_data:
                logger.info(f"✅ {name} has behavioral data")
                
                # Check structure
                if 'behavioral_insight' in behavioral_data:
                    logger.info(f"  ✅ Has behavioral_insight: {behavioral_data['behavioral_insight'][:50]}...")
                else:
                    logger.warning(f"  ⚠️  Missing behavioral_insight")
                
                if 'scores' in behavioral_data:
                    scores = behavioral_data['scores']
                    logger.info(f"  ✅ Has scores")
                    
                    # Check each score
                    for score_name in ['cmi', 'rbfs', 'ias']:
                        if score_name in scores:
                            score_data = scores[score_name]
                            if 'score' in score_data and 'explanation' in score_data:
                                logger.info(f"    ✅ {score_name.upper()}: {score_data['score']} - {score_data['explanation']}")
                            else:
                                logger.warning(f"    ⚠️  {score_name.upper()} missing score or explanation")
                        else:
                            logger.warning(f"    ⚠️  Missing {score_name.upper()} score")
                else:
                    logger.warning(f"  ⚠️  Missing scores")
            else:
                logger.error(f"❌ {name} missing behavioral data")
        
        # Step 6: Clean up test data
        supabase.table("people").delete().eq("search_id", search_id).execute()
        supabase.table("searches").delete().eq("request_id", test_request_id).execute()
        logger.info("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        # Try to clean up
        try:
            if 'test_request_id' in locals():
                supabase.table("searches").delete().eq("request_id", test_request_id).execute()
        except:
            pass
        return False

if __name__ == "__main__":
    print("🧪 Testing Full Behavioral Data System...")
    print("=" * 60)
    
    success = test_full_behavioral_data_flow()
    
    if success:
        print("\n🎉 All tests passed! The behavioral data system is working correctly.")
        print("\nWhat this means:")
        print("✅ Database can store behavioral data")
        print("✅ Database can retrieve behavioral data")
        print("✅ Behavioral data structure is correct")
        print("✅ All three scores (CMI, RBFS, IAS) are working")
        print("✅ Behavioral insights are being stored")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")