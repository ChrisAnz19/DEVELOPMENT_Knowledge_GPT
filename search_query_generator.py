#!/usr/bin/env python3
"""
Search Query Generator for URL Evidence Finder.

This module converts searchable claims into targeted web search queries
optimized for finding specific types of evidence (company pages, pricing info,
product documentation, etc.).
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


class SearchQueryGenerator:
    """Generates targeted search queries from searchable claims."""
    
    def __init__(self):
        # Domain mappings for major companies
        self.company_domains = {
            'salesforce': 'salesforce.com',
            'hubspot': 'hubspot.com',
            'microsoft': 'microsoft.com',
            'google': 'google.com',
            'amazon': 'amazon.com',
            'oracle': 'oracle.com',
            'sap': 'sap.com',
            'adobe': 'adobe.com',
            'zoom': 'zoom.us',
            'slack': 'slack.com',
            'shopify': 'shopify.com',
            'stripe': 'stripe.com',
            'twilio': 'twilio.com',
            'zendesk': 'zendesk.com',
            'atlassian': 'atlassian.com',
            'servicenow': 'servicenow.com',
            'workday': 'workday.com',
            'okta': 'okta.com',
            'tableau': 'tableau.com',
            'snowflake': 'snowflake.com',
            'databricks': 'databricks.com',
            'mongodb': 'mongodb.com',
            'docusign': 'docusign.com',
            'box': 'box.com',
            'dropbox': 'dropbox.com',
            'asana': 'asana.com',
            'trello': 'trello.com',
            'notion': 'notion.so'
        }
        
        # Alternative/lesser-known companies by category for diversity
        self.alternative_companies = {
            'crm': ['pipedrive', 'freshworks', 'zoho', 'insightly', 'copper', 'airtable', 'monday.com', 'clickup', 'basecamp'],
            'marketing_automation': ['mailchimp', 'constant_contact', 'sendinblue', 'activecampaign', 'drip', 'convertkit', 'getresponse'],
            'project_management': ['smartsheet', 'wrike', 'teamwork', 'proofhub', 'clarizen', 'workfront', 'liquidplanner'],
            'communication': ['discord', 'mattermost', 'rocket.chat', 'flock', 'chanty', 'ryver', 'twist'],
            'analytics': ['mixpanel', 'amplitude', 'heap', 'fullstory', 'hotjar', 'crazy_egg', 'kissmetrics'],
            'ecommerce': ['bigcommerce', 'woocommerce', 'magento', 'prestashop', 'opencart', 'volusion'],
            'hr': ['bamboohr', 'namely', 'gusto', 'rippling', 'justworks', 'paychex', 'adp'],
            'accounting': ['xero', 'freshbooks', 'wave', 'zoho_books', 'sage', 'netsuite'],
            'cybersecurity': ['crowdstrike', 'sentinelone', 'cylance', 'carbon_black', 'sophos', 'bitdefender'],
            'cloud_storage': ['pcloud', 'sync.com', 'icedrive', 'tresorit', 'spideroak', 'mega']
        }
        
        # Track used URLs to ensure uniqueness across candidates
        self.used_urls = set()
        self.used_domains = set()
        self.candidate_counter = 0
        
        # Authoritative domains for different types of content
        self.authoritative_domains = {
            'comparison': ['g2.com', 'capterra.com', 'trustradius.com', 'softwareadvice.com'],
            'news': ['techcrunch.com', 'venturebeat.com', 'forbes.com', 'businessinsider.com'],
            'research': ['gartner.com', 'forrester.com', 'idc.com', 'mckinsey.com'],
            'reviews': ['g2.com', 'trustpilot.com', 'glassdoor.com']
        }
    
    def generate_queries(self, claim: SearchableClaim, candidate_id: str = None) -> List[SearchQuery]:
        """
        Generate targeted search queries for a claim with diversity and uniqueness.
        
        Args:
            claim: Searchable claim with entities and context
            candidate_id: Unique identifier for candidate to ensure URL diversity
            
        Returns:
            List of optimized search queries
        """
        # Increment counter for diversity
        self.candidate_counter += 1
        
        queries = []
        
        # Strategy 1: Alternative/diverse company searches (prioritize variety)
        queries.extend(self._create_diverse_company_queries(claim))
        
        # Strategy 2: Direct company searches (lower priority to avoid repetition)
        if claim.entities.get('companies'):
            queries.extend(self._create_company_queries(claim))
        
        # Strategy 3: Product-specific searches with alternatives
        if claim.entities.get('products') or claim.claim_type in [ClaimType.PRODUCT_EVALUATION, ClaimType.FEATURE_COMPARISON]:
            queries.extend(self._create_diverse_product_queries(claim))
        
        # Strategy 4: Pricing-specific searches with variety
        if claim.entities.get('pricing_terms') or claim.claim_type == ClaimType.PRICING_RESEARCH:
            queries.extend(self._create_diverse_pricing_queries(claim))
        
        # Strategy 5: Comparison searches with lesser-known alternatives
        if claim.claim_type in [ClaimType.FEATURE_COMPARISON, ClaimType.VENDOR_EVALUATION]:
            queries.extend(self._create_diverse_comparison_queries(claim))
        
        # Strategy 6: Market research searches
        if claim.claim_type == ClaimType.MARKET_RESEARCH:
            queries.extend(self._create_market_research_queries(claim))
        
        # Strategy 7: General activity searches (fallback)
        if not queries or claim.claim_type == ClaimType.GENERAL_ACTIVITY:
            queries.extend(self._create_general_activity_queries(claim))
        
        # Add randomization and diversity
        queries = self._add_query_diversity(queries, claim)
        
        # Sort by priority and limit results
        queries.sort(key=lambda q: q.priority, reverse=True)
        return queries[:7]  # Increased to 7 queries for more variety
    
    def _create_company_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries targeting specific company pages."""
        queries = []
        
        for company in claim.entities.get('companies', []):
            company_lower = company.lower()
            domain = self.company_domains.get(company_lower)
            
            # Direct site search for official pages
            if domain:
                if claim.entities.get('pricing_terms'):
                    query = f"site:{domain} pricing plans cost"
                    queries.append(SearchQuery(
                        query=query,
                        expected_domains=[domain],
                        page_types=['pricing'],
                        priority=10,
                        claim_support=f"Official {company} pricing information",
                        search_strategy="company_pricing_direct"
                    ))
                
                if claim.entities.get('products'):
                    product_terms = ' '.join(claim.entities['products'][:2])
                    query = f"site:{domain} {product_terms} features"
                    queries.append(SearchQuery(
                        query=query,
                        expected_domains=[domain],
                        page_types=['product', 'features'],
                        priority=9,
                        claim_support=f"Official {company} product information",
                        search_strategy="company_product_direct"
                    ))
                
                # General company page search
                activity_terms = ' '.join(claim.entities.get('activities', []))
                query = f"site:{domain} {activity_terms}"
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[domain],
                    page_types=['company', 'about'],
                    priority=8,
                    claim_support=f"Official {company} information",
                    search_strategy="company_general_direct"
                ))
            
            # Broader company searches (not site-restricted)
            if claim.entities.get('pricing_terms'):
                query = f'"{company}" pricing plans cost official'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[domain] if domain else [],
                    page_types=['pricing'],
                    priority=8,
                    claim_support=f"{company} pricing information from authoritative sources",
                    search_strategy="company_pricing_broad"
                ))
        
        return queries
    
    def _create_product_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries for specific product pages."""
        queries = []
        
        products = claim.entities.get('products', [])
        companies = claim.entities.get('companies', [])
        
        # Product + company combinations
        for product in products:
            for company in companies:
                query = f'"{company}" {product} features documentation'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[self.company_domains.get(company.lower())] if self.company_domains.get(company.lower()) else [],
                    page_types=['product', 'documentation'],
                    priority=8,
                    claim_support=f"{company} {product} product information",
                    search_strategy="product_company_specific"
                ))
        
        # General product searches
        if products:
            product_terms = ' '.join(products[:2])
            
            # Product comparison search
            query = f"{product_terms} comparison features best"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['comparison', 'review'],
                priority=7,
                claim_support=f"Product comparison and feature analysis for {product_terms}",
                search_strategy="product_comparison"
            ))
            
            # Product evaluation search
            query = f"{product_terms} evaluation review 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('reviews', []),
                page_types=['review', 'evaluation'],
                priority=6,
                claim_support=f"Product evaluation and reviews for {product_terms}",
                search_strategy="product_evaluation"
            ))
        
        return queries
    
    def _create_pricing_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries specifically for pricing information."""
        queries = []
        
        companies = claim.entities.get('companies', [])
        products = claim.entities.get('products', [])
        
        # Company-specific pricing
        for company in companies:
            query = f'"{company}" pricing cost plans subscription'
            queries.append(SearchQuery(
                query=query,
                expected_domains=[self.company_domains.get(company.lower())] if self.company_domains.get(company.lower()) else [],
                page_types=['pricing'],
                priority=9,
                claim_support=f"{company} pricing and subscription information",
                search_strategy="pricing_company_specific"
            ))
        
        # Product category pricing
        if products:
            product_terms = ' '.join(products[:2])
            query = f"{product_terms} pricing comparison cost 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['pricing', 'comparison'],
                priority=7,
                claim_support=f"Pricing comparison for {product_terms} solutions",
                search_strategy="pricing_category_comparison"
            ))
        
        # General pricing research
        search_terms = ' '.join(claim.search_terms[:3])
        query = f"{search_terms} pricing cost budget ROI"
        queries.append(SearchQuery(
            query=query,
            expected_domains=[],
            page_types=['pricing', 'analysis'],
            priority=6,
            claim_support="General pricing and cost analysis information",
            search_strategy="pricing_general"
        ))
        
        return queries
    
    def _create_comparison_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries for comparison and evaluation content."""
        queries = []
        
        companies = claim.entities.get('companies', [])
        products = claim.entities.get('products', [])
        
        # Company vs company comparisons
        if len(companies) >= 2:
            comp1, comp2 = companies[0], companies[1]
            query = f'"{comp1}" vs "{comp2}" comparison features'
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['comparison'],
                priority=9,
                claim_support=f"Direct comparison between {comp1} and {comp2}",
                search_strategy="company_vs_company"
            ))
        
        # Product category comparisons
        if products:
            product_terms = ' '.join(products[:2])
            query = f"{product_terms} comparison best alternatives 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['comparison', 'alternatives'],
                priority=8,
                claim_support=f"Comparison of {product_terms} alternatives and options",
                search_strategy="product_alternatives"
            ))
        
        # Vendor evaluation
        if companies:
            company_terms = ' '.join(companies[:2])
            query = f"{company_terms} vendor evaluation review pros cons"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('reviews', []),
                page_types=['review', 'evaluation'],
                priority=7,
                claim_support=f"Vendor evaluation and review for {company_terms}",
                search_strategy="vendor_evaluation"
            ))
        
        return queries
    
    def _create_market_research_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries for market research and industry analysis."""
        queries = []
        
        products = claim.entities.get('products', [])
        search_terms = claim.search_terms[:3]
        
        # Industry analysis
        if products:
            product_terms = ' '.join(products[:2])
            query = f"{product_terms} market analysis trends 2024 report"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('research', []),
                page_types=['research', 'report'],
                priority=8,
                claim_support=f"Market analysis and trends for {product_terms} industry",
                search_strategy="market_analysis"
            ))
        
        # Competitive landscape
        terms = ' '.join(search_terms)
        query = f"{terms} competitive landscape market leaders"
        queries.append(SearchQuery(
            query=query,
            expected_domains=self.authoritative_domains.get('research', []),
            page_types=['research', 'analysis'],
            priority=7,
            claim_support="Competitive landscape and market leader analysis",
            search_strategy="competitive_landscape"
        ))
        
        # Industry trends
        query = f"{terms} industry trends digital transformation"
        queries.append(SearchQuery(
            query=query,
            expected_domains=self.authoritative_domains.get('research', []),
            page_types=['trends', 'analysis'],
            priority=6,
            claim_support="Industry trends and transformation insights",
            search_strategy="industry_trends"
        ))
        
        return queries
    
    def _create_general_activity_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create general activity searches as fallback."""
        queries = []
        
        search_terms = claim.search_terms[:4]
        terms = ' '.join(search_terms)
        
        # General search with key terms
        query = f"{terms} guide information"
        queries.append(SearchQuery(
            query=query,
            expected_domains=[],
            page_types=['guide', 'information'],
            priority=5,
            claim_support=f"General information and guidance about {terms}",
            search_strategy="general_information"
        ))
        
        # Activity-specific search
        activities = claim.entities.get('activities', [])
        if activities:
            activity_terms = ' '.join(activities[:2])
            query = f"{activity_terms} {terms} best practices"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['guide', 'best_practices'],
                priority=4,
                claim_support=f"Best practices and guidance for {activity_terms} {terms}",
                search_strategy="activity_best_practices"
            ))
        
        return queries


def test_search_query_generator():
    """Test function for the search query generator."""
    from explanation_analyzer import ExplanationAnalyzer
    
    analyzer = ExplanationAnalyzer()
    generator = SearchQueryGenerator()
    
    # Test explanations
    test_explanations = [
        "Currently researching Salesforce pricing options for enterprise deployment",
        "Actively comparing CRM solutions including HubSpot and Microsoft Dynamics",
        "Investigating marketing automation platforms and their integration capabilities"
    ]
    
    print("Testing Search Query Generator:")
    print("=" * 60)
    
    for i, explanation in enumerate(test_explanations, 1):
        print(f"\n{i}. Explanation: {explanation}")
        claims = analyzer.extract_claims(explanation)
        
        for j, claim in enumerate(claims, 1):
            print(f"\n   Claim {j}: {claim.text}")
            print(f"   Type: {claim.claim_type.value}")
            
            queries = generator.generate_queries(claim)
            print(f"   Generated {len(queries)} search queries:")
            
            for k, query in enumerate(queries, 1):
                print(f"     {k}. Query: {query.query}")
                print(f"        Strategy: {query.search_strategy}")
                print(f"        Priority: {query.priority}")
                print(f"        Expected domains: {query.expected_domains}")
                print(f"        Page types: {query.page_types}")
                print(f"        Support: {query.claim_support}")


if __name__ == '__main__':
    test_search_query_generator()  
  
    def _create_diverse_company_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries targeting diverse/alternative companies for variety."""
        queries = []
        
        # Identify product category from claim
        products = claim.entities.get('products', [])
        category = self._identify_product_category(claim.text, products)
        
        if category and category in self.alternative_companies:
            # Get alternative companies for this category
            alternatives = self.alternative_companies[category]
            
            # Use candidate counter to select different alternatives for each candidate
            selected_alternatives = self._select_diverse_alternatives(alternatives, 2)
            
            for alt_company in selected_alternatives:
                if claim.entities.get('pricing_terms'):
                    query = f'"{alt_company}" pricing plans cost features'
                    queries.append(SearchQuery(
                        query=query,
                        expected_domains=[f"{alt_company}.com"],
                        page_types=['pricing'],
                        priority=9,  # High priority for diversity
                        claim_support=f"Alternative {category} solution pricing information",
                        search_strategy="diverse_company_pricing"
                    ))
                else:
                    query = f'"{alt_company}" features review comparison'
                    queries.append(SearchQuery(
                        query=query,
                        expected_domains=[f"{alt_company}.com"],
                        page_types=['product', 'features'],
                        priority=8,
                        claim_support=f"Alternative {category} solution information",
                        search_strategy="diverse_company_product"
                    ))
        
        return queries
    
    def _create_diverse_product_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create product queries with emphasis on lesser-known alternatives."""
        queries = []
        
        products = claim.entities.get('products', [])
        
        for product in products:
            # Add variety terms to find different solutions
            variety_terms = [
                "alternative", "competitor", "similar", "open source", 
                "startup", "emerging", "new", "innovative"
            ]
            
            # Select different variety term based on candidate counter
            variety_term = variety_terms[self.candidate_counter % len(variety_terms)]
            
            query = f"{product} {variety_term} solutions comparison 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['comparison', 'alternatives'],
                priority=8,
                claim_support=f"Alternative {product} solutions and comparisons",
                search_strategy="diverse_product_alternatives"
            ))
            
            # Add specific niche search
            niche_terms = ["boutique", "specialized", "niche", "enterprise", "SMB", "startup-friendly"]
            niche_term = niche_terms[self.candidate_counter % len(niche_terms)]
            
            query = f"{niche_term} {product} tools review"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['review', 'comparison'],
                priority=7,
                claim_support=f"Specialized {product} tool reviews",
                search_strategy="niche_product_search"
            ))
        
        return queries
    
    def _create_diverse_pricing_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create pricing queries with variety in sources and approaches."""
        queries = []
        
        # Different pricing research approaches
        pricing_approaches = [
            "budget-friendly", "enterprise", "small business", "startup", 
            "cost-effective", "premium", "mid-market", "affordable"
        ]
        
        products = claim.entities.get('products', [])
        companies = claim.entities.get('companies', [])
        
        if products:
            product_terms = ' '.join(products[:2])
            
            # Select different approach based on candidate
            approach = pricing_approaches[self.candidate_counter % len(pricing_approaches)]
            
            query = f"{approach} {product_terms} pricing comparison 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=self.authoritative_domains.get('comparison', []),
                page_types=['pricing', 'comparison'],
                priority=8,
                claim_support=f"Pricing comparison for {approach} {product_terms} solutions",
                search_strategy="diverse_pricing_approach"
            ))
            
            # Add cost analysis from different perspectives
            perspectives = ["ROI analysis", "TCO comparison", "cost breakdown", "pricing tiers"]
            perspective = perspectives[self.candidate_counter % len(perspectives)]
            
            query = f"{product_terms} {perspective} study report"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['analysis', 'report'],
                priority=7,
                claim_support=f"Cost analysis and {perspective} for {product_terms}",
                search_strategy="pricing_analysis_diverse"
            ))
        
        return queries
    
    def _create_diverse_comparison_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create comparison queries focusing on lesser-known alternatives."""
        queries = []
        
        products = claim.entities.get('products', [])
        
        if products:
            product_terms = ' '.join(products[:2])
            
            # Different comparison angles
            comparison_angles = [
                "vs lesser known alternatives", "hidden gems", "underrated options",
                "emerging competitors", "open source alternatives", "indie solutions",
                "bootstrap-friendly", "developer-favorite", "community-driven"
            ]
            
            angle = comparison_angles[self.candidate_counter % len(comparison_angles)]
            
            query = f"{product_terms} {angle} 2024"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['comparison', 'alternatives'],
                priority=8,
                claim_support=f"Alternative and emerging {product_terms} solutions",
                search_strategy="diverse_alternatives_focus"
            ))
            
            # Add specific alternative discovery
            discovery_terms = [
                "ProductHunt", "AlternativeTo", "Slant", "StackShare", 
                "GitHub awesome lists", "indie hackers", "bootstrapped"
            ]
            
            discovery_source = discovery_terms[self.candidate_counter % len(discovery_terms)]
            
            query = f"{product_terms} alternatives {discovery_source}"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['alternatives', 'directory'],
                priority=7,
                claim_support=f"Alternative {product_terms} discovery from {discovery_source}",
                search_strategy="alternative_discovery"
            ))
        
        return queries
    
    def _identify_product_category(self, claim_text: str, products: List[str]) -> Optional[str]:
        """Identify the product category from claim text and products."""
        claim_lower = claim_text.lower()
        
        # Category keywords mapping
        category_keywords = {
            'crm': ['crm', 'customer relationship', 'sales management', 'lead management'],
            'marketing_automation': ['marketing automation', 'email marketing', 'campaign', 'nurturing'],
            'project_management': ['project management', 'task management', 'collaboration', 'workflow'],
            'communication': ['communication', 'chat', 'messaging', 'team communication'],
            'analytics': ['analytics', 'tracking', 'metrics', 'data analysis'],
            'ecommerce': ['ecommerce', 'online store', 'shopping cart', 'e-commerce'],
            'hr': ['hr', 'human resources', 'payroll', 'employee management'],
            'accounting': ['accounting', 'bookkeeping', 'financial', 'invoicing'],
            'cybersecurity': ['security', 'cybersecurity', 'antivirus', 'protection'],
            'cloud_storage': ['storage', 'file sharing', 'backup', 'cloud storage']
        }
        
        # Check products first
        for product in products:
            product_lower = product.lower()
            for category, keywords in category_keywords.items():
                if any(keyword in product_lower for keyword in keywords):
                    return category
        
        # Check claim text
        for category, keywords in category_keywords.items():
            if any(keyword in claim_lower for keyword in keywords):
                return category
        
        return None
    
    def _select_diverse_alternatives(self, alternatives: List[str], count: int) -> List[str]:
        """Select diverse alternatives based on candidate counter to ensure variety."""
        if len(alternatives) <= count:
            return alternatives
        
        # Use candidate counter to select different starting points
        start_index = self.candidate_counter % len(alternatives)
        selected = []
        
        for i in range(count):
            index = (start_index + i) % len(alternatives)
            selected.append(alternatives[index])
        
        return selected
    
    def _add_query_diversity(self, queries: List[SearchQuery], claim: SearchableClaim) -> List[SearchQuery]:
        """Add additional diversity to queries to avoid repetition."""
        # Add randomization terms
        randomization_terms = [
            "2024", "latest", "new", "updated", "recent", "current", 
            "best", "top", "leading", "popular", "trending", "emerging"
        ]
        
        # Add geographic diversity
        geo_terms = [
            "US", "North America", "global", "international", 
            "enterprise", "SMB", "startup", "mid-market"
        ]
        
        # Add source diversity
        source_terms = [
            "review", "comparison", "analysis", "guide", "report", 
            "study", "survey", "benchmark", "evaluation"
        ]
        
        enhanced_queries = []
        
        for i, query in enumerate(queries):
            # Add variety terms based on position and candidate counter
            rand_term = randomization_terms[(self.candidate_counter + i) % len(randomization_terms)]
            geo_term = geo_terms[(self.candidate_counter + i) % len(geo_terms)]
            source_term = source_terms[(self.candidate_counter + i) % len(source_terms)]
            
            # Enhance query with diversity terms
            if i % 3 == 0:  # Every third query gets randomization
                enhanced_query = f"{query.query} {rand_term}"
            elif i % 3 == 1:  # Every third query gets geographic focus
                enhanced_query = f"{geo_term} {query.query}"
            else:  # Remaining queries get source diversity
                enhanced_query = f"{query.query} {source_term}"
            
            # Create new query with enhanced search
            enhanced_queries.append(SearchQuery(
                query=enhanced_query,
                expected_domains=query.expected_domains,
                page_types=query.page_types,
                priority=query.priority,
                claim_support=query.claim_support,
                search_strategy=f"{query.search_strategy}_diverse"
            ))
        
        return enhanced_queries