#!/usr/bin/env python3
"""
Simplified Diversity Orchestrator for URL Evidence Enhancement.

This module provides a streamlined approach to ensuring URL diversity
while maintaining relevance to actual behavioral claims.
"""

import time
from typing import List, Dict, Set, Optional, Any
from dataclasses import dataclass

# Import components
from global_url_registry import GlobalURLRegistry
from alternative_source_manager import AlternativeSourceManager
from enhanced_search_query_generator import EnhancedSearchQueryGenerator, DiversityConfig
from uniqueness_aware_evidence_validator import UniquenessAwareEvidenceValidator, EnhancedEvidenceURL
from explanation_analyzer import ExplanationAnalyzer, SearchableClaim
from web_search_engine import WebSearchEngine
from evidence_models import create_enhanced_candidate_response


@dataclass
class SimplifiedDiversityConfig:
    """Simplified configuration for diversity processing."""
    ensure_url_uniqueness: bool = True      # Ensure no duplicate URLs across candidates
    max_same_domain_per_candidate: int = 1  # Max URLs from same domain per candidate
    prioritize_alternatives: bool = True     # Prioritize alternative sources over major ones
    diversity_weight: float = 0.3           # Weight given to diversity vs relevance


class SimplifiedDiversityOrchestrator:
    """
    Simplified orchestrator that ensures URL diversity while maintaining
    strong relevance to actual behavioral claims.
    """
    
    def __init__(self, config: SimplifiedDiversityConfig = None):
        # Configuration
        self.config = config or SimplifiedDiversityConfig()
        
        # Core components
        self.global_registry = GlobalURLRegistry()
        self.alternative_source_manager = AlternativeSourceManager()
        self.explanation_analyzer = ExplanationAnalyzer()
        
        # Enhanced components with diversity
        diversity_config = DiversityConfig(
            diversity_weight=self.config.diversity_weight,
            diversity_mode="balanced"
        )
        self.enhanced_query_generator = EnhancedSearchQueryGenerator(diversity_config)
        self.uniqueness_validator = UniquenessAwareEvidenceValidator(self.global_registry)
        
        # Web search engine (will be injected)
        self.web_search_engine = None
        
        # Statistics
        self.stats = {
            'candidates_processed': 0,
            'urls_found': 0,
            'unique_domains': 0,
            'diversity_score': 0.0
        }
    
    def set_web_search_engine(self, web_search_engine: WebSearchEngine):
        """Set the web search engine (dependency injection)."""
        self.web_search_engine = web_search_engine
    
    async def process_candidates_with_diversity(
        self,
        candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process candidates ensuring URL diversity while maintaining relevance.
        
        Args:
            candidates: List of candidate dictionaries with explanations
            
        Returns:
            List of enhanced candidates with diverse, relevant URLs
        """
        if not self.web_search_engine:
            raise ValueError("Web search engine not set. Call set_web_search_engine() first.")
        
        enhanced_candidates = []
        
        print(f"[Diversity Orchestrator] Processing {len(candidates)} candidates with diversity")
        
        for i, candidate in enumerate(candidates):
            try:
                enhanced_candidate = await self._process_single_candidate(
                    candidate, candidate_index=i
                )
                enhanced_candidates.append(enhanced_candidate)
                
                # Update statistics
                self.stats['candidates_processed'] += 1
                
            except Exception as e:
                print(f"[Diversity Orchestrator] Error processing candidate {candidate.get('id', 'unknown')}: {e}")
                # Return original candidate on error
                enhanced_candidates.append(candidate)
        
        # Update final statistics
        self._update_final_statistics()
        
        print(f"[Diversity Orchestrator] Completed processing with {self.stats['unique_domains']} unique domains")
        
        return enhanced_candidates
    
    async def _process_single_candidate(
        self,
        candidate: Dict[str, Any],
        candidate_index: int
    ) -> Dict[str, Any]:
        """Process a single candidate with diversity considerations."""
        start_time = time.time()
        
        candidate_id = str(candidate.get('id', f'candidate_{candidate_index}'))
        
        # Extract explanations from candidate
        explanations = self._extract_explanations_from_candidate(candidate)
        if not explanations:
            print(f"[Diversity Orchestrator] No explanations found for candidate {candidate_id}")
            return candidate
        
        print(f"[Diversity Orchestrator] Processing candidate {candidate_id} with {len(explanations)} explanations")
        
        # Analyze explanations to extract claims
        all_claims = []
        for explanation in explanations:
            claims = self.explanation_analyzer.extract_claims(explanation)
            all_claims.extend(claims)
        
        if not all_claims:
            print(f"[Diversity Orchestrator] No searchable claims found for candidate {candidate_id}")
            return candidate
        
        # Prioritize and limit claims
        prioritized_claims = sorted(all_claims, key=lambda c: (c.priority, c.confidence), reverse=True)
        selected_claims = prioritized_claims[:3]  # Limit to top 3 claims
        
        print(f"[Diversity Orchestrator] Processing {len(selected_claims)} claims for candidate {candidate_id}")
        
        # Generate diverse queries for each claim
        all_queries = []
        for claim in selected_claims:
            # Generate diverse queries with candidate context
            diverse_queries = self.enhanced_query_generator.generate_diverse_queries(
                claim=claim,
                candidate_id=candidate_id,
                used_sources=self._get_used_sources(),
                candidate_index=candidate_index
            )
            all_queries.extend(diverse_queries[:3])  # Limit to top 3 queries per claim
        
        if not all_queries:
            print(f"[Diversity Orchestrator] No queries generated for candidate {candidate_id}")
            return candidate
        
        print(f"[Diversity Orchestrator] Generated {len(all_queries)} diverse queries for candidate {candidate_id}")
        
        # Execute web searches
        search_results = await self.web_search_engine.search_for_evidence(all_queries)
        successful_results = [r for r in search_results if r.success]
        
        print(f"[Diversity Orchestrator] Completed {len(successful_results)}/{len(search_results)} searches for candidate {candidate_id}")
        
        # Validate and rank with uniqueness
        evidence_urls = []
        for claim in selected_claims:
            # Find search results for this claim
            claim_results = self._find_results_for_claim(successful_results, claim)
            
            if claim_results:
                # Validate with uniqueness constraints
                claim_evidence = self.uniqueness_validator.validate_with_uniqueness(
                    results=claim_results,
                    claim=claim,
                    candidate_id=candidate_id,
                    existing_evidence=evidence_urls
                )
                evidence_urls.extend(claim_evidence)
        
        # Apply final diversity filters
        final_evidence = self._apply_final_diversity_filters(evidence_urls)
        
        # Register evidence usage
        if final_evidence:
            self.uniqueness_validator.register_evidence_usage(final_evidence, candidate_id)
        
        # Update statistics
        self.stats['urls_found'] += len(final_evidence)
        
        processing_time = time.time() - start_time
        
        print(f"[Diversity Orchestrator] Found {len(final_evidence)} diverse URLs for candidate {candidate_id} in {processing_time:.2f}s")
        
        # Create enhanced response
        enhanced_candidate = create_enhanced_candidate_response(
            candidate, final_evidence, processing_time
        )
        
        return enhanced_candidate
    
    def _extract_explanations_from_candidate(self, candidate: Dict[str, Any]) -> List[str]:
        """Extract explanations from candidate data."""
        explanations = []
        
        # Check various possible fields
        if 'reasons' in candidate:
            explanations.extend(candidate['reasons'])
        elif 'explanations' in candidate:
            explanations.extend(candidate['explanations'])
        elif 'behavioral_insights' in candidate:
            explanations.extend(candidate['behavioral_insights'])
        elif 'why_matches' in candidate:
            explanations.extend(candidate['why_matches'])
        
        return [exp for exp in explanations if exp and isinstance(exp, str)]
    
    def _get_used_sources(self) -> Set[str]:
        """Get all sources used so far."""
        used_sources = set()
        
        # Get used URLs and domains from registry
        used_sources.update(self.global_registry.used_urls)
        used_sources.update(self.global_registry.used_domains.keys())
        
        return used_sources
    
    def _find_results_for_claim(self, search_results: List, claim: SearchableClaim) -> List:
        """Find search results relevant to a specific claim."""
        relevant_results = []
        
        for result in search_results:
            # Check if result query matches claim terms
            query_lower = result.query.query.lower()
            claim_terms = [term.lower() for term in claim.search_terms]
            
            # If any claim term appears in the query, consider it relevant
            if any(term in query_lower for term in claim_terms):
                relevant_results.append(result)
        
        return relevant_results
    
    def _apply_final_diversity_filters(
        self,
        evidence_urls: List[EnhancedEvidenceURL]
    ) -> List[EnhancedEvidenceURL]:
        """Apply final diversity filters to evidence URLs."""
        if not evidence_urls:
            return []
        
        # Sort by combined relevance and diversity score
        scored_urls = sorted(
            evidence_urls,
            key=lambda url: (url.relevance_score * 0.7 + url.diversity_score * 0.3),
            reverse=True
        )
        
        # Apply domain diversity constraint
        final_urls = []
        used_domains = set()
        
        for url in scored_urls:
            if len(final_urls) >= 5:  # Limit to 5 URLs per candidate
                break
            
            domain = self._extract_domain(url.url)
            
            # Check domain constraint
            if self.config.max_same_domain_per_candidate == 1:
                if domain in used_domains:
                    continue
            
            final_urls.append(url)
            used_domains.add(domain)
        
        return final_urls
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            # Fallback
            if '://' in url:
                url = url.split('://', 1)[1]
            if '/' in url:
                url = url.split('/', 1)[0]
            return url.lower()
    
    def _update_final_statistics(self):
        """Update final diversity statistics."""
        metrics = self.global_registry.get_diversity_metrics()
        self.stats['unique_domains'] = metrics.total_unique_domains
        self.stats['diversity_score'] = metrics.diversity_index
    
    def get_diversity_statistics(self) -> Dict[str, Any]:
        """Get diversity processing statistics."""
        registry_metrics = self.global_registry.get_diversity_metrics()
        
        return {
            'processing_stats': self.stats,
            'registry_metrics': {
                'total_unique_domains': registry_metrics.total_unique_domains,
                'domain_distribution': registry_metrics.domain_distribution,
                'source_tier_distribution': registry_metrics.source_tier_distribution,
                'diversity_index': registry_metrics.diversity_index,
                'uniqueness_score': registry_metrics.uniqueness_score
            },
            'configuration': {
                'ensure_url_uniqueness': self.config.ensure_url_uniqueness,
                'max_same_domain_per_candidate': self.config.max_same_domain_per_candidate,
                'prioritize_alternatives': self.config.prioritize_alternatives,
                'diversity_weight': self.config.diversity_weight
            }
        }
    
    def reset_diversity_state(self):
        """Reset diversity state (for testing or new sessions)."""
        self.global_registry.reset_registry()
        self.enhanced_query_generator.reset_diversity_tracking()
        self.stats = {
            'candidates_processed': 0,
            'urls_found': 0,
            'unique_domains': 0,
            'diversity_score': 0.0
        }


def test_simplified_diversity_orchestrator():
    """Test function for the Simplified Diversity Orchestrator."""
    import asyncio
    from web_search_engine import WebSearchEngine
    from openai import OpenAI
    
    print("Testing Simplified Diversity Orchestrator:")
    print("=" * 60)
    
    # Create orchestrator
    config = SimplifiedDiversityConfig(
        ensure_url_uniqueness=True,
        max_same_domain_per_candidate=1,
        diversity_weight=0.4
    )
    orchestrator = SimplifiedDiversityOrchestrator(config)
    
    # Set up web search engine (mock for testing)
    # In real usage, you'd pass the actual OpenAI client
    web_search_engine = WebSearchEngine()  # This would need OpenAI client in real usage
    orchestrator.set_web_search_engine(web_search_engine)
    
    # Test candidates with real estate focus (matching your example)
    test_candidates = [
        {
            'id': '1',
            'name': 'John Smith',
            'title': 'Investment Manager',
            'company': 'Wealth Partners',
            'reasons': [
                'Visited luxury real estate websites for Greenwich, Connecticut multiple times in the past month',
                'Engaged with financial calculators and mortgage rate comparison tools on real estate platforms',
                'Joined exclusive real estate investment forums discussing properties in Greenwich'
            ]
        },
        {
            'id': '2',
            'name': 'Sarah Johnson',
            'title': 'Portfolio Manager',
            'company': 'Capital Advisors',
            'reasons': [
                'Researched high-end residential properties in Westchester County',
                'Downloaded mortgage pre-approval applications from multiple lenders',
                'Saved multiple luxury home listings to favorites and shared them with a real estate agent'
            ]
        }
    ]
    
    print("Test candidates focus on real estate investment, not CRM")
    print("This should generate real estate-related URLs, not CRM URLs")
    
    # Note: This test would need actual OpenAI API access to run fully
    # For now, we'll just test the setup and configuration
    
    print(f"\nOrchestrator Configuration:")
    stats = orchestrator.get_diversity_statistics()
    config_info = stats['configuration']
    for key, value in config_info.items():
        print(f"  {key}: {value}")
    
    print(f"\nAlternative Source Manager Categories:")
    categories = orchestrator.alternative_source_manager.category_keywords.keys()
    print(f"  Available categories: {list(categories)}")
    
    # Test category identification
    sample_claim = "Visited luxury real estate websites for Greenwich, Connecticut"
    entities = {'activities': ['visited'], 'products': ['real estate'], 'locations': ['Greenwich', 'Connecticut']}
    category = orchestrator.alternative_source_manager.identify_category_from_claim(sample_claim, entities)
    print(f"  Identified category for real estate claim: {category}")
    
    if category:
        alternatives = orchestrator.alternative_source_manager.get_alternative_companies(category, count=3)
        print(f"  Alternative sources for {category}:")
        for alt in alternatives:
            print(f"    {alt.name} ({alt.domain}) - {alt.tier.value}")


if __name__ == '__main__':
    test_simplified_diversity_orchestrator()