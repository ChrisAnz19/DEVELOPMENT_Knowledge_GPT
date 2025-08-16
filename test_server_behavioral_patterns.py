#!/usr/bin/env python3
"""
Test script to verify the server is generating diverse behavioral patterns
without the problematic 'downloaded whitepaper' patterns.
"""

import requests
import json
import time

def test_server_behavioral_patterns(server_url):
    """Test the server to ensure it's generating diverse behavioral patterns."""
    
    print("TESTING SERVER BEHAVIORAL PATTERNS")
    print("="*80)
    print(f"Server URL: {server_url}")
    print("="*80)
    
    # Test prompts that previously generated problematic patterns
    test_prompts = [
        "Find me CMOs interested in CRM solutions",
        "Find me CTOs looking for cybersecurity software", 
        "Find me marketing directors interested in analytics platforms",
        "Find me sales managers looking for automation tools",
        "Find me executives interested in business intelligence"
    ]
    
    all_behavioral_reasons = []
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt}")
        print("-" * 60)
        
        try:
            # Create search request
            response = requests.post(
                f"{server_url}/api/search",
                json={"prompt": prompt, "max_candidates": 2},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code} - {response.text}")
                continue
            
            search_data = response.json()
            request_id = search_data.get("request_id")
            
            if not request_id:
                print("❌ No request_id returned")
                continue
            
            print(f"✅ Search created: {request_id}")
            
            # Wait for completion and get results
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    result_response = requests.get(f"{server_url}/api/search/{request_id}", timeout=10)
                    
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        
                        if result_data.get("status") == "completed":
                            candidates = result_data.get("candidates", [])
                            
                            if candidates:
                                print(f"✅ Found {len(candidates)} candidates")
                                
                                # Extract behavioral reasons
                                for j, candidate in enumerate(candidates, 1):
                                    name = candidate.get("name", "Unknown")
                                    title = candidate.get("title", "Unknown")
                                    reasons = candidate.get("reasons", [])
                                    
                                    print(f"\n  Candidate {j}: {name} - {title}")
                                    
                                    if reasons:
                                        print(f"  Behavioral Reasons:")
                                        for k, reason in enumerate(reasons, 1):
                                            print(f"    {k}. {reason}")
                                            all_behavioral_reasons.append(reason)
                                    else:
                                        print(f"  ⚠️  No behavioral reasons found")
                                
                                break
                            else:
                                print("⚠️  No candidates found")
                                break
                        
                        elif result_data.get("status") == "failed":
                            print(f"❌ Search failed: {result_data.get('error', 'Unknown error')}")
                            break
                        
                        else:
                            print(f"⏳ Status: {result_data.get('status', 'unknown')} (attempt {attempt + 1})")
                            time.sleep(2)
                    
                    else:
                        print(f"❌ Error getting results: {result_response.status_code}")
                        break
                        
                except requests.exceptions.Timeout:
                    print(f"⏳ Timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ Error: {e}")
                    break
            
            else:
                print("❌ Timeout waiting for results")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Analyze all collected behavioral reasons
    print(f"\n" + "="*80)
    print("BEHAVIORAL PATTERN ANALYSIS")
    print("="*80)
    
    if all_behavioral_reasons:
        print(f"Total behavioral reasons collected: {len(all_behavioral_reasons)}")
        
        # Check for problematic patterns
        problematic_patterns = [
            'downloaded', 'whitepaper', 'webinar', 'attended', 'viewed',
            'case study', 'implementation guide', 'newsletter'
        ]
        
        found_problems = {}
        for pattern in problematic_patterns:
            count = sum(1 for reason in all_behavioral_reasons if pattern.lower() in reason.lower())
            if count > 0:
                found_problems[pattern] = count
        
        if found_problems:
            print(f"\n❌ PROBLEMATIC PATTERNS FOUND:")
            for pattern, count in found_problems.items():
                print(f"  {count}x: '{pattern}'")
                # Show examples
                examples = [reason for reason in all_behavioral_reasons if pattern.lower() in reason.lower()]
                for example in examples[:2]:  # Show first 2 examples
                    print(f"    Example: {example}")
        else:
            print(f"\n✅ NO PROBLEMATIC PATTERNS FOUND!")
        
        # Show sample of diverse reasons
        print(f"\nSAMPLE BEHAVIORAL REASONS:")
        for i, reason in enumerate(all_behavioral_reasons[:5], 1):
            print(f"  {i}. {reason}")
        
        # Check uniqueness
        unique_reasons = len(set(all_behavioral_reasons))
        total_reasons = len(all_behavioral_reasons)
        diversity_percentage = (unique_reasons / total_reasons) * 100 if total_reasons > 0 else 0
        
        print(f"\nDIVERSITY METRICS:")
        print(f"  Unique reasons: {unique_reasons}/{total_reasons}")
        print(f"  Diversity percentage: {diversity_percentage:.1f}%")
        
        if diversity_percentage >= 90 and not found_problems:
            print(f"\n🎉 SUCCESS: Server is generating diverse, clean behavioral patterns!")
        elif not found_problems:
            print(f"\n✅ GOOD: No problematic patterns, but could improve diversity")
        else:
            print(f"\n⚠️  NEEDS ATTENTION: Problematic patterns still detected")
    
    else:
        print("❌ No behavioral reasons collected to analyze")
    
    print("="*80)

if __name__ == "__main__":
    # You can update this URL to match your server
    server_url = input("Enter server URL (e.g., https://your-server.com): ").strip()
    if not server_url:
        server_url = "http://localhost:8000"  # Default for local testing
    
    test_server_behavioral_patterns(server_url)