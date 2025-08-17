#!/usr/bin/env python3
"""
Basic testing and validation script for the Feedback Enhancement System.

This script performs the following tests:
1. Simple test execution using existing CSV files in csv_mock_data directory
2. Validate output file structure matches expected schema
3. Test error handling with intentionally missing files
4. Verify data integrity by checking record counts and data types in output
"""

import os
import sys
import tempfile
import shutil
import pandas as pd
from pathlib import Path
import subprocess
import logging

# Set up logging for test script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_successful_execution():
    """Test 1: Simple test execution using existing CSV files."""
    logger.info("=" * 60)
    logger.info("TEST 1: Testing successful execution with existing CSV files")
    logger.info("=" * 60)
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_output_dir:
        try:
            # Run the feedback enhancement system
            result = subprocess.run([
                sys.executable, 'feedback_enhancement_system.py',
                '--input-dir', 'csv_mock_data',
                '--output-dir', temp_output_dir,
                '--log-level', 'ERROR'  # Reduce log noise for testing
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Execution failed with return code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                return False
            
            # Check if output file was created
            output_file = Path(temp_output_dir) / 'enriched_feedback_master.csv'
            if not output_file.exists():
                logger.error("Output file was not created")
                return False
            
            logger.info("✓ Execution completed successfully")
            logger.info(f"✓ Output file created: {output_file}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Execution timed out after 30 seconds")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during execution: {e}")
            return False


def test_output_file_structure():
    """Test 2: Validate output file structure matches expected schema."""
    logger.info("=" * 60)
    logger.info("TEST 2: Validating output file structure and schema")
    logger.info("=" * 60)
    
    output_file = Path('output/enriched_feedback_master.csv')
    
    if not output_file.exists():
        logger.error("Output file does not exist. Run successful execution test first.")
        return False
    
    try:
        # Load the output CSV
        df = pd.read_csv(output_file)
        
        # Define expected schema
        expected_columns = [
            'feedback_id',
            'source_channel', 
            'timestamp',
            'feedback_text',
            'source_metric',
            'is_relevant',
            'sentiment_score',
            'theme',
            'strategic_goal'
        ]
        
        # Check if all expected columns exist
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing expected columns: {missing_columns}")
            return False
        
        # Check if there are unexpected columns
        unexpected_columns = [col for col in df.columns if col not in expected_columns]
        if unexpected_columns:
            logger.warning(f"Unexpected columns found: {unexpected_columns}")
        
        # Validate data types
        logger.info("Validating data types...")
        
        # Check feedback_id is string
        if not df['feedback_id'].dtype == 'object':
            logger.error(f"feedback_id should be string, got {df['feedback_id'].dtype}")
            return False
        
        # Check source_channel is string
        if not df['source_channel'].dtype == 'object':
            logger.error(f"source_channel should be string, got {df['source_channel'].dtype}")
            return False
        
        # Check timestamp can be converted to datetime
        try:
            pd.to_datetime(df['timestamp'])
        except Exception as e:
            logger.error(f"timestamp column cannot be converted to datetime: {e}")
            return False
        
        # Check feedback_text is string
        if not df['feedback_text'].dtype == 'object':
            logger.error(f"feedback_text should be string, got {df['feedback_text'].dtype}")
            return False
        
        # Check source_metric is numeric
        if not pd.api.types.is_numeric_dtype(df['source_metric']):
            logger.error(f"source_metric should be numeric, got {df['source_metric'].dtype}")
            return False
        
        # Check is_relevant is boolean
        if not df['is_relevant'].dtype == 'bool':
            logger.error(f"is_relevant should be boolean, got {df['is_relevant'].dtype}")
            return False
        
        # Check sentiment_score is numeric and in valid range
        if not pd.api.types.is_numeric_dtype(df['sentiment_score']):
            logger.error(f"sentiment_score should be numeric, got {df['sentiment_score'].dtype}")
            return False
        
        # Check sentiment_score range
        if df['sentiment_score'].min() < -1.0 or df['sentiment_score'].max() > 1.0:
            logger.error(f"sentiment_score out of range [-1.0, 1.0]: min={df['sentiment_score'].min()}, max={df['sentiment_score'].max()}")
            return False
        
        # Validate record counts
        expected_record_count = 200  # 50 records from each of 4 sources
        if len(df) != expected_record_count:
            logger.error(f"Expected {expected_record_count} records, got {len(df)}")
            return False
        
        # Validate source distribution
        source_counts = df['source_channel'].value_counts()
        expected_sources = ['Apple App Store', 'Google Play Store', 'Twitter (X)', 'Internal Sales Notes']
        
        for source in expected_sources:
            if source not in source_counts:
                logger.error(f"Missing source channel: {source}")
                return False
            if source_counts[source] != 50:
                logger.error(f"Expected 50 records for {source}, got {source_counts[source]}")
                return False
        
        # Validate unique feedback_id prefixes
        apple_ids = df[df['source_channel'] == 'Apple App Store']['feedback_id']
        google_ids = df[df['source_channel'] == 'Google Play Store']['feedback_id']
        twitter_ids = df[df['source_channel'] == 'Twitter (X)']['feedback_id']
        sales_ids = df[df['source_channel'] == 'Internal Sales Notes']['feedback_id']
        
        if not all(id.startswith('apple-') for id in apple_ids):
            logger.error("Not all Apple App Store records have 'apple-' prefix")
            return False
        
        if not all(id.startswith('google-') for id in google_ids):
            logger.error("Not all Google Play Store records have 'google-' prefix")
            return False
        
        if not all(id.startswith('twitter-') for id in twitter_ids):
            logger.error("Not all Twitter records have 'twitter-' prefix")
            return False
        
        if not all(id.startswith('sales-') for id in sales_ids):
            logger.error("Not all Internal Sales Notes records have 'sales-' prefix")
            return False
        
        logger.info("✓ All columns present and correctly named")
        logger.info("✓ All data types are correct")
        logger.info("✓ Record counts match expectations")
        logger.info("✓ Source distribution is correct")
        logger.info("✓ Feedback ID prefixes are correct")
        logger.info(f"✓ Schema validation passed: {len(df)} records, {len(df.columns)} columns")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating output file structure: {e}")
        return False


def test_error_handling_missing_files():
    """Test 3: Test error handling with intentionally missing files."""
    logger.info("=" * 60)
    logger.info("TEST 3: Testing error handling with missing files")
    logger.info("=" * 60)
    
    # Create temporary directory with only some CSV files
    with tempfile.TemporaryDirectory() as temp_input_dir:
        with tempfile.TemporaryDirectory() as temp_output_dir:
            try:
                # Copy only 2 out of 4 required files
                shutil.copy('csv_mock_data/coinbase_advance_apple_reviews.csv', temp_input_dir)
                shutil.copy('csv_mock_data/coinbase_advanceGoogle_Play.csv', temp_input_dir)
                # Intentionally omit twitter and sales files
                
                # Run the feedback enhancement system (should fail)
                result = subprocess.run([
                    sys.executable, 'feedback_enhancement_system.py',
                    '--input-dir', temp_input_dir,
                    '--output-dir', temp_output_dir,
                    '--log-level', 'ERROR'
                ], capture_output=True, text=True, timeout=30)
                
                # Should fail with non-zero return code
                if result.returncode == 0:
                    logger.error("Expected execution to fail with missing files, but it succeeded")
                    return False
                
                # Check that appropriate error messages are present
                if 'Missing required CSV files' not in result.stderr and 'FileNotFoundError' not in result.stderr:
                    logger.error("Expected error message about missing files not found in output")
                    logger.error(f"STDERR: {result.stderr}")
                    return False
                
                logger.info("✓ System correctly failed when files are missing")
                logger.info("✓ Appropriate error messages were generated")
                return True
                
            except subprocess.TimeoutExpired:
                logger.error("Error handling test timed out")
                return False
            except Exception as e:
                logger.error(f"Unexpected error during error handling test: {e}")
                return False


def test_data_integrity():
    """Test 4: Verify data integrity by checking record counts and data types in output."""
    logger.info("=" * 60)
    logger.info("TEST 4: Verifying data integrity and consistency")
    logger.info("=" * 60)
    
    output_file = Path('output/enriched_feedback_master.csv')
    
    if not output_file.exists():
        logger.error("Output file does not exist. Run successful execution test first.")
        return False
    
    try:
        # Load the output CSV
        df = pd.read_csv(output_file)
        
        # Check for duplicate feedback_ids
        duplicate_ids = df['feedback_id'].duplicated().sum()
        if duplicate_ids > 0:
            logger.error(f"Found {duplicate_ids} duplicate feedback_ids")
            return False
        
        # Check for null values in critical columns
        critical_columns = ['feedback_id', 'source_channel', 'feedback_text']
        for col in critical_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                logger.error(f"Found {null_count} null values in critical column: {col}")
                return False
        
        # Check sentiment score distribution
        sentiment_counts = df['sentiment_score'].value_counts()
        expected_sentiment_values = [-0.8, 0.0, 0.7]
        
        for value in expected_sentiment_values:
            if value not in sentiment_counts:
                logger.error(f"Expected sentiment score {value} not found in data")
                return False
        
        # Check that all records are marked as relevant
        if not df['is_relevant'].all():
            logger.error("Not all records are marked as relevant")
            return False
        
        # Check timestamp format consistency
        try:
            timestamps = pd.to_datetime(df['timestamp'])
            if timestamps.isnull().any():
                logger.error("Some timestamps could not be parsed")
                return False
        except Exception as e:
            logger.error(f"Timestamp parsing failed: {e}")
            return False
        
        # Verify source_metric values are reasonable (not all zeros or negative)
        if df['source_metric'].min() < 0:
            logger.warning("Some source_metric values are negative (may be expected for sales notes)")
        
        if df['source_metric'].max() == df['source_metric'].min():
            logger.warning("All source_metric values are identical (may indicate data issue)")
        
        logger.info("✓ No duplicate feedback_ids found")
        logger.info("✓ No null values in critical columns")
        logger.info("✓ Sentiment score distribution is correct")
        logger.info("✓ All records marked as relevant")
        logger.info("✓ Timestamp format is consistent")
        logger.info("✓ Data integrity validation passed")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during data integrity validation: {e}")
        return False


def main():
    """Main test runner function."""
    logger.info("Starting Feedback Enhancement System Testing")
    logger.info("=" * 80)
    
    tests = [
        ("Successful Execution", test_successful_execution),
        ("Output File Structure", test_output_file_structure),
        ("Error Handling", test_error_handling_missing_files),
        ("Data Integrity", test_data_integrity)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            logger.info(f"\nRunning test: {test_name}")
            result = test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"✓ {test_name}: PASSED")
            else:
                logger.error(f"✗ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"✗ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! The Feedback Enhancement System is working correctly.")
        return 0
    else:
        logger.error(f"❌ {total_tests - passed_tests} test(s) failed. Please review the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())