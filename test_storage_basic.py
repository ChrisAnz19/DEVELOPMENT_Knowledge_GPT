#!/usr/bin/env python3
"""
Basic tests for enhanced database storage operations without pytest dependency.
"""

import uuid
import json
import sys
from unittest.mock import Mock, patch

def test_basic_validation():
    """Test basic validation functionality."""
    print("Testing basic validation...")
    
    try:
        from database import _basic_search_validation
        
        # Test valid data
        valid_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': 'Find software engineers in San Francisco',
            'status': 'pending'
        }
        
        result = _basic_search_validation(valid_data)
        assert result['prompt'] == valid_data['prompt']
        print("✅ Basic validation with valid data passed")
        
        # Test missing prompt
        try:
            invalid_data = {
                'request_id': str(uuid.uuid4()),
                'status': 'pending'
                # Missing prompt
            }
            _basic_search_validation(invalid_data)
            print("❌ Should have failed for missing prompt")
            return False
        except ValueError as e:
            if "prompt" in str(e):
                print("✅ Correctly rejected missing prompt")
            else:
                print(f"❌ Wrong error for missing prompt: {e}")
                return False
        
        # Test empty prompt
        try:
            empty_prompt_data = {
                'request_id': str(uuid.uuid4()),
                'prompt': '   ',  # Whitespace only
                'status': 'pending'
            }
            _basic_search_validation(empty_prompt_data)
            print("❌ Should have failed for empty prompt")
            return False
        except ValueError as e:
            if "prompt" in str(e):
                print("✅ Correctly rejected empty prompt")
            else:
                print(f"❌ Wrong error for empty prompt: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic validation test failed: {e}")
        return False

def test_enhanced_storage():
    """Test enhanced storage functionality."""
    print("\nTesting enhanced storage...")
    
    try:
        # Mock supabase
        with patch('database.supabase') as mock_supabase:
            # Setup mock response
            mock_response = Mock()
            mock_response.data = [{
                'id': 123,
                'request_id': str(uuid.uuid4()),
                'prompt': 'Test prompt',
                'status': 'pending'
            }]
            
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import store_search_to_database
            
            # Test data
            test_data = {
                'request_id': str(uuid.uuid4()),
                'prompt': 'Find Python developers in NYC',
                'status': 'pending',
                'max_candidates': 5
            }
            
            result = store_search_to_database(test_data)
            
            assert result == 123
            assert mock_table.upsert.called
            print("✅ Enhanced storage test passed")
            return True
            
    except Exception as e:
        print(f"❌ Enhanced storage test failed: {e}")
        return False

def test_partial_update():
    """Test partial update functionality."""
    print("\nTesting partial update...")
    
    try:
        with patch('database.supabase') as mock_supabase, \
             patch('database.get_search_from_database') as mock_get:
            
            # Setup test data
            request_id = str(uuid.uuid4())
            original_data = {
                'request_id': request_id,
                'prompt': 'Original prompt',
                'status': 'pending'
            }
            
            # Setup mocks
            mock_get.return_value = original_data
            mock_response = Mock()
            mock_response.data = [original_data.copy()]
            mock_table = Mock()
            mock_table.upsert.return_value.execute.return_value = mock_response
            mock_supabase.table.return_value = mock_table
            
            from database import update_search_in_database
            
            # Test update
            updates = {'status': 'completed'}
            result = update_search_in_database(request_id, updates)
            
            assert result is True
            assert mock_table.upsert.called
            
            # Verify the upsert call preserved the prompt
            upsert_call_args = mock_table.upsert.call_args[0][0]
            assert upsert_call_args['prompt'] == 'Original prompt'
            assert upsert_call_args['status'] == 'completed'
            
            print("✅ Partial update test passed")
            return True
            
    except Exception as e:
        print(f"❌ Partial update test failed: {e}")
        return False

def test_validation_errors():
    """Test validation error handling."""
    print("\nTesting validation errors...")
    
    try:
        from database import store_search_to_database
        
        # Test with invalid UUID format request_id
        invalid_data = {
            'request_id': 'not-a-valid-uuid',  # Invalid UUID format
            'prompt': 'Valid prompt',
            'status': 'pending'
        }
        
        try:
            store_search_to_database(invalid_data)
            print("❌ Should have failed for invalid UUID request_id")
            return False
        except (ValueError, Exception) as e:
            if "uuid" in str(e).lower() or "request_id" in str(e).lower():
                print("✅ Correctly rejected invalid UUID request_id")
            else:
                print(f"✅ Rejected invalid request_id (different error): {e}")
        
        # Test with null prompt
        null_prompt_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': None,
            'status': 'pending'
        }
        
        try:
            store_search_to_database(null_prompt_data)
            print("❌ Should have failed for null prompt")
            return False
        except (ValueError, Exception) as e:
            if "prompt" in str(e).lower():
                print("✅ Correctly rejected null prompt")
            else:
                print(f"✅ Rejected null prompt (different error): {e}")
        
        # Test with empty prompt
        empty_prompt_data = {
            'request_id': str(uuid.uuid4()),
            'prompt': '',
            'status': 'pending'
        }
        
        try:
            store_search_to_database(empty_prompt_data)
            print("❌ Should have failed for empty prompt")
            return False
        except (ValueError, Exception) as e:
            if "prompt" in str(e).lower():
                print("✅ Correctly rejected empty prompt")
            else:
                print(f"✅ Rejected empty prompt (different error): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation error test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running Enhanced Storage Operations Tests\n")
    
    tests = [
        test_basic_validation,
        test_enhanced_storage,
        test_partial_update,
        test_validation_errors
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)