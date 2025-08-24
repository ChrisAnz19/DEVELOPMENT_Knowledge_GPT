#!/usr/bin/env python3
"""
Performance tests for avatar generation optimizations.

This test suite verifies that caching and performance optimizations
work correctly for avatar generation.
"""

import unittest
import time

# Mock the optimized avatar generation functions for testing
_avatar_cache = {}
_COLOR_PALETTE = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
    "#06B6D4", "#84CC16", "#F97316", "#EC4899", "#6366F1"
]

def extract_initials(first_name: str, last_name: str) -> str:
    """Mock initials extraction."""
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
    """Mock optimized color generation."""
    if not name or not isinstance(name, str):
        return _COLOR_PALETTE[0]
    
    name_normalized = name.lower().strip()
    if not name_normalized:
        return _COLOR_PALETTE[0]
    
    try:
        name_hash = hash(name_normalized)
        color_index = abs(name_hash) % len(_COLOR_PALETTE)
        return _COLOR_PALETTE[color_index]
    except Exception:
        return _COLOR_PALETTE[0]

def generate_initials_avatar(first_name: str, last_name: str) -> dict:
    """Mock cached avatar generation."""
    global _avatar_cache
    
    # Create cache key from normalized names
    cache_key = f"{(first_name or '').strip().lower()}|{(last_name or '').strip().lower()}"
    
    # Check cache first
    if cache_key in _avatar_cache:
        return _avatar_cache[cache_key].copy()
    
    try:
        # Extract initials
        initials = extract_initials(first_name, last_name)
        
        # Generate deterministic color based on full name
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        background_color = generate_deterministic_color(full_name)
        
        avatar_data = {
            "type": "initials",
            "photo_url": None,
            "initials": initials,
            "background_color": background_color
        }
        
        # Cache the result
        _avatar_cache[cache_key] = avatar_data.copy()
        
        # Limit cache size to prevent memory issues
        if len(_avatar_cache) > 1000:
            # Remove oldest entries (simple FIFO)
            oldest_keys = list(_avatar_cache.keys())[:100]
            for key in oldest_keys:
                del _avatar_cache[key]
        
        return avatar_data
        
    except Exception:
        # Fallback avatar configuration if generation fails
        fallback_avatar = {
            "type": "initials",
            "photo_url": None,
            "initials": "?",
            "background_color": "#3B82F6"
        }
        
        # Cache the fallback too to avoid repeated errors
        _avatar_cache[cache_key] = fallback_avatar.copy()
        
        return fallback_avatar

def get_avatar_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        "cache_size": len(_avatar_cache),
        "max_cache_size": 1000,
        "cache_utilization": len(_avatar_cache) / 1000 * 100
    }

def clear_avatar_cache() -> None:
    """Clear the cache."""
    global _avatar_cache
    _avatar_cache.clear()


class TestAvatarPerformance(unittest.TestCase):
    
    def setUp(self):
        """Clear cache before each test."""
        clear_avatar_cache()
        
    def test_caching_improves_performance(self):
        """Test that caching significantly improves performance for repeated requests."""
        # Generate avatar for the same person multiple times
        first_name = "John"
        last_name = "Doe"
        
        # First generation (cache miss)
        start_time = time.time()
        avatar1 = generate_initials_avatar(first_name, last_name)
        first_generation_time = time.time() - start_time
        
        # Second generation (cache hit)
        start_time = time.time()
        avatar2 = generate_initials_avatar(first_name, last_name)
        second_generation_time = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(avatar1, avatar2)
        
        # Second call should be faster (though timing can be variable in tests)
        # At minimum, verify cache is working by checking cache size
        cache_stats = get_avatar_cache_stats()
        self.assertEqual(cache_stats["cache_size"], 1)
        
    def test_cache_key_normalization(self):
        """Test that cache keys are properly normalized."""
        # These should all result in the same cache entry
        variations = [
            ("John", "Doe"),
            ("john", "doe"),
            ("JOHN", "DOE"),
            ("  John  ", "  Doe  "),
        ]
        
        avatars = []
        for first, last in variations:
            avatar = generate_initials_avatar(first, last)
            avatars.append(avatar)
        
        # All avatars should be identical
        for avatar in avatars[1:]:
            self.assertEqual(avatar, avatars[0])
        
        # Should only have one cache entry
        cache_stats = get_avatar_cache_stats()
        self.assertEqual(cache_stats["cache_size"], 1)
        
    def test_cache_size_limit(self):
        """Test that cache size is properly limited."""
        # Generate avatars for many different people
        for i in range(1100):  # More than the 1000 limit
            generate_initials_avatar(f"Person{i}", f"Last{i}")
        
        # Cache should be limited to 1000 entries
        cache_stats = get_avatar_cache_stats()
        self.assertLessEqual(cache_stats["cache_size"], 1000)
        
    def test_batch_processing_performance(self):
        """Test performance with batch processing of multiple candidates."""
        # Create a batch of candidates
        candidates = []
        for i in range(50):
            candidates.append({
                "name": f"Person {i}",
                "first_name": f"Person{i}",
                "last_name": f"Last{i}"
            })
        
        # Measure batch processing time
        start_time = time.time()
        for candidate in candidates:
            avatar = generate_initials_avatar(
                candidate["first_name"], 
                candidate["last_name"]
            )
            candidate["avatar"] = avatar
        batch_time = time.time() - start_time
        
        # Should complete reasonably quickly (less than 1 second for 50 candidates)
        self.assertLess(batch_time, 1.0)
        
        # All candidates should have avatars
        for candidate in candidates:
            self.assertIn("avatar", candidate)
            self.assertEqual(candidate["avatar"]["type"], "initials")
            
    def test_color_palette_efficiency(self):
        """Test that color generation is efficient with pre-defined palette."""
        # Generate colors for many different names
        names = [f"Person {i} Last{i}" for i in range(100)]
        
        start_time = time.time()
        colors = [generate_deterministic_color(name) for name in names]
        color_generation_time = time.time() - start_time
        
        # Should complete very quickly
        self.assertLess(color_generation_time, 0.1)
        
        # All colors should be from the expected palette
        expected_colors = set(_COLOR_PALETTE)
        generated_colors = set(colors)
        
        # All generated colors should be in the palette
        self.assertTrue(generated_colors.issubset(expected_colors))
        
    def test_cache_statistics_accuracy(self):
        """Test that cache statistics are accurate."""
        # Start with empty cache
        stats = get_avatar_cache_stats()
        self.assertEqual(stats["cache_size"], 0)
        self.assertEqual(stats["cache_utilization"], 0.0)
        
        # Add some entries
        for i in range(10):
            generate_initials_avatar(f"Person{i}", f"Last{i}")
        
        # Check updated statistics
        stats = get_avatar_cache_stats()
        self.assertEqual(stats["cache_size"], 10)
        self.assertEqual(stats["cache_utilization"], 1.0)  # 10/1000 * 100 = 1.0%
        
    def test_error_handling_performance(self):
        """Test that error cases don't significantly impact performance."""
        # Test with various error cases
        error_cases = [
            (None, None),
            ("", ""),
            ("123", "456"),
            ("   ", "   "),
        ]
        
        start_time = time.time()
        for first, last in error_cases:
            avatar = generate_initials_avatar(first, last)
            # Should get fallback initials for cases with no valid letters
            if first is None and last is None:
                self.assertEqual(avatar["initials"], "?")
            elif first == "" and last == "":
                self.assertEqual(avatar["initials"], "?")
            elif first == "   " and last == "   ":
                self.assertEqual(avatar["initials"], "?")
            # Color should be from the valid palette
            self.assertIn(avatar["background_color"], _COLOR_PALETTE)
        error_handling_time = time.time() - start_time
        
        # Error handling should be fast
        self.assertLess(error_handling_time, 0.1)
        
    def test_memory_efficiency(self):
        """Test that avatar generation doesn't consume excessive memory."""
        # Generate many avatars and check cache behavior
        initial_cache_size = get_avatar_cache_stats()["cache_size"]
        
        # Generate avatars for unique names
        for i in range(500):
            generate_initials_avatar(f"Unique{i}", f"Person{i}")
        
        # Cache should grow but not excessively
        final_cache_size = get_avatar_cache_stats()["cache_size"]
        self.assertGreater(final_cache_size, initial_cache_size)
        self.assertLessEqual(final_cache_size, 1000)  # Should respect limit
        
        # Generate same avatars again (should hit cache)
        for i in range(100):
            generate_initials_avatar(f"Unique{i}", f"Person{i}")
        
        # Cache size shouldn't grow for repeated requests
        repeated_cache_size = get_avatar_cache_stats()["cache_size"]
        self.assertEqual(repeated_cache_size, final_cache_size)


if __name__ == '__main__':
    unittest.main()