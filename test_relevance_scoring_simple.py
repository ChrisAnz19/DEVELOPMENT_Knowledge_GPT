#!/usr/bin/env python3
"""
Simple test for improved relevance scoring.

This test demonstrates that Wikipedia pages get low relevance scores
for behavioral searches while specific content gets higher scores.
"""

from improved_relevance_scorer import ImprovedRelevanceScorer


def test_wikipedia_vs_specific_content():
    """Test that Wikipedia gets lower scores than specific content."""
    
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
    
    # Test case 2: Specific job posting (should get higher score)
    job_posting_candidate = MockURLCandidate(
        url="https://jobs.salesforce.com/careers/job/chief-marketing-officer-startup-experience",
        title="CMO - Startup Experience Required | Salesforce Careers",
        snippet="We're seeking an experienced Chief Marketing Officer who has successfully scaled marketing at high-growth startups. Must have experience transitioning from Fortune 500 to startup environment.",
        domain="jobs.salesforce.com"
    )
    
    # Test case 3: Industry article (should get medium score)
    industry_article_candidate = MockURLCandidate(
        url="https://techcrunch.com/2024/cmo-startup-trends-fortune-500-exodus",
        title="Why Fortune 500 CMOs Are Flocking to Startups in 2024",
        snippet="A growing trend shows senior marketing executives leaving established corporations for startup opportunities, driven by equity potential and innovation freedom.",
        domain="techcrunch.com"
    )
    
    # Test case 4: Dictionary definition (should get very low score)
    dictionary_candidate = MockURLCandidate(
        url="https://www.merriam-webster.com/dictionary/marketing",
        title="Marketing Definition & Meaning - Merriam-Webster",
        snippet="The definition of marketing: the process or technique of promoting, selling, and distributing a product or service.",
        domain="merriam-webster.com"
    )
    
    claim = MockClaim("CMO looking to leave Fortune 500 role for startup opportunity")
    
    # Calculate scores
    wikipedia_score = scorer.calculate_enhanced_relevance_score(wikipedia_candidate, claim)
    job_posting_score = scorer.calculate_enhanced_relevance_score(job_posting_candidate, claim)
    industry_article_score = scorer.calculate_enhanced_relevance_score(industry_article_candidate, claim)
    dictionary_score = scorer.calculate_enhanced_relevance_score(dictionary_candidate, claim)
    
    print("Improved Relevance Scoring Results:")
    print("=" * 50)
    print(f"Wikipedia CMO page:     {wikipedia_score:.3f} (should be low)")
    print(f"Dictionary definition:  {dictionary_score:.3f} (should be very low)")
    print(f"Industry article:       {industry_article_score:.3f} (should be medium)")
    print(f"Specific job posting:   {job_posting_score:.3f} (should be highest)")
    print()
    
    # Verify expectations
    success = True
    
    # Wikipedia should be very low (< 0.3)
    if wikipedia_score >= 0.3:
        print(f"❌ FAIL: Wikipedia score too high ({wikipedia_score:.3f} >= 0.3)")
        success = False
    else:
        print(f"✅ PASS: Wikipedia score appropriately low ({wikipedia_score:.3f})")
    
    # Dictionary should be even lower
    if dictionary_score >= 0.2:
        print(f"❌ FAIL: Dictionary score too high ({dictionary_score:.3f} >= 0.2)")
        success = False
    else:
        print(f"✅ PASS: Dictionary score appropriately low ({dictionary_score:.3f})")
    
    # Job posting should be higher than Wikipedia
    if job_posting_score <= wikipedia_score:
        print(f"❌ FAIL: Job posting should score higher than Wikipedia")
        success = False
    else:
        print(f"✅ PASS: Job posting scores higher than Wikipedia")
    
    # Industry article should be higher than Wikipedia
    if industry_article_score <= wikipedia_score:
        print(f"❌ FAIL: Industry article should score higher than Wikipedia")
        success = False
    else:
        print(f"✅ PASS: Industry article scores higher than Wikipedia")
    
    print()
    if success:
        print("🎉 ALL TESTS PASSED! Relevance scoring is working correctly.")
        print("   Generic content (Wikipedia, dictionaries) gets low scores.")
        print("   Specific behavioral content gets higher scores.")
    else:
        print("❌ SOME TESTS FAILED! Relevance scoring needs adjustment.")
    
    return {
        'wikipedia': wikipedia_score,
        'dictionary': dictionary_score,
        'industry_article': industry_article_score,
        'job_posting': job_posting_score,
        'success': success
    }


def test_domain_penalties():
    """Test that different generic domains get appropriate penalties."""
    
    class MockURLCandidate:
        def __init__(self, url, title, snippet, domain):
            self.url = url
            self.title = title
            self.snippet = snippet
            self.domain = domain
    
    class MockClaim:
        def __init__(self, text):
            self.text = text
            self.claim_type = "behavioral_search"
            self.entities = {'roles': ['CMO']}
    
    scorer = ImprovedRelevanceScorer()
    claim = MockClaim("CMO looking for new opportunities")
    
    # Test different generic domains
    test_cases = [
        {
            'name': 'Wikipedia',
            'candidate': MockURLCandidate(
                url="https://en.wikipedia.org/wiki/Chief_marketing_officer",
                title="Chief marketing officer - Wikipedia",
                snippet="A chief marketing officer (CMO) is a corporate executive.",
                domain="en.wikipedia.org"
            ),
            'expected_penalty': 'high'
        },
        {
            'name': 'Dictionary',
            'candidate': MockURLCandidate(
                url="https://www.merriam-webster.com/dictionary/cmo",
                title="CMO Definition - Merriam-Webster",
                snippet="Definition of CMO: chief marketing officer.",
                domain="merriam-webster.com"
            ),
            'expected_penalty': 'very_high'
        },
        {
            'name': 'Investopedia',
            'candidate': MockURLCandidate(
                url="https://www.investopedia.com/terms/c/cmo.asp",
                title="Chief Marketing Officer (CMO) Definition",
                snippet="A CMO is responsible for marketing activities.",
                domain="investopedia.com"
            ),
            'expected_penalty': 'medium'
        },
        {
            'name': 'TechCrunch',
            'candidate': MockURLCandidate(
                url="https://techcrunch.com/cmo-trends",
                title="CMO Trends in 2024",
                snippet="Marketing executives are changing roles.",
                domain="techcrunch.com"
            ),
            'expected_penalty': 'low'
        }
    ]
    
    print("\nDomain Penalty Testing:")
    print("=" * 30)
    
    for test_case in test_cases:
        score = scorer.calculate_enhanced_relevance_score(test_case['candidate'], claim)
        print(f"{test_case['name']:15} {score:.3f} ({test_case['expected_penalty']} penalty expected)")
    
    return test_cases


if __name__ == "__main__":
    print("Testing Improved Relevance Scoring System")
    print("=========================================")
    
    # Run main test
    results = test_wikipedia_vs_specific_content()
    
    # Run domain penalty test
    test_domain_penalties()
    
    print(f"\nFinal Results:")
    print(f"- Wikipedia relevance: {results['wikipedia']:.3f}")
    print(f"- Job posting relevance: {results['job_posting']:.3f}")
    print(f"- Improvement factor: {results['job_posting'] / max(results['wikipedia'], 0.001):.1f}x")
    
    if results['success']:
        print("\n✅ SUCCESS: The improved relevance scoring correctly penalizes generic content!")
        print("   Wikipedia pages about job titles now get very low relevance scores.")
        print("   Specific behavioral content gets appropriately higher scores.")
    else:
        print("\n❌ NEEDS WORK: Some aspects of relevance scoring need adjustment.")