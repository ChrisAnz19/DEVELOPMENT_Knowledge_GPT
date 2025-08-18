#!/usr/bin/env python3
"""
Unit tests for LinkedIn photo validation logic.

This test suite verifies that the photo validation functions correctly identify
LinkedIn fallback images and prioritize candidates with valid profile photos.
"""

import unittest
import sys
import os

# Add the api directory to the path so we can import from main.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from api.main import is_valid_linkedin_photo, validate_candidate_photos, _get_photo_validation_reason, _get_photo_source


class TestPhotoValidation(unittest.TestCase):
    
    def test_linkedin_fallback_image_detection(self):
        """Test detection of LinkedIn fallback images."""
        # Primary LinkedIn fallback image
        fallback_url = "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"
        self.assertFalse(is_valid_linkedin_photo(fallback_url), 
                        "Should detect primary LinkedIn fallback image")
        
        # Fallback image in different URL format
        fallback_url2 = "https://static.licdn.com/scds/common/u/images/themes/katy/ghosts/person/ghost_person_200x200_v1.png"
        self.assertFalse(is_valid_linkedin_photo(fallback_url2),
                        "Should detect alternative LinkedIn fallback image")
        
        # Case insensitive detection
        fallback_url_upper = "HTTPS://STATIC.LICDN.COM/AERO-V1/SC/H/9C8PERY4ANDZJ6OHJKJP54MA2"
        self.assertFalse(is_valid_linkedin_photo(fallback_url_upper),
                        "Should detect fallback image regardless of case")
    
    def test_valid_linkedin_photo_detection(self):
        """Test detection of valid LinkedIn profile photos."""
        # Valid LinkedIn profile photo URL
        valid_url = "https://media.licdn.com/dms/image/v2/C5603AQE0-6w1xTp2Dw/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1519075821568?e=2147483647&v=beta&t=jVfUE2EyXrk__XirShU25FVRq5QSIMIr5IIc77X0YGE"
        self.assertTrue(is_valid_linkedin_photo(valid_url),
                       "Should recognize valid LinkedIn profile photo")
        
        # Another valid LinkedIn profile photo format
        valid_url2 = "https://media.licdn.com/dms/image/C4E03AQHOGF4NthKIzA/profile-displayphoto-shrink_200_200/0/1517580852157"
        self.assertTrue(is_valid_linkedin_photo(valid_url2),
                       "Should recognize valid LinkedIn profile photo format")
        
        # Valid LinkedIn URL without specific patterns
        valid_url3 = "https://media.licdn.com/dms/image/some-unique-photo-id"
        self.assertTrue(is_valid_linkedin_photo(valid_url3),
                       "Should assume LinkedIn URLs are valid unless proven otherwise")
    
    def test_non_linkedin_photo_urls(self):
        """Test handling of non-LinkedIn photo URLs."""
        # Non-LinkedIn URLs should be considered valid
        external_url = "https://example.com/profile-photo.jpg"
        self.assertTrue(is_valid_linkedin_photo(external_url),
                       "Should consider non-LinkedIn URLs as valid")
        
        # Company logo or other sources
        company_url = "https://company.com/employee-photos/john-doe.png"
        self.assertTrue(is_valid_linkedin_photo(company_url),
                       "Should consider company photo URLs as valid")
    
    def test_invalid_photo_urls(self):
        """Test handling of invalid or missing photo URLs."""
        # None/empty URLs
        self.assertFalse(is_valid_linkedin_photo(None),
                        "Should return False for None URL")
        self.assertFalse(is_valid_linkedin_photo(""),
                        "Should return False for empty URL")
        self.assertFalse(is_valid_linkedin_photo("   "),
                        "Should return False for whitespace URL")
        
        # Non-string inputs
        self.assertFalse(is_valid_linkedin_photo(123),
                        "Should return False for non-string input")
        self.assertFalse(is_valid_linkedin_photo({}),
                        "Should return False for dict input")
    
    def test_photo_validation_reason(self):
        """Test photo validation reason generation."""
        # No URL
        self.assertEqual(_get_photo_validation_reason(None, False), "no_url")
        self.assertEqual(_get_photo_validation_reason("", False), "no_url")
        
        # Fallback image
        fallback_url = "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"
        self.assertEqual(_get_photo_validation_reason(fallback_url, False), "fallback_image")
        
        # Valid photo
        valid_url = "https://media.licdn.com/dms/image/valid-photo"
        self.assertEqual(_get_photo_validation_reason(valid_url, True), "valid")
        
        # Invalid pattern
        invalid_url = "https://some-invalid-pattern.com/photo"
        self.assertEqual(_get_photo_validation_reason(invalid_url, False), "invalid_pattern")
    
    def test_photo_source_detection(self):
        """Test photo source detection."""
        # LinkedIn sources
        linkedin_url = "https://media.licdn.com/dms/image/photo"
        self.assertEqual(_get_photo_source(linkedin_url), "linkedin")
        
        linkedin_static = "https://static.licdn.com/photo"
        self.assertEqual(_get_photo_source(linkedin_static), "linkedin")
        
        # Non-LinkedIn sources
        external_url = "https://example.com/photo.jpg"
        self.assertEqual(_get_photo_source(external_url), "other")
        
        # No URL
        self.assertEqual(_get_photo_source(None), "none")
        self.assertEqual(_get_photo_source(""), "none")
    
    def test_validate_candidate_photos_function(self):
        """Test the validate_candidate_photos function with candidate data."""
        candidates = [
            {
                "name": "John Doe",
                "profile_photo_url": "https://media.licdn.com/dms/image/valid-photo",
                "title": "CEO"
            },
            {
                "name": "Jane Smith", 
                "profile_pic_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
                "title": "CTO"
            },
            {
                "name": "Bob Johnson",
                "title": "CFO"
                # No photo URL
            }
        ]
        
        validated = validate_candidate_photos(candidates)
        
        # Check that all candidates have photo validation data
        self.assertEqual(len(validated), 3)
        
        # John Doe should have valid photo
        john = validated[0]
        self.assertTrue(john["photo_validation"]["is_valid_photo"])
        self.assertEqual(john["photo_validation"]["photo_validation_reason"], "valid")
        self.assertEqual(john["photo_validation"]["photo_source"], "linkedin")
        self.assertEqual(john["selection_priority"], 10)
        
        # Jane Smith should have invalid photo (fallback)
        jane = validated[1]
        self.assertFalse(jane["photo_validation"]["is_valid_photo"])
        self.assertEqual(jane["photo_validation"]["photo_validation_reason"], "fallback_image")
        self.assertEqual(jane["photo_validation"]["photo_source"], "linkedin")
        self.assertEqual(jane["selection_priority"], 1)
        
        # Bob Johnson should have no photo
        bob = validated[2]
        self.assertFalse(bob["photo_validation"]["is_valid_photo"])
        self.assertEqual(bob["photo_validation"]["photo_validation_reason"], "no_url")
        self.assertEqual(bob["photo_validation"]["photo_source"], "none")
        self.assertEqual(bob["selection_priority"], 1)
    
    def test_validate_candidate_photos_edge_cases(self):
        """Test validate_candidate_photos with edge cases."""
        # Empty list
        self.assertEqual(validate_candidate_photos([]), [])
        
        # None input
        self.assertEqual(validate_candidate_photos(None), None)
        
        # Non-dict candidates
        candidates = ["not a dict", 123, None]
        validated = validate_candidate_photos(candidates)
        self.assertEqual(len(validated), 3)
        # Non-dict items should be passed through unchanged
        self.assertEqual(validated[0], "not a dict")
        self.assertEqual(validated[1], 123)
        self.assertEqual(validated[2], None)
    
    def test_photo_validation_with_different_field_names(self):
        """Test photo validation with different photo URL field names."""
        candidates = [
            {"name": "Test1", "profile_photo_url": "https://media.licdn.com/valid"},
            {"name": "Test2", "profile_pic_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"},
            {"name": "Test3", "photo_url": "https://example.com/photo.jpg"}
        ]
        
        validated = validate_candidate_photos(candidates)
        
        # All should have photo validation data
        for candidate in validated:
            self.assertIn("photo_validation", candidate)
            self.assertIn("selection_priority", candidate)
        
        # Check specific validations
        self.assertTrue(validated[0]["photo_validation"]["is_valid_photo"])  # Valid LinkedIn
        self.assertFalse(validated[1]["photo_validation"]["is_valid_photo"])  # Fallback
        self.assertTrue(validated[2]["photo_validation"]["is_valid_photo"])  # External URL


if __name__ == '__main__':
    unittest.main()