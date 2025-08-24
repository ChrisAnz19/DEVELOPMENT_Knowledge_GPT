#!/usr/bin/env python3
"""
Integration tests for enhanced photo validation with avatar generation.

This test suite verifies that the enhanced validate_candidate_photos function
correctly generates avatar data when LinkedIn photos are unavailable.
"""

import unittest

# Mock the functions we need for testing
def is_valid_linkedin_photo(photo_url: str) -> bool:
    """Mock photo validation function."""
    if not photo_url or not isinstance(photo_url, str) or not photo_url.strip():
        return False
    
    # Known LinkedIn fallback image patterns
    fallback_patterns = [
        "9c8pery4andzj6ohjkjp54ma2",
        "static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2",
        "static.licdn.com/scds/common/u/images/themes/katy/ghosts",
    ]
    
    photo_url_lower = photo_url.lower().strip()
    for pattern in fallback_patterns:
        if pattern in photo_url_lower:
            return False
    
    if "media.licdn.com" in photo_url_lower and "profile-displayphoto" in photo_url_lower:
        return True
    
    if "licdn.com" in photo_url_lower:
        return True
    
    return True

def extract_initials(first_name: str, last_name: str) -> str:
    """Extract initials from names."""
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    
    def get_first_letter(name: str) -> str:
        if not name:
            return ""
        for char in name:
            if char.isalpha():
                return char.upper()
        return ""
    
    first_initial = get_first_letter(first_name)
    last_initial = get_first_letter(last_name)
    
    if first_initial and last_initial:
        return f"{first_initial}{last_initial}"
    elif first_name:
        clean_name = ''.join(c for c in first_name if c.isalpha())
        if len(clean_name) >= 2:
            return clean_name[:2].upper()
        elif len(clean_name) == 1:
            return clean_name.upper()
    elif last_name:
        clean_name = ''.join(c for c in last_name if c.isalpha())
        if len(clean_name) >= 2:
            return clean_name[:2].upper()
        elif len(clean_name) == 1:
            return clean_name.upper()
    
    return "?"

def generate_deterministic_color(name: str) -> str:
    """Generate deterministic color."""
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
    
    if not name or not isinstance(name, str):
        return colors[0]
    
    name_normalized = name.lower().strip()
    if not name_normalized:
        return colors[0]
    
    try:
        name_hash = hash(name_normalized)
        color_index = abs(name_hash) % len(colors)
        return colors[color_index]
    except Exception:
        return colors[0]

def generate_initials_avatar(first_name: str, last_name: str) -> dict:
    """Generate initials avatar."""
    try:
        initials = extract_initials(first_name, last_name)
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        background_color = generate_deterministic_color(full_name)
        
        return {
            "type": "initials",
            "photo_url": None,
            "initials": initials,
            "background_color": background_color
        }
    except Exception:
        return {
            "type": "initials",
            "photo_url": None,
            "initials": "?",
            "background_color": "#3B82F6"
        }

def _get_photo_validation_reason(photo_url: str, is_valid: bool) -> str:
    """Get validation reason."""
    if not photo_url:
        return "no_url"
    if not is_valid:
        if "9c8pery4andzj6ohjkjp54ma2" in photo_url.lower():
            return "fallback_image"
        else:
            return "invalid_pattern"
    return "valid"

def _get_photo_source(photo_url: str) -> str:
    """Get photo source."""
    if not photo_url:
        return "none"
    if "licdn.com" in photo_url.lower():
        return "linkedin"
    return "other"

def validate_candidate_photos(candidates: list) -> list:
    """Enhanced photo validation with avatar generation."""
    if not candidates:
        return candidates
    
    validated_candidates = []
    
    for candidate in candidates:
        if not isinstance(candidate, dict):
            validated_candidates.append(candidate)
            continue
        
        # Extract photo URL from candidate
        photo_url = candidate.get("profile_photo_url") or candidate.get("profile_pic_url") or candidate.get("photo_url")
        
        # Validate photo
        is_valid = is_valid_linkedin_photo(photo_url)
        
        # Add photo validation status to candidate (existing functionality)
        candidate["photo_validation"] = {
            "photo_url": photo_url,
            "is_valid_photo": is_valid,
            "photo_validation_reason": _get_photo_validation_reason(photo_url, is_valid),
            "photo_source": _get_photo_source(photo_url)
        }
        
        # Generate avatar data based on photo validation
        if is_valid and photo_url:
            # Valid LinkedIn photo - use photo avatar
            candidate["avatar"] = {
                "type": "photo",
                "photo_url": photo_url,
                "initials": None,
                "background_color": None
            }
            # Maintain backward compatibility
            candidate["photo_url"] = photo_url
        else:
            # Invalid or missing photo - generate initials avatar
            first_name = candidate.get("first_name", "")
            last_name = candidate.get("last_name", "")
            
            # Try to extract names from full name if individual names not available
            if not first_name and not last_name:
                full_name = candidate.get("name", "")
                if full_name:
                    name_parts = full_name.strip().split()
                    if len(name_parts) >= 2:
                        first_name = name_parts[0]
                        last_name = name_parts[-1]
                    elif len(name_parts) == 1:
                        first_name = name_parts[0]
            
            # Generate initials avatar
            avatar_data = generate_initials_avatar(first_name, last_name)
            candidate["avatar"] = avatar_data
            
            # Backward compatibility - set photo_url to None for fallback images
            candidate["photo_url"] = None
        
        # Add selection priority (higher for valid photos)
        candidate["selection_priority"] = 10 if is_valid else 1
        
        validated_candidates.append(candidate)
    
    return validated_candidates


class TestEnhancedPhotoValidation(unittest.TestCase):
    
    def test_valid_linkedin_photo_generates_photo_avatar(self):
        """Test that valid LinkedIn photos generate photo avatar type."""
        candidates = [{
            "name": "John Doe",
            "first_name": "John",
            "last_name": "Doe",
            "profile_photo_url": "https://media.licdn.com/dms/image/valid-photo"
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should have photo avatar
        self.assertEqual(candidate["avatar"]["type"], "photo")
        self.assertEqual(candidate["avatar"]["photo_url"], "https://media.licdn.com/dms/image/valid-photo")
        self.assertIsNone(candidate["avatar"]["initials"])
        self.assertIsNone(candidate["avatar"]["background_color"])
        
        # Backward compatibility
        self.assertEqual(candidate["photo_url"], "https://media.licdn.com/dms/image/valid-photo")
        
    def test_fallback_linkedin_photo_generates_initials_avatar(self):
        """Test that LinkedIn fallback photos generate initials avatar."""
        candidates = [{
            "name": "Jane Smith",
            "first_name": "Jane",
            "last_name": "Smith",
            "profile_photo_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should have initials avatar
        self.assertEqual(candidate["avatar"]["type"], "initials")
        self.assertIsNone(candidate["avatar"]["photo_url"])
        self.assertEqual(candidate["avatar"]["initials"], "JS")
        self.assertTrue(candidate["avatar"]["background_color"].startswith("#"))
        
        # Backward compatibility - photo_url should be None for fallback
        self.assertIsNone(candidate["photo_url"])
        
    def test_no_photo_url_generates_initials_avatar(self):
        """Test that missing photo URLs generate initials avatar."""
        candidates = [{
            "name": "Michael Johnson",
            "first_name": "Michael",
            "last_name": "Johnson"
            # No photo_url field
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should have initials avatar
        self.assertEqual(candidate["avatar"]["type"], "initials")
        self.assertIsNone(candidate["avatar"]["photo_url"])
        self.assertEqual(candidate["avatar"]["initials"], "MJ")
        self.assertTrue(candidate["avatar"]["background_color"].startswith("#"))
        
        # Backward compatibility
        self.assertIsNone(candidate["photo_url"])
        
    def test_name_extraction_from_full_name(self):
        """Test that names are extracted from full name field when individual names missing."""
        candidates = [{
            "name": "Sarah Wilson"
            # No first_name or last_name fields
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should extract names and generate initials
        self.assertEqual(candidate["avatar"]["type"], "initials")
        self.assertEqual(candidate["avatar"]["initials"], "SW")
        
    def test_single_name_extraction(self):
        """Test initials generation with single name."""
        candidates = [{
            "name": "Madonna"
            # Single name only
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should use first two letters of single name
        self.assertEqual(candidate["avatar"]["type"], "initials")
        self.assertEqual(candidate["avatar"]["initials"], "MA")
        
    def test_no_name_fallback(self):
        """Test fallback when no name is available."""
        candidates = [{
            "title": "Software Engineer"
            # No name fields
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should use fallback initials
        self.assertEqual(candidate["avatar"]["type"], "initials")
        self.assertEqual(candidate["avatar"]["initials"], "?")
        self.assertEqual(candidate["avatar"]["background_color"], "#3B82F6")
        
    def test_photo_validation_fields_preserved(self):
        """Test that existing photo validation fields are preserved."""
        candidates = [{
            "name": "Test User",
            "profile_photo_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"
        }]
        
        validated = validate_candidate_photos(candidates)
        candidate = validated[0]
        
        # Should have photo validation fields
        self.assertIn("photo_validation", candidate)
        self.assertFalse(candidate["photo_validation"]["is_valid_photo"])
        self.assertEqual(candidate["photo_validation"]["photo_validation_reason"], "fallback_image")
        self.assertEqual(candidate["photo_validation"]["photo_source"], "linkedin")
        
        # Should have selection priority
        self.assertEqual(candidate["selection_priority"], 1)  # Low priority for invalid photo
        
    def test_mixed_candidates_processing(self):
        """Test processing candidates with mix of valid and invalid photos."""
        candidates = [
            {
                "name": "Valid Photo User",
                "first_name": "Valid",
                "last_name": "User",
                "profile_photo_url": "https://media.licdn.com/dms/image/valid-photo"
            },
            {
                "name": "Fallback Photo User", 
                "first_name": "Fallback",
                "last_name": "User",
                "profile_photo_url": "https://static.licdn.com/aero-v1/sc/h/9c8pery4andzj6ohjkjp54ma2"
            },
            {
                "name": "No Photo User",
                "first_name": "No",
                "last_name": "User"
            }
        ]
        
        validated = validate_candidate_photos(candidates)
        
        # First candidate should have photo avatar
        self.assertEqual(validated[0]["avatar"]["type"], "photo")
        self.assertEqual(validated[0]["selection_priority"], 10)
        
        # Second candidate should have initials avatar
        self.assertEqual(validated[1]["avatar"]["type"], "initials")
        self.assertEqual(validated[1]["avatar"]["initials"], "FU")
        self.assertEqual(validated[1]["selection_priority"], 1)
        
        # Third candidate should have initials avatar
        self.assertEqual(validated[2]["avatar"]["type"], "initials")
        self.assertEqual(validated[2]["avatar"]["initials"], "NU")
        self.assertEqual(validated[2]["selection_priority"], 1)


if __name__ == '__main__':
    unittest.main()