#!/usr/bin/env python3
"""
Global URL Registry for URL Diversity Enhancement.

This module tracks used URLs across all candidates to ensure uniqueness
and provides diversity metrics for monitoring and optimization.
"""

import time
from typing import Set, Dict, List, Optional, DefaultDict
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence that URLs can provide."""
    OFFICIAL_COMPANY_PAGE = "official_company_page"
    PRODUCT_PAGE = "product_page"
    PRICING_PAGE = "pricing_page"
    DOCUMENTATION = "documentation"
    NEWS_ARTICLE = "news_article"
    CASE_STUDY = "case_study"
    COMPARISON_SITE = "comparison_site"
    INDUSTRY_REPORT = "industry_report"
    REVIEW_SITE = "review_site"
    BLOG_POST = "blog_post"
    GENERAL_INFORMATION = "general_information"


@dataclass
class URLAssignment:
    """Represents a URL assignment to a candidate."""
    url: str
    candidate_id: str
    domain: str
    evidence_type: EvidenceType
    timestamp: float
    source_tier: str  # major, mid-tier, niche, alternative


@dataclass
class DiversityMetrics:
    """Metrics tracking diversity across candidates."""
    total_unique_domains: int = 0
    domain_distribution: Dict[str, int] = field(default_factory=dict)
    source_tier_distribution: Dict[str, int] = field(default_factory=dict)
    evidence_type_distribution: Dict[str, int] = field(default_factory=dict)
    uniqueness_score: float = 0.0
    diversity_index: float = 0.0
    total_urls: int = 0
    total_candidates: int = 0


class GlobalURLRegistry:
    """
    Tracks used URLs across all candidates to ensure uniqueness
    and provides diversity metrics.
    """
    
    def __init__(self, max_registry_size: int = 10000):
        # Core tracking data
        self.used_urls: Set[str] = set()
        self.used_domains: DefaultDict[str, int] = defaultdict(int)
        self.candidate_assignments: Dict[str, List[URLAssignment]] = {}
        self.url_assignments: Dict[str, URLAssignment] = {}
        
        # Configuration
        self.max_registry_size = max_registry_size
        
        # Statistics
        self.total_candidates_processed = 0
        self.total_urls_assigned = 0
        self.registry_created_at = time.time()
        
    def is_url_available(self, url: str) -> bool:
        """
        Check if URL is available for use (not already assigned).
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is available, False if already used
        """
        return url not in self.used_urls
    
    def is_domain_overused(self, domain: str, threshold: int = 3) -> bool:
        """
        Check if domain is being overused across candidates.
        
        Args:
            domain: Domain to check
            threshold: Maximum uses allowed per domain
            
        Returns:
            True if domain usage exceeds threshold
        """
        return self.used_domains[domain] >= threshold
    
    def register_url_usage(
        self,
        url: str,
        candidate_id: str,
        evidence_type: EvidenceType,
        source_tier: str = "unknown"
    ) -> bool:
        """
        Register URL as used by a candidate.
        
        Args:
            url: URL being assigned
            candidate_id: ID of candidate receiving the URL
            evidence_type: Type of evidence this URL provides
            source_tier: Tier of the source (major, mid-tier, niche, alternative)
            
        Returns:
            True if registration successful, False if URL already used
        """
        if not self.is_url_available(url):
            return False
        
        # Extract domain
        domain = self._extract_domain(url)
        
        # Create assignment record
        assignment = URLAssignment(
            url=url,
            candidate_id=candidate_id,
            domain=domain,
            evidence_type=evidence_type,
            timestamp=time.time(),
            source_tier=source_tier
        )
        
        # Update tracking data
        self.used_urls.add(url)
        self.used_domains[domain] += 1
        self.url_assignments[url] = assignment
        
        # Update candidate assignments
        if candidate_id not in self.candidate_assignments:
            self.candidate_assignments[candidate_id] = []
        self.candidate_assignments[candidate_id].append(assignment)
        
        # Update statistics
        self.total_urls_assigned += 1
        
        # Cleanup if registry is getting too large
        self._cleanup_if_needed()
        
        return True
    
    def register_candidate_processed(self, candidate_id: str):
        """
        Register that a candidate has been processed.
        
        Args:
            candidate_id: ID of processed candidate
        """
        if candidate_id not in self.candidate_assignments:
            self.candidate_assignments[candidate_id] = []
        
        self.total_candidates_processed += 1
    
    def get_candidate_urls(self, candidate_id: str) -> List[URLAssignment]:
        """
        Get all URLs assigned to a specific candidate.
        
        Args:
            candidate_id: ID of candidate
            
        Returns:
            List of URL assignments for the candidate
        """
        return self.candidate_assignments.get(candidate_id, [])
    
    def get_used_domains_for_candidate(self, candidate_id: str) -> Set[str]:
        """
        Get all domains used by a specific candidate.
        
        Args:
            candidate_id: ID of candidate
            
        Returns:
            Set of domains used by the candidate
        """
        assignments = self.get_candidate_urls(candidate_id)
        return {assignment.domain for assignment in assignments}
    
    def get_diversity_metrics(self) -> DiversityMetrics:
        """
        Calculate and return current diversity metrics.
        
        Returns:
            DiversityMetrics object with current statistics
        """
        # Count unique domains
        unique_domains = len(self.used_domains)
        
        # Calculate domain distribution
        domain_dist = dict(self.used_domains)
        
        # Calculate source tier distribution
        source_tier_dist = defaultdict(int)
        evidence_type_dist = defaultdict(int)
        
        for assignment in self.url_assignments.values():
            source_tier_dist[assignment.source_tier] += 1
            evidence_type_dist[assignment.evidence_type.value] += 1
        
        # Calculate uniqueness score (percentage of unique URLs)
        uniqueness_score = (
            len(self.used_urls) / max(self.total_urls_assigned, 1)
        )
        
        # Calculate diversity index using Shannon entropy
        diversity_index = self._calculate_shannon_entropy(domain_dist)
        
        return DiversityMetrics(
            total_unique_domains=unique_domains,
            domain_distribution=domain_dist,
            source_tier_distribution=dict(source_tier_dist),
            evidence_type_distribution=dict(evidence_type_dist),
            uniqueness_score=uniqueness_score,
            diversity_index=diversity_index,
            total_urls=self.total_urls_assigned,
            total_candidates=self.total_candidates_processed
        )
    
    def get_registry_stats(self) -> Dict[str, any]:
        """
        Get registry statistics and health information.
        
        Returns:
            Dictionary with registry statistics
        """
        return {
            'total_urls_tracked': len(self.used_urls),
            'total_domains_tracked': len(self.used_domains),
            'total_candidates_processed': self.total_candidates_processed,
            'total_urls_assigned': self.total_urls_assigned,
            'registry_age_seconds': time.time() - self.registry_created_at,
            'registry_size_limit': self.max_registry_size,
            'memory_usage_estimate': self._estimate_memory_usage()
        }
    
    def clear_candidate_data(self, candidate_id: str):
        """
        Clear all data for a specific candidate (for testing/cleanup).
        
        Args:
            candidate_id: ID of candidate to clear
        """
        if candidate_id not in self.candidate_assignments:
            return
        
        # Remove URLs from tracking
        assignments = self.candidate_assignments[candidate_id]
        for assignment in assignments:
            if assignment.url in self.used_urls:
                self.used_urls.remove(assignment.url)
            
            if assignment.url in self.url_assignments:
                del self.url_assignments[assignment.url]
            
            # Decrement domain count
            self.used_domains[assignment.domain] -= 1
            if self.used_domains[assignment.domain] <= 0:
                del self.used_domains[assignment.domain]
        
        # Remove candidate assignments
        del self.candidate_assignments[candidate_id]
        
        # Update statistics
        self.total_urls_assigned -= len(assignments)
        self.total_candidates_processed -= 1
    
    def reset_registry(self):
        """Reset the entire registry (for testing/cleanup)."""
        self.used_urls.clear()
        self.used_domains.clear()
        self.candidate_assignments.clear()
        self.url_assignments.clear()
        self.total_candidates_processed = 0
        self.total_urls_assigned = 0
        self.registry_created_at = time.time()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            # Fallback to simple extraction
            try:
                if '://' in url:
                    url = url.split('://', 1)[1]
                if '/' in url:
                    url = url.split('/', 1)[0]
                return url.lower()
            except:
                return url.lower()
    
    def _calculate_shannon_entropy(self, distribution: Dict[str, int]) -> float:
        """Calculate Shannon entropy for diversity measurement."""
        if not distribution:
            return 0.0
        
        import math
        
        total = sum(distribution.values())
        if total == 0:
            return 0.0
        
        entropy = 0.0
        for count in distribution.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # Rough estimation
        url_memory = sum(len(url) for url in self.used_urls) * 2  # Unicode chars
        domain_memory = sum(len(domain) for domain in self.used_domains) * 2
        assignment_memory = len(self.url_assignments) * 200  # Rough estimate per assignment
        
        return url_memory + domain_memory + assignment_memory
    
    def _cleanup_if_needed(self):
        """Clean up old entries if registry is getting too large."""
        if len(self.used_urls) <= self.max_registry_size:
            return
        
        # Remove oldest 20% of entries
        cleanup_count = int(self.max_registry_size * 0.2)
        
        # Sort assignments by timestamp
        sorted_assignments = sorted(
            self.url_assignments.values(),
            key=lambda a: a.timestamp
        )
        
        # Remove oldest entries
        for assignment in sorted_assignments[:cleanup_count]:
            self._remove_assignment(assignment)
    
    def _remove_assignment(self, assignment: URLAssignment):
        """Remove a specific assignment from tracking."""
        # Remove from used URLs
        if assignment.url in self.used_urls:
            self.used_urls.remove(assignment.url)
        
        # Remove from URL assignments
        if assignment.url in self.url_assignments:
            del self.url_assignments[assignment.url]
        
        # Decrement domain count
        self.used_domains[assignment.domain] -= 1
        if self.used_domains[assignment.domain] <= 0:
            del self.used_domains[assignment.domain]
        
        # Remove from candidate assignments
        if assignment.candidate_id in self.candidate_assignments:
            candidate_assignments = self.candidate_assignments[assignment.candidate_id]
            self.candidate_assignments[assignment.candidate_id] = [
                a for a in candidate_assignments if a.url != assignment.url
            ]


def test_global_url_registry():
    """Test function for the Global URL Registry."""
    print("Testing Global URL Registry:")
    print("=" * 50)
    
    # Create registry
    registry = GlobalURLRegistry()
    
    # Test URL availability
    test_url = "https://example.com/pricing"
    print(f"URL available: {registry.is_url_available(test_url)}")
    
    # Register URL usage
    success = registry.register_url_usage(
        test_url,
        "candidate_1",
        EvidenceType.PRICING_PAGE,
        "major"
    )
    print(f"Registration successful: {success}")
    
    # Test URL no longer available
    print(f"URL available after registration: {registry.is_url_available(test_url)}")
    
    # Register more URLs
    registry.register_url_usage(
        "https://alternative.com/features",
        "candidate_2",
        EvidenceType.PRODUCT_PAGE,
        "alternative"
    )
    
    registry.register_url_usage(
        "https://example.com/docs",
        "candidate_3",
        EvidenceType.DOCUMENTATION,
        "major"
    )
    
    # Register candidates as processed
    registry.register_candidate_processed("candidate_1")
    registry.register_candidate_processed("candidate_2")
    registry.register_candidate_processed("candidate_3")
    
    # Test domain overuse
    print(f"Domain overused: {registry.is_domain_overused('example.com', threshold=2)}")
    
    # Get diversity metrics
    metrics = registry.get_diversity_metrics()
    print(f"\nDiversity Metrics:")
    print(f"Unique domains: {metrics.total_unique_domains}")
    print(f"Domain distribution: {metrics.domain_distribution}")
    print(f"Source tier distribution: {metrics.source_tier_distribution}")
    print(f"Uniqueness score: {metrics.uniqueness_score:.3f}")
    print(f"Diversity index: {metrics.diversity_index:.3f}")
    
    # Get registry stats
    stats = registry.get_registry_stats()
    print(f"\nRegistry Stats:")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Test candidate URL retrieval
    candidate_urls = registry.get_candidate_urls("candidate_1")
    print(f"\nCandidate 1 URLs: {len(candidate_urls)}")
    for assignment in candidate_urls:
        print(f"  {assignment.url} ({assignment.evidence_type.value})")


if __name__ == '__main__':
    test_global_url_registry()