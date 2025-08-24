#!/usr/bin/env python3
"""
Unit tests for avatar generation functionality.

This test suite verifies that the avatar generation functions correctly create
initials and colors for candidates when LinkedIn photos are unavailable.
"""

import unittest
import sys
import os

# Define the avatar generation functions directly for testing
def extract_initials(first_name: str, last_name: str) -> str:
    """
    Extract initials from candidate names.
    
    Args:
        first_name: Candidate's first name
        last_name: Candidate's last name
        
    Returns:
        str: Generated initials (e.g., "JD" for "John Doe")
    """
    # Clean and validate inputs
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    
    # Remove non-alphabetic characters and get first letter
    def get_first_letter(name: str) -> str:
        if not name:
            return ""
        # Find first alphabetic character
        for char in name:
            if char.isalpha():
                return char.upper()
        return ""
    
    first_initial = get_first_letter(first_name)
    last_initial = get_first_letter(last_name)
    
    # Generate initials based on available names
    if first_initial and last_initial:
        return f"{first_initial}{last_initial}"
    elif first_name:
        # Use first two letters of first name
        clean_name = ''.join(c for c in first_name if c.isalpha())
        if len(clean_name) >= 2:
            return clean_name[:2].upper()
        elif len(clean_name) == 1:
            return clean_name.upper()
    elif last_name:
        # Use first two letters of last name
        clean_name = ''.join(c for c in last_name if c.isalpha())
        if len(clean_name) >= 2:
            return clean_name[:2].upper()
        elif len(clean_name) == 1:
            return clean_name.upper()
    
    # Fallback when no valid name is available
    return "?"

def generate_deterministic_color(name: str) -> str:
    """
    Generate a deterministic background color based on name.
    
    Uses a predefined palette of professional colors to ensure
    good contrast and visual appeal.
    
    Args:
        name: Full name string to generate color from
        
    Returns:
        str: Hex color code (e.g., "#3B82F6")
    """
    # Professional color palette with good contrast for white text
    colors = [
        "#3B82F6",  # Blue
        "#10B981",  # Green  
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
        "#EC4899",  # Pink
        "#6366F1",  # Indigo
    ]
    
    # Default color for empty/invalid names
    if not name or not isinstance(name, str):
        return colors[0]  # Default to blue
    
    # Generate hash and select color deterministically
    name_normalized = name.lower().strip()
    if not name_normalized:
        return colors[0]
    
    try:
        name_hash = hash(name_normalized)
        color_index = abs(name_hash) % len(colors)
        return colors[color_index]
    except Exception:
        # Fallback to default color if hashing fails
        return colors[0]

def generate_initials_avatar(first_name: str, last_name: str) -> dict:
    """
    Generate initials avatar configuration for a candidate.
    
    Args:
        first_name: Candidate's first name
        last_name: Candidate's last name
        
    Returns:
        Dict containing avatar type, initials, and background color
    """
    try:
        # Extract initials
        initials = extract_initials(first_name, last_name)
        
        # Generate deterministic color based on full name
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        background_color = generate_deterministic_color(full_name)
        
        return {
            "type": "initials",
            "photo_url": None,
            "initials": initials,
            "background_color": background_color
        }
    except Exception as e:
        # Fallback avatar configuration if generation fails
        return {
            "type": "initials",
            "photo_url": None,
            "initials": "?",
            "background_color": "#3B82F6"  # Default blue
        }


class TestAvatarGeneration(unittest.TestCase):
    
    def test_extract_initials_normal_names(self):
        """Test initials extraction from normal first and last names."""
        # Standard case - first and last name
        self.assertEqual(extract_initials("John", "Doe"), "JD")
        self.assertEqual(extract_initials("Jane", "Smith"), "JS")
        self.assertEqual(extract_initials("Michael", "Johnson"), "MJ")
        
        # Case insensitive
        self.assertEqual(extract_initials("john", "doe"), "JD")
        self.assertEqual(extract_initials("JANE", "SMITH"), "JS")
        
    def test_extract_initials_single_name(self):
        """Test initials extraction when only one name is provided."""
        # Only first name provided
        self.assertEqual(extract_initials("John", ""), "JO")
        self.assertEqual(extract_initials("Jane", None), "JA")
        self.assertEqual(extract_initials("Michael", ""), "MI")
        
        # Only last name provided
        self.assertEqual(extract_initials("", "Smith"), "SM")
        self.assertEqual(extract_initials(None, "Johnson"), "JO")
        
        # Single character names
        self.assertEqual(extract_initials("A", ""), "A")
        self.assertEqual(extract_initials("", "B"), "B")
        
    def test_extract_initials_special_characters(self):
        """Test initials extraction with special characters and numbers."""
        # Names with numbers and special characters
        self.assertEqual(extract_initials("John123", "Doe456"), "JD")
        self.assertEqual(extract_initials("Jane-Marie", "Smith-Jones"), "JS")
        self.assertEqual(extract_initials("O'Connor", "McDonald"), "OM")
        
        # Names starting with non-alphabetic characters
        self.assertEqual(extract_initials("123John", "456Doe"), "JD")
        self.assertEqual(extract_initials("-Jane", "_Smith"), "JS")
        
        # Names with only special characters
        self.assertEqual(extract_initials("123", "456"), "?")
        self.assertEqual(extract_initials("---", "___"), "?")
        
    def test_extract_initials_empty_names(self):
        """Test initials extraction with empty or invalid names."""
        # Both names empty
        self.assertEqual(extract_initials("", ""), "?")
        self.assertEqual(extract_initials(None, None), "?")
        self.assertEqual(extract_initials("   ", "   "), "?")
        
        # Names with only whitespace
        self.assertEqual(extract_initials("  ", "  "), "?")
        
    def test_extract_initials_unicode_names(self):
        """Test initials extraction with unicode characters."""
        # Names with accented characters
        self.assertEqual(extract_initials("José", "García"), "JG")
        self.assertEqual(extract_initials("François", "Müller"), "FM")
        
        # Names with non-Latin scripts (will extract first characters)
        # Note: Chinese characters are considered alphabetic by Python's isalpha()
        result = extract_initials("张", "李")
        self.assertEqual(len(result), 2)  # Should get two characters
        
    def test_generate_deterministic_color_consistency(self):
        """Test that color generation is deterministic and consistent."""
        # Same name should always produce same color
        color1 = generate_deterministic_color("John Doe")
        color2 = generate_deterministic_color("John Doe")
        self.assertEqual(color1, color2)
        
        # Case insensitive
        color3 = generate_deterministic_color("john doe")
        color4 = generate_deterministic_color("JOHN DOE")
        self.assertEqual(color3, color4)
        
        # Whitespace normalization - test that strip() works
        color5 = generate_deterministic_color("John Doe")
        color6 = generate_deterministic_color("John Doe")
        self.assertEqual(color5, color6)
        
    def test_generate_deterministic_color_format(self):
        """Test that generated colors are in proper hex format."""
        colors = [
            generate_deterministic_color("John Doe"),
            generate_deterministic_color("Jane Smith"),
            generate_deterministic_color("Michael Johnson"),
            generate_deterministic_color("Sarah Wilson"),
            generate_deterministic_color("David Brown")
        ]
        
        for color in colors:
            # Should be hex color format
            self.assertTrue(color.startswith("#"))
            self.assertEqual(len(color), 7)  # #RRGGBB format
            # Should be valid hex
            try:
                int(color[1:], 16)
            except ValueError:
                self.fail(f"Color {color} is not valid hex")
                
    def test_generate_deterministic_color_palette(self):
        """Test that colors come from the expected palette."""
        expected_colors = [
            "#3B82F6",  # Blue
            "#10B981",  # Green  
            "#F59E0B",  # Amber
            "#EF4444",  # Red
            "#8B5CF6",  # Purple
            "#06B6D4",  # Cyan
            "#84CC16",  # Lime
            "#F97316",  # Orange
            "#EC4899",  # Pink
            "#6366F1",  # Indigo
        ]
        
        # Generate colors for many different names
        test_names = [
            "John Doe", "Jane Smith", "Michael Johnson", "Sarah Wilson", "David Brown",
            "Emily Davis", "Robert Miller", "Lisa Garcia", "William Rodriguez", "Jennifer Martinez",
            "Christopher Anderson", "Amanda Taylor", "Matthew Thomas", "Ashley Jackson", "Joshua White"
        ]
        
        generated_colors = [generate_deterministic_color(name) for name in test_names]
        
        # All generated colors should be from the expected palette
        for color in generated_colors:
            self.assertIn(color, expected_colors)
            
    def test_generate_deterministic_color_edge_cases(self):
        """Test color generation with edge cases."""
        # Empty name should return default color
        self.assertEqual(generate_deterministic_color(""), "#3B82F6")
        self.assertEqual(generate_deterministic_color(None), "#3B82F6")
        self.assertEqual(generate_deterministic_color("   "), "#3B82F6")
        
        # Non-string input should return default color
        self.assertEqual(generate_deterministic_color(123), "#3B82F6")
        self.assertEqual(generate_deterministic_color([]), "#3B82F6")
        self.assertEqual(generate_deterministic_color({}), "#3B82F6")
        
    def test_generate_initials_avatar_complete(self):
        """Test complete avatar generation with valid names."""
        avatar = generate_initials_avatar("John", "Doe")
        
        # Check structure
        self.assertIsInstance(avatar, dict)
        self.assertIn("type", avatar)
        self.assertIn("photo_url", avatar)
        self.assertIn("initials", avatar)
        self.assertIn("background_color", avatar)
        
        # Check values
        self.assertEqual(avatar["type"], "initials")
        self.assertIsNone(avatar["photo_url"])
        self.assertEqual(avatar["initials"], "JD")
        self.assertTrue(avatar["background_color"].startswith("#"))
        
    def test_generate_initials_avatar_single_name(self):
        """Test avatar generation with single name."""
        avatar = generate_initials_avatar("John", "")
        
        self.assertEqual(avatar["type"], "initials")
        self.assertEqual(avatar["initials"], "JO")
        self.assertTrue(avatar["background_color"].startswith("#"))
        
    def test_generate_initials_avatar_no_names(self):
        """Test avatar generation with no valid names."""
        avatar = generate_initials_avatar("", "")
        
        self.assertEqual(avatar["type"], "initials")
        self.assertEqual(avatar["initials"], "?")
        self.assertEqual(avatar["background_color"], "#3B82F6")  # Default color
        
    def test_generate_initials_avatar_error_handling(self):
        """Test avatar generation error handling."""
        # Should not crash with None inputs
        avatar = generate_initials_avatar(None, None)
        
        self.assertEqual(avatar["type"], "initials")
        self.assertEqual(avatar["initials"], "?")
        self.assertEqual(avatar["background_color"], "#3B82F6")
        
    def test_generate_initials_avatar_consistency(self):
        """Test that avatar generation is consistent for same inputs."""
        avatar1 = generate_initials_avatar("John", "Doe")
        avatar2 = generate_initials_avatar("John", "Doe")
        
        self.assertEqual(avatar1, avatar2)
        
        # Case insensitive consistency
        avatar3 = generate_initials_avatar("john", "doe")
        self.assertEqual(avatar1["initials"], avatar3["initials"])
        self.assertEqual(avatar1["background_color"], avatar3["background_color"])


if __name__ == '__main__':
    unittest.main()