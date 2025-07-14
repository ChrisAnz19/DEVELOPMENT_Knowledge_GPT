#!/usr/bin/env python3
"""
Comprehensive test script for the Knowledge_GPT pipeline
Tests the entire flow from prompt entry to Supabase storage
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "https://knowledge-gpt-siuq.onrender.com"
LOCAL_API_BASE_URL = "http://localhost:8000"

# Test prompts
TEST_PROMPTS = [
    "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
    "Looking for marketing managers with experience in B2B SaaS and LinkedIn advertising",
    "Need data scientists with expertise in machine learning and Python, preferably with PhD degrees"
]

class PipelineTester:
    def __init__(self, use_local: bool = False):
        self.base_url = LOCAL_API_BASE_URL if use_local else API_BASE_URL
        self.test_results = []
        self.session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        self.log("Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check passed: {data}")
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Health check failed with exception: {e}", "ERROR")
            return False
    
    def test_database_stats(self) -> bool:
        """Test database statistics endpoint"""
        self.log("Testing database statistics endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/database/stats")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Database stats: {data}")
                return True
            else:
                self.log(f"❌ Database stats failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Database stats failed with exception: {e}", "ERROR")
            return False
    
    def test_search_creation(self, prompt: str) -> Optional[str]:
        """Test creating a new search"""
        self.log(f"Creating search with prompt: {prompt[:50]}...")
        try:
            payload = {
                "prompt": prompt,
                "max_candidates": 2,
                "include_linkedin": True,
                "include_posts": False
            }
            
            response = self.session.post(f"{self.base_url}/api/search", json=payload)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                self.log(f"✅ Search created successfully: {request_id}")
                return request_id
            else:
                self.log(f"❌ Search creation failed: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Search creation failed with exception: {e}", "ERROR")
            return None
    
    def poll_search_result(self, request_id: str, max_wait: int = 300) -> Optional[Dict[str, Any]]:
        """Poll for search result completion"""
        self.log(f"Polling for search result: {request_id}")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/api/search/{request_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    self.log(f"Search status: {status}")
                    
                    if status == "completed":
                        self.log(f"✅ Search completed successfully!")
                        return data
                    elif status == "failed":
                        error = data.get("error", "Unknown error")
                        self.log(f"❌ Search failed: {error}", "ERROR")
                        return data
                    elif status == "processing":
                        self.log("Search still processing...")
                    else:
                        self.log(f"Unknown status: {status}")
                        
                else:
                    self.log(f"❌ Failed to get search result: {response.status_code}", "ERROR")
                    return None
                    
            except Exception as e:
                self.log(f"❌ Exception while polling: {e}", "ERROR")
                return None
                
            time.sleep(10)  # Wait 10 seconds between polls
            
        self.log(f"❌ Search timed out after {max_wait} seconds", "ERROR")
        return None
    
    def test_search_listing(self) -> bool:
        """Test listing all searches"""
        self.log("Testing search listing endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/search")
            if response.status_code == 200:
                data = response.json()
                searches = data.get("searches", [])
                self.log(f"✅ Found {len(searches)} searches")
                return True
            else:
                self.log(f"❌ Search listing failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Search listing failed with exception: {e}", "ERROR")
            return False
    
    def test_exclusions_endpoint(self) -> bool:
        """Test exclusions endpoint"""
        self.log("Testing exclusions endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/exclusions")
            if response.status_code == 200:
                data = response.json()
                exclusions = data.get("exclusions", [])
                self.log(f"✅ Found {len(exclusions)} active exclusions")
                return True
            else:
                self.log(f"❌ Exclusions endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Exclusions endpoint failed with exception: {e}", "ERROR")
            return False
    
    def test_json_endpoint(self, request_id: str) -> bool:
        """Test JSON file endpoint"""
        self.log(f"Testing JSON endpoint for: {request_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/search/{request_id}/json")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ JSON endpoint working, data size: {len(str(data))} chars")
                return True
            else:
                self.log(f"❌ JSON endpoint failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ JSON endpoint failed with exception: {e}", "ERROR")
            return False
    
    def test_search_deletion(self, request_id: str) -> bool:
        """Test search deletion"""
        self.log(f"Testing search deletion for: {request_id}")
        try:
            response = self.session.delete(f"{self.base_url}/api/search/{request_id}")
            if response.status_code == 200:
                self.log(f"✅ Search deleted successfully")
                return True
            else:
                self.log(f"❌ Search deletion failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Search deletion failed with exception: {e}", "ERROR")
            return False
    
    def run_full_pipeline_test(self) -> Dict[str, Any]:
        """Run the complete pipeline test"""
        self.log("🚀 Starting comprehensive pipeline test...")
        
        test_summary = {
            "start_time": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tests": 0,
            "results": []
        }
        
        # Test 1: Health check
        test_summary["total_tests"] += 1
        if self.test_health_check():
            test_summary["tests_passed"] += 1
            test_summary["results"].append({"test": "health_check", "status": "PASSED"})
        else:
            test_summary["tests_failed"] += 1
            test_summary["results"].append({"test": "health_check", "status": "FAILED"})
        
        # Test 2: Database stats
        test_summary["total_tests"] += 1
        if self.test_database_stats():
            test_summary["tests_passed"] += 1
            test_summary["results"].append({"test": "database_stats", "status": "PASSED"})
        else:
            test_summary["tests_failed"] += 1
            test_summary["results"].append({"test": "database_stats", "status": "FAILED"})
        
        # Test 3: Search listing
        test_summary["total_tests"] += 1
        if self.test_search_listing():
            test_summary["tests_passed"] += 1
            test_summary["results"].append({"test": "search_listing", "status": "PASSED"})
        else:
            test_summary["tests_failed"] += 1
            test_summary["results"].append({"test": "search_listing", "status": "FAILED"})
        
        # Test 4: Exclusions endpoint
        test_summary["total_tests"] += 1
        if self.test_exclusions_endpoint():
            test_summary["tests_passed"] += 1
            test_summary["results"].append({"test": "exclusions_endpoint", "status": "PASSED"})
        else:
            test_summary["tests_failed"] += 1
            test_summary["results"].append({"test": "exclusions_endpoint", "status": "FAILED"})
        
        # Test 5: Full search pipeline
        self.log("🧪 Testing full search pipeline...")
        for i, prompt in enumerate(TEST_PROMPTS[:1]):  # Test with first prompt only
            self.log(f"Testing prompt {i+1}: {prompt[:50]}...")
            
            # Create search
            request_id = self.test_search_creation(prompt)
            if request_id:
                test_summary["total_tests"] += 1
                test_summary["tests_passed"] += 1
                test_summary["results"].append({"test": f"search_creation_{i+1}", "status": "PASSED", "request_id": request_id})
                
                # Poll for completion
                result = self.poll_search_result(request_id)
                if result and result.get("status") == "completed":
                    test_summary["total_tests"] += 1
                    test_summary["tests_passed"] += 1
                    test_summary["results"].append({"test": f"search_completion_{i+1}", "status": "PASSED", "request_id": request_id})
                    
                    # Test JSON endpoint
                    if self.test_json_endpoint(request_id):
                        test_summary["total_tests"] += 1
                        test_summary["tests_passed"] += 1
                        test_summary["results"].append({"test": f"json_endpoint_{i+1}", "status": "PASSED", "request_id": request_id})
                    else:
                        test_summary["total_tests"] += 1
                        test_summary["tests_failed"] += 1
                        test_summary["results"].append({"test": f"json_endpoint_{i+1}", "status": "FAILED", "request_id": request_id})
                    
                    # Test deletion
                    if self.test_search_deletion(request_id):
                        test_summary["total_tests"] += 1
                        test_summary["tests_passed"] += 1
                        test_summary["results"].append({"test": f"search_deletion_{i+1}", "status": "PASSED", "request_id": request_id})
                    else:
                        test_summary["total_tests"] += 1
                        test_summary["tests_failed"] += 1
                        test_summary["results"].append({"test": f"search_deletion_{i+1}", "status": "FAILED", "request_id": request_id})
                        
                else:
                    test_summary["total_tests"] += 1
                    test_summary["tests_failed"] += 1
                    test_summary["results"].append({"test": f"search_completion_{i+1}", "status": "FAILED", "request_id": request_id})
            else:
                test_summary["total_tests"] += 1
                test_summary["tests_failed"] += 1
                test_summary["results"].append({"test": f"search_creation_{i+1}", "status": "FAILED"})
        
        test_summary["end_time"] = datetime.now().isoformat()
        test_summary["success_rate"] = (test_summary["tests_passed"] / test_summary["total_tests"]) * 100 if test_summary["total_tests"] > 0 else 0
        
        return test_summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary"""
        self.log("=" * 60)
        self.log("📊 TEST SUMMARY")
        self.log("=" * 60)
        self.log(f"Start Time: {summary['start_time']}")
        self.log(f"End Time: {summary['end_time']}")
        self.log(f"Total Tests: {summary['total_tests']}")
        self.log(f"Tests Passed: {summary['tests_passed']}")
        self.log(f"Tests Failed: {summary['tests_failed']}")
        self.log(f"Success Rate: {summary['success_rate']:.1f}%")
        
        self.log("\n📋 DETAILED RESULTS:")
        for result in summary["results"]:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            self.log(f"{status_emoji} {result['test']}: {result['status']}")
            if "request_id" in result:
                self.log(f"   Request ID: {result['request_id']}")
        
        self.log("=" * 60)
        
        if summary["success_rate"] >= 80:
            self.log("🎉 Pipeline test completed successfully!")
        elif summary["success_rate"] >= 60:
            self.log("⚠️  Pipeline test completed with some issues")
        else:
            self.log("💥 Pipeline test failed - significant issues detected")

def main():
    """Main function"""
    print("Knowledge_GPT Pipeline Test Suite")
    print("=" * 50)
    
    # Check if user wants to test local or deployed API
    use_local = "--local" in sys.argv
    
    if use_local:
        print("Testing LOCAL API (http://localhost:8000)")
    else:
        print("Testing DEPLOYED API (https://knowledge-gpt-siuq.onrender.com)")
    
    print("\nStarting comprehensive pipeline test...")
    print("This will test:")
    print("- Health check endpoint")
    print("- Database statistics")
    print("- Search creation and processing")
    print("- Result polling and completion")
    print("- JSON file endpoints")
    print("- Search deletion")
    print("- Exclusions system")
    print("\n" + "=" * 50)
    
    # Run the test
    tester = PipelineTester(use_local=use_local)
    summary = tester.run_full_pipeline_test()
    
    # Print results
    tester.print_summary(summary)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pipeline_test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {filename}")
    
    # Exit with appropriate code
    if summary["success_rate"] >= 80:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 