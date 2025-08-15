#!/usr/bin/env python3
"""
Quick Test Runner for Advanced Trade Insight Engine

A simple script to run tests quickly during development.
This is a lightweight alternative to the comprehensive test runner.

Usage:
    python run_tests.py [--quick] [--coverage]
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"💥 {description} failed with exception: {e}")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Quick test runner for Advanced Trade Insight Engine")
    parser.add_argument('--quick', action='store_true', help='Run only essential tests')
    parser.add_argument('--coverage', action='store_true', help='Include coverage reporting')
    
    args = parser.parse_args()
    
    print("🚀 Advanced Trade Insight Engine - Quick Test Runner")
    print("=" * 60)
    
    # Determine test scope
    if args.quick:
        print("📋 Running essential tests only...")
        test_pattern = "tests/test_*_*.py"  # Skip integration and comprehensive tests
    else:
        print("📋 Running all tests...")
        test_pattern = "tests/"
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest", test_pattern, "-v"]
    
    if args.coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing"])
    
    # Run tests
    success = run_command(cmd, "Test execution")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("  - Run comprehensive tests: python run_comprehensive_tests.py")
        print("  - Check coverage: pytest --cov=src --cov-report=html")
        print("  - Run specific tests: pytest tests/test_specific_module.py")
    else:
        print("❌ Some tests failed!")
        print("\nTroubleshooting:")
        print("  - Check test output above for specific failures")
        print("  - Run with verbose output: pytest -v --tb=long")
        print("  - Check individual test files: pytest tests/test_specific.py::TestClass::test_method")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
