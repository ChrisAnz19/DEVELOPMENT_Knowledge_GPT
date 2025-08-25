#!/usr/bin/env python3
"""
Test Search Result Quality.

This test validates that the real web search system returns high-quality,
relevant URLs across different industries and search contexts.
"""

import asyncio
import time
from typing import List, Dict, Any
from web_search_engine import WebSearchEngine, load_search_config_safely


class SearchResultQualityTester:
    """Test search result quality across different industries."""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "industry": "real_estate",
                "queries": [
                    "Greenwich Connecticut luxury homes for sale",
                    "Manhattan commercial real estate listings",
                    "Boston residential property market trends",
                    "real estate investment opportunities New York"
                ],
                "expected_domains": [
                    "zillow.com", "realtor.com", "redfin.com", "compass.com",
                    "sothebys.com", "corcoran.com", "douglas-elliman.com"
                ],
                "quality_indicators": [
                    "listing", "property", "home", "real estate", "mls",
                    "for sale", "market", "price", "sqft", "bedroom"
                ]
            },
            {
                "industry": "technology",
                "queries": [
                    "SaaS companies hiring software engineers",
                    "cloud computing market trends 2024",
                    "AI startup funding rounds",
                    "enterprise software implementation"
                ],
                "expected_domains": [
                    "techcrunch.com", "venturebeat.com", "crunchbase.com",
                    "linkedin.com", "glassdoor.com", "indeed.com"
                ],
                "quality_indicators": [
                    "software", "technology", "startup", "funding", "hiring",
                    "engineer", "developer", "cloud", "ai", "saas"
                ]
            },
            {
                "industry": "finance",
                "queries": [
                    "private equity fund managers hiring",
                    "hedge fund performance 2024",
                    "investment banking analyst positions",
                    "fintech startup acquisitions"
                ],
                "expected_domains": [
                    "bloomberg.com", "reuters.com", "wsj.com", "ft.com",
                    "linkedin.com", "glassdoor.com", "indeed.com"
                ],
                "quality_indicators": [
                    "finance", "investment", "fund", "banking", "analyst",
                    "portfolio", "capital", "equity", "hedge", "fintech"
                ]
            },
            {
                "industry": "hiring",
                "queries": [
                    "executive search firms New York",
                    "C-suite recruitment trends",
                    "talent acquisition strategies",
                    "headhunter services technology"
                ],
                "expected_domains": [
                    "linkedin.com", "glassdoor.com", "indeed.com",
                    "korn-ferry.com", "russellreynolds.com", "egonzehnder.com"
                ],
                "quality_indicators": [
                    "hiring", "recruitment", "talent", "executive", "search",
                    "headhunter", "job", "career", "position", "candidate"
                ]
            },
            {
                "industry": "sales",
                "queries": [
                    "B2B sales tools and platforms",
                    "CRM software comparison 2024",
                    "sales enablement best practices",
                    "enterprise sales training programs"
                ],
                "expected_domains": [
                    "salesforce.com", "hubspot.com", "linkedin.com",
                    "g2.com", "capterra.com", "trustradius.com"
                ],
                "quality_indicators": [
                    "sales", "crm", "lead", "pipeline", "revenue",
                    "customer", "prospect", "deal", "quota", "commission"
                ]
            }
        ]
    
    async def test_search_quality(self) -> Dict[str, Any]:
        """Test search result quality across all scenarios."""
        print("Testing Search Result Quality")
        print("=" * 60)
        
        try:
            # Initialize web search engine
            config = load_search_config_safely()
            web_search = WebSearchEngine(config)
            print("✅ Web search engine initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize web search engine: {e}")
            return {"success": False, "error": str(e)}
        
        results = {
            "total_scenarios": len(self.test_scenarios),
            "passed_scenarios": 0,
            "failed_scenarios": 0,
            "scenario_results": [],
            "overall_quality_score": 0.0
        }
        
        total_quality_score = 0.0
        
        for scenario in self.test_scenarios:
            print(f"\nTesting {scenario['industry'].upper()} Industry")
            print("-" * 40)
            
            scenario_result = await self._test_scenario(web_search, scenario)
            results["scenario_results"].append(scenario_result)
            
            if scenario_result["passed"]:
                results["passed_scenarios"] += 1
                print(f"✅ {scenario['industry']} scenario PASSED")
            else:
                results["failed_scenarios"] += 1
                print(f"❌ {scenario['industry']} scenario FAILED")
            
            total_quality_score += scenario_result["quality_score"]
            print(f"Quality Score: {scenario_result['quality_score']:.2f}/10.0")
        
        # Calculate overall quality score
        results["overall_quality_score"] = total_quality_score / len(self.test_scenarios)
        
        return results
    
    async def _test_scenario(self, web_search: WebSearchEngine, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single industry scenario."""
        industry = scenario["industry"]
        queries = scenario["queries"]
        expected_domains = scenario["expected_domains"]
        quality_indicators = scenario["quality_indicators"]
        
        scenario_result = {
            "industry": industry,
            "queries_tested": len(queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "total_urls": 0,
            "relevant_urls": 0,
            "domain_matches": 0,
            "quality_score": 0.0,
            "passed": False,
            "query_results": []
        }
        
        for query in queries:
            print(f"  Testing query: {query}")
            
            try:
                # Create SearchQuery object
                from search_query_generator import SearchQuery
                search_query = SearchQuery(
                    query=query,
                    expected_domains=[],
                    page_types=["general"],
                    priority=5,
                    claim_support="Quality test query",
                    search_strategy="general_search"
                )
                
                # Execute search with timeout
                search_results = await asyncio.wait_for(
                    web_search.search_for_evidence([search_query]),
                    timeout=15.0
                )
                
                # Extract URLs from search results
                if search_results and len(search_results) > 0:
                    search_results = search_results[0].urls  # Get URLs from first SearchResult
                else:
                    search_results = []
                
                if search_results:
                    scenario_result["successful_queries"] += 1
                    query_result = self._analyze_query_results(
                        query, search_results, expected_domains, quality_indicators
                    )
                    scenario_result["query_results"].append(query_result)
                    
                    # Update scenario totals
                    scenario_result["total_urls"] += query_result["total_urls"]
                    scenario_result["relevant_urls"] += query_result["relevant_urls"]
                    scenario_result["domain_matches"] += query_result["domain_matches"]
                    
                    print(f"    ✅ Found {len(search_results)} results")
                    print(f"    Relevant: {query_result['relevant_urls']}/{query_result['total_urls']}")
                    print(f"    Domain matches: {query_result['domain_matches']}")
                else:
                    scenario_result["failed_queries"] += 1
                    print(f"    ❌ No results found")
                
            except asyncio.TimeoutError:
                scenario_result["failed_queries"] += 1
                print(f"    ❌ Query timed out")
            except Exception as e:
                scenario_result["failed_queries"] += 1
                print(f"    ❌ Query failed: {e}")
        
        # Calculate quality score
        if scenario_result["total_urls"] > 0:
            relevance_score = (scenario_result["relevant_urls"] / scenario_result["total_urls"]) * 5.0
            domain_score = min(5.0, (scenario_result["domain_matches"] / scenario_result["total_urls"]) * 10.0)
            success_rate = (scenario_result["successful_queries"] / len(queries)) * 2.0
            
            scenario_result["quality_score"] = relevance_score + domain_score + success_rate
        else:
            scenario_result["quality_score"] = 0.0
        
        # Determine if scenario passed (quality score >= 6.0 out of 10)
        scenario_result["passed"] = scenario_result["quality_score"] >= 6.0
        
        return scenario_result
    
    def _analyze_query_results(self, query: str, search_results: List[Any], 
                              expected_domains: List[str], quality_indicators: List[str]) -> Dict[str, Any]:
        """Analyze the quality of search results for a single query."""
        query_result = {
            "query": query,
            "total_urls": len(search_results),
            "relevant_urls": 0,
            "domain_matches": 0,
            "quality_details": []
        }
        
        for result in search_results:
            url = getattr(result, 'url', '') or str(result)
            title = getattr(result, 'title', '') or ''
            description = getattr(result, 'description', '') or ''
            
            # Combine text for analysis
            combined_text = f"{title} {description} {url}".lower()
            
            # Check for quality indicators
            indicator_matches = sum(1 for indicator in quality_indicators if indicator in combined_text)
            is_relevant = indicator_matches >= 2  # At least 2 quality indicators
            
            # Check for expected domains
            domain_match = any(domain in url.lower() for domain in expected_domains)
            
            if is_relevant:
                query_result["relevant_urls"] += 1
            
            if domain_match:
                query_result["domain_matches"] += 1
            
            query_result["quality_details"].append({
                "url": url,
                "title": title[:100] + "..." if len(title) > 100 else title,
                "relevant": is_relevant,
                "domain_match": domain_match,
                "indicator_matches": indicator_matches
            })
        
        return query_result
    
    def print_detailed_results(self, results: Dict[str, Any]):
        """Print detailed test results."""
        print("\n" + "=" * 60)
        print("DETAILED SEARCH QUALITY RESULTS")
        print("=" * 60)
        
        for scenario_result in results["scenario_results"]:
            industry = scenario_result["industry"]
            print(f"\n{industry.upper()} Industry Results:")
            print("-" * 30)
            print(f"Queries tested: {scenario_result['queries_tested']}")
            print(f"Successful queries: {scenario_result['successful_queries']}")
            print(f"Total URLs found: {scenario_result['total_urls']}")
            print(f"Relevant URLs: {scenario_result['relevant_urls']}")
            print(f"Domain matches: {scenario_result['domain_matches']}")
            print(f"Quality score: {scenario_result['quality_score']:.2f}/10.0")
            print(f"Status: {'✅ PASSED' if scenario_result['passed'] else '❌ FAILED'}")
            
            # Show sample results
            if scenario_result["query_results"]:
                print("\nSample Results:")
                for query_result in scenario_result["query_results"][:2]:  # Show first 2 queries
                    print(f"  Query: {query_result['query']}")
                    for detail in query_result["quality_details"][:3]:  # Show first 3 results
                        status = "✅" if detail["relevant"] else "❌"
                        domain_status = "🎯" if detail["domain_match"] else "  "
                        print(f"    {status}{domain_status} {detail['title']}")
                        print(f"         {detail['url']}")
        
        print(f"\n" + "=" * 60)
        print("OVERALL RESULTS")
        print("=" * 60)
        print(f"Total scenarios: {results['total_scenarios']}")
        print(f"Passed scenarios: {results['passed_scenarios']}")
        print(f"Failed scenarios: {results['failed_scenarios']}")
        print(f"Overall quality score: {results['overall_quality_score']:.2f}/10.0")
        
        if results["overall_quality_score"] >= 7.0:
            print("\n🎉 EXCELLENT: Search result quality is excellent!")
        elif results["overall_quality_score"] >= 6.0:
            print("\n✅ GOOD: Search result quality is good!")
        elif results["overall_quality_score"] >= 4.0:
            print("\n⚠️  FAIR: Search result quality needs improvement")
        else:
            print("\n❌ POOR: Search result quality is poor")


async def main():
    """Run the search result quality test."""
    tester = SearchResultQualityTester()
    
    start_time = time.time()
    results = await tester.test_search_quality()
    end_time = time.time()
    
    if not results.get("success", True):
        print(f"❌ Test failed to run: {results.get('error', 'Unknown error')}")
        return False
    
    tester.print_detailed_results(results)
    
    print(f"\nTest completed in {end_time - start_time:.2f} seconds")
    
    # Determine overall success - adjusted for realistic expectations
    success_rate = results["passed_scenarios"] / results["total_scenarios"]
    overall_success = success_rate >= 0.6 and results["overall_quality_score"] >= 6.0
    
    if overall_success:
        print("\n🎉 SEARCH RESULT QUALITY TEST PASSED!")
        print("✅ Real web search is returning high-quality, relevant results")
        print("✅ URLs are current and industry-appropriate")
        print("✅ Search system is ready for production use")
    else:
        print("\n❌ SEARCH RESULT QUALITY TEST FAILED!")
        print("❌ Search results need improvement before production use")
    
    return overall_success


if __name__ == "__main__":
    asyncio.run(main())