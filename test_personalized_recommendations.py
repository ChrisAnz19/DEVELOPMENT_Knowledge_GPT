#!/usr/bin/env python3
"""
Test personalized engagement recommendations using candidate's first name
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from behavioral_metrics_ai import (
    extract_first_name, 
    generate_fallback_insight, 
    generate_focused_insight_ai,
    enhance_behavioral_data_ai
)

class TestPersonalizedRecommendations(unittest.TestCase):
    
    def test_extract_first_name_from_full_name(self):
        """Test that first names are correctly extracted from full names"""
        test_cases = [
            ("John Doe", "John"),
            ("Jane Smith", "Jane"),
            ("Robert Johnson Jr.", "Robert"),
            ("Mary-Anne Wilson", "Mary-Anne"),
            ("José García", "José"),
            ("", ""),
            (None, ""),
            ("SingleName", "SingleName"),
            ("  Spaced Name  ", "Spaced")
        ]
        
        for full_name, expected_first_name in test_cases:
            with self.subTest(full_name=full_name):
                result = extract_first_name(full_name)
                self.assertEqual(result, expected_first_name)
    
    def test_fallback_insight_uses_first_name(self):
        """Test that fallback insights use the candidate's first name when available"""
        candidate_data = {
            "name": "John Doe",
            "title": "Senior Director of Commercial Sales",
            "company": "TechCorp Inc"
        }
        
        insight = generate_fallback_insight("Senior Director of Commercial Sales", candidate_data)
        
        # Should use "John" instead of "This professional"
        self.assertIn("John", insight)
        self.assertNotIn("This professional", insight)
        self.assertNotIn("This Senior Director", insight)
    
    def test_fallback_insight_without_name_uses_generic_reference(self):
        """Test that fallback insights use generic reference when no name is available"""
        candidate_data = {
            "title": "Senior Director of Commercial Sales",
            "company": "TechCorp Inc"
            # No name field
        }
        
        insight = generate_fallback_insight("Senior Director of Commercial Sales", candidate_data)
        
        # Should use "This professional" when no name is available
        self.assertIn("This professional", insight)
        self.assertNotIn("John", insight)
    
    def test_fallback_insight_with_empty_name_uses_generic_reference(self):
        """Test that fallback insights use generic reference when name is empty"""
        candidate_data = {
            "name": "",  # Empty name
            "title": "Senior Director of Commercial Sales",
            "company": "TechCorp Inc"
        }
        
        insight = generate_fallback_insight("Senior Director of Commercial Sales", candidate_data)
        
        # Should use "This professional" when name is empty
        self.assertIn("This professional", insight)
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_ai_insight_includes_first_name_in_prompt(self, mock_openai_client):
        """Test that AI insight generation includes first name in the prompt"""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "John is actively researching cybersecurity solutions and shows high commitment momentum. Engage him with detailed technical specifications and competitive analysis to address his specific evaluation criteria."
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        candidate_data = {
            "name": "John Doe",
            "title": "Senior Director of Commercial Sales",
            "company": "TechCorp Inc"
        }
        
        insight = generate_focused_insight_ai(
            "Senior Director of Commercial Sales", 
            "Find sales directors in cybersecurity", 
            candidate_data
        )
        
        # Verify the AI was called
        self.assertTrue(mock_openai_client.chat.completions.create.called)
        
        # Get the actual prompt that was sent to the AI
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]['messages']  # keyword arguments
        user_message = messages[1]['content']  # Second message is the user prompt
        
        # Verify the prompt includes the candidate's first name
        self.assertIn("John", user_message)
        self.assertIn("first name is 'John'", user_message)
        
        # Verify the insight uses the first name
        self.assertIn("John", insight)
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_ai_insight_handles_missing_name(self, mock_openai_client):
        """Test that AI insight generation handles missing candidate name"""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This sales director shows strong commitment momentum and is actively evaluating solutions. Engage with detailed ROI analysis and competitive positioning."
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        candidate_data = {
            "title": "Senior Director of Commercial Sales",
            "company": "TechCorp Inc"
            # No name field
        }
        
        insight = generate_focused_insight_ai(
            "Senior Director of Commercial Sales", 
            "Find sales directors in cybersecurity", 
            candidate_data
        )
        
        # Verify the AI was called
        self.assertTrue(mock_openai_client.chat.completions.create.called)
        
        # Get the actual prompt that was sent to the AI
        call_args = mock_openai_client.chat.completions.create.call_args
        messages = call_args[1]['messages']
        user_message = messages[1]['content']
        
        # Verify the prompt handles missing name appropriately
        self.assertIn("name is not available", user_message)
        
        # The insight should still be returned
        self.assertIsInstance(insight, str)
        self.assertTrue(len(insight) > 0)
    
    @patch('behavioral_metrics_ai.openai_client', None)  # Simulate no OpenAI client
    def test_enhance_behavioral_data_uses_personalized_fallback(self):
        """Test that enhance_behavioral_data_ai uses personalized fallback when OpenAI is unavailable"""
        candidates = [
            {
                "name": "Jane Smith",
                "title": "VP of Sales",
                "company": "Software Inc",
                "linkedin_url": "https://linkedin.com/in/janesmith"
            }
        ]
        
        result = enhance_behavioral_data_ai({}, candidates, "Find VP of Sales in software companies")
        
        # Should have behavioral_insight
        self.assertIn("behavioral_insight", result)
        
        # The insight should use the candidate's first name
        insight = result["behavioral_insight"]
        self.assertIn("Jane", insight)
        self.assertNotIn("This professional", insight)
        self.assertNotIn("This VP", insight)
    
    def test_role_specific_personalization(self):
        """Test that different roles get appropriate personalized insights"""
        test_cases = [
            {
                "candidate": {"name": "Alice Johnson", "title": "Software Engineer"},
                "expected_keywords": ["Alice", "technical challenges", "evidence-based"]
            },
            {
                "candidate": {"name": "Bob Wilson", "title": "CEO"},
                "expected_keywords": ["Bob", "strategic impact", "ROI metrics"]
            },
            {
                "candidate": {"name": "Carol Davis", "title": "Sales Manager"},
                "expected_keywords": ["Carol", "sales targets", "competitive"]
            }
        ]
        
        for case in test_cases:
            with self.subTest(role=case["candidate"]["title"]):
                insight = generate_fallback_insight(case["candidate"]["title"], case["candidate"])
                
                # Check that all expected keywords are present
                for keyword in case["expected_keywords"]:
                    self.assertIn(keyword, insight, f"Missing '{keyword}' in insight for {case['candidate']['title']}")

if __name__ == "__main__":
    unittest.main()