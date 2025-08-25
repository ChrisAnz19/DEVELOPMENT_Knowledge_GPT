#!/usr/bin/env python3
"""
Improved Relevance Scoring System

This module provides enhanced relevance scoring that better distinguishes between
generic informational content (like Wikipedia) and specific behavioral evidence.
"""

import re
from typing import List, Dict, Set
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    """Types of content that affect relevance scoring."""
    SPECIFIC_BEHAVIORAL = "specific_behavioral"      # High relevance for behavioral searches
    COMPANY_SPECIFIC = "company_specific"            # Company-specific content
    INDUSTRY_SPECIFIC = "industry_specific"          # Industry-specific content
    GENERIC_INFORMATIONAL = "generic_informational"  # Wikipedia, definitions, etc.
    PROMOTIONAL = "promotional"                      # Marketing/sales content
    NEWS_ARTICLE = "news_article"                   # News and press releases
    FORUM_DISCUSSION = "forum_discussion"           # Forums, Q&A sites
    ACADEMIC_RESEARCH = "academic_research"         # Research papers, studies

@dataclass
class RelevanceFactors:
    """Factors that influence relevance scoring."""
    content_type: ContentType
    behavioral_specificity: float  # 0-1, how specific to the behavioral claim
    entity_alignment: float        # 0-1, alignment with search entities (companies, roles)
    temporal_relevance: float      # 0-1, how recent/current the content is
    source_authority: float        # 0-1, authority of the source
    content_depth: float          # 0-1, depth vs surface-level information

class ImprovedRelevanceScorer:
    """Enhanced relevance scorer that better handles behavioral search context."""
    
    def __init__(self):
        # Generic content domains that should get lower scores for behavioral searches
        self.generic_domains = {
            'wikipedia.org': 0.2,      # Very low for behavioral searches
            'wikimedia.org': 0.2,
            'britannica.com': 0.3,
            'dictionary.com': 0.1,
            'merriam-webster.com': 0.1,
            'investopedia.com': 0.4,   # Slightly higher for business terms
            'indeed.com/career-advice': 0.3,  # Career advice is generic
            'glassdoor.com/blog': 0.3,
        }
        
        # Behavioral indicators that suggest specific, actionable content
        self.behavioral_indicators = {
            'high_value': [
                'hiring', 'recruiting', 'looking for', 'seeking', 'evaluating',
                'implementing', 'adopting', 'switching to', 'migrating from',
                'expanding', 'scaling', 'growing', 'launching', 'piloting',
                'testing', 'trialing', 'considering', 'researching',
                'budget for', 'investing in', 'purchasing', 'buying',
                'partnership', 'acquisition', 'merger', 'funding',
                'job posting', 'career opportunity', 'open position',
                'case study', 'success story', 'implementation',
                'roi', 'return on investment', 'cost savings',
                'efficiency gains', 'productivity improvement'
            ],
            'medium_value': [
                'strategy', 'planning', 'roadmap', 'initiative',
                'project', 'program', 'transformation', 'optimization',
                'analysis', 'assessment', 'evaluation', 'comparison',
                'requirements', 'specifications', 'criteria'
            ],
            'low_value': [
                'definition', 'what is', 'overview', 'introduction',
                'basics', 'fundamentals', 'guide', 'tutorial',
                'history', 'background', 'general information'
            ]
        }
        
        # Company-specific indicators
        self.company_indicators = [
            'careers', 'jobs', 'hiring', 'team', 'about us',
            'press release', 'news', 'announcement', 'blog',
            'case study', 'customer story', 'testimonial',
            'pricing', 'plans', 'products', 'solutions',
            'contact', 'sales', 'demo', 'trial'
        ]
        
        # Generic content patterns that should be penalized
        self.generic_patterns = [
            r'\b(definition|meaning|what is|overview|introduction)\b',
            r'\b(history of|background of|general information)\b',
            r'\b(types of|kinds of|categories of)\b',
            r'\b(encyclopedia|dictionary|glossary)\b',
            r'\b(basic|fundamental|elementary|simple)\b.*\b(guide|tutorial|explanation)\b'
        ]

    def calculate_enhanced_relevance_score(self, url_candidate, claim) -> float:
        """
        Calculate enhanced relevance score with behavioral context awareness.
        
        Args:
            url_candidate: URL candidate with title, snippet, url, domain
            claim: SearchableClaim with behavioral context
            
        Returns:
            Enhanced relevance score between 0 and 1
        """
        # Get relevance factors
        factors = self._analyze_relevance_factors(url_candidate, claim)
        
        # Calculate base similarity score
        base_score = self._calculate_base_similarity(url_candidate, claim)
        
        # Apply content type modifiers
        content_modifier = self._get_content_type_modifier(factors.content_type, claim)
        
        # Apply behavioral specificity boost
        behavioral_boost = factors.behavioral_specificity * 0.3
        
        # Apply entity alignment boost
        entity_boost = factors.entity_alignment * 0.2
        
        # Apply generic content penalty
        generic_penalty = self._calculate_generic_penalty(url_candidate, claim)
        
        # Calculate final score
        final_score = (
            base_score * content_modifier +
            behavioral_boost +
            entity_boost -
            generic_penalty
        )
        
        return max(0.0, min(1.0, final_score))

    def _analyze_relevance_factors(self, url_candidate, claim) -> RelevanceFactors:
        """Analyze various factors that affect relevance."""
        
        # Determine content type
        content_type = self._classify_content_type(url_candidate)
        
        # Calculate behavioral specificity
        behavioral_specificity = self._calculate_behavioral_specificity(url_candidate, claim)
        
        # Calculate entity alignment
        entity_alignment = self._calculate_entity_alignment(url_candidate, claim)
        
        # Calculate source authority (simplified)
        source_authority = self._calculate_source_authority(url_candidate)
        
        # Calculate content depth
        content_depth = self._calculate_content_depth(url_candidate)
        
        return RelevanceFactors(
            content_type=content_type,
            behavioral_specificity=behavioral_specificity,
            entity_alignment=entity_alignment,
            temporal_relevance=0.8,  # Default, could be enhanced with date parsing
            source_authority=source_authority,
            content_depth=content_depth
        )

    def _classify_content_type(self, url_candidate) -> ContentType:
        """Classify the type of content based on URL and content."""
        domain = url_candidate.domain.lower()
        url_lower = url_candidate.url.lower()
        title_lower = url_candidate.title.lower()
        snippet_lower = url_candidate.snippet.lower()
        
        # Check for generic informational content
        if any(generic_domain in domain for generic_domain in self.generic_domains.keys()):
            return ContentType.GENERIC_INFORMATIONAL
        
        # Check for company-specific content
        if any(indicator in url_lower for indicator in self.company_indicators):
            return ContentType.COMPANY_SPECIFIC
        
        # Check for behavioral content
        all_text = f"{title_lower} {snippet_lower}".lower()
        high_behavioral_count = sum(1 for indicator in self.behavioral_indicators['high_value'] 
                                  if indicator in all_text)
        
        if high_behavioral_count >= 2:
            return ContentType.SPECIFIC_BEHAVIORAL
        
        # Check for news content
        if any(term in domain for term in ['news', 'press', 'reuters', 'bloomberg', 'techcrunch']):
            return ContentType.NEWS_ARTICLE
        
        # Check for forum/discussion content
        if any(term in domain for term in ['reddit', 'stackoverflow', 'quora', 'forum']):
            return ContentType.FORUM_DISCUSSION
        
        # Default to industry specific
        return ContentType.INDUSTRY_SPECIFIC

    def _calculate_behavioral_specificity(self, url_candidate, claim) -> float:
        """Calculate how specific the content is to behavioral claims."""
        all_text = f"{url_candidate.title} {url_candidate.snippet}".lower()
        
        # Count behavioral indicators
        high_count = sum(1 for indicator in self.behavioral_indicators['high_value'] 
                        if indicator in all_text)
        medium_count = sum(1 for indicator in self.behavioral_indicators['medium_value'] 
                          if indicator in all_text)
        low_count = sum(1 for indicator in self.behavioral_indicators['low_value'] 
                       if indicator in all_text)
        
        # Calculate weighted score
        behavioral_score = (high_count * 1.0 + medium_count * 0.6 + low_count * 0.2) / 5.0
        
        # Penalty for generic patterns
        generic_penalty = sum(1 for pattern in self.generic_patterns 
                            if re.search(pattern, all_text, re.IGNORECASE))
        
        return max(0.0, min(1.0, behavioral_score - (generic_penalty * 0.3)))

    def _calculate_entity_alignment(self, url_candidate, claim) -> float:
        """Calculate alignment with search entities (companies, roles, etc.)."""
        all_text = f"{url_candidate.title} {url_candidate.snippet} {url_candidate.url}".lower()
        
        alignment_score = 0.0
        total_entities = 0
        
        # Check company alignment
        companies = claim.entities.get('companies', [])
        if companies:
            company_matches = sum(1 for company in companies 
                                if company.lower() in all_text)
            alignment_score += (company_matches / len(companies)) * 0.4
            total_entities += len(companies)
        
        # Check role/title alignment
        roles = claim.entities.get('roles', [])
        if roles:
            role_matches = sum(1 for role in roles 
                             if role.lower() in all_text)
            alignment_score += (role_matches / len(roles)) * 0.3
            total_entities += len(roles)
        
        # Check industry alignment
        industries = claim.entities.get('industries', [])
        if industries:
            industry_matches = sum(1 for industry in industries 
                                 if industry.lower() in all_text)
            alignment_score += (industry_matches / len(industries)) * 0.3
            total_entities += len(industries)
        
        return alignment_score if total_entities > 0 else 0.5

    def _get_content_type_modifier(self, content_type: ContentType, claim) -> float:
        """Get modifier based on content type and claim context."""
        
        # For behavioral claims, heavily penalize generic informational content
        if hasattr(claim, 'claim_type') and 'behavioral' in str(claim.claim_type).lower():
            modifiers = {
                ContentType.SPECIFIC_BEHAVIORAL: 1.2,      # Boost behavioral content
                ContentType.COMPANY_SPECIFIC: 1.0,         # Neutral for company content
                ContentType.INDUSTRY_SPECIFIC: 0.8,        # Slight penalty
                ContentType.GENERIC_INFORMATIONAL: 0.2,    # Heavy penalty for Wikipedia, etc.
                ContentType.NEWS_ARTICLE: 0.7,             # News can be relevant but not primary
                ContentType.FORUM_DISCUSSION: 0.6,         # Forums less reliable
                ContentType.ACADEMIC_RESEARCH: 0.9,        # Research is good but not behavioral
                ContentType.PROMOTIONAL: 0.5               # Marketing content less valuable
            }
        else:
            # For non-behavioral claims, be more lenient with informational content
            modifiers = {
                ContentType.SPECIFIC_BEHAVIORAL: 1.0,
                ContentType.COMPANY_SPECIFIC: 1.1,
                ContentType.INDUSTRY_SPECIFIC: 1.0,
                ContentType.GENERIC_INFORMATIONAL: 0.6,    # Less penalty for non-behavioral
                ContentType.NEWS_ARTICLE: 0.9,
                ContentType.FORUM_DISCUSSION: 0.7,
                ContentType.ACADEMIC_RESEARCH: 1.1,
                ContentType.PROMOTIONAL: 0.7
            }
        
        return modifiers.get(content_type, 0.8)

    def _calculate_generic_penalty(self, url_candidate, claim) -> float:
        """Calculate penalty for generic content that doesn't provide specific evidence."""
        domain = url_candidate.domain.lower()
        
        # Apply domain-specific penalties
        for generic_domain, penalty in self.generic_domains.items():
            if generic_domain in domain:
                # For behavioral searches, Wikipedia about job titles should get heavy penalty
                if 'behavioral' in str(getattr(claim, 'claim_type', '')).lower():
                    return 1.0 - penalty  # Convert to penalty (higher penalty for lower scores)
                else:
                    return (1.0 - penalty) * 0.5  # Lighter penalty for non-behavioral
        
        return 0.0

    def _calculate_base_similarity(self, url_candidate, claim) -> float:
        """Calculate base text similarity (existing logic)."""
        title_score = self._calculate_text_similarity(
            url_candidate.title.lower(), 
            claim.text.lower()
        )
        snippet_score = self._calculate_text_similarity(
            url_candidate.snippet.lower(), 
            claim.text.lower()
        )
        
        return (title_score * 0.6 + snippet_score * 0.4)

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

    def _calculate_source_authority(self, url_candidate) -> float:
        """Calculate source authority (simplified version)."""
        domain = url_candidate.domain.lower()
        
        # High authority domains
        high_authority = [
            'harvard.edu', 'stanford.edu', 'mit.edu',
            'mckinsey.com', 'bcg.com', 'bain.com',
            'deloitte.com', 'pwc.com', 'ey.com', 'kpmg.com',
            'gartner.com', 'forrester.com', 'idc.com'
        ]
        
        # Medium authority domains
        medium_authority = [
            'techcrunch.com', 'venturebeat.com', 'wired.com',
            'forbes.com', 'bloomberg.com', 'reuters.com',
            'wsj.com', 'ft.com', 'economist.com'
        ]
        
        if any(auth_domain in domain for auth_domain in high_authority):
            return 0.9
        elif any(auth_domain in domain for auth_domain in medium_authority):
            return 0.7
        elif domain.endswith('.edu') or domain.endswith('.gov'):
            return 0.8
        else:
            return 0.5

    def _calculate_content_depth(self, url_candidate) -> float:
        """Calculate content depth based on snippet length and URL structure."""
        snippet_length = len(url_candidate.snippet.split())
        url_depth = url_candidate.url.count('/') - 2  # Subtract protocol and domain
        
        # Longer snippets and deeper URLs suggest more detailed content
        depth_score = min(1.0, (snippet_length / 50.0) + (url_depth / 10.0))
        
        return depth_score


def test_improved_scoring():
    """Test the improved scoring system with example cases."""
    
    # Mock classes for testing
    class MockURLCandidate:
        def __init__(self, url, title, snippet, domain):
            self.url = url
            self.title = title
            self.snippet = snippet
            self.domain = domain
    
    class MockClaim:
        def __init__(self, text, claim_type="behavioral_search"):
            self.text = text
            self.claim_type = claim_type
            self.entities = {
                'companies': ['Salesforce', 'HubSpot'],
                'roles': ['CMO', 'Chief Marketing Officer'],
                'industries': ['SaaS', 'Technology']
            }
    
    scorer = ImprovedRelevanceScorer()
    
    # Test case 1: Wikipedia page about CMO (should get low score)
    wikipedia_candidate = MockURLCandidate(
        url="https://en.wikipedia.org/wiki/Chief_marketing_officer",
        title="Chief marketing officer - Wikipedia",
        snippet="A chief marketing officer (CMO) is a C-level corporate executive responsible for activities in an organization that have to do with creating, communicating and delivering offerings that have value for customers, clients or business partners.",
        domain="en.wikipedia.org"
    )
    
    # Test case 2: Specific job posting (should get high score)
    job_posting_candidate = MockURLCandidate(
        url="https://jobs.salesforce.com/careers/job/chief-marketing-officer-startup-experience",
        title="CMO - Startup Experience Required | Salesforce Careers",
        snippet="We're seeking an experienced Chief Marketing Officer who has successfully scaled marketing at high-growth startups. Must have experience transitioning from Fortune 500 to startup environment.",
        domain="jobs.salesforce.com"
    )
    
    # Test case 3: Industry article about CMO trends (should get medium score)
    industry_article_candidate = MockURLCandidate(
        url="https://techcrunch.com/2024/cmo-startup-trends-fortune-500-exodus",
        title="Why Fortune 500 CMOs Are Flocking to Startups in 2024",
        snippet="A growing trend shows senior marketing executives leaving established corporations for startup opportunities, driven by equity potential and innovation freedom.",
        domain="techcrunch.com"
    )
    
    claim = MockClaim("CMO looking to leave Fortune 500 role for startup opportunity")
    
    # Calculate scores
    wikipedia_score = scorer.calculate_enhanced_relevance_score(wikipedia_candidate, claim)
    job_posting_score = scorer.calculate_enhanced_relevance_score(job_posting_candidate, claim)
    industry_article_score = scorer.calculate_enhanced_relevance_score(industry_article_candidate, claim)
    
    print("Improved Relevance Scoring Test Results:")
    print(f"Wikipedia CMO page: {wikipedia_score:.3f} (should be low)")
    print(f"Specific job posting: {job_posting_score:.3f} (should be high)")
    print(f"Industry article: {industry_article_score:.3f} (should be medium)")
    
    return {
        'wikipedia': wikipedia_score,
        'job_posting': job_posting_score,
        'industry_article': industry_article_score
    }


if __name__ == "__main__":
    test_improved_scoring()