#!/usr/bin/env python3
"""
Test suite for the enhanced assessment functionality
"""

import json
import unittest
from unittest.mock import patch, MagicMock
from assess_and_return import (
    select_top_candidates,
    build_assessment_prompt,
    _validate_assessment_response,
    _get_industry_specific_patterns,
    _apply_pattern_replacements,
    _fallback_assessment
)

class TestEnhancedAssessment(unittest.TestCase):
    """Test cases for the enhanced assessment functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.test_people = [
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "organization_name": "Tech Solutions Inc.",
                "email": "jane.smith@example.com",
                "linkedin_url": "https://linkedin.com/in/janesmith"
            },
            {
                "name": "John Doe",
                "title": "Marketing Director",
                "organization_name": "Brand Builders LLC",
                "email": "john.doe@example.com",
                "linkedin_url": "https://linkedin.com/in/johndoe"
            },
            {
                "name": "Alex Johnson",
                "title": "Financial Analyst",
                "organization_name": "Investment Partners",
                "email": "alex.johnson@example.com",
                "linkedin_url": "https://linkedin.com/in/alexjohnson"
            }
        ]
        
        self.valid_response = [
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "email": "jane.smith@example.com",
                "accuracy": 90,
                "reasons": [
                    "Visited GitHub repositories for React state management libraries 5 times in the past week",
                    "Researched cloud architecture optimization techniques across multiple technical blogs, spending 30+ minutes on each",
                    "Compared Kubernetes with Docker Swarm on review sites, then deeply explored Kubernetes documentation"
                ]
            },
            {
                "name": "Alex Johnson",
                "title": "Financial Analyst",
                "company": "Investment Partners",
                "email": "alex.johnson@example.com",
                "accuracy": 75,
                "reasons": [
                    "Analyzed quarterly reports from companies in the SaaS sector over the past month",
                    "Compared financial data visualization tools, then focused on advanced features",
                    "Tracked market indicators related to SaaS over a month-long period"
                ]
            }
        ]
        
        self.invalid_response = [
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "email": "jane.smith@example.com",
                "accuracy": 90,
                "reasons": [
                    "Selected based on title and company fit",
                    "Profile indicates relevant experience"
                ]
            }
        ]

    def test_build_assessment_prompt(self):
        """Test prompt building functionality"""
        user_prompt = "Looking for a senior developer with cloud experience"
        simplified_people = [
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "email": "jane.smith@example.com"
            }
        ]
        
        system_prompt, user_prompt_result = build_assessment_prompt(user_prompt, simplified_people)
        
        # Check that system prompt contains key instructions
        self.assertIn("REALISTIC behavioral reasons", system_prompt)
        self.assertIn("TIME-SERIES patterns", system_prompt)
        self.assertIn("AVOID unrealistic scenarios", system_prompt)
        
        # Check that user prompt contains the search query and candidate data
        self.assertIn("Looking for a senior developer with cloud experience", user_prompt_result)
        self.assertIn("Jane Smith", user_prompt_result)
        self.assertIn("Senior Software Engineer", user_prompt_result)

    @patch('assess_and_return.call_openai')
    def test_select_top_candidates_success(self, mock_call_openai):
        """Test successful API response handling"""
        # Mock successful API response
        mock_call_openai.return_value = json.dumps(self.valid_response)
        
        result = select_top_candidates("Looking for a senior developer", self.test_people)
        
        # Verify the result matches the expected output
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Jane Smith")
        self.assertEqual(result[0]["accuracy"], 90)
        self.assertEqual(len(result[0]["reasons"]), 3)

    @patch('assess_and_return.call_openai')
    def test_select_top_candidates_fallback(self, mock_call_openai):
        """Test fallback when API returns invalid response"""
        # Mock invalid API response
        mock_call_openai.return_value = json.dumps(self.invalid_response)
        
        result = select_top_candidates("Looking for a senior developer", self.test_people)
        
        # Verify fallback was used
        self.assertEqual(len(result), 2)  # Fallback always returns 2 results
        self.assertIn("accuracy", result[0])
        self.assertGreaterEqual(len(result[0]["reasons"]), 3)  # Should have at least 3 reasons

    def test_validate_assessment_response(self):
        """Test response validation logic"""
        # Valid response should pass validation
        result = _validate_assessment_response(self.valid_response, "Looking for a senior developer")
        self.assertEqual(result, self.valid_response)
        
        # Invalid response should fail validation
        result = _validate_assessment_response(self.invalid_response, "Looking for a senior developer")
        self.assertIsNone(result)
        
        # Test with missing required fields
        invalid_missing_fields = [{"name": "Test", "title": "Engineer"}]
        result = _validate_assessment_response(invalid_missing_fields, "Looking for a senior developer")
        self.assertIsNone(result)
        
        # Test with invalid accuracy value
        invalid_accuracy = [
            {
                "name": "Jane Smith",
                "title": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "email": "jane.smith@example.com",
                "accuracy": 150,  # Invalid: > 100
                "reasons": ["Valid reason 1", "Valid reason 2"]
            },
            {
                "name": "John Doe",
                "title": "Developer",
                "company": "Company",
                "email": "email",
                "accuracy": 80,
                "reasons": ["Valid reason 1", "Valid reason 2"]
            }
        ]
        result = _validate_assessment_response(invalid_accuracy, "Looking for a senior developer")
        self.assertIsNone(result)

    def test_get_industry_specific_patterns(self):
        """Test industry detection and pattern generation"""
        # Test tech industry detection
        tech_result = _get_industry_specific_patterns("Senior Software Engineer", "Tech Company")
        self.assertEqual(tech_result["industry"], "tech")
        self.assertEqual(tech_result["role_level"], "senior")
        self.assertGreaterEqual(len(tech_result["patterns"]), 3)
        
        # Test marketing industry detection
        marketing_result = _get_industry_specific_patterns("Marketing Manager", "Brand Agency")
        self.assertEqual(marketing_result["industry"], "marketing")
        self.assertEqual(marketing_result["role_level"], "mid")
        
        # Test finance industry detection
        finance_result = _get_industry_specific_patterns("Financial Analyst", "Investment Bank")
        self.assertEqual(finance_result["industry"], "finance")
        
        # Test executive level detection
        exec_result = _get_industry_specific_patterns("CTO", "Tech Company")
        self.assertEqual(exec_result["role_level"], "executive")

    def test_apply_pattern_replacements(self):
        """Test pattern template replacement"""
        patterns = [
            "Researched {tech_topic} extensively",
            "Used {tech_tool} for {industry_sector} applications"
        ]
        
        replacements = {
            "tech_topic": "machine learning",
            "tech_tool": "TensorFlow",
            "industry_sector": "healthcare"
        }
        
        result = _apply_pattern_replacements(patterns, replacements)
        
        self.assertEqual(result[0], "Researched machine learning extensively")
        self.assertEqual(result[1], "Used TensorFlow for healthcare applications")

    def test_fallback_assessment(self):
        """Test fallback assessment generation"""
        result = _fallback_assessment(self.test_people, "Looking for a cloud engineer")
        
        # Check that we get 2 results
        self.assertEqual(len(result), 2)
        
        # Check that each result has the required fields
        for item in result:
            self.assertIn("name", item)
            self.assertIn("title", item)
            self.assertIn("company", item)
            self.assertIn("email", item)
            self.assertIn("accuracy", item)
            self.assertIn("reasons", item)
            
            # Check that we have at least 3 reasons
            self.assertGreaterEqual(len(item["reasons"]), 3)
            
            # Check that accuracy values are reasonable
            self.assertGreaterEqual(item["accuracy"], 0)
            self.assertLessEqual(item["accuracy"], 100)

if __name__ == "__main__":
    unittest.main()