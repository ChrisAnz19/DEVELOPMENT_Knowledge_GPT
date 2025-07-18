#!/usr/bin/env python3
"""
Comprehensive tests for enhanced database storage operations.

Tests the enhanced storage functionality including:
- Pre-storage validation
- Prompt integrity preservation
- Partial update functionality
- Error handling and validation

Requirements addressed:
- 1.1: Proper access and preservation of prompt data
- 1.2: Correct mapping and storage of prompt values
- 2.1: Preserve prompt data through storage pipeline
"""

import pytest
import uuid
import json
from unittest.mock import Mock, patch, MagicMock
import logging

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Test data fixtures
@pytest.fixture
def valid_search_data():
    """Valid search data for testing."""
    return {
        'request_id': str(uuid.uuid4()),
        'prompt': 'Find software engineers in San Francisco with Python experience',
        'status': 'pending',
        'max_candidates': 5,
        'filters': json.dumps({'location': 'San Francisco', 'skills': ['Python']}),
        'behavioral_data': json.dumps({'openness': 0.8, 'conscientiousness': 0.7})
    }

@pytest.fixture
def invalid_search_data():
    """Invalid search data for testing validation."""
    return {
        'request_id': 'invalid-uuid',
        'prompt': '',  # Empty prompt
        'status': 'invalid_status',
        'max_candidates': 'not_a_number'
    }

@pytest.fixture
def mock_supabase_response():
    """Mock successful Supabase response."""
    mock_response = Mock()
    mock_response.data = [{
        'id': 123,
        'request_id': str(uuid.uuid4()),
        'prompt': 'Test prompt',
        'status': 'pending',
        'created_at': '2024-01-01T00:00:00Z'
    }]
    return mock_response

@pytest.fixture
def mock_supabase_table():
    """Mock Supabase table operations."""
    mock_table = Mock()
    mock_table.upsert.return_value.execute.return_value = Mock()
    mock_table.select.return_value.eq.return_value.execute.return_value = Mock()
    return mock_table


class TestEnhancedStorageOperations:
    """Test suite for enhanced database storage operations."""
    
    def test_store_search_with_validation_success(self, valid_search_data, mock_supabase_response):
        """Test successful storage with validation."""
        with patch('database.supabase') as mock_supabase:
            # Setup mock
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_supabase_response
            mock_supabase.table.return_value = mock_table
            
            # Import and test
            from database import store_search_to_database
            
            result = store_search_to_database(valid_search_data)
            
            # Verify result
            assert result == 123
            mock_table.upsert.assert_called_once()
            
            # Verify the data passed to upsert contains validated prompt
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert 'prompt' in upsert_call_args
            assert upsert_call_args['prompt'] == valid_search_data['prompt']
    
    def test_store_search_validation_failure(self, invalid_search_data):
        """Test storage failure due to validation errors."""
        from database import store_search_to_database
        
        with pytest.raises(ValueError) as exc_info:
            store_search_to_database(invalid_search_data)
        
        # Should fail on validation
        assert "request_id" in str(exc_info.value) or "prompt" in str(exc_info.value)
    
    def test_store_search_prompt_integrity_preservation(self, valid_search_data, mock_supabase_response):
        """Test that prompt integrity is preserved during storage."""
        original_prompt = valid_search_data['prompt']
        
        with patch('database.supabase') as mock_supabase:
            # Setup mock to return the same prompt
            mock_supabase_response.data[0]['prompt'] = original_prompt
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_supabase_response
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database
            
            result = store_search_to_database(valid_search_data)
            
            # Verify prompt was preserved
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['prompt'] == original_prompt
    
    def test_store_search_with_missing_prompt(self):
        """Test storage behavior with missing prompt."""
        search_data = {
            'request_id': str(uuid.uuid4()),
            'status': 'pending'
            # Missing prompt
        }
        
        from database import store_search_to_database
        
        with pytest.raises(ValueError) as exc_info:
            store_search_to_database(search_data)
        
        assert "prompt" in str(exc_info.value)
    
    def test_store_search_with_null_prompt(self):
        """Test storage behavior with null prompt."""
        search_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': None,
            'status': 'pending'
        }
        
        from database import store_search_to_database
        
        with pytest.raises(ValueError) as exc_info:
            store_search_to_database(search_data)
        
        assert "prompt" in str(exc_info.value)
    
    def test_store_search_with_empty_prompt(self):
        """Test storage behavior with empty prompt."""
        search_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': '',
            'status': 'pending'
        }
        
        from database import store_search_to_database
        
        with pytest.raises(ValueError) as exc_info:
            store_search_to_database(search_data)
        
        assert "prompt" in str(exc_info.value)
    
    def test_store_search_enhanced_alias(self, valid_search_data, mock_supabase_response):
        """Test the enhanced storage alias function."""
        with patch('database.supabase') as mock_supabase:
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_supabase_response
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database_enhanced
            
            result = store_search_to_database_enhanced(valid_search_data)
            
            assert result == 123
            mock_table.upsert.assert_called_once()


class TestPartialUpdateOperations:
    """Test suite for partial update functionality."""
    
    def test_partial_update_success(self, valid_search_data, mock_supabase_response):
        """Test successful partial update."""
        request_id = valid_search_data['request_id']
        updates = {'status': 'completed', 'completed_at': '2024-01-01T12:00:00Z'}
        
        with patch('database.supabase') as mock_supabase, \
             patch('database.get_search_from_database') as mock_get:
            
            # Setup mocks
            mock_get.return_value = valid_search_data
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_supabase_response
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            result = update_search_in_database(request_id, updates)
            
            assert result is True
            mock_table.upsert.assert_called_once()
            
            # Verify merged data includes both original and updates
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['prompt'] == valid_search_data['prompt']  # Preserved
            assert upsert_call_args['status'] == 'completed'  # Updated
    
    def test_partial_update_prompt_preservation(self, valid_search_data):
        """Test that partial update preserves existing prompt data."""
        request_id = valid_search_data['request_id']
        original_prompt = valid_search_data['prompt']
        updates = {'status': 'processing'}  # No prompt in updates
        
        with patch('database.supabase') as mock_supabase, \
             patch('database.get_search_from_database') as mock_get:
            
            # Setup mocks
            mock_get.return_value = valid_search_data
            mock_response = Mock()
            mock_response.data = [valid_search_data.copy()]
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            result = update_search_in_database(request_id, updates, preserve_existing=True)
            
            assert result is True
            
            # Verify prompt was preserved
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['prompt'] == original_prompt
    
    def test_partial_update_without_preservation(self, valid_search_data):
        """Test partial update without preserving existing data."""
        request_id = valid_search_data['request_id']
        updates = {'status': 'failed', 'error': 'Test error'}
        
        with patch('database.supabase') as mock_supabase:
            mock_response = Mock()
            mock_response.data = [updates.copy()]
            mock_response.data[0]['request_id'] = request_id
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            result = update_search_in_database(request_id, updates, preserve_existing=False)
            
            assert result is True
            
            # Verify only updates + request_id were sent
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['request_id'] == request_id
            assert upsert_call_args['status'] == 'failed'
            assert upsert_call_args['error'] == 'Test error'
    
    def test_partial_update_nonexistent_search(self):
        """Test partial update of non-existent search."""
        request_id = str(uuid.uuid4())
        updates = {'status': 'completed'}
        
        with patch('database.get_search_from_database') as mock_get:
            mock_get.return_value = None  # Search not found
            
            from database import update_search_in_database
            
            with pytest.raises(ValueError) as exc_info:
                update_search_in_database(request_id, updates)
            
            assert "not found" in str(exc_info.value)
    
    def test_partial_update_invalid_request_id(self):
        """Test partial update with invalid request_id."""
        from database import update_search_in_database
        
        with pytest.raises(ValueError) as exc_info:
            update_search_in_database("", {'status': 'completed'})
        
        assert "request_id" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            update_search_in_database(None, {'status': 'completed'})
        
        assert "request_id" in str(exc_info.value)
    
    def test_partial_update_invalid_updates(self):
        """Test partial update with invalid updates parameter."""
        request_id = str(uuid.uuid4())
        
        from database import update_search_in_database
        
        with pytest.raises(ValueError) as exc_info:
            update_search_in_database(request_id, "not_a_dict")
        
        assert "updates must be a dictionary" in str(exc_info.value)
    
    def test_partial_update_empty_updates(self):
        """Test partial update with empty updates."""
        request_id = str(uuid.uuid4())
        
        from database import update_search_in_database
        
        result = update_search_in_database(request_id, {})
        
        # Should return True for empty updates (nothing to do)
        assert result is True
    
    def test_partial_update_with_prompt_change(self, valid_search_data):
        """Test partial update that changes the prompt."""
        request_id = valid_search_data['request_id']
        new_prompt = 'Updated prompt for testing'
        updates = {'prompt': new_prompt, 'status': 'processing'}
        
        with patch('database.supabase') as mock_supabase, \
             patch('database.get_search_from_database') as mock_get:
            
            # Setup mocks
            mock_get.return_value = valid_search_data
            updated_data = valid_search_data.copy()
            updated_data.update(updates)
            mock_response = Mock()
            mock_response.data = [updated_data]
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            result = update_search_in_database(request_id, updates)
            
            assert result is True
            
            # Verify prompt was updated
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['prompt'] == new_prompt


class TestBasicValidation:
    """Test suite for basic validation functionality."""
    
    def test_basic_validation_success(self, valid_search_data):
        """Test successful basic validation."""
        from database import _basic_search_validation
        
        result = _basic_search_validation(valid_search_data)
        
        assert result['request_id'] == valid_search_data['request_id']
        assert result['prompt'] == valid_search_data['prompt']
        assert result['status'] == valid_search_data['status']
    
    def test_basic_validation_missing_required_fields(self):
        """Test basic validation with missing required fields."""
        from database import _basic_search_validation
        
        # Missing prompt
        data = {'request_id': str(uuid.uuid4()), 'status': 'pending'}
        with pytest.raises(ValueError) as exc_info:
            _basic_search_validation(data)
        assert "prompt" in str(exc_info.value)
        
        # Missing request_id
        data = {'prompt': 'test prompt', 'status': 'pending'}
        with pytest.raises(ValueError) as exc_info:
            _basic_search_validation(data)
        assert "request_id" in str(exc_info.value)
        
        # Missing status
        data = {'request_id': str(uuid.uuid4()), 'prompt': 'test prompt'}
        with pytest.raises(ValueError) as exc_info:
            _basic_search_validation(data)
        assert "status" in str(exc_info.value)
    
    def test_basic_validation_type_conversion(self):
        """Test basic validation with type conversion."""
        from database import _basic_search_validation
        
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 123,  # Will be converted to string
            'status': 'pending'
        }
        
        result = _basic_search_validation(data)
        
        assert isinstance(result['prompt'], str)
        assert result['prompt'] == '123'
    
    def test_basic_validation_empty_prompt(self):
        """Test basic validation with empty prompt."""
        from database import _basic_search_validation
        
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': '   ',  # Whitespace only
            'status': 'pending'
        }
        
        with pytest.raises(ValueError) as exc_info:
            _basic_search_validation(data)
        assert "prompt must be a non-empty string" in str(exc_info.value)
    
    def test_basic_validation_invalid_status(self):
        """Test basic validation with invalid status."""
        from database import _basic_search_validation
        
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'test prompt',
            'status': 'invalid_status'
        }
        
        # Should not raise error but log warning
        result = _basic_search_validation(data)
        assert result['status'] == 'invalid_status'


class TestErrorHandling:
    """Test suite for error handling in storage operations."""
    
    def test_store_search_database_error(self, valid_search_data):
        """Test storage behavior when database operation fails."""
        with patch('database.supabase') as mock_supabase:
            # Setup mock to raise exception
            mock_table = Mock()
            mock_table.upsert.return_value.execute.side_effect = Exception("Database connection failed")
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database
            
            with pytest.raises(Exception) as exc_info:
                store_search_to_database(valid_search_data)
            
            assert "Database connection failed" in str(exc_info.value)
    
    def test_partial_update_database_error(self, valid_search_data):
        """Test partial update behavior when database operation fails."""
        request_id = valid_search_data['request_id']
        updates = {'status': 'completed'}
        
        with patch('database.supabase') as mock_supabase, \
             patch('database.get_search_from_database') as mock_get:
            
            # Setup mocks
            mock_get.return_value = valid_search_data
            mock_table = Mock()
            mock_table.upsert.return_value.execute.side_effect = Exception("Database error")
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            with pytest.raises(Exception) as exc_info:
                update_search_in_database(request_id, updates)
            
            assert "Database error" in str(exc_info.value)
    
    def test_validation_with_search_data_validator_unavailable(self, valid_search_data):
        """Test storage when SearchDataValidator is not available."""
        with patch('database.supabase') as mock_supabase, \
             patch('builtins.__import__', side_effect=ImportError("Module not found")):
            
            mock_response = Mock()
            mock_response.data = [{'id': 123}]
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database
            
            # Should fall back to basic validation
            result = store_search_to_database(valid_search_data)
            assert result == 123


class TestIntegrationScenarios:
    """Integration test scenarios for storage operations."""
    
    def test_full_storage_and_update_cycle(self, valid_search_data):
        """Test complete storage and update cycle."""
        request_id = valid_search_data['request_id']
        
        with patch('database.supabase') as mock_supabase:
            # Setup mocks for storage
            store_response = Mock()
            store_response.data = [valid_search_data.copy()]
            store_response.data[0]['id'] = 123
            
            # Setup mocks for update
            updated_data = valid_search_data.copy()
            updated_data['status'] = 'completed'
            update_response = Mock()
            update_response.data = [updated_data]
            
            mock_table = Mock()
            mock_table.upsert.return_value.execute.side_effect = [store_response, update_response]
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database, update_search_in_database
            
            # Test storage
            with patch('database.get_search_from_database', return_value=None):
                store_result = store_search_to_database(valid_search_data)
                assert store_result == 123
            
            # Test update
            with patch('database.get_search_from_database', return_value=valid_search_data):
                update_result = update_search_in_database(request_id, {'status': 'completed'})
                assert update_result is True
    
    def test_prompt_integrity_throughout_pipeline(self, valid_search_data):
        """Test that prompt integrity is maintained throughout the entire pipeline."""
        original_prompt = valid_search_data['prompt']
        request_id = valid_search_data['request_id']
        
        with patch('database.supabase') as mock_supabase:
            # Mock responses that preserve prompt
            responses = []
            for i in range(3):  # Multiple operations
                response = Mock()
                data = valid_search_data.copy()
                data['id'] = 123 + i
                response.data = [data]
                responses.append(response)
            
            mock_table = Mock()
            mock_table.upsert.return_value.execute.side_effect = responses
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database, update_search_in_database
            
            # Store initial data
            with patch('database.get_search_from_database', return_value=None):
                store_result = store_search_to_database(valid_search_data)
                assert store_result == 123
            
            # Update without changing prompt
            with patch('database.get_search_from_database', return_value=valid_search_data):
                update_result = update_search_in_database(request_id, {'status': 'processing'})
                assert update_result is True
            
            # Update with explicit prompt preservation
            with patch('database.get_search_from_database', return_value=valid_search_data):
                update_result = update_search_in_database(
                    request_id, 
                    {'status': 'completed'}, 
                    preserve_existing=True
                )
                assert update_result is True
            
            # Verify all upsert calls preserved the prompt
            for call in mock_table.upsert.call_args_list:
                upsert_data = call[0][0]
                assert upsert_data['prompt'] == original_prompt


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])