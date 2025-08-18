"""
Unit tests for enhanced search context analysis functionality.
Tests various search query patterns to ensure correct context categorization.
"""

import unittest
from behavioral_metrics_ai import analyze_search_context

class TestSearchContextAnalysis(unittest.TestCase):
    
    def test_real_estate_context_detection(self):
        """Test that real estate queries are correctly identified."""
        # Primary real estate queries
        queries = [
            "Find me an executive looking to buy a home in Greenwich, Connecticut",
            "Looking for executives who are buying house in Manhattan",
            "Find CEOs interested in residential property in Westchester",
            "Executives looking for commercial real estate in NYC"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "real_estate")
                self.assertGreater(result["confidence_score"], 0.5)
                self.assertTrue(result["is_personal"])
                self.assertIn("real_estate_research", result["activity_templates"])
                self.assertEqual(result["behavioral_focus"], "personal")
    
    def test_legal_services_context_detection(self):
        """Test that legal service queries are correctly identified."""
        queries = [
            "Find attorneys specializing in corporate law",
            "Looking for lawyers with family law experience",
            "Find legal counsel for intellectual property matters",
            "Executives who need estate planning attorney"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "legal_services")
                self.assertGreater(result["confidence_score"], 0.5)
                self.assertTrue(result["is_specialized"])
                self.assertIn("attorney_research", result["activity_templates"])
    
    def test_business_solution_context_detection(self):
        """Test that B2B technology queries are correctly identified."""
        queries = [
            "Find CTOs evaluating CRM solutions",
            "Looking for executives interested in marketing automation",
            "Find IT directors considering cloud migration",
            "Executives evaluating enterprise software solutions"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "business_solution")
                self.assertTrue(result["is_business"])
                self.assertIn("solution_evaluation", result["activity_templates"])
                self.assertEqual(result["behavioral_focus"], "professional")
    
    def test_personal_purchase_context_detection(self):
        """Test that personal purchase queries are correctly identified."""
        queries = [
            "Find executives looking to buy a new car",
            "Looking for professionals interested in personal insurance",
            "Find managers considering mortgage options",
            "Executives shopping for personal laptops"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "personal_purchase")
                self.assertTrue(result["is_personal"])
                self.assertIn("product_research", result["activity_templates"])
                self.assertEqual(result["behavioral_focus"], "personal")
    
    def test_financial_decision_context_detection(self):
        """Test that financial/investment queries are correctly identified."""
        queries = [
            "Find executives interested in investment opportunities",
            "Looking for portfolio managers evaluating ESG funds",
            "Find wealth managers considering sustainable investments",
            "Executives seeking financial advisors"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "financial_decision")
                self.assertTrue(result["is_specialized"])
                self.assertIn("investment_research", result["activity_templates"])
                self.assertEqual(result["behavioral_focus"], "mixed")
    
    def test_mixed_context_queries(self):
        """Test queries that might have multiple context indicators."""
        # Real estate + business context
        result = analyze_search_context("Find executives looking for office space and CRM software")
        # Should prioritize based on weights and primary indicators
        self.assertIn(result["context_type"], ["real_estate", "business_solution"])
        self.assertGreater(result["confidence_score"], 0.3)
    
    def test_ambiguous_context_fallback(self):
        """Test that ambiguous queries fall back to general_business."""
        queries = [
            "Find executives in New York",
            "Looking for professionals",
            "Find managers with experience"
        ]
        
        for query in queries:
            with self.subTest(query=query):
                result = analyze_search_context(query)
                self.assertEqual(result["context_type"], "general_business")
                self.assertLessEqual(result["confidence_score"], 0.5)
                self.assertTrue(result["is_business"])
    
    def test_confidence_scoring(self):
        """Test that confidence scores are appropriate for different query types."""
        # High confidence query (specific real estate)
        high_conf_result = analyze_search_context("Find executives looking to buy home in Greenwich Connecticut")
        self.assertGreater(high_conf_result["confidence_score"], 0.6)
        
        # Medium confidence query (some indicators)
        med_conf_result = analyze_search_context("Find executives interested in property")
        self.assertGreater(med_conf_result["confidence_score"], 0.3)
        self.assertLess(med_conf_result["confidence_score"], 0.8)
        
        # Low confidence query (generic)
        low_conf_result = analyze_search_context("Find executives")
        self.assertLessEqual(low_conf_result["confidence_score"], 0.5)
    
    def test_decision_factors_mapping(self):
        """Test that appropriate decision factors are returned for each context."""
        # Real estate should have location, budget, etc.
        real_estate_result = analyze_search_context("Find executives buying homes")
        self.assertIn("location_preference", real_estate_result["decision_factors"])
        self.assertIn("budget_considerations", real_estate_result["decision_factors"])
        
        # Business solution should have ROI, integration, etc.
        business_result = analyze_search_context("Find CTOs evaluating CRM")
        self.assertIn("roi_value", business_result["decision_factors"])
        self.assertIn("integration_compatibility", business_result["decision_factors"])
    
    def test_activity_templates_mapping(self):
        """Test that appropriate activity templates are returned for each context."""
        # Real estate should have property research templates
        real_estate_result = analyze_search_context("Find executives buying property")
        expected_templates = ["real_estate_research", "location_analysis", "market_comparison", "financial_planning"]
        self.assertEqual(real_estate_result["activity_templates"], expected_templates)
        
        # Legal services should have attorney research templates
        legal_result = analyze_search_context("Find executives needing attorneys")
        expected_templates = ["attorney_research", "case_evaluation", "consultation_scheduling", "legal_comparison"]
        self.assertEqual(legal_result["activity_templates"], expected_templates)
    
    def test_behavioral_focus_determination(self):
        """Test that behavioral focus is correctly determined."""
        # Personal contexts
        personal_result = analyze_search_context("Find executives buying homes")
        self.assertEqual(personal_result["behavioral_focus"], "personal")
        
        # Professional contexts
        professional_result = analyze_search_context("Find CTOs evaluating software")
        self.assertEqual(professional_result["behavioral_focus"], "professional")
        
        # Mixed contexts
        mixed_result = analyze_search_context("Find executives seeking financial advisors")
        self.assertEqual(mixed_result["behavioral_focus"], "mixed")

if __name__ == "__main__":
    unittest.main()