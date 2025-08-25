#!/usr/bin/env python3
"""
Debug script to test the evidence flow and see where URLs are getting lost.
"""

import asyncio
import json

async def test_evidence_flow():
    """Test the evidence enhancement flow step by step."""
    
    # Test candidate with real behavioral data
    test_candidate = {
        'id': 'test_1',
        'name': 'Luke Shardlow',
        'title': 'CRM Manager',
        'company': 'TechCorp',
        'behavioral_data': {
            'behavioral_insight': 'Luke is actively researching CRM solutions and has been comparing Salesforce pricing with HubSpot alternatives'
        }
    }
    
    print("=== TESTING EVIDENCE FLOW ===")
    print(f"Original candidate: {json.dumps(test_candidate, indent=2)}")
    
    try:
        from enhanced_url_evidence_finder import EnhancedURLEvidenceFinder
        
        # Initialize evidence finder
        evidence_finder = EnhancedURLEvidenceFinder(enable_diversity=True)
        evidence_finder.configure_diversity(
            ensure_uniqueness=True,
            max_same_domain=1,
            prioritize_alternatives=True,
            diversity_weight=0.4
        )
        
        print("\n=== PROCESSING WITH EVIDENCE FINDER ===")
        
        # Process the candidate
        enhanced_candidates = await evidence_finder.process_candidates_batch([test_candidate])
        
        print(f"\nEnhanced candidates returned: {len(enhanced_candidates)}")
        
        if enhanced_candidates:
            enhanced_candidate = enhanced_candidates[0]
            print(f"\nEnhanced candidate keys: {list(enhanced_candidate.keys())}")
            
            evidence_urls = enhanced_candidate.get('evidence_urls', [])
            print(f"Evidence URLs count: {len(evidence_urls)}")
            print(f"Evidence URLs type: {type(evidence_urls)}")
            
            if evidence_urls:
                print(f"First evidence URL: {evidence_urls[0]}")
            else:
                print("No evidence URLs found")
            
            print(f"Evidence summary: {enhanced_candidate.get('evidence_summary', 'None')}")
            print(f"Evidence confidence: {enhanced_candidate.get('evidence_confidence', 0)}")
            
            # Test the has_evidence check that the API uses
            has_evidence = bool(enhanced_candidate.get('evidence_urls'))
            print(f"\nAPI has_evidence check: {has_evidence}")
            
            return enhanced_candidate
        else:
            print("No enhanced candidates returned!")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = asyncio.run(test_evidence_flow())
    
    if result:
        print(f"\n=== FINAL RESULT ===")
        print(f"Evidence URLs: {len(result.get('evidence_urls', []))}")
        print(f"Has evidence: {bool(result.get('evidence_urls'))}")