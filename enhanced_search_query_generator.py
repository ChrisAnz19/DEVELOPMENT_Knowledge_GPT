#!/usr/bin/env python3
"""
Enhanced Search Query Generator for URL Diversity Enhancement.

This module extends the existing SearchQueryGenerator with diversity-focused
strategies to find varied and lesser-known sources.
"""

import random
from typing import List, Dict, Set, Optional
from dataclasses import dataclass

# Import existing components
from search_query_generator import SearchQueryGenerator, SearchQuery
from alternative_source_manager import AlternativeSourceManager, SourceTier
from explanation_analyzer import SearchableClaim, ClaimType


@dataclass
class DiversityConfig:
    """Configuration for diversity-focused query generation."""
    diversity_weight: float = 0.3           # Weight of diversity vs relevance
    max_major_sources_per_batch: int = 2    # Limit major company sources
    min_alternative_sources: int = 3        # Minimum alternative sources
    enable_source_rotation: bool = True     # Enable rotation across candidates
    exclude_domains: Set[str] = None        # Domains to avoid
    diversity_mode: str = "balanced"        # balanced, aggressive, conservative
    
    def __post_init__(self):
        if self.exclude_domains is None:
            self.exclude_domains = set()


class EnhancedSearchQueryGenerator(SearchQueryGenerator):
    """
    Enhanced search query generator with diversity-focused strategies
    to find varied and lesser-known sources.
    """
    
    def __init__(self, diversity_config: DiversityConfig = None):
        super().__init__()
        
        # Initialize diversity components
        self.alternative_source_manager = AlternativeSourceManager()
        self.diversity_config = diversity_config or DiversityConfig()
        
        # Track used sources across candidates
        self.used_sources_global = set()
        self.candidate_source_history = {}
        
        # Diversity query modifiers
        self.diversity_modifiers = self._initialize_diversity_modifiers()
        
        # Alternative search strategies
        self.alternative_strategies = self._initialize_alternative_strategies()
    
    def generate_diverse_queries(
        self,
        claim: SearchableClaim,
        candidate_id: str,
        used_sources: Set[str] = None,
        candidate_index: int = None
    ) -> List[SearchQuery]:
        """
        Generate queries prioritizing unused and diverse sources.
        
        Args:
            claim: Searchable claim with entities and context
            candidate_id: Unique identifier for candidate
            used_sources: Sources already used (for this candidate or globally)
            candidate_index: Index of candidate for deterministic rotation
            
        Returns:
            List of diversity-focused search queries
        """
        used_sources = used_sources or set()
        all_used = used_sources.union(self.used_sources_global)
        
        queries = []
        
        # Strategy 1: Alternative company queries (highest priority for diversity)
        alt_queries = self.create_alternative_company_queries(claim, all_used, candidate_index)
        queries.extend(alt_queries)
        
        # Strategy 2: Niche and specialized source queries
        niche_queries = self._create_niche_source_queries(claim, all_used)
        queries.extend(niche_queries)
        
        # Strategy 3: Diversity-modified general queries
        modified_queries = self._create_diversity_modified_queries(claim, all_used)
        queries.extend(modified_queries)
        
        # Strategy 4: Alternative discovery queries
        discovery_queries = self._create_alternative_discovery_queries(claim, candidate_index)
        queries.extend(discovery_queries)
        
        # Strategy 5: Exclusion-based queries (avoid major players)
        exclusion_queries = self._create_exclusion_based_queries(claim)
        queries.extend(exclusion_queries)
        
        # Apply diversity scoring and ranking
        scored_queries = self._apply_diversity_scoring(queries, claim, all_used)
        
        # Sort by diversity-adjusted priority
        scored_queries.sort(key=lambda q: q.priority, reverse=True)
        
        # Track used sources
        self._track_query_sources(scored_queries, candidate_id)
        
        return scored_queries[:8]  # Return top 8 diverse queries
    
    def create_alternative_company_queries(
        self,
        claim: SearchableClaim,
        excluded_sources: Set[str],
        candidate_index: int = None
    ) -> List[SearchQuery]:
        """
        Create queries targeting alternative/lesser-known companies.
        
        Args:
            claim: Searchable claim
            excluded_sources: Sources to exclude
            candidate_index: Index for rotation
            
        Returns:
            List of alternative company queries
        """
        queries = []
        
        # Identify category
        category = self.alternative_source_manager.identify_category_from_claim(
            claim.text, claim.entities
        )
        
        if not category:
            return queries
        
        # Get alternative companies
        alternatives = self.alternative_source_manager.get_alternative_companies(
            category=category,
            exclude=excluded_sources,
            count=4,
            tier_preference=[SourceTier.ALTERNATIVE, SourceTier.NICHE, SourceTier.MID_TIER]
        )
        
        # Apply rotation if candidate index provided
        if candidate_index is not None and alternatives:
            alternatives = self.alternative_source_manager.rotate_source_selection(
                alternatives, category, candidate_index
            )
        
        # Create queries for each alternative
        for alt in alternatives:
            # Pricing query
            if claim.entities.get('pricing_terms') or claim.claim_type == ClaimType.PRICING_RESEARCH:
                query = f'"{alt.name}" pricing plans cost features'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[alt.domain],
                    page_types=['pricing'],
                    priority=9,  # High priority for diversity
                    claim_support=f"Alternative {category} solution pricing from {alt.name}",
                    search_strategy="diverse_alternative_pricing"
                ))
            
            # Product/feature query
            if claim.entities.get('products') or claim.claim_type == ClaimType.PRODUCT_EVALUATION:
                product_terms = ' '.join(claim.entities.get('products', [category])[:2])
                query = f'"{alt.name}" {product_terms} features review'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[alt.domain],
                    page_types=['product', 'features'],
                    priority=8,
                    claim_support=f"Alternative {category} product information from {alt.name}",
                    search_strategy="diverse_alternative_product"
                ))
            
            # General company query
            activity_terms = ' '.join(claim.entities.get('activities', [])[:2])
            query = f'"{alt.name}" {activity_terms} solution'
            queries.append(SearchQuery(
                query=query,
                expected_domains=[alt.domain],
                page_types=['company', 'solution'],
                priority=7,
                claim_support=f"Alternative {category} solution from {alt.name}",
                search_strategy="diverse_alternative_general"
            ))
        
        return queries
    
    def apply_diversity_modifiers(
        self,
        base_query: str,
        diversity_level: int = 1
    ) -> List[str]:
        """
        Apply modifiers to increase source diversity.
        
        Args:
            base_query: Base search query
            diversity_level: Level of diversity (1-3, higher = more diverse)
            
        Returns:
            List of modified queries with diversity terms
        """
        modified_queries = []
        
        # Get appropriate modifiers for diversity level
        if diversity_level == 1:
            modifiers = self.diversity_modifiers['conservative']
        elif diversity_level == 2:
            modifiers = self.diversity_modifiers['balanced']
        else:
            modifiers = self.diversity_modifiers['aggressive']
        
        # Apply modifiers
        for modifier in modifiers:
            if modifier.startswith('-'):
                # Exclusion modifier
                modified_query = f"{base_query} {modifier}"
            else:
                # Inclusion modifier
                modified_query = f"{base_query} {modifier}"
            
            modified_queries.append(modified_query)
        
        return modified_queries
    
    def _create_niche_source_queries(
        self,
        claim: SearchableClaim,
        excluded_sources: Set[str]
    ) -> List[SearchQuery]:
        """Create queries targeting niche and specialized sources."""
        queries = []
        
        # Identify category
        category = self.alternative_source_manager.identify_category_from_claim(
            claim.text, claim.entities
        )
        
        if not category:
            return queries
        
        # Get niche sources
        niche_sources = self.alternative_source_manager.get_niche_sources(
            category=category,
            search_terms=claim.search_terms,
            exclude=excluded_sources,
            count=3
        )
        
        # Create queries for niche sources
        for source in niche_sources:
            search_terms = ' '.join(claim.search_terms[:3])
            query = f'"{source.name}" {search_terms} review comparison'
            
            queries.append(SearchQuery(
                query=query,
                expected_domains=[source.domain],
                page_types=['review', 'comparison'],
                priority=8,
                claim_support=f"Specialized {category} solution from {source.name}",
                search_strategy="niche_source_targeted"
            ))
        
        return queries
    
    def _create_diversity_modified_queries(
        self,
        claim: SearchableClaim,
        excluded_sources: Set[str]
    ) -> List[SearchQuery]:
        """Create general queries with diversity modifiers applied."""
        queries = []
        
        # Base query from search terms
        base_terms = ' '.join(claim.search_terms[:3])
        
        # Apply different diversity levels
        for level in [1, 2, 3]:
            modified_queries = self.apply_diversity_modifiers(base_terms, level)
            
            for modified_query in modified_queries[:2]:  # Limit to 2 per level
                queries.append(SearchQuery(
                    query=modified_query,
                    expected_domains=[],
                    page_types=['comparison', 'alternatives'],
                    priority=6 + level,  # Higher priority for more diverse queries
                    claim_support=f"Diverse sources for {base_terms} with level {level} diversity",
                    search_strategy=f"diversity_modified_level_{level}"
                ))
        
        return queries
    
    def _create_alternative_discovery_queries(
        self,
        claim: SearchableClaim,
        candidate_index: int = None
    ) -> List[SearchQuery]:
        """Create queries using alternative discovery strategies."""
        queries = []
        
        # Get base terms
        search_terms = ' '.join(claim.search_terms[:2])
        
        # Alternative discovery sources
        discovery_sources = [
            "ProductHunt", "AlternativeTo", "Slant", "StackShare",
            "indie hackers", "bootstrapped", "open source"
        ]
        
        # Rotate discovery sources based on candidate
        if candidate_index is not None:
            start_idx = candidate_index % len(discovery_sources)
            discovery_sources = discovery_sources[start_idx:] + discovery_sources[:start_idx]
        
        # Create discovery queries
        for source in discovery_sources[:3]:  # Use top 3
            query = f"{search_terms} alternatives {source}"
            
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['alternatives', 'directory'],
                priority=7,
                claim_support=f"Alternative discovery for {search_terms} via {source}",
                search_strategy="alternative_discovery"
            ))
        
        return queries
    
    def _create_exclusion_based_queries(self, claim: SearchableClaim) -> List[SearchQuery]:
        """Create queries that explicitly exclude major players."""
        queries = []
        
        # Identify category for exclusions
        category = self.alternative_source_manager.identify_category_from_claim(
            claim.text, claim.entities
        )
        
        if not category:
            return queries
        
        # Get exclusion terms
        exclusion_terms = self.alternative_source_manager.get_exclusion_terms_for_diversity(category)
        
        # Create exclusion-based queries
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Basic exclusion query
        exclusions = ' '.join(exclusion_terms[:5])  # Use top 5 exclusions
        query = f"{search_terms} {exclusions}"
        
        queries.append(SearchQuery(
            query=query,
            expected_domains=[],
            page_types=['alternatives', 'comparison'],
            priority=6,
            claim_support=f"Diverse sources excluding major players for {search_terms}",
            search_strategy="major_exclusion"
        ))
        
        return queries
    
    def _apply_diversity_scoring(
        self,
        queries: List[SearchQuery],
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Apply diversity scoring to adjust query priorities."""
        scored_queries = []
        
        for query in queries:
            # Calculate diversity bonus
            diversity_bonus = 0
            
            # Bonus for alternative/niche strategies
            if query.search_strategy.startswith(('diverse_', 'niche_', 'alternative_')):
                diversity_bonus += 2
            
            # Bonus for exclusion strategies
            if 'exclusion' in query.search_strategy:
                diversity_bonus += 1
            
            # Bonus for unused domains
            if query.expected_domains:
                domain = query.expected_domains[0]
                if domain not in used_sources:
                    diversity_bonus += 1
            
            # Apply diversity weight
            diversity_adjustment = diversity_bonus * self.diversity_config.diversity_weight
            
            # Create new query with adjusted priority
            adjusted_query = SearchQuery(
                query=query.query,
                expected_domains=query.expected_domains,
                page_types=query.page_types,
                priority=query.priority + diversity_adjustment,
                claim_support=query.claim_support,
                search_strategy=query.search_strategy
            )
            
            scored_queries.append(adjusted_query)
        
        return scored_queries
    
    def _track_query_sources(self, queries: List[SearchQuery], candidate_id: str):
        """Track sources used in queries for future diversity."""
        if candidate_id not in self.candidate_source_history:
            self.candidate_source_history[candidate_id] = set()
        
        for query in queries:
            # Track expected domains
            for domain in query.expected_domains:
                self.used_sources_global.add(domain)
                self.candidate_source_history[candidate_id].add(domain)
            
            # Track company names mentioned in queries
            query_lower = query.query.lower()
            for company in self.alternative_source_manager.major_companies:
                if company.lower() in query_lower:
                    self.used_sources_global.add(company.lower())
                    self.candidate_source_history[candidate_id].add(company.lower())
    
    def _initialize_diversity_modifiers(self) -> Dict[str, List[str]]:
        """Initialize diversity modifiers for different levels."""
        return {
            'conservative': [
                'alternatives', 'options', 'competitors', 'similar'
            ],
            'balanced': [
                'alternatives', 'lesser known', 'emerging', 'startup',
                'open source', 'indie', '-salesforce', '-hubspot'
            ],
            'aggressive': [
                'hidden gems', 'underrated', 'boutique', 'specialized',
                'niche', 'indie hackers', 'bootstrapped', 'community driven',
                '-salesforce', '-hubspot', '-microsoft', '-google'
            ]
        }
    
    def _initialize_alternative_strategies(self) -> List[str]:
        """Initialize alternative search strategies."""
        return [
            'ProductHunt alternatives',
            'AlternativeTo recommendations',
            'Slant comparisons',
            'StackShare alternatives',
            'GitHub awesome lists',
            'indie hacker tools',
            'bootstrapped solutions',
            'open source alternatives',
            'community recommendations',
            'developer favorites'
        ]
    
    def reset_diversity_tracking(self):
        """Reset diversity tracking (for testing or new sessions)."""
        self.used_sources_global.clear()
        self.candidate_source_history.clear()
    
    def get_diversity_stats(self) -> Dict[str, any]:
        """Get diversity tracking statistics."""
        return {
            'total_sources_used': len(self.used_sources_global),
            'candidates_processed': len(self.candidate_source_history),
            'average_sources_per_candidate': (
                sum(len(sources) for sources in self.candidate_source_history.values()) /
                max(len(self.candidate_source_history), 1)
            ),
            'diversity_config': {
                'diversity_weight': self.diversity_config.diversity_weight,
                'diversity_mode': self.diversity_config.diversity_mode,
                'max_major_sources': self.diversity_config.max_major_sources_per_batch
            }
        }


def test_enhanced_search_query_generator():
    """Test function for the Enhanced Search Query Generator."""
    from explanation_analyzer import ExplanationAnalyzer
    
    print("Testing Enhanced Search Query Generator:")
    print("=" * 60)
    
    # Create components
    analyzer = ExplanationAnalyzer()
    diversity_config = DiversityConfig(diversity_mode="balanced", diversity_weight=0.4)
    generator = EnhancedSearchQueryGenerator(diversity_config)
    
    # Test explanations
    test_explanations = [
        "Currently researching CRM solutions for small business",
        "Evaluating project management tools for remote team",
        "Investigating marketing automation platforms for ecommerce"
    ]
    
    for i, explanation in enumerate(test_explanations):
        print(f"\n{i+1}. Explanation: {explanation}")
        claims = analyzer.extract_claims(explanation)
        
        for j, claim in enumerate(claims):
            print(f"\n   Claim {j+1}: {claim.text}")
            print(f"   Type: {claim.claim_type.value}")
            
            # Generate diverse queries
            diverse_queries = generator.generate_diverse_queries(
                claim, 
                candidate_id=f"candidate_{i+1}",
                candidate_index=i
            )
            
            print(f"   Generated {len(diverse_queries)} diverse queries:")
            
            for k, query in enumerate(diverse_queries[:5], 1):  # Show top 5
                print(f"     {k}. Query: {query.query}")
                print(f"        Strategy: {query.search_strategy}")
                print(f"        Priority: {query.priority:.1f}")
                print(f"        Domains: {query.expected_domains}")
    
    # Show diversity stats
    print(f"\nDiversity Statistics:")
    stats = generator.get_diversity_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    test_enhanced_search_query_generator()