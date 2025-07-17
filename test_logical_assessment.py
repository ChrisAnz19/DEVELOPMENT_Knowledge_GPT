#!/usr/bin/env python3
"""
Unit tests for the logical_assessment module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from logical_assessment import assess_logical_coherence

class TestLogicalAssessment(unittest.TestCase):
    """Test cases for the logical_assessment module."""

    def setUp(self):
        """Set up test fixtures."""
        self.user_query = "Find me senior software engineers at Google with experience in AI"
        self.apollo_results = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "location": "Mountain View, CA",
                "seniority": "Director"
            },
            {
                "name": "Jane Smith",
                "title": "Marketing Manager",
                "organization_name": "Facebook",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "location": "San Francisco, CA",
                "seniority": "Manager"
            },
            {
                "name": "Bob Johnson",
                "title": "Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/bobjohnson",
                "location": "Seattle, WA",
                "seniority": "Senior"
            }
        ]

    @patch('logical_assessment.call_openai')
    def test_assess_logical_coherence_success(self, mock_call_openai):
        """Test successful assessment with coherent results."""
        # Mock the OpenAI API response
        mock_response = json.dumps({
            "overall_coherent": True,
            "coherent_results": [0, 2],  # John Doe and Bob Johnson are coherent
            "explanation": "John Doe and Bob Johnson are software engineers at Google, matching the query."
        })
        mock_call_openai.return_value = mock_response
        
        # Call the function
        is_coherent, coherent_results, explanation = assess_logical_coherence(
            self.user_query, self.apollo_results
        )
        
        # Assertions
        self.assertTrue(is_coherent)
        self.assertEqual(len(coherent_results), 2)
        self.assertEqual(coherent_results[0]["name"], "John Doe")
        self.assertEqual(coherent_results[1]["name"], "Bob Johnson")
        self.assertIn("John Doe", explanation)
        self.assertIn("Bob Johnson", explanation)

    @patch('logical_assessment.call_openai')
    def test_assess_logical_coherence_no_coherent_results(self, mock_call_openai):
        """Test assessment with no coherent results."""
        # Mock the OpenAI API response
        mock_response = json.dumps({
            "overall_coherent": False,
            "coherent_results": [],
            "explanation": "None of the results match the query for senior software engineers at Google with AI experience."
        })
        mock_call_openai.return_value = mock_response
        
        # Call the function
        is_coherent, coherent_results, explanation = assess_logical_coherence(
            self.user_query, self.apollo_results
        )
        
        # Assertions
        self.assertFalse(is_coherent)
        self.assertEqual(coherent_results, self.apollo_results)  # Should return all results as fallback
        self.assertIn("fallback", explanation.lower())

    @patch('logical_assessment.call_openai')
    def test_assess_logical_coherence_api_failure(self, mock_call_openai):
        """Test handling of API failure."""
        # Mock the OpenAI API failure
        mock_call_openai.return_value = None
        
        # Call the function
        is_coherent, coherent_results, explanation = assess_logical_coherence(
            self.user_query, self.apollo_results
        )
        
        # Assertions
        self.assertTrue(is_coherent)  # Default to True on failure
        self.assertEqual(coherent_results, self.apollo_results)  # Should return all results
        self.assertIn("failed", explanation.lower())

    def test_assess_logical_coherence_empty_results(self):
        """Test handling of empty results."""
        # Call the function with empty results
        is_coherent, coherent_results, explanation = assess_logical_coherence(
            self.user_query, []
        )
        
        # Assertions
        self.assertTrue(is_coherent)  # Default to True for empty results
        self.assertEqual(coherent_results, [])  # Should return empty list
        self.assertIn("no results", explanation.lower())

    @patch('logical_assessment.call_openai')
    def test_assess_logical_coherence_json_parse_error(self, mock_call_openai):
        """Test handling of JSON parse error."""
        # Mock an invalid JSON response
        mock_call_openai.return_value = "This is not valid JSON"
        
        # Call the function
        is_coherent, coherent_results, explanation = assess_logical_coherence(
            self.user_query, self.apollo_results
        )
        
        # Assertions
        self.assertTrue(is_coherent)  # Default to True on parse error
        self.assertEqual(coherent_results, self.apollo_results)  # Should return all results
        self.assertIn("failed to parse", explanation.lower())

if __name__ == '__main__':
    unittest.main()