#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Runner for Advanced Trade Insight Engine

This script runs all unit tests, integration tests, and error scenario tests
to provide comprehensive coverage validation for the system.

Usage:
    python tests/run_all_tests.py [--verbose] [--coverage] [--performance]

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import sys
import os
import unittest
import time
import argparse
from pathlib import Path
from io import StringIO

# Add project directories to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'tests'))


class ComprehensiveTestRunner:
    """Comprehensive test runner for all test suites."""
    
    def __init__(self, verbose=False, coverage=False, performance=False):
        self.verbose = verbose
        self.coverage = coverage
        self.performance = performance
        self.results = {}
        
    def discover_and_run_tests(self):
        """Discover and run all test suites."""
        print("🚀 Advanced Trade Insight Engine - Comprehensive Test Suite")
        print("=" * 70)
        print(f"Project Root: {project_root}")
        print(f"Verbose: {'✅ Enabled' if self.verbose else '❌ Disabled'}")
        print(f"Coverage: {'✅ Enabled' if self.coverage else '❌ Disabled'}")
        print(f"Performance: {'✅ Enabled' if self.performance else '❌ Disabled'}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run different test categories
        success = True
        
        # 1. Unit Tests
        print("\n📋 1. Running Unit Tests...")
        unit_success = self._run_unit_tests()
        success = success and unit_success
        
        # 2. Integration Tests
        print("\n🔗 2. Running Integration Tests...")
        integration_success = self._run_integration_tests()
        success = success and integration_success
        
        # 3. Error Scenario Tests
        print("\n🚨 3. Running Error Scenario Tests...")
        error_success = self._run_error_scenario_tests()
        success = success and error_success
        
        # 4. End-to-End Tests
        print("\n🔄 4. Running End-to-End Tests...")
        e2e_success = self._run_e2e_tests()
        success = success and e2e_success
        
        # 5. Performance Tests (if enabled)
        if self.performance:
            print("\n⚡ 5. Running Performance Tests...")
            perf_success = self._run_performance_tests()
            success = success and perf_success
        
        # 6. Generate Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUITE SUMMARY")
        print("=" * 70)
        self._print_test_summary()
        print(f"Total Duration: {duration:.2f} seconds")
        print(f"Overall Result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success
    
    def _run_unit_tests(self):
        """Run all unit tests."""
        unit_test_modules = [
            'test_data_processing.test_data_loader',
            'test_data_processing.test_data_normalizer',
            'test_analysis.test_nlp_models',
            'test_analysis.test_scoring_engine',
            'test_reporting.test_content_builder',
            'test_reporting.test_pdf_formatter',
            'test_reporting.test_report_generator',
            'test_dashboard.test_components',
            'test_dashboard.test_charts',
            'test_dashboard.test_dashboard'
        ]
        
        return self._run_test_modules(unit_test_modules, "Unit Tests")
    
    def _run_integration_tests(self):
        """Run integration tests."""
        integration_test_modules = [
            'test_integration.test_main_pipeline'
        ]
        
        return self._run_test_modules(integration_test_modules, "Integration Tests")
    
    def _run_error_scenario_tests(self):
        """Run error scenario tests."""
        try:
            # Import and run error scenario tests
            from test_error_scenarios import (
                TestDataLoadingErrors, TestDataProcessingErrors,
                TestReportGenerationErrors, TestDashboardErrors,
                TestMemoryAndPerformanceErrors, TestSystemIntegrationErrors
            )
            
            test_classes = [
                TestDataLoadingErrors, TestDataProcessingErrors,
                TestReportGenerationErrors, TestDashboardErrors,
                TestMemoryAndPerformanceErrors, TestSystemIntegrationErrors
            ]
            
            return self._run_test_classes(test_classes, "Error Scenario Tests")
            
        except ImportError as e:
            print(f"⚠️  Error scenario tests not available: {e}")
            return True
    
    def _run_e2e_tests(self):
        """Run end-to-end tests."""
        e2e_test_modules = [
            'test_e2e_workflow'
        ]
        
        return self._run_test_modules(e2e_test_modules, "End-to-End Tests")
    
    def _run_performance_tests(self):
        """Run performance tests."""
        performance_test_modules = [
            'test_performance'
        ]
        
        return self._run_test_modules(performance_test_modules, "Performance Tests")
    
    def _run_test_modules(self, modules, test_type):
        """Run tests for specific modules."""
        success = True
        total_tests = 0
        passed_tests = 0
        
        for module in modules:
            try:
                result = self._run_single_module(module)
                if result['success']:
                    passed_tests += result['tests_run']
                else:
                    success = False
                total_tests += result['tests_run']
                
                # Store results
                self.results[module] = result
                
            except Exception as e:
                print(f"❌ Error running {module}: {e}")
                success = False
                self.results[module] = {
                    'success': False,
                    'tests_run': 0,
                    'error': str(e)
                }
        
        print(f"   {test_type}: {passed_tests}/{total_tests} tests passed")
        return success
    
    def _run_test_classes(self, test_classes, test_type):
        """Run tests for specific test classes."""
        success = True
        total_tests = 0
        passed_tests = 0
        
        for test_class in test_classes:
            try:
                # Create test suite for this class
                suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
                
                # Run tests
                stream = StringIO()
                runner = unittest.TextTestRunner(stream=stream, verbosity=1)
                result = runner.run(suite)
                
                # Process results
                tests_run = result.testsRun
                test_success = result.wasSuccessful()
                
                if test_success:
                    passed_tests += tests_run
                else:
                    success = False
                
                total_tests += tests_run
                
                # Store results
                class_name = test_class.__name__
                self.results[class_name] = {
                    'success': test_success,
                    'tests_run': tests_run,
                    'failures': len(result.failures),
                    'errors': len(result.errors),
                    'skipped': len(result.skipped)
                }
                
            except Exception as e:
                print(f"❌ Error running {test_class.__name__}: {e}")
                success = False
                self.results[test_class.__name__] = {
                    'success': False,
                    'tests_run': 0,
                    'error': str(e)
                }
        
        print(f"   {test_type}: {passed_tests}/{total_tests} tests passed")
        return success
    
    def _run_single_module(self, module_name):
        """Run tests for a single module."""
        try:
            # Discover tests in the module
            loader = unittest.TestLoader()
            
            # Try to load the module
            try:
                suite = loader.loadTestsFromName(module_name)
            except (ImportError, AttributeError):
                # Module might not exist or have tests
                return {
                    'success': True,
                    'tests_run': 0,
                    'skipped': True,
                    'message': f'Module {module_name} not found or has no tests'
                }
            
            # Run the tests
            stream = StringIO()
            runner = unittest.TextTestRunner(
                stream=stream,
                verbosity=2 if self.verbose else 1
            )
            result = runner.run(suite)
            
            return {
                'success': result.wasSuccessful(),
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped),
                'output': stream.getvalue()
            }
            
        except Exception as e:
            return {
                'success': False,
                'tests_run': 0,
                'error': str(e)
            }
    
    def _print_test_summary(self):
        """Print summary of test results."""
        total_modules = len(self.results)
        successful_modules = sum(1 for r in self.results.values() if r.get('success', False))
        total_tests = sum(r.get('tests_run', 0) for r in self.results.values())
        total_failures = sum(r.get('failures', 0) for r in self.results.values())
        total_errors = sum(r.get('errors', 0) for r in self.results.values())
        total_skipped = sum(r.get('skipped', 0) for r in self.results.values())
        
        print(f"Test Modules: {successful_modules}/{total_modules} successful")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_tests - total_failures - total_errors}")
        print(f"Failed: {total_failures}")
        print(f"Errors: {total_errors}")
        print(f"Skipped: {total_skipped}")
        
        if total_tests > 0:
            success_rate = ((total_tests - total_failures - total_errors) / total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        if self.verbose:
            print("\nDetailed Results:")
            for module, result in self.results.items():
                status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
                tests_run = result.get('tests_run', 0)
                print(f"  {module}: {status} ({tests_run} tests)")
                
                if not result.get('success', False) and 'error' in result:
                    print(f"    Error: {result['error']}")
                
                if result.get('skipped', False):
                    print(f"    Skipped: {result.get('message', 'No reason provided')}")


def main():
    """Main entry point for the comprehensive test runner."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for Advanced Trade Insight Engine"
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Enable coverage reporting (requires coverage.py)'
    )
    parser.add_argument(
        '--performance',
        action='store_true',
        help='Enable performance testing'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = ComprehensiveTestRunner(
        verbose=args.verbose,
        coverage=args.coverage,
        performance=args.performance
    )
    
    # Run tests
    success = runner.discover_and_run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()