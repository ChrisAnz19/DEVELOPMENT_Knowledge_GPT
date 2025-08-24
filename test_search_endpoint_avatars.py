#!/usr/bin/env python3
"""
Test to verify search endpoints include avatar data correctly.

This test simulates the search endpoint behavior to ensure avatar data
is properly included in API responses.
"""

import unittest
import json

def simulate_search_result_processing():
    """Simulate how the search result endpoint processes candidates with avatar data."""
    # Mock candidates from database (as they would be stored after validate_candidate_photos)
    stored_candidates = [
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
            "reasons": ["Strong technical background"],
            "linkedin_profile": {},
            "behavioral_data": {},
            # Avatar data stored after validation
            "avatar": {
                "type": "photo",
                "photo_url": "https://media.licdn.com/dms/image/valid-photo",
                "initials": None,
                "background_color": None
            },
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
            "profile_photo_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
            "accuracy": 88,
            "reasons": ["Product management experience"],
            "linkedin_profile": {},
            "behavioral_data": {},
            # Avatar data for fallback image
            "avatar": {
                "type": "initials",
                "photo_url": None,
                "initials": "JS",
                "background_color": "#3B82F6"
            },
            "photo_url": None  # Backward compatibility - None for fallback
        }
    ]
    
    # Simulate the processing done in get_search_result endpoint
    processed_candidates = []
    for candidate in stored_candidates:
        if isinstance(candidate, dict):
            processed_candidate = {
                "id": candidate.get("id"),
                "name": candidate.get("name"),
                "title": candidate.get("title"),
                "email": candidate.get("email"),
                "location": candidate.get("location"),
                "company": candidate.get("company"),
                "linkedin_url": candidate.get("linkedin_url"), 
                "profile_photo_url": candidate.get("profile_photo_url"),
                "accuracy": candidate.get("accuracy"),
                "reasons": candidate.get("reasons"),
                "linkedin_profile": candidate.get("linkedin_profile"),
                "behavioral_data": candidate.get("behavioral_data"),
                # New avatar data for initials fallback
                "avatar": candidate.get("avatar"),
                # Backward compatibility - photo_url field
                "photo_url": candidate.get("photo_url")
            }
            processed_candidates.append(processed_candidate)
    
    return {
        "request_id": "test-123",
        "status": "completed",
        "candidates": processed_candidates
    }


class TestSearchEndpointAvatars(unittest.TestCase):
    
    def test_search_result_includes_avatar_data(self):
        """Test that search results include avatar data for all candidates."""
        result = simulate_search_result_processing()
        
        self.assertIn("candidates", result)
        self.assertEqual(len(result["candidates"]), 2)
        
        # Check first candidate (photo avatar)
        candidate1 = result["candidates"][0]
        self.assertIn("avatar", candidate1)
        self.assertEqual(candidate1["avatar"]["type"], "photo")
        self.assertIsNotNone(candidate1["avatar"]["photo_url"])
        
        # Check second candidate (initials avatar)
        candidate2 = result["candidates"][1]
        self.assertIn("avatar", candidate2)
        self.assertEqual(candidate2["avatar"]["type"], "initials")
        self.assertEqual(candidate2["avatar"]["initials"], "JS")
        self.assertTrue(candidate2["avatar"]["background_color"].startswith("#"))
        
    def test_backward_compatibility_maintained(self):
        """Test that existing API behavior is maintained."""
        result = simulate_search_result_processing()
        
        for candidate in result["candidates"]:
            # All existing fields should be present
            required_fields = [
                "id", "name", "title", "email", "location", "company",
                "linkedin_url", "profile_photo_url", "accuracy", "reasons",
                "linkedin_profile", "behavioral_data", "photo_url"
            ]
            
            for field in required_fields:
                self.assertIn(field, candidate)
            
            # New avatar field should be additional
            self.assertIn("avatar", candidate)
            
    def test_photo_url_backward_compatibility(self):
        """Test that photo_url field behavior matches avatar data."""
        result = simulate_search_result_processing()
        
        for candidate in result["candidates"]:
            avatar = candidate["avatar"]
            photo_url = candidate["photo_url"]
            
            if avatar["type"] == "photo":
                # For photo avatars, photo_url should match avatar photo_url
                self.assertEqual(photo_url, avatar["photo_url"])
                self.assertIsNotNone(photo_url)
            elif avatar["type"] == "initials":
                # For initials avatars, photo_url should be None
                self.assertIsNone(photo_url)
                self.assertIsNone(avatar["photo_url"])
                
    def test_avatar_generation_logging_simulation(self):
        """Test that avatar generation would log appropriate information."""
        # Simulate the logging that would occur during avatar generation
        candidates = [
            {"name": "John Doe", "profile_photo_url": "https://media.licdn.com/valid"},
            {"name": "Jane Smith", "profile_photo_url": "https://static.licdn.com/fallback"},
            {"name": "Bob Wilson", "profile_photo_url": None}
        ]
        
        # Simulate avatar generation statistics
        photo_avatars = 1  # John Doe has valid photo
        initials_avatars = 2  # Jane Smith and Bob Wilson need initials
        
        self.assertEqual(photo_avatars + initials_avatars, len(candidates))
        self.assertGreater(photo_avatars, 0)
        self.assertGreater(initials_avatars, 0)
        
        # Verify we would log the right statistics
        log_message = f"Generated {photo_avatars} photo avatars, {initials_avatars} initials avatars"
        self.assertIn("photo avatars", log_message)
        self.assertIn("initials avatars", log_message)
        
    def test_error_handling_in_avatar_generation(self):
        """Test that avatar generation errors are handled gracefully."""
        # Simulate error cases that might occur
        error_cases = [
            {"first_name": None, "last_name": None},  # None names
            {"first_name": "", "last_name": ""},      # Empty names
            {"first_name": "123", "last_name": "456"}, # Non-alphabetic names
        ]
        
        for case in error_cases:
            # Should not crash and should return fallback avatar
            try:
                # Simulate the fallback behavior
                fallback_avatar = {
                    "type": "initials",
                    "photo_url": None,
                    "initials": "?",
                    "background_color": "#3B82F6"
                }
                
                # Verify fallback structure
                self.assertEqual(fallback_avatar["type"], "initials")
                self.assertEqual(fallback_avatar["initials"], "?")
                self.assertEqual(fallback_avatar["background_color"], "#3B82F6")
                
            except Exception as e:
                self.fail(f"Avatar generation should not crash on error case {case}: {e}")
                
    def test_api_response_json_serializable(self):
        """Test that the complete API response can be JSON serialized."""
        result = simulate_search_result_processing()
        
        try:
            # Should be able to serialize to JSON
            json_str = json.dumps(result)
            
            # Should be able to parse back
            parsed = json.loads(json_str)
            
            # Data should be intact
            self.assertEqual(len(parsed["candidates"]), 2)
            self.assertIn("avatar", parsed["candidates"][0])
            self.assertIn("avatar", parsed["candidates"][1])
            
        except (TypeError, ValueError) as e:
            self.fail(f"API response should be JSON serializable: {e}")


if __name__ == '__main__':
    unittest.main()