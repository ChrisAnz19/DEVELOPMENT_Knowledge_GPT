#!/usr/bin/env python3
"""
Test script to verify the API response structure includes the new focused behavioral insight format.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from api.main import SearchResponse
from behavioral_metrics import enhance_behavioral_data

class TestAPIResponseStructure(unittest.TestCase):
    """Test cases for the updated API response structure."""
    
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
    
    def test_new_behavioral_data_format(self):
        """Test that the new behavioral data format includes behavioral_insight."""
        # Test the enhance_behavioral_data function
        enhanced_data = enhance_behavioral_data(
            behavioral_data=self.sample_behavioral_data,
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        # Verify the new format
        self.assertIn("behavioral_insight", enhanced_data)
        self.assertIsInstance(enhanced_data["behavioral_insight"], str)
        self.assertGreater(len(enhanced_data["behavioral_insight"]), 0)
        
        # Verify that the new format contains both behavioral_insight and scores fields
        self.assertEqual(len(enhanced_data.keys()), 2, "Enhanced data should contain behavioral_insight and scores fields")
        self.assertIn("scores", enhanced_data, "Enhanced data should include scores object")
        
        print(f"✓ Enhanced behavioral data format: {enhanced_data}")
    
    def test_search_response_validation(self):
        """Test that SearchResponse validates the new behavioral data format."""
        # Create a response with new format
        response_data = {
            "request_id": "test-123",
            "status": "completed",
            "prompt": self.user_prompt,
            "behavioral_data": {
                "behavioral_insight": "This is a focused behavioral insight for engagement."
            },
            "created_at": "2025-07-16T01:23:45Z"
        }
        
        response = SearchResponse(**response_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertTrue(is_valid)
        
        print(f"✓ New format validation passed: {response.behavioral_data}")
    
    def test_backward_compatibility_validation(self):
        """Test that SearchResponse maintains backward compatibility with legacy format."""
        # Create a response with legacy format
        legacy_response_data = {
            "request_id": "test-456",
            "status": "completed", 
            "prompt": self.user_prompt,
            "behavioral_data": {
                "commitment_momentum_index": {
                    "score": 75,
                    "description": "High commitment momentum"
                },
                "risk_barrier_focus_score": {
                    "score": 60,
                    "description": "Moderate risk focus"
                }
            },
            "created_at": "2025-07-16T01:23:45Z"
        }
        
        response = SearchResponse(**legacy_response_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertTrue(is_valid)
        
        print(f"✓ Legacy format validation passed: {response.behavioral_data}")
    
    def test_empty_behavioral_data_validation(self):
        """Test that SearchResponse handles empty behavioral data gracefully."""
        # Create a response with no behavioral data
        empty_response_data = {
            "request_id": "test-789",
            "status": "completed",
            "prompt": self.user_prompt,
            "behavioral_data": None,
            "created_at": "2025-07-16T01:23:45Z"
        }
        
        response = SearchResponse(**empty_response_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertTrue(is_valid)
        
        print(f"✓ Empty behavioral data validation passed")
    
    def test_invalid_behavioral_insight_type(self):
        """Test that SearchResponse detects invalid behavioral_insight type."""
        # Create a response with invalid behavioral_insight type
        invalid_response_data = {
            "request_id": "test-invalid",
            "status": "completed",
            "prompt": self.user_prompt,
            "behavioral_data": {
                "behavioral_insight": 123  # Should be string, not number
            },
            "created_at": "2025-07-16T01:23:45Z"
        }
        
        response = SearchResponse(**invalid_response_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertFalse(is_valid)
        
        print(f"✓ Invalid type validation correctly failed")
    
    def test_empty_behavioral_insight_validation(self):
        """Test that SearchResponse detects empty behavioral_insight."""
        # Create a response with empty behavioral_insight
        empty_insight_data = {
            "request_id": "test-empty-insight",
            "status": "completed",
            "prompt": self.user_prompt,
            "behavioral_data": {
                "behavioral_insight": ""  # Empty string should be invalid
            },
            "created_at": "2025-07-16T01:23:45Z"
        }
        
        response = SearchResponse(**empty_insight_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertFalse(is_valid)
        
        print(f"✓ Empty insight validation correctly failed")
    
    def test_enhance_behavioral_data_error_handling(self):
        """Test that enhance_behavioral_data handles errors gracefully."""
        # Test with None behavioral data
        enhanced_data = enhance_behavioral_data(
            behavioral_data=None,
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        self.assertIn("behavioral_insight", enhanced_data)
        self.assertIsInstance(enhanced_data["behavioral_insight"], str)
        
        # Test with invalid behavioral data type
        enhanced_data = enhance_behavioral_data(
            behavioral_data="invalid_type",
            candidates=self.sample_candidates,
            user_prompt=self.user_prompt
        )
        
        self.assertIn("behavioral_insight", enhanced_data)
        self.assertIsInstance(enhanced_data["behavioral_insight"], str)
        
        print(f"✓ Error handling works correctly")
    
    def test_api_response_example(self):
        """Test that the API response matches the expected format from the design document."""
        # Create a response based on the example in the design document
        example_response_data = {
            "request_id": "123e4567-e89b-12d3-a456-426614174000",
            "status": "completed",
            "prompt": "Looking for a senior developer with cloud experience",
            "filters": {"role": "developer", "seniority": "senior", "skills": ["cloud"]},
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
                    "linkedin_profile": {}
                }
            ],
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
            },
            "created_at": "2025-07-16T01:23:45Z",
            "completed_at": "2025-07-16T01:23:50Z"
        }
        
        response = SearchResponse(**example_response_data)
        
        # Test validation
        is_valid = response.validate_behavioral_data_format()
        self.assertTrue(is_valid)
        
        # Verify the response structure matches the design
        self.assertEqual(response.status, "completed")
        self.assertIn("behavioral_insight", response.behavioral_data)
        self.assertIsInstance(response.behavioral_data["behavioral_insight"], str)
        
        print(f"✓ API response example matches expected format")

if __name__ == "__main__":
    print("Testing API Response Structure Updates...")
    print("=" * 50)
    
    unittest.main(verbosity=2)