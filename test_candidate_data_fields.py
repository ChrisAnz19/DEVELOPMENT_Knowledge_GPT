#!/usr/bin/env python3
"""
Test to verify candidate data fields in API response
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_people_for_search, store_people_to_database

class TestCandidateDataFields(unittest.TestCase):
    
    @patch('database.supabase')
    def test_get_people_includes_all_required_fields(self, mock_supabase):
        """Test that get_people_for_search returns all required fields"""
        # Mock the supabase response with complete candidate data
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        
        # Sample complete candidate data
        complete_candidate = {
            'id': 1,
            'search_id': 123,
            'name': 'John Doe',
            'title': 'Senior Director of Commercial Sales',
            'company': 'TechCorp Inc',  # This should be included
            'email': 'john.doe@techcorp.com',
            'linkedin_url': 'https://linkedin.com/in/johndoe',  # This should be included
            'profile_photo_url': 'https://example.com/photo.jpg',
            'location': 'San Francisco, CA',
            'accuracy': 85,
            'reasons': ['5+ years experience', 'Tech industry'],
            'linkedin_profile': {'headline': 'Sales Director'},
            'linkedin_posts': [],
            'behavioral_data': '{"insight": "test"}',
            'created_at': '2025-07-17T23:17:03.281386+00:00'
        }
        
        mock_table.execute.return_value = MagicMock(data=[complete_candidate])
        
        # Call the function
        result = get_people_for_search(123)
        
        # Verify the result includes all required fields
        self.assertEqual(len(result), 1)
        candidate = result[0]
        
        # Check that linkedin_url and company are present
        self.assertIn('linkedin_url', candidate)
        self.assertIn('company', candidate)
        self.assertEqual(candidate['linkedin_url'], 'https://linkedin.com/in/johndoe')
        self.assertEqual(candidate['company'], 'TechCorp Inc')
        
        # Verify the select query includes the required fields
        mock_table.select.assert_called_with(
            "id, search_id, name, title, company, email, linkedin_url, profile_photo_url, location, accuracy, reasons, linkedin_profile, linkedin_posts, behavioral_data, created_at"
        )
    
    @patch('database.supabase')
    def test_store_people_preserves_linkedin_url_and_company(self, mock_supabase):
        """Test that store_people_to_database preserves linkedin_url and company fields"""
        # Mock the supabase response
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = MagicMock()
        
        # Sample people data with linkedin_url and company
        people_data = [
            {
                'name': 'John Doe',
                'title': 'Senior Director of Commercial Sales',
                'company': 'TechCorp Inc',  # Should be preserved
                'email': 'john.doe@techcorp.com',
                'linkedin_url': 'https://linkedin.com/in/johndoe',  # Should be preserved
                'profile_photo_url': 'https://example.com/photo.jpg',
                'location': 'San Francisco, CA',
                'accuracy': 85,
                'reasons': ['5+ years experience'],
                'linkedin_profile': {'headline': 'Sales Director'},
                'behavioral_data': {'insight': 'test data'}
            }
        ]
        
        # Call the function
        store_people_to_database(123, people_data)
        
        # Verify supabase was called
        mock_supabase.table.assert_called_with("people")
        mock_table.insert.assert_called_once()
        
        # Get the actual data that was passed to insert
        inserted_data = mock_table.insert.call_args[0][0]
        self.assertEqual(len(inserted_data), 1)
        
        person = inserted_data[0]
        
        # Verify linkedin_url and company are preserved
        self.assertIn('linkedin_url', person)
        self.assertIn('company', person)
        self.assertEqual(person['linkedin_url'], 'https://linkedin.com/in/johndoe')
        self.assertEqual(person['company'], 'TechCorp Inc')
        self.assertEqual(person['search_id'], 123)
    
    def test_apollo_data_field_mapping(self):
        """Test that we understand the Apollo API field structure"""
        # This is what Apollo API typically returns
        apollo_person = {
            'id': 'apollo-123',
            'name': 'John Doe',
            'title': 'Senior Director of Commercial Sales',
            'linkedin_url': 'https://linkedin.com/in/johndoe',
            'organization': {
                'name': 'TechCorp Inc',  # Company name is nested in organization
                'website_url': 'https://techcorp.com'
            },
            'email': 'john.doe@techcorp.com',
            'profile_picture_url': 'https://example.com/photo.jpg',
            'city': 'San Francisco',
            'state': 'CA',
            'country': 'United States'
        }
        
        # We need to map organization.name to company field
        mapped_person = apollo_person.copy()
        if 'organization' in apollo_person and apollo_person['organization']:
            mapped_person['company'] = apollo_person['organization'].get('name', '')
        
        # Verify the mapping worked
        self.assertEqual(mapped_person['company'], 'TechCorp Inc')
        self.assertEqual(mapped_person['linkedin_url'], 'https://linkedin.com/in/johndoe')

if __name__ == "__main__":
    unittest.main()