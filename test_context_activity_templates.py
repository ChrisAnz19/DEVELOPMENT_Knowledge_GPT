"""
Unit tests for context-specific behavioral activity templates.
Tests that appropriate activities are available for different search contexts.
"""

import unittest
from assess_and_return import context_specific_activities

class TestContextActivityTemplates(unittest.TestCase):
    
    def test_real_estate_activities_exist(self):
        """Test that real estate activity templates are properly defined."""
        self.assertIn("real_estate", context_specific_activities)
        
        real_estate_activities = context_specific_activities["real_estate"]
        
        # Check that all required activity types exist
        required_types = ["research_activities", "evaluation_activities", "comparison_activities"]
        for activity_type in required_types:
            with self.subTest(activity_type=activity_type):
                self.assertIn(activity_type, real_estate_activities)
                self.assertIsInstance(real_estate_activities[activity_type], list)
                self.assertGreater(len(real_estate_activities[activity_type]), 5)
    
    def test_real_estate_activities_content(self):
        """Test that real estate activities contain appropriate content."""
        real_estate_activities = context_specific_activities["real_estate"]
        
        # Check research activities contain property-related terms
        research_activities = real_estate_activities["research_activities"]
        property_terms = ["property", "neighborhood", "mortgage", "school", "zillow", "realtor"]
        
        found_terms = []
        for activity in research_activities:
            activity_lower = activity.lower()
            for term in property_terms:
                if term in activity_lower:
                    found_terms.append(term)
        
        # Should find multiple property-related terms
        self.assertGreater(len(set(found_terms)), 3, 
                          f"Real estate activities should contain property-related terms, found: {set(found_terms)}")
    
    def test_legal_services_activities_exist(self):
        """Test that legal services activity templates are properly defined."""
        self.assertIn("legal_services", context_specific_activities)
        
        legal_activities = context_specific_activities["legal_services"]
        
        # Check that all required activity types exist
        required_types = ["research_activities", "evaluation_activities", "comparison_activities"]
        for activity_type in required_types:
            with self.subTest(activity_type=activity_type):
                self.assertIn(activity_type, legal_activities)
                self.assertIsInstance(legal_activities[activity_type], list)
                self.assertGreater(len(legal_activities[activity_type]), 5)
    
    def test_legal_services_activities_content(self):
        """Test that legal services activities contain appropriate content."""
        legal_activities = context_specific_activities["legal_services"]
        
        # Check research activities contain legal-related terms
        research_activities = legal_activities["research_activities"]
        legal_terms = ["attorney", "lawyer", "legal", "case", "bar", "court"]
        
        found_terms = []
        for activity in research_activities:
            activity_lower = activity.lower()
            for term in legal_terms:
                if term in activity_lower:
                    found_terms.append(term)
        
        # Should find multiple legal-related terms
        self.assertGreater(len(set(found_terms)), 3,
                          f"Legal activities should contain legal-related terms, found: {set(found_terms)}")
    
    def test_personal_purchase_activities_exist(self):
        """Test that personal purchase activity templates are properly defined."""
        self.assertIn("personal_purchase", context_specific_activities)
        
        personal_activities = context_specific_activities["personal_purchase"]
        
        # Check that all required activity types exist
        required_types = ["research_activities", "evaluation_activities", "comparison_activities"]
        for activity_type in required_types:
            with self.subTest(activity_type=activity_type):
                self.assertIn(activity_type, personal_activities)
                self.assertIsInstance(personal_activities[activity_type], list)
                self.assertGreater(len(personal_activities[activity_type]), 5)
    
    def test_personal_purchase_activities_content(self):
        """Test that personal purchase activities contain appropriate content."""
        personal_activities = context_specific_activities["personal_purchase"]
        
        # Check research activities contain consumer-related terms
        research_activities = personal_activities["research_activities"]
        consumer_terms = ["product", "reviews", "warranty", "pricing", "customer", "amazon"]
        
        found_terms = []
        for activity in research_activities:
            activity_lower = activity.lower()
            for term in consumer_terms:
                if term in activity_lower:
                    found_terms.append(term)
        
        # Should find multiple consumer-related terms
        self.assertGreater(len(set(found_terms)), 3,
                          f"Personal purchase activities should contain consumer-related terms, found: {set(found_terms)}")
    
    def test_financial_decision_activities_exist(self):
        """Test that financial decision activity templates are properly defined."""
        self.assertIn("financial_decision", context_specific_activities)
        
        financial_activities = context_specific_activities["financial_decision"]
        
        # Check that all required activity types exist
        required_types = ["research_activities", "evaluation_activities", "comparison_activities"]
        for activity_type in required_types:
            with self.subTest(activity_type=activity_type):
                self.assertIn(activity_type, financial_activities)
                self.assertIsInstance(financial_activities[activity_type], list)
                self.assertGreater(len(financial_activities[activity_type]), 5)
    
    def test_financial_decision_activities_content(self):
        """Test that financial decision activities contain appropriate content."""
        financial_activities = context_specific_activities["financial_decision"]
        
        # Check research activities contain finance-related terms
        research_activities = financial_activities["research_activities"]
        finance_terms = ["investment", "financial", "advisor", "portfolio", "returns", "market"]
        
        found_terms = []
        for activity in research_activities:
            activity_lower = activity.lower()
            for term in finance_terms:
                if term in activity_lower:
                    found_terms.append(term)
        
        # Should find multiple finance-related terms
        self.assertGreater(len(set(found_terms)), 3,
                          f"Financial activities should contain finance-related terms, found: {set(found_terms)}")
    
    def test_no_forbidden_patterns(self):
        """Test that context-specific activities don't contain forbidden patterns."""
        forbidden_patterns = [
            "downloaded whitepaper", "attended webinar", "viewed webinar", 
            "subscribed to newsletter", "downloaded case study"
        ]
        
        for context_name, context_activities in context_specific_activities.items():
            for activity_type, activities in context_activities.items():
                for activity in activities:
                    activity_lower = activity.lower()
                    for pattern in forbidden_patterns:
                        with self.subTest(context=context_name, activity_type=activity_type, activity=activity):
                            self.assertNotIn(pattern, activity_lower,
                                           f"Activity contains forbidden pattern '{pattern}': {activity}")
    
    def test_activities_have_time_references(self):
        """Test that activities include time-series patterns and realistic website references."""
        for context_name, context_activities in context_specific_activities.items():
            for activity_type, activities in context_activities.items():
                # Check that activities contain realistic website references
                website_count = 0
                for activity in activities:
                    if ".com" in activity or ".org" in activity or ".gov" in activity:
                        website_count += 1
                
                with self.subTest(context=context_name, activity_type=activity_type):
                    # Most activities should reference real websites (at least 50%)
                    self.assertGreaterEqual(website_count, len(activities) * 0.5,
                                          f"Activities should reference real websites for credibility")
    
    def test_activity_diversity(self):
        """Test that activities within each context are diverse and non-repetitive."""
        for context_name, context_activities in context_specific_activities.items():
            for activity_type, activities in context_activities.items():
                # Check that activities don't start with the same words too often
                starting_words = [activity.split()[0].lower() for activity in activities]
                unique_starting_words = set(starting_words)
                
                with self.subTest(context=context_name, activity_type=activity_type):
                    # Should have reasonable diversity in starting words (at least 50%)
                    diversity_ratio = len(unique_starting_words) / len(starting_words)
                    self.assertGreaterEqual(diversity_ratio, 0.5,
                                          f"Activities should be diverse, diversity ratio: {diversity_ratio}")

if __name__ == "__main__":
    unittest.main()