#!/usr/bin/env python3
"""
Integration tests for data mapping and transformation fixes.

This test suite validates the complete data flow from API to database,
ensuring prompt data is preserved throughout all transformations.

Requirements addressed:
- 2.1: Preserve prompt data throughout data flow
- 2.2: Correct mapping of prompt fields between data structures  
- 2.4: Maintain data integrity through all operations
"""

import unittest
from unittest.mock import patch, MagicMock, call
import sys
import os
import json
import uuid
from datetime import datetime, timezone

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules to test
from data_mapping_transformer import (
    SearchDataTransformer,
    ValidationCheckpoint,
    safe_transform_for_storage,
    safe_transform_for_api_response,
    safe_merge_search_updates,
    validate_field_mapping,
    DataMappingError,
    TransformationError
)

try:
    from search_data_validator import (
        SearchDataValidator,
        SearchDataValidationError,
        PromptIntegrityError
    )
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False

try:
    from database import (
        store_search_to_database,
        get_search_from_database,
        update_search_in_database
    )
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


class TestDataMappingIntegration(unittest.TestCase):
    """Integration tests for data mapping and transformation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_request_id = str(uuid.uuid4())
        self.test_prompt = "Find software engineers in San Francisco with 5+ years experience"
        
        # Sample search data for testing
        self.sample_search_data = {
            'request_id': self.test_request_id,
            'prompt': self.test_prompt,
            'status': 'processing',
            'max_candidates': 5,
            'filters': {'location': 'San Francisco', 'experience': '5+'},
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Sample update data
        self.sample_updates = {
            'status': 'completed',
            'completed_at': datetime.now(timezone.utc).isoformat(),
            'filters': {'location': 'San Francisco', 'experience': '5+', 'role': 'engineer'}
        }
    
    def test_safe_transform_for_storage_preserves_prompt(self):
        """Test that storage transformation preserves prompt data."""
        # Test with valid data
        transformed_data = safe_transform_for_storage(self.sample_search_data)
        
        # Verify prompt is preserved
        self.assertEqual(transformed_data['prompt'], self.test_prompt)
        self.assertEqual(transformed_data['request_id'], self.test_request_id)
        
        # Verify JSON fields are converted to strings
        self.assertIsInstance(transformed_data['filters'], str)
        
        # Verify critical fields are present
        for field in ['request_id', 'prompt', 'status']:
            self.assertIn(field, transformed_data)
            self.assertIsNotNone(transformed_data[field])
    
    def test_safe_transform_for_storage_rejects_null_prompt(self):
        """Test that storage transformation rejects null prompts."""
        invalid_data = self.sample_search_data.copy()
        invalid_data['prompt'] = None
        
        with self.assertRaises((TransformationError, PromptIntegrityError)):
            safe_transform_for_storage(invalid_data)
    
    def test_safe_transform_for_storage_rejects_empty_prompt(self):
        """Test that storage transformation rejects empty prompts."""
        invalid_data = self.sample_search_data.copy()
        invalid_data['prompt'] = "   "  # Whitespace only
        
        with self.assertRaises((TransformationError, PromptIntegrityError)):
            safe_transform_for_storage(invalid_data)
    
    def test_safe_transform_for_api_response_preserves_prompt(self):
        """Test that API response transformation preserves prompt data."""
        # First transform for storage (JSON strings)
        storage_data = safe_transform_for_storage(self.sample_search_data)
        
        # Then transform for API response (back to objects)
        api_data = safe_transform_for_api_response(storage_data)
        
        # Verify prompt is preserved
        self.assertEqual(api_data['prompt'], self.test_prompt)
        self.assertEqual(api_data['request_id'], self.test_request_id)
        
        # Verify JSON fields are converted back to objects
        self.assertIsInstance(api_data['filters'], dict)
        
        # Verify internal fields are filtered out
        self.assertNotIn('id', api_data)  # Database ID should be filtered
    
    def test_safe_merge_search_updates_preserves_prompt(self):
        """Test that merge operations preserve prompt data."""
        existing_data = self.sample_search_data.copy()
        existing_data['id'] = 123  # Add database ID
        
        # Updates without prompt
        updates_without_prompt = {
            'status': 'completed',
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        merged_data = safe_merge_search_updates(existing_data, updates_without_prompt)
        
        # Verify prompt is preserved from existing data
        self.assertEqual(merged_data['prompt'], self.test_prompt)
        self.assertEqual(merged_data['request_id'], self.test_request_id)
        
        # Verify updates are applied
        self.assertEqual(merged_data['status'], 'completed')
        self.assertIsNotNone(merged_data['completed_at'])
        
        # Verify existing fields are preserved
        self.assertEqual(merged_data['id'], 123)
    
    def test_safe_merge_search_updates_validates_prompt_changes(self):
        """Test that merge operations handle invalid prompt updates correctly."""
        existing_data = self.sample_search_data.copy()
        
        # Try to update with empty prompt
        invalid_updates = {
            'prompt': '',  # Empty prompt
            'status': 'completed'
        }
        
        # The merge should preserve the original valid prompt when update is invalid
        merged_data = safe_merge_search_updates(existing_data, invalid_updates)
        
        # Should preserve original prompt and apply other updates
        self.assertEqual(merged_data['prompt'], self.test_prompt)  # Original prompt preserved
        self.assertEqual(merged_data['status'], 'completed')  # Other updates applied
    
    def test_validate_field_mapping_detects_prompt_loss(self):
        """Test that field mapping validation detects prompt data loss."""
        source_data = self.sample_search_data.copy()
        
        # Create target data with missing prompt
        target_data = source_data.copy()
        del target_data['prompt']
        
        is_valid, issues = validate_field_mapping(source_data, target_data)
        
        self.assertFalse(is_valid)
        self.assertTrue(any('prompt' in issue.lower() for issue in issues))
    
    def test_validate_field_mapping_detects_prompt_changes(self):
        """Test that field mapping validation detects prompt changes."""
        source_data = self.sample_search_data.copy()
        
        # Create target data with changed prompt
        target_data = source_data.copy()
        target_data['prompt'] = "Different prompt"
        
        is_valid, issues = validate_field_mapping(source_data, target_data)
        
        self.assertFalse(is_valid)
        self.assertTrue(any('prompt changed' in issue.lower() for issue in issues))
    
    def test_validation_checkpoint_detects_issues(self):
        """Test that validation checkpoints detect data integrity issues."""
        checkpoint = ValidationCheckpoint("test_checkpoint")
        
        # Test with valid data
        is_valid, issues = checkpoint.validate_at_checkpoint(self.sample_search_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)
        
        # Test with invalid data (missing prompt)
        invalid_data = self.sample_search_data.copy()
        del invalid_data['prompt']
        
        is_valid, issues = checkpoint.validate_at_checkpoint(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any('prompt' in issue.lower() for issue in issues))
    
    def test_validation_checkpoint_with_expected_prompt(self):
        """Test validation checkpoint with expected prompt value."""
        checkpoint = ValidationCheckpoint("test_checkpoint")
        
        # Test with matching prompt
        is_valid, issues = checkpoint.validate_at_checkpoint(
            self.sample_search_data, 
            expected_prompt=self.test_prompt
        )
        self.assertTrue(is_valid)
        
        # Test with non-matching prompt
        is_valid, issues = checkpoint.validate_at_checkpoint(
            self.sample_search_data, 
            expected_prompt="Different prompt"
        )
        self.assertFalse(is_valid)
        self.assertTrue(any('mismatch' in issue.lower() for issue in issues))
    
    @patch('data_mapping_transformer.log_data_flow')
    @patch('data_mapping_transformer.track_prompt_presence')
    def test_transformation_logging(self, mock_track, mock_log):
        """Test that transformations are properly logged."""
        # Perform transformation
        transformed_data = safe_transform_for_storage(self.sample_search_data)
        
        # Verify logging calls were made
        self.assertTrue(mock_log.called)
        self.assertTrue(mock_track.called)
        
        # Check that prompt presence was tracked
        track_calls = mock_track.call_args_list
        self.assertTrue(any('post_transform' in str(call) for call in track_calls))
    
    def test_complete_data_flow_simulation(self):
        """Test complete data flow from API creation to database storage."""
        # Step 1: API creates initial search data
        api_data = {
            'request_id': self.test_request_id,
            'prompt': self.test_prompt,
            'status': 'processing',
            'max_candidates': 5,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Step 2: Transform for storage
        storage_data = safe_transform_for_storage(api_data)
        
        # Verify prompt is preserved
        self.assertEqual(storage_data['prompt'], self.test_prompt)
        
        # Step 3: Simulate database storage and retrieval
        # (In real scenario, this would go to database)
        retrieved_data = storage_data.copy()
        retrieved_data['id'] = 123  # Add database ID
        
        # Step 4: Process updates (background processing)
        updates = {
            'status': 'completed',
            'filters': json.dumps({'location': 'San Francisco'}),
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Step 5: Merge updates safely
        updated_data = safe_merge_search_updates(retrieved_data, updates)
        
        # Verify prompt is still preserved
        self.assertEqual(updated_data['prompt'], self.test_prompt)
        self.assertEqual(updated_data['status'], 'completed')
        
        # Step 6: Transform for API response
        final_api_data = safe_transform_for_api_response(updated_data)
        
        # Verify final data integrity
        self.assertEqual(final_api_data['prompt'], self.test_prompt)
        self.assertEqual(final_api_data['request_id'], self.test_request_id)
        self.assertEqual(final_api_data['status'], 'completed')
        self.assertIsInstance(final_api_data['filters'], dict)
    
    def test_error_handling_in_transformations(self):
        """Test error handling in transformation operations."""
        # Test with invalid data type
        with self.assertRaises(TransformationError):
            safe_transform_for_storage("not a dictionary")
        
        # Test with missing critical fields
        invalid_data = {'status': 'processing'}  # Missing request_id and prompt
        
        with self.assertRaises((TransformationError, PromptIntegrityError)):
            safe_transform_for_storage(invalid_data)
    
    def test_json_field_handling(self):
        """Test proper handling of JSON fields during transformations."""
        # Test with dict filters
        data_with_dict_filters = self.sample_search_data.copy()
        data_with_dict_filters['filters'] = {'location': 'SF', 'role': 'engineer'}
        
        # Transform for storage (should convert to JSON string)
        storage_data = safe_transform_for_storage(data_with_dict_filters)
        self.assertIsInstance(storage_data['filters'], str)
        
        # Transform for API response (should convert back to dict)
        api_data = safe_transform_for_api_response(storage_data)
        self.assertIsInstance(api_data['filters'], dict)
        self.assertEqual(api_data['filters']['location'], 'SF')
    
    def test_timestamp_normalization(self):
        """Test timestamp normalization during transformations."""
        # Test with datetime object
        data_with_datetime = self.sample_search_data.copy()
        data_with_datetime['created_at'] = datetime.now(timezone.utc)
        
        # Transform for storage (should convert to ISO string)
        storage_data = safe_transform_for_storage(data_with_datetime)
        self.assertIsInstance(storage_data['created_at'], str)
        
        # Verify it's a valid ISO format
        datetime.fromisoformat(storage_data['created_at'].replace('Z', '+00:00'))


@unittest.skipUnless(DATABASE_AVAILABLE, "Database module not available")
class TestDatabaseIntegration(unittest.TestCase):
    """Integration tests with actual database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_request_id = str(uuid.uuid4())
        self.test_prompt = "Find data scientists in New York"
        
        self.sample_search_data = {
            'request_id': self.test_request_id,
            'prompt': self.test_prompt,
            'status': 'processing',
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    
    @patch('database.supabase')
    def test_enhanced_store_search_with_validation(self, mock_supabase):
        """Test enhanced store_search_to_database with validation."""
        # Mock successful database response
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[{'id': 123, **self.sample_search_data}])
        
        # Store search data
        result = store_search_to_database(self.sample_search_data)
        
        # Verify result
        self.assertEqual(result, 123)
        
        # Verify database was called
        mock_supabase.table.assert_called_with("searches")
        mock_table.upsert.assert_called_once()
        
        # Get the actual data that was stored
        stored_data = mock_table.upsert.call_args[0][0]
        
        # Verify prompt was preserved
        self.assertEqual(stored_data['prompt'], self.test_prompt)
        self.assertEqual(stored_data['request_id'], self.test_request_id)
    
    @patch('database.supabase')
    def test_enhanced_update_search_with_validation(self, mock_supabase):
        """Test enhanced update_search_in_database with validation."""
        # Mock database responses
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        
        # Mock get_search_from_database response
        existing_data = self.sample_search_data.copy()
        existing_data['id'] = 123
        
        with patch('database.get_search_from_database', return_value=existing_data):
            # Mock upsert response
            updated_data = existing_data.copy()
            updated_data['status'] = 'completed'
            mock_table.upsert.return_value = mock_table
            mock_table.execute.return_value = MagicMock(data=[updated_data])
            
            # Perform update
            updates = {'status': 'completed'}
            result = update_search_in_database(self.test_request_id, updates)
            
            # Verify result
            self.assertTrue(result)
            
            # Verify database was called
            mock_table.upsert.assert_called_once()
            
            # Get the actual data that was updated
            updated_data_call = mock_table.upsert.call_args[0][0]
            
            # Verify prompt was preserved
            self.assertEqual(updated_data_call['prompt'], self.test_prompt)
            self.assertEqual(updated_data_call['status'], 'completed')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error scenarios."""
    
    def test_transformation_with_unicode_prompt(self):
        """Test transformation with unicode characters in prompt."""
        unicode_prompt = "Find développeurs in São Paulo with résumé"
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': unicode_prompt,
            'status': 'processing'
        }
        
        # Should handle unicode without issues
        transformed_data = safe_transform_for_storage(data)
        self.assertEqual(transformed_data['prompt'], unicode_prompt)
    
    def test_transformation_with_very_long_prompt(self):
        """Test transformation with very long prompt."""
        long_prompt = "Find engineers " * 1000  # Very long prompt
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': long_prompt,
            'status': 'processing'
        }
        
        # Should handle long prompts without issues
        transformed_data = safe_transform_for_storage(data)
        self.assertEqual(transformed_data['prompt'], long_prompt)
    
    def test_merge_with_conflicting_prompts(self):
        """Test merge behavior with conflicting prompt values."""
        existing_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'Original prompt',
            'status': 'processing'
        }
        
        updates = {
            'prompt': 'Updated prompt',
            'status': 'completed'
        }
        
        # Should use the updated prompt if it's valid
        merged_data = safe_merge_search_updates(existing_data, updates)
        self.assertEqual(merged_data['prompt'], 'Updated prompt')
    
    def test_merge_preserves_prompt_when_update_invalid(self):
        """Test that merge preserves original prompt when update is invalid."""
        existing_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'Valid original prompt',
            'status': 'processing'
        }
        
        updates = {
            'prompt': '',  # Invalid empty prompt
            'status': 'completed'
        }
        
        # Should preserve original prompt when update is invalid
        merged_data = safe_merge_search_updates(existing_data, updates)
        self.assertEqual(merged_data['prompt'], 'Valid original prompt')


if __name__ == "__main__":
    # Run the tests
    print("🧪 Running Data Mapping Integration Tests...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDataMappingIntegration))
    if DATABASE_AVAILABLE:
        suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ All tests passed!")
    else:
        print(f"\n❌ Some tests failed!")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)