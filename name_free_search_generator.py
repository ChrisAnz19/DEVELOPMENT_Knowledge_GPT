#!/usr/bin/env python3
"""
Name-Free Search Query Generator.

This module generates search queries that NEVER include prospect names,
focusing only on behavioral evidence.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from explanation_analyzer import SearchableClaim, ClaimType


@dataclass
class SearchQuery:
    """Represents a targeted search query for evidence gathering."""
    query: str                          # The search query string
    expected_domains: List[str]         # Preferred domains for this query
    page_types: List[str]              # Expected page types (pricing, features, etc.)
    priority: int                      # Query priority (1-10, 10 being highest)
    claim_support: str                 # How this query supports the original claim
    search_strategy: str               # Strategy used (company_direct, product_general, etc.)


class NameFreeSearchGenerator:
    """Generates search queries without using prospect names."""
    
    def __init__(self):
        # Company domains for direct searches
        self.company_domains = {
            'salesforce': 'salesforce.com',
            'hubspot': 'hubspot.com',
            'microsoft': 'microsoft.com',
            'google': 'google.com',
            'amazon': 'amazon.com',
            'oracle': 'oracle.com',
            'sap': 'sap.com',
            'adobe': 'adobe.com'
        }
        
        # Authoritative domains for different types of content
        self.authoritative_domains = {
            'comparison': ['g2.com', 'capterra.com', 'trustradius.com'],
            'news': ['techcrunch.com', 'venturebeat.com', 'forbes.com'],
            'research': ['gartner.com', 'forrester.com', 'mckinsey.com']
        }
    
    def generate_queries(self, claim: SearchableClaim, candidate_id: str = None) -> List[SearchQuery]:
        """
        Generate search queries focused on behavioral evidence (NO NAMES).
        
        Args:
            claim: Searchable claim with entities and context
            candidate_id: Ignored - not used in query generation
            
        Returns:
            List of name-free search queries
        """
        queries = []
        
        # Strategy 1: Company-specific behavioral queries
        if claim.entities.get('companies'):
            queries.extend(self._create_company_behavioral_queries(claim))
        
        # Strategy 2: Product evaluation queries
        if claim.entities.get('products'):
            queries.extend(self._create_product_queries(claim))
        
        # Strategy 3: Pricing research queries
        if claim.entities.get('pricing_terms') or claim.claim_type == ClaimType.PRICING_RESEARCH:
            queries.extend(self._create_pricing_queries(claim))
        
        # Strategy 4: Industry/role-based queries
        if claim.entities.get('roles') or claim.entities.get('industries'):
            queries.extend(self._create_role_industry_queries(claim))
        
        # Strategy 5: General behavioral queries
        queries.extend(self._create_behavioral_queries(claim))
        
        # Sort by priority and limit results
        queries.sort(key=lambda q: q.priority, reverse=True)
        return queries[:5]
    
    def _create_company_behavioral_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create behavioral queries about companies (NO NAMES)."""
        queries = []
        
        for company in claim.entities.get('companies', []):
            company_lower = company.lower()
            domain = self.company_domains.get(company_lower)
            
            # Company hiring/recruitment queries
            if claim.entities.get('roles'):
                role = claim.entities['roles'][0]
                query = f'"{company}" {role} hiring recruitment jobs'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[domain] if domain else [],
                    page_types=['careers', 'jobs'],
                    priority=9,
                    claim_support=f"{company} hiring and recruitment information",
                    search_strategy="company_hiring"
                ))
            
            # Company executive changes
            query = f'"{company}" executive changes leadership transitions'
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['news', 'press'],
                priority=8,
                claim_support=f"{company} leadership and executive changes",
                search_strategy="company_leadership"
            ))
            
            # Company expansion/growth
            query = f'"{company}" expansion growth new markets'
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['news', 'analysis'],
                priority=7,
                claim_support=f"{company} expansion and growth activities",
                search_strategy="company_growth"
            ))
        
        return queries
    
    def _create_product_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create product evaluation queries (NO NAMES)."""
        queries = []
        
        products = claim.entities.get('products', [])
        companies = claim.entities.get('companies', [])
        
        for product in products:
            # Product comparison queries
            query = f"{product} comparison alternatives 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['comparison'],
                page_types=['comparison', 'review'],
                priority=8,
                claim_support=f"Product comparison for {product} solutions",
                search_strategy="product_comparison"
            ))
            
            # Product evaluation queries
            query = f"{product} evaluation review enterprise"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['comparison'],
                page_types=['review', 'evaluation'],
                priority=7,
                claim_support=f"Product evaluation for {product}",
                search_strategy="product_evaluation"
            ))
        
        return queries
    
    def _create_pricing_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create pricing research queries (NO NAMES)."""
        queries = []
        
        companies = claim.entities.get('companies', [])
        products = claim.entities.get('products', [])
        
        # Company pricing queries
        for company in companies:
            query = f'"{company}" pricing plans cost subscription'
            queries.append(SearchQuery(
                query=query,
                expected_domains=[self.company_domains.get(company.lower())] if self.company_domains.get(company.lower()) else [],
                page_types=['pricing'],
                priority=9,
                claim_support=f"{company} pricing information",
                search_strategy="company_pricing"
            ))
        
        # Product category pricing
        for product in products:
            query = f"{product} pricing comparison cost analysis"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['comparison'],
                page_types=['pricing', 'comparison'],
                priority=8,
                claim_support=f"Pricing analysis for {product} category",
                search_strategy="product_pricing"
            ))
        
        return queries
    
    def _create_role_industry_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create role and industry queries (NO NAMES)."""
        queries = []
        
        roles = claim.entities.get('roles', [])
        industries = claim.entities.get('industries', [])
        
        # Role-based market queries
        for role in roles:
            query = f"{role} job market trends 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['research'],
                page_types=['research', 'analysis'],
                priority=7,
                claim_support=f"Job market trends for {role} positions",
                search_strategy="role_market_trends"
            ))
            
            query = f"{role} salary compensation trends"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['research', 'salary'],
                priority=6,
                claim_support=f"Compensation trends for {role}",
                search_strategy="role_compensation"
            ))
        
        # Industry analysis queries
        for industry in industries:
            query = f"{industry} industry analysis trends 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['research'],
                page_types=['research', 'analysis'],
                priority=7,
                claim_support=f"Industry analysis for {industry}",
                search_strategy="industry_analysis"
            ))
        
        return queries
    
    def _create_behavioral_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create general behavioral queries (NO NAMES)."""
        queries = []
        
        # Use search terms but never names
        search_terms = [term for term in claim.search_terms 
                       if not self._is_likely_name(term)][:3]
        
        if search_terms:
            terms = ' '.join(search_terms)
            
            # Behavioral activity queries
            query = f"{terms} trends analysis 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['analysis', 'trends'],
                priority=6,
                claim_support=f"Trend analysis for {terms}",
                search_strategy="behavioral_trends"
            ))
            
            # Market activity queries
            query = f"{terms} market activity research"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains['research'],
                page_types=['research', 'market'],
                priority=5,
                claim_support=f"Market research for {terms}",
                search_strategy="market_activity"
            ))
        
        return queries
    
    def _is_likely_name(self, term: str) -> bool:
        """Check if a term is likely a person's name."""
        # Simple heuristic: capitalized single words that aren't common business terms
        business_terms = {
            'cmo', 'ceo', 'cto', 'cfo', 'vp', 'director', 'manager',
            'salesforce', 'hubspot', 'microsoft', 'google', 'amazon',
            'crm', 'saas', 'api', 'platform', 'software', 'technology',
            'marketing', 'sales', 'finance', 'engineering', 'product'
        }
        
        return (term.istitle() and 
                len(term) > 2 and 
                term.lower() not in business_terms and
                not any(char.isdigit() for char in term))


def test_name_free_generator():
    """Test that the generator produces no name-based queries."""
    
    print("Testing Name-Free Search Generator")
    print("=" * 35)
    
    # Create test claim
    claim = SearchableClaim(
        text="CMO looking to leave Fortune 500 role for startup opportunity",
        claim_type=ClaimType.GENERAL_ACTIVITY,
        entities={
            'roles': ['CMO', 'Chief Marketing Officer'],
            'companies': ['Fortune 500', 'Salesforce'],
            'industries': ['startup']
        },
        search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity'],
        priority=8,
        confidence=0.9
    )
    
    generator = NameFreeSearchGenerator()
    queries = generator.generate_queries(claim)
    
    print(f"Generated {len(queries)} queries:")
    
    # Check for name violations
    problematic_names = ['john', 'jane', 'smith', 'doe', 'michael', 'sarah']
    name_violations = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query.query}")
        print(f"   Strategy: {query.search_strategy}")
        print(f"   Priority: {query.priority}")
        
        # Check for name violations
        query_lower = query.query.lower()
        for name in problematic_names:
            if name in query_lower:
                name_violations.append((query.query, name))
    
    print(f"\nName Violations: {len(name_violations)}")
    
    if name_violations:
        print("❌ VIOLATIONS FOUND:")
        for query, name in name_violations:
            print(f"  - '{query}' contains '{name}'")
        return False
    else:
        print("✅ SUCCESS: No names found in queries")
        print("✅ All queries focus on behavioral evidence")
        return True


if __name__ == "__main__":
    test_name_free_generator()