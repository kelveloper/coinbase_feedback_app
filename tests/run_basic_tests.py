#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Test Runner for Advanced Trade Insight Engine

This script runs tests that don't require external dependencies like pandas, streamlit, etc.
It focuses on testing the core logic and structure validation.

Usage:
    python tests/run_basic_tests.py [--verbose]

Requirements: 8.1, 8.4
"""

import sys
import os
import unittest
import time
import argparse
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'tests'))


def run_basic_tests(verbose=False):
    """Run basic tests that don't require external dependencies."""
    print("🧪 Advanced Trade Insight Engine - Basic Test Suite")
    print("=" * 60)
    print(f"Project Root: {project_root}")
    print(f"Verbose: {'✅ Enabled' if verbose else '❌ Disabled'}")
    print("=" * 60)
    
    start_time = time.time()
    
    # Discover and run basic functionality tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add basic functionality tests
    try:
        from test_basic_functionality import (
            TestBasicFunctionality, 
            TestStringOperations, 
            TestDataStructures
        )
        
        suite.addTest(loader.loadTestsFromTestCase(TestBasicFunctionality))
        suite.addTest(loader.loadTestsFromTestCase(TestStringOperations))
        suite.addTest(loader.loadTestsFromTestCase(TestDataStructures))
        
        print("✅ Basic functionality tests loaded")
        
    except ImportError as e:
        print(f"⚠️  Could not load basic functionality tests: {e}")
    
    # Add core logic tests
    try:
        from test_core_logic import (
            TestSentimentProcessing,
            TestThemeProcessing,
            TestStrategicGoalProcessing,
            TestSourceWeightCalculation,
            TestImpactScoreCalculation,
            TestDataValidation,
            TestFileOperations
        )
        
        suite.addTest(loader.loadTestsFromTestCase(TestSentimentProcessing))
        suite.addTest(loader.loadTestsFromTestCase(TestThemeProcessing))
        suite.addTest(loader.loadTestsFromTestCase(TestStrategicGoalProcessing))
        suite.addTest(loader.loadTestsFromTestCase(TestSourceWeightCalculation))
        suite.addTest(loader.loadTestsFromTestCase(TestImpactScoreCalculation))
        suite.addTest(loader.loadTestsFromTestCase(TestDataValidation))
        suite.addTest(loader.loadTestsFromTestCase(TestFileOperations))
        
        print("✅ Core logic tests loaded")
        
    except ImportError as e:
        print(f"⚠️  Could not load core logic tests: {e}")
    
    # Add integration tests
    try:
        from test_integration_basic import (
            TestDataPipelineIntegration,
            TestEndToEndWorkflowSimulation,
            TestErrorHandlingIntegration
        )
        
        suite.addTest(loader.loadTestsFromTestCase(TestDataPipelineIntegration))
        suite.addTest(loader.loadTestsFromTestCase(TestEndToEndWorkflowSimulation))
        suite.addTest(loader.loadTestsFromTestCase(TestErrorHandlingIntegration))
        
        print("✅ Integration tests loaded")
        
    except ImportError as e:
        print(f"⚠️  Could not load integration tests: {e}")
    
    # Try to add other tests that might work without dependencies
    test_modules = [
        'test_error_scenarios',
        'test_performance', 
        'test_e2e_workflow'
    ]
    
    for module_name in test_modules:
        try:
            module = __import__(module_name)
            # Try to find test classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, unittest.TestCase) and 
                    attr != unittest.TestCase):
                    try:
                        suite.addTest(loader.loadTestsFromTestCase(attr))
                        print(f"✅ Added tests from {module_name}.{attr_name}")
                    except Exception as e:
                        print(f"⚠️  Could not load {module_name}.{attr_name}: {e}")
        except ImportError:
            print(f"⚠️  Could not import {module_name}")
    
    # Run the tests
    runner = unittest.TextTestRunner(
        verbosity=2 if verbose else 1,
        stream=sys.stdout
    )
    
    print(f"\n🚀 Running {suite.countTestCases()} tests...")
    print("-" * 60)
    
    result = runner.run(suite)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 BASIC TEST SUITE SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.testsRun > 0:
        success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
        print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"Duration: {duration:.2f} seconds")
    print(f"Overall Result: {'✅ PASSED' if result.wasSuccessful() else '❌ FAILED'}")
    
    # Print detailed failure information if verbose
    if verbose and (result.failures or result.errors):
        print("\n" + "=" * 60)
        print("📋 DETAILED FAILURE INFORMATION")
        print("=" * 60)
        
        for test, traceback in result.failures:
            print(f"\n❌ FAILURE: {test}")
            print("-" * 40)
            print(traceback)
        
        for test, traceback in result.errors:
            print(f"\n💥 ERROR: {test}")
            print("-" * 40)
            print(traceback)
    
    return result.wasSuccessful()


def main():
    """Main entry point for the basic test runner."""
    parser = argparse.ArgumentParser(
        description="Run basic tests for Advanced Trade Insight Engine"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Run tests
    success = run_basic_tests(verbose=args.verbose)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()