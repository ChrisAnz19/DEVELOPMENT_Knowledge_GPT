import asyncio
import unittest
from unittest.mock import patch, MagicMock, AsyncMock, call
import sys
import os
import json
import time
from datetime import datetime, timezone

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the fixed module
from api.main_fixed_infinite_loop import process_search

class TestInfiniteLoopFix(unittest.TestCase):
    """Test the fixes for the infinite loop in search processing."""
    
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
    def tearDown(self):
        self.loop.close()

    @patch('api.main_fixed_infinite_loop.get_search_from_database')
    @patch('api.main_fixed_infinite_loop.store_search_to_database')
    @patch('api.main_fixed_infinite_loop.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_infinite_loop.search_people_via_internal_database')
    @patch('api.main_fixed_infinite_loop.async_scrape_linkedin_profiles')
    @patch('api.main_fixed_infinite_loop.select_top_candidates')
    @patch('api.main_fixed_infinite_loop.enhance_behavioral_data_ai')
    @patch('api.main_fixed_infinite_loop.store_people_to_database')
    def test_process_search_normal_flow(
        self, mock_store_people, mock_enhance_data, mock_select_candidates, 
        mock_scrape_linkedin, mock_search_people, mock_parse_prompt, 
        mock_store_search, mock_get_search
    ):
        """Test the normal flow of process_search without infinite loops."""
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
        
        mock_select_candidates.return_value = [
            {"name": "Test Person 1", "linkedin_url": "https://linkedin.com/in/testperson1"},
            {"name": "Test Person 2", "linkedin_url": "https://linkedin.com/in/testperson2"}
        ]
        
        mock_enhance_data.return_value = {
            "behavioral_insight": "Test insight",
            "scores": {
                "cmi": {"score": 70, "explanation": "Test explanation"},
                "rbfs": {"score": 65, "explanation": "Test explanation"},
                "ias": {"score": 75, "explanation": "Test explanation"}
            }
        }
        
        mock_store_search.return_value = True
        mock_store_people.return_value = True
        
        # Run the process_search function
        self.loop.run_until_complete(process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        ))
        
        # Verify that store_search_to_database was called exactly once with status="completed"
        completed_calls = [
            call for call in mock_store_search.call_args_list 
            if call.args and isinstance(call.args[0], dict) and call.args[0].get("status") == "completed"
        ]
        self.assertEqual(len(completed_calls), 1, "store_search_to_database should be called exactly once with status='completed'")
        
        # Verify that store_people_to_database was called exactly once
        self.assertEqual(mock_store_people.call_count, 1, "store_people_to_database should be called exactly once")

    @patch('api.main_fixed_infinite_loop.get_search_from_database')
    @patch('api.main_fixed_infinite_loop.store_search_to_database')
    @patch('api.main_fixed_infinite_loop.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_infinite_loop.search_people_via_internal_database')
    def test_process_search_already_completed(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test that process_search doesn't reprocess already completed searches."""
        # Setup mock responses for a completed search
        mock_get_search.return_value = {
            "id": 1,
            "request_id": "test-request-id",
            "status": "completed",
            "prompt": "test prompt",
            "filters": "{}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Run the process_search function
        self.loop.run_until_complete(process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        ))
        
        # Verify that search_people_via_internal_database was not called
        mock_search_people.assert_not_called()
        
        # Verify that store_search_to_database was not called
        mock_store_search.assert_not_called()

    @patch('api.main_fixed_infinite_loop.get_search_from_database')
    @patch('api.main_fixed_infinite_loop.store_search_to_database')
    @patch('api.main_fixed_infinite_loop.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_infinite_loop.search_people_via_internal_database')
    def test_process_search_with_timeout(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test that process_search handles timeouts properly."""
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
        
        # Setup AsyncMock for search_people_via_internal_database to simulate a timeout
        mock_search_people.side_effect = asyncio.TimeoutError("Search timeout")
        
        # Run the process_search function
        self.loop.run_until_complete(process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        ))
        
        # Verify that store_search_to_database was called with status="failed"
        failed_calls = [
            call for call in mock_store_search.call_args_list 
            if call.args and isinstance(call.args[0], dict) and call.args[0].get("status") == "failed"
        ]
        self.assertEqual(len(failed_calls), 1, "store_search_to_database should be called exactly once with status='failed'")

    @patch('api.main_fixed_infinite_loop.get_search_from_database')
    @patch('api.main_fixed_infinite_loop.store_search_to_database')
    @patch('api.main_fixed_infinite_loop.parse_prompt_to_internal_database_filters')
    @patch('api.main_fixed_infinite_loop.search_people_via_internal_database')
    def test_process_search_with_global_timeout(
        self, mock_search_people, mock_parse_prompt, mock_store_search, mock_get_search
    ):
        """Test that process_search handles global timeouts properly."""
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
        mock_search_people.side_effect = TimeoutError("Global timeout exceeded")
        
        # Run the process_search function
        self.loop.run_until_complete(process_search(
            request_id="test-request-id",
            prompt="test prompt",
            max_candidates=2,
            include_linkedin=True
        ))
        
        # Verify that store_search_to_database was called with status="failed"
        failed_calls = [
            call for call in mock_store_search.call_args_list 
            if call.args and isinstance(call.args[0], dict) and call.args[0].get("status") == "failed"
        ]
        self.assertEqual(len(failed_calls), 1, "store_search_to_database should be called exactly once with status='failed'")

if __name__ == "__main__":
    unittest.main()