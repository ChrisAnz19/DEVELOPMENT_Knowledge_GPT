#!/usr/bin/env python3
"""
Verification test for Task 3: Implement contextual activity selection logic

This test verifies that all requirements from task 3 are implemented:
- Modify _generate_realistic_behavioral_reasons() function to use context-aware selection
- Add select_contextual_activities() function that matches activities to search context and candidate role  
- Implement role-context relevance scoring to ensure logical connections
- Add fallback logic for unknown contexts to use generic professional activities
"""

import unittest
from assess_and_return import (
    _generate_realistic_behavioral_reasons,
    select_contextual_activities, 
    _calculate_role_context_relevance,
    context_specific_activities
)
from behavioral_metrics_ai import analyze_search_context


class TestTask3Implementation(unittest.TestCase):
    
    def test_context_aware_selection(self):
        """Test that _generate_realistic_behavioral_reasons uses context-aware selection."""
        # Real estate context should generate real estate activities
        reasons = _generate_realistic_behavioral_reasons('CEO', 'executive looking to buy home in Greenwich', 0)
        self.assertTrue(any('neighborhood' in reason or 'property' in reason or 'real estate' in reason.lower() 
                           for reason in reasons), 
                       "Real estate search should generate real estate activities")
        
        # CRM context should generate business solution activities  
        reasons = _generate_realistic_behavioral_reasons('CTO', 'looking for CRM solutions', 0)
        self.assertTrue(any('pricing' in reason or 'vendor' in reason or 'solution' in reason.lower()
                           for reason in reasons),
                       "CRM search should generate business solution activities")
        
        # Legal context should generate legal activities
        reasons = _generate_realistic_behavioral_reasons('Attorney', 'attorney specializing in corporate law', 0)
        self.assertTrue(any('attorney' in reason or 'legal' in reason or 'law' in reason.lower()
                           for reason in reasons),
                       "Legal search should generate legal activities")

    def test_select_contextual_activities_function_exists(self):
        """Test that select_contextual_activities function exists and works."""
        context = analyze_search_context('executive looking to buy home')
        activities = select_contextual_activities(context, 'CEO', 0)
        
        self.assertIsInstance(activities, list)
        self.assertGreater(len(activities), 0)
        self.assertTrue(all(isinstance(activity, str) for activity in activities))

    def test_role_context_relevance_scoring(self):
        """Test that role-context relevance scoring ensures logical connections."""
        # Real estate agent should have high relevance for real estate
        relevance = _calculate_role_context_relevance('Real Estate Agent', 'real_estate')
        self.assertGreaterEqual(relevance, 0.8, "Real estate agent should have high relevance for real estate")
        
        # Attorney should have high relevance for legal services
        relevance = _calculate_role_context_relevance('Attorney', 'legal_services')
        self.assertGreaterEqual(relevance, 0.8, "Attorney should have high relevance for legal services")
        
        # CEO should have high relevance for personal purchases
        relevance = _calculate_role_context_relevance('CEO', 'personal_purchase')
        self.assertGreaterEqual(relevance, 0.8, "CEO should have high relevance for personal purchases")
        
        # Software engineer should have lower relevance for real estate
        relevance = _calculate_role_context_relevance('Software Engineer', 'real_estate')
        self.assertLessEqual(relevance, 0.6, "Software engineer should have lower relevance for real estate")

    def test_fallback_logic_for_unknown_contexts(self):
        """Test that fallback logic works for unknown contexts."""
        # Unknown context should fall back to generic professional activities
        reasons = _generate_realistic_behavioral_reasons('Manager', 'looking for purple unicorns', 0)
        
        self.assertIsInstance(reasons, list)
        self.assertGreater(len(reasons), 0)
        
        # Should contain generic business activities, not context-specific ones
        combined_reasons = ' '.join(reasons).lower()
        self.assertFalse(any(term in combined_reasons for term in ['neighborhood', 'property', 'attorney', 'legal']),
                        "Unknown context should not generate context-specific activities")

    def test_activity_diversity_across_candidates(self):
        """Test that different candidates get different activities for same context."""
        context_query = 'executive looking to buy home in Greenwich'
        
        reasons_0 = _generate_realistic_behavioral_reasons('CEO', context_query, 0)
        reasons_1 = _generate_realistic_behavioral_reasons('CEO', context_query, 1) 
        reasons_2 = _generate_realistic_behavioral_reasons('CEO', context_query, 2)
        
        # First activities should be different across candidates
        self.assertNotEqual(reasons_0[0], reasons_1[0])
        self.assertNotEqual(reasons_1[0], reasons_2[0])
        self.assertNotEqual(reasons_0[0], reasons_2[0])

    def test_context_specific_activities_exist(self):
        """Test that context-specific activity templates exist."""
        required_contexts = ['real_estate', 'legal_services', 'personal_purchase', 'financial_decision', 'business_solution']
        
        for context in required_contexts:
            self.assertIn(context, context_specific_activities, 
                         f"Context-specific activities should exist for {context}")
            
            context_data = context_specific_activities[context]
            self.assertIn('research_activities', context_data)
            self.assertIn('evaluation_activities', context_data)
            self.assertIn('comparison_activities', context_data)

    def test_logical_connections_between_role_and_context(self):
        """Test that behavioral data shows logical connections between role and search context."""
        test_cases = [
            ('Real Estate Agent', 'executive looking to buy home', 'real_estate'),
            ('Attorney', 'attorney specializing in corporate law', 'legal_services'),
            ('CTO', 'looking for CRM solutions', 'business_solution'),
            ('CEO', 'looking to buy a new car', 'personal_purchase')
        ]
        
        for role, query, expected_context in test_cases:
            context = analyze_search_context(query)
            self.assertEqual(context['context_type'], expected_context)
            
            relevance = _calculate_role_context_relevance(role, expected_context)
            reasons = _generate_realistic_behavioral_reasons(role, query, 0)
            
            # High relevance roles should get contextually appropriate activities
            if relevance >= 0.7:
                combined_reasons = ' '.join(reasons).lower()
                if expected_context == 'real_estate':
                    self.assertTrue(any(term in combined_reasons for term in ['property', 'neighborhood', 'real estate', 'home']),
                                   f"High relevance {role} should get real estate activities")
                elif expected_context == 'legal_services':
                    self.assertTrue(any(term in combined_reasons for term in ['attorney', 'legal', 'law', 'bar']),
                                   f"High relevance {role} should get legal activities")


if __name__ == '__main__':
    unittest.main()