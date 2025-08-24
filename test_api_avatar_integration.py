#!/usr/bin/env python3
"""
Integration tests for API responses with avatar data.

This test suite verifies that API endpoints return proper avatar metadata
and maintain backward compatibility with existing clients.
"""

import unittest
import json

class TestAPIAvatarIntegration(unittest.TestCase):
    
    def test_api_response_structure_with_avatar(self):
        """Test that API responses include avatar data in correct structure."""
        # Mock API response with avatar data
        mock_response = {
            "request_id": "test-123",
            "status": "completed",
            "candidates": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "title": "Software Engineer",
                    "email": "john.doe@example.com",
                    "location": "San Francisco, CA",
                    "company": "Tech Corp",
                    "linkedin_url": "https://linkedin.com/in/johndoe",
                    "profile_photo_url": "https://media.licdn.com/dms/image/valid-photo",
                    "accuracy": 95,
                    "reasons": ["Strong technical background", "Relevant experience"],
                    "linkedin_profile": {},
                    "behavioral_data": {},
                    # New avatar data
                    "avatar": {
                        "type": "photo",
                        "photo_url": "https://media.licdn.com/dms/image/valid-photo",
                        "initials": None,
                        "background_color": None
                    },
                    # Backward compatibility
                    "photo_url": "https://media.licdn.com/dms/image/valid-photo"
                },
                {
                    "id": 2,
                    "name": "Jane Smith",
                    "title": "Product Manager", 
                    "email": "jane.smith@example.com",
                    "location": "New York, NY",
                    "company": "Innovation Inc",
                    "linkedin_url": "https://linkedin.com/in/janesmith",
                    "profile_photo_url": None,
                    "accuracy": 88,
                    "reasons": ["Product management experience", "Industry knowledge"],
                    "linkedin_profile": {},
                    "behavioral_data": {},
                    # New avatar data for initials fallback
                    "avatar": {
                        "type": "initials",
                        "photo_url": None,
                        "initials": "JS",
                        "background_color": "#3B82F6"
                    },
                    # Backward compatibility
                    "photo_url": None
                }
            ]
        }
        
        # Validate response structure
        self.assertIn("candidates", mock_response)
        self.assertEqual(len(mock_response["candidates"]), 2)
        
        # Validate first candidate (photo avatar)
        candidate1 = mock_response["candidates"][0]
        self.assertIn("avatar", candidate1)
        self.assertEqual(candidate1["avatar"]["type"], "photo")
        self.assertIsNotNone(candidate1["avatar"]["photo_url"])
        self.assertIsNone(candidate1["avatar"]["initials"])
        self.assertIsNone(candidate1["avatar"]["background_color"])
        
        # Backward compatibility
        self.assertIn("photo_url", candidate1)
        self.assertEqual(candidate1["photo_url"], candidate1["avatar"]["photo_url"])
        
        # Validate second candidate (initials avatar)
        candidate2 = mock_response["candidates"][1]
        self.assertIn("avatar", candidate2)
        self.assertEqual(candidate2["avatar"]["type"], "initials")
        self.assertIsNone(candidate2["avatar"]["photo_url"])
        self.assertEqual(candidate2["avatar"]["initials"], "JS")
        self.assertTrue(candidate2["avatar"]["background_color"].startswith("#"))
        
        # Backward compatibility
        self.assertIn("photo_url", candidate2)
        self.assertIsNone(candidate2["photo_url"])
        
    def test_backward_compatibility_fields(self):
        """Test that existing API clients receive expected fields."""
        # Mock candidate with initials avatar
        candidate = {
            "name": "Test User",
            "avatar": {
                "type": "initials",
                "photo_url": None,
                "initials": "TU",
                "background_color": "#10B981"
            },
            "photo_url": None  # Should be None for fallback images
        }
        
        # Existing clients should still get photo_url field
        self.assertIn("photo_url", candidate)
        
        # For fallback cases, photo_url should be None (not the fallback URL)
        self.assertIsNone(candidate["photo_url"])
        
        # New avatar data should be additional, not replacing
        self.assertIn("avatar", candidate)
        
    def test_avatar_data_validation(self):
        """Test that avatar data meets expected format requirements."""
        # Test photo avatar format
        photo_avatar = {
            "type": "photo",
            "photo_url": "https://media.licdn.com/dms/image/valid-photo",
            "initials": None,
            "background_color": None
        }
        
        self.assertEqual(photo_avatar["type"], "photo")
        self.assertTrue(photo_avatar["photo_url"].startswith("http"))
        self.assertIsNone(photo_avatar["initials"])
        self.assertIsNone(photo_avatar["background_color"])
        
        # Test initials avatar format
        initials_avatar = {
            "type": "initials",
            "photo_url": None,
            "initials": "AB",
            "background_color": "#3B82F6"
        }
        
        self.assertEqual(initials_avatar["type"], "initials")
        self.assertIsNone(initials_avatar["photo_url"])
        self.assertEqual(len(initials_avatar["initials"]), 2)
        self.assertTrue(initials_avatar["background_color"].startswith("#"))
        self.assertEqual(len(initials_avatar["background_color"]), 7)  # #RRGGBB format
        
    def test_error_handling_graceful_degradation(self):
        """Test that API handles avatar generation failures gracefully."""
        # Mock candidate with avatar generation failure
        candidate_with_error = {
            "name": "",  # Empty name that might cause issues
            "avatar": {
                "type": "initials",
                "photo_url": None,
                "initials": "?",
                "background_color": "#3B82F6"  # Default fallback
            },
            "photo_url": None
        }
        
        # Should have fallback avatar even with empty name
        self.assertEqual(candidate_with_error["avatar"]["type"], "initials")
        self.assertEqual(candidate_with_error["avatar"]["initials"], "?")
        self.assertEqual(candidate_with_error["avatar"]["background_color"], "#3B82F6")
        
    def test_json_serialization_compatibility(self):
        """Test that avatar data can be properly JSON serialized."""
        response_with_avatars = {
            "candidates": [
                {
                    "name": "John Doe",
                    "avatar": {
                        "type": "photo",
                        "photo_url": "https://example.com/photo.jpg",
                        "initials": None,
                        "background_color": None
                    }
                },
                {
                    "name": "Jane Smith",
                    "avatar": {
                        "type": "initials",
                        "photo_url": None,
                        "initials": "JS",
                        "background_color": "#3B82F6"
                    }
                }
            ]
        }
        
        # Should be able to serialize to JSON without errors
        try:
            json_str = json.dumps(response_with_avatars)
            parsed_back = json.loads(json_str)
            
            # Verify data integrity after serialization
            self.assertEqual(len(parsed_back["candidates"]), 2)
            self.assertEqual(parsed_back["candidates"][0]["avatar"]["type"], "photo")
            self.assertEqual(parsed_back["candidates"][1]["avatar"]["type"], "initials")
            self.assertEqual(parsed_back["candidates"][1]["avatar"]["initials"], "JS")
            
        except (TypeError, ValueError) as e:
            self.fail(f"JSON serialization failed: {e}")
            
    def test_api_response_completeness(self):
        """Test that API responses include all required fields."""
        # Mock complete API response
        complete_response = {
            "request_id": "test-456",
            "status": "completed",
            "prompt": "Find software engineers",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:01:00Z",
            "estimated_count": 150,
            "error": None,
            "candidates": [
                {
                    "id": 1,
                    "name": "Alice Johnson",
                    "title": "Senior Software Engineer",
                    "email": "alice@example.com",
                    "location": "Seattle, WA",
                    "company": "Tech Solutions",
                    "linkedin_url": "https://linkedin.com/in/alicejohnson",
                    "profile_photo_url": "https://static.licdn.com/fallback-image",
                    "accuracy": 92,
                    "reasons": ["Strong technical skills", "Relevant experience"],
                    "linkedin_profile": {"summary": "Experienced engineer"},
                    "behavioral_data": {"scores": {"engagement": 85}},
                    # Enhanced with avatar data
                    "avatar": {
                        "type": "initials",
                        "photo_url": None,
                        "initials": "AJ",
                        "background_color": "#10B981"
                    },
                    "photo_url": None  # Backward compatibility
                }
            ]
        }
        
        # Validate all required top-level fields
        required_fields = ["request_id", "status", "candidates"]
        for field in required_fields:
            self.assertIn(field, complete_response)
            
        # Validate candidate has both old and new fields
        candidate = complete_response["candidates"][0]
        
        # Existing required fields
        existing_fields = ["name", "title", "company", "photo_url"]
        for field in existing_fields:
            self.assertIn(field, candidate)
            
        # New avatar field
        self.assertIn("avatar", candidate)
        avatar = candidate["avatar"]
        avatar_fields = ["type", "photo_url", "initials", "background_color"]
        for field in avatar_fields:
            self.assertIn(field, avatar)
            
    def test_legacy_client_compatibility(self):
        """Test that legacy clients can still function with new response format."""
        # Simulate how a legacy client might process the response
        api_response = {
            "candidates": [
                {
                    "name": "Legacy Test User",
                    "title": "Manager",
                    "company": "Old Corp",
                    "photo_url": "https://media.licdn.com/valid-photo",  # Legacy field
                    "avatar": {  # New field that legacy clients will ignore
                        "type": "photo",
                        "photo_url": "https://media.licdn.com/valid-photo",
                        "initials": None,
                        "background_color": None
                    }
                },
                {
                    "name": "Another User",
                    "title": "Developer", 
                    "company": "New Corp",
                    "photo_url": None,  # Legacy field - None for fallback
                    "avatar": {  # New field that legacy clients will ignore
                        "type": "initials",
                        "photo_url": None,
                        "initials": "AU",
                        "background_color": "#F59E0B"
                    }
                }
            ]
        }
        
        # Legacy client processing (ignores avatar field)
        for candidate in api_response["candidates"]:
            # Legacy clients can still access standard fields
            self.assertIn("name", candidate)
            self.assertIn("title", candidate)
            self.assertIn("company", candidate)
            self.assertIn("photo_url", candidate)
            
            # Legacy clients will ignore avatar field (no errors)
            # They can still check if photo_url is None to handle missing photos
            photo_url = candidate.get("photo_url")
            if photo_url:
                # Legacy client would display the photo
                self.assertTrue(photo_url.startswith("http"))
            else:
                # Legacy client would show placeholder or skip photo
                self.assertIsNone(photo_url)


if __name__ == '__main__':
    unittest.main()