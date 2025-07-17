#!/usr/bin/env python3
"""
Test script to verify if the API response includes the three behavioral scores.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from api.main import SearchResponse
from behavioral_metrics import enhance_behavioral_data

class TestAPIScores(unittest.TestCase):
    """Test cases for the behavioral scores in API response."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_behavioral_data = {
            "insights": ["Sample insight 1", "Sample insight 2"],
            "data_points": ["Point 1", "Point 2"]
        }
        
        self.sample_candidates = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "email": "john.doe@techcorp.com"
            }
        ]
        
        self.user_prompt = "Find a senior software engineer with Python experience"
    
    def test_behavioral_scores_in_enhanced_data(self):
        """Test if enhance_behavioral_data includes the three behavioral scores."""
        # Test the enhance_behavioral_data function
        enhanced_data = enhance_behavioral_data(
            behavioral_data=self.sample_behavioral_data,
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Print the enhanced data for inspection
        print(f"Enhanced behavioral data: {json.dumps(enhanced_data, indent=2)}")
        
        # Check if scores are included
        self.assertIn("behavioral_insight", enhanced_data)
        
        # Check if the scores object exists
        if "scores" in enhanced_data:
            # Check if the three scores are included
            scores = enhanced_data["scores"]
            self.assertIn("cmi", scores, "CMI score is missing")
            self.assertIn("rbfs", scores, "RBFS score is missing")
            self.assertIn("ias", scores, "IAS score is missing")
            
            # Check if each score has a score value and explanation
            for score_key in ["cmi", "rbfs", "ias"]:
                score_obj = scores[score_key]
                self.assertIn("score", score_obj, f"{score_key} is missing score value")
                self.assertIn("explanation", score_obj, f"{score_key} is missing explanation")
        else:
            self.fail("Scores object is missing in the enhanced behavioral data")

if __name__ == "__main__":
    print("Testing API Behavioral Scores...")
    print("=" * 50)
    
    unittest.main(verbosity=2)