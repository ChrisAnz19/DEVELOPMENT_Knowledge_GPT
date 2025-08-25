#!/usr/bin/env python3
"""
API Integration Patch for URL Evidence Finder.

This file contains the modifications needed to integrate the URL Evidence Finder
into the existing API. It shows exactly where to add the evidence enhancement
in the process_search function.
"""

# Add this import at the top of api/main.py (around line 30)
IMPORT_TO_ADD = """
# Import evidence integration
try:
    from evidence_integration import enhance_candidates_with_evidence_urls, get_evidence_integration_stats
    EVIDENCE_INTEGRATION_AVAILABLE = True
    print("[API] Evidence integration module loaded successfully")
except ImportError as e:
    EVIDENCE_INTEGRATION_AVAILABLE = False
    print(f"[API] Evidence integration not available: {e}")
"""

# Add this function to api/main.py (around line 1340, before the demo endpoints)
NEW_ENDPOINT_TO_ADD = """
@app.get("/api/evidence/stats")
async def get_evidence_stats():
    \"\"\"Get evidence integration statistics and performance metrics.\"\"\"
    try:
        if not EVIDENCE_INTEGRATION_AVAILABLE:
            return {
                "enabled": False,
                "error": "Evidence integration module not available"
            }
        
        stats = get_evidence_integration_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get evidence stats: {str(e)}")
"""

# Modify the process_search function - add this code after the behavioral data enhancement
# (around line 1280, after the behavioral_data processing and before storing to database)
EVIDENCE_ENHANCEMENT_CODE = """
        # Enhance candidates with evidence URLs (new feature)
        if EVIDENCE_INTEGRATION_AVAILABLE and candidates:
            try:
                print(f"[Evidence Enhancement] Processing {len(candidates)} candidates for evidence URLs")
                evidence_start_time = time.time()
                
                # Enhance candidates with evidence URLs
                candidates = await enhance_candidates_with_evidence_urls(candidates, prompt)
                
                evidence_processing_time = time.time() - evidence_start_time
                print(f"[Evidence Enhancement] Completed in {evidence_processing_time:.2f}s")
                
                # Log evidence statistics
                evidence_count = sum(len(c.get('evidence_urls', [])) for c in candidates if isinstance(c, dict))
                candidates_with_evidence = sum(1 for c in candidates if isinstance(c, dict) and c.get('evidence_urls'))
                
                print(f"[Evidence Enhancement] Found {evidence_count} total evidence URLs for {candidates_with_evidence}/{len(candidates)} candidates")
                
            except Exception as e:
                print(f"[Evidence Enhancement Error] Failed to enhance candidates with evidence: {str(e)}")
                # Continue processing without evidence URLs - don't fail the entire search
"""

# Configuration environment variables to add to deployment
ENVIRONMENT_VARIABLES = """
# Evidence Finder Configuration (add to environment variables)
EVIDENCE_FINDER_ENABLED=true
EVIDENCE_FINDER_CACHE=true
EVIDENCE_FINDER_ASYNC=true
EVIDENCE_MAX_CANDIDATES=10
EVIDENCE_TIMEOUT=30
EVIDENCE_CACHE_SIZE=1000
EVIDENCE_MIN_EXPLANATION_LENGTH=10
EVIDENCE_REQUIRE_BEHAVIORAL=false
"""

def show_integration_instructions():
    """Show step-by-step integration instructions."""
    print("URL Evidence Finder - API Integration Instructions")
    print("=" * 60)
    
    print("\n1. Add Import Statement")
    print("   Add this import near the top of api/main.py (around line 30):")
    print(IMPORT_TO_ADD)
    
    print("\n2. Add Evidence Stats Endpoint")
    print("   Add this endpoint to api/main.py (around line 1340, before demo endpoints):")
    print(NEW_ENDPOINT_TO_ADD)
    
    print("\n3. Integrate Evidence Enhancement")
    print("   Add this code in the process_search function (around line 1280):")
    print("   Insert AFTER behavioral data processing and BEFORE database storage:")
    print(EVIDENCE_ENHANCEMENT_CODE)
    
    print("\n4. Environment Configuration")
    print("   Add these environment variables to your deployment:")
    print(ENVIRONMENT_VARIABLES)
    
    print("\n5. Test the Integration")
    print("   After making these changes:")
    print("   - Restart the API server")
    print("   - Make a search request")
    print("   - Check the response for 'evidence_urls' field in candidates")
    print("   - Visit /api/evidence/stats to see performance metrics")
    
    print("\n6. Backward Compatibility")
    print("   - Existing API clients will continue to work unchanged")
    print("   - New 'evidence_urls' field is added to candidate objects")
    print("   - If evidence finding fails, candidates are returned without evidence URLs")
    print("   - Feature can be disabled via EVIDENCE_FINDER_ENABLED=false")


def create_integration_example():
    """Create an example of the integrated API response."""
    example_response = {
        "request_id": "12345-67890",
        "status": "completed",
        "candidates": [
            {
                "id": 1,
                "name": "John Doe",
                "title": "VP of Sales",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "reasons": [
                    "Currently researching Salesforce pricing options for enterprise deployment",
                    "Actively comparing CRM solutions including HubSpot and Microsoft Dynamics"
                ],
                "behavioral_data": {
                    "behavioral_insight": "Shows strong interest in CRM technology evaluation",
                    "scores": {"cmi": 0.85, "rbfs": 0.78, "ias": 0.82}
                },
                # NEW: Evidence URLs field
                "evidence_urls": [
                    {
                        "url": "https://www.salesforce.com/products/platform/pricing/",
                        "title": "Salesforce Platform Pricing | Plans & Packages",
                        "description": "Official Salesforce pricing page showing current plans and costs",
                        "evidence_type": "pricing_page",
                        "relevance_score": 0.95,
                        "confidence_level": "high",
                        "supporting_explanation": "Directly supports claim about researching Salesforce pricing options"
                    },
                    {
                        "url": "https://www.g2.com/categories/crm",
                        "title": "Best CRM Software 2024 | G2",
                        "description": "Comprehensive CRM comparison and reviews",
                        "evidence_type": "comparison_site",
                        "relevance_score": 0.88,
                        "confidence_level": "high",
                        "supporting_explanation": "Supports claim about comparing CRM solutions"
                    }
                ],
                # NEW: Evidence summary fields
                "evidence_summary": "Found 2 supporting URLs including official pricing pages and product documentation",
                "evidence_confidence": 0.87,
                "evidence_processing_time": 2.3
            }
        ]
    }
    
    print("\nExample Enhanced API Response:")
    print("=" * 40)
    import json
    print(json.dumps(example_response, indent=2))


if __name__ == '__main__':
    show_integration_instructions()
    create_integration_example()