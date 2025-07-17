#!/usr/bin/env python3
"""
Integration test for the logical assessment feature in the pipeline.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import uuid
import asyncio
from datetime import datetime, timezone

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the modules to test
from api.main import process_search
from logical_assessment import assess_logical_coherence

class TestPipelineIntegration(unittest.TestCase):
    """Test the integration of the logical assessment function into the pipeline."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock request
        self.request_id = str(uuid.uuid4())
        self.request = MagicMock()
        self.request.prompt = "Find me senior software engineers at Google with experience in AI"
        self.request.max_candidates = 2
        self.request.include_linkedin = False
        
        # Create a mock search result
        self.search_result = MagicMock()
        self.search_result.request_id = self.request_id
        self.search_result.status = "processing"
        self.search_result.prompt = self.request.prompt
        self.search_result.created_at = datetime.now(timezone.utc).isoformat()
        self.search_result.dict = MagicMock(return_value={
            "request_id": self.request_id,
            "status": "processing",
            "prompt": self.request.prompt,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        # Mock the search_results dictionary
        self.search_results_patch = patch('api.main.search_results', {self.request_id: self.search_result})
        self.mock_search_results = self.search_results_patch.start()
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.search_results_patch.stop()

    @patch('api.main.parse_prompt_to_internal_database_filters')
    @patch('api.main.search_people_via_internal_database')
    @patch('api.main.assess_logical_coherence')
    @patch('api.main.select_top_candidates')
    @patch('api.main.simulate_behavioral_data')
    @patch('api.main.store_search_to_database')
    @patch('api.main.store_people_to_database')
    @patch('api.main.save_search_to_json')
    def test_logical_assessment_integration(
        self, mock_save_json, mock_store_people, mock_store_search, 
        mock_simulate, mock_select, mock_assess, mock_search, mock_parse
    ):
        """Test that the logical assessment function is called in the pipeline."""
        # Mock the parse_prompt_to_internal_database_filters function
        mock_parse.return_value = {
            "reasoning": "Valid query for senior software engineers at Google with AI experience",
            "filters": {"title": "Software Engineer", "company": "Google"}
        }
        
        # Mock the search_people_via_internal_database function
        mock_search.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "location": "Mountain View, CA",
                "seniority": "Director"
            },
            {
                "name": "Jane Smith",
                "title": "Marketing Manager",
                "organization_name": "Facebook",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "location": "San Francisco, CA",
                "seniority": "Manager"
            },
            {
                "name": "Bob Johnson",
                "title": "Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/bobjohnson",
                "location": "Seattle, WA",
                "seniority": "Senior"
            }
        ]
        
        # Mock the assess_logical_coherence function
        mock_assess.return_value = (
            True,  # is_coherent
            [mock_search.return_value[0], mock_search.return_value[2]],  # coherent_people (only Google employees)
            "John Doe and Bob Johnson are software engineers at Google, matching the query."  # explanation
        )
        
        # Mock the select_top_candidates function
        mock_select.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "company": "Google",
                "email": "john.doe@example.com",
                "accuracy": 95,
                "reasons": ["Senior Software Engineer at Google with AI experience"]
            },
            {
                "name": "Bob Johnson",
                "title": "Software Engineer",
                "company": "Google",
                "email": "bob.johnson@example.com",
                "accuracy": 85,
                "reasons": ["Software Engineer at Google"]
            }
        ]
        
        # Mock the simulate_behavioral_data function
        mock_simulate.return_value = {"behavioral_data": "simulated"}
        
        # Mock the database functions
        mock_store_search.return_value = 123  # search_id
        mock_store_people.return_value = None
        
        # Call the process_search function using the async helper
        async def run_test():
            await process_search(self.request_id, self.request)
            
            # Verify that the assess_logical_coherence function was called with the correct arguments
            mock_assess.assert_called_once()
            args, _ = mock_assess.call_args
            self.assertEqual(args[0], self.request.prompt)
            self.assertEqual(args[1], mock_search.return_value)
            
            # Verify that select_top_candidates was called with the filtered results
            mock_select.assert_called_once()
            args, _ = mock_select.call_args
            self.assertEqual(args[0], self.request.prompt)
            self.assertEqual(args[1], [mock_search.return_value[0], mock_search.return_value[2]])
            
            # Verify that the search result was updated correctly
            self.assertEqual(self.search_result.status, "completed")
            self.assertIsNotNone(self.search_result.completed_at)
            self.assertEqual(self.search_result.behavioral_data, {"behavioral_data": "simulated"})
            
        run_async_test(run_test())

    @patch('api.main.parse_prompt_to_internal_database_filters')
    @patch('api.main.search_people_via_internal_database')
    @patch('api.main.assess_logical_coherence')
    @patch('api.main.select_top_candidates')
    @patch('api.main.simulate_behavioral_data')
    @patch('api.main.store_search_to_database')
    @patch('api.main.store_people_to_database')
    @patch('api.main.save_search_to_json')
    def test_logical_assessment_error_handling(
        self, mock_save_json, mock_store_people, mock_store_search, 
        mock_simulate, mock_select, mock_assess, mock_search, mock_parse
    ):
        """Test that errors in the logical assessment function are handled properly."""
        # Mock the parse_prompt_to_internal_database_filters function
        mock_parse.return_value = {
            "reasoning": "Valid query for senior software engineers at Google with AI experience",
            "filters": {"title": "Software Engineer", "company": "Google"}
        }
        
        # Mock the search_people_via_internal_database function
        mock_search.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "location": "Mountain View, CA",
                "seniority": "Director"
            },
            {
                "name": "Jane Smith",
                "title": "Marketing Manager",
                "organization_name": "Facebook",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "location": "San Francisco, CA",
                "seniority": "Manager"
            }
        ]
        
        # Mock the assess_logical_coherence function to raise an exception
        mock_assess.side_effect = Exception("Assessment failed")
        
        # Mock the select_top_candidates function
        mock_select.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "company": "Google",
                "email": "john.doe@example.com",
                "accuracy": 95,
                "reasons": ["Senior Software Engineer at Google with AI experience"]
            }
        ]
        
        # Mock the simulate_behavioral_data function
        mock_simulate.return_value = {"behavioral_data": "simulated"}
        
        # Mock the database functions
        mock_store_search.return_value = 123  # search_id
        mock_store_people.return_value = None
        
        # Call the process_search function using the async helper
        async def run_test():
            await process_search(self.request_id, self.request)
            
            # Verify that the assess_logical_coherence function was called
            mock_assess.assert_called_once()
            
            # Verify that select_top_candidates was called with the original results
            # (since the assessment failed, it should use all results)
            mock_select.assert_called_once()
            args, _ = mock_select.call_args
            self.assertEqual(args[0], self.request.prompt)
            self.assertEqual(args[1], mock_search.return_value)
            
            # Verify that the search result was updated correctly
            self.assertEqual(self.search_result.status, "completed")
            self.assertIsNotNone(self.search_result.completed_at)
            self.assertEqual(self.search_result.behavioral_data, {"behavioral_data": "simulated"})
            
        run_async_test(run_test())

    @patch('api.main.parse_prompt_to_internal_database_filters')
    @patch('api.main.search_people_via_internal_database')
    @patch('api.main.assess_logical_coherence')
    @patch('api.main.select_top_candidates')
    @patch('api.main.simulate_behavioral_data')
    @patch('api.main.store_search_to_database')
    @patch('api.main.store_people_to_database')
    @patch('api.main.save_search_to_json')
    def test_no_coherent_results_fallback(
        self, mock_save_json, mock_store_people, mock_store_search, 
        mock_simulate, mock_select, mock_assess, mock_search, mock_parse
    ):
        """Test that the pipeline falls back to all results when no coherent results are found."""
        # Mock the parse_prompt_to_internal_database_filters function
        mock_parse.return_value = {
            "reasoning": "Valid query for senior software engineers at Google with AI experience",
            "filters": {"title": "Software Engineer", "company": "Google"}
        }
        
        # Mock the search_people_via_internal_database function
        mock_search.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "organization_name": "Google",
                "linkedin_url": "https://linkedin.com/in/johndoe",
                "location": "Mountain View, CA",
                "seniority": "Director"
            },
            {
                "name": "Jane Smith",
                "title": "Marketing Manager",
                "organization_name": "Facebook",
                "linkedin_url": "https://linkedin.com/in/janesmith",
                "location": "San Francisco, CA",
                "seniority": "Manager"
            }
        ]
        
        # Mock the assess_logical_coherence function to return no coherent results
        mock_assess.return_value = (
            False,  # is_coherent
            [],  # no coherent_people
            "No results match the query for senior software engineers at Google with AI experience."  # explanation
        )
        
        # Mock the select_top_candidates function
        mock_select.return_value = [
            {
                "name": "John Doe",
                "title": "Senior Software Engineer",
                "company": "Google",
                "email": "john.doe@example.com",
                "accuracy": 95,
                "reasons": ["Senior Software Engineer at Google with AI experience"]
            }
        ]
        
        # Mock the simulate_behavioral_data function
        mock_simulate.return_value = {"behavioral_data": "simulated"}
        
        # Mock the database functions
        mock_store_search.return_value = 123  # search_id
        mock_store_people.return_value = None
        
        # Call the process_search function using the async helper
        async def run_test():
            await process_search(self.request_id, self.request)
            
            # Verify that the assess_logical_coherence function was called
            mock_assess.assert_called_once()
            
            # Verify that select_top_candidates was called with all results
            # (since no coherent results were found, it should use all results)
            mock_select.assert_called_once()
            args, _ = mock_select.call_args
            self.assertEqual(args[0], self.request.prompt)
            self.assertEqual(args[1], mock_search.return_value)
            
            # Verify that the search result was updated correctly
            self.assertEqual(self.search_result.status, "completed")
            self.assertIsNotNone(self.search_result.completed_at)
            self.assertEqual(self.search_result.behavioral_data, {"behavioral_data": "simulated"})
            
        run_async_test(run_test())

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main()