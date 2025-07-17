import unittest
from behavioral_metrics import (
    generate_psychometric_modeling_insight,
    analyze_content_preferences,
    analyze_engagement_patterns,
    infer_decision_making_style,
    generate_communication_advice
)

class TestPsychometricModelingInsight(unittest.TestCase):
    
    def setUp(self):
        # Sample candidate data
        self.candidate_data = {
            "name": "John Doe",
            "title": "Senior Software Engineer",
            "company": "Tech Corp"
        }
        
        # Sample behavioral data with technical focus
        self.technical_behavioral_data = {
            "page_views": [
                {"url": "https://example.com/api-docs", "title": "API Documentation", "timestamp": 1626400000},
                {"url": "https://example.com/technical-specs", "title": "Technical Specifications", "timestamp": 1626410000},
                {"url": "https://example.com/integration-guide", "title": "Integration Guide", "timestamp": 1626420000}
            ],
            "sessions": [
                {"timestamp": 1626400000, "duration": 900},  # 15 minutes
                {"timestamp": 1626410000, "duration": 1200},  # 20 minutes
                {"timestamp": 1626420000, "duration": 1500}   # 25 minutes
            ],
            "content_interactions": [
                {"content_type": "api_documentation", "title": "REST API Reference", "timestamp": 1626405000},
                {"content_type": "code_sample", "title": "Integration Code Sample", "timestamp": 1626415000}
            ]
        }
        
        # Sample behavioral data with business focus
        self.business_behavioral_data = {
            "page_views": [
                {"url": "https://example.com/pricing", "title": "Pricing Plans", "timestamp": 1626400000},
                {"url": "https://example.com/case-studies", "title": "Customer Case Studies", "timestamp": 1626410000},
                {"url": "https://example.com/roi-calculator", "title": "ROI Calculator", "timestamp": 1626420000}
            ],
            "sessions": [
                {"timestamp": 1626400000, "duration": 600},  # 10 minutes
                {"timestamp": 1626410000, "duration": 300},  # 5 minutes
                {"timestamp": 1626420000, "duration": 450}   # 7.5 minutes
            ],
            "content_interactions": [
                {"content_type": "case_study", "title": "Enterprise ROI Study", "timestamp": 1626405000},
                {"content_type": "pricing_document", "title": "Enterprise Pricing", "timestamp": 1626415000}
            ]
        }
        
        # Sample behavioral data with minimal information
        self.minimal_behavioral_data = {
            "page_views": [
                {"url": "https://example.com/home", "title": "Home Page", "timestamp": 1626400000}
            ],
            "sessions": [
                {"timestamp": 1626400000, "duration": 60}  # 1 minute
            ],
            "content_interactions": []
        }
        
        # Empty behavioral data
        self.empty_behavioral_data = {}
    
    def test_analyze_content_preferences(self):
        # Test with technical focus
        tech_preferences = analyze_content_preferences(self.technical_behavioral_data)
        self.assertGreater(tech_preferences["technical"], 0.7)
        self.assertLess(tech_preferences["business"], tech_preferences["technical"])
        
        # Test with business focus
        business_preferences = analyze_content_preferences(self.business_behavioral_data)
        self.assertGreater(business_preferences["business"], 0.7)
        self.assertLess(business_preferences["technical"], business_preferences["business"])
        
        # Test with minimal data
        minimal_preferences = analyze_content_preferences(self.minimal_behavioral_data)
        for value in minimal_preferences.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
        
        # Test with empty data
        empty_preferences = analyze_content_preferences(self.empty_behavioral_data)
        for value in empty_preferences.values():
            self.assertEqual(value, 0.5)  # Default value
    
    def test_analyze_engagement_patterns(self):
        # Test with technical focus (longer sessions)
        tech_patterns = analyze_engagement_patterns(self.technical_behavioral_data)
        self.assertGreater(tech_patterns["depth"], 0.6)
        
        # Test with business focus (shorter sessions)
        business_patterns = analyze_engagement_patterns(self.business_behavioral_data)
        self.assertLess(business_patterns["depth"], tech_patterns["depth"])
        
        # Test with minimal data
        minimal_patterns = analyze_engagement_patterns(self.minimal_behavioral_data)
        for value in minimal_patterns.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
        
        # Test with empty data
        empty_patterns = analyze_engagement_patterns(self.empty_behavioral_data)
        for value in empty_patterns.values():
            self.assertEqual(value, 0.5)  # Default value
    
    def test_infer_decision_making_style(self):
        # Test with technical focus
        tech_preferences = analyze_content_preferences(self.technical_behavioral_data)
        tech_patterns = analyze_engagement_patterns(self.technical_behavioral_data)
        tech_style = infer_decision_making_style(
            self.technical_behavioral_data,
            tech_preferences,
            tech_patterns
        )
        self.assertGreater(tech_style["analytical"], 0.6)
        
        # Test with business focus
        business_preferences = analyze_content_preferences(self.business_behavioral_data)
        business_patterns = analyze_engagement_patterns(self.business_behavioral_data)
        business_style = infer_decision_making_style(
            self.business_behavioral_data,
            business_preferences,
            business_patterns
        )
        
        # Test with minimal data
        minimal_preferences = analyze_content_preferences(self.minimal_behavioral_data)
        minimal_patterns = analyze_engagement_patterns(self.minimal_behavioral_data)
        minimal_style = infer_decision_making_style(
            self.minimal_behavioral_data,
            minimal_preferences,
            minimal_patterns
        )
        for value in minimal_style.values():
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
    
    def test_generate_communication_advice(self):
        # Test with technical focus
        tech_preferences = analyze_content_preferences(self.technical_behavioral_data)
        tech_patterns = analyze_engagement_patterns(self.technical_behavioral_data)
        tech_style = infer_decision_making_style(
            self.technical_behavioral_data,
            tech_preferences,
            tech_patterns
        )
        tech_advice = generate_communication_advice(
            self.candidate_data,
            tech_preferences,
            tech_patterns,
            tech_style
        )
        self.assertIsInstance(tech_advice, str)
        self.assertGreater(len(tech_advice), 20)
        self.assertIn("technical", tech_advice.lower())
        
        # Test with business focus
        business_preferences = analyze_content_preferences(self.business_behavioral_data)
        business_patterns = analyze_engagement_patterns(self.business_behavioral_data)
        business_style = infer_decision_making_style(
            self.business_behavioral_data,
            business_preferences,
            business_patterns
        )
        business_advice = generate_communication_advice(
            self.candidate_data,
            business_preferences,
            business_patterns,
            business_style
        )
        self.assertIsInstance(business_advice, str)
        self.assertGreater(len(business_advice), 20)
        self.assertIn("roi", business_advice.lower())
    
    def test_generate_psychometric_modeling_insight(self):
        # Test with technical focus
        tech_insight = generate_psychometric_modeling_insight(
            self.candidate_data,
            self.technical_behavioral_data
        )
        self.assertIsInstance(tech_insight, str)
        self.assertGreater(len(tech_insight), 20)
        
        # Test with business focus
        business_insight = generate_psychometric_modeling_insight(
            self.candidate_data,
            self.business_behavioral_data
        )
        self.assertIsInstance(business_insight, str)
        self.assertGreater(len(business_insight), 20)
        
        # Test with minimal data
        minimal_insight = generate_psychometric_modeling_insight(
            self.candidate_data,
            self.minimal_behavioral_data
        )
        self.assertIsInstance(minimal_insight, str)
        self.assertGreater(len(minimal_insight), 20)
        
        # Test with empty data
        empty_insight = generate_psychometric_modeling_insight(
            self.candidate_data,
            self.empty_behavioral_data
        )
        self.assertIsInstance(empty_insight, str)
        self.assertGreater(len(empty_insight), 20)
        self.assertIn("insufficient", empty_insight.lower())

if __name__ == "__main__":
    unittest.main()