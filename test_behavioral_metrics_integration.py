"""
Test the integration of behavioral metrics with the API.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from behavioral_metrics import enhance_behavioral_data, generate_behavioral_metrics

class TestBehavioralMetricsIntegration(unittest.TestCase):
    """Test the integration of behavioral metrics with the API."""

    def setUp(self):
        """Set up test data."""
        # Sample behavioral data
        self.behavioral_data = {
            "insights": [
                "High engagement with pricing pages indicates purchase intent",
                "Multiple sessions during evening hours suggest urgency"
            ],
            "data_points": [
                {"type": "page_view", "url": "/pricing", "timestamp": 1626912000},
                {"type": "content_interaction", "content_type": "case_study", "timestamp": 1626998400}
            ],
            "page_views": [
                {"url": "/pricing", "timestamp": 1626912000, "duration": 300},
                {"url": "/features", "timestamp": 1626998400, "duration": 180}
            ],
            "sessions": [
                {"timestamp": 1626912000, "duration": 600, "pages": 5},
                {"timestamp": 1626998400, "duration": 900, "pages": 8}
            ],
            "content_interactions": [
                {"content_type": "case_study", "timestamp": 1626998400},
                {"content_type": "whitepaper", "timestamp": 1627084800}
            ]
        }
        
        # Sample candidate data
        self.candidates = [
            {
                "name": "John Doe",
                "title": "CTO",
                "company": "Tech Corp",
                "email": "john@example.com"
            }
        ]
        
        # Sample user prompt
        self.user_prompt = "Find a CTO in the tech industry"

    def test_enhance_behavioral_data(self):
        """Test that enhance_behavioral_data adds the required metrics."""
        enhanced_data = enhance_behavioral_data(
            self.behavioral_data,
            self.candidates,
            self.user_prompt
        )
        
        # Check that the enhanced data contains the original data
        for key in self.behavioral_data:
            self.assertIn(key, enhanced_data)
        
        # Check that the enhanced data contains the new metrics
        self.assertIn("commitment_momentum_index", enhanced_data)
        self.assertIn("risk_barrier_focus_score", enhanced_data)
        self.assertIn("identity_alignment_signal", enhanced_data)
        self.assertIn("psychometric_modeling_insight", enhanced_data)
        
        # Check the structure of the commitment_momentum_index
        cmi = enhanced_data["commitment_momentum_index"]
        self.assertIn("score", cmi)
        self.assertIn("description", cmi)
        self.assertIn("factors", cmi)
        self.assertIsInstance(cmi["score"], int)
        self.assertIsInstance(cmi["description"], str)
        self.assertIsInstance(cmi["factors"], dict)
        
        # Check the structure of the risk_barrier_focus_score
        rbfs = enhanced_data["risk_barrier_focus_score"]
        self.assertIn("score", rbfs)
        self.assertIn("description", rbfs)
        self.assertIn("factors", rbfs)
        self.assertIsInstance(rbfs["score"], int)
        self.assertIsInstance(rbfs["description"], str)
        self.assertIsInstance(rbfs["factors"], dict)
        
        # Check the structure of the identity_alignment_signal
        ias = enhanced_data["identity_alignment_signal"]
        self.assertIn("score", ias)
        self.assertIn("description", ias)
        self.assertIn("factors", ias)
        self.assertIsInstance(ias["score"], int)
        self.assertIsInstance(ias["description"], str)
        self.assertIsInstance(ias["factors"], dict)
        
        # Check the psychometric_modeling_insight
        self.assertIsInstance(enhanced_data["psychometric_modeling_insight"], str)
    
    def test_enhance_behavioral_data_with_empty_data(self):
        """Test that enhance_behavioral_data handles empty data gracefully."""
        enhanced_data = enhance_behavioral_data(
            {},
            self.candidates,
            self.user_prompt
        )
        
        # For empty data, we should still get a valid result with metrics
        # The generate_behavioral_metrics function should handle empty data
        self.assertIsInstance(enhanced_data, dict)
        # We expect at least some of the metrics to be present
        self.assertTrue(
            "commitment_momentum_index" in enhanced_data or
            "risk_barrier_focus_score" in enhanced_data or
            "identity_alignment_signal" in enhanced_data or
            "psychometric_modeling_insight" in enhanced_data
        )
    
    def test_enhance_behavioral_data_with_none_data(self):
        """Test that enhance_behavioral_data handles None data gracefully."""
        enhanced_data = enhance_behavioral_data(
            None,
            self.candidates,
            self.user_prompt
        )
        
        # Check that the function returns an empty dict when given None
        self.assertEqual(enhanced_data, {})
    
    def test_enhance_behavioral_data_with_invalid_data(self):
        """Test that enhance_behavioral_data handles invalid data gracefully."""
        # Test with a string instead of a dict
        enhanced_data = enhance_behavioral_data(
            "invalid data",
            self.candidates,
            self.user_prompt
        )
        
        # Check that the function returns the original data when given invalid data
        self.assertEqual(enhanced_data, "invalid data")
    
    @patch('behavioral_metrics.generate_behavioral_metrics')
    def test_enhance_behavioral_data_with_exception(self, mock_generate):
        """Test that enhance_behavioral_data handles exceptions gracefully."""
        # Make the generate_behavioral_metrics function raise an exception
        mock_generate.side_effect = Exception("Test exception")
        
        # Call enhance_behavioral_data
        enhanced_data = enhance_behavioral_data(
            self.behavioral_data,
            self.candidates,
            self.user_prompt
        )
        
        # Check that the function returns the original data when an exception occurs
        self.assertEqual(enhanced_data, self.behavioral_data)

if __name__ == '__main__':
    unittest.main()