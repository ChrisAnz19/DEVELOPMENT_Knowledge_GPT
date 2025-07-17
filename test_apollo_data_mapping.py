#!/usr/bin/env python3
"""
Test Apollo API data mapping for LinkedIn URL and company name
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import json
import asyncio

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from apollo_api_call import search_people_via_internal_database

class TestApolloDataMapping(unittest.TestCase):
    
    @patch('apollo_api_call.httpx.AsyncClient')
    @patch('apollo_api_call.INTERNAL_DATABASE_API_KEY', 'test-api-key')
    def test_apollo_extracts_company_and_linkedin_url(self, mock_client_class):
        """Test that Apollo API correctly extracts company name and LinkedIn URL"""
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock the search response
        search_response = MagicMock()
        search_response.json.return_value = {
            "people": [
                {
                    "id": "apollo-123",
                    "name": "John Doe"
                }
            ]
        }
        
        # Mock the enrichment response with nested organization data
        enrich_response = MagicMock()
        enrich_response.json.return_value = {
            "person": {
                "id": "apollo-123",
                "name": "John Doe",
                "title": "Senior Director of Commercial Sales",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "organization": {
                    "name": "TechCorp Inc",  # This should be extracted to company field
                    "website_url": "https://techcorp.com"
                },
                "email": "john.doe@techcorp.com",
                "profile_picture_url": "https://example.com/photo.jpg",
                "city": "San Francisco",
                "state": "CA"
            }
        }
        
        # Set up the mock client to return our responses
        mock_client.post.side_effect = [search_response, enrich_response]
        
        # Run the async function
        filters = {"person_filters": {"titles": ["Director"]}}
        result = asyncio.run(search_people_via_internal_database(filters, per_page=1))
        
        # Verify the result
        self.assertEqual(len(result), 1)
        person = result[0]
        
        # Check that company name was extracted from organization.name
        self.assertIn('company', person)
        self.assertEqual(person['company'], 'TechCorp Inc')
        
        # Check that LinkedIn URL is present
        self.assertIn('linkedin_url', person)
        self.assertEqual(person['linkedin_url'], 'https://linkedin.com/in/johndoe')
        
        # Check that profile photo URL is present
        self.assertIn('profile_photo_url', person)
        self.assertEqual(person['profile_photo_url'], 'https://example.com/photo.jpg')
    
    @patch('apollo_api_call.httpx.AsyncClient')
    @patch('apollo_api_call.INTERNAL_DATABASE_API_KEY', 'test-api-key')
    def test_apollo_handles_string_organization(self, mock_client_class):
        """Test that Apollo API handles organization as a string"""
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock the search response
        search_response = MagicMock()
        search_response.json.return_value = {
            "people": [{"id": "apollo-456", "name": "Jane Smith"}]
        }
        
        # Mock the enrichment response with organization as string
        enrich_response = MagicMock()
        enrich_response.json.return_value = {
            "person": {
                "id": "apollo-456",
                "name": "Jane Smith",
                "title": "VP of Sales",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "organization": "Software Inc",  # Organization as string
                "email": "jane@software.com"
            }
        }
        
        # Set up the mock client to return our responses
        mock_client.post.side_effect = [search_response, enrich_response]
        
        # Run the async function
        filters = {"person_filters": {"titles": ["VP"]}}
        result = asyncio.run(search_people_via_internal_database(filters, per_page=1))
        
        # Verify the result
        self.assertEqual(len(result), 1)
        person = result[0]
        
        # Check that company name was extracted from string organization
        self.assertIn('company', person)
        self.assertEqual(person['company'], 'Software Inc')
        
        # Check that LinkedIn URL is present
        self.assertIn('linkedin_url', person)
        self.assertEqual(person['linkedin_url'], 'https://linkedin.com/in/janesmith')
    
    @patch('apollo_api_call.httpx.AsyncClient')
    @patch('apollo_api_call.INTERNAL_DATABASE_API_KEY', 'test-api-key')
    def test_apollo_fixes_linkedin_url_format(self, mock_client_class):
        """Test that Apollo API fixes LinkedIn URL format if missing https://"""
        
        # Mock the HTTP client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Mock the search response
        search_response = MagicMock()
        search_response.json.return_value = {
            "people": [{"id": "apollo-789", "name": "Bob Johnson"}]
        }
        
        # Mock the enrichment response with malformed LinkedIn URL
        enrich_response = MagicMock()
        enrich_response.json.return_value = {
            "person": {
                "id": "apollo-789",
                "name": "Bob Johnson",
                "title": "Sales Manager",
                "linkedin_url": "linkedin.com/in/bobjohnson",  # Missing https://
                "organization": {"name": "Cloud Systems"},
                "email": "bob@cloud.com"
            }
        }
        
        # Set up the mock client to return our responses
        mock_client.post.side_effect = [search_response, enrich_response]
        
        # Run the async function
        filters = {"person_filters": {"titles": ["Manager"]}}
        result = asyncio.run(search_people_via_internal_database(filters, per_page=1))
        
        # Verify the result
        self.assertEqual(len(result), 1)
        person = result[0]
        
        # Check that LinkedIn URL was fixed to include https://
        self.assertIn('linkedin_url', person)
        self.assertEqual(person['linkedin_url'], 'https://linkedin.com/in/bobjohnson')
        
        # Check that company name was extracted
        self.assertIn('company', person)
        self.assertEqual(person['company'], 'Cloud Systems')

if __name__ == "__main__":
    unittest.main()