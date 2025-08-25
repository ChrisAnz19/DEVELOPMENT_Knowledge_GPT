#!/usr/bin/env python3
"""
Context-Aware Evidence Finder.

This module creates evidence URLs that are relevant to the specific search context,
rather than generic or domain-specific URLs.
"""

import re
import asyncio
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from enhanced_url_evidence_finder import EnhancedURLEvidenceFinder
from explanation_analyzer import SearchableClaim, ClaimType
from web_search_engine import WebSearchEngine


@dataclass
class SearchContext:
    """Represents the context of the original search."""
    search_prompt: str
    industry: Optional[str] = None
    role_type: Optional[str] = None
    activity_type: Optional[str] = None
    key_terms: List[str] = None
    
    def __post_init__(self):
        if self.key_terms is None:
            self.key_terms = []


class ContextAwareEvidenceFinder(EnhancedURLEvidenceFinder):
    """Evidence finder that understands search context and generates relevant URLs."""
    
    def __init__(self, enable_diversity: bool = True):
        super().__init__(enable_diversity)
        self.search_context = None
        
    def set_search_context(self, search_prompt: str):
        """
        Set the search context from the original search prompt.
        
        Args:
            search_prompt: The original search query that generated these candidates
        """
        self.search_context = self._analyze_search_context(search_prompt)
        print(f"[Context-Aware Evidence] Search context: {self.search_context.industry} | {self.search_context.role_type} | {self.search_context.activity_type}")
    
    def _analyze_search_context(self, search_prompt: str) -> SearchContext:
        """
        Analyze the search prompt to understand context.
        
        Args:
            search_prompt: Original search query
            
        Returns:
            SearchContext with extracted information
        """
        prompt_lower = search_prompt.lower()
        
        # Detect industry
        industry = self._detect_industry(prompt_lower)
        
        # Detect role type
        role_type = self._detect_role_type(prompt_lower)
        
        # Detect activity type
        activity_type = self._detect_activity_type(prompt_lower)
        
        # Extract key terms
        key_terms = self._extract_key_terms(search_prompt)
        
        return SearchContext(
            search_prompt=search_prompt,
            industry=industry,
            role_type=role_type,
            activity_type=activity_type,
            key_terms=key_terms
        )
    
    def _detect_industry(self, prompt: str) -> Optional[str]:
        """Detect industry from search prompt."""
        industry_patterns = {
            'media': r'\b(media|entertainment|broadcasting|publishing|content|streaming)\b',
            'technology': r'\b(tech|technology|software|saas|ai|digital|cloud)\b',
            'finance': r'\b(financial|finance|banking|investment|private equity|hedge fund)\b',
            'healthcare': r'\b(healthcare|medical|pharma|biotech|hospital)\b',
            'real_estate': r'\b(real estate|property|commercial|residential|reit)\b',
            'retail': r'\b(retail|consumer|e-commerce|shopping|brand)\b',
            'manufacturing': r'\b(manufacturing|industrial|automotive|aerospace)\b',
            'energy': r'\b(energy|oil|gas|renewable|utilities)\b'
        }
        
        for industry, pattern in industry_patterns.items():
            if re.search(pattern, prompt):
                return industry
        
        return None
    
    def _detect_role_type(self, prompt: str) -> Optional[str]:
        """Detect role type from search prompt."""
        role_patterns = {
            'corporate_development': r'\b(corporate development|m&a|mergers|acquisitions|divestiture)\b',
            'marketing': r'\b(marketing|cmo|brand|advertising|digital marketing)\b',
            'sales': r'\b(sales|business development|revenue|account)\b',
            'finance': r'\b(cfo|finance|accounting|controller|treasurer)\b',
            'operations': r'\b(operations|coo|supply chain|logistics)\b',
            'technology': r'\b(cto|engineering|developer|architect|devops)\b',
            'hr': r'\b(hr|human resources|talent|recruiting|chro)\b',
            'executive': r'\b(ceo|president|founder|executive|c-level)\b'
        }
        
        for role, pattern in role_patterns.items():
            if re.search(pattern, prompt):
                return role
        
        return None
    
    def _detect_activity_type(self, prompt: str) -> Optional[str]:
        """Detect activity type from search prompt."""
        activity_patterns = {
            'considering': r'\b(considering|evaluating|exploring|looking at)\b',
            'implementing': r'\b(implementing|deploying|rolling out|adopting)\b',
            'researching': r'\b(researching|investigating|studying|analyzing)\b',
            'planning': r'\b(planning|preparing|strategizing|developing)\b',
            'buying': r'\b(buying|purchasing|acquiring|procuring)\b',
            'selling': r'\b(selling|divesting|disposing|exiting)\b'
        }
        
        for activity, pattern in activity_patterns.items():
            if re.search(pattern, prompt):
                return activity
        
        return None
    
    def _extract_key_terms(self, prompt: str) -> List[str]:
        """Extract key terms from search prompt."""
        # Remove common words and extract meaningful terms
        common_words = {'find', 'people', 'who', 'are', 'at', 'in', 'with', 'for', 'the', 'and', 'or', 'of', 'to', 'a', 'an'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower())
        key_terms = [word for word in words if word not in common_words]
        
        return key_terms[:10]  # Limit to top 10 terms
    
    async def process_candidates_batch(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process candidates with context-aware evidence finding.
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            List of enhanced candidates with contextually relevant evidence URLs
        """
        if not self.search_context:
            print("[Context-Aware Evidence] Warning: No search context set. Using generic evidence finding.")
            return await super().process_candidates_batch(candidates)
        
        print(f"[Context-Aware Evidence] Processing {len(candidates)} candidates with context: {self.search_context.industry}")
        
        enhanced_candidates = []
        
        for candidate in candidates:
            try:
                enhanced_candidate = await self._process_candidate_with_context(candidate)
                enhanced_candidates.append(enhanced_candidate)
            except Exception as e:
                print(f"[Context-Aware Evidence] Error processing candidate {candidate.get('name', 'Unknown')}: {e}")
                enhanced_candidates.append(candidate)
        
        return enhanced_candidates
    
    async def _process_candidate_with_context(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single candidate with context awareness."""
        
        # Generate context-aware search queries
        search_queries = self._generate_contextual_queries(candidate)
        
        if not search_queries:
            print(f"[Context-Aware Evidence] No contextual queries generated for {candidate.get('name', 'Unknown')}")
            return candidate
        
        print(f"[Context-Aware Evidence] Generated {len(search_queries)} contextual queries for {candidate.get('name', 'Unknown')}")
        
        # Execute searches
        web_search = WebSearchEngine()
        search_results = []
        
        # Import SearchQuery for proper formatting
        from search_query_generator import SearchQuery
        
        for query_str in search_queries[:2]:  # Limit to 2 queries to prevent timeout
            try:
                print(f"[Context-Aware Evidence] Searching: {query_str}")
                
                # Create SearchQuery object
                search_query = SearchQuery(
                    query=query_str,
                    expected_domains=[],  # Let the system find relevant domains
                    page_types=["article", "news", "research"],
                    priority=5,  # Medium priority
                    claim_support="contextual evidence for search relevance",
                    search_strategy="contextual_evidence"
                )
                
                results = await web_search.search_for_evidence([search_query])
                search_results.extend(results)
            except Exception as e:
                print(f"[Context-Aware Evidence] Search failed for query '{query_str}': {e}")
        
        # Filter and validate URLs
        evidence_urls = await self._extract_and_validate_urls(search_results)
        
        # Create enhanced candidate response
        if evidence_urls:
            candidate['evidence_urls'] = [self._format_evidence_url(url) for url in evidence_urls]
            candidate['evidence_summary'] = f"Found {len(evidence_urls)} contextually relevant evidence URLs"
            candidate['evidence_confidence'] = min(0.95, 0.6 + (len(evidence_urls) * 0.1))
            print(f"[Context-Aware Evidence] Found {len(evidence_urls)} relevant URLs for {candidate.get('name', 'Unknown')}")
        else:
            candidate['evidence_urls'] = []
            candidate['evidence_summary'] = "No contextually relevant evidence URLs found"
            candidate['evidence_confidence'] = 0.0
            print(f"[Context-Aware Evidence] No relevant URLs found for {candidate.get('name', 'Unknown')}")
        
        return candidate
    
    def _generate_contextual_queries(self, candidate: Dict[str, Any]) -> List[str]:
        """Generate search queries based on context and candidate info."""
        queries = []
        
        name = candidate.get('name', '')
        title = candidate.get('title', '')
        company = candidate.get('company', '')
        
        # Get behavioral insight
        behavioral_data = candidate.get('behavioral_data', {})
        insight = behavioral_data.get('behavioral_insight', '') if isinstance(behavioral_data, dict) else ''
        
        # Base query with context
        if self.search_context.industry and self.search_context.activity_type:
            base_query = f"{self.search_context.industry} {self.search_context.activity_type}"
            queries.append(base_query)
        
        # Role-specific query
        if self.search_context.role_type:
            role_query = f"{self.search_context.role_type} best practices"
            queries.append(role_query)
        
        # Industry trends query
        if self.search_context.industry:
            trends_query = f"{self.search_context.industry} industry trends 2024"
            queries.append(trends_query)
        
        # Activity-specific query
        if self.search_context.activity_type and self.search_context.industry:
            activity_query = f"companies {self.search_context.activity_type} {self.search_context.industry}"
            queries.append(activity_query)
        
        # Key terms query
        if self.search_context.key_terms:
            key_terms_query = " ".join(self.search_context.key_terms[:3])
            queries.append(key_terms_query)
        
        return queries[:5]  # Limit to 5 queries
    
    async def _extract_and_validate_urls(self, search_results: List) -> List[str]:
        """Extract and validate URLs from search results."""
        urls = []
        
        for result in search_results:
            if hasattr(result, 'success') and result.success and hasattr(result, 'urls'):
                for url_candidate in result.urls[:3]:  # Limit URLs per result
                    if hasattr(url_candidate, 'url'):
                        urls.append(url_candidate.url)
        
        # Remove duplicates
        unique_urls = list(dict.fromkeys(urls))
        
        # Validate URLs (simple validation for now)
        from url_validator import URLValidator
        
        if unique_urls:
            async with URLValidator(timeout=2.0, max_concurrent=3) as validator:
                validation_results = await validator.validate_urls(unique_urls[:5])  # Limit to 5 URLs
            
            valid_urls = [result.url for result in validation_results if result.is_valid]
            print(f"[Context-Aware Evidence] Validated {len(valid_urls)}/{len(unique_urls)} URLs")
            return valid_urls
        
        return []
    
    def _format_evidence_url(self, url: str) -> Dict[str, Any]:
        """Format URL for frontend consumption."""
        return {
            'url': url,
            'title': self._generate_title_from_url(url),
            'relevance_score': 0.8,
            'source_type': 'contextual_evidence'
        }
    
    def _generate_title_from_url(self, url: str) -> str:
        """Generate a title from URL."""
        try:
            domain = url.split('/')[2].replace('www.', '')
            if 'forbes' in domain:
                return f"Forbes - {self.search_context.industry or 'Business'} Insights"
            elif 'harvard' in domain:
                return f"Harvard Business Review - {self.search_context.role_type or 'Leadership'}"
            elif 'mckinsey' in domain:
                return f"McKinsey - {self.search_context.industry or 'Strategy'} Analysis"
            else:
                return f"{domain.title()} - Industry Resource"
        except:
            return "Industry Resource"


# Test function
async def test_context_aware_evidence():
    """Test the context-aware evidence finder."""
    finder = ContextAwareEvidenceFinder(enable_diversity=True)
    
    # Set search context
    search_prompt = "Find corporate development officers at media companies considering divestiture"
    finder.set_search_context(search_prompt)
    
    # Test candidate
    test_candidates = [{
        'id': 'test_1',
        'name': 'Sarah Johnson',
        'title': 'VP Corporate Development',
        'company': 'MediaCorp Inc',
        'behavioral_data': {
            'behavioral_insight': 'Sarah is evaluating strategic divestiture options and has been researching M&A market conditions'
        }
    }]
    
    print("Testing Context-Aware Evidence Finder...")
    results = await finder.process_candidates_batch(test_candidates)
    
    if results:
        candidate = results[0]
        evidence_urls = candidate.get('evidence_urls', [])
        print(f"\nResults for {candidate.get('name')}:")
        print(f"Evidence URLs: {len(evidence_urls)}")
        for i, url in enumerate(evidence_urls):
            print(f"  {i+1}. {url.get('title')} - {url.get('url')}")


if __name__ == '__main__':
    asyncio.run(test_context_aware_evidence())