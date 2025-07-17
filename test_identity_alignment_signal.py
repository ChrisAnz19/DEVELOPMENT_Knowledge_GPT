import unittest
from behavioral_metrics import (
    calculate_identity_alignment_signal,
    analyze_purpose_driven_engagement,
    analyze_thought_leadership_focus,
    analyze_community_engagement,
    generate_ias_description
)
from datetime import datetime, timedelta
import time

class TestIdentityAlignmentSignal(unittest.TestCase):
    
    def test_purpose_driven_engagement(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_purpose_driven_engagement(empty_data), 0.0)
        
        # Test with no purpose-driven content
        non_purpose_data = {
            "page_views": [
                {"url": "https://example.com/blog", "title": "Blog Post"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "blog_post", "title": "Industry Trends"}
            ]
        }
        self.assertAlmostEqual(analyze_purpose_driven_engagement(non_purpose_data), 0.0)
        
        # Test with purpose-driven content
        purpose_data = {
            "page_views": [
                {"url": "https://example.com/about-us", "title": "About Our Company"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "mission_statement", "title": "Our Mission and Values"}
            ]
        }
        self.assertGreater(analyze_purpose_driven_engagement(purpose_data), 0.5)
        
        # Test with high-value purpose content
        high_value_data = {
            "page_views": [
                {"url": "https://example.com/mission", "title": "Our Mission Statement"},
                {"url": "https://example.com/sustainability", "title": "Sustainability Initiatives"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_purpose_driven_engagement(high_value_data), 0.6)
    
    def test_thought_leadership_focus(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_thought_leadership_focus(empty_data), 0.0)
        
        # Test with no thought leadership content
        non_thought_leadership_data = {
            "page_views": [
                {"url": "https://example.com/contact", "title": "Contact Us"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "product_brochure", "title": "Product Features"}
            ]
        }
        self.assertAlmostEqual(analyze_thought_leadership_focus(non_thought_leadership_data), 0.0)
        
        # Test with thought leadership content
        thought_leadership_data = {
            "page_views": [
                {"url": "https://example.com/blog", "title": "Industry Blog"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "whitepaper", "title": "Future Trends in Technology"}
            ]
        }
        self.assertGreater(analyze_thought_leadership_focus(thought_leadership_data), 0.5)
        
        # Test with high-value thought leadership content
        high_value_data = {
            "page_views": [
                {"url": "https://example.com/research", "title": "Research Reports"},
                {"url": "https://example.com/whitepaper", "title": "Industry Analysis"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_thought_leadership_focus(high_value_data), 0.6)
    
    def test_community_engagement(self):
        # Test with empty data
        empty_data = {}
        self.assertEqual(analyze_community_engagement(empty_data), 0.0)
        
        # Test with no community content
        non_community_data = {
            "page_views": [
                {"url": "https://example.com/contact", "title": "Contact Us"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "product_brochure", "title": "Product Features"}
            ]
        }
        self.assertAlmostEqual(analyze_community_engagement(non_community_data), 0.0)
        
        # Test with community content
        community_data = {
            "page_views": [
                {"url": "https://example.com/forum", "title": "User Forum"},
                {"url": "https://example.com/products", "title": "Our Products"}
            ],
            "content_interactions": [
                {"content_type": "forum_post", "title": "Discussion Thread"}
            ]
        }
        self.assertGreater(analyze_community_engagement(community_data), 0.5)
        
        # Test with high-value community content
        high_value_data = {
            "page_views": [
                {"url": "https://example.com/community", "title": "Community Portal"},
                {"url": "https://example.com/events", "title": "User Group Meetups"}
            ],
            "content_interactions": []
        }
        self.assertGreater(analyze_community_engagement(high_value_data), 0.6)
    
    def test_ias_description(self):
        # Test very high score with purpose-driven focus
        description_high_purpose = generate_ias_description(85, 0.9, 0.5, 0.3)
        self.assertIn("Very Strong", description_high_purpose)
        self.assertIn("Values-driven", description_high_purpose)
        
        # Test moderate score with thought leadership focus
        description_moderate_thought = generate_ias_description(55, 0.3, 0.8, 0.2)
        self.assertIn("Moderate", description_moderate_thought)
        self.assertIn("industry expertise", description_moderate_thought)
        
        # Test low score
        description_low = generate_ias_description(15, 0.1, 0.2, 0.1)
        self.assertIn("Very Weak", description_low)
        self.assertIn("Limited", description_low)
    
    def test_calculate_identity_alignment_signal(self):
        # Test with empty data
        empty_result = calculate_identity_alignment_signal({}, {})
        self.assertEqual(empty_result["score"], 50)  # Default score
        self.assertIn("factors", empty_result)
        
        # Test with sample data
        sample_data = {
            "page_views": [
                {"url": "https://example.com/about-us", "title": "About Our Company"},
                {"url": "https://example.com/blog", "title": "Industry Blog"}
            ],
            "content_interactions": [
                {"content_type": "mission_statement", "title": "Our Mission and Values"}
            ]
        }
        
        result = calculate_identity_alignment_signal({}, {"page_views": sample_data["page_views"], "content_interactions": sample_data["content_interactions"]})
        self.assertGreater(result["score"], 50)  # Should be above average
        self.assertIn("description", result)
        self.assertEqual(len(result["factors"]), 3)  # Should have 3 factors

if __name__ == "__main__":
    unittest.main()