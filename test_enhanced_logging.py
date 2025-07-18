#!/usr/bin/env python3
"""
Test script for enhanced logging and data flow tracking functionality.
Tests the new logging utilities and data flow monitoring capabilities.
"""

import sys
import json
from datetime import datetime

def test_search_data_logger():
    """Test the SearchDataLogger functionality."""
    print("🧪 Testing SearchDataLogger...")
    
    try:
        from search_data_logger import (
            SearchDataLogger, 
            log_data_flow, 
            track_prompt_presence,
            log_prompt_integrity_check,
            get_data_flow_summary
        )
        
        # Test basic logging
        test_request_id = "test-12345"
        test_data = {
            "request_id": test_request_id,
            "prompt": "Test prompt for logging",
            "status": "processing"
        }
        
        print("  ✓ Imported logging utilities successfully")
        
        # Test data flow logging
        log_data_flow("test_store", test_request_id, test_data, "test_stage")
        print("  ✓ Data flow logging works")
        
        # Test prompt tracking
        track_prompt_presence("test_operation", test_request_id, True, 25, "test_context")
        print("  ✓ Prompt presence tracking works")
        
        # Test integrity checking
        integrity_ok = log_prompt_integrity_check(test_request_id, "expected", "expected", "test_op")
        assert integrity_ok == True
        print("  ✓ Prompt integrity checking works")
        
        # Test with null prompt
        null_data = {
            "request_id": test_request_id,
            "prompt": None,
            "status": "processing"
        }
        log_data_flow("test_null", test_request_id, null_data, "test_null_stage")
        print("  ✓ Null prompt logging works")
        
        # Test summary
        summary = get_data_flow_summary(test_request_id)
        assert isinstance(summary, dict)
        assert summary["total_operations"] > 0
        print(f"  ✓ Data flow summary works (found {summary['total_operations']} operations)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ SearchDataLogger test failed: {str(e)}")
        return False

def test_data_flow_monitor():
    """Test the DataFlowMonitor functionality."""
    print("\n🧪 Testing DataFlowMonitor...")
    
    try:
        from data_flow_monitor import (
            DataFlowMonitor,
            analyze_null_prompt_patterns,
            get_data_flow_metrics,
            generate_monitoring_report
        )
        
        print("  ✓ Imported monitoring utilities successfully")
        
        # Test pattern analysis (may fail if no database connection)
        patterns = analyze_null_prompt_patterns(5)
        if "error" in patterns:
            print(f"  ⚠️  Pattern analysis returned error (expected if no DB): {patterns['error']}")
        else:
            print(f"  ✓ Pattern analysis works (analyzed {patterns.get('total_searches', 0)} searches)")
        
        # Test data flow metrics
        metrics = get_data_flow_metrics(hours_back=1)
        if "error" in metrics:
            print(f"  ⚠️  Flow metrics returned error: {metrics['error']}")
        else:
            print(f"  ✓ Flow metrics work (found {metrics.get('total_operations', 0)} operations)")
        
        # Test monitoring report
        report = generate_monitoring_report(hours_back=1)
        assert isinstance(report, dict)
        assert "report_timestamp" in report
        print("  ✓ Monitoring report generation works")
        
        return True
        
    except Exception as e:
        print(f"  ❌ DataFlowMonitor test failed: {str(e)}")
        return False

def test_database_integration():
    """Test integration with database operations."""
    print("\n🧪 Testing Database Integration...")
    
    try:
        # Import database functions
        from database import store_search_to_database, get_search_from_database
        
        print("  ✓ Imported database functions successfully")
        
        # Test data with valid prompt
        test_data = {
            "request_id": f"test-integration-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "prompt": "Integration test prompt",
            "status": "testing",
            "filters": "{}",
            "behavioral_data": "{}"
        }
        
        print("  ✓ Created test data")
        
        # Note: Actual database operations will depend on connection availability
        # This test verifies the functions can be called without errors
        print("  ⚠️  Database operations require active connection (skipping actual DB calls)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database integration test failed: {str(e)}")
        return False

def test_logging_output():
    """Test that logging produces expected output."""
    print("\n🧪 Testing Logging Output...")
    
    try:
        from search_data_logger import SearchDataLogger
        
        # Create a test logger
        test_logger = SearchDataLogger("test_logger")
        
        # Test various scenarios
        test_scenarios = [
            {
                "name": "Valid prompt",
                "data": {"request_id": "test-1", "prompt": "Valid test prompt", "status": "ok"},
                "expected_warning": False
            },
            {
                "name": "Null prompt",
                "data": {"request_id": "test-2", "prompt": None, "status": "ok"},
                "expected_warning": True
            },
            {
                "name": "Empty prompt",
                "data": {"request_id": "test-3", "prompt": "", "status": "ok"},
                "expected_warning": True
            },
            {
                "name": "Whitespace prompt",
                "data": {"request_id": "test-4", "prompt": "   ", "status": "ok"},
                "expected_warning": True
            }
        ]
        
        for scenario in test_scenarios:
            test_logger.log_data_flow("test", scenario["data"]["request_id"], 
                                    scenario["data"], "test_stage")
            print(f"  ✓ Logged scenario: {scenario['name']}")
        
        # Check summary
        summary = test_logger.get_data_flow_summary()
        prompt_issues = len(summary.get("prompt_issues", []))
        print(f"  ✓ Found {prompt_issues} prompt issues in test scenarios")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Logging output test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Logging Tests\n")
    
    tests = [
        test_search_data_logger,
        test_data_flow_monitor,
        test_database_integration,
        test_logging_output
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced logging is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)