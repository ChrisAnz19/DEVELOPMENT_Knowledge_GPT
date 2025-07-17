#!/usr/bin/env python3
"""
Test script to verify the AI-based behavioral metrics generation.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from behavioral_metrics_ai import (
    generate_focused_insight_ai,
    generate_cmi_score_ai,
    generate_rbfs_score_ai,
    generate_ias_score_ai,
    enhance_behavioral_data_ai
)

class TestBehavioralMetricsAI(unittest.TestCase):
    """Test cases for the AI-based behavioral metrics generation."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_candidates = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "email": "john.doe@techcorp.com",
                "accuracy": 92,
                "reasons": ["5+ years experience", "Python and React skills", "San Francisco location"],
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "profile_photo_url": "https://example.com/photo.jpg",
                "location": "San Francisco, CA",
                "linkedin_profile": {
                    "summary": "Experienced software engineer with expertise in cloud architecture, distributed systems, and machine learning infrastructure. Passionate about solving complex technical challenges and building scalable solutions.",
                    "experience": [
                        {
                            "title": "Senior Software Engineer",
                            "company": "Tech Corp",
                            "duration": "3 years",
                            "description": "Leading backend development for cloud-based analytics platform."
                        },
                        {
                            "title": "Software Engineer",
                            "company": "StartupX",
                            "duration": "2 years",
                            "description": "Developed microservices architecture for e-commerce platform."
                        }
                    ],
                    "education": [
                        {
                            "degree": "M.S. Computer Science",
                            "school": "Stanford University",
                            "year": "2018"
                        }
                    ],
                    "skills": ["Python", "React", "AWS", "Kubernetes", "Machine Learning"]
                }
            }
        ]
        
        self.user_prompt = "Find a senior software engineer with cloud experience"
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_generate_focused_insight_ai(self, mock_openai):
        """Test that the AI-based focused insight generator works correctly."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing."
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Generate a focused insight
        role = "Senior Software Engineer"
        user_prompt = self.user_prompt
        candidate_data = self.sample_candidates[0]
        
        insight = generate_focused_insight_ai(role, user_prompt, candidate_data)
        
        # Verify the insight is a non-empty string
        self.assertIsInstance(insight, str)
        self.assertGreater(len(insight), 0)
        
        # Verify OpenAI was called with appropriate parameters
        mock_openai.chat.completions.create.assert_called_once()
        call_args = mock_openai.chat.completions.create.call_args[1]
        self.assertIn("messages", call_args)
        self.assertGreaterEqual(len(call_args["messages"]), 1)
        
        print(f"Generated insight: {insight}")
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_generate_cmi_score_ai(self, mock_openai):
        """Test that the AI-based CMI score generator works correctly."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "score": 85,
            "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
        })
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Generate a CMI score
        role = "Senior Software Engineer"
        candidate_data = self.sample_candidates[0]
        
        cmi_score = generate_cmi_score_ai(role, candidate_data)
        
        # Verify the score structure
        self.assertIn("score", cmi_score)
        self.assertIn("explanation", cmi_score)
        
        # Verify the score is a number between 0 and 100
        self.assertIsInstance(cmi_score["score"], int)
        self.assertGreaterEqual(cmi_score["score"], 0)
        self.assertLessEqual(cmi_score["score"], 100)
        
        # Verify the explanation is a non-empty string
        self.assertIsInstance(cmi_score["explanation"], str)
        self.assertGreater(len(cmi_score["explanation"]), 0)
        
        print(f"Generated CMI score: {cmi_score}")
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_generate_rbfs_score_ai(self, mock_openai):
        """Test that the AI-based RBFS score generator works correctly."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "score": 72,
            "explanation": "Moderate risk-barrier focus score suggests balancing opportunity messaging with appropriate risk mitigation."
        })
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Generate a RBFS score
        role = "Senior Software Engineer"
        candidate_data = self.sample_candidates[0]
        
        rbfs_score = generate_rbfs_score_ai(role, candidate_data)
        
        # Verify the score structure
        self.assertIn("score", rbfs_score)
        self.assertIn("explanation", rbfs_score)
        
        # Verify the score is a number between 0 and 100
        self.assertIsInstance(rbfs_score["score"], int)
        self.assertGreaterEqual(rbfs_score["score"], 0)
        self.assertLessEqual(rbfs_score["score"], 100)
        
        # Verify the explanation is a non-empty string
        self.assertIsInstance(rbfs_score["explanation"], str)
        self.assertGreater(len(rbfs_score["explanation"]), 0)
        
        print(f"Generated RBFS score: {rbfs_score}")
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_generate_ias_score_ai(self, mock_openai):
        """Test that the AI-based IAS score generator works correctly."""
        # Mock the OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps({
            "score": 90,
            "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
        })
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Generate an IAS score
        role = "Senior Software Engineer"
        candidate_data = self.sample_candidates[0]
        
        ias_score = generate_ias_score_ai(role, candidate_data)
        
        # Verify the score structure
        self.assertIn("score", ias_score)
        self.assertIn("explanation", ias_score)
        
        # Verify the score is a number between 0 and 100
        self.assertIsInstance(ias_score["score"], int)
        self.assertGreaterEqual(ias_score["score"], 0)
        self.assertLessEqual(ias_score["score"], 100)
        
        # Verify the explanation is a non-empty string
        self.assertIsInstance(ias_score["explanation"], str)
        self.assertGreater(len(ias_score["explanation"]), 0)
        
        print(f"Generated IAS score: {ias_score}")
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_enhance_behavioral_data_ai(self, mock_openai):
        """Test that the AI-based behavioral data enhancement works correctly."""
        # Mock the OpenAI responses for each function
        mock_insight_response = MagicMock()
        mock_insight_response.choices[0].message.content = "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing."
        
        mock_cmi_response = MagicMock()
        mock_cmi_response.choices[0].message.content = json.dumps({
            "score": 85,
            "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
        })
        
        mock_rbfs_response = MagicMock()
        mock_rbfs_response.choices[0].message.content = json.dumps({
            "score": 72,
            "explanation": "Moderate risk-barrier focus score suggests balancing opportunity messaging with appropriate risk mitigation."
        })
        
        mock_ias_response = MagicMock()
        mock_ias_response.choices[0].message.content = json.dumps({
            "score": 90,
            "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
        })
        
        # Set up the mock to return different responses for different calls
        mock_openai.chat.completions.create.side_effect = [
            mock_insight_response,
            mock_cmi_response,
            mock_rbfs_response,
            mock_ias_response
        ]
        
        # Enhance behavioral data
        enhanced_data = enhance_behavioral_data_ai(
            behavioral_data={},
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Verify the enhanced data structure
        self.assertIn("behavioral_insight", enhanced_data)
        self.assertIn("scores", enhanced_data)
        
        # Verify the scores
        scores = enhanced_data["scores"]
        self.assertIn("cmi", scores)
        self.assertIn("rbfs", scores)
        self.assertIn("ias", scores)
        
        # Verify each score has the required fields
        for score_key in ["cmi", "rbfs", "ias"]:
            score_obj = scores[score_key]
            self.assertIn("score", score_obj)
            self.assertIn("explanation", score_obj)
        
        print(f"Enhanced behavioral data: {json.dumps(enhanced_data, indent=2)}")
    
    @patch('behavioral_metrics_ai.openai_client')
    def test_error_handling(self, mock_openai):
        """Test that errors are handled gracefully."""
        # Mock the OpenAI client to raise an exception
        mock_openai.chat.completions.create.side_effect = Exception("API error")
        
        # Enhance behavioral data with error
        enhanced_data = enhance_behavioral_data_ai(
            behavioral_data={},
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Verify that default values are returned
        self.assertIn("behavioral_insight", enhanced_data)
        self.assertIn("scores", enhanced_data)
        
        # Verify the scores
        scores = enhanced_data["scores"]
        self.assertIn("cmi", scores)
        self.assertIn("rbfs", scores)
        self.assertIn("ias", scores)
        
        print(f"Enhanced data with error handling: {json.dumps(enhanced_data, indent=2)}")

if __name__ == "__main__":
    print("Testing AI-Based Behavioral Metrics...")
    print("=" * 50)
    
    unittest.main(verbosity=2)