#!/usr/bin/env python3
"""
Fallback and Alternative Discovery Strategies for URL Diversity Enhancement.

This module provides fallback strategies when primary diverse sources are
exhausted or when uniqueness constraints cannot be met.
"""

import random
from typing import List, Dict, Set, Optional, Any, Tuple
from dataclasses import dataclass

from alternative_source_manager import AlternativeSourceManager, AlternativeSource, SourceTier
from explanation_analyzer import SearchableClaim, ClaimType
from search_query_generator import SearchQuery


@dataclass
class FallbackResult:
    """Result from a fallback strategy."""
    queries: List[SearchQuery]
    strategy_used: str
    success: bool
    fallback_level: int  # 1=primary, 2=secondary, 3=tertiary


class FallbackStrategyManager:
    """
    Manages fallback strategies when primary diverse sources are exhausted
    or when uniqueness constraints cannot be met.
    """
    
    def __init__(self):
        self.alternative_source_manager = AlternativeSourceManager()
        
        # Fallback strategy configurations
        self.fallback_strategies = {
            'category_expansion': self._category_expansion_strategy,
            'temporal_variation': self._temporal_variation_strategy,
            'geographic_variation': self._geographic_variation_strategy,
            'indirect_evidence': self._indirect_evidence_strategy,
            'creative_alternatives': self._creative_alternatives_strategy,
            'quality_relaxation': self._quality_relaxation_strategy
        }
        
        # Alternative discovery sources
        self.discovery_platforms = [
            'ProductHunt', 'AlternativeTo', 'Slant', 'StackShare',
            'G2 Crowd', 'Capterra', 'TrustRadius', 'SoftwareAdvice',
            'indie hackers', 'bootstrapped', 'open source',
            'GitHub awesome lists', 'Reddit recommendations'
        ]
        
        # Creative search modifiers
        self.creative_modifiers = [
            'hidden gems', 'underrated', 'lesser known', 'boutique',
            'specialized', 'niche', 'emerging', 'startup',
            'indie', 'community favorite', 'developer choice',
            'bootstrap friendly', 'cost effective', 'simple'
        ]
    
    def apply_fallback_strategies(
        self,
        claim: SearchableClaim,
        used_sources: Set[str],
        failed_strategies: List[str] = None,
        max_fallback_level: int = 3
    ) -> List[FallbackResult]:
        """
        Apply fallback strategies to find alternative sources.
        
        Args:
            claim: Original searchable claim
            used_sources: Sources already used (to avoid)
            failed_strategies: Strategies that have already failed
            max_fallback_level: Maximum fallback level to attempt
            
        Returns:
            List of fallback results with queries
        """
        failed_strategies = failed_strategies or []
        fallback_results = []
        
        print(f"[Fallback] Applying fallback strategies for claim: {claim.text[:50]}...")
        
        # Level 1: Category expansion and related searches
        if max_fallback_level >= 1:
            level1_results = self._apply_level1_fallbacks(claim, used_sources, failed_strategies)
            fallback_results.extend(level1_results)
        
        # Level 2: Creative and indirect approaches
        if max_fallback_level >= 2:
            level2_results = self._apply_level2_fallbacks(claim, used_sources, failed_strategies)
            fallback_results.extend(level2_results)
        
        # Level 3: Last resort strategies
        if max_fallback_level >= 3:
            level3_results = self._apply_level3_fallbacks(claim, used_sources, failed_strategies)
            fallback_results.extend(level3_results)
        
        print(f"[Fallback] Generated {len(fallback_results)} fallback strategies")
        
        return fallback_results
    
    def _apply_level1_fallbacks(
        self,
        claim: SearchableClaim,
        used_sources: Set[str],
        failed_strategies: List[str]
    ) -> List[FallbackResult]:
        """Apply level 1 fallback strategies (category expansion, temporal variation)."""
        results = []
        
        # Strategy 1: Category expansion
        if 'category_expansion' not in failed_strategies:
            try:
                queries = self._category_expansion_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='category_expansion',
                        success=True,
                        fallback_level=1
                    ))
            except Exception as e:
                print(f"[Fallback] Category expansion failed: {e}")
        
        # Strategy 2: Temporal variation
        if 'temporal_variation' not in failed_strategies:
            try:
                queries = self._temporal_variation_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='temporal_variation',
                        success=True,
                        fallback_level=1
                    ))
            except Exception as e:
                print(f"[Fallback] Temporal variation failed: {e}")
        
        return results
    
    def _apply_level2_fallbacks(
        self,
        claim: SearchableClaim,
        used_sources: Set[str],
        failed_strategies: List[str]
    ) -> List[FallbackResult]:
        """Apply level 2 fallback strategies (geographic, indirect evidence)."""
        results = []
        
        # Strategy 3: Geographic variation
        if 'geographic_variation' not in failed_strategies:
            try:
                queries = self._geographic_variation_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='geographic_variation',
                        success=True,
                        fallback_level=2
                    ))
            except Exception as e:
                print(f"[Fallback] Geographic variation failed: {e}")
        
        # Strategy 4: Indirect evidence
        if 'indirect_evidence' not in failed_strategies:
            try:
                queries = self._indirect_evidence_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='indirect_evidence',
                        success=True,
                        fallback_level=2
                    ))
            except Exception as e:
                print(f"[Fallback] Indirect evidence failed: {e}")
        
        return results
    
    def _apply_level3_fallbacks(
        self,
        claim: SearchableClaim,
        used_sources: Set[str],
        failed_strategies: List[str]
    ) -> List[FallbackResult]:
        """Apply level 3 fallback strategies (creative alternatives, quality relaxation)."""
        results = []
        
        # Strategy 5: Creative alternatives
        if 'creative_alternatives' not in failed_strategies:
            try:
                queries = self._creative_alternatives_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='creative_alternatives',
                        success=True,
                        fallback_level=3
                    ))
            except Exception as e:
                print(f"[Fallback] Creative alternatives failed: {e}")
        
        # Strategy 6: Quality relaxation (broader searches)
        if 'quality_relaxation' not in failed_strategies:
            try:
                queries = self._quality_relaxation_strategy(claim, used_sources)
                if queries:
                    results.append(FallbackResult(
                        queries=queries,
                        strategy_used='quality_relaxation',
                        success=True,
                        fallback_level=3
                    ))
            except Exception as e:
                print(f"[Fallback] Quality relaxation failed: {e}")
        
        return results
    
    def _category_expansion_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Expand to related categories when primary category is exhausted."""
        queries = []
        
        # Identify primary category
        primary_category = self.alternative_source_manager.identify_category_from_claim(
            claim.text, claim.entities
        )
        
        if not primary_category:
            return queries
        
        # Define category relationships
        category_expansions = {
            'real_estate': ['financial_services', 'investment_forums', 'analytics'],
            'crm': ['marketing_automation', 'project_management', 'communication'],
            'marketing_automation': ['crm', 'analytics', 'ecommerce'],
            'project_management': ['communication', 'crm', 'hr'],
            'financial_services': ['real_estate', 'accounting', 'analytics'],
            'investment_forums': ['real_estate', 'financial_services', 'analytics']
        }
        
        # Get related categories
        related_categories = category_expansions.get(primary_category, [])
        
        # Generate queries for related categories
        search_terms = ' '.join(claim.search_terms[:3])
        
        for related_category in related_categories[:2]:  # Limit to 2 related categories
            # Get sources from related category
            related_sources = self.alternative_source_manager.get_alternative_companies(
                related_category,
                exclude=used_sources,
                count=2
            )
            
            for source in related_sources:
                query = f'"{source.name}" {search_terms} integration solution'
                queries.append(SearchQuery(
                    query=query,
                    expected_domains=[source.domain],
                    page_types=['product', 'integration'],
                    priority=6,
                    claim_support=f"Related {related_category} solution for {search_terms}",
                    search_strategy=f"category_expansion_{related_category}"
                ))
        
        return queries
    
    def _temporal_variation_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Add temporal variations to find different content."""
        queries = []
        
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Temporal modifiers
        temporal_modifiers = [
            '2024', '2023', 'latest', 'new', 'updated',
            'recent', 'current', 'modern', 'next generation'
        ]
        
        # Create temporal queries
        for modifier in temporal_modifiers[:3]:  # Use top 3
            query = f"{search_terms} {modifier} alternatives comparison"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['comparison', 'review'],
                priority=5,
                claim_support=f"Temporal variation search for {search_terms} ({modifier})",
                search_strategy=f"temporal_variation_{modifier}"
            ))
        
        return queries
    
    def _geographic_variation_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Add geographic variations to find regional alternatives."""
        queries = []
        
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Geographic modifiers
        geographic_modifiers = [
            'European', 'UK', 'Canadian', 'Australian',
            'international', 'global', 'regional', 'local'
        ]
        
        # Create geographic queries
        for modifier in geographic_modifiers[:3]:  # Use top 3
            query = f"{modifier} {search_terms} alternatives solutions"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['alternatives', 'comparison'],
                priority=5,
                claim_support=f"Geographic variation search for {search_terms} ({modifier})",
                search_strategy=f"geographic_variation_{modifier}"
            ))
        
        return queries
    
    def _indirect_evidence_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Find indirect evidence like case studies, reviews, or industry reports."""
        queries = []
        
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Indirect evidence types
        indirect_types = [
            'case study', 'success story', 'implementation',
            'review', 'comparison', 'analysis',
            'industry report', 'market research', 'survey',
            'best practices', 'lessons learned', 'experience'
        ]
        
        # Create indirect evidence queries
        for evidence_type in indirect_types[:4]:  # Use top 4
            query = f"{search_terms} {evidence_type} examples"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['case_study', 'review', 'report'],
                priority=4,
                claim_support=f"Indirect evidence search for {search_terms} ({evidence_type})",
                search_strategy=f"indirect_evidence_{evidence_type.replace(' ', '_')}"
            ))
        
        return queries
    
    def _creative_alternatives_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Use creative search approaches and discovery platforms."""
        queries = []
        
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Use discovery platforms
        selected_platforms = random.sample(self.discovery_platforms, min(3, len(self.discovery_platforms)))
        
        for platform in selected_platforms:
            query = f"{search_terms} alternatives {platform}"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['alternatives', 'directory'],
                priority=4,
                claim_support=f"Creative discovery via {platform} for {search_terms}",
                search_strategy=f"creative_discovery_{platform.replace(' ', '_')}"
            ))
        
        # Use creative modifiers
        selected_modifiers = random.sample(self.creative_modifiers, min(3, len(self.creative_modifiers)))
        
        for modifier in selected_modifiers:
            query = f"{modifier} {search_terms} tools solutions"
            queries.append(SearchQuery(
                query=query,
                expected_domains=[],
                page_types=['alternatives', 'review'],
                priority=4,
                claim_support=f"Creative search for {modifier} {search_terms} solutions",
                search_strategy=f"creative_modifier_{modifier.replace(' ', '_')}"
            ))
        
        return queries
    
    def _quality_relaxation_strategy(
        self,
        claim: SearchableClaim,
        used_sources: Set[str]
    ) -> List[SearchQuery]:
        """Relax quality constraints for broader search results."""
        queries = []
        
        search_terms = ' '.join(claim.search_terms[:3])
        
        # Broader, more general searches
        broad_searches = [
            f"{search_terms} options",
            f"{search_terms} tools",
            f"{search_terms} software",
            f"{search_terms} platforms",
            f"{search_terms} services",
            f"{search_terms} solutions"
        ]
        
        for broad_search in broad_searches[:3]:  # Use top 3
            queries.append(SearchQuery(
                query=broad_search,
                expected_domains=[],
                page_types=['general_information'],
                priority=3,
                claim_support=f"Broad search for {search_terms} with relaxed quality constraints",
                search_strategy="quality_relaxation_broad"
            ))
        
        return queries
    
    def get_fallback_recommendations(
        self,
        claim: SearchableClaim,
        used_sources: Set[str],
        failed_attempts: int
    ) -> List[str]:
        """Get recommendations for improving fallback success."""
        recommendations = []
        
        # Analyze the situation
        primary_category = self.alternative_source_manager.identify_category_from_claim(
            claim.text, claim.entities
        )
        
        if not primary_category:
            recommendations.append(
                "Consider manually specifying the product category for better source discovery"
            )
        
        if len(used_sources) > 10:
            recommendations.append(
                "Many sources already used. Consider relaxing uniqueness constraints or expanding search scope"
            )
        
        if failed_attempts > 3:
            recommendations.append(
                "Multiple fallback attempts failed. Consider using more general search terms or reducing diversity requirements"
            )
        
        # Category-specific recommendations
        if primary_category:
            available_sources = self.alternative_source_manager.get_alternative_companies(
                primary_category, exclude=used_sources, count=10
            )
            
            if len(available_sources) < 3:
                recommendations.append(
                    f"Limited alternative sources available for {primary_category}. "
                    "Consider expanding to related categories or using broader search terms"
                )
        
        return recommendations


def test_fallback_strategies():
    """Test function for fallback strategies."""
    print("Testing Fallback Strategies:")
    print("=" * 50)
    
    # Create manager
    fallback_manager = FallbackStrategyManager()
    
    # Create test claim
    from explanation_analyzer import SearchableClaim, ClaimType
    
    test_claim = SearchableClaim(
        text="Researching luxury real estate investment opportunities in Greenwich",
        entities={'activities': ['researching'], 'products': ['real estate'], 'locations': ['Greenwich']},
        claim_type=ClaimType.MARKET_RESEARCH,
        priority=8,
        search_terms=['luxury', 'real estate', 'investment', 'Greenwich'],
        confidence=0.8
    )
    
    # Simulate used sources
    used_sources = {
        'zillow.com', 'realtor.com', 'sothebysrealty.com', 
        'compass.com', 'redfin.com'
    }
    
    print(f"Test claim: {test_claim.text}")
    print(f"Used sources: {len(used_sources)}")
    print()
    
    # Test fallback strategies
    print("1. Testing Level 1 Fallbacks (Category Expansion, Temporal):")
    level1_results = fallback_manager._apply_level1_fallbacks(test_claim, used_sources, [])
    
    for result in level1_results:
        print(f"   Strategy: {result.strategy_used}")
        print(f"   Queries generated: {len(result.queries)}")
        for query in result.queries[:2]:  # Show first 2
            print(f"     - {query.query}")
        print()
    
    print("2. Testing Level 2 Fallbacks (Geographic, Indirect):")
    level2_results = fallback_manager._apply_level2_fallbacks(test_claim, used_sources, [])
    
    for result in level2_results:
        print(f"   Strategy: {result.strategy_used}")
        print(f"   Queries generated: {len(result.queries)}")
        for query in result.queries[:2]:  # Show first 2
            print(f"     - {query.query}")
        print()
    
    print("3. Testing Level 3 Fallbacks (Creative, Quality Relaxation):")
    level3_results = fallback_manager._apply_level3_fallbacks(test_claim, used_sources, [])
    
    for result in level3_results:
        print(f"   Strategy: {result.strategy_used}")
        print(f"   Queries generated: {len(result.queries)}")
        for query in result.queries[:2]:  # Show first 2
            print(f"     - {query.query}")
        print()
    
    # Test recommendations
    print("4. Testing Fallback Recommendations:")
    recommendations = fallback_manager.get_fallback_recommendations(test_claim, used_sources, 2)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")


if __name__ == '__main__':
    test_fallback_strategies()