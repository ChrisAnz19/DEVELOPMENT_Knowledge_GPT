#!/usr/bin/env python3
"""
Diversity Metrics and Scoring for URL Evidence Enhancement.

This module provides simplified diversity scoring and metrics calculation
to ensure URL variety while maintaining relevance.
"""

import math
from typing import List, Dict, Set, Any
from dataclasses import dataclass, field
from collections import defaultdict

from uniqueness_aware_evidence_validator import EnhancedEvidenceURL
from alternative_source_manager import SourceTier


@dataclass
class DiversityScore:
    """Individual diversity score breakdown."""
    overall_score: float = 0.0
    domain_uniqueness: float = 0.0
    source_tier_diversity: float = 0.0
    content_variety: float = 0.0
    evidence_type_diversity: float = 0.0


@dataclass
class BatchDiversityMetrics:
    """Metrics for a batch of candidates."""
    total_candidates: int = 0
    total_urls: int = 0
    unique_domains: int = 0
    domain_distribution: Dict[str, int] = field(default_factory=dict)
    source_tier_distribution: Dict[str, int] = field(default_factory=dict)
    evidence_type_distribution: Dict[str, int] = field(default_factory=dict)
    diversity_index: float = 0.0
    uniqueness_rate: float = 0.0
    average_urls_per_candidate: float = 0.0


class SimplifiedDiversityScorer:
    """
    Simplified diversity scorer that focuses on key diversity factors
    without over-complicating the scoring logic.
    """
    
    def __init__(self):
        # Scoring weights (simplified)
        self.weights = {
            'domain_uniqueness': 0.4,      # Most important: avoid duplicate domains
            'source_tier_diversity': 0.3,   # Prefer alternative sources
            'evidence_type_diversity': 0.2, # Variety in evidence types
            'content_variety': 0.1          # Content uniqueness
        }
        
        # Source tier preference scores
        self.tier_scores = {
            'alternative': 1.0,
            'niche': 0.9,
            'emerging': 0.8,
            'mid-tier': 0.6,
            'major': 0.3,
            'unknown': 0.5
        }
    
    def calculate_diversity_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EnhancedEvidenceURL],
        global_used_domains: Set[str] = None
    ) -> DiversityScore:
        """
        Calculate diversity score for an evidence URL.
        
        Args:
            evidence_url: URL to score
            existing_urls: URLs already selected for this candidate
            global_used_domains: Domains used across all candidates
            
        Returns:
            DiversityScore with breakdown
        """
        global_used_domains = global_used_domains or set()
        
        # Calculate individual components
        domain_score = self._calculate_domain_uniqueness(
            evidence_url, existing_urls, global_used_domains
        )
        
        tier_score = self._calculate_source_tier_score(
            evidence_url, existing_urls
        )
        
        type_score = self._calculate_evidence_type_diversity(
            evidence_url, existing_urls
        )
        
        content_score = self._calculate_content_variety(
            evidence_url, existing_urls
        )
        
        # Calculate overall score
        overall_score = (
            domain_score * self.weights['domain_uniqueness'] +
            tier_score * self.weights['source_tier_diversity'] +
            type_score * self.weights['evidence_type_diversity'] +
            content_score * self.weights['content_variety']
        )
        
        return DiversityScore(
            overall_score=overall_score,
            domain_uniqueness=domain_score,
            source_tier_diversity=tier_score,
            content_variety=content_score,
            evidence_type_diversity=type_score
        )
    
    def _calculate_domain_uniqueness(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EnhancedEvidenceURL],
        global_used_domains: Set[str]
    ) -> float:
        """Calculate domain uniqueness score."""
        domain = self._extract_domain(evidence_url.url)
        
        # Check if domain is new globally
        if domain not in global_used_domains:
            global_bonus = 0.3
        else:
            global_bonus = 0.0
        
        # Check if domain is new for this candidate
        existing_domains = {self._extract_domain(url.url) for url in existing_urls}
        if domain not in existing_domains:
            candidate_bonus = 0.7
        else:
            candidate_bonus = 0.0
        
        return min(global_bonus + candidate_bonus, 1.0)
    
    def _calculate_source_tier_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EnhancedEvidenceURL]
    ) -> float:
        """Calculate source tier diversity score."""
        # Base score from tier preference
        base_score = self.tier_scores.get(evidence_url.source_tier, 0.5)
        
        # Check if this tier is already represented
        existing_tiers = {url.source_tier for url in existing_urls if hasattr(url, 'source_tier')}
        
        # Bonus for new tier
        if evidence_url.source_tier not in existing_tiers:
            tier_bonus = 0.2
        else:
            tier_bonus = 0.0
        
        return min(base_score + tier_bonus, 1.0)
    
    def _calculate_evidence_type_diversity(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EnhancedEvidenceURL]
    ) -> float:
        """Calculate evidence type diversity score."""
        existing_types = {url.evidence_type for url in existing_urls}
        
        # High score for new evidence type
        if evidence_url.evidence_type not in existing_types:
            return 1.0
        
        # Lower score for repeated type
        return 0.3
    
    def _calculate_content_variety(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EnhancedEvidenceURL]
    ) -> float:
        """Calculate content variety score based on title similarity."""
        if not existing_urls:
            return 1.0
        
        current_words = set(evidence_url.title.lower().split())
        
        max_similarity = 0.0
        for existing_url in existing_urls:
            existing_words = set(existing_url.title.lower().split())
            
            if current_words and existing_words:
                intersection = current_words.intersection(existing_words)
                union = current_words.union(existing_words)
                similarity = len(intersection) / len(union) if union else 0
                max_similarity = max(max_similarity, similarity)
        
        # Return inverse of similarity (higher score for more unique content)
        return 1.0 - max_similarity
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            if '://' in url:
                url = url.split('://', 1)[1]
            if '/' in url:
                url = url.split('/', 1)[0]
            return url.lower()


class BatchDiversityAnalyzer:
    """
    Analyzes diversity metrics across a batch of candidates
    to provide insights and optimization suggestions.
    """
    
    def __init__(self):
        self.scorer = SimplifiedDiversityScorer()
    
    def analyze_batch_diversity(
        self,
        candidates_with_urls: List[Dict[str, Any]]
    ) -> BatchDiversityMetrics:
        """
        Analyze diversity metrics for a batch of candidates.
        
        Args:
            candidates_with_urls: List of candidates with their evidence URLs
            
        Returns:
            BatchDiversityMetrics with comprehensive analysis
        """
        all_urls = []
        domain_counts = defaultdict(int)
        tier_counts = defaultdict(int)
        type_counts = defaultdict(int)
        
        # Collect all URLs and count distributions
        for candidate in candidates_with_urls:
            evidence_urls = candidate.get('evidence_urls', [])
            
            for url_data in evidence_urls:
                # Handle both dict and object formats
                if isinstance(url_data, dict):
                    url = url_data.get('url', '')
                    source_tier = url_data.get('source_tier', 'unknown')
                    evidence_type = url_data.get('evidence_type', 'general_information')
                else:
                    url = getattr(url_data, 'url', '')
                    source_tier = getattr(url_data, 'source_tier', 'unknown')
                    evidence_type = getattr(url_data, 'evidence_type', 'general_information')
                
                if url:
                    all_urls.append(url)
                    domain = self._extract_domain(url)
                    domain_counts[domain] += 1
                    tier_counts[source_tier] += 1
                    
                    # Handle evidence type (could be enum or string)
                    if hasattr(evidence_type, 'value'):
                        type_counts[evidence_type.value] += 1
                    else:
                        type_counts[str(evidence_type)] += 1
        
        # Calculate metrics
        total_candidates = len(candidates_with_urls)
        total_urls = len(all_urls)
        unique_domains = len(domain_counts)
        
        # Calculate diversity index using Shannon entropy
        diversity_index = self._calculate_shannon_entropy(domain_counts)
        
        # Calculate uniqueness rate
        uniqueness_rate = unique_domains / max(total_urls, 1)
        
        # Calculate average URLs per candidate
        avg_urls_per_candidate = total_urls / max(total_candidates, 1)
        
        return BatchDiversityMetrics(
            total_candidates=total_candidates,
            total_urls=total_urls,
            unique_domains=unique_domains,
            domain_distribution=dict(domain_counts),
            source_tier_distribution=dict(tier_counts),
            evidence_type_distribution=dict(type_counts),
            diversity_index=diversity_index,
            uniqueness_rate=uniqueness_rate,
            average_urls_per_candidate=avg_urls_per_candidate
        )
    
    def get_diversity_recommendations(
        self,
        metrics: BatchDiversityMetrics
    ) -> List[str]:
        """
        Get recommendations for improving diversity based on metrics.
        
        Args:
            metrics: Batch diversity metrics
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check uniqueness rate
        if metrics.uniqueness_rate < 0.7:
            recommendations.append(
                f"Low domain uniqueness ({metrics.uniqueness_rate:.1%}). "
                "Consider using more alternative sources to increase variety."
            )
        
        # Check source tier distribution
        tier_dist = metrics.source_tier_distribution
        major_percentage = tier_dist.get('major', 0) / max(metrics.total_urls, 1)
        if major_percentage > 0.5:
            recommendations.append(
                f"High percentage of major sources ({major_percentage:.1%}). "
                "Consider prioritizing alternative and niche sources."
            )
        
        # Check diversity index
        if metrics.diversity_index < 2.0:
            recommendations.append(
                f"Low diversity index ({metrics.diversity_index:.2f}). "
                "URLs are concentrated in few domains. Increase source variety."
            )
        
        # Check evidence type variety
        type_variety = len(metrics.evidence_type_distribution)
        if type_variety < 3:
            recommendations.append(
                f"Limited evidence type variety ({type_variety} types). "
                "Try to include different types of evidence (pricing, reviews, documentation, etc.)."
            )
        
        if not recommendations:
            recommendations.append("Diversity metrics look good! URLs show good variety across domains and sources.")
        
        return recommendations
    
    def _calculate_shannon_entropy(self, distribution: Dict[str, int]) -> float:
        """Calculate Shannon entropy for diversity measurement."""
        if not distribution:
            return 0.0
        
        total = sum(distribution.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in distribution.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            if '://' in url:
                url = url.split('://', 1)[1]
            if '/' in url:
                url = url.split('/', 1)[0]
            return url.lower()


def test_diversity_metrics():
    """Test function for diversity metrics and scoring."""
    print("Testing Diversity Metrics and Scoring:")
    print("=" * 50)
    
    # Create test data
    scorer = SimplifiedDiversityScorer()
    analyzer = BatchDiversityAnalyzer()
    
    # Mock evidence URLs for testing
    test_urls = [
        {
            'url': 'https://zillow.com/greenwich-ct/',
            'title': 'Greenwich CT Real Estate - Luxury Homes',
            'source_tier': 'major',
            'evidence_type': 'product_page'
        },
        {
            'url': 'https://sothebysrealty.com/greenwich/',
            'title': 'Sotheby\'s International Realty - Greenwich Properties',
            'source_tier': 'niche',
            'evidence_type': 'official_company_page'
        },
        {
            'url': 'https://bankrate.com/mortgage-calculator/',
            'title': 'Mortgage Calculator - Bankrate',
            'source_tier': 'mid-tier',
            'evidence_type': 'general_information'
        }
    ]
    
    # Test candidates with URLs
    test_candidates = [
        {
            'id': '1',
            'name': 'John Smith',
            'evidence_urls': test_urls[:2]  # First 2 URLs
        },
        {
            'id': '2',
            'name': 'Jane Doe',
            'evidence_urls': test_urls[1:]  # Last 2 URLs (with overlap)
        }
    ]
    
    # Analyze batch diversity
    print("1. Analyzing batch diversity:")
    metrics = analyzer.analyze_batch_diversity(test_candidates)
    
    print(f"   Total candidates: {metrics.total_candidates}")
    print(f"   Total URLs: {metrics.total_urls}")
    print(f"   Unique domains: {metrics.unique_domains}")
    print(f"   Uniqueness rate: {metrics.uniqueness_rate:.1%}")
    print(f"   Diversity index: {metrics.diversity_index:.2f}")
    print(f"   Avg URLs per candidate: {metrics.average_urls_per_candidate:.1f}")
    
    print(f"\n   Domain distribution:")
    for domain, count in metrics.domain_distribution.items():
        print(f"     {domain}: {count}")
    
    print(f"\n   Source tier distribution:")
    for tier, count in metrics.source_tier_distribution.items():
        print(f"     {tier}: {count}")
    
    # Get recommendations
    print(f"\n2. Diversity recommendations:")
    recommendations = analyzer.get_diversity_recommendations(metrics)
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    print(f"\n3. Testing individual diversity scoring:")
    # This would require actual EnhancedEvidenceURL objects for full testing
    print("   (Individual scoring requires EnhancedEvidenceURL objects)")
    print("   Scoring weights:")
    for component, weight in scorer.weights.items():
        print(f"     {component}: {weight}")


if __name__ == '__main__':
    test_diversity_metrics()