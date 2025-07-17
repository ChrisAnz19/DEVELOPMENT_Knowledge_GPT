#!/usr/bin/env python3
"""
Script to run the integration tests for the logical assessment feature.
"""

import unittest
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the test modules
from test_integrated_logical_assessment import TestIntegratedLogicalAssessment

if __name__ == '__main__':
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestIntegratedLogicalAssessment))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())