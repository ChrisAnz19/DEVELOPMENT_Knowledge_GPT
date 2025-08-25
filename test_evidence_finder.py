#!/usr/bin/env python3
"""
Comprehensive Test Suite for URL Evidence Finder.

This module contains unit tests, integration tests, and end-to-end tests
for all components of the URL Evidence Finder system.
"""

import unittest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

# Import components to test
from explanation_analyzer import ExplanationAnalyzer, SearchableClaim, ClaimType
from search_query_generator import SearchQueryGenerator, SearchQuery
from web_search_engine import WebSearchEngine, URLCandidate, SearchResult
from evidence_validator import EvidenceValidator, EvidenceURL, EvidenceType
from evidence_models import (
    SearchableClaimModel, EvidenceURLModel, EnhancedCandidateModel,
    serialize_evidence_urls, validate_candidate_for_evidence_processing,
    extract_explanations_from_candidate
)
from evidence_cache import EvidenceCache, SearchResultCache, PerformanceMonitor
from url_evidence_finder import URLEvidenceFinder
from evidence_integration import EvidenceIntegrationService


class TestExplanationAnalyzer(unittest.TestCase):
    """Test cases for the ExplanationAnalyzer class."""
    
    def setUp(self):
        self.analyzer = ExplanationAnalyzer()
    
    def test_extract_claims_basic(self):
        """Test basic claim extraction."""
        explanation = "Currently researching Salesforce pricing options for enterprise deployment"
        claims = self.analyzer.extract_claims(explanation)
        
        self.assertGreater(len(claims), 0)
        self.assertIsInstance(claims[0], SearchableClaim)
        self.assertEqual(claims[0].text, explanation)
        self.assertEqual(claims[0].claim_type, ClaimType.PRICING_RESEARCH)
    
    def test_extract_claims_multiple_sentences(self):
        """Test claim extraction from multiple sentences."""
        explanation = "Researching CRM solutions. Comparing HubSpot and Salesforce features. Evaluating pricing options."
        claims = self.analyzer.extract_claims(explanation)
        
        self.assertGreater(len(claims), 0)
        # Should extract multiple claims from multiple sentences
        for claim in claims:
            self.assertIsInstance(claim, SearchableClaim)
    
    def test_identify_entities(self):
        """Test entity identification."""
        text = "Researching Salesforce pricing and HubSpot features for CRM evaluation"
        entities = self.analyzer.identify_entities(text)
        
        self.assertIn('companies', entities)
        self.assertIn('salesforce', entities['companies'])
        self.assertIn('hubspot', entities['companies'])
        self.assertIn('products', entities)
        self.assertIn('crm', entities['products'])
    
    def test_categorize_claim_pricing(self):
        """Test claim categorization for pricing research."""
        claim = "Looking at Salesforce pricing plans and costs"
        claim_type = self.analyzer.categorize_claim(claim)
        self.assertEqual(claim_type, ClaimType.PRICING_RESEARCH)
    
    def test_categorize_claim_product_evaluation(self):
        """Test claim categorization for product evaluation."""
        claim = "Evaluating CRM platforms and their features"
        claim_type = self.analyzer.categorize_claim(claim)
        self.assertEqual(claim_type, ClaimType.PRODUCT_EVALUATION)
    
    def test_empty_explanation(self):
        """Test handling of empty explanations."""
        claims = self.analyzer.extract_claims("")
        self.assertEqual(len(claims), 0)
        
        claims = self.analyzer.extract_claims("   ")
        self.assertEqual(len(claims), 0)
    
    def test_short_explanation(self):
        """Test handling of very short explanations."""
        claims = self.analyzer.extract_claims("CRM")
        self.assertEqual(len(claims), 0)  # Too short to be searchable


class TestSearchQueryGenerator(unittest.TestCase):
    """Test cases for the SearchQueryGenerator class."""
    
    def setUp(self):
        self.generator = SearchQueryGenerator()
    
    def test_generate_queries_company_specific(self):
        """Test query generation for company-specific claims."""
        claim = SearchableClaim(
            text="Researching Salesforce pricing options",
            entities={'companies': ['salesforce'], 'pricing_terms': ['pricing']},
            claim_type=ClaimType.PRICING_RESEARCH,
            priority=8,
            search_terms=['salesforce', 'pricing'],
            confidence=0.9
        )
        
        queries = self.generator.generate_queries(claim)
        
        self.assertGreater(len(queries), 0)
        self.assertIsInstance(queries[0], SearchQuery)
        
        # Should have high-priority company-specific queries
        high_priority_queries = [q for q in queries if q.priority >= 9]
        self.assertGreater(len(high_priority_queries), 0)
        
        # Should include site-specific searches
        site_queries = [q for q in queries if 'site:salesforce.com' in q.query]
        self.assertGreater(len(site_queries), 0)
    
    def test_generate_queries_product_evaluation(self):
        """Test query generation for product evaluation claims."""
        claim = SearchableClaim(
            text="Comparing CRM solutions",
            entities={'products': ['crm'], 'activities': ['comparing']},
            claim_type=ClaimType.PRODUCT_EVALUATION,
            priority=7,
            search_terms=['crm', 'comparing'],
            confidence=0.8
        )
        
        queries = self.generator.generate_queries(claim)
        
        self.assertGreater(len(queries), 0)
        
        # Should include comparison-focused queries
        comparison_queries = [q for q in queries if 'comparison' in q.query.lower()]
        self.assertGreater(len(comparison_queries), 0)
    
    def test_query_priority_ordering(self):
        """Test that queries are properly prioritized."""
        claim = SearchableClaim(
            text="Researching Salesforce pricing",
            entities={'companies': ['salesforce'], 'pricing_terms': ['pricing']},
            claim_type=ClaimType.PRICING_RESEARCH,
            priority=10,
            search_terms=['salesforce', 'pricing'],
            confidence=0.9
        )
        
        queries = self.generator.generate_queries(claim)
        
        # Queries should be sorted by priority (highest first)
        for i in range(len(queries) - 1):
            self.assertGreaterEqual(queries[i].priority, queries[i + 1].priority)


class TestWebSearchEngine(unittest.TestCase):
    """Test cases for the WebSearchEngine class."""
    
    def setUp(self):
        # Create mock OpenAI client
        self.mock_client = Mock()
        self.search_engine = WebSearchEngine(self.mock_client)
    
    def test_extract_domain(self):
        """Test domain extraction from URLs."""
        url = "https://www.salesforce.com/products/pricing/"
        domain = self.search_engine._extract_domain(url)
        self.assertEqual(domain, "www.salesforce.com")
    
    def test_detect_page_type_pricing(self):
        """Test page type detection for pricing pages."""
        url = "https://salesforce.com/pricing"
        title = "Salesforce Pricing Plans"
        page_type = self.search_engine._detect_page_type(url, title)
        self.assertEqual(page_type, "pricing")
    
    def test_detect_page_type_product(self):
        """Test page type detection for product pages."""
        url = "https://salesforce.com/products/sales-cloud"
        title = "Sales Cloud Product Features"
        page_type = self.search_engine._detect_page_type(url, title)
        self.assertEqual(page_type, "product")
    
    def test_detect_page_type_documentation(self):
        """Test page type detection for documentation."""
        url = "https://developer.salesforce.com/docs"
        title = "Salesforce Developer Documentation"
        page_type = self.search_engine._detect_page_type(url, title)
        self.assertEqual(page_type, "documentation")
    
    @patch('asyncio.sleep')
    async def test_rate_limiting(self, mock_sleep):
        """Test rate limiting functionality."""
        # Set a very short rate limit for testing
        self.search_engine.rate_limit_delay = 0.1
        
        # Make two rapid requests
        await self.search_engine._enforce_rate_limit()
        await self.search_engine._enforce_rate_limit()
        
        # Should have called sleep for rate limiting
        mock_sleep.assert_called()


class TestEvidenceValidator(unittest.TestCase):
    """Test cases for the EvidenceValidator class."""
    
    def setUp(self):
        self.validator = EvidenceValidator()
    
    def test_validate_url_quality_good_url(self):
        """Test URL quality validation for good URLs."""
        url_candidate = URLCandidate(
            url="https://www.salesforce.com/pricing",
            title="Salesforce Pricing Plans and Packages for Business",  # Longer, more descriptive title
            snippet="Official pricing information for Salesforce products and services",
            domain="www.salesforce.com",  # Include www prefix
            page_type="pricing",
            search_query="salesforce pricing",
            citation_index=0
        )
        
        is_valid = self.validator.validate_url_quality(url_candidate)
        self.assertTrue(is_valid)
    
    def test_validate_url_quality_spam_url(self):
        """Test URL quality validation for spam URLs."""
        url_candidate = URLCandidate(
            url="https://spam-site.com/buy-now",
            title="BUY NOW! LIMITED TIME OFFER! CLICK HERE!",
            snippet="Special discount! Act now! Free trial! Click here!",
            domain="spam-site.com",
            page_type=None,
            search_query="test",
            citation_index=0
        )
        
        is_valid = self.validator.validate_url_quality(url_candidate)
        self.assertFalse(is_valid)
    
    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        url_candidate = URLCandidate(
            url="https://www.salesforce.com/pricing",
            title="Salesforce Pricing Plans and Packages",
            snippet="Compare Salesforce pricing options for your business",
            domain="salesforce.com",
            page_type="pricing",
            search_query="salesforce pricing",
            citation_index=0
        )
        
        claim = SearchableClaim(
            text="Researching Salesforce pricing options",
            entities={'companies': ['salesforce'], 'pricing_terms': ['pricing']},
            claim_type=ClaimType.PRICING_RESEARCH,
            priority=8,
            search_terms=['salesforce', 'pricing'],
            confidence=0.9
        )
        
        score = self.validator.calculate_relevance_score(url_candidate, claim)
        
        self.assertGreater(score, 0.5)  # Should be a good match
        self.assertLessEqual(score, 1.0)  # Should not exceed 1.0
    
    def test_categorize_evidence_pricing_page(self):
        """Test evidence categorization for pricing pages."""
        url_candidate = URLCandidate(
            url="https://salesforce.com/pricing",
            title="Salesforce Pricing",
            snippet="",
            domain="salesforce.com",
            page_type="pricing",
            search_query="",
            citation_index=0
        )
        
        evidence_type = self.validator.categorize_evidence(url_candidate)
        self.assertEqual(evidence_type, EvidenceType.PRICING_PAGE)
    
    def test_categorize_evidence_comparison_site(self):
        """Test evidence categorization for comparison sites."""
        url_candidate = URLCandidate(
            url="https://g2.com/categories/crm",
            title="Best CRM Software",
            snippet="",
            domain="g2.com",
            page_type=None,
            search_query="",
            citation_index=0
        )
        
        evidence_type = self.validator.categorize_evidence(url_candidate)
        self.assertEqual(evidence_type, EvidenceType.COMPARISON_SITE)


class TestEvidenceModels(unittest.TestCase):
    """Test cases for evidence data models."""
    
    def test_searchable_claim_model_validation(self):
        """Test SearchableClaimModel validation."""
        # Valid model
        model = SearchableClaimModel(
            text="Test claim",
            claim_type="pricing_research",  # Use string value instead of enum
            priority=5,
            confidence=0.8
        )
        self.assertEqual(model.text, "Test claim")
        self.assertEqual(model.claim_type, "pricing_research")
    
    def test_evidence_url_model_validation(self):
        """Test EvidenceURLModel validation."""
        # Valid model
        model = EvidenceURLModel(
            url="https://example.com",
            title="Test Title",
            description="Test description for evidence",
            evidence_type="pricing_page",  # Use string value instead of enum
            relevance_score=0.85,
            confidence_level="high",
            supporting_explanation="Test explanation",
            domain_authority=0.9,
            page_quality_score=0.8
        )
        self.assertEqual(str(model.url), "https://example.com")
        self.assertEqual(model.evidence_type, "pricing_page")
    
    def test_serialize_evidence_urls(self):
        """Test evidence URL serialization."""
        # Create evidence URL using the dataclass from evidence_validator
        from evidence_validator import EvidenceURL as ValidatorEvidenceURL, EvidenceType as ValidatorEvidenceType
        
        evidence_url = ValidatorEvidenceURL(
            url="https://example.com",
            title="Test Title",
            description="Test description for evidence",
            evidence_type=ValidatorEvidenceType.PRICING_PAGE,
            relevance_score=0.85,
            confidence_level="high",
            supporting_explanation="Test explanation",
            domain_authority=0.9,
            page_quality_score=0.8,
            last_validated=time.time()
        )
        
        serialized = serialize_evidence_urls([evidence_url])
        
        self.assertEqual(len(serialized), 1)
        self.assertIsInstance(serialized[0], dict)
        self.assertEqual(serialized[0]['url'], "https://example.com")
        self.assertEqual(serialized[0]['evidence_type'], "pricing_page")
    
    def test_validate_candidate_for_evidence_processing(self):
        """Test candidate validation for evidence processing."""
        # Valid candidate
        valid_candidate = {
            'id': '123',
            'name': 'John Doe',
            'reasons': ['Researching CRM solutions']
        }
        self.assertTrue(validate_candidate_for_evidence_processing(valid_candidate))
        
        # Invalid candidate (missing required fields)
        invalid_candidate = {
            'name': 'John Doe'
        }
        self.assertFalse(validate_candidate_for_evidence_processing(invalid_candidate))
    
    def test_extract_explanations_from_candidate(self):
        """Test explanation extraction from candidate objects."""
        candidate = {
            'id': '123',
            'name': 'John Doe',
            'reasons': ['Researching CRM solutions', 'Evaluating pricing options'],
            'behavioral_data': {
                'explanation': 'Shows interest in technology evaluation'
            },
            'accuracy_explanation': 'High confidence match'
        }
        
        explanations = extract_explanations_from_candidate(candidate)
        
        self.assertGreater(len(explanations), 0)
        self.assertIn('Researching CRM solutions', explanations)
        self.assertIn('Evaluating pricing options', explanations)
        self.assertIn('Shows interest in technology evaluation', explanations)
        self.assertIn('High confidence match', explanations)


class TestEvidenceCache(unittest.TestCase):
    """Test cases for evidence caching functionality."""
    
    def setUp(self):
        self.cache = EvidenceCache(max_size=5, default_ttl=1)  # Small cache with short TTL for testing
    
    def test_cache_put_and_get(self):
        """Test basic cache put and get operations."""
        self.cache.put("key1", "value1")
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")
    
    def test_cache_miss(self):
        """Test cache miss behavior."""
        result = self.cache.get("nonexistent_key")
        self.assertIsNone(result)
    
    def test_cache_ttl_expiration(self):
        """Test TTL expiration."""
        self.cache.put("key1", "value1", ttl=0.1)  # Very short TTL
        
        # Should be available immediately
        result = self.cache.get("key1")
        self.assertEqual(result, "value1")
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired now
        result = self.cache.get("key1")
        self.assertIsNone(result)
    
    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        for i in range(5):
            self.cache.put(f"key{i}", f"value{i}")
        
        # Add one more item (should evict oldest)
        self.cache.put("key5", "value5")
        
        # First item should be evicted
        result = self.cache.get("key0")
        self.assertIsNone(result)
        
        # Last item should still be there
        result = self.cache.get("key5")
        self.assertEqual(result, "value5")
    
    def test_cache_stats(self):
        """Test cache statistics tracking."""
        # Generate some hits and misses
        self.cache.put("key1", "value1")
        self.cache.get("key1")  # Hit
        self.cache.get("key2")  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['total_requests'], 2)
        self.assertGreater(stats['hit_rate'], 0)


class TestPerformanceMonitor(unittest.TestCase):
    """Test cases for performance monitoring."""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
    
    def test_record_operation_time(self):
        """Test operation time recording."""
        self.monitor.record_operation_time("test_op", 1.5)
        self.monitor.record_operation_time("test_op", 2.0)
        
        stats = self.monitor.get_operation_stats("test_op")
        
        self.assertEqual(stats['count'], 2)
        self.assertEqual(stats['avg_time'], 1.75)
        self.assertEqual(stats['min_time'], 1.5)
        self.assertEqual(stats['max_time'], 2.0)
    
    def test_record_error(self):
        """Test error recording."""
        self.monitor.record_error("test_op", "ValueError")
        self.monitor.record_error("test_op", "ValueError")
        self.monitor.record_error("test_op", "TypeError")
        
        stats = self.monitor.get_all_stats()
        
        self.assertEqual(stats['errors']['test_op:ValueError'], 2)
        self.assertEqual(stats['errors']['test_op:TypeError'], 1)
    
    def test_record_api_usage(self):
        """Test API usage recording."""
        self.monitor.record_api_usage(requests=3, tokens=150)
        self.monitor.record_api_usage(requests=2, tokens=100)
        
        stats = self.monitor.get_all_stats()
        
        self.assertEqual(stats['api_usage']['requests_made'], 5)
        self.assertEqual(stats['api_usage']['tokens_used'], 250)


class TestURLEvidenceFinder(unittest.TestCase):
    """Test cases for the main URLEvidenceFinder class."""
    
    def setUp(self):
        # Create mock OpenAI client
        self.mock_client = Mock()
        self.evidence_finder = URLEvidenceFinder(self.mock_client)
    
    def test_initialization(self):
        """Test proper initialization of components."""
        self.assertIsNotNone(self.evidence_finder.explanation_analyzer)
        self.assertIsNotNone(self.evidence_finder.query_generator)
        self.assertIsNotNone(self.evidence_finder.web_search_engine)
        self.assertIsNotNone(self.evidence_finder.evidence_validator)
    
    def test_configuration_defaults(self):
        """Test default configuration values."""
        self.assertEqual(self.evidence_finder.max_claims_per_candidate, 5)
        self.assertEqual(self.evidence_finder.max_queries_per_claim, 3)
        self.assertEqual(self.evidence_finder.max_evidence_urls_per_candidate, 5)
    
    @patch('url_evidence_finder.URLEvidenceFinder.web_search_engine')
    async def test_find_evidence_no_explanations(self, mock_search_engine):
        """Test evidence finding with no explanations."""
        result = await self.evidence_finder.find_evidence([])
        self.assertEqual(len(result), 0)
    
    @patch('url_evidence_finder.URLEvidenceFinder.web_search_engine')
    async def test_find_evidence_with_explanations(self, mock_search_engine):
        """Test evidence finding with valid explanations."""
        # Mock search results
        mock_search_engine.search_for_evidence = AsyncMock(return_value=[])
        
        explanations = ["Researching Salesforce pricing options"]
        result = await self.evidence_finder.find_evidence(explanations)
        
        # Should complete without error (even with empty search results)
        self.assertIsInstance(result, list)


class TestEvidenceIntegration(unittest.TestCase):
    """Test cases for evidence integration with the API."""
    
    def setUp(self):
        # Create mock OpenAI client
        self.mock_client = Mock()
        self.integration_service = EvidenceIntegrationService(self.mock_client)
    
    def test_filter_eligible_candidates(self):
        """Test filtering of eligible candidates."""
        candidates = [
            {
                'id': '1',
                'name': 'John Doe',
                'reasons': ['Researching CRM solutions with detailed analysis']
            },
            {
                'id': '2',
                'name': 'Jane Smith',
                'reasons': ['Short']  # Too short
            },
            {
                'id': '3',
                'name': 'Bob Johnson'
                # No reasons
            }
        ]
        
        eligible = self.integration_service._filter_eligible_candidates(candidates)
        
        self.assertEqual(len(eligible), 1)
        self.assertEqual(eligible[0]['id'], '1')
    
    def test_merge_enhanced_candidates(self):
        """Test merging of enhanced candidates with original list."""
        original_candidates = [
            {'id': '1', 'name': 'John Doe'},
            {'id': '2', 'name': 'Jane Smith'},
            {'id': '3', 'name': 'Bob Johnson'}
        ]
        
        enhanced_candidates = [
            {
                'id': '1',
                'name': 'John Doe',
                'evidence_urls': [{'url': 'https://example.com'}]
            },
            {
                'id': '3',
                'name': 'Bob Johnson',
                'evidence_urls': []
            }
        ]
        
        merged = self.integration_service._merge_enhanced_candidates(
            original_candidates, enhanced_candidates
        )
        
        self.assertEqual(len(merged), 3)
        self.assertEqual(len(merged[0].get('evidence_urls', [])), 1)  # John has evidence
        self.assertNotIn('evidence_urls', merged[1])  # Jane unchanged
        self.assertEqual(len(merged[2].get('evidence_urls', [])), 0)  # Bob has empty evidence


class TestEndToEndIntegration(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        # Create mock components for end-to-end testing
        self.mock_client = Mock()
    
    async def test_complete_evidence_pipeline(self):
        """Test the complete evidence gathering pipeline."""
        # Test data
        test_candidate = {
            'id': '1',
            'name': 'John Doe',
            'title': 'VP of Sales',
            'company': 'TechCorp',
            'reasons': [
                'Currently researching Salesforce pricing options for enterprise deployment',
                'Actively comparing CRM solutions including HubSpot and Microsoft Dynamics'
            ],
            'behavioral_data': {
                'behavioral_insight': 'Shows strong interest in CRM technology evaluation',
                'scores': {'cmi': 0.85, 'rbfs': 0.78, 'ias': 0.82}
            }
        }
        
        # Test explanation analysis
        analyzer = ExplanationAnalyzer()
        claims = []
        for reason in test_candidate['reasons']:
            extracted_claims = analyzer.extract_claims(reason)
            claims.extend(extracted_claims)
        
        self.assertGreater(len(claims), 0)
        
        # Test query generation
        generator = SearchQueryGenerator()
        all_queries = []
        for claim in claims:
            queries = generator.generate_queries(claim)
            all_queries.extend(queries)
        
        self.assertGreater(len(all_queries), 0)
        
        # Test evidence validation (with mock data)
        validator = EvidenceValidator()
        
        # Create mock URL candidate
        mock_url_candidate = URLCandidate(
            url="https://www.salesforce.com/pricing",
            title="Salesforce Pricing Plans",
            snippet="Official pricing information",
            domain="salesforce.com",
            page_type="pricing",
            search_query="salesforce pricing",
            citation_index=0
        )
        
        # Create mock search result
        mock_search_result = SearchResult(
            query=all_queries[0],
            urls=[mock_url_candidate],
            citations=[],
            search_metadata={},
            success=True,
            error_message=None
        )
        
        # Test validation
        evidence_urls = validator.validate_and_rank([mock_search_result], claims[0])
        
        self.assertGreater(len(evidence_urls), 0)
        self.assertIsInstance(evidence_urls[0], EvidenceURL)
    
    def test_model_serialization_roundtrip(self):
        """Test that models can be serialized and deserialized correctly."""
        # Create evidence URL using the dataclass from evidence_validator
        from evidence_validator import EvidenceURL as ValidatorEvidenceURL, EvidenceType as ValidatorEvidenceType
        
        evidence_url = ValidatorEvidenceURL(
            url="https://example.com",
            title="Test Title",
            description="Test description for evidence URL",
            evidence_type=ValidatorEvidenceType.PRICING_PAGE,
            relevance_score=0.85,
            confidence_level="high",
            supporting_explanation="Test explanation",
            domain_authority=0.9,
            page_quality_score=0.8,
            last_validated=time.time()
        )
        
        # Serialize
        serialized = serialize_evidence_urls([evidence_url])
        
        # Check serialization
        self.assertEqual(len(serialized), 1)
        self.assertEqual(serialized[0]['url'], "https://example.com")
        self.assertEqual(serialized[0]['evidence_type'], "pricing_page")
        
        # Test JSON serialization
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)
        
        self.assertEqual(deserialized[0]['url'], "https://example.com")


def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    
    def run_async(self, coro):
        """Run an async coroutine in a test."""
        return run_async_test(coro)


class TestAsyncComponents(AsyncTestCase):
    """Test cases for async components."""
    
    def test_async_evidence_finding(self):
        """Test async evidence finding functionality."""
        async def test_coro():
            # Create mock evidence finder
            mock_client = Mock()
            evidence_finder = URLEvidenceFinder(mock_client)
            
            # Mock the web search to avoid actual API calls
            evidence_finder.web_search_engine.search_for_evidence = AsyncMock(return_value=[])
            
            # Test with empty explanations
            result = await evidence_finder.find_evidence([])
            self.assertEqual(len(result), 0)
            
            # Test with explanations
            explanations = ["Researching CRM solutions"]
            result = await evidence_finder.find_evidence(explanations)
            self.assertIsInstance(result, list)
        
        self.run_async(test_coro())


def create_test_suite():
    """Create a comprehensive test suite."""
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestExplanationAnalyzer,
        TestSearchQueryGenerator,
        TestWebSearchEngine,
        TestEvidenceValidator,
        TestEvidenceModels,
        TestEvidenceCache,
        TestPerformanceMonitor,
        TestURLEvidenceFinder,
        TestEvidenceIntegration,
        TestEndToEndIntegration,
        TestAsyncComponents
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def run_tests():
    """Run all tests and display results."""
    print("Running URL Evidence Finder Test Suite")
    print("=" * 60)
    
    # Create and run test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)