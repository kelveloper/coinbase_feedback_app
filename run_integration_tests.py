#!/usr/bin/env python3
"""
Integration Test Runner for Advanced Trade Insight Engine

This script runs comprehensive integration tests for the main execution pipeline,
including end-to-end workflow testing, error scenario validation, and performance monitoring.

Usage:
    python run_integration_tests.py [--verbose] [--coverage]

Requirements: 7.4, 7.5, 7.6
"""

import sys
import os
import unittest
import argparse
from pathlib import Path

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'tests'))


def discover_and_run_tests(verbose: bool = False, pattern: str = 'test_*.py') -> bool:
    """
    Discover and run integration tests.
    
    Args:
        verbose (bool): Enable verbose test output
        pattern (str): Test file pattern to match
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Set up test discovery
    test_dir = project_root / 'tests' / 'test_integration'
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        return False
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(test_dir),
        pattern=pattern,
        top_level_dir=str(project_root)
    )
    
    # Configure test runner
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        stream=sys.stdout,
        buffer=True,
        failfast=False
    )
    
    print("🚀 Running Advanced Trade Insight Engine Integration Tests")
    print("=" * 60)
    
    # Run tests
    result = runner.run(suite)
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 TEST EXECUTION SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {total_tests - failures - errors - skipped}")
    print(f"❌ Failed: {failures}")
    print(f"💥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    
    success_rate = ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Display detailed failure information
    if failures:
        print(f"\n❌ FAILURES ({failures}):")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"  {i}. {test}")
            if verbose:
                print(f"     {traceback.split('AssertionError:')[-1].strip()}")
    
    if errors:
        print(f"\n💥 ERRORS ({errors}):")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"  {i}. {test}")
            if verbose:
                print(f"     {traceback.split('Exception:')[-1].strip()}")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if result.wasSuccessful():
        print("  ✅ All integration tests passed!")
        print("  ✅ The main pipeline is ready for production use")
        print("  ✅ Consider running performance benchmarks")
    else:
        print("  ❌ Some tests failed - review the failures above")
        print("  🔍 Check data file integrity and permissions")
        print("  🛠️  Fix issues before deploying to production")
        print("  📋 Run tests again after making fixes")
    
    return result.wasSuccessful()


def run_specific_test_class(class_name: str, verbose: bool = False) -> bool:
    """
    Run a specific test class.
    
    Args:
        class_name (str): Name of the test class to run
        verbose (bool): Enable verbose output
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    try:
        # Import the test module
        from tests.test_integration.test_main_pipeline import TestMainPipelineIntegration, TestErrorScenarios
        
        # Map class names to actual classes
        test_classes = {
            'TestMainPipelineIntegration': TestMainPipelineIntegration,
            'TestErrorScenarios': TestErrorScenarios
        }
        
        if class_name not in test_classes:
            print(f"❌ Test class '{class_name}' not found")
            print(f"Available classes: {', '.join(test_classes.keys())}")
            return False
        
        # Create test suite for specific class
        suite = unittest.TestLoader().loadTestsFromTestCase(test_classes[class_name])
        
        # Run tests
        verbosity = 2 if verbose else 1
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Failed to import test class: {e}")
        return False


def check_test_environment() -> bool:
    """
    Check that the test environment is properly set up.
    
    Returns:
        bool: True if environment is ready, False otherwise
    """
    print("🔍 Checking test environment...")
    
    # Check required directories
    required_dirs = [
        project_root / 'src',
        project_root / 'tests',
        project_root / 'tests' / 'test_integration'
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"❌ Required directory missing: {dir_path}")
            return False
        print(f"✅ Found: {dir_path}")
    
    # Check required files
    required_files = [
        project_root / 'main.py',
        project_root / 'config.py',
        project_root / 'tests' / 'test_integration' / 'test_main_pipeline.py'
    ]
    
    for file_path in required_files:
        if not file_path.exists():
            print(f"❌ Required file missing: {file_path}")
            return False
        print(f"✅ Found: {file_path}")
    
    # Check Python path
    try:
        import main
        import config
        print("✅ Main modules can be imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    print("✅ Test environment is ready")
    return True


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Integration Test Runner for Advanced Trade Insight Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_integration_tests.py                    # Run all integration tests
  python run_integration_tests.py --verbose          # Run with verbose output
  python run_integration_tests.py --class TestMainPipelineIntegration  # Run specific class
  python run_integration_tests.py --check-env        # Check test environment only
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose test output'
    )
    
    parser.add_argument(
        '--class',
        dest='test_class',
        help='Run specific test class only'
    )
    
    parser.add_argument(
        '--pattern',
        default='test_*.py',
        help='Test file pattern to match (default: test_*.py)'
    )
    
    parser.add_argument(
        '--check-env',
        action='store_true',
        help='Check test environment setup only'
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main test runner entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()
    
    print("🧪 Advanced Trade Insight Engine - Integration Test Runner")
    print("=" * 60)
    
    # Check environment first
    if not check_test_environment():
        print("❌ Test environment check failed")
        return 1
    
    if args.check_env:
        print("✅ Test environment check completed successfully")
        return 0
    
    try:
        # Run specific test class if requested
        if args.test_class:
            success = run_specific_test_class(args.test_class, args.verbose)
        else:
            # Run all integration tests
            success = discover_and_run_tests(args.verbose, args.pattern)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during test execution: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)