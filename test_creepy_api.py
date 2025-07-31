#!/usr/bin/env python3
"""
Test the creepy detection in the API
"""

import requests
import json
import time

# Test cases
test_cases = [
    {
        "prompt": "Find me marketing directors in New York",
        "should_be_blocked": False,
        "description": "Legitimate professional search - no names"
    },
    {
        "prompt": "What is John Smith looking for?",
        "should_be_blocked": True,
        "description": "Contains full name - blocked in ultra strict mode"
    },
    {
        "prompt": "Is Jane Doe looking for a divorce attorney?",
        "should_be_blocked": True,
        "description": "Contains full name - blocked in ultra strict mode"
    },
    {
        "prompt": "Find me a John Smith who works in sales",
        "should_be_blocked": True,
        "description": "Contains full name - blocked in ultra strict mode"
    },
    {
        "prompt": "Tell me about Mike Johnson's interests",
        "should_be_blocked": True,
        "description": "Contains full name - blocked in ultra strict mode"
    },
    {
        "prompt": "Looking for software engineers named David",
        "should_be_blocked": True,
        "description": "Contains first name - blocked in ultra strict mode"
    },
    {
        "prompt": "Find me CEOs in San Francisco",
        "should_be_blocked": False,
        "description": "Professional search with location - no names"
    },
    {
        "prompt": "Looking for Mary Johnson in marketing",
        "should_be_blocked": True,
        "description": "Contains full name - blocked in ultra strict mode"
    },
    {
        "prompt": "Get me Sarah from marketing",
        "should_be_blocked": True,
        "description": "Contains first name - blocked in ultra strict mode"
    },
    {
        "prompt": "Show me professionals in finance",
        "should_be_blocked": False,
        "description": "Professional search - no names"
    }
]

def test_api_endpoint(base_url="http://localhost:8000"):
    """Test the API with various prompts"""
    
    print("🧪 Testing Creepy Detection in API...")
    print(f"📡 API Base URL: {base_url}")
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Testing: '{test_case['prompt']}'")
        print(f"   Expected: {'BLOCKED' if test_case['should_be_blocked'] else 'ALLOWED'}")
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/api/search",
                json={
                    "prompt": test_case["prompt"],
                    "max_candidates": 3
                },
                timeout=10
            )
            
            if response.status_code == 400:
                # Check if it's a creepy detection
                error_detail = response.json().get("detail", "")
                if "creepy" in error_detail.lower() or "stalking" in error_detail.lower():
                    print(f"   🚨 BLOCKED (Creepy): {error_detail}")
                    results.append({
                        "test": test_case["prompt"],
                        "expected_blocked": test_case["should_be_blocked"],
                        "actually_blocked": True,
                        "reason": "Creepy detection",
                        "response": error_detail,
                        "correct": test_case["should_be_blocked"]
                    })
                else:
                    print(f"   ❌ BLOCKED (Other): {error_detail}")
                    results.append({
                        "test": test_case["prompt"],
                        "expected_blocked": test_case["should_be_blocked"],
                        "actually_blocked": True,
                        "reason": "Other validation",
                        "response": error_detail,
                        "correct": False
                    })
            elif response.status_code == 200:
                print(f"   ✅ ALLOWED: Search created successfully")
                results.append({
                    "test": test_case["prompt"],
                    "expected_blocked": test_case["should_be_blocked"],
                    "actually_blocked": False,
                    "reason": "Allowed",
                    "response": "Search created",
                    "correct": not test_case["should_be_blocked"]
                })
            else:
                print(f"   ⚠️  Unexpected status: {response.status_code}")
                results.append({
                    "test": test_case["prompt"],
                    "expected_blocked": test_case["should_be_blocked"],
                    "actually_blocked": False,
                    "reason": f"HTTP {response.status_code}",
                    "response": response.text,
                    "correct": False
                })
                
        except requests.exceptions.RequestException as e:
            print(f"   💥 Request failed: {e}")
            results.append({
                "test": test_case["prompt"],
                "expected_blocked": test_case["should_be_blocked"],
                "actually_blocked": False,
                "reason": "Request failed",
                "response": str(e),
                "correct": False
            })
    
    # Summary
    print("\n📊 Test Results Summary:")
    correct_count = sum(1 for r in results if r["correct"])
    total_count = len(results)
    
    print(f"✅ Correct: {correct_count}/{total_count}")
    print(f"❌ Incorrect: {total_count - correct_count}/{total_count}")
    
    if correct_count == total_count:
        print("🎉 All tests passed! Creepy detection is working perfectly.")
    else:
        print("💥 Some tests failed. Check the results above.")
        
        # Show failed tests
        failed_tests = [r for r in results if not r["correct"]]
        for failed in failed_tests:
            print(f"   ❌ '{failed['test']}' - Expected: {'BLOCKED' if failed['expected_blocked'] else 'ALLOWED'}, Got: {'BLOCKED' if failed['actually_blocked'] else 'ALLOWED'}")

if __name__ == "__main__":
    print("🚀 Make sure the API server is running on localhost:8000")
    print("   Start it with: cd api && python3 main.py")
    input("Press Enter when ready to test...")
    
    test_api_endpoint()