#!/usr/bin/env python3
"""
Tests for enhanced database retrieval operations.
Verifies that prompt data is properly retrieved and logged.
"""

import unittest
from unittest.mock import patch, MagicMock, call
import logging
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced database function
from database import get_search_from_database

class TestEnhancedDatabaseRetrieval(unittest.TestCase):
    """Test the enhanced database retrieval operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_request_id = "test-request-123"
        self.sample_search_data = {
            "id": 1,
            "request_id": self.test_request_id,
            "status": "completed",
            "prompt": "Find software engineers in San Francisco",
            "filters": '{"location": "San Francisco", "title": "software engineer"}',
            "behavioral_data": '{"personality": "analytical"}',
            "created_at": "2024-01-01T10:00:00Z",
            "completed_at": "2024-01-01T10:05:00Z",
            "error": None
        }
        
        # Set up logging capture
        self.log_capture = []
        self.original_handlers = logging.getLogger().handlers[:]
        
        # Create a custom handler to capture log messages
        class LogCapture(logging.Handler):
            def __init__(self, capture_list):
                super().__init__()
                self.capture_list = capture_list
            
            def emit(self, record):
                self.capture_list.append(self.format(record))
        
        self.log_handler = LogCapture(self.log_capture)
        self.log_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original logging handlers
        logging.getLogger().handlers = self.original_handlers
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_successful_retrieval_with_prompt(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test successful retrieval of search data with valid prompt."""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.data = [self.sample_search_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["request_id"], self.test_request_id)
        self.assertEqual(result["prompt"], "Find software engineers in San Francisco")
        self.assertEqual(result["status"], "completed")
        
        # Verify explicit field selection was used
        expected_fields = "id, request_id, status, prompt, filters, behavioral_data, created_at, completed_at, error"
        mock_table.select.assert_called_once_with(expected_fields)
        mock_table.select.return_value.eq.assert_called_once_with("request_id", self.test_request_id)
        
        # Verify logging calls
        mock_log_flow.assert_any_call("retrieve", self.test_request_id, {}, "pre_retrieval")
        mock_log_flow.assert_any_call("retrieve", self.test_request_id, self.sample_search_data, "post_retrieval")
        mock_log_db.assert_called_once_with("select", "searches", self.test_request_id, None, mock_result, None)
        
        # Verify prompt tracking (length should be 40, not 37)
        mock_track.assert_any_call("post_retrieve", self.test_request_id, True, 40, "retrieved_from_db")
        
        # Check that success logs were generated
        success_logs = [log for log in self.log_capture if "Successfully retrieved search data" in log]
        self.assertGreater(len(success_logs), 0, "Should have success log messages")
        
        # Check that prompt integrity was verified
        integrity_logs = [log for log in self.log_capture if "Prompt integrity verified" in log]
        self.assertGreater(len(integrity_logs), 0, "Should have prompt integrity verification")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_retrieval_with_null_prompt(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test retrieval of search data with null prompt - should log critical error."""
        # Setup search data with null prompt
        null_prompt_data = self.sample_search_data.copy()
        null_prompt_data["prompt"] = None
        
        mock_result = MagicMock()
        mock_result.data = [null_prompt_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result is still returned (function doesn't fail)
        self.assertIsNotNone(result)
        self.assertEqual(result["request_id"], self.test_request_id)
        self.assertIsNone(result["prompt"])
        
        # Verify prompt tracking shows no prompt
        mock_track.assert_any_call("post_retrieve", self.test_request_id, False, 0, "retrieved_from_db")
        mock_track.assert_any_call("integrity_violation", self.test_request_id, False, 0, "null_prompt_in_db_result: None")
        
        # Check that critical error logs were generated
        critical_logs = [log for log in self.log_capture if "CRITICAL: Retrieved search" in log and "null/empty prompt" in log]
        self.assertGreater(len(critical_logs), 0, "Should have critical error log for null prompt")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_retrieval_with_empty_prompt(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test retrieval of search data with empty string prompt."""
        # Setup search data with empty prompt
        empty_prompt_data = self.sample_search_data.copy()
        empty_prompt_data["prompt"] = "   "  # Whitespace only
        
        mock_result = MagicMock()
        mock_result.data = [empty_prompt_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["prompt"], "   ")
        
        # Verify prompt tracking shows no valid prompt (empty after strip)
        mock_track.assert_any_call("post_retrieve", self.test_request_id, False, 3, "retrieved_from_db")
        mock_track.assert_any_call("integrity_violation", self.test_request_id, False, 0, "null_prompt_in_db_result: '   '")
        
        # Check that critical error logs were generated
        critical_logs = [log for log in self.log_capture if "CRITICAL: Retrieved search" in log]
        self.assertGreater(len(critical_logs), 0, "Should have critical error log for empty prompt")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_retrieval_not_found(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test retrieval when search is not found."""
        # Setup mock response with no data
        mock_result = MagicMock()
        mock_result.data = []
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result
        self.assertIsNone(result)
        
        # Verify logging calls
        mock_log_flow.assert_any_call("retrieve", self.test_request_id, {}, "pre_retrieval")
        mock_log_db.assert_called_once_with("select", "searches", self.test_request_id, None, mock_result, None)
        mock_track.assert_called_with("retrieve_not_found", self.test_request_id, False, 0, "no_data_found")
        
        # Check that not found logs were generated
        not_found_logs = [log for log in self.log_capture if "No search record found" in log]
        self.assertGreater(len(not_found_logs), 0, "Should have not found log messages")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_retrieval_database_error(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test retrieval when database error occurs."""
        # Setup mock to raise an exception
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.side_effect = Exception("Database connection failed")
        mock_supabase.table.return_value = mock_table
        
        # Execute the function and expect exception
        with self.assertRaises(Exception) as context:
            get_search_from_database(self.test_request_id)
        
        self.assertIn("Database connection failed", str(context.exception))
        
        # Verify error logging
        mock_log_db.assert_called_once()
        args = mock_log_db.call_args[0]
        self.assertEqual(args[0], "select")  # operation
        self.assertEqual(args[1], "searches")  # table
        self.assertEqual(args[2], self.test_request_id)  # request_id
        self.assertIsInstance(args[5], Exception)  # error
        
        mock_track.assert_called_with("retrieve_error", self.test_request_id, False, 0, "error: Database connection failed")
        
        # Check that error logs were generated
        error_logs = [log for log in self.log_capture if "Database error retrieving search" in log]
        self.assertGreater(len(error_logs), 0, "Should have error log messages")
    
    def test_invalid_request_id_validation(self):
        """Test validation of invalid request_id values."""
        invalid_ids = [None, "", "   ", 123, [], {}]
        
        for invalid_id in invalid_ids:
            with self.subTest(request_id=invalid_id):
                with self.assertRaises(ValueError) as context:
                    get_search_from_database(invalid_id)
                
                self.assertIn("request_id must be a non-empty string", str(context.exception))
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_multiple_records_warning(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test warning when multiple records are found for same request_id."""
        # Setup mock response with multiple records
        duplicate_data = self.sample_search_data.copy()
        duplicate_data["id"] = 2
        
        mock_result = MagicMock()
        mock_result.data = [self.sample_search_data, duplicate_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result (should return first record)
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], 1)  # First record
        
        # Check that warning logs were generated
        warning_logs = [log for log in self.log_capture if "Multiple records found" in log]
        self.assertGreater(len(warning_logs), 0, "Should have warning for multiple records")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_missing_fields_warning(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test warning when retrieved data is missing expected fields."""
        # Setup search data missing some fields
        incomplete_data = {
            "id": 1,
            "request_id": self.test_request_id,
            "status": "completed",
            "prompt": "Find engineers"
            # Missing: filters, behavioral_data, created_at, completed_at, error
        }
        
        mock_result = MagicMock()
        mock_result.data = [incomplete_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify the result
        self.assertIsNotNone(result)
        self.assertEqual(result["prompt"], "Find engineers")
        
        # Check that warning logs were generated for missing fields
        warning_logs = [log for log in self.log_capture if "missing expected fields" in log]
        self.assertGreater(len(warning_logs), 0, "Should have warning for missing fields")
    
    @patch('database.supabase')
    @patch('database.log_data_flow')
    @patch('database.log_database_operation')
    @patch('database.track_prompt_presence')
    def test_detailed_logging_output(self, mock_track, mock_log_db, mock_log_flow, mock_supabase):
        """Test that detailed logging information is properly output."""
        # Setup mock response
        mock_result = MagicMock()
        mock_result.data = [self.sample_search_data]
        
        mock_table = MagicMock()
        mock_table.select.return_value.eq.return_value.execute.return_value = mock_result
        mock_supabase.table.return_value = mock_table
        
        # Execute the function
        result = get_search_from_database(self.test_request_id)
        
        # Verify detailed logging was performed
        expected_log_patterns = [
            "Starting database retrieval for request_id",
            "Executing database query: SELECT",
            "Database response: data_count=1",
            "Successfully retrieved search data:",
            "request_id: test-request-123",
            "status: completed",
            "prompt: 'Find software engineers in San Francisco' (length: 40)",
            "has_filters: True",
            "has_behavioral_data: True",
            "Prompt integrity verified"
        ]
        
        for pattern in expected_log_patterns:
            matching_logs = [log for log in self.log_capture if pattern in log]
            self.assertGreater(len(matching_logs), 0, f"Should have log containing: {pattern}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)