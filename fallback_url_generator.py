#!/usr/bin/env python3
"""
Fallback URL Generator for Web Search Engine.

This module provides pattern-based URL generation when external search APIs fail.
It generates relevant URLs based on search query patterns and common business domains.
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from search_query_generator import SearchQuery
from web_search_engine import URLCandidate


@dataclass
class URLPattern:
    """Represents a URL pattern template."""
    template: str
    domains: List[str]
    page_type: str
    keywords: List[str]
    priority: int = 1


class FallbackURLGenerator:
    """Generates relevant URLs based on search patterns when external search fails."""
    
    def __init__(self):
        self.url_patterns = self._initialize_patterns()
        self.domain_categories = self._initialize_domain_categories()
    
    def generate_fallback_urls(self, query: SearchQuery, max_urls: int = 5) -> List[URLCandidate]:
        """
        Generate fallback URLs for a search query.
        
        Args:
            query: Search query to generate URLs for
            max_urls: Maximum number of URLs to generate
            
        Returns:
            List of URL candidates
        """
        candidates = []
        query_lower = query.query.lower()
        
        # Extract key terms from query
        key_terms = self._extract_key_terms(query_lower)
        
        # Generate URLs based on query patterns
        for pattern in self.url_patterns:
            if self._pattern_matches_query(pattern, query_lower, key_terms):
                pattern_urls = self._generate_urls_from_pattern(pattern, query, key_terms)
                candidates.extend(pattern_urls)
        
        # Sort by relevance and priority
        candidates.sort(key=lambda x: self._calculate_relevance_score(x, query), reverse=True)
        
        # Return top candidates
        return candidates[:max_urls]
    
    def _initialize_patterns(self) -> List[URLPattern]:
        """Initialize URL patterns for different types of searches."""
        patterns = []
        
        # CRM and Software patterns
        patterns.extend([
            URLPattern(
                template="https://{domain}/pricing/",
                domains=["salesforce.com", "hubspot.com", "pipedrive.com", "zoho.com"],
                page_type="pricing",
                keywords=["crm", "pricing", "cost", "plan", "software"],
                priority=3
            ),
            URLPattern(
                template="https://{domain}/products/",
                domains=["salesforce.com", "microsoft.com", "oracle.com", "sap.com"],
                page_type="product",
                keywords=["crm", "software", "platform", "solution"],
                priority=2
            ),
            URLPattern(
                template="https://www.g2.com/categories/{category}",
                domains=["g2.com"],
                page_type="comparison",
                keywords=["crm", "software", "review", "comparison"],
                priority=2
            ),
            URLPattern(
                template="https://www.capterra.com/p/{category}-software/",
                domains=["capterra.com"],
                page_type="comparison",
                keywords=["software", "review", "comparison"],
                priority=2
            ),
            URLPattern(
                template="https://www.trustradius.com/{category}/",
                domains=["trustradius.com"],
                page_type="comparison",
                keywords=["software", "review", "comparison"],
                priority=2
            ),
            URLPattern(
                template="https://www.softwareadvice.com/{category}/",
                domains=["softwareadvice.com"],
                page_type="comparison",
                keywords=["software", "advice", "comparison"],
                priority=2
            )
        ])
        
        # Real Estate patterns
        patterns.extend([
            URLPattern(
                template="https://{domain}/",
                domains=["realtor.com", "zillow.com", "redfin.com", "trulia.com"],
                page_type="product",
                keywords=["real estate", "property", "house", "home"],
                priority=3
            ),
            URLPattern(
                template="https://www.biggerpockets.com/",
                domains=["biggerpockets.com"],
                page_type="community",
                keywords=["real estate", "investment", "property", "rei"],
                priority=2
            )
        ])
        
        # Technology and AI patterns
        patterns.extend([
            URLPattern(
                template="https://{domain}/",
                domains=["openai.com", "anthropic.com", "google.com/ai", "microsoft.com/ai"],
                page_type="product",
                keywords=["ai", "artificial intelligence", "machine learning", "technology"],
                priority=2
            ),
            URLPattern(
                template="https://techcrunch.com/",
                domains=["techcrunch.com"],
                page_type="news",
                keywords=["technology", "startup", "funding", "tech"],
                priority=1
            )
        ])
        
        # Business and Finance patterns
        patterns.extend([
            URLPattern(
                template="https://{domain}/",
                domains=["bloomberg.com", "reuters.com", "wsj.com", "ft.com"],
                page_type="news",
                keywords=["business", "finance", "market", "investment"],
                priority=2
            ),
            URLPattern(
                template="https://www.crunchbase.com/",
                domains=["crunchbase.com"],
                page_type="company",
                keywords=["startup", "company", "funding", "investment"],
                priority=2
            )
        ])
        
        return patterns
    
    def _initialize_domain_categories(self) -> Dict[str, List[str]]:
        """Initialize domain categories for different business areas."""
        return {
            "crm": ["salesforce.com", "hubspot.com", "pipedrive.com", "zoho.com", "freshworks.com"],
            "software_reviews": ["g2.com", "capterra.com", "trustradius.com", "softwareadvice.com"],
            "real_estate": ["realtor.com", "zillow.com", "redfin.com", "trulia.com", "biggerpockets.com"],
            "technology": ["techcrunch.com", "venturebeat.com", "wired.com", "arstechnica.com"],
            "business": ["bloomberg.com", "reuters.com", "wsj.com", "ft.com", "forbes.com"],
            "startup": ["crunchbase.com", "angellist.com", "producthunt.com"]
        }
    
    def _extract_key_terms(self, query: str) -> List[str]:
        """Extract key terms from search query."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'find', 'looking', 'search', 'need', 'want', 'who', 'what', 'where', 'when',
            'why', 'how', 'that', 'this', 'these', 'those'
        }
        
        # Extract words and filter
        words = re.findall(r'\b\w+\b', query.lower())
        key_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return key_terms
    
    def _pattern_matches_query(self, pattern: URLPattern, query: str, key_terms: List[str]) -> bool:
        """Check if a URL pattern matches the search query."""
        # First check for domain-specific indicators
        real_estate_indicators = ["real estate", "property", "house", "home", "mansion", "luxury", "greenwich", "westchester", "residential"]
        crm_indicators = ["crm", "customer relationship", "sales software", "lead management"]
        
        # If query contains real estate indicators, only match real estate patterns
        if any(indicator in query for indicator in real_estate_indicators):
            if pattern.page_type in ["product"] and any(domain in ["realtor.com", "zillow.com", "redfin.com", "trulia.com"] for domain in pattern.domains):
                return True
            return False
        
        # If query contains CRM indicators, only match CRM patterns  
        if any(indicator in query for indicator in crm_indicators):
            if "crm" in pattern.keywords:
                return True
            return False
        
        # Default matching logic for other cases
        # Check if any pattern keywords appear in query or key terms
        for keyword in pattern.keywords:
            if keyword in query or keyword in key_terms:
                return True
        
        # Check for partial matches
        for keyword in pattern.keywords:
            for term in key_terms:
                if keyword in term or term in keyword:
                    return True
        
        return False
    
    def _generate_urls_from_pattern(self, pattern: URLPattern, query: SearchQuery, key_terms: List[str]) -> List[URLCandidate]:
        """Generate URL candidates from a pattern."""
        candidates = []
        
        for domain in pattern.domains:
            # Generate URL from template
            if "{domain}" in pattern.template:
                url = pattern.template.format(domain=domain)
            elif "{category}" in pattern.template:
                category = self._infer_category(key_terms)
                url = pattern.template.format(category=category)
            else:
                url = pattern.template
            
            # Generate title and snippet
            title = self._generate_title(domain, pattern.page_type, key_terms)
            snippet = self._generate_snippet(domain, pattern.page_type, key_terms)
            
            candidate = URLCandidate(
                url=url,
                title=title,
                snippet=snippet,
                domain=domain,
                page_type=pattern.page_type,
                search_query=query.query,
                citation_index=len(candidates)
            )
            
            candidates.append(candidate)
        
        return candidates
    
    def _infer_category(self, key_terms: List[str]) -> str:
        """Infer category from key terms for URL templates."""
        category_mappings = {
            "crm": ["crm", "customer", "relationship", "management", "sales"],
            "project-management": ["project", "management", "task", "team"],
            "accounting": ["accounting", "finance", "bookkeeping", "tax"],
            "marketing": ["marketing", "campaign", "email", "social"],
            "hr": ["hr", "human", "resources", "payroll", "employee"],
            "real-estate": ["real", "estate", "property", "house", "home", "rei"]
        }
        
        for category, keywords in category_mappings.items():
            for term in key_terms:
                if any(keyword in term.lower() for keyword in keywords):
                    return category
        
        return "business-software"  # Default category
    
    def _generate_title(self, domain: str, page_type: str, key_terms: List[str]) -> str:
        """Generate a relevant title for the URL."""
        domain_names = {
            "salesforce.com": "Salesforce",
            "hubspot.com": "HubSpot",
            "g2.com": "G2",
            "capterra.com": "Capterra",
            "trustradius.com": "TrustRadius",
            "softwareadvice.com": "Software Advice",
            "realtor.com": "Realtor.com",
            "zillow.com": "Zillow",
            "biggerpockets.com": "BiggerPockets"
        }
        
        brand_name = domain_names.get(domain, domain.split('.')[0].title())
        
        if page_type == "pricing":
            return f"{brand_name} Pricing & Plans"
        elif page_type == "product":
            return f"{brand_name} - Product Overview"
        elif page_type == "comparison":
            return f"Best Software Reviews & Comparisons - {brand_name}"
        elif page_type == "news":
            return f"Latest News - {brand_name}"
        elif page_type == "company":
            return f"Company Information - {brand_name}"
        else:
            return f"{brand_name} - {' '.join(key_terms[:3]).title()}"
    
    def _generate_snippet(self, domain: str, page_type: str, key_terms: List[str]) -> str:
        """Generate a relevant snippet for the URL."""
        if page_type == "pricing":
            return f"Compare pricing plans and features. Find the right plan for your business needs."
        elif page_type == "product":
            return f"Comprehensive product information, features, and capabilities."
        elif page_type == "comparison":
            return f"Read reviews, compare features, and find the best software solutions."
        elif page_type == "news":
            return f"Latest industry news, trends, and insights."
        elif page_type == "company":
            return f"Company profile, funding information, and business details."
        else:
            return f"Relevant information about {' '.join(key_terms[:3])}."
    
    def _calculate_relevance_score(self, candidate: URLCandidate, query: SearchQuery) -> float:
        """Calculate relevance score for a URL candidate."""
        score = 0.0
        query_lower = query.query.lower()
        
        # Domain relevance
        if any(keyword in candidate.domain for keyword in ["salesforce", "hubspot", "g2", "capterra"]):
            score += 2.0
        
        # Page type relevance
        if candidate.page_type in query.page_types:
            score += 3.0
        
        # Title relevance
        title_words = candidate.title.lower().split()
        query_words = query_lower.split()
        common_words = set(title_words) & set(query_words)
        score += len(common_words) * 0.5
        
        # Domain authority (simple heuristic)
        authority_domains = {
            "salesforce.com": 3.0,
            "g2.com": 2.5,
            "capterra.com": 2.5,
            "trustradius.com": 2.0,
            "softwareadvice.com": 2.0,
            "hubspot.com": 2.5
        }
        score += authority_domains.get(candidate.domain, 1.0)
        
        return score


def test_fallback_generator():
    """Test function for the fallback URL generator."""
    from search_query_generator import SearchQuery
    
    generator = FallbackURLGenerator()
    
    # Test queries
    test_queries = [
        SearchQuery(
            query="Find CRM software pricing information",
            page_types=["pricing", "product"],
            priority=1,
            search_context="software evaluation"
        ),
        SearchQuery(
            query="Real estate investment networking groups",
            page_types=["community", "product"],
            priority=1,
            search_context="real estate"
        ),
        SearchQuery(
            query="AI technology companies and startups",
            page_types=["company", "news"],
            priority=1,
            search_context="technology research"
        )
    ]
    
    print("Testing Fallback URL Generator:")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query.query}")
        candidates = generator.generate_fallback_urls(query, max_urls=5)
        
        print(f"   Generated {len(candidates)} URLs:")
        for j, candidate in enumerate(candidates, 1):
            print(f"     {j}. {candidate.title}")
            print(f"        URL: {candidate.url}")
            print(f"        Domain: {candidate.domain}")
            print(f"        Type: {candidate.page_type}")


if __name__ == '__main__':
    test_fallback_generator()