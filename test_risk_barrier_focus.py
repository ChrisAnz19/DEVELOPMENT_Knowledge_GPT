import unittest
from behavioral_metrics import (
    calculate_risk_barrier_focus_score,
    analyze_risk_content_engagement,
    analyze_negative_review_focus,
    analyze_compliance_focus,
    generate_rbfs_description
)
from datetime import datetime, timedelta
import time

class TestRiskBarrierFocusScore(unittest.TestCase):
    
    def test_risk_content_engagement(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_risk_content_engagement(empty_data), 0.0)
        
        # Test with no risk content
        non_risk_data = {
            "page_views": [
                {"url": "https://example.com/blog", "title": "Blog Post"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "blog_post", "title": "Industry Trends"}
            ]
        }
        self.assertAlmostEqual(analyze_risk_content_engagement(non_risk_data), 0.0)
        
        # Test with risk content
        risk_data = {
            "page_views": [
                {"url": "https://example.com/security", "title": "Security Features"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "security_document", "title": "Data Protection"}
            ]
        }
        self.assertGreater(analyze_risk_content_engagement(risk_data), 0.5)
        
        # Test with high-risk content
        high_risk_data = {
            "page_views": [
                {"url": "https://example.com/privacy", "title": "Privacy Policy"},
                {"url": "https://example.com/security/breach", "title": "Breach Prevention"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_risk_content_engagement(high_risk_data), 0.6)
    
    def test_negative_review_focus(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_negative_review_focus(empty_data), 0.0)
        
        # Test with no negative review content
        non_negative_data = {
            "page_views": [
                {"url": "https://example.com/blog", "title": "Blog Post"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "blog_post", "title": "Industry Trends"}
            ]
        }
        self.assertAlmostEqual(analyze_negative_review_focus(non_negative_data), 0.0)
        
        # Test with negative review content
        negative_data = {
            "page_views": [
                {"url": "https://example.com/reviews", "title": "Product Reviews"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "review", "title": "Customer Feedback"}
            ]
        }
        self.assertGreater(analyze_negative_review_focus(negative_data), 0.5)
        
        # Test with highly critical content
        highly_critical_data = {
            "page_views": [
                {"url": "https://example.com/complaints", "title": "Customer Complaints"},
                {"url": "https://example.com/issues", "title": "Known Issues"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_negative_review_focus(highly_critical_data), 0.6)
    
    def test_compliance_focus(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_compliance_focus(empty_data), 0.0)
        
        # Test with no compliance content
        non_compliance_data = {
            "page_views": [
                {"url": "https://example.com/blog", "title": "Blog Post"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "blog_post", "title": "Industry Trends"}
            ]
        }
        self.assertAlmostEqual(analyze_compliance_focus(non_compliance_data), 0.0)
        
        # Test with compliance content
        compliance_data = {
            "page_views": [
                {"url": "https://example.com/compliance", "title": "Compliance Information"},
                {"url": "https://example.com/about", "title": "About Us"}
            ],
            "content_interactions": [
                {"content_type": "compliance_document", "title": "Regulatory Guide"}
            ]
        }
        self.assertGreater(analyze_compliance_focus(compliance_data), 0.5)
        
        # Test with specific compliance standards
        specific_compliance_data = {
            "page_views": [
                {"url": "https://example.com/gdpr", "title": "GDPR Compliance"},
                {"url": "https://example.com/hipaa", "title": "HIPAA Requirements"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_compliance_focus(specific_compliance_data), 0.6)
    
    def test_rbfs_description(self):
        # Test very high score with risk content focus
        description_high_risk = generate_rbfs_description(85, 0.9, 0.5, 0.3)
        self.assertIn("Very High concern", description_high_risk)
        self.assertIn("Security", description_high_risk)
        
        # Test moderate score with negative review focus
        description_moderate_negative = generate_rbfs_description(55, 0.3, 0.8, 0.2)
        self.assertIn("Moderate concern", description_moderate_negative)
        self.assertIn("critical reviews", description_moderate_negative)
        
        # Test low score
        description_low = generate_rbfs_description(15, 0.1, 0.2, 0.1)
        self.assertIn("Very Low concern", description_low)
        self.assertIn("benefits", description_low)
    
    def test_calculate_risk_barrier_focus_score(self):
        # Test with empty data
        empty_result = calculate_risk_barrier_focus_score({}, {})
        self.assertEqual(empty_result["score"], 50)  # Default score
        self.assertIn("factors", empty_result)
        
        # Test with sample data
        sample_data = {
            "page_views": [
                {"url": "https://example.com/security", "title": "Security Features"},
                {"url": "https://example.com/reviews", "title": "Product Reviews"}
            ],
            "content_interactions": [
                {"content_type": "compliance_document", "title": "GDPR Compliance"}
            ]
        }
        
        result = calculate_risk_barrier_focus_score({}, {"page_views": sample_data["page_views"], "content_interactions": sample_data["content_interactions"]})
        self.assertGreater(result["score"], 50)  # Should be above average
        self.assertIn("description", result)
        self.assertEqual(len(result["factors"]), 3)  # Should have 3 factors

if __name__ == "__main__":
    unittest.main()