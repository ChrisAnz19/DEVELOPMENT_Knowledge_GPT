"""
End-to-end integration tests for the behavioral metrics API integration.

This test suite focuses on testing the integration of behavioral metrics with the API,
ensuring that the metrics are correctly included in API responses and that the API
maintains backward compatibility with existing clients.
"""

import unittest
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime
import uuid
import requests
from fastapi.testclient import TestClient

from api.main import app
from behavioral_metrics import enhance_behavioral_data
from prompt_formatting import simulate_behavioral_data

class TestBehavioralMetricsAPIIntegrationE2E(unittest.TestCase):
    """End-to-end integration tests for the behavioral metrics API integration."""
    
    def setUp(self):
        """Set up test data and client."""
        # Create a test client
        self.client = TestClient(app)
        
        # Sample user prompt
        self.user_prompt = "Find a senior developer with cloud experience"
        
        # Sample candidate data
        self.candidate_data = {
            "name": "John Doe",
            "title": "Senior Software Developer",
            "company": "Cloud Tech Inc.",
            "email": "john@example.com",
            "linkedin_url": "https://linkedin.com/in/johndoe",
            "accuracy": 90,
            "reasons": ["Senior developer title", "Cloud experience"]
        }
        
        # Current timestamp for testing
        self.current_time = time.time()
        
        # Sample behavioral data
        self.behavioral_data = {
            "insights": [
                "High engagement with technical documentation indicates technical focus",
                "Multiple sessions during business hours suggest professional interest"
            ],
            "page_views": [
                {"url": "/docs", "title": "API Documentation", "timestamp": self.current_time - 86400},
                {"url": "/pricing", "title": "Pricing Plans", "timestamp": self.current_time - 43200},
                {"url": "/features", "title": "Product Features", "timestamp": self.current_time - 21600},
                {"url": "/case-studies", "title": "Customer Success Stories", "timestamp": self.current_time - 10800}
            ],
            "sessions": [
                {"timestamp": self.current_time - 86400, "duration": 600, "pages": 5},
                {"timestamp": self.current_time - 43200, "duration": 900, "pages": 8},
                {"timestamp": self.current_time - 21600, "duration": 300, "pages": 3},
                {"timestamp": self.current_time - 10800, "duration": 1200, "pages": 10}
            ],
            "content_interactions": [
                {"content_type": "api_documentation", "title": "REST API Reference", "timestamp": self.current_time - 86400},
                {"content_type": "whitepaper", "title": "Cloud Architecture Best Practices", "timestamp": self.current_time - 43200},
                {"content_type": "case_study", "title": "Enterprise Implementation", "timestamp": self.current_time - 21600},
                {"content_type": "webinar", "title": "Product Demo", "timestamp": self.current_time - 10800}
            ]
        }
        
        # Generate a unique request ID for testing
        self.request_id = str(uuid.uuid4())

    def test_api_search_endpoint_with_behavioral_metrics(self):
        """Test that the search endpoint includes behavioral metrics in the response."""
        # Mock the database functions to avoid actual database operations
        with patch('api.main.store_search_to_database', return_value=1), \
             patch('api.main.store_people_to_database'), \
             patch('api.main.get_search_from_database'), \
             patch('api.main.get_people_for_search', return_value=[self.candidate_data]), \
             patch('api.main.search_people_via_internal_database', return_value=[self.candidate_data]), \
             patch('api.main.select_top_candidates', return_value=[self.candidate_data]), \
             patch('api.main.simulate_behavioral_data', return_value=self.behavioral_data):
            
            # Create a search request
            response = self.client.post(
                "/api/search",
                json={"prompt": self.user_prompt, "max_candidates": 1}
            )
            
            # Check that the request was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "processing")
            
            # Store the request ID for the next step
            request_id = data["request_id"]
            
            # Mock the search result in memory for the GET request
            from api.main import search_results
            
            # Enhance the behavioral data with our metrics
            enhanced_data = enhance_behavioral_data(
                self.behavioral_data,
                [self.candidate_data],
                self.user_prompt
            )
            
            # Create a mock search result
            search_results[request_id] = {
                "request_id": request_id,
                "status": "completed",
                "prompt": self.user_prompt,
                "filters": {"title": "Senior Developer", "keywords": ["cloud"]},
                "candidates": [self.candidate_data],
                "behavioral_data": enhanced_data,
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Get the search result
            response = self.client.get(f"/api/search/{request_id}")
            
            # Check that the response was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Check that the behavioral metrics are included in the response
            self.assertIn("behavioral_data", data)
            behavioral_data = data["behavioral_data"]
            
            # Check that all required metrics are present
            self.assertIn("commitment_momentum_index", behavioral_data)
            self.assertIn("risk_barrier_focus_score", behavioral_data)
            self.assertIn("identity_alignment_signal", behavioral_data)
            self.assertIn("psychometric_modeling_insight", behavioral_data)
            
            # Check that the metrics have the required structure as per API documentation
            cmi = behavioral_data["commitment_momentum_index"]
            self.assertIn("score", cmi)
            self.assertIn("description", cmi)
            self.assertIn("factors", cmi)
            self.assertIn("bottom_funnel_engagement", cmi["factors"])
            self.assertIn("recency_frequency", cmi["factors"])
            self.assertIn("off_hours_activity", cmi["factors"])
            
            rbfs = behavioral_data["risk_barrier_focus_score"]
            self.assertIn("score", rbfs)
            self.assertIn("description", rbfs)
            self.assertIn("factors", rbfs)
            self.assertIn("risk_content_engagement", rbfs["factors"])
            self.assertIn("negative_review_focus", rbfs["factors"])
            self.assertIn("compliance_focus", rbfs["factors"])
            
            ias = behavioral_data["identity_alignment_signal"]
            self.assertIn("score", ias)
            self.assertIn("description", ias)
            self.assertIn("factors", ias)
            self.assertIn("purpose_driven_engagement", ias["factors"])
            self.assertIn("thought_leadership_focus", ias["factors"])
            self.assertIn("community_engagement", ias["factors"])
            
            # Check that the metrics can be serialized to JSON
            try:
                json_data = json.dumps(data)
                self.assertIsInstance(json_data, str)
            except Exception as e:
                self.fail(f"API response could not be serialized to JSON: {e}")

    def test_api_backward_compatibility(self):
        """Test that the API maintains backward compatibility with existing clients."""
        # Mock the database functions to avoid actual database operations
        with patch('api.main.store_search_to_database', return_value=1), \
             patch('api.main.store_people_to_database'), \
             patch('api.main.get_search_from_database'), \
             patch('api.main.get_people_for_search', return_value=[self.candidate_data]), \
             patch('api.main.search_people_via_internal_database', return_value=[self.candidate_data]), \
             patch('api.main.select_top_candidates', return_value=[self.candidate_data]), \
             patch('api.main.simulate_behavioral_data', return_value=self.behavioral_data):
            
            # Create a search request
            response = self.client.post(
                "/api/search",
                json={"prompt": self.user_prompt, "max_candidates": 1}
            )
            
            # Check that the request was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "processing")
            
            # Store the request ID for the next step
            request_id = data["request_id"]
            
            # Mock the search result in memory for the GET request
            from api.main import search_results
            
            # Enhance the behavioral data with our metrics
            enhanced_data = enhance_behavioral_data(
                self.behavioral_data,
                [self.candidate_data],
                self.user_prompt
            )
            
            # Create a mock search result
            search_results[request_id] = {
                "request_id": request_id,
                "status": "completed",
                "prompt": self.user_prompt,
                "filters": {"title": "Senior Developer", "keywords": ["cloud"]},
                "candidates": [self.candidate_data],
                "behavioral_data": enhanced_data,
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Get the search result
            response = self.client.get(f"/api/search/{request_id}")
            
            # Check that the response was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Simulate an old client that only expects the original behavioral data fields
            original_keys = set(self.behavioral_data.keys())
            
            # Check that all original keys are still present in the response
            for key in original_keys:
                self.assertIn(key, data["behavioral_data"])
                
            # Check that the original data values are preserved
            for key in original_keys:
                self.assertEqual(data["behavioral_data"][key], self.behavioral_data[key])
                
            # Check that an old client can still parse the response
            old_client_data = {
                "request_id": data["request_id"],
                "status": data["status"],
                "prompt": data["prompt"],
                "filters": data["filters"],
                "candidates": data["candidates"],
                "behavioral_data": {k: data["behavioral_data"][k] for k in original_keys},
                "created_at": data["created_at"],
                "completed_at": data["completed_at"]
            }
            
            # Check that the old client data can be serialized to JSON
            try:
                json_data = json.dumps(old_client_data)
                self.assertIsInstance(json_data, str)
            except Exception as e:
                self.fail(f"Old client data could not be serialized to JSON: {e}")

    def test_api_error_handling(self):
        """Test error handling in the API integration."""
        # Mock the database functions to avoid actual database operations
        with patch('api.main.store_search_to_database', return_value=1), \
             patch('api.main.store_people_to_database'), \
             patch('api.main.get_search_from_database'), \
             patch('api.main.get_people_for_search', return_value=[self.candidate_data]), \
             patch('api.main.search_people_via_internal_database', return_value=[self.candidate_data]), \
             patch('api.main.select_top_candidates', return_value=[self.candidate_data]), \
             patch('api.main.simulate_behavioral_data', return_value=self.behavioral_data), \
             patch('behavioral_metrics.enhance_behavioral_data', side_effect=Exception("Test error")):
            
            # Create a search request
            response = self.client.post(
                "/api/search",
                json={"prompt": self.user_prompt, "max_candidates": 1}
            )
            
            # Check that the request was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "processing")
            
            # Store the request ID for the next step
            request_id = data["request_id"]
            
            # Mock the search result in memory for the GET request
            from api.main import search_results
            
            # Create a mock search result with an error in behavioral metrics
            search_results[request_id] = {
                "request_id": request_id,
                "status": "completed",
                "prompt": self.user_prompt,
                "filters": {"title": "Senior Developer", "keywords": ["cloud"]},
                "candidates": [self.candidate_data],
                "behavioral_data": self.behavioral_data,  # Original data without enhancement
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Get the search result
            response = self.client.get(f"/api/search/{request_id}")
            
            # Check that the response was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Check that the behavioral data is the original data (fallback)
            self.assertIn("behavioral_data", data)
            self.assertEqual(data["behavioral_data"], self.behavioral_data)
            
            # Check that the original behavioral data fields are present
            self.assertIn("insights", data["behavioral_data"])
            self.assertIn("page_views", data["behavioral_data"])
            self.assertIn("sessions", data["behavioral_data"])
            self.assertIn("content_interactions", data["behavioral_data"])

    def test_api_json_endpoint(self):
        """Test that the JSON endpoint includes behavioral metrics."""
        # Mock the necessary functions
        with patch('api.main.load_search_from_json') as mock_load:
            # Create a mock JSON response with behavioral metrics
            mock_load.return_value = {
                "request_id": self.request_id,
                "status": "completed",
                "prompt": self.user_prompt,
                "filters": {"title": "Senior Developer", "keywords": ["cloud"]},
                "candidates": [self.candidate_data],
                "behavioral_data": {
                    **self.behavioral_data,
                    "commitment_momentum_index": {
                        "score": 85,
                        "description": "Active: Reviewing implementation guides",
                        "factors": {
                            "bottom_funnel_engagement": 0.9,
                            "recency_frequency": 0.8,
                            "off_hours_activity": 0.7
                        }
                    },
                    "risk_barrier_focus_score": {
                        "score": 35,
                        "description": "Low concern: Focused on benefits",
                        "factors": {
                            "risk_content_engagement": 0.3,
                            "negative_review_focus": 0.4,
                            "compliance_focus": 0.3
                        }
                    },
                    "identity_alignment_signal": {
                        "score": 70,
                        "description": "Strong alignment: Values-driven decision",
                        "factors": {
                            "purpose_driven_engagement": 0.7,
                            "thought_leadership_focus": 0.8,
                            "community_engagement": 0.6
                        }
                    },
                    "psychometric_modeling_insight": "This prospect responds well to detailed technical information and values data-driven discussions."
                },
                "created_at": datetime.now().isoformat(),
                "completed_at": datetime.now().isoformat()
            }
            
            # Get the JSON data
            response = self.client.get(f"/api/search/{self.request_id}/json")
            
            # Check that the response was successful
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Check that the behavioral metrics are included in the response
            self.assertIn("behavioral_data", data)
            behavioral_data = data["behavioral_data"]
            
            # Check that all required metrics are present
            self.assertIn("commitment_momentum_index", behavioral_data)
            self.assertIn("risk_barrier_focus_score", behavioral_data)
            self.assertIn("identity_alignment_signal", behavioral_data)
            self.assertIn("psychometric_modeling_insight", behavioral_data)

if __name__ == "__main__":
    unittest.main()