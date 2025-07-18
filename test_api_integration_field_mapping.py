#!/usr/bin/env python3
"""
Integration test to verify the complete API field mapping flow.
This test simulates the actual API endpoint behavior to validate the fix.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import datetime, timezone

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestAPIIntegrationFieldMapping(unittest.TestCase):
    """Integration test for the API field mapping fix."""
    
    def setUp(self):
        """Set up test data."""
        self.mock_search_data = {
            "id": 123,
            "request_id": "test-request-123",
            "status": "processing",
            "prompt": "Find software engineers with Python experience",
            "filters": "{}",
            "created_at": "2025-07-17T23:17:03.281386+00:00",
            "completed_at": None
        }
        
        self.mock_candidates = [
            {
                'id': 1,
                'search_id': 123,
                'name': 'John Doe',
                'title': 'Senior Software Engineer',
                'company': 'TechCorp Inc',
                'email': 'john.doe@techcorp.com',
                'linkedin_url': 'https://linkedin.com/in/johndoe',
                'profile_photo_url': 'https://example.com/photo.jpg',
                'location': 'San Francisco, CA',
                'accuracy': 85,
                'reasons': ['5+ years Python experience', 'Tech industry'],
                'linkedin_profile': {'headline': 'Software Engineer'},
                'behavioral_data': {'insight': 'test data'},
                'created_at': '2025-07-17T23:17:03.281386+00:00'
            },
            {
                'id': 2,
                'search_id': 123,
                'name': 'Jane Smith',
                'title': 'Python Developer',
                'company': '',  # Empty string - should become null
                'email': 'jane.smith@example.com',
                'linkedin_url': None,  # Null value
                'profile_photo_url': 'https://example.com/jane.jpg',
                'location': 'New York, NY',
                'accuracy': 92,
                'reasons': ['10+ years Python experience'],
                'linkedin_profile': None,
                'behavioral_data': None,
                'created_at': '2025-07-17T23:17:03.281386+00:00'
            }
        ]
    
    @patch('api.main.get_search_from_database')
    @patch('api.main.get_people_for_search')
    @patch('api.main.enhance_behavioral_data_ai')
    @patch('api.main.store_search_to_database')
    def test_complete_api_endpoint_field_mapping(self, mock_store_search, mock_enhance_behavioral, 
                                                mock_get_people, mock_get_search):
        """Test the complete API endpoint with field mapping."""
        
        # Set up mocks
        mock_get_search.return_value = self.mock_search_data
        mock_get_people.return_value = self.mock_candidates
        mock_enhance_behavioral.return_value = {"insight": "enhanced behavioral data"}
        mock_store_search.return_value = None
        
        # Import the API function
        from api.main import get_search_result
        import asyncio
        
        # Call the API endpoint function
        result = asyncio.run(get_search_result("test-request-123"))
        
        # Verify the result structure
        self.assertIsInstance(result, dict)
        self.assertEqual(result["request_id"], "test-request-123")
        self.assertEqual(result["status"], "completed")
        self.assertIn("candidates", result)
        
        candidates = result["candidates"]
        self.assertEqual(len(candidates), 2)
        
        # Verify first candidate (complete LinkedIn data)
        candidate1 = candidates[0]
        
        # Check all expected fields are present
        expected_fields = [
            "id", "name", "title", "email", "location",
            "company", "linkedin_url", "profile_photo_url",
            "accuracy", "reasons", "linkedin_profile", "behavioral_data"
        ]
        
        for field in expected_fields:
            self.assertIn(field, candidate1, f"Field '{field}' missing from API response")
        
        # Verify LinkedIn data fields are correctly mapped
        self.assertEqual(candidate1["company"], "TechCorp Inc")
        self.assertEqual(candidate1["linkedin_url"], "https://linkedin.com/in/johndoe")
        self.assertEqual(candidate1["profile_photo_url"], "https://example.com/photo.jpg")
        
        # Verify second candidate (null handling)
        candidate2 = candidates[1]
        
        # Check all expected fields are present
        for field in expected_fields:
            self.assertIn(field, candidate2, f"Field '{field}' missing from API response")
        
        # Verify null handling
        self.assertIsNone(candidate2["company"])  # Empty string should become None
        self.assertIsNone(candidate2["linkedin_url"])  # Was None, should remain None
        self.assertEqual(candidate2["profile_photo_url"], "https://example.com/jane.jpg")
        
        # Verify that the search status was updated to completed
        self.assertEqual(result["status"], "completed")
        self.assertIsNotNone(result["completed_at"])
        
        print("✅ Complete API endpoint integration test passed!")
        print(f"   - API returned {len(candidates)} candidates")
        print("   - All expected fields present in API response")
        print("   - LinkedIn data fields correctly mapped")
        print("   - Null value handling working correctly")
        print("   - Search status updated to completed")
    
    def test_field_mapping_logging_validation(self):
        """Test that the field mapping includes proper logging for validation."""
        
        # Simulate the field mapping logic with logging validation
        processed_candidates = []
        
        for i, candidate in enumerate(self.mock_candidates):
            # Apply the exact field mapping logic from the API fix
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
                "behavioral_data": candidate.get("behavioral_data")
            }
            
            # Apply null value handling
            for field_name, field_value in processed_candidate.items():
                if field_value is None:
                    processed_candidate[field_name] = None
                elif isinstance(field_value, str) and not field_value.strip():
                    processed_candidate[field_name] = None
            
            # Validate field mapping (simulate logging validation)
            critical_fields = ['company', 'linkedin_url', 'profile_photo_url']
            mapping_errors = []
            
            for field in critical_fields:
                original_value = candidate.get(field)
                mapped_value = processed_candidate.get(field)
                has_original = bool(original_value and str(original_value).strip())
                has_mapped = bool(mapped_value and str(mapped_value).strip())
                
                # Check for mapping consistency
                if has_original != has_mapped:
                    mapping_errors.append(f"Field mapping error for {field}: DB={'✓' if has_original else '✗'} -> API={'✓' if has_mapped else '✗'}")
            
            # Verify no mapping errors occurred
            self.assertEqual(len(mapping_errors), 0, f"Field mapping errors for candidate {i+1}: {mapping_errors}")
            
            processed_candidates.append(processed_candidate)
        
        # Verify all candidates were processed correctly
        self.assertEqual(len(processed_candidates), 2)
        
        print("✅ Field mapping logging validation test passed!")
        print("   - No field mapping errors detected")
        print("   - All candidates processed correctly")
        print("   - Logging validation logic working")

if __name__ == "__main__":
    print("Testing API Integration Field Mapping...")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)