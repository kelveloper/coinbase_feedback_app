#!/usr/bin/env python3
"""
Comprehensive Test Runner for Advanced Trade Insight Engine

This script runs the complete testing suite including:
- Unit tests for all modules
- Integration tests for data pipeline
- End-to-end tests with mock data
- Performance tests for large datasets
- Error scenario testing
- Coverage reporting (target: 80%+)

Usage:
    python run_comprehensive_tests.py [--verbose] [--coverage] [--performance] [--error-scenarios]

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project directories to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'tests'))


class ComprehensiveTestRunner:
    """Comprehensive test runner for the Advanced Trade Insight Engine."""
    
    def __init__(self, verbose: bool = False, coverage: bool = True, 
                 performance: bool = True, error_scenarios: bool = True):
        self.verbose = verbose
        self.coverage = coverage
        self.performance = performance
        self.error_scenarios = error_scenarios
        self.project_root = project_root
        self.test_results = {}
        
    def run_tests(self) -> bool:
        """Run the complete testing suite."""
        print("🚀 Advanced Trade Insight Engine - Comprehensive Testing Suite")
        print("=" * 70)
        print(f"Project Root: {self.project_root}")
        print(f"Coverage: {'✅ Enabled' if self.coverage else '❌ Disabled'}")
        print(f"Performance: {'✅ Enabled' if self.performance else '❌ Disabled'}")
        print(f"Error Scenarios: {'✅ Enabled' if self.error_scenarios else '❌ Disabled'}")
        print("=" * 70)
        
        start_time = time.time()
        
        # Run different test categories
        success = True
        
        # 1. Unit Tests
        print("\n📋 1. Running Unit Tests...")
        if not self._run_unit_tests():
            success = False
            
        # 2. Integration Tests
        print("\n🔗 2. Running Integration Tests...")
        if not self._run_integration_tests():
            success = False
            
        # 3. End-to-End Tests
        print("\n🔄 3. Running End-to-End Tests...")
        if not self._run_e2e_tests():
            success = False
            
        # 4. Performance Tests
        if self.performance:
            print("\n⚡ 4. Running Performance Tests...")
            if not self._run_performance_tests():
                success = False
                
        # 5. Error Scenario Tests
        if self.error_scenarios:
            print("\n🚨 5. Running Error Scenario Tests...")
            if not self._run_error_scenario_tests():
                success = False
                
        # 6. Coverage Report
        if self.coverage:
            print("\n📊 6. Generating Coverage Report...")
            self._generate_coverage_report()
            
        # 7. Test Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST SUITE SUMMARY")
        print("=" * 70)
        self._print_test_summary()
        print(f"Total Duration: {duration:.2f} seconds")
        print(f"Overall Result: {'✅ PASSED' if success else '❌ FAILED'}")
        
        return success
    
    def _run_unit_tests(self) -> bool:
        """Run unit tests for all modules."""
        test_modules = [
            'tests.test_data_processing.test_data_loader',
            'tests.test_data_processing.test_data_normalizer',
            'tests.test_analysis.test_nlp_models',
            'tests.test_analysis.test_scoring_engine',
            'tests.test_reporting.test_content_builder',
            'tests.test_reporting.test_pdf_formatter',
            'tests.test_reporting.test_report_generator',
            'tests.test_dashboard.test_components',
            'tests.test_dashboard.test_charts',
            'tests.test_dashboard.test_dashboard'
        ]
        
        return self._run_test_modules(test_modules, "Unit Tests")
    
    def _run_integration_tests(self) -> bool:
        """Run integration tests for data pipeline."""
        test_modules = [
            'tests.test_integration.test_main_pipeline'
        ]
        
        return self._run_test_modules(test_modules, "Integration Tests")
    
    def _run_e2e_tests(self) -> bool:
        """Run end-to-end tests with mock data."""
        # Create a temporary test runner for E2E tests
        e2e_test_file = self.project_root / 'tests' / 'test_e2e_workflow.py'
        if e2e_test_file.exists():
            return self._run_test_file(str(e2e_test_file), "End-to-End Tests")
        else:
            print("⚠️  E2E test file not found, skipping...")
            return True
    
    def _run_performance_tests(self) -> bool:
        """Run performance tests for large dataset processing."""
        performance_test_file = self.project_root / 'tests' / 'test_performance.py'
        if performance_test_file.exists():
            return self._run_test_file(str(performance_test_file), "Performance Tests")
        else:
            print("⚠️  Performance test file not found, skipping...")
            return True
    
    def _run_error_scenario_tests(self) -> bool:
        """Run error scenario tests."""
        error_test_file = self.project_root / 'tests' / 'test_error_scenarios.py'
        if error_test_file.exists():
            return self._run_test_file(str(error_test_file), "Error Scenario Tests")
        else:
            print("⚠️  Error scenario test file not found, skipping...")
            return True
    
    def _run_test_modules(self, modules: List[str], test_type: str) -> bool:
        """Run tests for specific modules."""
        success = True
        total_tests = 0
        passed_tests = 0
        
        for module in modules:
            try:
                result = self._run_test_module(module)
                if result['success']:
                    passed_tests += result['tests_run']
                else:
                    success = False
                total_tests += result['tests_run']
                
                # Store results
                self.test_results[module] = result
                
            except Exception as e:
                print(f"❌ Error running {module}: {e}")
                success = False
                self.test_results[module] = {
                    'success': False,
                    'tests_run': 0,
                    'error': str(e)
                }
        
        print(f"   {test_type}: {passed_tests}/{total_tests} tests passed")
        return success
    
    def _run_test_module(self, module: str) -> Dict[str, Any]:
        """Run tests for a specific module."""
        cmd = [
            sys.executable, '-m', 'pytest', module,
            '--tb=short',
            '--quiet'
        ]
        
        if self.verbose:
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300  # 5 minute timeout
            )
            
            # Parse test results
            tests_run = 0
            if result.returncode == 0:
                # Count tests from output
                for line in result.stdout.split('\n'):
                    if 'passed' in line and 'failed' in line:
                        # Extract test counts
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'passed':
                                tests_run = int(parts[i-1])
                                break
                        break
            
            return {
                'success': result.returncode == 0,
                'tests_run': tests_run,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'tests_run': 0,
                'error': 'Timeout expired',
                'stdout': '',
                'stderr': 'Test execution timed out after 5 minutes'
            }
    
    def _run_test_file(self, test_file: str, test_type: str) -> bool:
        """Run tests from a specific test file."""
        cmd = [
            sys.executable, '-m', 'pytest', test_file,
            '--tb=short',
            '--quiet'
        ]
        
        if self.verbose:
            cmd.append('--verbose')
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )
            
            success = result.returncode == 0
            print(f"   {test_type}: {'✅ PASSED' if success else '❌ FAILED'}")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"   {test_type}: ❌ TIMEOUT")
            return False
    
    def _generate_coverage_report(self):
        """Generate comprehensive coverage report."""
        try:
            cmd = [
                sys.executable, '-m', 'pytest',
                '--cov=src',
                '--cov-report=term-missing',
                '--cov-report=html:htmlcov',
                '--cov-report=xml',
                '--cov-fail-under=80',
                'tests/',
                '--tb=short',
                '--quiet'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600  # 10 minute timeout for coverage
            )
            
            if result.returncode == 0:
                print("✅ Coverage report generated successfully")
                print("📁 HTML report: htmlcov/index.html")
                print("📁 XML report: coverage.xml")
                
                # Extract coverage percentage
                for line in result.stdout.split('\n'):
                    if 'TOTAL' in line and '%' in line:
                        print(f"📊 {line.strip()}")
                        break
            else:
                print("❌ Failed to generate coverage report")
                if result.stderr:
                    print(f"Error: {result.stderr}")
                    
        except Exception as e:
            print(f"❌ Error generating coverage report: {e}")
    
    def _print_test_summary(self):
        """Print summary of test results."""
        total_modules = len(self.test_results)
        successful_modules = sum(1 for r in self.test_results.values() if r.get('success', False))
        
        print(f"Test Modules: {successful_modules}/{total_modules} successful")
        
        if self.verbose:
            print("\nDetailed Results:")
            for module, result in self.test_results.items():
                status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
                tests_run = result.get('tests_run', 0)
                print(f"  {module}: {status} ({tests_run} tests)")
                
                if not result.get('success', False) and 'error' in result:
                    print(f"    Error: {result['error']}")


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
        '--no-coverage',
        action='store_true',
        help='Disable coverage reporting'
    )
    parser.add_argument(
        '--no-performance',
        action='store_true',
        help='Disable performance testing'
    )
    parser.add_argument(
        '--no-error-scenarios',
        action='store_true',
        help='Disable error scenario testing'
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = ComprehensiveTestRunner(
        verbose=args.verbose,
        coverage=not args.no_coverage,
        performance=not args.no_performance,
        error_scenarios=not args.no_error_scenarios
    )
    
    # Run tests
    success = runner.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
