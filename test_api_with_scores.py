#!/usr/bin/env python3
"""
Test script to verify that the API returns the correct output structure with behavioral scores.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from api.main import SearchResponse
from behavioral_metrics import enhance_behavioral_data

class TestAPIWithScores(unittest.TestCase):
    """Test cases for the API with behavioral scores."""
    
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
                "linkedin_profile": {"summary": "Experienced software engineer..."}
            }
        ]
        
        self.user_prompt = "Find a senior software engineer with Python experience"
    
    def test_behavioral_data_structure(self):
        """Test that the behavioral data structure matches the API documentation."""
        # Generate behavioral data for a candidate
        behavioral_data = enhance_behavioral_data(
            behavioral_data={},
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Print the behavioral data for inspection
        print(f"Generated behavioral data: {json.dumps(behavioral_data, indent=2)}")
        
        # Verify the structure matches the API documentation
        self.assertIn("behavioral_insight", behavioral_data)
        self.assertIsInstance(behavioral_data["behavioral_insight"], str)
        self.assertGreater(len(behavioral_data["behavioral_insight"]), 0)
        
        # Verify scores are included
        self.assertIn("scores", behavioral_data)
        scores = behavioral_data["scores"]
        
        # Verify the three required scores are present
        self.assertIn("cmi", scores)
        self.assertIn("rbfs", scores)
        self.assertIn("ias", scores)
        
        # Verify each score has the required fields
        for score_key in ["cmi", "rbfs", "ias"]:
            score_obj = scores[score_key]
            self.assertIn("score", score_obj)
            self.assertIn("explanation", score_obj)
            
            # Verify score is a number between 0 and 100
            self.assertIsInstance(score_obj["score"], int)
            self.assertGreaterEqual(score_obj["score"], 0)
            self.assertLessEqual(score_obj["score"], 100)
            
            # Verify explanation is a non-empty string
            self.assertIsInstance(score_obj["explanation"], str)
            self.assertGreater(len(score_obj["explanation"]), 0)
    
    def test_candidate_with_behavioral_data(self):
        """Test that a candidate can have behavioral data with scores."""
        # Create behavioral data for the candidate
        behavioral_data = enhance_behavioral_data(
            behavioral_data={},
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Add behavioral data to the candidate
        candidate = self.sample_candidates[0].copy()
        candidate["behavioral_data"] = behavioral_data
        
        # Create a search response with the candidate
        response_data = {
            "request_id": "test-123",
            "status": "completed",
            "prompt": self.user_prompt,
            "candidates": [candidate],
            "created_at": "2025-07-16T01:23:45Z",
            "completed_at": "2025-07-16T01:23:50Z"
        }
        
        # Create the response object
        response = SearchResponse(**response_data)
        
        # Verify the candidate has behavioral data with scores
        self.assertIsNotNone(response.candidates)
        self.assertEqual(len(response.candidates), 1)
        
        candidate_data = response.candidates[0]
        self.assertIn("behavioral_data", candidate_data)
        
        candidate_behavioral_data = candidate_data["behavioral_data"]
        self.assertIn("behavioral_insight", candidate_behavioral_data)
        self.assertIn("scores", candidate_behavioral_data)
        
        # Verify the scores
        scores = candidate_behavioral_data["scores"]
        for score_key in ["cmi", "rbfs", "ias"]:
            self.assertIn(score_key, scores)
            self.assertIn("score", scores[score_key])
            self.assertIn("explanation", scores[score_key])
    
    def test_api_response_matches_documentation(self):
        """Test that the API response structure matches the documentation."""
        # Create a response based on the example in the API documentation
        example_response_data = {
            "request_id": "36a2dc60-1b9f-406b-ac54-0f18e5ffaaac",
            "status": "completed",
            "prompt": "Find software engineers with 5+ years of experience in Python and React who work at tech companies in San Francisco",
            "filters": {
                "person_filters": {
                    "person_titles": ["Software Engineer"],
                    "include_similar_titles": True,
                    "person_seniorities": ["director", "vp"]
                },
                "organization_filters": {
                    "q_organization_keyword_tags": ["Technology"]
                },
                "reasoning": "Filtered for Software Engineers with director or VP level seniority in Technology companies."
            },
            "candidates": [
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
                    "linkedin_profile": {"summary": "Experienced software engineer..."},
                    "behavioral_data": {
                        "behavioral_insight": "This senior developer responds best to technical depth and practical examples. Start conversations by asking about their current cloud architecture challenges, then demonstrate how your solution addresses specific technical pain points they're experiencing.",
                        "scores": {
                            "cmi": {
                                "score": 85,
                                "explanation": "High communication maturity index indicates preference for direct, technical communication with specific examples."
                            },
                            "rbfs": {
                                "score": 72,
                                "explanation": "Moderate risk-barrier focus score suggests balancing technical details with clear business outcomes."
                            },
                            "ias": {
                                "score": 90,
                                "explanation": "Strong identity alignment signal shows this candidate strongly identifies with their technical expertise and problem-solving abilities."
                            }
                        }
                    }
                }
            ],
            "created_at": "2024-01-15T10:30:00Z",
            "completed_at": "2024-01-15T10:32:15Z"
        }
        
        # Create the response object
        response = SearchResponse(**example_response_data)
        
        # Verify the response structure matches the documentation
        self.assertEqual(response.status, "completed")
        self.assertIsNotNone(response.candidates)
        self.assertEqual(len(response.candidates), 1)
        
        candidate = response.candidates[0]
        self.assertIn("behavioral_data", candidate)
        
        behavioral_data = candidate["behavioral_data"]
        self.assertIn("behavioral_insight", behavioral_data)
        self.assertIn("scores", behavioral_data)
        
        # Verify the scores
        scores = behavioral_data["scores"]
        for score_key in ["cmi", "rbfs", "ias"]:
            self.assertIn(score_key, scores)
            self.assertIn("score", scores[score_key])
            self.assertIn("explanation", scores[score_key])
        
        # Verify specific score values from the example
        self.assertEqual(scores["cmi"]["score"], 85)
        self.assertEqual(scores["rbfs"]["score"], 72)
        self.assertEqual(scores["ias"]["score"], 90)

if __name__ == "__main__":
    print("Testing API with Behavioral Scores...")
    print("=" * 50)
    
    unittest.main(verbosity=2)