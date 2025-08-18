#!/usr/bin/env python3
"""
Test for contextual behavioral metrics (CMI, RBFS, IAS) descriptions.

This test verifies that behavioral metrics show context-appropriate descriptions
instead of generic vendor/business language for all search types.
"""

import unittest
from behavioral_metrics_ai import generate_top_lead_scores, analyze_search_context


class TestBehavioralMetricsContext(unittest.TestCase):
    
    def setUp(self):
        """Set up mock scores structure for testing."""
        self.mock_scores = {
            'cmi': {'score': 85, 'explanation': 'old explanation'},
            'rbfs': {'score': 40, 'explanation': 'old explanation'},
            'ias': {'score': 90, 'explanation': 'old explanation'}
        }
    
    def test_real_estate_context_metrics(self):
        """Test that real estate searches generate real estate-specific behavioral metrics."""
        query = 'executive looking to buy home in Greenwich, Connecticut'
        result = generate_top_lead_scores(self.mock_scores, 0, query)
        
        # CMI should reference real estate activities, not vendor solutions
        cmi_explanation = result['cmi']['explanation'].lower()
        self.assertIn('property', cmi_explanation, "CMI should reference property-related activities")
        self.assertNotIn('vendor', cmi_explanation, "CMI should not reference vendor solutions for real estate")
        self.assertNotIn('demo', cmi_explanation, "CMI should not reference demos for real estate")
        
        # RBFS should reference real estate decision-making
        rbfs_explanation = result['rbfs']['explanation'].lower()
        self.assertTrue(
            any(term in rbfs_explanation for term in ['property', 'neighborhood', 'real estate', 'market']),
            "RBFS should reference real estate decision-making"
        )
        
        # IAS should reference personal investment in property search
        ias_explanation = result['ias']['explanation'].lower()
        self.assertTrue(
            any(term in ias_explanation for term in ['property', 'real estate', 'neighborhood']),
            "IAS should reference personal investment in property search"
        )
    
    def test_legal_services_context_metrics(self):
        """Test that legal services searches generate legal-specific behavioral metrics."""
        query = 'attorney specializing in corporate law'
        result = generate_top_lead_scores(self.mock_scores, 0, query)
        
        # CMI should reference legal activities
        cmi_explanation = result['cmi']['explanation'].lower()
        self.assertTrue(
            any(term in cmi_explanation for term in ['attorney', 'legal', 'law', 'case']),
            "CMI should reference legal activities"
        )
        self.assertNotIn('vendor', cmi_explanation, "CMI should not reference vendor solutions for legal services")
        
        # RBFS should reference legal decision-making
        rbfs_explanation = result['rbfs']['explanation'].lower()
        self.assertTrue(
            any(term in rbfs_explanation for term in ['legal', 'case', 'attorney', 'law']),
            "RBFS should reference legal decision-making"
        )
        
        # IAS should reference legal case preparation
        ias_explanation = result['ias']['explanation'].lower()
        self.assertTrue(
            any(term in ias_explanation for term in ['legal', 'case', 'attorney', 'law']),
            "IAS should reference legal case preparation"
        )
    
    def test_personal_purchase_context_metrics(self):
        """Test that personal purchase searches generate purchase-specific behavioral metrics."""
        query = 'looking to buy a new car'
        result = generate_top_lead_scores(self.mock_scores, 0, query)
        
        # CMI should reference product research activities
        cmi_explanation = result['cmi']['explanation'].lower()
        self.assertTrue(
            any(term in cmi_explanation for term in ['product', 'features', 'pricing', 'quality', 'reviews']),
            "CMI should reference product research activities"
        )
        self.assertNotIn('vendor', cmi_explanation, "CMI should not reference vendor solutions for personal purchases")
        
        # RBFS should reference purchase decision-making
        rbfs_explanation = result['rbfs']['explanation'].lower()
        self.assertTrue(
            any(term in rbfs_explanation for term in ['brand', 'product', 'purchase', 'quality', 'value']),
            "RBFS should reference purchase decision-making"
        )
        
        # IAS should reference personal investment in product choice
        ias_explanation = result['ias']['explanation'].lower()
        self.assertTrue(
            any(term in ias_explanation for term in ['product', 'choice', 'research', 'comparison']),
            "IAS should reference personal investment in product choice"
        )
    
    def test_financial_decision_context_metrics(self):
        """Test that financial decision searches generate finance-specific behavioral metrics."""
        query = 'investment advisor for portfolio management'
        result = generate_top_lead_scores(self.mock_scores, 0, query)
        
        # CMI should reference investment activities
        cmi_explanation = result['cmi']['explanation'].lower()
        self.assertTrue(
            any(term in cmi_explanation for term in ['investment', 'portfolio', 'financial', 'advisor', 'market']),
            "CMI should reference investment activities"
        )
        self.assertNotIn('vendor', cmi_explanation, "CMI should not reference vendor solutions for financial decisions")
        
        # RBFS should reference investment decision-making
        rbfs_explanation = result['rbfs']['explanation'].lower()
        self.assertTrue(
            any(term in rbfs_explanation for term in ['investment', 'portfolio', 'financial', 'market', 'risk']),
            "RBFS should reference investment decision-making"
        )
        
        # IAS should reference financial planning commitment
        ias_explanation = result['ias']['explanation'].lower()
        self.assertTrue(
            any(term in ias_explanation for term in ['financial', 'investment', 'portfolio', 'planning']),
            "IAS should reference financial planning commitment"
        )
    
    def test_business_solution_context_metrics(self):
        """Test that business solution searches still generate vendor-specific behavioral metrics."""
        query = 'looking for CRM solutions'
        result = generate_top_lead_scores(self.mock_scores, 0, query)
        
        # CMI should reference vendor activities for business solutions
        cmi_explanation = result['cmi']['explanation'].lower()
        self.assertTrue(
            any(term in cmi_explanation for term in ['vendor', 'solution', 'demo', 'implementation', 'integration']),
            "CMI should reference vendor activities for business solutions"
        )
        
        # RBFS should reference business decision-making
        rbfs_explanation = result['rbfs']['explanation'].lower()
        self.assertTrue(
            any(term in rbfs_explanation for term in ['approach', 'solution', 'advantage', 'innovation']),
            "RBFS should reference business decision-making"
        )
        
        # IAS should reference business research commitment
        ias_explanation = result['ias']['explanation'].lower()
        self.assertTrue(
            any(term in ias_explanation for term in ['research', 'evaluation', 'activity', 'commitment']),
            "IAS should reference business research commitment"
        )
    
    def test_context_diversity_across_candidates(self):
        """Test that different candidates get different explanations within the same context."""
        query = 'executive looking to buy home in Greenwich, Connecticut'
        
        result_0 = generate_top_lead_scores(self.mock_scores, 0, query)
        result_1 = generate_top_lead_scores(self.mock_scores, 1, query)
        result_2 = generate_top_lead_scores(self.mock_scores, 2, query)
        
        # Explanations should be different across candidates
        self.assertNotEqual(result_0['cmi']['explanation'], result_1['cmi']['explanation'])
        self.assertNotEqual(result_1['cmi']['explanation'], result_2['cmi']['explanation'])
        self.assertNotEqual(result_0['cmi']['explanation'], result_2['cmi']['explanation'])
        
        # But all should be real estate related
        for result in [result_0, result_1, result_2]:
            cmi_explanation = result['cmi']['explanation'].lower()
            self.assertNotIn('vendor', cmi_explanation, "All real estate CMI should avoid vendor language")


if __name__ == '__main__':
    unittest.main()