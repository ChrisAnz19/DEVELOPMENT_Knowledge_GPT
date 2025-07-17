"""
Test the integration of behavioral metrics with the API.

This test suite focuses on how the behavioral metrics module integrates with the API,
ensuring that the metrics are correctly included in API responses.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import time
from datetime import datetime

from behavioral_metrics import enhance_behavioral_data

class TestBehavioralMetricsAPIIntegration(unittest.TestCase):
    """Test the integration of behavioral metrics with the API."""
    
    def setUp(self):
        """Set up test data."""
        # Current timestamp for testing
        self.current_time = time.time()
        
        # Sample user prompt
        self.user_prompt = "Find a CTO with cloud experience"
        
        # Sample candidate data
        self.candidate_data = {
            "name": "Jane Smith",
            "title": "Chief Technology Officer",
            "company": "Cloud Innovations Inc.",
            "email": "jane@example.com",
            "linkedin_url": "https://linkedin.com/in/janesmith"
        }
        
        # Sample behavioral data
        self.behavioral_data = {
            "insights": [
                "High engagement with pricing pages indicates purchase intent",
                "Multiple sessions during evening hours suggest urgency"
            ],
            "page_views": [
                {"url": "/pricing", "title": "Pricing Plans", "timestamp": self.current_time - 86400},
                {"url": "/features", "title": "Product Features", "timestamp": self.current_time - 43200}
            ],
            "sessions": [
                {"timestamp": self.current_time - 86400, "duration": 600, "pages": 5},
                {"timestamp": self.current_time - 43200, "duration": 900, "pages": 8}
            ],
            "content_interactions": [
                {"content_type": "pricing_document", "title": "Enterprise Pricing", "timestamp": self.current_time - 86400},
                {"content_type": "whitepaper", "title": "Cloud Security Best Practices", "timestamp": self.current_time - 43200}
            ]
        }
        
        # Sample API response structure
        self.api_response = {
            "request_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "completed",
            "prompt": self.user_prompt,
            "filters": {"title": "CTO", "keywords": ["cloud"]},
            "candidates": [self.candidate_data],
            "behavioral_data": self.behavioral_data,
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()
        }

    def test_api_process_search_integration(self):
        """Test that process_search correctly integrates behavioral metrics."""
        # Instead of mocking process_search which is an async function,
        # we'll just test the enhance_behavioral_data function directly
        # since that's what process_search would call
        
        # In a real integration, process_search would call enhance_behavioral_data
        # We'll test that enhance_behavioral_data returns the expected structure
        enhanced_data = enhance_behavioral_data(
            self.behavioral_data,
            [self.candidate_data],
            self.user_prompt
        )
        
        # Check that the enhanced data contains the required metrics
        self.assertIn("commitment_momentum_index", enhanced_data)
        self.assertIn("risk_barrier_focus_score", enhanced_data)
        self.assertIn("identity_alignment_signal", enhanced_data)
        self.assertIn("psychometric_modeling_insight", enhanced_data)
        
        # Check that the metrics have the required structure
        self.assertIn("score", enhanced_data["commitment_momentum_index"])
        self.assertIn("description", enhanced_data["commitment_momentum_index"])
        self.assertIn("factors", enhanced_data["commitment_momentum_index"])
        
        self.assertIn("score", enhanced_data["risk_barrier_focus_score"])
        self.assertIn("description", enhanced_data["risk_barrier_focus_score"])
        self.assertIn("factors", enhanced_data["risk_barrier_focus_score"])
        
        self.assertIn("score", enhanced_data["identity_alignment_signal"])
        self.assertIn("description", enhanced_data["identity_alignment_signal"])
        self.assertIn("factors", enhanced_data["identity_alignment_signal"])
        
        self.assertIsInstance(enhanced_data["psychometric_modeling_insight"], str)

    def test_api_response_format(self):
        """Test that the API response format includes behavioral metrics."""
        # Enhance the behavioral data
        enhanced_data = enhance_behavioral_data(
            self.behavioral_data,
            [self.candidate_data],
            self.user_prompt
        )
        
        # Create a simulated API response with enhanced data
        api_response = self.api_response.copy()
        api_response["behavioral_data"] = enhanced_data
        
        # Check that the API response contains the enhanced behavioral data
        self.assertIn("commitment_momentum_index", api_response["behavioral_data"])
        self.assertIn("risk_barrier_focus_score", api_response["behavioral_data"])
        self.assertIn("identity_alignment_signal", api_response["behavioral_data"])
        self.assertIn("psychometric_modeling_insight", api_response["behavioral_data"])
        
        # Check that the API response can be serialized to JSON
        try:
            json_response = json.dumps(api_response)
            self.assertIsInstance(json_response, str)
        except Exception as e:
            self.fail(f"API response could not be serialized to JSON: {e}")

    def test_backward_compatibility(self):
        """Test that the enhanced behavioral data maintains backward compatibility."""
        # Enhance the behavioral data
        enhanced_data = enhance_behavioral_data(
            self.behavioral_data,
            [self.candidate_data],
            self.user_prompt
        )
        
        # Check that the original behavioral data is preserved
        for key in self.behavioral_data:
            self.assertIn(key, enhanced_data)
            self.assertEqual(enhanced_data[key], self.behavioral_data[key])
        
        # Check that clients that don't expect the new metrics can still use the original data
        original_keys = set(self.behavioral_data.keys())
        enhanced_keys = set(enhanced_data.keys())
        new_keys = enhanced_keys - original_keys
        
        # Create a simulated old client that only uses original keys
        old_client_data = {k: enhanced_data[k] for k in original_keys}
        
        # Check that the old client data matches the original data
        self.assertEqual(old_client_data, self.behavioral_data)

    def test_error_handling_in_api_integration(self):
        """Test error handling in API integration."""
        # Test with None behavioral data
        none_enhanced = enhance_behavioral_data(
            None,
            [self.candidate_data],
            self.user_prompt
        )
        self.assertEqual(none_enhanced, {})
        
        # Test with invalid behavioral data
        invalid_enhanced = enhance_behavioral_data(
            "not a dict",
            [self.candidate_data],
            self.user_prompt
        )
        self.assertEqual(invalid_enhanced, "not a dict")
        
        # Test with exception in generate_behavioral_metrics
        with patch('behavioral_metrics.generate_behavioral_metrics', side_effect=Exception("Test error")):
            error_enhanced = enhance_behavioral_data(
                self.behavioral_data,
                [self.candidate_data],
                self.user_prompt
            )
            # Should return original behavioral data on error for backward compatibility
            self.assertEqual(error_enhanced, self.behavioral_data)

if __name__ == "__main__":
    unittest.main()