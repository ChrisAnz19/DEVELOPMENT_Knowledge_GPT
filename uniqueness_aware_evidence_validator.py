#!/usr/bin/env python3
"""
Uniqueness-Aware Evidence Validator for URL Diversity Enhancement.

This module extends the existing EvidenceValidator with global uniqueness
checking and diversity scoring capabilities.
"""

import time
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass

# Import existing components
from evidence_validator import EvidenceValidator
from evidence_models import EvidenceURL, EvidenceType
from global_url_registry import GlobalURLRegistry, URLAssignment
from alternative_source_manager import AlternativeSourceManager, SourceTier
from explanation_analyzer import SearchableClaim
from web_search_engine import SearchResult, URLCandidate


@dataclass
class EnhancedEvidenceURL(EvidenceURL):
    """Enhanced Evidence URL with diversity-specific fields."""
    diversity_score: float = 0.0        # How much this URL contributes to diversity
    source_tier: str = "unknown"        # major, mid-tier, niche, alternative
    uniqueness_factor: float = 0.0      # How unique this source is
    rotation_index: int = 0             # For tracking rotation patterns
    
    def to_model(self):
        """Convert to model format (inherit from parent and add diversity fields)."""
        from evidence_models import EvidenceURLModel, ConfidenceLevel
        
        # Convert evidence_type to the correct enum if needed
        if hasattr(self.evidence_type, 'value'):
            evidence_type_value = self.evidence_type.value
        else:
            evidence_type_value = str(self.evidence_type)
        
        # Create the model directly to avoid enum conversion issues
        return EvidenceURLModel(
            url=self.url,
            title=self.title,
            description=self.description,
            evidence_type=evidence_type_value,  # Pass the string value directly
            relevance_score=self.relevance_score,
            confidence_level=self.confidence_level,
            supporting_explanation=self.supporting_explanation,
            domain_authority=self.domain_authority,
            page_quality_score=self.page_quality_score,
            last_validated=self.last_validated
        )


class UniquenessAwareEvidenceValidator(EvidenceValidator):
    """
    Enhanced evidence validator with global uniqueness tracking
    and diversity scoring capabilities.
    """
    
    def __init__(self, global_registry: GlobalURLRegistry = None):
        super().__init__()
        
        # Global registry for uniqueness tracking
        self.global_registry = global_registry or GlobalURLRegistry()
        
        # Alternative source manager for diversity scoring
        self.alternative_source_manager = AlternativeSourceManager()
        
        # Diversity scoring weights
        self.diversity_weights = {
            'source_tier': 0.3,      # Weight for source tier diversity
            'domain_uniqueness': 0.4, # Weight for domain uniqueness
            'evidence_type': 0.2,     # Weight for evidence type diversity
            'content_uniqueness': 0.1 # Weight for content uniqueness
        }
        
        # Source tier scoring
        self.tier_scores = {
            SourceTier.ALTERNATIVE: 1.0,
            SourceTier.NICHE: 0.9,
            SourceTier.EMERGING: 0.8,
            SourceTier.MID_TIER: 0.6,
            SourceTier.MAJOR: 0.3
        }
    
    def validate_with_uniqueness(
        self,
        results: List[SearchResult],
        claim: SearchableClaim,
        candidate_id: str,
        existing_evidence: List[EvidenceURL] = None
    ) -> List[EnhancedEvidenceURL]:
        """
        Validate URLs ensuring global uniqueness and calculating diversity scores.
        
        Args:
            results: Raw search results
            claim: Original claim being supported
            candidate_id: Unique identifier for candidate
            existing_evidence: Evidence already selected for this candidate
            
        Returns:
            Ranked list of enhanced evidence URLs (globally unique)
        """
        existing_evidence = existing_evidence or []
        all_candidates = []
        
        # Collect all URL candidates from search results
        print(f"[Uniqueness Validator] Processing {len(results)} search results")
        for result in results:
            if result.success:
                print(f"[Uniqueness Validator] Processing successful result with {len(result.urls)} URLs")
                for url_candidate in result.urls:
                    print(f"[Uniqueness Validator] Checking URL: {url_candidate.url}")
                    
                    # Skip if URL already used globally
                    if not self.global_registry.is_url_available(url_candidate.url):
                        print(f"[Uniqueness Validator] Skipped (already used): {url_candidate.url}")
                        continue
                    
                    # Skip if domain already overused
                    domain = self._extract_domain(url_candidate.url)
                    if self.global_registry.is_domain_overused(domain, threshold=3):
                        print(f"[Uniqueness Validator] Skipped (domain overused): {domain}")
                        continue
                    
                    # Validate URL quality (from parent class)
                    if self.validate_url_quality(url_candidate):
                        print(f"[Uniqueness Validator] URL passed quality check: {url_candidate.url}")
                        enhanced_url = self._create_enhanced_evidence_url(
                            url_candidate, claim, result, existing_evidence
                        )
                        if enhanced_url:
                            print(f"[Uniqueness Validator] Created enhanced URL: {enhanced_url.url}")
                            all_candidates.append(enhanced_url)
                        else:
                            print(f"[Uniqueness Validator] Failed to create enhanced URL for: {url_candidate.url}")
                    else:
                        print(f"[Uniqueness Validator] URL failed quality check: {url_candidate.url}")
            else:
                print(f"[Uniqueness Validator] Skipped unsuccessful result")
        
        # Remove duplicates and apply uniqueness constraints
        unique_candidates = self._enforce_uniqueness_constraints(all_candidates)
        
        # Calculate diversity scores
        scored_candidates = self._calculate_diversity_scores(unique_candidates, existing_evidence)
        
        # Rank by combined relevance and diversity score
        ranked_candidates = self._rank_by_combined_score(scored_candidates)
        
        # Apply quality filters
        filtered_candidates = self._apply_enhanced_quality_filters(ranked_candidates, claim)
        
        # Select diverse final set
        final_candidates = self._select_diverse_final_set(filtered_candidates, existing_evidence)
        
        return final_candidates
    
    def calculate_diversity_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EvidenceURL]
    ) -> float:
        """
        Calculate diversity contribution score for an evidence URL.
        
        Args:
            evidence_url: URL to score
            existing_urls: URLs already selected
            
        Returns:
            Diversity score between 0 and 1
        """
        score = 0.0
        
        # Source tier diversity score
        tier_score = self._calculate_tier_diversity_score(evidence_url, existing_urls)
        score += tier_score * self.diversity_weights['source_tier']
        
        # Domain uniqueness score
        domain_score = self._calculate_domain_uniqueness_score(evidence_url, existing_urls)
        score += domain_score * self.diversity_weights['domain_uniqueness']
        
        # Evidence type diversity score
        type_score = self._calculate_type_diversity_score(evidence_url, existing_urls)
        score += type_score * self.diversity_weights['evidence_type']
        
        # Content uniqueness score
        content_score = self._calculate_content_uniqueness_score(evidence_url, existing_urls)
        score += content_score * self.diversity_weights['content_uniqueness']
        
        return min(score, 1.0)
    
    def enforce_uniqueness_constraints(
        self,
        candidates: List[EnhancedEvidenceURL]
    ) -> List[EnhancedEvidenceURL]:
        """
        Filter out already-used URLs and apply uniqueness constraints.
        
        Args:
            candidates: URL candidates to filter
            
        Returns:
            Filtered list with unique URLs only
        """
        return self._enforce_uniqueness_constraints(candidates)
    
    def register_evidence_usage(
        self,
        evidence_urls: List[EnhancedEvidenceURL],
        candidate_id: str
    ):
        """
        Register evidence URLs as used in the global registry.
        
        Args:
            evidence_urls: URLs being assigned to candidate
            candidate_id: ID of candidate receiving the URLs
        """
        for evidence_url in evidence_urls:
            # Determine source tier
            source_tier = self._determine_source_tier(evidence_url)
            
            # Register in global registry
            self.global_registry.register_url_usage(
                url=evidence_url.url,
                candidate_id=candidate_id,
                evidence_type=evidence_url.evidence_type,
                source_tier=source_tier
            )
    
    def _create_enhanced_evidence_url(
        self,
        url_candidate: URLCandidate,
        claim: SearchableClaim,
        search_result: SearchResult,
        existing_evidence: List[EvidenceURL]
    ) -> Optional[EnhancedEvidenceURL]:
        """Create an Enhanced Evidence URL from a URL candidate."""
        try:
            # Get base evidence URL from parent class
            base_evidence = self._create_evidence_url(url_candidate, claim, search_result)
            if not base_evidence:
                return None
            
            # Determine source tier
            source_tier = self._classify_source_tier(url_candidate)
            
            # Calculate uniqueness factor
            uniqueness_factor = self._calculate_uniqueness_factor(url_candidate)
            
            # Create enhanced evidence URL
            enhanced_evidence = EnhancedEvidenceURL(
                url=base_evidence.url,
                title=base_evidence.title,
                description=base_evidence.description,
                evidence_type=base_evidence.evidence_type,
                relevance_score=base_evidence.relevance_score,
                confidence_level=base_evidence.confidence_level,
                supporting_explanation=base_evidence.supporting_explanation,
                domain_authority=base_evidence.domain_authority,
                page_quality_score=base_evidence.page_quality_score,
                last_validated=base_evidence.last_validated,
                diversity_score=0.0,  # Will be calculated later
                source_tier=source_tier,
                uniqueness_factor=uniqueness_factor,
                rotation_index=0
            )
            
            return enhanced_evidence
            
        except Exception as e:
            print(f"[Enhanced Validator] Error creating enhanced evidence URL: {e}")
            return None
    
    def _enforce_uniqueness_constraints(
        self,
        candidates: List[EnhancedEvidenceURL]
    ) -> List[EnhancedEvidenceURL]:
        """Apply uniqueness constraints to filter candidates."""
        unique_candidates = []
        seen_urls = set()
        seen_domains = set()
        
        for candidate in candidates:
            # Skip if URL already seen
            if candidate.url in seen_urls:
                continue
            
            # Skip if URL not available in global registry
            if not self.global_registry.is_url_available(candidate.url):
                continue
            
            # Extract domain
            domain = self._extract_domain(candidate.url)
            
            # Skip if domain overused globally
            if self.global_registry.is_domain_overused(domain, threshold=3):
                continue
            
            # Skip if too many from same domain in this candidate set
            if domain in seen_domains:
                continue
            
            # Add to unique set
            unique_candidates.append(candidate)
            seen_urls.add(candidate.url)
            seen_domains.add(domain)
        
        return unique_candidates
    
    def _calculate_diversity_scores(
        self,
        candidates: List[EnhancedEvidenceURL],
        existing_evidence: List[EvidenceURL]
    ) -> List[EnhancedEvidenceURL]:
        """Calculate diversity scores for all candidates."""
        scored_candidates = []
        
        for candidate in candidates:
            diversity_score = self.calculate_diversity_score(candidate, existing_evidence)
            
            # Update the candidate with diversity score
            candidate.diversity_score = diversity_score
            scored_candidates.append(candidate)
        
        return scored_candidates
    
    def _rank_by_combined_score(
        self,
        candidates: List[EnhancedEvidenceURL],
        diversity_weight: float = 0.4
    ) -> List[EnhancedEvidenceURL]:
        """Rank candidates by combined relevance and diversity score."""
        def combined_score(candidate):
            relevance_component = candidate.relevance_score * (1 - diversity_weight)
            diversity_component = candidate.diversity_score * diversity_weight
            quality_component = candidate.page_quality_score * 0.1
            
            return relevance_component + diversity_component + quality_component
        
        return sorted(candidates, key=combined_score, reverse=True)
    
    def _apply_enhanced_quality_filters(
        self,
        candidates: List[EnhancedEvidenceURL],
        claim: SearchableClaim
    ) -> List[EnhancedEvidenceURL]:
        """Apply enhanced quality filters considering diversity."""
        filtered = []
        
        for candidate in candidates:
            # Base quality thresholds (from parent class)
            # Use lower threshold if high diversity score compensates for low relevance
            relevance_threshold = 0.10 if candidate.diversity_score > 0.8 else 0.25
            if candidate.relevance_score < relevance_threshold:
                continue
            
            if candidate.page_quality_score < 0.35:  # Slightly lower for diversity
                continue
            
            # Enhanced filters for diversity
            # Allow lower authority if high diversity score
            if (candidate.domain_authority < 0.5 and 
                candidate.diversity_score < 0.6 and 
                candidate.confidence_level == "low"):
                continue
            
            # Require minimum combined score
            combined_score = (
                candidate.relevance_score * 0.4 +
                candidate.diversity_score * 0.3 +
                candidate.page_quality_score * 0.3
            )
            
            if combined_score < 0.4:
                continue
            
            filtered.append(candidate)
        
        return filtered
    
    def _select_diverse_final_set(
        self,
        candidates: List[EnhancedEvidenceURL],
        existing_evidence: List[EvidenceURL],
        max_count: int = 5
    ) -> List[EnhancedEvidenceURL]:
        """Select final diverse set ensuring variety."""
        if len(candidates) <= max_count:
            return candidates
        
        selected = []
        used_tiers = set()
        used_evidence_types = set()
        used_domains = set()
        
        # Add existing evidence to tracking
        for evidence in existing_evidence:
            used_evidence_types.add(evidence.evidence_type)
            domain = self._extract_domain(evidence.url)
            used_domains.add(domain)
        
        # First pass: select high-diversity candidates
        for candidate in candidates:
            if len(selected) >= max_count:
                break
            
            domain = self._extract_domain(candidate.url)
            
            # Check diversity factors
            tier_new = candidate.source_tier not in used_tiers
            type_new = candidate.evidence_type not in used_evidence_types
            domain_new = domain not in used_domains
            
            # Prioritize high diversity or high quality
            if (candidate.diversity_score >= 0.7 or 
                tier_new or type_new or domain_new or 
                len(selected) < 2):
                
                selected.append(candidate)
                used_tiers.add(candidate.source_tier)
                used_evidence_types.add(candidate.evidence_type)
                used_domains.add(domain)
        
        # Fill remaining slots with best remaining candidates
        remaining_slots = max_count - len(selected)
        if remaining_slots > 0:
            remaining_candidates = [c for c in candidates if c not in selected]
            selected.extend(remaining_candidates[:remaining_slots])
        
        return selected
    
    def _calculate_tier_diversity_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EvidenceURL]
    ) -> float:
        """Calculate source tier diversity score."""
        # Get tier from source_tier string
        try:
            tier = SourceTier(evidence_url.source_tier)
            base_score = self.tier_scores.get(tier, 0.5)
        except ValueError:
            base_score = 0.5
        
        # Check if this tier is already represented
        existing_tiers = set()
        for url in existing_urls:
            if hasattr(url, 'source_tier'):
                existing_tiers.add(url.source_tier)
        
        # Bonus for new tier
        if evidence_url.source_tier not in existing_tiers:
            base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _calculate_domain_uniqueness_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EvidenceURL]
    ) -> float:
        """Calculate domain uniqueness score."""
        domain = self._extract_domain(evidence_url.url)
        
        # Check existing domains
        existing_domains = set()
        for url in existing_urls:
            existing_domains.add(self._extract_domain(url.url))
        
        # High score for new domain
        if domain not in existing_domains:
            return 1.0
        
        # Lower score for repeated domain
        return 0.3
    
    def _calculate_type_diversity_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EvidenceURL]
    ) -> float:
        """Calculate evidence type diversity score."""
        # Check existing evidence types
        existing_types = {url.evidence_type for url in existing_urls}
        
        # High score for new evidence type
        if evidence_url.evidence_type not in existing_types:
            return 1.0
        
        # Lower score for repeated type
        return 0.4
    
    def _calculate_content_uniqueness_score(
        self,
        evidence_url: EnhancedEvidenceURL,
        existing_urls: List[EvidenceURL]
    ) -> float:
        """Calculate content uniqueness score based on title/description similarity."""
        if not existing_urls:
            return 1.0
        
        # Simple content similarity check
        current_words = set(evidence_url.title.lower().split())
        
        max_similarity = 0.0
        for existing_url in existing_urls:
            existing_words = set(existing_url.title.lower().split())
            
            if current_words and existing_words:
                intersection = current_words.intersection(existing_words)
                union = current_words.union(existing_words)
                similarity = len(intersection) / len(union)
                max_similarity = max(max_similarity, similarity)
        
        # Return inverse of similarity (higher score for more unique content)
        return 1.0 - max_similarity
    
    def _classify_source_tier(self, url_candidate: URLCandidate) -> str:
        """Classify the source tier of a URL candidate."""
        domain = url_candidate.domain.lower()
        
        # Check if it's a major company
        if self.alternative_source_manager.is_major_company(domain.replace('.com', '')):
            return SourceTier.MAJOR.value
        
        # Check against alternative companies database
        for category, sources in self.alternative_source_manager.alternative_companies.items():
            for source in sources:
                if source.domain.lower() == domain:
                    return source.tier.value
        
        # Check against niche sources
        for category, sources in self.alternative_source_manager.niche_sources.items():
            for source in sources:
                if source.domain.lower() == domain:
                    return source.tier.value
        
        # Default classification based on domain authority
        domain_authority = self._get_domain_authority(domain)
        if domain_authority >= 0.8:
            return SourceTier.MAJOR.value
        elif domain_authority >= 0.6:
            return SourceTier.MID_TIER.value
        else:
            return SourceTier.ALTERNATIVE.value
    
    def _calculate_uniqueness_factor(self, url_candidate: URLCandidate) -> float:
        """Calculate how unique this source is globally."""
        domain = url_candidate.domain.lower()
        
        # Check global usage
        domain_usage = self.global_registry.used_domains.get(domain, 0)
        
        # Higher uniqueness for less used domains
        if domain_usage == 0:
            return 1.0
        elif domain_usage == 1:
            return 0.8
        elif domain_usage == 2:
            return 0.6
        else:
            return 0.3
    
    def _determine_source_tier(self, evidence_url: EnhancedEvidenceURL) -> str:
        """Determine source tier for registry registration."""
        return evidence_url.source_tier
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL (inherited from parent but ensure consistency)."""
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


def test_uniqueness_aware_evidence_validator():
    """Test function for the Uniqueness-Aware Evidence Validator."""
    from explanation_analyzer import ExplanationAnalyzer, SearchableClaim, ClaimType
    from web_search_engine import URLCandidate, SearchResult
    from search_query_generator import SearchQuery
    
    print("Testing Uniqueness-Aware Evidence Validator:")
    print("=" * 60)
    
    # Create components
    registry = GlobalURLRegistry()
    validator = UniquenessAwareEvidenceValidator(registry)
    
    # Mock URL candidates
    url_candidates = [
        URLCandidate(
            url="https://pipedrive.com/pricing/",
            title="Pipedrive Pricing | Sales CRM Plans",
            snippet="Choose the right Pipedrive plan for your sales team. Compare features and pricing.",
            domain="pipedrive.com",
            page_type="pricing",
            search_query="crm pricing plans",
            citation_index=0
        ),
        URLCandidate(
            url="https://freshworks.com/crm/",
            title="Freshworks CRM | Customer Relationship Management",
            snippet="Powerful CRM software to manage your customer relationships effectively.",
            domain="freshworks.com",
            page_type="product",
            search_query="crm solutions",
            citation_index=1
        ),
        URLCandidate(
            url="https://salesforce.com/pricing/",
            title="Salesforce Pricing | CRM Plans",
            snippet="Salesforce CRM pricing and plans for businesses of all sizes.",
            domain="salesforce.com",
            page_type="pricing",
            search_query="crm pricing",
            citation_index=2
        )
    ]
    
    # Mock claim
    claim = SearchableClaim(
        text="Currently researching CRM solutions for small business",
        entities={'companies': ['crm'], 'products': ['crm']},
        claim_type=ClaimType.PRODUCT_EVALUATION,
        priority=10,
        search_terms=['crm', 'solutions', 'small', 'business'],
        confidence=0.9
    )
    
    # Mock search results
    search_results = [
        SearchResult(
            query=SearchQuery("crm alternatives", [], [], 10, "", ""),
            urls=url_candidates,
            citations=[],
            search_metadata={},
            success=True,
            error_message=None
        )
    ]
    
    # Test validation with uniqueness
    print("1. Testing uniqueness-aware validation:")
    enhanced_urls = validator.validate_with_uniqueness(
        search_results, claim, "candidate_1"
    )
    
    print(f"Found {len(enhanced_urls)} enhanced evidence URLs:")
    for i, url in enumerate(enhanced_urls, 1):
        print(f"\n{i}. {url.title}")
        print(f"   URL: {url.url}")
        print(f"   Source Tier: {url.source_tier}")
        print(f"   Relevance: {url.relevance_score:.3f}")
        print(f"   Diversity: {url.diversity_score:.3f}")
        print(f"   Uniqueness: {url.uniqueness_factor:.3f}")
        print(f"   Combined Quality: {(url.relevance_score + url.diversity_score) / 2:.3f}")
    
    # Register usage
    validator.register_evidence_usage(enhanced_urls, "candidate_1")
    
    # Test with second candidate (should get different URLs)
    print(f"\n2. Testing with second candidate (uniqueness enforcement):")
    enhanced_urls_2 = validator.validate_with_uniqueness(
        search_results, claim, "candidate_2"
    )
    
    print(f"Found {len(enhanced_urls_2)} URLs for candidate 2:")
    for url in enhanced_urls_2:
        print(f"   {url.title} - {url.url}")
    
    # Show registry stats
    print(f"\n3. Registry Statistics:")
    stats = registry.get_registry_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Show diversity metrics
    print(f"\n4. Diversity Metrics:")
    metrics = registry.get_diversity_metrics()
    print(f"Unique domains: {metrics.total_unique_domains}")
    print(f"Source tier distribution: {metrics.source_tier_distribution}")
    print(f"Diversity index: {metrics.diversity_index:.3f}")


if __name__ == '__main__':
    test_uniqueness_aware_evidence_validator()