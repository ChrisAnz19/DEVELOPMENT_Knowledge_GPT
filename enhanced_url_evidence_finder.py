#!/usr/bin/env python3
"""
Enhanced URL Evidence Finder with Diversity Support.

This module integrates the diversity enhancement system with the existing
URL Evidence Finder to provide unique, varied URLs while maintaining relevance.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Import existing components
from url_evidence_finder import URLEvidenceFinder
from evidence_models import create_enhanced_candidate_response

# Import diversity components
from simplified_diversity_orchestrator import SimplifiedDiversityOrchestrator, SimplifiedDiversityConfig
from diversity_metrics import BatchDiversityAnalyzer


class EnhancedURLEvidenceFinder(URLEvidenceFinder):
    """
    Enhanced URL Evidence Finder with diversity support.
    Extends the existing finder to ensure unique, varied URLs across candidates.
    """
    
    def __init__(self, openai_client: Optional[OpenAI] = None, enable_diversity: bool = True):
        # Initialize parent class
        super().__init__(openai_client)
        
        # Diversity configuration
        self.enable_diversity = enable_diversity
        self.diversity_config = SimplifiedDiversityConfig(
            ensure_url_uniqueness=True,
            max_same_domain_per_candidate=1,
            prioritize_alternatives=True,
            diversity_weight=0.3
        )
        
        # Diversity components
        if self.enable_diversity:
            self.diversity_orchestrator = SimplifiedDiversityOrchestrator(self.diversity_config)
            self.diversity_orchestrator.set_web_search_engine(self.web_search_engine)
            self.diversity_analyzer = BatchDiversityAnalyzer()
        else:
            self.diversity_orchestrator = None
            self.diversity_analyzer = None
        
        # Enhanced statistics
        self.enhanced_stats = {
            'diversity_enabled': self.enable_diversity,
            'unique_domains_found': 0,
            'diversity_score': 0.0,
            'alternative_sources_used': 0
        }
    
    async def process_candidates_batch(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple candidates with optional diversity enhancement.
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            List of enhanced candidates with evidence URLs
        """
        start_time = time.time()
        
        print(f"[Enhanced Evidence Finder] Processing batch of {len(candidates)} candidates (diversity: {self.enable_diversity})")
        
        if self.enable_diversity and self.diversity_orchestrator:
            # Use diversity-enhanced processing
            enhanced_candidates = await self.diversity_orchestrator.process_candidates_with_diversity(candidates)
            
            # Analyze diversity metrics
            diversity_stats = self.diversity_orchestrator.get_diversity_statistics()
            self.enhanced_stats.update({
                'unique_domains_found': diversity_stats['registry_metrics']['total_unique_domains'],
                'diversity_score': diversity_stats['registry_metrics']['diversity_index'],
            })
            
            # Get diversity recommendations
            if self.diversity_analyzer:
                batch_metrics = self.diversity_analyzer.analyze_batch_diversity(enhanced_candidates)
                recommendations = self.diversity_analyzer.get_diversity_recommendations(batch_metrics)
                
                print(f"[Enhanced Evidence Finder] Diversity Analysis:")
                print(f"  Unique domains: {batch_metrics.unique_domains}")
                print(f"  Uniqueness rate: {batch_metrics.uniqueness_rate:.1%}")
                print(f"  Diversity index: {batch_metrics.diversity_index:.2f}")
                
                if recommendations:
                    print(f"  Recommendations: {recommendations[0]}")
        
        else:
            # Use standard processing (from parent class)
            enhanced_candidates = await super().process_candidates_batch(candidates)
        
        batch_time = time.time() - start_time
        print(f"[Enhanced Evidence Finder] Completed batch processing in {batch_time:.2f}s")
        
        return enhanced_candidates
    
    async def process_candidate(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single candidate with optional diversity enhancement.
        
        Args:
            candidate: Candidate dictionary with explanations
            
        Returns:
            Enhanced candidate with evidence URLs
        """
        if self.enable_diversity and self.diversity_orchestrator:
            # Process through diversity orchestrator
            enhanced_candidates = await self.diversity_orchestrator.process_candidates_with_diversity([candidate])
            return enhanced_candidates[0] if enhanced_candidates else candidate
        else:
            # Use standard processing
            return await super().process_candidate(candidate)
    
    def configure_diversity(
        self,
        ensure_uniqueness: bool = True,
        max_same_domain: int = 1,
        prioritize_alternatives: bool = True,
        diversity_weight: float = 0.3
    ):
        """
        Configure diversity settings.
        
        Args:
            ensure_uniqueness: Ensure no duplicate URLs across candidates
            max_same_domain: Maximum URLs from same domain per candidate
            prioritize_alternatives: Prioritize alternative sources over major ones
            diversity_weight: Weight given to diversity vs relevance (0-1)
        """
        self.diversity_config = SimplifiedDiversityConfig(
            ensure_url_uniqueness=ensure_uniqueness,
            max_same_domain_per_candidate=max_same_domain,
            prioritize_alternatives=prioritize_alternatives,
            diversity_weight=diversity_weight
        )
        
        if self.diversity_orchestrator:
            self.diversity_orchestrator.config = self.diversity_config
        
        print(f"[Enhanced Evidence Finder] Updated diversity configuration")
    
    def enable_diversity_mode(self, enable: bool = True):
        """
        Enable or disable diversity mode.
        
        Args:
            enable: Whether to enable diversity processing
        """
        self.enable_diversity = enable
        
        if enable and not self.diversity_orchestrator:
            # Initialize diversity components
            self.diversity_orchestrator = SimplifiedDiversityOrchestrator(self.diversity_config)
            self.diversity_orchestrator.set_web_search_engine(self.web_search_engine)
            self.diversity_analyzer = BatchDiversityAnalyzer()
        
        self.enhanced_stats['diversity_enabled'] = enable
        print(f"[Enhanced Evidence Finder] Diversity mode {'enabled' if enable else 'disabled'}")
    
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Get enhanced processing statistics including diversity metrics."""
        base_stats = super().get_statistics()
        
        enhanced_stats = {
            **base_stats,
            'diversity_stats': self.enhanced_stats
        }
        
        # Add diversity orchestrator stats if available
        if self.diversity_orchestrator:
            diversity_stats = self.diversity_orchestrator.get_diversity_statistics()
            enhanced_stats['diversity_details'] = diversity_stats
        
        return enhanced_stats
    
    def reset_diversity_state(self):
        """Reset diversity state (for testing or new sessions)."""
        if self.diversity_orchestrator:
            self.diversity_orchestrator.reset_diversity_state()
        
        self.enhanced_stats.update({
            'unique_domains_found': 0,
            'diversity_score': 0.0,
            'alternative_sources_used': 0
        })
        
        print(f"[Enhanced Evidence Finder] Reset diversity state")


async def test_enhanced_url_evidence_finder():
    """Test function for the Enhanced URL Evidence Finder."""
    print("Testing Enhanced URL Evidence Finder:")
    print("=" * 60)
    
    # Create enhanced evidence finder
    enhanced_finder = EnhancedURLEvidenceFinder(enable_diversity=True)
    
    # Configure diversity settings
    enhanced_finder.configure_diversity(
        ensure_uniqueness=True,
        max_same_domain=1,
        prioritize_alternatives=True,
        diversity_weight=0.4
    )
    
    # Test candidates with real estate focus (matching the behavioral reasons)
    test_candidates = [
        {
            'id': '1',
            'name': 'John Smith',
            'title': 'Investment Manager',
            'company': 'Wealth Partners',
            'reasons': [
                'Visited luxury real estate websites for Greenwich, Connecticut multiple times in the past month',
                'Engaged with financial calculators and mortgage rate comparison tools on real estate platforms'
            ]
        },
        {
            'id': '2',
            'name': 'Sarah Johnson',
            'title': 'Portfolio Manager', 
            'company': 'Capital Advisors',
            'reasons': [
                'Researched high-end residential properties in Westchester County',
                'Downloaded mortgage pre-approval applications from multiple lenders'
            ]
        },
        {
            'id': '3',
            'name': 'Mike Wilson',
            'title': 'Financial Advisor',
            'company': 'Premier Investments',
            'reasons': [
                'Joined exclusive real estate investment forums discussing properties in Greenwich',
                'Saved multiple luxury home listings to favorites and shared them with a real estate agent'
            ]
        }
    ]
    
    print("Test Setup:")
    print("- Candidates have real estate investment behavioral reasons")
    print("- URLs should be real estate-related, not CRM-related")
    print("- Each candidate should get unique URLs (no duplicates)")
    print("- Should prioritize alternative/niche real estate sources")
    
    # Test single candidate processing
    print(f"\n1. Testing single candidate processing:")
    enhanced_candidate = await enhanced_finder.process_candidate(test_candidates[0])
    
    print(f"Candidate: {enhanced_candidate['name']}")
    evidence_urls = enhanced_candidate.get('evidence_urls', [])
    print(f"Evidence URLs found: {len(evidence_urls)}")
    
    for i, url_data in enumerate(evidence_urls, 1):
        if isinstance(url_data, dict):
            url = url_data.get('url', 'N/A')
            title = url_data.get('title', 'N/A')
        else:
            url = getattr(url_data, 'url', 'N/A')
            title = getattr(url_data, 'title', 'N/A')
        
        print(f"  {i}. {title}")
        print(f"     URL: {url}")
    
    # Test batch processing
    print(f"\n2. Testing batch processing with diversity:")
    
    # Note: This would require actual OpenAI API access to run fully
    # For demonstration, we'll show the configuration and setup
    
    print("Configuration:")
    stats = enhanced_finder.get_enhanced_statistics()
    diversity_config = stats.get('diversity_stats', {})
    for key, value in diversity_config.items():
        print(f"  {key}: {value}")
    
    # Test diversity mode toggle
    print(f"\n3. Testing diversity mode toggle:")
    enhanced_finder.enable_diversity_mode(False)
    print("Diversity disabled")
    
    enhanced_finder.enable_diversity_mode(True)
    print("Diversity re-enabled")
    
    # Show available categories for real estate
    if enhanced_finder.diversity_orchestrator:
        alt_manager = enhanced_finder.diversity_orchestrator.alternative_source_manager
        
        print(f"\n4. Available source categories:")
        categories = list(alt_manager.category_keywords.keys())
        print(f"Categories: {categories}")
        
        # Test real estate category
        if 'real_estate' in alt_manager.alternative_companies:
            real_estate_sources = alt_manager.alternative_companies['real_estate']
            print(f"\nReal estate sources available:")
            for source in real_estate_sources[:5]:  # Show first 5
                print(f"  {source.name} ({source.domain}) - {source.tier.value}")


if __name__ == '__main__':
    print("Enhanced URL Evidence Finder module loaded successfully!")
    print("To test with actual API calls, run: asyncio.run(test_enhanced_url_evidence_finder())")
    print("Make sure you have OPENAI_API_KEY environment variable set.")
    
    # Run basic test without API calls
    asyncio.run(test_enhanced_url_evidence_finder())