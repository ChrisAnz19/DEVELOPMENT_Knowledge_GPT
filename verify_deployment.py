#!/usr/bin/env python3
"""
Automated deployment verification script
Runs comprehensive checks after deployment to ensure everything is working
"""

import asyncio
import httpx
import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

class DeploymentVerifier:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": base_url,
            "overall_status": "unknown",
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "critical_failures": 0
            }
        }
    
    async def verify_basic_connectivity(self) -> Dict[str, Any]:
        """Verify basic API connectivity"""
        print("🔍 Verifying basic connectivity...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/")
                
                return {
                    "test_name": "Basic Connectivity",
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "critical": True
                }
        except Exception as e:
            return {
                "test_name": "Basic Connectivity", 
                "success": False,
                "error": str(e),
                "critical": True
            }
    
    async def verify_hubspot_oauth_endpoints(self) -> List[Dict[str, Any]]:
        """Verify all HubSpot OAuth endpoints are working"""
        print("🔍 Verifying HubSpot OAuth endpoints...")
        
        endpoints_to_test = [
            {
                "name": "OAuth Health",
                "method": "GET",
                "path": "/api/hubspot/oauth/health",
                "expected_status": 200,
                "critical": True
            },
            {
                "name": "OAuth Debug",
                "method": "GET", 
                "path": "/api/hubspot/oauth/debug",
                "expected_status": 200,
                "critical": False
            },
            {
                "name": "OAuth Test",
                "method": "POST",
                "path": "/api/hubspot/oauth/test",
                "expected_status": 200,
                "critical": False
            },
            {
                "name": "OAuth Token (Invalid)",
                "method": "POST",
                "path": "/api/hubspot/oauth/token",
                "data": {"code": "test", "redirect_uri": "https://test.com"},
                "expected_status": [400, 422, 500],  # Should fail with test data
                "critical": True
            }
        ]
        
        results = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            for endpoint in endpoints_to_test:
                try:
                    url = f"{self.base_url}{endpoint['path']}"
                    
                    if endpoint['method'] == 'GET':
                        response = await client.get(url)
                    else:
                        response = await client.post(url, json=endpoint.get('data', {}))
                    
                    expected_statuses = endpoint['expected_status'] if isinstance(endpoint['expected_status'], list) else [endpoint['expected_status']]
                    success = response.status_code in expected_statuses
                    
                    results.append({
                        "test_name": endpoint['name'],
                        "success": success,
                        "status_code": response.status_code,
                        "expected_status": expected_statuses,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "critical": endpoint['critical']
                    })
                    
                except Exception as e:
                    results.append({
                        "test_name": endpoint['name'],
                        "success": False,
                        "error": str(e),
                        "critical": endpoint['critical']
                    })
        
        return results
    
    async def verify_system_diagnostics(self) -> List[Dict[str, Any]]:
        """Verify system diagnostic endpoints"""
        print("🔍 Verifying system diagnostic endpoints...")
        
        diagnostic_endpoints = [
            {
                "name": "Prismatic Diagnostics",
                "path": "/api/system/prismatic/diagnostics",
                "critical": False
            },
            {
                "name": "Deployment Sync Check",
                "path": "/api/system/deployment/sync-check", 
                "critical": False
            },
            {
                "name": "Comprehensive Health",
                "path": "/api/system/health/comprehensive",
                "critical": False
            }
        ]
        
        results = []
        async with httpx.AsyncClient(timeout=20.0) as client:
            for endpoint in diagnostic_endpoints:
                try:
                    url = f"{self.base_url}{endpoint['path']}"
                    response = await client.get(url)
                    
                    # Try to parse JSON to ensure valid response
                    response_data = response.json()
                    
                    results.append({
                        "test_name": endpoint['name'],
                        "success": response.status_code == 200,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "has_valid_json": True,
                        "critical": endpoint['critical']
                    })
                    
                except json.JSONDecodeError:
                    results.append({
                        "test_name": endpoint['name'],
                        "success": False,
                        "error": "Invalid JSON response",
                        "status_code": response.status_code if 'response' in locals() else None,
                        "critical": endpoint['critical']
                    })
                except Exception as e:
                    results.append({
                        "test_name": endpoint['name'],
                        "success": False,
                        "error": str(e),
                        "critical": endpoint['critical']
                    })
        
        return results
    
    async def verify_environment_configuration(self) -> Dict[str, Any]:
        """Verify environment configuration through API"""
        print("🔍 Verifying environment configuration...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/system/deployment/sync-check")
                
                if response.status_code == 200:
                    data = response.json()
                    env_vars = data.get('critical_env_vars', {})
                    
                    # Check critical environment variables
                    hubspot_id_configured = env_vars.get('HUBSPOT_CLIENT_ID', {}).get('configured', False)
                    hubspot_secret_configured = env_vars.get('HUBSPOT_CLIENT_SECRET', {}).get('configured', False)
                    
                    config_issues = []
                    if not hubspot_id_configured:
                        config_issues.append("HUBSPOT_CLIENT_ID not configured")
                    if not hubspot_secret_configured:
                        config_issues.append("HUBSPOT_CLIENT_SECRET not configured")
                    
                    return {
                        "test_name": "Environment Configuration",
                        "success": len(config_issues) == 0,
                        "hubspot_client_id_configured": hubspot_id_configured,
                        "hubspot_client_secret_configured": hubspot_secret_configured,
                        "configuration_issues": config_issues,
                        "environment": data.get('environment_info', {}).get('detected_environment', 'unknown'),
                        "critical": True
                    }
                else:
                    return {
                        "test_name": "Environment Configuration",
                        "success": False,
                        "error": f"Sync check endpoint returned {response.status_code}",
                        "critical": True
                    }
                    
        except Exception as e:
            return {
                "test_name": "Environment Configuration",
                "success": False,
                "error": str(e),
                "critical": True
            }
    
    async def verify_prismatic_readiness(self) -> Dict[str, Any]:
        """Verify readiness for Prismatic integration"""
        print("🔍 Verifying Prismatic integration readiness...")
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Test webhook simulation
                response = await client.post(f"{self.base_url}/api/system/webhook/test")
                
                if response.status_code == 200:
                    data = response.json()
                    summary = data.get('summary', {})
                    
                    return {
                        "test_name": "Prismatic Readiness",
                        "success": summary.get('overall_prismatic_readiness', False),
                        "success_rate": summary.get('success_rate', 0),
                        "compatibility_rate": summary.get('compatibility_rate', 0),
                        "total_webhook_tests": summary.get('total_tests', 0),
                        "recommendations": data.get('recommendations', []),
                        "critical": True
                    }
                else:
                    return {
                        "test_name": "Prismatic Readiness",
                        "success": False,
                        "error": f"Webhook test endpoint returned {response.status_code}",
                        "critical": True
                    }
                    
        except Exception as e:
            return {
                "test_name": "Prismatic Readiness",
                "success": False,
                "error": str(e),
                "critical": True
            }
    
    async def run_full_verification(self) -> Dict[str, Any]:
        """Run complete deployment verification"""
        print(f"🚀 Starting deployment verification for: {self.base_url}")
        print("=" * 60)
        
        # Run all verification tests
        basic_connectivity = await self.verify_basic_connectivity()
        oauth_endpoints = await self.verify_hubspot_oauth_endpoints()
        system_diagnostics = await self.verify_system_diagnostics()
        env_config = await self.verify_environment_configuration()
        prismatic_readiness = await self.verify_prismatic_readiness()
        
        # Collect all test results
        all_tests = [basic_connectivity, env_config, prismatic_readiness] + oauth_endpoints + system_diagnostics
        
        # Calculate summary
        total_tests = len(all_tests)
        passed_tests = sum(1 for test in all_tests if test.get('success', False))
        failed_tests = total_tests - passed_tests
        critical_failures = sum(1 for test in all_tests if not test.get('success', False) and test.get('critical', False))
        
        # Determine overall status
        if critical_failures > 0:
            overall_status = "critical_failure"
        elif failed_tests == 0:
            overall_status = "success"
        elif failed_tests <= total_tests * 0.2:  # Less than 20% failures
            overall_status = "warning"
        else:
            overall_status = "failure"
        
        # Update results
        self.verification_results.update({
            "overall_status": overall_status,
            "tests": {
                "basic_connectivity": basic_connectivity,
                "environment_configuration": env_config,
                "prismatic_readiness": prismatic_readiness,
                "oauth_endpoints": oauth_endpoints,
                "system_diagnostics": system_diagnostics
            },
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "critical_failures": critical_failures,
                "success_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            }
        })
        
        # Print summary
        print(f"\n📊 Deployment Verification Summary:")
        print(f"   Overall Status: {overall_status.upper()}")
        print(f"   Tests Passed: {passed_tests}/{total_tests} ({self.verification_results['summary']['success_rate']:.1f}%)")
        print(f"   Critical Failures: {critical_failures}")
        
        if overall_status == "success":
            print("   ✅ Deployment verification PASSED - system is ready")
        elif overall_status == "warning":
            print("   ⚠️  Deployment verification passed with warnings")
        else:
            print("   ❌ Deployment verification FAILED - issues need to be resolved")
        
        # Print failed tests
        failed_test_details = [test for test in all_tests if not test.get('success', False)]
        if failed_test_details:
            print(f"\n❌ Failed Tests:")
            for test in failed_test_details:
                critical_marker = " (CRITICAL)" if test.get('critical', False) else ""
                print(f"   - {test['test_name']}{critical_marker}: {test.get('error', 'Failed')}")
        
        return self.verification_results

async def main():
    """Main verification function"""
    if len(sys.argv) < 2:
        print("Usage: python verify_deployment.py <base_url>")
        print("Example: python verify_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    verifier = DeploymentVerifier(base_url)
    
    try:
        results = await verifier.run_full_verification()
        
        # Save results to file
        output_file = f"deployment_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        # Exit with appropriate code
        if results['overall_status'] == 'critical_failure':
            print("🚨 CRITICAL DEPLOYMENT ISSUES DETECTED")
            sys.exit(2)
        elif results['overall_status'] == 'failure':
            print("❌ DEPLOYMENT VERIFICATION FAILED")
            sys.exit(1)
        elif results['overall_status'] == 'warning':
            print("⚠️  DEPLOYMENT HAS WARNINGS")
            sys.exit(0)
        else:
            print("✅ DEPLOYMENT VERIFICATION SUCCESSFUL")
            sys.exit(0)
            
    except Exception as e:
        print(f"💥 Verification script failed: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())