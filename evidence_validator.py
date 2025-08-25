#!/usr/bin/env python3
"""
Evidence Validator for URL Evidence Finder.

This module validates and ranks URLs by relevance and quality, filtering out
low-quality sources and categorizing evidence types for presentation.
"""

import re
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from explanation_analyzer import SearchableClaim, ClaimType
from web_search_engine import SearchResult, URLCandidate
from improved_relevance_scorer import ImprovedRelevanceScorer


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
class EvidenceURL:
    """Represents a validated URL that provides evidence for a claim."""
    url: str                        # The actual URL
    title: str                      # Page title
    description: str                # Brief description of relevance
    evidence_type: EvidenceType     # Category of evidence
    relevance_score: float          # Relevance score (0-1)
    confidence_level: str           # high, medium, low
    supporting_explanation: str     # How this URL supports the claim
    domain_authority: float         # Authority/trustworthiness score (0-1)
    page_quality_score: float       # Overall page quality score (0-1)
    last_validated: float           # Timestamp when validated


class EvidenceValidator:
    """Validates and ranks URLs by relevance and quality."""
    
    def __init__(self):
        """Initialize the evidence validator with improved relevance scoring."""
        self.improved_scorer = ImprovedRelevanceScorer()
        
        # Keep existing domain authority and quality scoring logic
        self.domain_authority_cache = {}
        self.quality_indicators = {
            'high_quality': ['official', 'documentation', 'guide', 'whitepaper'],
            'medium_quality': ['blog', 'article', 'news', 'review'],
            'low_quality': ['forum', 'discussion', 'comment', 'social']
        }
    def __init__(self):
        # Track used URLs globally to ensure uniqueness across candidates
        self.used_urls = set()
        self.used_domains_per_candidate = {}
        self.candidate_url_history = {}
        
        # Domain authority scores (0-1, 1 being highest authority)
        self.domain_authority_scores = {
            # Major SaaS companies
            'salesforce.com': 0.95,
            'hubspot.com': 0.90,
            'microsoft.com': 0.95,
            'google.com': 0.95,
            'amazon.com': 0.95,
            'oracle.com': 0.85,
            'sap.com': 0.85,
            'adobe.com': 0.85,
            'zoom.us': 0.80,
            'slack.com': 0.80,
            'shopify.com': 0.85,
            'stripe.com': 0.85,
            'twilio.com': 0.80,
            'zendesk.com': 0.80,
            'atlassian.com': 0.80,
            'servicenow.com': 0.80,
            'workday.com': 0.80,
            'okta.com': 0.75,
            'tableau.com': 0.80,
            'snowflake.com': 0.75,
            'databricks.com': 0.75,
            'mongodb.com': 0.75,
            'docusign.com': 0.75,
            'box.com': 0.75,
            'dropbox.com': 0.75,
            'asana.com': 0.70,
            'trello.com': 0.70,
            'notion.so': 0.70,
            
            # Research and analysis
            'gartner.com': 0.90,
            'forrester.com': 0.85,
            'idc.com': 0.80,
            'mckinsey.com': 0.85,
            'deloitte.com': 0.80,
            'pwc.com': 0.80,
            'accenture.com': 0.75,
            
            # Comparison and review sites
            'g2.com': 0.85,
            'capterra.com': 0.80,
            'trustradius.com': 0.75,
            'softwareadvice.com': 0.75,
            'trustpilot.com': 0.70,
            'glassdoor.com': 0.70,
            
            # News and media
            'techcrunch.com': 0.80,
            'venturebeat.com': 0.75,
            'forbes.com': 0.85,
            'businessinsider.com': 0.75,
            'reuters.com': 0.90,
            'bloomberg.com': 0.85,
            'wsj.com': 0.90,
            'ft.com': 0.85,
            
            # Tech publications
            'arstechnica.com': 0.75,
            'wired.com': 0.80,
            'theverge.com': 0.75,
            'engadget.com': 0.70,
            'zdnet.com': 0.70,
            'cnet.com': 0.70,
        }
        
        # Low-quality domain patterns to avoid
        self.low_quality_patterns = [
            r'.*\.blogspot\.com',
            r'.*\.wordpress\.com',
            r'.*\.medium\.com',
            r'.*\.reddit\.com',
            r'.*\.quora\.com',
            r'.*\.yahoo\.com',
            r'.*\.answers\.com',
            r'.*\.ehow\.com',
            r'.*\.wikihow\.com',
            r'.*ads.*',
            r'.*spam.*',
            r'.*affiliate.*',
        ]
        
        # Spam/promotional keywords to avoid
        self.spam_keywords = [
            'buy now', 'click here', 'free trial', 'limited time',
            'act now', 'special offer', 'discount', 'coupon',
            'affiliate', 'sponsored', 'advertisement', 'promo'
        ]
    
    def validate_and_rank(self, results: List[SearchResult], claim: SearchableClaim, candidate_id: str = None) -> List[EvidenceURL]:
        """
        Validate and rank URLs by relevance and quality with uniqueness enforcement.
        
        Args:
            results: Raw search results
            claim: Original claim being supported
            candidate_id: Unique identifier for candidate to ensure URL uniqueness
            
        Returns:
            Ranked list of evidence URLs (unique across all candidates)
        """
        all_candidates = []
        
        # Collect all URL candidates from search results
        for result in results:
            if result.success:
                for url_candidate in result.urls:
                    # Skip if URL already used globally
                    if url_candidate.url in self.used_urls:
                        continue
                    
                    # Validate URL quality
                    if self.validate_url_quality(url_candidate):
                        evidence_url = self._create_evidence_url(url_candidate, claim, result)
                        if evidence_url:
                            all_candidates.append(evidence_url)
        
        # Remove duplicates based on URL
        unique_candidates = self._remove_duplicates(all_candidates)
        
        # Apply uniqueness filters
        unique_candidates = self._enforce_url_uniqueness(unique_candidates, candidate_id)
        
        # Rank by combined score
        ranked_candidates = sorted(
            unique_candidates,
            key=lambda url: (url.relevance_score * 0.6 + url.page_quality_score * 0.4),
            reverse=True
        )
        
        # Apply quality assurance filters
        filtered_candidates = self._apply_quality_filters(ranked_candidates, claim)
        
        # Limit to top results and ensure diversity
        final_candidates = self._select_diverse_results(filtered_candidates, max_count=5)
        
        # Track used URLs
        if candidate_id:
            self._track_used_urls(final_candidates, candidate_id)
        
        return final_candidates
    
    def validate_url_quality(self, url_candidate: URLCandidate) -> bool:
        """
        Check if URL meets quality standards.
        
        Args:
            url_candidate: URL candidate to validate
            
        Returns:
            True if URL passes quality checks
        """
        # Check for low-quality domain patterns
        for pattern in self.low_quality_patterns:
            if re.match(pattern, url_candidate.domain, re.IGNORECASE):
                return False
        
        # Check for spam keywords in title and snippet
        content = (url_candidate.title + " " + url_candidate.snippet).lower()
        spam_count = sum(1 for keyword in self.spam_keywords if keyword in content)
        if spam_count >= 2:  # Allow 1 spam keyword, but not 2+
            return False
        
        # Check URL structure
        if not self._is_valid_url_structure(url_candidate.url):
            return False
        
        # Check title quality
        if not self._is_valid_title(url_candidate.title):
            return False
        
        return True
    
    def calculate_relevance_score(self, url_candidate: URLCandidate, claim: SearchableClaim) -> float:
        """
        Calculate how well URL supports the claim using improved behavioral context awareness.
        
        Args:
            url_candidate: URL candidate to score
            claim: Original claim
            
        Returns:
            Enhanced relevance score between 0 and 1
        """
        # Use the improved relevance scorer for better behavioral context awareness
        enhanced_score = self.improved_scorer.calculate_enhanced_relevance_score(url_candidate, claim)
        
        # Fallback to legacy scoring if enhanced scorer fails
        if enhanced_score is None or enhanced_score < 0:
            return self._calculate_legacy_relevance_score(url_candidate, claim)
        
        return enhanced_score
    
    def _calculate_legacy_relevance_score(self, url_candidate: URLCandidate, claim: SearchableClaim) -> float:
        """
        Legacy relevance calculation method (kept as fallback).
        
        Args:
            url_candidate: URL candidate to score
            claim: Original claim
            
        Returns:
            Relevance score between 0 and 1
        """
        score = 0.0
        
        # Title relevance (30%)
        title_score = self._calculate_text_similarity(url_candidate.title.lower(), claim.text.lower())
        score += title_score * 0.3
        
        # Content snippet relevance (25%)
        snippet_score = self._calculate_text_similarity(url_candidate.snippet.lower(), claim.text.lower())
        score += snippet_score * 0.25
        
        # Domain authority (20%)
        domain_score = self._get_domain_authority(url_candidate.domain)
        score += domain_score * 0.2
        
        # URL structure relevance (15%)
        url_score = self._calculate_url_relevance(url_candidate.url, claim)
        score += url_score * 0.15
        
        # Search terms match (10%)
        terms_score = self._calculate_search_terms_match(
            url_candidate.title + " " + url_candidate.snippet,
            claim.search_terms
        )
        score += terms_score * 0.1
        
        return min(score, 1.0)
    
    def categorize_evidence(self, url_candidate: URLCandidate) -> EvidenceType:
        """
        Categorize evidence type based on URL and content.
        
        Args:
            url_candidate: URL candidate to categorize
            
        Returns:
            EvidenceType enum value
        """
        url_lower = url_candidate.url.lower()
        title_lower = url_candidate.title.lower()
        domain = url_candidate.domain.lower()
        
        # Official company pages
        if self._is_official_company_domain(domain):
            if any(word in url_lower for word in ['pricing', 'price', 'plan', 'cost']):
                return EvidenceType.PRICING_PAGE
            elif any(word in url_lower for word in ['product', 'solution', 'platform']):
                return EvidenceType.PRODUCT_PAGE
            elif any(word in url_lower for word in ['doc', 'guide', 'api', 'help']):
                return EvidenceType.DOCUMENTATION
            else:
                return EvidenceType.OFFICIAL_COMPANY_PAGE
        
        # Comparison sites
        if domain in ['g2.com', 'capterra.com', 'trustradius.com', 'softwareadvice.com']:
            return EvidenceType.COMPARISON_SITE
        
        # Review sites
        if domain in ['trustpilot.com', 'glassdoor.com'] or 'review' in title_lower:
            return EvidenceType.REVIEW_SITE
        
        # Research and reports
        if domain in ['gartner.com', 'forrester.com', 'idc.com', 'mckinsey.com']:
            return EvidenceType.INDUSTRY_REPORT
        
        # News articles
        if domain in ['techcrunch.com', 'venturebeat.com', 'forbes.com', 'businessinsider.com']:
            return EvidenceType.NEWS_ARTICLE
        
        # Documentation
        if any(word in url_lower for word in ['doc', 'guide', 'api', 'help', 'support']):
            return EvidenceType.DOCUMENTATION
        
        # Case studies
        if 'case-study' in url_lower or 'case study' in title_lower:
            return EvidenceType.CASE_STUDY
        
        # Blog posts
        if 'blog' in url_lower or 'blog' in domain:
            return EvidenceType.BLOG_POST
        
        # Pricing pages
        if any(word in url_lower for word in ['pricing', 'price', 'plan', 'cost']):
            return EvidenceType.PRICING_PAGE
        
        # Product pages
        if any(word in url_lower for word in ['product', 'solution', 'platform']):
            return EvidenceType.PRODUCT_PAGE
        
        # Default to general information
        return EvidenceType.GENERAL_INFORMATION
    
    def _create_evidence_url(self, url_candidate: URLCandidate, claim: SearchableClaim, search_result: SearchResult) -> Optional[EvidenceURL]:
        """Create an EvidenceURL from a URL candidate."""
        try:
            # Calculate scores
            relevance_score = self.calculate_relevance_score(url_candidate, claim)
            page_quality_score = self._calculate_page_quality_score(url_candidate)
            domain_authority = self._get_domain_authority(url_candidate.domain)
            
            # Categorize evidence
            evidence_type = self.categorize_evidence(url_candidate)
            
            # Generate description and explanation
            description = self._generate_description(url_candidate, evidence_type)
            supporting_explanation = self._generate_supporting_explanation(url_candidate, claim, evidence_type)
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(relevance_score, page_quality_score, domain_authority)
            
            return EvidenceURL(
                url=url_candidate.url,
                title=url_candidate.title,
                description=description,
                evidence_type=evidence_type,
                relevance_score=relevance_score,
                confidence_level=confidence_level,
                supporting_explanation=supporting_explanation,
                domain_authority=domain_authority,
                page_quality_score=page_quality_score,
                last_validated=time.time()
            )
            
        except Exception as e:
            print(f"[Evidence Validator] Error creating evidence URL: {e}")
            return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on common words."""
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_url_relevance(self, url: str, claim: SearchableClaim) -> float:
        """Calculate URL structure relevance to the claim."""
        url_lower = url.lower()
        score = 0.0
        
        # Check for claim type specific patterns
        if claim.claim_type == ClaimType.PRICING_RESEARCH:
            if any(word in url_lower for word in ['pricing', 'price', 'plan', 'cost']):
                score += 0.5
        
        elif claim.claim_type == ClaimType.PRODUCT_EVALUATION:
            if any(word in url_lower for word in ['product', 'solution', 'platform', 'features']):
                score += 0.5
        
        elif claim.claim_type == ClaimType.COMPANY_RESEARCH:
            # Check if it's from a mentioned company's domain
            for company in claim.entities.get('companies', []):
                if company.lower() in url_lower:
                    score += 0.7
                    break
        
        # Check for search terms in URL
        for term in claim.search_terms:
            if term.lower() in url_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_search_terms_match(self, text: str, search_terms: List[str]) -> float:
        """Calculate how many search terms appear in the text."""
        if not search_terms:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for term in search_terms if term.lower() in text_lower)
        
        return matches / len(search_terms)
    
    def _get_domain_authority(self, domain: str) -> float:
        """Get domain authority score for a domain."""
        return self.domain_authority_scores.get(domain.lower(), 0.5)  # Default to 0.5
    
    def _calculate_page_quality_score(self, url_candidate: URLCandidate) -> float:
        """Calculate overall page quality score."""
        score = 0.5  # Base score
        
        # Title quality
        if url_candidate.title and len(url_candidate.title) > 10:
            score += 0.2
        
        # Snippet quality
        if url_candidate.snippet and len(url_candidate.snippet) > 20:
            score += 0.2
        
        # Domain authority
        domain_score = self._get_domain_authority(url_candidate.domain)
        score += domain_score * 0.3
        
        return min(score, 1.0)
    
    def _is_official_company_domain(self, domain: str) -> bool:
        """Check if domain is an official company domain."""
        # Check against known company domains
        company_domains = [
            'salesforce.com', 'hubspot.com', 'microsoft.com', 'google.com',
            'amazon.com', 'oracle.com', 'sap.com', 'adobe.com', 'zoom.us',
            'slack.com', 'shopify.com', 'stripe.com', 'twilio.com'
        ]
        return domain.lower() in company_domains
    
    def _is_valid_url_structure(self, url: str) -> bool:
        """Check if URL has valid structure."""
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'.*\.tk$', r'.*\.ml$', r'.*\.ga$',  # Suspicious TLDs
            r'.*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.*',  # IP addresses
            r'.*[a-z0-9]{20,}\..*',  # Very long random strings
        ]
        
        for pattern in suspicious_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _is_valid_title(self, title: str) -> bool:
        """Check if title is valid and meaningful."""
        if not title or len(title) < 5:
            return False
        
        # Check for spam patterns
        # Check for ALL CAPS (without IGNORECASE to only catch actual caps)
        if re.match(r'^[A-Z\s!]+$', title):
            return False
            
        # Check for price mentions and discount patterns (case insensitive)
        price_discount_patterns = [
            r'.*\$\d+.*',    # Price mentions
            r'.*\d+%.*off.*', # Discount mentions
        ]
        
        for pattern in price_discount_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return False
        
        return True
    
    def _generate_description(self, url_candidate: URLCandidate, evidence_type: EvidenceType) -> str:
        """Generate a description for the evidence URL."""
        type_descriptions = {
            EvidenceType.OFFICIAL_COMPANY_PAGE: "Official company information and overview",
            EvidenceType.PRODUCT_PAGE: "Product features and capabilities information",
            EvidenceType.PRICING_PAGE: "Pricing plans and cost information",
            EvidenceType.DOCUMENTATION: "Technical documentation and guides",
            EvidenceType.NEWS_ARTICLE: "News article and industry coverage",
            EvidenceType.CASE_STUDY: "Case study and implementation example",
            EvidenceType.COMPARISON_SITE: "Product comparison and reviews",
            EvidenceType.INDUSTRY_REPORT: "Industry analysis and research report",
            EvidenceType.REVIEW_SITE: "User reviews and ratings",
            EvidenceType.BLOG_POST: "Blog post and insights",
            EvidenceType.GENERAL_INFORMATION: "General information and resources"
        }
        
        base_description = type_descriptions.get(evidence_type, "Relevant information")
        
        # Add domain context if it's a well-known source
        domain = url_candidate.domain.lower()
        if domain in ['g2.com', 'capterra.com']:
            base_description += " from trusted software review platform"
        elif domain in ['gartner.com', 'forrester.com']:
            base_description += " from leading research firm"
        elif self._is_official_company_domain(domain):
            base_description += " from official company website"
        
        return base_description
    
    def _generate_supporting_explanation(self, url_candidate: URLCandidate, claim: SearchableClaim, evidence_type: EvidenceType) -> str:
        """Generate explanation of how URL supports the claim."""
        # Extract key elements from claim
        companies = claim.entities.get('companies', [])
        activities = claim.entities.get('activities', [])
        
        explanation_parts = []
        
        # Company-specific support
        if companies:
            for company in companies:
                if company.lower() in url_candidate.url.lower() or company.lower() in url_candidate.title.lower():
                    explanation_parts.append(f"provides {company}-specific information")
                    break
        
        # Activity-specific support
        if activities:
            activity = activities[0]
            if evidence_type == EvidenceType.PRICING_PAGE:
                explanation_parts.append(f"supports {activity} pricing information")
            elif evidence_type == EvidenceType.PRODUCT_PAGE:
                explanation_parts.append(f"supports {activity} product details")
            elif evidence_type == EvidenceType.COMPARISON_SITE:
                explanation_parts.append(f"supports {activity} comparison analysis")
            else:
                explanation_parts.append(f"supports {activity} activities")
        
        # Evidence type specific support
        if evidence_type == EvidenceType.OFFICIAL_COMPANY_PAGE:
            explanation_parts.append("from authoritative company source")
        elif evidence_type == EvidenceType.INDUSTRY_REPORT:
            explanation_parts.append("provides industry research and analysis")
        
        # Fallback
        if not explanation_parts:
            explanation_parts.append("provides relevant supporting information")
        
        return "Directly " + " and ".join(explanation_parts) + " mentioned in the behavioral claim"
    
    def _determine_confidence_level(self, relevance_score: float, page_quality_score: float, domain_authority: float) -> str:
        """Determine confidence level based on scores."""
        combined_score = (relevance_score * 0.5 + page_quality_score * 0.3 + domain_authority * 0.2)
        
        if combined_score >= 0.8:
            return "high"
        elif combined_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _remove_duplicates(self, candidates: List[EvidenceURL]) -> List[EvidenceURL]:
        """Remove duplicate URLs."""
        seen_urls = set()
        unique_candidates = []
        
        for candidate in candidates:
            if candidate.url not in seen_urls:
                seen_urls.add(candidate.url)
                unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _apply_quality_filters(self, candidates: List[EvidenceURL], claim: SearchableClaim) -> List[EvidenceURL]:
        """Apply quality filters to candidates."""
        filtered = []
        
        for candidate in candidates:
            # Minimum relevance threshold
            if candidate.relevance_score < 0.3:
                continue
            
            # Minimum quality threshold
            if candidate.page_quality_score < 0.4:
                continue
            
            # Require at least medium confidence for low authority domains
            if candidate.domain_authority < 0.6 and candidate.confidence_level == "low":
                continue
            
            filtered.append(candidate)
        
        return filtered
    
    def _select_diverse_results(self, candidates: List[EvidenceURL], max_count: int = 5) -> List[EvidenceURL]:
        """Select diverse results ensuring variety in evidence types and domains."""
        if len(candidates) <= max_count:
            return candidates
        
        selected = []
        used_domains = set()
        used_evidence_types = set()
        
        # First pass: select high-quality diverse results
        for candidate in candidates:
            if len(selected) >= max_count:
                break
            
            # Prefer diversity in domains and evidence types
            domain_new = candidate.domain_authority not in used_domains
            type_new = candidate.evidence_type not in used_evidence_types
            
            if domain_new or type_new or len(selected) < 2:
                selected.append(candidate)
                used_domains.add(candidate.domain_authority)
                used_evidence_types.add(candidate.evidence_type)
        
        # Fill remaining slots with best remaining candidates
        remaining_slots = max_count - len(selected)
        if remaining_slots > 0:
            remaining_candidates = [c for c in candidates if c not in selected]
            selected.extend(remaining_candidates[:remaining_slots])
        
        return selected


def test_evidence_validator():
    """Test function for the evidence validator."""
    from explanation_analyzer import ExplanationAnalyzer, SearchableClaim, ClaimType
    from web_search_engine import URLCandidate, SearchResult
    from search_query_generator import SearchQuery
    
    # Create test data
    validator = EvidenceValidator()
    
    # Mock search result
    url_candidate = URLCandidate(
        url="https://www.salesforce.com/products/platform/pricing/",
        title="Salesforce Platform Pricing | Plans & Packages",
        snippet="Choose the right Salesforce plan for your business. Compare pricing and features across all Salesforce products.",
        domain="salesforce.com",
        page_type="pricing",
        search_query="salesforce pricing plans",
        citation_index=0
    )
    
    # Mock claim
    claim = SearchableClaim(
        text="Currently researching Salesforce pricing options for enterprise deployment",
        entities={'companies': ['salesforce'], 'pricing_terms': ['pricing']},
        claim_type=ClaimType.PRICING_RESEARCH,
        priority=10,
        search_terms=['salesforce', 'pricing', 'enterprise'],
        confidence=0.9
    )
    
    # Mock search result
    search_result = SearchResult(
        query=SearchQuery("salesforce pricing", [], [], 10, "", ""),
        urls=[url_candidate],
        citations=[],
        search_metadata={},
        success=True,
        error_message=None
    )
    
    print("Testing Evidence Validator:")
    print("=" * 50)
    
    # Test validation
    is_valid = validator.validate_url_quality(url_candidate)
    print(f"URL Quality Valid: {is_valid}")
    
    # Test relevance scoring
    relevance = validator.calculate_relevance_score(url_candidate, claim)
    print(f"Relevance Score: {relevance:.3f}")
    
    # Test categorization
    evidence_type = validator.categorize_evidence(url_candidate)
    print(f"Evidence Type: {evidence_type.value}")
    
    # Test full validation and ranking
    evidence_urls = validator.validate_and_rank([search_result], claim)
    print(f"\nValidated Evidence URLs: {len(evidence_urls)}")
    
    for i, evidence in enumerate(evidence_urls, 1):
        print(f"\n{i}. {evidence.title}")
        print(f"   URL: {evidence.url}")
        print(f"   Type: {evidence.evidence_type.value}")
        print(f"   Relevance: {evidence.relevance_score:.3f}")
        print(f"   Quality: {evidence.page_quality_score:.3f}")
        print(f"   Confidence: {evidence.confidence_level}")
        print(f"   Support: {evidence.supporting_explanation}")


if __name__ == '__main__':
    test_evidence_validator()    

    def _enforce_url_uniqueness(self, candidates: List[EvidenceURL], candidate_id: str = None) -> List[EvidenceURL]:
        """Enforce URL uniqueness across all candidates."""
        unique_candidates = []
        
        for candidate in candidates:
            # Skip if URL already used
            if candidate.url in self.used_urls:
                continue
            
            # Skip if domain already used too many times for this candidate
            domain = self._extract_domain_from_url(candidate.url)
            if candidate_id:
                used_domains = self.used_domains_per_candidate.get(candidate_id, set())
                if domain in used_domains:
                    continue  # Avoid domain repetition within same candidate
            
            unique_candidates.append(candidate)
        
        return unique_candidates
    
    def _track_used_urls(self, evidence_urls: List[EvidenceURL], candidate_id: str):
        """Track used URLs and domains for uniqueness enforcement."""
        for evidence_url in evidence_urls:
            # Track globally used URLs
            self.used_urls.add(evidence_url.url)
            
            # Track domains per candidate
            domain = self._extract_domain_from_url(evidence_url.url)
            if candidate_id not in self.used_domains_per_candidate:
                self.used_domains_per_candidate[candidate_id] = set()
            self.used_domains_per_candidate[candidate_id].add(domain)
            
            # Track candidate URL history
            if candidate_id not in self.candidate_url_history:
                self.candidate_url_history[candidate_id] = []
            self.candidate_url_history[candidate_id].append({
                'url': evidence_url.url,
                'domain': domain,
                'evidence_type': evidence_url.evidence_type,
                'timestamp': evidence_url.last_validated
            })
    
    def _extract_domain_from_url(self, url: str) -> str:
        """Extract domain from URL for tracking purposes."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            # Fallback to simple extraction
            try:
                return url.split('/')[2].lower()
            except:
                return url.lower()
    
    def get_uniqueness_stats(self) -> Dict[str, Any]:
        """Get statistics about URL uniqueness and usage."""
        return {
            'total_unique_urls_used': len(self.used_urls),
            'candidates_processed': len(self.candidate_url_history),
            'average_urls_per_candidate': (
                sum(len(urls) for urls in self.candidate_url_history.values()) / 
                len(self.candidate_url_history) if self.candidate_url_history else 0
            ),
            'domain_diversity': len(set(
                self._extract_domain_from_url(url) for url in self.used_urls
            )),
            'candidates_with_urls': len([
                cid for cid, urls in self.candidate_url_history.items() if urls
            ])
        }
    
    def reset_uniqueness_tracking(self):
        """Reset uniqueness tracking (useful for testing or new batches)."""
        self.used_urls.clear()
        self.used_domains_per_candidate.clear()
        self.candidate_url_history.clear()