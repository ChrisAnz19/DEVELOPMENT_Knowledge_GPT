#!/usr/bin/env python3
"""
Web Search Engine for URL Evidence Finder.

This module provides URL search capabilities using OpenAI chat completions
with fallback URL generation when AI responses are insufficient.
"""

import asyncio
import time
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI
from search_query_generator import SearchQuery


@dataclass
class URLCandidate:
    """Represents a URL candidate from search results."""
    url: str                    # The actual URL
    title: str                  # Page title
    snippet: str                # Content snippet/description
    domain: str                 # Domain name
    page_type: Optional[str]    # Detected page type
    search_query: str           # Query that found this URL
    citation_index: int         # Citation index from search results


@dataclass
class SearchResult:
    """Represents the result of a search query execution."""
    query: SearchQuery          # Original search query
    urls: List[URLCandidate]    # Found URL candidates
    citations: List[Dict[str, Any]]  # Raw citation data
    search_metadata: Dict[str, Any]  # Search execution metadata
    success: bool               # Whether search was successful
    error_message: Optional[str] # Error message if failed


@dataclass
class WebSearchConfig:
    """Configuration for web search engine."""
    serpapi_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    max_results_per_query: int = 5
    timeout: int = 5  # Reasonable timeout
    enable_fallback_urls: bool = True


def load_search_config() -> WebSearchConfig:
    """Load search configuration from secrets.json and environment variables."""
    config = WebSearchConfig()
    
    # Try to load from secrets.json first
    try:
        secrets_path = os.path.join(os.path.dirname(__file__), 'api', 'secrets.json')
        if not os.path.exists(secrets_path):
            # Try alternative path
            secrets_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'secrets.json')
        
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
                config.serpapi_key = secrets.get('SERP_API_KEY')
                config.openai_api_key = secrets.get('OPENAI_API_KEY')
                print(f"[Web Search Config] Loaded API keys from secrets.json")
        else:
            print(f"[Web Search Config] secrets.json not found at {secrets_path}")
    except Exception as e:
        print(f"[Web Search Config] Error loading secrets.json: {e}")
    
    # Override with environment variables if available
    if os.getenv('SERP_API_KEY'):
        config.serpapi_key = os.getenv('SERP_API_KEY')
        print(f"[Web Search Config] Using SERP_API_KEY from environment")
    
    if os.getenv('OPENAI_API_KEY'):
        config.openai_api_key = os.getenv('OPENAI_API_KEY')
        print(f"[Web Search Config] Using OPENAI_API_KEY from environment")
    
    return config


class WebSearchEngine:
    """Executes web searches using real search APIs with fallback URL generation."""
    
    def __init__(self, config: Optional[WebSearchConfig] = None):
        self.config = config or load_search_config()
        self.client = None  # Will be lazy loaded
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 0.1  # Short delay for speed
        self.max_retries = 0  # No retries for maximum speed
        self.timeout = self.config.timeout
        self.fallback_enabled = True
        self._fallback_generator = None
        self.max_requests_per_batch = 5  # Limit requests per batch
    
    async def _search_with_serpapi(self, query: SearchQuery) -> SearchResult:
        """
        Execute search using SerpAPI (Google Search API).
        
        Args:
            query: Search query to execute
            
        Returns:
            SearchResult with URLs from SerpAPI
        """
        start_time = time.time()
        
        if not self.config.serpapi_key:
            return SearchResult(
                query=query,
                urls=[],
                citations=[],
                search_metadata={'error': 'No SerpAPI key available'},
                success=False,
                error_message='No SerpAPI key configured'
            )
        
        try:
            import requests
            
            # Use SerpAPI REST endpoint directly
            search_params = {
                "q": query.query,
                "api_key": self.config.serpapi_key,
                "num": self.config.max_results_per_query,
                "hl": "en",
                "gl": "us",
                "engine": "google"
            }
            
            response = requests.get("https://serpapi.com/search", params=search_params, timeout=self.timeout)
            response.raise_for_status()
            results = response.json()
            
            # Parse results into URLCandidate objects
            url_candidates = []
            citations = []
            
            # Process organic results
            organic_results = results.get('organic_results', [])
            for i, result in enumerate(organic_results):
                url = result.get('link', '')
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                
                if url and url.startswith(('http://', 'https://')):
                    domain = self._extract_domain(url)
                    page_type = self._detect_page_type(url, title)
                    
                    candidate = URLCandidate(
                        url=url,
                        title=title,
                        snippet=snippet,
                        domain=domain,
                        page_type=page_type,
                        search_query=query.query,
                        citation_index=i
                    )
                    
                    url_candidates.append(candidate)
                    citations.append(result)
            
            execution_time = time.time() - start_time
            
            return SearchResult(
                query=query,
                urls=url_candidates,
                citations=citations,
                search_metadata={
                    'execution_time': execution_time,
                    'source': 'serpapi',
                    'total_results': len(organic_results)
                },
                success=True,
                error_message=None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"[Web Search SerpAPI Error] {str(e)}")
            
            return SearchResult(
                query=query,
                urls=[],
                citations=[],
                search_metadata={
                    'execution_time': execution_time,
                    'error': str(e),
                    'source': 'serpapi'
                },
                success=False,
                error_message=str(e)
            )
    

    
    async def search_for_evidence(self, queries: List[SearchQuery]) -> List[SearchResult]:
        """
        Execute web searches with circuit breaker to prevent hanging.
        
        Args:
            queries: List of search queries to execute
            
        Returns:
            List of search results with URLs and metadata
        """
        results = []
        
        # Limit number of queries to prevent hanging
        limited_queries = queries[:self.max_requests_per_batch]
        if len(queries) > self.max_requests_per_batch:
            print(f"[Web Search] Limited to {self.max_requests_per_batch} queries (from {len(queries)})")
        
        # Process queries with rate limiting and timeout
        for i, query in enumerate(limited_queries):
            try:
                print(f"[Web Search] Processing query {i+1}/{len(limited_queries)}: {query.query[:50]}...")
                
                # Enforce rate limiting
                await self._enforce_rate_limit()
                
                # Execute search with simple timeout
                result = await asyncio.wait_for(
                    self._execute_search(query),
                    timeout=self.timeout  # Use configured timeout
                )
                results.append(result)
                
                # Log successful search
                if result.success:
                    print(f"[Web Search] Found {len(result.urls)} URLs for query: {query.query[:50]}...")
                else:
                    print(f"[Web Search] Failed query: {query.query[:50]}... - {result.error_message}")
                
            except asyncio.TimeoutError:
                print(f"[Web Search] Query timed out: {query.query[:50]}...")
                # Use fallback for timed out queries
                fallback_urls = self._get_fallback_urls(query) if self.fallback_enabled else []
                results.append(SearchResult(
                    query=query,
                    urls=fallback_urls,
                    citations=[{'source': 'fallback_timeout', 'url': url.url} for url in fallback_urls],
                    search_metadata={'error': 'timeout', 'fallback_used': len(fallback_urls)},
                    success=len(fallback_urls) > 0,
                    error_message='Query timed out'
                ))
            except Exception as e:
                print(f"[Web Search Error] Query failed: {query.query[:50]}... - {str(e)}")
                # Use fallback for failed queries
                fallback_urls = self._get_fallback_urls(query) if self.fallback_enabled else []
                results.append(SearchResult(
                    query=query,
                    urls=fallback_urls,
                    citations=[{'source': 'fallback_error', 'url': url.url} for url in fallback_urls],
                    search_metadata={'error': str(e), 'fallback_used': len(fallback_urls)},
                    success=len(fallback_urls) > 0,
                    error_message=str(e)
                ))
        
        print(f"[Web Search] Completed batch: {len(results)} results")
        return results
    

    
    async def _execute_search(self, query: SearchQuery) -> SearchResult:
        """Execute single search query using real web search APIs."""
        print(f"[Web Search] Executing real search for: {query.query[:50]}...")
        
        # Strategy 1: Try SerpAPI first (if API key available)
        if self.config.serpapi_key:
            print(f"[Web Search] Trying SerpAPI for: {query.query[:30]}...")
            result = await self._search_with_serpapi(query)
            if result.success and result.urls:
                print(f"[Web Search] SerpAPI found {len(result.urls)} URLs")
                return result
            else:
                print(f"[Web Search] SerpAPI failed: {result.error_message}")
        
        # Strategy 2: Final fallback to contextual URL generation
        if self.config.enable_fallback_urls:
            print(f"[Web Search] Using fallback URL generation for: {query.query[:30]}...")
            fallback_urls = self._get_fallback_urls(query)
            
            return SearchResult(
                query=query,
                urls=fallback_urls,
                citations=[{'source': 'fallback', 'url': url.url} for url in fallback_urls],
                search_metadata={
                    'source': 'fallback',
                    'fallback_used': len(fallback_urls)
                },
                success=len(fallback_urls) > 0,
                error_message=None if fallback_urls else "All search methods failed"
            )
        
        # Complete failure
        return SearchResult(
            query=query,
            urls=[],
            citations=[],
            search_metadata={'error': 'All search methods failed'},
            success=False,
            error_message="No search methods available or all failed"
        )
    

    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            # Fallback to simple extraction
            try:
                return url.split('/')[2].lower()
            except:
                return ""
    
    def _detect_page_type(self, url: str, title: str) -> Optional[str]:
        """Detect page type based on URL and title."""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Pricing pages
        if any(word in url_lower for word in ['pricing', 'price', 'plan', 'cost']):
            return 'pricing'
        if any(word in title_lower for word in ['pricing', 'price', 'plan', 'cost']):
            return 'pricing'
        
        # Product pages
        if any(word in url_lower for word in ['product', 'solution', 'platform']):
            return 'product'
        if any(word in title_lower for word in ['product', 'solution', 'platform']):
            return 'product'
        
        # Documentation
        if any(word in url_lower for word in ['doc', 'guide', 'api', 'help', 'support']):
            return 'documentation'
        if any(word in title_lower for word in ['documentation', 'guide', 'api', 'help']):
            return 'documentation'
        
        # Comparison pages
        if any(word in url_lower for word in ['comparison', 'compare', 'vs', 'versus']):
            return 'comparison'
        if any(word in title_lower for word in ['comparison', 'compare', 'vs', 'versus']):
            return 'comparison'
        
        # News/blog
        if any(word in url_lower for word in ['blog', 'news', 'article']):
            return 'news'
        
        # Company pages
        if any(word in url_lower for word in ['about', 'company', 'team']):
            return 'company'
        
        return None
    
    def _extract_title_from_context(self, content: str, url: str) -> str:
        """Extract title from surrounding context in content."""
        try:
            # Look for text near the URL that might be a title
            url_index = content.find(url)
            if url_index == -1:
                return ""
            
            # Look for text before the URL (potential title)
            start = max(0, url_index - 100)
            before_text = content[start:url_index].strip()
            
            # Simple heuristic: take the last sentence/phrase before the URL
            sentences = before_text.split('.')
            if sentences:
                potential_title = sentences[-1].strip()
                if len(potential_title) > 5 and len(potential_title) < 100:
                    return potential_title
            
            return ""
        except:
            return ""
    
    def _get_fallback_urls(self, query: SearchQuery) -> List[URLCandidate]:
        """Get fallback URLs when AI search fails or returns no results."""
        try:
            if self._fallback_generator is None:
                from fallback_url_generator import FallbackURLGenerator
                self._fallback_generator = FallbackURLGenerator()
            
            return self._fallback_generator.generate_fallback_urls(query, max_urls=3)
        except Exception as e:
            print(f"[Web Search] Fallback generation failed: {str(e)}")
            return []
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()


async def test_web_search_engine():
    """Test function for the web search engine."""
    from explanation_analyzer import ExplanationAnalyzer
    from search_query_generator import SearchQueryGenerator
    
    # Initialize components
    analyzer = ExplanationAnalyzer()
    generator = SearchQueryGenerator()
    search_engine = WebSearchEngine()
    
    # Test explanation
    explanation = "Currently researching Salesforce pricing options for enterprise deployment"
    
    print("Testing Web Search Engine:")
    print("=" * 50)
    print(f"Explanation: {explanation}")
    
    # Extract claims and generate queries
    claims = analyzer.extract_claims(explanation)
    if not claims:
        print("No claims extracted!")
        return
    
    claim = claims[0]
    queries = generator.generate_queries(claim)
    
    print(f"\nGenerated {len(queries)} queries for claim: {claim.text}")
    
    # Test with first 2 queries to avoid too many API calls
    test_queries = queries[:2]
    
    # Execute searches
    results = await search_engine.search_for_evidence(test_queries)
    
    print(f"\nSearch Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Query: {result.query.query}")
        print(f"   Success: {result.success}")
        if result.success:
            print(f"   Found {len(result.urls)} URLs:")
            for j, url in enumerate(result.urls, 1):
                print(f"     {j}. {url.title}")
                print(f"        URL: {url.url}")
                print(f"        Domain: {url.domain}")
                print(f"        Type: {url.page_type}")
        else:
            print(f"   Error: {result.error_message}")


if __name__ == '__main__':
    # Note: This test requires OpenAI API key and will make actual API calls
    print("Web Search Engine module loaded successfully!")
    print("To test with actual API calls, run: asyncio.run(test_web_search_engine())")
    print("Make sure you have OPENAI_API_KEY environment variable set.")