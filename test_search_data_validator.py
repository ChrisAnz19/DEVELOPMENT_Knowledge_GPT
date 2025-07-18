#!/usr/bin/env python3
"""
Unit tests for SearchDataValidator and related validation functions.

Tests cover:
- Search data structure validation
- Prompt integrity checking
- Data flow tracking
- Error handling scenarios
- Edge cases and boundary conditions
"""

import unittest
import uuid
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from search_data_validator import (
    SearchDataValidator,
    PromptIntegrityChecker,
    SearchDataValidationError,
    PromptIntegrityError,
    validate_search_request,
    check_prompt_integrity
)


class TestSearchDataValidator(unittest.TestCase):
    """Test cases for SearchDataValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_request_id = str(uuid.uuid4())
        self.valid_search_data = {
            'request_id': self.valid_request_id,
            'prompt': 'Find software engineers in San Francisco',
            'status': 'pending',
            'max_candidates': 5,
            'filters': '{"location": "San Francisco"}',
            'behavioral_data': '{"personality": "analytical"}'
        }
        
        self.minimal_valid_data = {
            'request_id': self.valid_request_id,
            'prompt': 'Test prompt',
            'status': 'pending'
        }
    
    def test_validate_search_data_valid_input(self):
        """Test validation with valid search data."""
        result = SearchDataValidator.validate_search_data(self.valid_search_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['request_id'], self.valid_request_id)
        self.assertEqual(result['prompt'], 'Find software engineers in San Francisco')
        self.assertEqual(result['status'], 'pending')
    
    def test_validate_search_data_minimal_valid(self):
        """Test validation with minimal valid data."""
        result = SearchDataValidator.validate_search_data(self.minimal_valid_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['request_id'], self.valid_request_id)
        self.assertEqual(result['prompt'], 'Test prompt')
        self.assertEqual(result['status'], 'pending')
    
    def test_validate_search_data_missing_required_fields(self):
        """Test validation fails with missing required fields."""
        # Missing request_id
        invalid_data = {
            'prompt': 'Test prompt',
            'status': 'pending'
        }
        
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator.validate_search_data(invalid_data)
        
        self.assertIn('Missing required fields', str(context.exception))
        self.assertIn('request_id', str(context.exception))
    
    def test_validate_search_data_invalid_types(self):
        """Test validation fails with invalid field types."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['max_candidates'] = 'not_an_integer'
        
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator.validate_search_data(invalid_data)
        
        self.assertIn('Invalid type for max_candidates', str(context.exception))
    
    def test_validate_search_data_invalid_status(self):
        """Test validation fails with invalid status."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['status'] = 'invalid_status'
        
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator.validate_search_data(invalid_data)
        
        self.assertIn('Invalid status', str(context.exception))
    
    def test_validate_search_data_invalid_request_id(self):
        """Test validation fails with invalid request_id format."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['request_id'] = 'not-a-uuid'
        
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator.validate_search_data(invalid_data)
        
        self.assertIn('Invalid request_id format', str(context.exception))
    
    def test_validate_search_data_not_dict(self):
        """Test validation fails when input is not a dictionary."""
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator.validate_search_data("not a dict")
        
        self.assertIn('must be a dictionary', str(context.exception))
    
    def test_ensure_prompt_integrity_valid(self):
        """Test prompt integrity with valid prompt."""
        result = SearchDataValidator.ensure_prompt_integrity(self.valid_search_data)
        
        self.assertEqual(result['prompt'], 'Find software engineers in San Francisco')
    
    def test_ensure_prompt_integrity_none_prompt(self):
        """Test prompt integrity fails with None prompt."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = None
        
        with self.assertRaises(PromptIntegrityError) as context:
            SearchDataValidator.ensure_prompt_integrity(invalid_data)
        
        self.assertIn('Prompt is None', str(context.exception))
    
    def test_ensure_prompt_integrity_empty_prompt(self):
        """Test prompt integrity fails with empty prompt."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = '   '  # Whitespace only
        
        with self.assertRaises(PromptIntegrityError) as context:
            SearchDataValidator.ensure_prompt_integrity(invalid_data)
        
        self.assertIn('empty or whitespace-only', str(context.exception))
    
    def test_ensure_prompt_integrity_non_string_prompt(self):
        """Test prompt integrity converts non-string to string."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = 12345
        
        with patch('search_data_validator.logger') as mock_logger:
            result = SearchDataValidator.ensure_prompt_integrity(invalid_data)
            
            self.assertEqual(result['prompt'], '12345')
            mock_logger.warning.assert_called_once()
    
    def test_validate_prompt_preservation_identical(self):
        """Test prompt preservation with identical prompts."""
        original = {'prompt': 'Test prompt'}
        processed = {'prompt': 'Test prompt'}
        
        result = SearchDataValidator.validate_prompt_preservation(original, processed)
        self.assertTrue(result)
    
    def test_validate_prompt_preservation_different(self):
        """Test prompt preservation with different prompts."""
        original = {'prompt': 'Original prompt'}
        processed = {'prompt': 'Different prompt'}
        
        with patch('search_data_validator.logger') as mock_logger:
            result = SearchDataValidator.validate_prompt_preservation(original, processed)
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once()
    
    def test_validate_prompt_preservation_both_empty(self):
        """Test prompt preservation with both prompts empty."""
        original = {'prompt': ''}
        processed = {'prompt': ''}
        
        result = SearchDataValidator.validate_prompt_preservation(original, processed)
        self.assertTrue(result)
    
    @patch('search_data_validator.logger')
    def test_log_data_flow(self, mock_logger):
        """Test data flow logging."""
        SearchDataValidator.log_data_flow('test_operation', self.valid_search_data, 'test_stage')
        
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        self.assertIn('test_operation', call_args)
        self.assertIn('test_stage', call_args)
        self.assertIn(self.valid_request_id, call_args)
    
    def test_analyze_search_data_structure_valid(self):
        """Test analysis of valid search data structure."""
        analysis = SearchDataValidator.analyze_search_data_structure(self.valid_search_data)
        
        self.assertTrue(analysis['valid'])
        self.assertEqual(len(analysis['issues']), 0)
        self.assertTrue(analysis['prompt_analysis']['valid'])
        self.assertTrue(analysis['field_analysis']['request_id']['present'])
        self.assertTrue(analysis['field_analysis']['prompt']['present'])
    
    def test_analyze_search_data_structure_invalid(self):
        """Test analysis of invalid search data structure."""
        invalid_data = {
            'request_id': 'invalid-uuid',
            'prompt': '',  # Empty prompt
            'status': 'invalid_status'
        }
        
        analysis = SearchDataValidator.analyze_search_data_structure(invalid_data)
        
        self.assertFalse(analysis['valid'])
        self.assertGreater(len(analysis['issues']), 0)
        self.assertFalse(analysis['prompt_analysis']['valid'])
    
    def test_normalize_json_fields_dict_to_string(self):
        """Test normalization of dict fields to JSON strings."""
        data_with_dict = self.valid_search_data.copy()
        data_with_dict['filters'] = {"location": "San Francisco"}
        
        result = SearchDataValidator._normalize_json_fields(data_with_dict)
        
        self.assertIsInstance(result['filters'], str)
        self.assertEqual(json.loads(result['filters']), {"location": "San Francisco"})
    
    def test_normalize_json_fields_invalid_json_string(self):
        """Test normalization fails with invalid JSON string."""
        data_with_invalid_json = self.valid_search_data.copy()
        data_with_invalid_json['filters'] = '{"invalid": json}'
        
        with self.assertRaises(SearchDataValidationError) as context:
            SearchDataValidator._normalize_json_fields(data_with_invalid_json)
        
        self.assertIn('Invalid JSON in filters', str(context.exception))


class TestPromptIntegrityChecker(unittest.TestCase):
    """Test cases for PromptIntegrityChecker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_request_id = str(uuid.uuid4())
        self.valid_search_data = {
            'request_id': self.valid_request_id,
            'prompt': 'Test prompt',
            'status': 'pending'
        }
    
    def test_check_prompt_at_stage_valid(self):
        """Test prompt integrity check at stage with valid data."""
        is_valid, message = PromptIntegrityChecker.check_prompt_at_stage(
            self.valid_search_data, 'test_stage'
        )
        
        self.assertTrue(is_valid)
        self.assertIn('verified', message)
        self.assertIn('test_stage', message)
    
    def test_check_prompt_at_stage_none_prompt(self):
        """Test prompt integrity check fails with None prompt."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = None
        
        is_valid, message = PromptIntegrityChecker.check_prompt_at_stage(
            invalid_data, 'test_stage'
        )
        
        self.assertFalse(is_valid)
        self.assertIn('Prompt is None', message)
    
    def test_check_prompt_at_stage_empty_prompt(self):
        """Test prompt integrity check fails with empty prompt."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = '   '
        
        is_valid, message = PromptIntegrityChecker.check_prompt_at_stage(
            invalid_data, 'test_stage'
        )
        
        self.assertFalse(is_valid)
        self.assertIn('empty', message)
    
    def test_check_prompt_at_stage_expected_prompt_match(self):
        """Test prompt integrity check with matching expected prompt."""
        is_valid, message = PromptIntegrityChecker.check_prompt_at_stage(
            self.valid_search_data, 'test_stage', 'Test prompt'
        )
        
        self.assertTrue(is_valid)
        self.assertIn('verified', message)
    
    def test_check_prompt_at_stage_expected_prompt_mismatch(self):
        """Test prompt integrity check fails with mismatched expected prompt."""
        is_valid, message = PromptIntegrityChecker.check_prompt_at_stage(
            self.valid_search_data, 'test_stage', 'Different prompt'
        )
        
        self.assertFalse(is_valid)
        self.assertIn('mismatch', message)
    
    def test_track_prompt_changes_no_change(self):
        """Test tracking when prompt doesn't change."""
        original = self.valid_search_data.copy()
        modified = self.valid_search_data.copy()
        
        tracking_info = PromptIntegrityChecker.track_prompt_changes(
            original, modified, 'test_operation'
        )
        
        self.assertFalse(tracking_info['prompt_changed'])
        self.assertEqual(len(tracking_info['changes']), 0)
        self.assertEqual(tracking_info['operation'], 'test_operation')
    
    def test_track_prompt_changes_with_change(self):
        """Test tracking when prompt changes."""
        original = self.valid_search_data.copy()
        modified = self.valid_search_data.copy()
        modified['prompt'] = 'Modified prompt'
        
        with patch('search_data_validator.logger') as mock_logger:
            tracking_info = PromptIntegrityChecker.track_prompt_changes(
                original, modified, 'test_operation'
            )
            
            self.assertTrue(tracking_info['prompt_changed'])
            self.assertEqual(len(tracking_info['changes']), 1)
            self.assertEqual(tracking_info['changes'][0]['field'], 'prompt')
            mock_logger.warning.assert_called_once()


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_request_id = str(uuid.uuid4())
        self.valid_search_data = {
            'request_id': self.valid_request_id,
            'prompt': 'Test prompt',
            'status': 'pending'
        }
    
    def test_validate_search_request_valid(self):
        """Test validate_search_request convenience function with valid data."""
        result = validate_search_request(self.valid_search_data)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['prompt'], 'Test prompt')
    
    def test_validate_search_request_invalid(self):
        """Test validate_search_request convenience function with invalid data."""
        invalid_data = {'prompt': None}
        
        with self.assertRaises(SearchDataValidationError):
            validate_search_request(invalid_data)
    
    def test_check_prompt_integrity_valid(self):
        """Test check_prompt_integrity convenience function with valid data."""
        result = check_prompt_integrity(self.valid_search_data)
        self.assertTrue(result)
    
    def test_check_prompt_integrity_invalid(self):
        """Test check_prompt_integrity convenience function with invalid data."""
        invalid_data = self.valid_search_data.copy()
        invalid_data['prompt'] = None
        
        result = check_prompt_integrity(invalid_data)
        self.assertFalse(result)


class TestEdgeCases(unittest.TestCase):
    """Test cases for edge cases and boundary conditions."""
    
    def test_very_long_prompt(self):
        """Test validation with very long prompt."""
        long_prompt = 'A' * 10000  # 10k character prompt
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': long_prompt,
            'status': 'pending'
        }
        
        result = SearchDataValidator.validate_search_data(data)
        self.assertEqual(result['prompt'], long_prompt)
    
    def test_unicode_prompt(self):
        """Test validation with unicode characters in prompt."""
        unicode_prompt = 'Find engineers in 北京 with émigré background 🚀'
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': unicode_prompt,
            'status': 'pending'
        }
        
        result = SearchDataValidator.validate_search_data(data)
        self.assertEqual(result['prompt'], unicode_prompt)
    
    def test_complex_json_fields(self):
        """Test validation with complex nested JSON in fields."""
        complex_filters = {
            'location': ['San Francisco', 'New York'],
            'skills': {
                'required': ['Python', 'JavaScript'],
                'preferred': ['React', 'Django']
            },
            'experience': {'min': 3, 'max': 10}
        }
        
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'Complex search',
            'status': 'pending',
            'filters': complex_filters
        }
        
        result = SearchDataValidator.validate_search_data(data)
        self.assertIsInstance(result['filters'], str)
        self.assertEqual(json.loads(result['filters']), complex_filters)
    
    def test_all_valid_statuses(self):
        """Test validation with all valid status values."""
        valid_statuses = ['pending', 'processing', 'completed', 'failed', 'cancelled']
        
        for status in valid_statuses:
            data = {
                'request_id': str(uuid.uuid4()),
                'prompt': f'Test prompt for {status}',
                'status': status
            }
            
            result = SearchDataValidator.validate_search_data(data)
            self.assertEqual(result['status'], status)
    
    def test_empty_optional_fields(self):
        """Test validation with empty optional fields."""
        data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'Test prompt',
            'status': 'pending',
            'filters': '',
            'behavioral_data': '',
            'error': ''
        }
        
        result = SearchDataValidator.validate_search_data(data)
        self.assertEqual(result['prompt'], 'Test prompt')


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)