#!/usr/bin/env python3
"""
Test the fixes for async/await usage in the codebase.
"""

import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os
import json
from datetime import datetime, timezone

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed modules
from api.main_fixed_async import process_search, extract_profile_photo_url

class AsyncTestCase(unittest.TestCase):
    """Base class for async test cases."""
    
    def run_async(self, coro):
        """Run an async coroutine in the event loop."""
        return asyncio.run(coro)

class TestAsyncAwaitFixes(AsyncTestCase):
    """Test the fixes for async/await usage."""

    @patch('api.main_fixed_async.get_search_from_database')
    @patch('api.main_fixed_async.store_search_to_database')
    @patch('api.main_fixed_async.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_async.search_people_via_internal_database')
    async def test_process_search_async_flow(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test the async flow of process_search."""
        # Setup mock responses
        mock_get_search.return_value = {
            "id": 1,
            "request_id": "test-request-id",
            "status": "processing",
            "prompt": "test prompt",
            "filters": "{}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        mock_parse_prompt.return_value = {"industry": "Technology"}
        
        # Setup AsyncMock for search_people_via_internal_database
        mock_search_people.return_value = [
            {"name": "Test Person 1", "linkedin_url": "https://linkedin.com/in/testperson1"},
            {"name": "Test Person 2", "linkedin_url": "https://linkedin.com/in/testperson2"}
        ]
        
        # Run the process_search function
        await process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=False  # Skip LinkedIn scraping for this test
        )
        
        # Verify that search_people_via_internal_database was called with the correct arguments
        mock_search_people.assert_called_once_with({"industry": "Technology"}, 2)
        
        # Verify that store_search_to_database was called
        mock_store_search.assert_called()

    @patch('api.main_fixed_async.get_search_from_database')
    @patch('api.main_fixed_async.store_search_to_database')
    @patch('api.main_fixed_async.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_async.search_people_via_internal_database')
    @patch('api.main_fixed_async.async_scrape_linkedin_profiles')
    async def test_process_search_with_linkedin_scraping(
        self, mock_scrape_linkedin, mock_search_people, mock_parse_prompt, 
        mock_store_search, mock_get_search
    ):
        """Test process_search with LinkedIn scraping."""
        # Setup mock responses
        mock_get_search.return_value = {
            "id": 1,
            "request_id": "test-request-id",
            "status": "processing",
            "prompt": "test prompt",
            "filters": "{}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        mock_parse_prompt.return_value = {"industry": "Technology"}
        
        # Setup AsyncMock for search_people_via_internal_database
        mock_search_people.return_value = [
            {"name": "Test Person 1", "linkedin_url": "https://linkedin.com/in/testperson1"},
            {"name": "Test Person 2", "linkedin_url": "https://linkedin.com/in/testperson2"}
        ]
        
        # Setup AsyncMock for async_scrape_linkedin_profiles
        mock_scrape_linkedin.return_value = [
            {"linkedin_url": "https://linkedin.com/in/testperson1", "headline": "Test Headline 1"},
            {"linkedin_url": "https://linkedin.com/in/testperson2", "headline": "Test Headline 2"}
        ]
        
        # Run the process_search function
        await process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        )
        
        # Verify that async_scrape_linkedin_profiles was called with the correct arguments
        mock_scrape_linkedin.assert_called_once_with(
            ["https://linkedin.com/in/testperson1", "https://linkedin.com/in/testperson2"]
        )
        
        # Verify that store_search_to_database was called
        mock_store_search.assert_called()

    @patch('api.main_fixed_async.get_search_from_database')
    @patch('api.main_fixed_async.store_search_to_database')
    @patch('api.main_fixed_async.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_async.search_people_via_internal_database')
    async def test_process_search_with_empty_results(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test process_search with empty search results."""
        # Setup mock responses
        mock_get_search.return_value = {
            "id": 1,
            "request_id": "test-request-id",
            "status": "processing",
            "prompt": "test prompt",
            "filters": "{}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        mock_parse_prompt.return_value = {"industry": "Technology"}
        
        # Setup AsyncMock for search_people_via_internal_database to return empty list
        mock_search_people.return_value = []
        
        # Run the process_search function
        await process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        )
        
        # Verify that store_search_to_database was called with status="completed"
        completed_calls = [
            call for call in mock_store_search.call_args_list 
            if call.args and isinstance(call.args[0], dict) and call.args[0].get("status") == "completed"
        ]
        self.assertGreaterEqual(len(completed_calls), 1, "store_search_to_database should be called with status='completed'")

    @patch('api.main_fixed_async.get_search_from_database')
    @patch('api.main_fixed_async.store_search_to_database')
    @patch('api.main_fixed_async.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_async.search_people_via_internal_database')
    async def test_process_search_with_asyncio_timeout(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test process_search with asyncio.TimeoutError."""
        # Setup mock responses
        mock_get_search.return_value = {
            "id": 1,
            "request_id": "test-request-id",
            "status": "processing",
            "prompt": "test prompt",
            "filters": "{}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None
        }
        
        mock_parse_prompt.return_value = {"industry": "Technology"}
        
        # Setup AsyncMock for search_people_via_internal_database to raise TimeoutError
        mock_search_people.side_effect = asyncio.TimeoutError("Search timeout")
        
        # Run the process_search function
        await process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        )
        
        # Verify that store_search_to_database was called with status="failed"
        failed_calls = [
            call for call in mock_store_search.call_args_list 
            if call.args and isinstance(call.args[0], dict) and call.args[0].get("status") == "failed"
        ]
        self.assertGreaterEqual(len(failed_calls), 1, "store_search_to_database should be called with status='failed'")

    def test_extract_profile_photo_url(self):
        """Test the extract_profile_photo_url function."""
        # Test with LinkedIn profile data
        linkedin_profile = {
            "profile_photo_url": "https://example.com/photo.jpg"
        }
        candidate_data = {
            "name": "Test Person"
        }
        result = extract_profile_photo_url(candidate_data, linkedin_profile)
        self.assertEqual(result, "https://example.com/photo.jpg")
        
        # Test with candidate data only
        candidate_data = {
            "name": "Test Person",
            "profile_photo_url": "https://example.com/photo2.jpg"
        }
        result = extract_profile_photo_url(candidate_data)
        self.assertEqual(result, "https://example.com/photo2.jpg")
        
        # Test with organization logo as fallback
        candidate_data = {
            "name": "Test Person",
            "organization": {
                "logo_url": "https://example.com/logo.jpg"
            }
        }
        result = extract_profile_photo_url(candidate_data)
        self.assertEqual(result, "https://example.com/logo.jpg")
        
        # Test with invalid URL
        candidate_data = {
            "name": "Test Person",
            "profile_photo_url": "not-a-url"
        }
        result = extract_profile_photo_url(candidate_data)
        self.assertIsNone(result)
        
        # Test with empty data
        result = extract_profile_photo_url({})
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()