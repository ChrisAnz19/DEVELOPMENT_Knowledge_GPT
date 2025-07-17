#!/usr/bin/env python3
"""
Test the null prompt database fix
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import store_search_to_database

class TestNullPromptFix(unittest.TestCase):
    
    @patch('database.supabase')
    def test_store_search_with_null_prompt_uses_default(self, mock_supabase):
        """Test that searches with null prompts get a default prompt"""
        # Mock the supabase response
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[{'id': 123}])
        
        # Test data with null prompt (similar to the error case)
        search_data = {
            'id': 206,
            'request_id': 'abfbafb8-e0ab-4458-9cfa-fca123bd0055',
            'status': 'completed',
            'behavioral_data': '{"behavioral_insight": "test"}',
            'completed_at': '2025-07-17T23:17:03.281386+00:00'
            # Note: no 'prompt' field
        }
        
        # Call the function
        result = store_search_to_database(search_data)
        
        # Verify it succeeded
        self.assertEqual(result, 123)
        
        # Verify supabase was called with the default prompt
        mock_supabase.table.assert_called_with("searches")
        mock_table.upsert.assert_called_once()
        
        # Get the actual data that was passed to upsert
        upserted_data = mock_table.upsert.call_args[0][0]
        self.assertEqual(upserted_data['prompt'], "No prompt provided")
        self.assertEqual(upserted_data['request_id'], 'abfbafb8-e0ab-4458-9cfa-fca123bd0055')
        self.assertEqual(upserted_data['status'], 'completed')
    
    @patch('database.supabase')
    def test_store_search_with_empty_string_prompt_uses_default(self, mock_supabase):
        """Test that searches with empty string prompts get a default prompt"""
        # Mock the supabase response
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[{'id': 124}])
        
        # Test data with empty prompt
        search_data = {
            'request_id': 'test-request-id',
            'status': 'completed',
            'prompt': ''  # Empty string
        }
        
        # Call the function
        result = store_search_to_database(search_data)
        
        # Verify it succeeded
        self.assertEqual(result, 124)
        
        # Get the actual data that was passed to upsert
        upserted_data = mock_table.upsert.call_args[0][0]
        self.assertEqual(upserted_data['prompt'], "No prompt provided")
    
    @patch('database.supabase')
    def test_store_search_with_valid_prompt_unchanged(self, mock_supabase):
        """Test that searches with valid prompts are stored unchanged"""
        # Mock the supabase response
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[{'id': 125}])
        
        # Test data with valid prompt
        search_data = {
            'request_id': 'test-request-id',
            'status': 'completed',
            'prompt': 'Find sales directors in tech companies'
        }
        
        # Call the function
        result = store_search_to_database(search_data)
        
        # Verify it succeeded
        self.assertEqual(result, 125)
        
        # Get the actual data that was passed to upsert
        upserted_data = mock_table.upsert.call_args[0][0]
        self.assertEqual(upserted_data['prompt'], 'Find sales directors in tech companies')
    
    def test_store_search_with_null_request_id_raises_error(self):
        """Test that searches without request_id still raise an error"""
        search_data = {
            'status': 'completed',
            'prompt': 'Valid prompt'
            # Note: no 'request_id' field
        }
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            store_search_to_database(search_data)
        
        self.assertIn("request_id cannot be null", str(context.exception))

if __name__ == "__main__":
    unittest.main()