#!/usr/bin/env python3
"""
Test the integration of improved relevance scoring with the evidence validator.

This test verifies that Wikipedia pages and other generic content get appropriately
low relevance scores for behavioral searches.
"""

import unittest
from evidence_validator import EvidenceValidator
from web_search_engine import URLCandidate
from explanation_analyzer import SearchableClaim, ClaimType


class TestImprovedRelevanceIntegration(unittest.TestCase):
    """Test improved relevance scoring integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EvidenceValidator()
    
    def test_wikipedia_cmo_low_relevance(self):
        """Test that Wikipedia CMO page gets low relevance for behavioral search."""
        
        # Create Wikipedia URL candidate
        wikipedia_candidate = URLCandidate(
            url="https://en.wikipedia.org/wiki/Chief_marketing_officer",
            title="Chief marketing officer - Wikipedia",
            snippet="A chief marketing officer (CMO) is a C-level corporate executive responsible for activities in an organization that have to do with creating, communicating and delivering offerings that have value for customers, clients or business partners.",
            domain="en.wikipedia.org",
            page_type="encyclopedia",
            search_query="CMO Fortune 500 startup",
            citation_index=1
        )
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking to leave Fortune 500 role for startup opportunity",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Fortune 500'],
                'industries': ['startup']
            },
            search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity']
        )
        
        # Calculate relevance score
        relevance_score = self.validator.calculate_relevance_score(wikipedia_candidate, claim)
        
        # Wikipedia should get very low relevance for behavioral searches
        self.assertLess(relevance_score, 0.3, 
                       f"Wikipedia CMO page should have low relevance (<0.3), got {relevance_score:.3f}")
        print(f"✓ Wikipedia CMO relevance: {relevance_score:.3f} (correctly low)")
    
    def test_specific_job_posting_high_relevance(self):
        """Test that specific job postings get high relevance for behavioral search."""
        
        # Create specific job posting URL candidate
        job_candidate = URLCandidate(
            url="https://jobs.salesforce.com/careers/job/chief-marketing-officer-startup-experience",
            title="CMO - Startup Experience Required | Salesforce Careers",
            snippet="We're seeking an experienced Chief Marketing Officer who has successfully scaled marketing at high-growth startups. Must have experience transitioning from Fortune 500 to startup environment. Equity package available.",
            domain="jobs.salesforce.com",
            page_type="job_posting",
            search_query="CMO Fortune 500 startup",
            citation_index=1
        )
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking to leave Fortune 500 role for startup opportunity",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Fortune 500', 'Salesforce'],
                'industries': ['startup']
            },
            search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity']
        )
        
        # Calculate relevance score
        relevance_score = self.validator.calculate_relevance_score(job_candidate, claim)
        
        # Specific job posting should get higher relevance
        self.assertGreater(relevance_score, 0.2, 
                          f"Specific job posting should have higher relevance (>0.2), got {relevance_score:.3f}")
        print(f"✓ Job posting relevance: {relevance_score:.3f} (appropriately higher)")
    
    def test_industry_article_medium_relevance(self):
        """Test that industry articles get medium relevance for behavioral search."""
        
        # Create industry article URL candidate
        article_candidate = URLCandidate(
            url="https://techcrunch.com/2024/cmo-startup-trends-fortune-500-exodus",
            title="Why Fortune 500 CMOs Are Flocking to Startups in 2024",
            snippet="A growing trend shows senior marketing executives leaving established corporations for startup opportunities, driven by equity potential and innovation freedom. Survey data shows 40% increase in CMO transitions.",
            domain="techcrunch.com",
            page_type="news_article",
            search_query="CMO Fortune 500 startup",
            citation_index=1
        )
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking to leave Fortune 500 role for startup opportunity",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Fortune 500'],
                'industries': ['startup']
            },
            search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity']
        )
        
        # Calculate relevance score
        relevance_score = self.validator.calculate_relevance_score(article_candidate, claim)
        
        # Industry article should get medium relevance
        self.assertGreater(relevance_score, 0.1, 
                          f"Industry article should have medium relevance (>0.1), got {relevance_score:.3f}")
        print(f"✓ Industry article relevance: {relevance_score:.3f} (medium level)")
    
    def test_generic_content_penalty(self):
        """Test that various types of generic content get appropriate penalties."""
        
        # Test cases with different types of generic content
        test_cases = [
            {
                'name': 'Wikipedia definition',
                'candidate': URLCandidate(
                    url="https://en.wikipedia.org/wiki/Marketing",
                    title="Marketing - Wikipedia",
                    snippet="Marketing is the process of exploring, creating, and delivering value to meet the needs of a target market in terms of goods and services.",
                    domain="en.wikipedia.org",
                    page_type="encyclopedia",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                ),
                'expected_max': 0.3
            },
            {
                'name': 'Dictionary definition',
                'candidate': URLCandidate(
                    url="https://www.merriam-webster.com/dictionary/marketing",
                    title="Marketing Definition & Meaning - Merriam-Webster",
                    snippet="The definition of marketing: the process or technique of promoting, selling, and distributing a product or service.",
                    domain="merriam-webster.com",
                    page_type="dictionary",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                ),
                'expected_max': 0.2
            },
            {
                'name': 'Investopedia definition',
                'candidate': URLCandidate(
                    url="https://www.investopedia.com/terms/c/cmo.asp",
                    title="Chief Marketing Officer (CMO) Definition",
                    snippet="A chief marketing officer (CMO) is the executive responsible for marketing activities in an organization. Learn about CMO responsibilities and qualifications.",
                    domain="investopedia.com",
                    page_type="definition",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                ),
                'expected_max': 0.4
            }
        ]
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking to leave Fortune 500 role for startup opportunity",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Fortune 500'],
                'industries': ['startup']
            },
            search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity']
        )
        
        for test_case in test_cases:
            with self.subTest(content_type=test_case['name']):
                relevance_score = self.validator.calculate_relevance_score(
                    test_case['candidate'], claim
                )
                
                self.assertLess(
                    relevance_score, 
                    test_case['expected_max'],
                    f"{test_case['name']} should have low relevance (<{test_case['expected_max']}), got {relevance_score:.3f}"
                )
                print(f"✓ {test_case['name']} relevance: {relevance_score:.3f} (correctly penalized)")
    
    def test_company_specific_content_boost(self):
        """Test that company-specific content gets appropriate boost."""
        
        # Create company-specific URL candidate
        company_candidate = URLCandidate(
            url="https://salesforce.com/company/careers/marketing-leadership",
            title="Marketing Leadership Opportunities at Salesforce",
            snippet="Join our marketing team and help drive growth at one of the world's leading CRM companies. We're looking for experienced marketing executives to lead our expansion initiatives.",
            domain="salesforce.com",
            page_type="careers",
            search_query="CMO Salesforce opportunities",
            citation_index=1
        )
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking for opportunities at Salesforce",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Salesforce'],
                'industries': ['CRM', 'SaaS']
            },
            search_terms=['CMO', 'Salesforce', 'opportunities']
        )
        
        # Calculate relevance score
        relevance_score = self.validator.calculate_relevance_score(company_candidate, claim)
        
        # Company-specific content should get good relevance
        self.assertGreater(relevance_score, 0.2, 
                          f"Company-specific content should have good relevance (>0.2), got {relevance_score:.3f}")
        print(f"✓ Company-specific content relevance: {relevance_score:.3f} (appropriately boosted)")
    
    def test_relevance_score_comparison(self):
        """Test that relevance scores are properly ordered by specificity."""
        
        # Create different types of content
        candidates = [
            {
                'name': 'Wikipedia (generic)',
                'candidate': URLCandidate(
                    url="https://en.wikipedia.org/wiki/Chief_marketing_officer",
                    title="Chief marketing officer - Wikipedia",
                    snippet="A chief marketing officer (CMO) is a C-level corporate executive responsible for marketing activities.",
                    domain="en.wikipedia.org",
                    page_type="encyclopedia",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                )
            },
            {
                'name': 'Industry article (medium)',
                'candidate': URLCandidate(
                    url="https://techcrunch.com/cmo-trends-2024",
                    title="CMO Trends in 2024: The Startup Migration",
                    snippet="More Fortune 500 CMOs are making the jump to startups, seeking equity and innovation opportunities.",
                    domain="techcrunch.com",
                    page_type="news_article",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                )
            },
            {
                'name': 'Job posting (specific)',
                'candidate': URLCandidate(
                    url="https://jobs.startup.com/cmo-position-ex-fortune-500",
                    title="CMO Position - Fortune 500 Experience Required",
                    snippet="Seeking CMO with Fortune 500 background to join our fast-growing startup. Equity package and leadership opportunity.",
                    domain="jobs.startup.com",
                    page_type="job_posting",
                    search_query="CMO Fortune 500 startup",
                    citation_index=1
                )
            }
        ]
        
        # Create behavioral claim
        claim = SearchableClaim(
            text="CMO looking to leave Fortune 500 role for startup opportunity",
            claim_type=ClaimType.GENERAL_ACTIVITY,
            entities={
                'roles': ['CMO', 'Chief Marketing Officer'],
                'companies': ['Fortune 500'],
                'industries': ['startup']
            },
            search_terms=['CMO', 'Fortune 500', 'startup', 'leave', 'opportunity']
        )
        
        # Calculate scores
        scores = []
        for candidate_info in candidates:
            score = self.validator.calculate_relevance_score(
                candidate_info['candidate'], claim
            )
            scores.append((candidate_info['name'], score))
            print(f"✓ {candidate_info['name']}: {score:.3f}")
        
        # Verify ordering: Job posting > Industry article > Wikipedia
        job_score = next(score for name, score in scores if 'Job posting' in name)
        article_score = next(score for name, score in scores if 'Industry article' in name)
        wikipedia_score = next(score for name, score in scores if 'Wikipedia' in name)
        
        self.assertGreater(job_score, wikipedia_score, 
                          "Job posting should score higher than Wikipedia")
        self.assertGreater(article_score, wikipedia_score, 
                          "Industry article should score higher than Wikipedia")
        
        print(f"\n✓ Correct ordering: Job posting ({job_score:.3f}) > Industry article ({article_score:.3f}) > Wikipedia ({wikipedia_score:.3f})")


if __name__ == '__main__':
    print("Testing Improved Relevance Scoring Integration...")
    print("=" * 60)
    
    unittest.main(verbosity=2)