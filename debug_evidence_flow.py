#!/usr/bin/env python3
"""
Debug script to test the complete evidence finding flow.
"""

import asyncio
import os
import json
from enhanced_url_evidence_finder import EnhancedURLEvidenceFinder

# Load API keys
if not os.getenv('OPENAI_API_KEY'):
    try:
        with open("secrets.json", "r") as f:
            secrets = json.load(f)
            os.environ['OPENAI_API_KEY'] = secrets.get('openai_api_key', '') or secrets.get('OPENAI_API_KEY', '')
    except (FileNotFoundError, json.JSONDecodeError):
        pass

async def debug_evidence_flow():
    """Debug the complete evidence finding flow."""
    print("=== Debugging Complete Evidence Flow ===")
    
    # Test candidate with real estate behavioral reasons (matching the logs)
    test_candidate = {
        'id': '61094af3bb061c0001ccdd4f',
        'name': 'Mike Bennyhoff',
        'title': 'CEO',
        'company': 'Bennyhoff Products And Services LLC',
        'behavioral_data': {
            'behavioral_insight': 'Frequently visited luxury real estate websites and seems to prioritize properties with unique features and hidden gems',
            'scores': {'cmi': 85, 'rbfs': 78, 'ias': 82}
        }
    }
    
    print(f"Test candidate: {test_candidate['name']}")
    print(f"Behavioral insight: {test_candidate['behavioral_data']['behavioral_insight']}")
    
    # Initialize evidence finder
    evidence_finder = EnhancedURLEvidenceFinder(enable_diversity=True)
    
    # Configure for real estate
    evidence_finder.configure_diversity(
        ensure_uniqueness=True,
        max_same_domain=1,
        prioritize_alternatives=True,
        diversity_weight=0.4
    )
    
    print("\n=== Processing Candidate ===")
    
    try:
        # Process the candidate
        enhanced_candidate = await evidence_finder.process_candidate(test_candidate)
        
        print(f"Processing completed!")
        print(f"Enhanced candidate keys: {list(enhanced_candidate.keys())}")
        
        # Check for evidence URLs
        evidence_urls = enhanced_candidate.get('evidence_urls', [])
        print(f"Evidence URLs found: {len(evidence_urls)}")
        
        if evidence_urls:
            print("\nEvidence URLs:")
            for i, url_data in enumerate(evidence_urls, 1):
                if isinstance(url_data, dict):
                    url = url_data.get('url', 'N/A')
                    title = url_data.get('title', 'N/A')
                    confidence = url_data.get('confidence_level', 'N/A')
                else:
                    url = getattr(url_data, 'url', 'N/A')
                    title = getattr(url_data, 'title', 'N/A')
                    confidence = getattr(url_data, 'confidence_level', 'N/A')
                
                print(f"  {i}. {title} (confidence: {confidence})")
                print(f"     URL: {url}")
        else:
            print("No evidence URLs found!")
            
            # Check for error messages
            error_msg = enhanced_candidate.get('evidence_summary', '')
            if 'failed' in error_msg.lower() or 'error' in error_msg.lower():
                print(f"Error message: {error_msg}")
        
        # Get statistics
        stats = evidence_finder.get_enhanced_statistics()
        print(f"\nStatistics:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
                
    except Exception as e:
        print(f"Error processing candidate: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(debug_evidence_flow())