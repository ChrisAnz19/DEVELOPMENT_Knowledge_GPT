#!/usr/bin/env python3
"""
Web Search Engine for URL Evidence Finder.

This module integrates with OpenAI's web search capabilities to execute
search queries and extract relevant URLs with citations and metadata.
"""

import asyncio
import time
import json
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


class WebSearchEngine:
    """Executes web searches using OpenAI's web search tool."""
    
    def __init__(self, openai_client: Optional[OpenAI] = None):
        self.client = openai_client or OpenAI()
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # Minimum delay between requests (seconds)
        self.max_retries = 3
        self.timeout = 30  # Request timeout in seconds
    
    async def search_for_evidence(self, queries: List[SearchQuery]) -> List[SearchResult]:
        """
        Execute web searches using OpenAI's web search tool.
        
        Args:
            queries: List of search queries to execute
            
        Returns:
            List of search results with URLs and metadata
        """
        results = []
        
        # Process queries with rate limiting
        for query in queries:
            try:
                # Enforce rate limiting
                await self._enforce_rate_limit()
                
                # Execute search with retries
                result = await self._execute_search_with_retries(query)
                results.append(result)
                
                # Log successful search
                if result.success:
                    print(f"[Web Search] Found {len(result.urls)} URLs for query: {query.query[:50]}...")
                else:
                    print(f"[Web Search] Failed query: {query.query[:50]}... - {result.error_message}")
                
            except Exception as e:
                print(f"[Web Search Error] Query failed: {query.query[:50]}... - {str(e)}")
                # Create failed result
                results.append(SearchResult(
                    query=query,
                    urls=[],
                    citations=[],
                    search_metadata={'error': str(e)},
                    success=False,
                    error_message=str(e)
                ))
        
        return results
    
    async def _execute_search_with_retries(self, query: SearchQuery) -> SearchResult:
        """Execute search with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await self._execute_search(query)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * self.rate_limit_delay
                    print(f"[Web Search] Retry {attempt + 1} in {wait_time}s for query: {query.query[:30]}...")
                    await asyncio.sleep(wait_time)
        
        # All retries failed
        return SearchResult(
            query=query,
            urls=[],
            citations=[],
            search_metadata={'retries': self.max_retries, 'final_error': str(last_error)},
            success=False,
            error_message=f"Failed after {self.max_retries} retries: {str(last_error)}"
        )
    
    async def _execute_search(self, query: SearchQuery) -> SearchResult:
        """Execute single search query with OpenAI web search."""
        start_time = time.time()
        
        try:
            # Construct the search request
            messages = [
                {
                    "role": "user",
                    "content": f"Find URLs that support this search query: {query.query}. Focus on finding {', '.join(query.page_types)} pages from authoritative sources."
                }
            ]
            
            # Make the API call with web search tool
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=[{
                    "type": "web_search"
                }],
                tool_choice="auto",
                timeout=self.timeout
            )
            
            self.request_count += 1
            execution_time = time.time() - start_time
            
            # Parse the response
            urls, citations = self._parse_search_response(response, query)
            
            return SearchResult(
                query=query,
                urls=urls,
                citations=citations,
                search_metadata={
                    'execution_time': execution_time,
                    'request_count': self.request_count,
                    'model_used': 'gpt-4o-mini'
                },
                success=True,
                error_message=None
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"[Web Search API Error] {str(e)}")
            
            return SearchResult(
                query=query,
                urls=[],
                citations=[],
                search_metadata={
                    'execution_time': execution_time,
                    'error': str(e)
                },
                success=False,
                error_message=str(e)
            )
    
    def _parse_search_response(self, response: Any, query: SearchQuery) -> tuple[List[URLCandidate], List[Dict[str, Any]]]:
        """
        Parse OpenAI search response into URL candidates.
        
        Args:
            response: OpenAI API response
            query: Original search query
            
        Returns:
            Tuple of (URL candidates, raw citations)
        """
        url_candidates = []
        citations = []
        
        try:
            # Check if the response has tool calls
            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                
                if hasattr(choice, 'message') and hasattr(choice.message, 'tool_calls'):
                    for tool_call in choice.message.tool_calls:
                        if tool_call.type == "web_search":
                            # Parse web search results
                            try:
                                search_results = json.loads(tool_call.function.arguments)
                                urls, cites = self._extract_urls_from_search_results(search_results, query)
                                url_candidates.extend(urls)
                                citations.extend(cites)
                            except json.JSONDecodeError as e:
                                print(f"[Web Search] JSON decode error: {e}")
                
                # Also check message content for citations
                if hasattr(choice.message, 'content') and choice.message.content:
                    content_urls, content_cites = self._extract_urls_from_content(choice.message.content, query)
                    url_candidates.extend(content_urls)
                    citations.extend(content_cites)
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_candidates = []
            for candidate in url_candidates:
                if candidate.url not in seen_urls:
                    seen_urls.add(candidate.url)
                    unique_candidates.append(candidate)
            
            return unique_candidates, citations
            
        except Exception as e:
            print(f"[Web Search Parse Error] Failed to parse response: {str(e)}")
            return [], []
    
    def _extract_urls_from_search_results(self, search_results: Dict[str, Any], query: SearchQuery) -> tuple[List[URLCandidate], List[Dict[str, Any]]]:
        """Extract URLs from structured search results."""
        url_candidates = []
        citations = []
        
        try:
            # Handle different possible search result formats
            results = search_results.get('results', [])
            if not results:
                results = search_results.get('web_results', [])
            if not results:
                results = search_results.get('items', [])
            
            for i, result in enumerate(results):
                url = result.get('url', result.get('link', ''))
                title = result.get('title', result.get('name', ''))
                snippet = result.get('snippet', result.get('description', ''))
                
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
            
        except Exception as e:
            print(f"[Web Search] Error extracting from search results: {e}")
        
        return url_candidates, citations
    
    def _extract_urls_from_content(self, content: str, query: SearchQuery) -> tuple[List[URLCandidate], List[Dict[str, Any]]]:
        """Extract URLs from message content (fallback method)."""
        url_candidates = []
        citations = []
        
        try:
            import re
            
            # Simple URL extraction from content
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'
            urls = re.findall(url_pattern, content)
            
            for i, url in enumerate(urls):
                domain = self._extract_domain(url)
                
                # Try to extract title from surrounding context
                title = self._extract_title_from_context(content, url)
                
                candidate = URLCandidate(
                    url=url,
                    title=title,
                    snippet="",
                    domain=domain,
                    page_type=self._detect_page_type(url, title),
                    search_query=query.query,
                    citation_index=i
                )
                
                url_candidates.append(candidate)
                citations.append({'url': url, 'title': title, 'source': 'content_extraction'})
        
        except Exception as e:
            print(f"[Web Search] Error extracting from content: {e}")
        
        return url_candidates, citations
    
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