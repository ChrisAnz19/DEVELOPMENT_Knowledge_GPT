#!/usr/bin/env python3
"""
Deployment diagnostic script to test HubSpot OAuth endpoints
in both local and deployed environments
"""

import asyncio
import httpx
import json
import sys
import os
from typing import Optional, Dict, Any

class OAuthEndpointTester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.results = {}
        self.prismatic_checks = {}
        
    async def test_endpoint(self, method: str, path: str, data: Optional[Dict] = None, 
                          headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Test a single endpoint and return results"""
        url = f"{self.base_url}{path}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == 'GET':
                    response = await client.get(url, headers=headers or {})
                elif method.upper() == 'POST':
                    response = await client.post(url, json=data, headers=headers or {})
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                result = {
                    "url": url,
                    "method": method.upper(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "response_size": len(response.content),
                    "success": 200 <= response.status_code < 300
                }
                
                # Try to parse JSON response
                try:
                    result["json_response"] = response.json()
                except:
                    result["text_response"] = response.text[:500]  # First 500 chars
                
                return result
                
        except Exception as e:
            return {
                "url": url,
                "method": method.upper(),
                "error": str(e),
                "success": False
            }
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        print(f"🔍 Testing OAuth endpoints at: {self.base_url}")
        print("=" * 60)
        
        # Test cases
        test_cases = [
            {
                "name": "Health Check",
                "method": "GET",
                "path": "/api/hubspot/oauth/health",
                "description": "Check if OAuth service is configured"
            },
            {
                "name": "Debug Info",
                "method": "GET", 
                "path": "/api/hubspot/oauth/debug",
                "description": "Get debug information about available routes"
            },
            {
                "name": "Test Endpoint",
                "method": "POST",
                "path": "/api/hubspot/oauth/test",
                "description": "Test JSON response format"
            },
            {
                "name": "Token Exchange (Invalid)",
                "method": "POST",
                "path": "/api/hubspot/oauth/token",
                "data": {"code": "test_code", "redirect_uri": "https://example.com/callback"},
                "description": "Test token exchange with invalid code"
            },
            {
                "name": "Token Exchange (Missing Data)",
                "method": "POST",
                "path": "/api/hubspot/oauth/token",
                "data": {},
                "description": "Test validation with missing required fields"
            },
            {
                "name": "Root Health",
                "method": "GET",
                "path": "/",
                "description": "Check if API server is running"
            },
            {
                "name": "Prismatic Diagnostics",
                "method": "GET",
                "path": "/api/system/prismatic/diagnostics",
                "description": "Comprehensive Prismatic integration diagnostics"
            }
        ]
        
        results = {
            "base_url": self.base_url,
            "timestamp": "2025-08-16T17:32:00Z",  # Will be updated
            "tests": {},
            "summary": {
                "total_tests": len(test_cases),
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
        
        # Run each test
        for test_case in test_cases:
            print(f"\n📋 {test_case['name']}: {test_case['description']}")
            
            result = await self.test_endpoint(
                method=test_case['method'],
                path=test_case['path'],
                data=test_case.get('data'),
                headers={"Content-Type": "application/json"}
            )
            
            results["tests"][test_case['name']] = result
            
            # Print result
            if result.get('success'):
                print(f"   ✅ {result['status_code']} - Success")
                results["summary"]["passed"] += 1
            elif 'error' in result:
                print(f"   ❌ Error: {result['error']}")
                results["summary"]["failed"] += 1
                results["summary"]["errors"].append(f"{test_case['name']}: {result['error']}")
            else:
                print(f"   ⚠️  {result['status_code']} - {result.get('text_response', 'No response')[:100]}")
                if result['status_code'] == 404:
                    results["summary"]["errors"].append(f"{test_case['name']}: 404 Not Found")
                results["summary"]["failed"] += 1
        
        return results
    
    async def analyze_404_issues(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze 404 errors and provide recommendations"""
        print(f"\n🔍 Analyzing 404 Issues...")
        print("=" * 40)
        
        analysis = {
            "found_404s": [],
            "missing_endpoints": [],
            "recommendations": []
        }
        
        # Check for 404s
        for test_name, result in results["tests"].items():
            if result.get('status_code') == 404:
                analysis["found_404s"].append({
                    "test": test_name,
                    "url": result['url'],
                    "method": result['method']
                })
        
        # Check if debug endpoint worked
        debug_result = results["tests"].get("Debug Info", {})
        if debug_result.get('success') and 'json_response' in debug_result:
            available_routes = debug_result['json_response'].get('hubspot_oauth_routes', [])
            print(f"📋 Available HubSpot OAuth routes: {len(available_routes)}")
            for route in available_routes:
                print(f"   - {route['methods']} {route['path']}")
        
        # Provide recommendations
        if analysis["found_404s"]:
            analysis["recommendations"].append("Some endpoints are returning 404 - check if they're deployed")
            analysis["recommendations"].append("Verify the deployed code includes all OAuth endpoints")
            analysis["recommendations"].append("Check if there are any routing conflicts or middleware issues")
        
        return analysis
    
    async def run_prismatic_specific_checks(self) -> Dict[str, Any]:
        """Run Prismatic-specific diagnostic checks"""
        print(f"\n🔧 Running Prismatic Integration Checks...")
        print("=" * 50)
        
        prismatic_analysis = {
            "environment_variables": {},
            "external_connectivity": {},
            "webhook_simulation": {},
            "integration_readiness": {}
        }
        
        # Check environment variables
        print("📋 Checking Environment Variables...")
        env_check = await self.test_endpoint("GET", "/api/system/prismatic/diagnostics")
        if env_check.get('success') and 'json_response' in env_check:
            diagnostics = env_check['json_response']
            prismatic_analysis["environment_variables"] = diagnostics.get('integration_config', {}).get('auth_config', {})
            prismatic_analysis["critical_issues"] = diagnostics.get('critical_issues', [])
            prismatic_analysis["recommendations"] = diagnostics.get('recommendations', [])
            
            print(f"   ✅ HubSpot Client ID: {'Configured' if prismatic_analysis['environment_variables'].get('hubspot_client_id_configured') else '❌ Missing'}")
            print(f"   ✅ HubSpot Client Secret: {'Configured' if prismatic_analysis['environment_variables'].get('hubspot_client_secret_configured') else '❌ Missing'}")
        else:
            print("   ❌ Could not retrieve environment diagnostics")
            prismatic_analysis["environment_variables"]["error"] = "Diagnostic endpoint not accessible"
        
        # Test external connectivity (simulate Prismatic calling our API)
        print("\n📋 Testing External Connectivity...")
        if "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            connectivity_test = await self.test_endpoint("GET", "/api/hubspot/oauth/health")
            if connectivity_test.get('success'):
                print("   ✅ API is externally accessible")
                prismatic_analysis["external_connectivity"]["accessible"] = True
                prismatic_analysis["external_connectivity"]["https"] = self.base_url.startswith("https://")
                print(f"   {'✅' if prismatic_analysis['external_connectivity']['https'] else '⚠️'} HTTPS: {prismatic_analysis['external_connectivity']['https']}")
            else:
                print("   ❌ API is not externally accessible")
                prismatic_analysis["external_connectivity"]["accessible"] = False
        else:
            print("   ⚠️  Skipping external connectivity test (localhost)")
            prismatic_analysis["external_connectivity"]["skipped"] = "localhost environment"
        
        # Simulate webhook calls that Prismatic would make
        print("\n📋 Simulating Prismatic Webhook Calls...")
        webhook_tests = [
            {
                "name": "OAuth Health Check",
                "path": "/api/hubspot/oauth/health",
                "method": "GET",
                "expected_status": 200
            },
            {
                "name": "OAuth Token Exchange",
                "path": "/api/hubspot/oauth/token", 
                "method": "POST",
                "data": {"code": "prismatic_test_code", "redirect_uri": "https://prismatic.io/callback"},
                "expected_status": [400, 422, 500]  # Expected to fail with test data
            }
        ]
        
        webhook_results = []
        for test in webhook_tests:
            result = await self.test_endpoint(
                test["method"], 
                test["path"], 
                test.get("data"),
                {"User-Agent": "Prismatic-Integration/1.0"}
            )
            
            expected_statuses = test["expected_status"] if isinstance(test["expected_status"], list) else [test["expected_status"]]
            success = result.get("status_code") in expected_statuses
            
            webhook_results.append({
                "test_name": test["name"],
                "success": success,
                "status_code": result.get("status_code"),
                "expected": expected_statuses
            })
            
            print(f"   {'✅' if success else '❌'} {test['name']}: {result.get('status_code')} (expected {expected_statuses})")
        
        prismatic_analysis["webhook_simulation"] = webhook_results
        
        # Overall integration readiness assessment
        print("\n📋 Integration Readiness Assessment...")
        readiness_score = 0
        total_checks = 4
        
        # Check 1: Environment variables configured
        if prismatic_analysis["environment_variables"].get("hubspot_client_id_configured") and \
           prismatic_analysis["environment_variables"].get("hubspot_client_secret_configured"):
            readiness_score += 1
            print("   ✅ Environment variables configured")
        else:
            print("   ❌ Environment variables missing")
        
        # Check 2: External accessibility
        if prismatic_analysis["external_connectivity"].get("accessible", False):
            readiness_score += 1
            print("   ✅ API externally accessible")
        else:
            print("   ❌ API not externally accessible")
        
        # Check 3: HTTPS enabled
        if prismatic_analysis["external_connectivity"].get("https", False):
            readiness_score += 1
            print("   ✅ HTTPS enabled")
        else:
            print("   ⚠️  HTTPS not enabled (recommended for production)")
        
        # Check 4: Webhook endpoints responding
        successful_webhooks = sum(1 for w in webhook_results if w["success"])
        if successful_webhooks >= len(webhook_results) * 0.8:  # 80% success rate
            readiness_score += 1
            print("   ✅ Webhook endpoints responding correctly")
        else:
            print("   ❌ Webhook endpoints not responding correctly")
        
        readiness_percentage = (readiness_score / total_checks) * 100
        prismatic_analysis["integration_readiness"] = {
            "score": readiness_score,
            "total_checks": total_checks,
            "percentage": readiness_percentage,
            "ready": readiness_percentage >= 75
        }
        
        print(f"\n🎯 Integration Readiness: {readiness_percentage:.0f}% ({readiness_score}/{total_checks})")
        
        return prismatic_analysis

async def main():
    """Main test function"""
    print("🚀 HubSpot OAuth Deployment Diagnostic Tool")
    print("=" * 60)
    
    # Test environments
    environments = [
        {
            "name": "Local Development",
            "url": "http://localhost:8000",
            "description": "Local development server"
        }
    ]
    
    # Add production URL if provided
    if len(sys.argv) > 1:
        prod_url = sys.argv[1]
        environments.append({
            "name": "Production/Deployed",
            "url": prod_url,
            "description": "Deployed environment"
        })
    else:
        print("💡 Usage: python test_deployment_debug.py [production_url]")
        print("   Example: python test_deployment_debug.py https://your-app.onrender.com")
        print("\n🔧 Testing local environment only...\n")
    
    all_results = {}
    
    # Test each environment
    for env in environments:
        print(f"\n🌍 Testing {env['name']}: {env['url']}")
        print(f"   {env['description']}")
        print("-" * 60)
        
        tester = OAuthEndpointTester(env['url'])
        results = await tester.run_comprehensive_test()
        analysis = await tester.analyze_404_issues(results)
        prismatic_analysis = await tester.run_prismatic_specific_checks()
        
        all_results[env['name']] = {
            "results": results,
            "analysis": analysis,
            "prismatic_analysis": prismatic_analysis
        }
        
        # Print summary
        summary = results['summary']
        print(f"\n📊 Summary for {env['name']}:")
        print(f"   ✅ Passed: {summary['passed']}/{summary['total_tests']}")
        print(f"   ❌ Failed: {summary['failed']}/{summary['total_tests']}")
        
        if summary['errors']:
            print(f"   🚨 Errors:")
            for error in summary['errors']:
                print(f"      - {error}")
    
    # Compare environments if we have multiple
    if len(environments) > 1:
        print(f"\n🔄 Environment Comparison")
        print("=" * 40)
        
        local_tests = all_results.get("Local Development", {}).get("results", {}).get("tests", {})
        prod_tests = all_results.get("Production/Deployed", {}).get("results", {}).get("tests", {})
        
        for test_name in local_tests.keys():
            local_status = local_tests[test_name].get('status_code', 'N/A')
            prod_status = prod_tests.get(test_name, {}).get('status_code', 'N/A')
            
            if local_status != prod_status:
                print(f"   ⚠️  {test_name}: Local={local_status}, Prod={prod_status}")
            else:
                print(f"   ✅ {test_name}: Both={local_status}")
    
    # Save detailed results
    with open("oauth_diagnostic_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: oauth_diagnostic_results.json")
    print(f"🎯 Diagnostic complete!")

if __name__ == "__main__":
    asyncio.run(main())