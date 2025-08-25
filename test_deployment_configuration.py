#!/usr/bin/env python3
"""
Test Deployment Configuration.

This test verifies that the deployment configuration is correct and
API keys are properly loaded in production environment.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from web_search_engine import WebSearchEngine, load_search_config_safely


class DeploymentConfigurationTester:
    """Test deployment configuration and API key loading."""
    
    def __init__(self):
        self.test_results = {
            "secrets_file_test": False,
            "environment_variables_test": False,
            "api_key_validation_test": False,
            "web_search_initialization_test": False,
            "search_functionality_test": False,
            "overall_deployment_ready": False
        }
    
    def test_secrets_file_loading(self) -> Dict[str, Any]:
        """Test that secrets.json file can be loaded properly."""
        print("Testing Secrets File Loading")
        print("-" * 40)
        
        result = {
            "success": False,
            "secrets_file_found": False,
            "secrets_file_readable": False,
            "required_keys_present": False,
            "api_keys_loaded": {},
            "error": None
        }
        
        try:
            # Check for secrets.json in multiple locations
            possible_paths = [
                os.path.join(os.path.dirname(__file__), 'api', 'secrets.json'),
                os.path.join(os.path.dirname(__file__), '..', 'api', 'secrets.json'),
                os.path.join(os.getcwd(), 'api', 'secrets.json'),
                os.path.join(os.getcwd(), 'secrets.json')
            ]
            
            secrets_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    secrets_path = path
                    result["secrets_file_found"] = True
                    print(f"✅ Found secrets.json at: {path}")
                    break
            
            if not secrets_path:
                result["error"] = "secrets.json file not found in any expected location"
                print("❌ secrets.json file not found")
                return result
            
            # Try to read the secrets file
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                result["secrets_file_readable"] = True
                print("✅ secrets.json file is readable")
            
            # Check for required API keys
            required_keys = ['SERP_API_KEY', 'OPENAI_API_KEY']
            keys_present = []
            keys_missing = []
            
            for key in required_keys:
                if key in secrets and secrets[key]:
                    keys_present.append(key)
                    result["api_keys_loaded"][key] = "present"
                    print(f"✅ {key} is present")
                else:
                    keys_missing.append(key)
                    result["api_keys_loaded"][key] = "missing"
                    print(f"❌ {key} is missing or empty")
            
            result["required_keys_present"] = len(keys_missing) == 0
            
            if result["required_keys_present"]:
                result["success"] = True
                print("✅ All required API keys are present in secrets.json")
            else:
                result["error"] = f"Missing required keys: {keys_missing}"
                print(f"❌ Missing required keys: {keys_missing}")
            
        except json.JSONDecodeError as e:
            result["error"] = f"Invalid JSON in secrets.json: {e}"
            print(f"❌ Invalid JSON in secrets.json: {e}")
        except Exception as e:
            result["error"] = f"Error reading secrets.json: {e}"
            print(f"❌ Error reading secrets.json: {e}")
        
        self.test_results["secrets_file_test"] = result["success"]
        return result
    
    def test_environment_variables(self) -> Dict[str, Any]:
        """Test environment variable loading."""
        print("\nTesting Environment Variables")
        print("-" * 40)
        
        result = {
            "success": False,
            "environment_keys_present": {},
            "fallback_available": False,
            "error": None
        }
        
        try:
            # Check for environment variables
            env_keys = ['SERP_API_KEY', 'OPENAI_API_KEY']
            env_keys_present = []
            env_keys_missing = []
            
            for key in env_keys:
                if os.getenv(key):
                    env_keys_present.append(key)
                    result["environment_keys_present"][key] = "present"
                    print(f"✅ Environment variable {key} is set")
                else:
                    env_keys_missing.append(key)
                    result["environment_keys_present"][key] = "missing"
                    print(f"⚠️  Environment variable {key} is not set")
            
            # Check if we have fallback from secrets.json
            secrets_result = self.test_results.get("secrets_file_test", False)
            if secrets_result or len(env_keys_present) > 0:
                result["fallback_available"] = True
                result["success"] = True
                print("✅ API keys available (either from environment or secrets.json)")
            else:
                result["error"] = "No API keys available from environment or secrets.json"
                print("❌ No API keys available from any source")
            
        except Exception as e:
            result["error"] = f"Error checking environment variables: {e}"
            print(f"❌ Error checking environment variables: {e}")
        
        self.test_results["environment_variables_test"] = result["success"]
        return result
    
    def test_api_key_validation(self) -> Dict[str, Any]:
        """Test API key validation through configuration loading."""
        print("\nTesting API Key Validation")
        print("-" * 40)
        
        result = {
            "success": False,
            "config_loaded": False,
            "serpapi_key_valid": False,
            "openai_key_valid": False,
            "error": None
        }
        
        try:
            # Load configuration using the safe loader
            config = load_search_config_safely()
            result["config_loaded"] = True
            print("✅ Configuration loaded successfully")
            
            # Validate API keys
            if config.serpapi_key and len(config.serpapi_key.strip()) > 10:
                result["serpapi_key_valid"] = True
                print("✅ SERP API key appears valid (length check)")
            else:
                print("❌ SERP API key is missing or too short")
            
            if config.openai_api_key and len(config.openai_api_key.strip()) > 10:
                result["openai_key_valid"] = True
                print("✅ OpenAI API key appears valid (length check)")
            else:
                print("❌ OpenAI API key is missing or too short")
            
            # Overall validation
            if result["serpapi_key_valid"] and result["openai_key_valid"]:
                result["success"] = True
                print("✅ All API keys appear valid")
            else:
                result["error"] = "One or more API keys are invalid"
                print("❌ One or more API keys are invalid")
            
        except Exception as e:
            result["error"] = f"Error validating API keys: {e}"
            print(f"❌ Error validating API keys: {e}")
        
        self.test_results["api_key_validation_test"] = result["success"]
        return result
    
    def test_web_search_initialization(self) -> Dict[str, Any]:
        """Test web search engine initialization."""
        print("\nTesting Web Search Engine Initialization")
        print("-" * 40)
        
        result = {
            "success": False,
            "engine_initialized": False,
            "config_valid": False,
            "error": None
        }
        
        try:
            # Initialize web search engine
            config = load_search_config_safely()
            web_search = WebSearchEngine(config)
            result["engine_initialized"] = True
            result["config_valid"] = True
            result["success"] = True
            print("✅ Web search engine initialized successfully")
            
        except Exception as e:
            result["error"] = f"Error initializing web search engine: {e}"
            print(f"❌ Error initializing web search engine: {e}")
        
        self.test_results["web_search_initialization_test"] = result["success"]
        return result
    
    async def test_search_functionality(self) -> Dict[str, Any]:
        """Test basic search functionality."""
        print("\nTesting Search Functionality")
        print("-" * 40)
        
        result = {
            "success": False,
            "search_executed": False,
            "results_returned": False,
            "results_count": 0,
            "error": None
        }
        
        try:
            # Initialize web search engine
            config = load_search_config_safely()
            web_search = WebSearchEngine(config)
            
            # Create a simple test query
            from search_query_generator import SearchQuery
            test_query = SearchQuery(
                query="technology companies hiring",
                expected_domains=[],
                page_types=["general"],
                priority=5,
                claim_support="Deployment test query",
                search_strategy="deployment_test"
            )
            
            # Execute search with timeout
            search_results = await asyncio.wait_for(
                web_search.search_for_evidence([test_query]),
                timeout=10.0
            )
            
            result["search_executed"] = True
            print("✅ Search executed successfully")
            
            if search_results and len(search_results) > 0:
                urls = search_results[0].urls if hasattr(search_results[0], 'urls') else []
                result["results_returned"] = len(urls) > 0
                result["results_count"] = len(urls)
                
                if result["results_returned"]:
                    result["success"] = True
                    print(f"✅ Search returned {result['results_count']} results")
                else:
                    result["error"] = "Search executed but returned no results"
                    print("❌ Search executed but returned no results")
            else:
                result["error"] = "Search executed but returned empty results"
                print("❌ Search executed but returned empty results")
            
        except asyncio.TimeoutError:
            result["error"] = "Search timed out"
            print("❌ Search timed out")
        except Exception as e:
            result["error"] = f"Error executing search: {e}"
            print(f"❌ Error executing search: {e}")
        
        self.test_results["search_functionality_test"] = result["success"]
        return result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment configuration tests."""
        print("Deployment Configuration Test Suite")
        print("=" * 60)
        
        # Run all tests
        secrets_result = self.test_secrets_file_loading()
        env_result = self.test_environment_variables()
        validation_result = self.test_api_key_validation()
        init_result = self.test_web_search_initialization()
        search_result = await self.test_search_functionality()
        
        # Determine overall deployment readiness
        all_critical_tests_passed = (
            self.test_results["api_key_validation_test"] and
            self.test_results["web_search_initialization_test"] and
            self.test_results["search_functionality_test"]
        )
        
        self.test_results["overall_deployment_ready"] = all_critical_tests_passed
        
        # Print summary
        print("\n" + "=" * 60)
        print("DEPLOYMENT CONFIGURATION TEST RESULTS")
        print("=" * 60)
        
        test_names = {
            "secrets_file_test": "Secrets File Loading",
            "environment_variables_test": "Environment Variables",
            "api_key_validation_test": "API Key Validation",
            "web_search_initialization_test": "Web Search Initialization",
            "search_functionality_test": "Search Functionality"
        }
        
        for test_key, test_name in test_names.items():
            status = "✅ PASS" if self.test_results[test_key] else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nOverall Deployment Ready: {'✅ YES' if self.test_results['overall_deployment_ready'] else '❌ NO'}")
        
        if self.test_results["overall_deployment_ready"]:
            print("\n🎉 DEPLOYMENT CONFIGURATION TEST PASSED!")
            print("✅ System is ready for production deployment")
            print("✅ API keys are properly configured")
            print("✅ Web search functionality is working")
        else:
            print("\n❌ DEPLOYMENT CONFIGURATION TEST FAILED!")
            print("❌ System is NOT ready for production deployment")
            print("❌ Fix the failing tests before deploying")
        
        return {
            "overall_success": self.test_results["overall_deployment_ready"],
            "test_results": self.test_results,
            "detailed_results": {
                "secrets": secrets_result,
                "environment": env_result,
                "validation": validation_result,
                "initialization": init_result,
                "search": search_result
            }
        }


async def main():
    """Run the deployment configuration test."""
    tester = DeploymentConfigurationTester()
    results = await tester.run_all_tests()
    return results["overall_success"]


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)