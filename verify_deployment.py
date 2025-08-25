#!/usr/bin/env python3
"""
Deployment Verification Script for Web Search API Fix

This script verifies that the web search API fix has been properly deployed
and that the system no longer uses the deprecated web_search tool.
"""

import sys
import os
import asyncio
from typing import List

def verify_files_exist() -> bool:
    """Verify that all required files exist."""
    required_files = [
        'web_search_engine.py',
        'fallback_url_generator.py',
        'search_query_generator.py',
        'README_URL_Evidence_Finder.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def verify_web_search_fix() -> bool:
    """Verify that the deprecated web_search tool has been removed."""
    try:
        with open('web_search_engine.py', 'r') as f:
            content = f.read()
        
        # Check that deprecated web_search tool is not used
        if '"type": "web_search"' in content:
            print("❌ Still using deprecated web_search tool type")
            return False
        
        # Check that fallback system is integrated
        if 'fallback' not in content.lower():
            print("❌ Fallback system not integrated")
            return False
        
        # Check that enhanced error handling is present
        if 'rate_limit' not in content.lower():
            print("❌ Enhanced error handling not implemented")
            return False
        
        print("✅ Web search engine properly updated")
        return True
        
    except Exception as e:
        print(f"❌ Error reading web_search_engine.py: {e}")
        return False

def verify_fallback_system() -> bool:
    """Verify that the fallback URL generator works."""
    try:
        from fallback_url_generator import FallbackURLGenerator
        from search_query_generator import SearchQuery
        
        generator = FallbackURLGenerator()
        
        # Test query
        query = SearchQuery(
            query='Find CRM software pricing information',
            expected_domains=['salesforce.com'],
            page_types=['pricing', 'product'],
            priority=1,
            claim_support='pricing research',
            search_strategy='product_general'
        )
        
        urls = generator.generate_fallback_urls(query, max_urls=3)
        
        if len(urls) == 0:
            print("❌ Fallback generator returned no URLs")
            return False
        
        # Check that URLs are relevant
        relevant_domains = ['salesforce.com', 'hubspot.com', 'g2.com', 'capterra.com']
        found_relevant = any(any(domain in url.url for domain in relevant_domains) for url in urls)
        
        if not found_relevant:
            print("❌ Fallback URLs not relevant to query")
            return False
        
        print(f"✅ Fallback system working - generated {len(urls)} relevant URLs")
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback system: {e}")
        return False

async def verify_web_search_engine() -> bool:
    """Verify that the web search engine works without API key."""
    try:
        # Import without initializing OpenAI client
        import sys
        sys.path.append('.')
        
        # Test that the class can be imported and doesn't immediately fail
        from web_search_engine import WebSearchEngine
        
        # Create instance without OpenAI client (will fail on actual search, but that's expected)
        engine = WebSearchEngine(openai_client=None)
        
        # Check that fallback is enabled by default
        if not hasattr(engine, 'fallback_enabled') or not engine.fallback_enabled:
            print("❌ Fallback not enabled by default")
            return False
        
        print("✅ Web search engine can be imported and configured")
        return True
        
    except Exception as e:
        print(f"❌ Error testing web search engine: {e}")
        return False

def verify_documentation() -> bool:
    """Verify that documentation has been updated."""
    try:
        with open('README_URL_Evidence_Finder.md', 'r') as f:
            content = f.read()
        
        # Check for updated documentation
        if 'Recent Updates (Web Search API Fix)' not in content:
            print("❌ Documentation not updated with fix information")
            return False
        
        if 'fallback' not in content.lower():
            print("❌ Documentation doesn't mention fallback system")
            return False
        
        print("✅ Documentation properly updated")
        return True
        
    except Exception as e:
        print(f"❌ Error reading documentation: {e}")
        return False

async def main():
    """Run all verification checks."""
    print("🔍 Verifying Web Search API Fix Deployment")
    print("=" * 50)
    
    checks = [
        ("File Existence", verify_files_exist),
        ("Web Search Fix", verify_web_search_fix),
        ("Fallback System", verify_fallback_system),
        ("Web Search Engine", verify_web_search_engine),
        ("Documentation", verify_documentation)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Deployment verification PASSED!")
        print("\n✅ The web search API fix has been successfully deployed:")
        print("   • Deprecated 'web_search' tool removed")
        print("   • Fallback URL generation system active")
        print("   • Enhanced error handling implemented")
        print("   • Documentation updated")
        print("\n🚀 Your system should no longer experience the OpenAI API error!")
        return True
    else:
        print("❌ Deployment verification FAILED!")
        print(f"   {total - passed} checks failed - please review the issues above")
        return False

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)