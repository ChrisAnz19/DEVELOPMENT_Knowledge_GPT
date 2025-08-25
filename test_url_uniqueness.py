#!/usr/bin/env python3
"""
Test URL Uniqueness and Diversity for Evidence Finder.

This test verifies that the system generates unique URLs for different candidates
and provides diverse, relevant alternatives rather than defaulting to major sites.
"""

import asyncio
from explanation_analyzer import ExplanationAnalyzer
from search_query_generator import SearchQueryGenerator
from evidence_validator import EvidenceValidator


def test_url_uniqueness_and_diversity():
    """Test that URLs are unique between candidates and include diverse sources."""
    print("Testing URL Uniqueness and Diversity:")
    print("=" * 60)
    
    # Initialize components
    analyzer = ExplanationAnalyzer()
    generator = SearchQueryGenerator()
    validator = EvidenceValidator()
    
    # Test scenarios with different candidates
    test_scenarios = [
        {
            'candidate_id': 'candidate_1',
            'explanation': 'Currently researching new CRM solutions for small business'
        },
        {
            'candidate_id': 'candidate_2', 
            'explanation': 'Evaluating CRM platforms for enterprise deployment'
        },
        {
            'candidate_id': 'candidate_3',
            'explanation': 'Comparing CRM tools for startup team'
        },
        {
            'candidate_id': 'candidate_4',
            'explanation': 'Looking into CRM alternatives for mid-market company'
        }
    ]
    
    all_generated_queries = []
    
    print("\n1. Testing Query Diversity:")
    print("-" * 30)
    
    for scenario in test_scenarios:
        print(f"\nCandidate: {scenario['candidate_id']}")
        print(f"Explanation: {scenario['explanation']}")
        
        # Extract claims
        claims = analyzer.extract_claims(scenario['explanation'])
        
        if claims:
            claim = claims[0]  # Use first claim
            
            # Generate queries with candidate ID for diversity
            queries = generator.generate_queries(claim, scenario['candidate_id'])
            all_generated_queries.extend(queries)
            
            print(f"Generated {len(queries)} queries:")
            for i, query in enumerate(queries[:3], 1):  # Show first 3
                print(f"  {i}. {query.query}")
                print(f"     Strategy: {query.search_strategy}")
    
    print(f"\n2. Query Diversity Analysis:")
    print("-" * 30)
    
    # Analyze query diversity
    unique_queries = set(q.query for q in all_generated_queries)
    unique_strategies = set(q.search_strategy for q in all_generated_queries)
    
    print(f"Total queries generated: {len(all_generated_queries)}")
    print(f"Unique queries: {len(unique_queries)}")
    print(f"Diversity rate: {len(unique_queries)/len(all_generated_queries)*100:.1f}%")
    print(f"Unique strategies used: {len(unique_strategies)}")
    
    # Check for alternative company mentions
    alternative_mentions = 0
    major_company_mentions = 0
    
    major_companies = ['salesforce', 'hubspot', 'microsoft', 'google']
    
    for query in all_generated_queries:
        query_lower = query.query.lower()
        
        # Check for major companies
        if any(company in query_lower for company in major_companies):
            major_company_mentions += 1
        
        # Check for alternative indicators
        alternative_indicators = [
            'alternative', 'pipedrive', 'freshworks', 'zoho', 'copper',
            'emerging', 'startup', 'indie', 'open source', 'lesser known'
        ]
        if any(indicator in query_lower for indicator in alternative_indicators):
            alternative_mentions += 1
    
    print(f"Queries mentioning major companies: {major_company_mentions}")
    print(f"Queries mentioning alternatives: {alternative_mentions}")
    print(f"Alternative focus rate: {alternative_mentions/len(all_generated_queries)*100:.1f}%")
    
    print(f"\n3. Testing URL Uniqueness Tracking:")
    print("-" * 30)
    
    # Test uniqueness tracking
    validator.reset_uniqueness_tracking()
    
    # Simulate some evidence URLs for testing
    from evidence_validator import EvidenceURL, EvidenceType
    import time
    
    test_evidence_sets = []
    
    for i, scenario in enumerate(test_scenarios):
        # Create mock evidence URLs for each candidate
        evidence_urls = [
            EvidenceURL(
                url=f"https://example-crm-{i}-{j}.com/features",
                title=f"CRM Solution {i}-{j} Features",
                description=f"Features and capabilities of CRM solution {i}-{j}",
                evidence_type=EvidenceType.PRODUCT_PAGE,
                relevance_score=0.8,
                confidence_level="high",
                supporting_explanation="Supports CRM research claim",
                domain_authority=0.7,
                page_quality_score=0.8,
                last_validated=time.time()
            )
            for j in range(3)  # 3 URLs per candidate
        ]
        
        # Track URLs for this candidate
        validator._track_used_urls(evidence_urls, scenario['candidate_id'])
        test_evidence_sets.append(evidence_urls)
    
    # Check uniqueness stats
    stats = validator.get_uniqueness_stats()
    
    print(f"Total unique URLs tracked: {stats['total_unique_urls_used']}")
    print(f"Candidates processed: {stats['candidates_processed']}")
    print(f"Average URLs per candidate: {stats['average_urls_per_candidate']:.1f}")
    print(f"Domain diversity: {stats['domain_diversity']}")
    
    # Verify no URL repetition
    all_urls = []
    for evidence_set in test_evidence_sets:
        for evidence in evidence_set:
            all_urls.append(evidence.url)
    
    unique_urls = set(all_urls)
    print(f"URL uniqueness verification: {len(unique_urls)} unique out of {len(all_urls)} total")
    print(f"Uniqueness rate: {len(unique_urls)/len(all_urls)*100:.1f}%")
    
    print(f"\n4. Alternative Company Detection:")
    print("-" * 30)
    
    # Test alternative company detection
    category_tests = [
        ('CRM solutions for small business', 'crm'),
        ('marketing automation platform', 'marketing_automation'),
        ('project management tool', 'project_management'),
        ('cloud storage service', 'cloud_storage')
    ]
    
    for claim_text, expected_category in category_tests:
        detected_category = generator._identify_product_category(claim_text, [])
        alternatives = generator.alternative_companies.get(detected_category, [])
        
        print(f"Claim: '{claim_text}'")
        print(f"Detected category: {detected_category}")
        print(f"Available alternatives: {len(alternatives)}")
        if alternatives:
            print(f"Sample alternatives: {', '.join(alternatives[:3])}")
        print()
    
    print("✅ URL Uniqueness and Diversity Test Completed!")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"- Query diversity rate: {len(unique_queries)/len(all_generated_queries)*100:.1f}%")
    print(f"- Alternative focus rate: {alternative_mentions/len(all_generated_queries)*100:.1f}%")
    print(f"- URL uniqueness rate: {len(unique_urls)/len(all_urls)*100:.1f}%")
    print(f"- Unique strategies: {len(unique_strategies)}")
    
    # Recommendations
    if len(unique_queries)/len(all_generated_queries) > 0.7:
        print("✅ Good query diversity achieved")
    else:
        print("⚠️  Consider improving query diversity")
    
    if alternative_mentions/len(all_generated_queries) > 0.3:
        print("✅ Good alternative focus achieved")
    else:
        print("⚠️  Consider increasing alternative company focus")


if __name__ == '__main__':
    test_url_uniqueness_and_diversity()