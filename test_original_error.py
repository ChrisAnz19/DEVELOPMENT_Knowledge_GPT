#!/usr/bin/env python3
"""
Test to reproduce and verify the fix for the original error:
'bool' object has no attribute 'timeout'
"""

import asyncio

async def test_original_error_scenario():
    """Test the specific scenario that caused the original error."""
    print("Testing original error scenario...")
    
    try:
        from context_aware_evidence_finder import ContextAwareEvidenceFinder
        
        # Create evidence finder
        finder = ContextAwareEvidenceFinder(enable_diversity=True)
        
        # Set search context (similar to the original error scenario)
        search_prompt = "Find people at Heritage Health and Housing"
        finder.set_search_context(search_prompt)
        
        # Test candidates similar to the original error
        test_candidates = [
            {
                'id': 'test_1',
                'name': 'Valerie Tomaselli',
                'title': 'Executive',
                'company': 'Heritage Health and Housing',
                'behavioral_data': {
                    'behavioral_insight': 'Valerie is involved in strategic planning'
                }
            },
            {
                'id': 'test_2', 
                'name': 'Shlomo Landa',
                'title': 'Director',
                'company': 'Heritage Health and Housing',
                'behavioral_data': {
                    'behavioral_insight': 'Shlomo manages operations'
                }
            }
        ]
        
        print(f"Processing {len(test_candidates)} candidates...")
        
        # This should NOT crash with 'bool' object has no attribute 'timeout'
        results = await finder.process_candidates_batch(test_candidates)
        
        print(f"✅ SUCCESS: Processed {len(results)} candidates without error")
        
        # Check results
        for i, candidate in enumerate(results):
            name = candidate.get('name', 'Unknown')
            evidence_urls = candidate.get('evidence_urls', [])
            evidence_summary = candidate.get('evidence_summary', 'No summary')
            evidence_confidence = candidate.get('evidence_confidence', 0.0)
            
            print(f"  Candidate {i+1}: {name}")
            print(f"    Evidence URLs: {len(evidence_urls)}")
            print(f"    Evidence Summary: {evidence_summary}")
            print(f"    Evidence Confidence: {evidence_confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_original_error_scenario())
    if success:
        print("\n🎉 Original error has been FIXED!")
    else:
        print("\n❌ Original error still exists!")