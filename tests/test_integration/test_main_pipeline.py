"""
Integration tests for the main execution pipeline.

This module tests the complete end-to-end workflow of the Advanced Trade Insight Engine,
including data loading, processing, report generation, and dashboard preparation.

Requirements: 7.4, 7.5, 7.6
"""

import unittest
import os
import sys
import tempfile
import shutil
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import main pipeline components
from main import (
    main, validate_environment, load_and_normalize_data,
    process_nlp_and_scoring, generate_reports, prepare_dashboard_data,
    ProgressTracker, handle_graceful_failure
)


class TestMainPipelineIntegration(unittest.TestCase):
    """
    Integration tests for the main execution pipeline.
    
    Requirements: 7.4, 7.5, 7.6
    """
    
    def setUp(self):
        """Set up test environment with temporary directories and mock data."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, 'csv_mock_data')
        self.output_dir = os.path.join(self.test_dir, 'output')
        
        os.makedirs(self.data_dir)
        os.makedirs(self.output_dir)
        
        # Create mock CSV files with minimal valid data
        self.create_mock_csv_files()
        
        # Setup logging for tests
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def tearDown(self):
        """Clean up temporary test directories."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_mock_csv_files(self):
        """Create mock CSV files with valid test data."""
        
        # iOS App Store reviews
        ios_data = pd.DataFrame({
            'customer_id': ['ios_001', 'ios_002'],
            'source': ['iOS App Store', 'iOS App Store'],
            'username': ['user1', 'user2'],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-02 11:00:00'],
            'rating': [4, 2],
            'sentiment': ['positive', 'negative'],
            'review_text': ['Great app!', 'Needs improvement'],
            'theme': ['Performance', 'Trading/Execution & Fees'],
            'severity': [1.0, 2.0],
            'strategic_goal': ['Growth', 'CX Efficiency'],
            'helpful_votes': [5, 10]
        })
        ios_data.to_csv(os.path.join(self.data_dir, 'coinbase_advance_apple_reviews.csv'), index=False)
        
        # Google Play Store reviews
        android_data = pd.DataFrame({
            'customer_id': ['android_001', 'android_002'],
            'source': ['Google Play Store', 'Google Play Store'],
            'username': ['user3', 'user4'],
            'timestamp': ['2024-01-03 12:00:00', '2024-01-04 13:00:00'],
            'rating': [5, 3],
            'sentiment': ['positive', 'neutral'],
            'review_text': ['Love it!', 'It\'s okay'],
            'theme': ['General Feedback', 'Support Experience'],
            'severity': [1.0, 1.5],
            'strategic_goal': ['Growth', 'Trust&Safety'],
            'helpful_votes': [3, 7]
        })
        android_data.to_csv(os.path.join(self.data_dir, 'coinbase_advanceGoogle_Play.csv'), index=False)
        
        # Internal sales notes
        sales_data = pd.DataFrame({
            'customer_id': ['sales_001', 'sales_002'],
            'source': ['Internal Sales Notes', 'Internal Sales Notes'],
            'account_name': ['Enterprise Corp', 'Startup Inc'],
            'timestamp': ['2024-01-05 14:00:00', '2024-01-06 15:00:00'],
            'sentiment': ['negative', 'positive'],
            'note_text': ['Client wants better fees', 'Happy with service'],
            'theme': ['Trading/Execution & Fees', 'General Feedback'],
            'severity': [3.0, 1.0],
            'strategic_goal': ['Growth', 'CX Efficiency'],
            'ARR_impact_estimate_USD': [100000, 50000]
        })
        sales_data.to_csv(os.path.join(self.data_dir, 'coinbase_advance_internal_sales_notes.csv'), index=False)
        
        # Twitter mentions
        twitter_data = pd.DataFrame({
            'customer_id': ['twitter_001', 'twitter_002'],
            'source': ['Twitter', 'Twitter'],
            'handle': ['@trader1', '@crypto_fan'],
            'followers': [1000, 5000],
            'timestamp': ['2024-01-07 16:00:00', '2024-01-08 17:00:00'],
            'sentiment': ['neutral', 'negative'],
            'tweet_text': ['Using Coinbase Advanced', 'Issues with the platform'],
            'theme': ['General Feedback', 'Performance/Outages'],
            'severity': [1.0, 2.5],
            'strategic_goal': ['Growth', 'Trust&Safety']
        })
        twitter_data.to_csv(os.path.join(self.data_dir, 'coinbase_advanced_twitter_mentions.csv'), index=False)
    
    def test_environment_validation_success(self):
        """Test successful environment validation."""
        is_valid, message = validate_environment(self.data_dir, self.output_dir)
        self.assertTrue(is_valid)
        self.assertIn('successful', message.lower())
    
    def test_environment_validation_missing_data_dir(self):
        """Test environment validation with missing data directory."""
        missing_dir = os.path.join(self.test_dir, 'nonexistent')
        is_valid, message = validate_environment(missing_dir, self.output_dir)
        self.assertFalse(is_valid)
        self.assertIn('missing files', message.lower())
    
    def test_data_loading_and_normalization(self):
        """Test complete data loading and normalization process."""
        normalized_df = load_and_normalize_data(self.data_dir, self.logger)
        
        self.assertIsNotNone(normalized_df)
        self.assertGreater(len(normalized_df), 0)
        
        # Check that all sources are represented
        expected_sources = 4  # iOS, Android, Sales, Twitter
        actual_sources = normalized_df['source_channel'].nunique() if 'source_channel' in normalized_df.columns else normalized_df['source'].nunique()
        self.assertEqual(actual_sources, expected_sources)
        
        # Check required columns exist
        required_columns = ['feedback_text', 'author_handle', 'sentiment', 'theme']
        for col in required_columns:
            self.assertIn(col, normalized_df.columns, f"Missing required column: {col}")
    
    def test_nlp_processing_and_scoring(self):
        """Test NLP processing and impact scoring."""
        # First load and normalize data
        normalized_df = load_and_normalize_data(self.data_dir, self.logger)
        self.assertIsNotNone(normalized_df)
        
        # Then process with NLP and scoring
        processed_df = process_nlp_and_scoring(normalized_df, self.logger)
        
        self.assertIsNotNone(processed_df)
        self.assertEqual(len(processed_df), len(normalized_df))
        
        # Check that scoring columns were added
        self.assertIn('source_weight', processed_df.columns)
        self.assertIn('impact_score', processed_df.columns)
        
        # Check that all impact scores are numeric and non-negative
        self.assertTrue(pd.api.types.is_numeric_dtype(processed_df['impact_score']))
        self.assertTrue((processed_df['impact_score'] >= 0).all())
    
    def test_report_generation(self):
        """Test PDF report generation."""
        # Load, normalize, and process data
        normalized_df = load_and_normalize_data(self.data_dir, self.logger)
        processed_df = process_nlp_and_scoring(normalized_df, self.logger)
        
        # Generate reports
        report_results = generate_reports(processed_df, self.output_dir, self.logger)
        
        # Check report generation results
        self.assertIsInstance(report_results, dict)
        
        # If successful, check that PDF file exists
        if report_results.get('success', False):
            pdf_path = report_results.get('output_path')
            self.assertTrue(os.path.exists(pdf_path))
            self.assertGreater(os.path.getsize(pdf_path), 0)
    
    def test_dashboard_data_preparation(self):
        """Test dashboard data preparation."""
        # Load, normalize, and process data
        normalized_df = load_and_normalize_data(self.data_dir, self.logger)
        processed_df = process_nlp_and_scoring(normalized_df, self.logger)
        
        # Prepare dashboard data
        dashboard_success = prepare_dashboard_data(processed_df, self.output_dir, self.logger)
        
        self.assertTrue(dashboard_success)
        
        # Check that CSV file was created
        csv_path = os.path.join(self.output_dir, 'processed_feedback_data.csv')
        self.assertTrue(os.path.exists(csv_path))
        self.assertGreater(os.path.getsize(csv_path), 0)
        
        # Verify CSV content
        saved_df = pd.read_csv(csv_path)
        self.assertEqual(len(saved_df), len(processed_df))
        self.assertIn('impact_score', saved_df.columns)
    
    def test_progress_tracker(self):
        """Test progress tracking functionality."""
        progress_tracker = ProgressTracker(self.logger)
        
        # Add test steps
        progress_tracker.add_step("Test Step 1", "First test step")
        progress_tracker.add_step("Test Step 2", "Second test step")
        
        # Start execution
        progress_tracker.start_execution()
        
        # Test step progression
        progress_tracker.start_step(0)
        progress_tracker.complete_step(0, True)
        
        progress_tracker.start_step(1)
        progress_tracker.complete_step(1, False, "Test error")
        
        # Check progress summary
        summary = progress_tracker.get_progress_summary()
        self.assertEqual(summary['total_steps'], 2)
        self.assertEqual(summary['completed'], 1)
        self.assertEqual(summary['failed'], 1)
        
        # Check step details
        self.assertEqual(progress_tracker.steps[0]['status'], 'completed')
        self.assertEqual(progress_tracker.steps[1]['status'], 'failed')
        self.assertEqual(progress_tracker.steps[1]['error'], 'Test error')
    
    def test_graceful_failure_handling(self):
        """Test graceful failure handling."""
        progress_tracker = ProgressTracker(self.logger)
        test_error = Exception("Test error for graceful handling")
        
        # Test continuing execution after failure
        continue_exec = handle_graceful_failure(
            "Test Step", test_error, self.logger, progress_tracker, True
        )
        self.assertTrue(continue_exec)
        
        # Test stopping execution after critical failure
        stop_exec = handle_graceful_failure(
            "Critical Step", test_error, self.logger, progress_tracker, False
        )
        self.assertFalse(stop_exec)
    
    @patch('sys.argv', ['main.py', '--data-dir', 'test_data', '--output-dir', 'test_output'])
    def test_main_function_with_missing_data(self):
        """Test main function behavior with missing data directory."""
        with patch('main.validate_environment') as mock_validate:
            mock_validate.return_value = (False, "Missing data directory")
            
            exit_code = main()
            self.assertEqual(exit_code, 1)
    
    def test_end_to_end_pipeline_success(self):
        """Test complete end-to-end pipeline execution."""
        # Mock command line arguments
        with patch('sys.argv', ['main.py', '--data-dir', self.data_dir, '--output-dir', self.output_dir]):
            exit_code = main()
            
            # Should succeed with our mock data
            self.assertEqual(exit_code, 0)
            
            # Check that output files were created
            expected_files = [
                'processed_feedback_data.csv'
            ]
            
            for filename in expected_files:
                filepath = os.path.join(self.output_dir, filename)
                self.assertTrue(os.path.exists(filepath), f"Expected output file not found: {filename}")
    
    def test_pipeline_with_corrupted_data(self):
        """Test pipeline behavior with corrupted CSV data."""
        # Create a corrupted CSV file
        corrupted_file = os.path.join(self.data_dir, 'coinbase_advance_apple_reviews.csv')
        with open(corrupted_file, 'w') as f:
            f.write("invalid,csv,data\nwith,missing,columns")
        
        # Pipeline should handle this gracefully
        normalized_df = load_and_normalize_data(self.data_dir, self.logger)
        
        # Should still work with other valid files
        self.assertIsNotNone(normalized_df)
        # Should have fewer records due to skipped corrupted file
        self.assertLess(len(normalized_df), 8)  # Less than all 8 mock records
    
    def test_pipeline_performance_tracking(self):
        """Test that pipeline tracks performance metrics."""
        progress_tracker = ProgressTracker(self.logger)
        progress_tracker.add_step("Performance Test", "Test performance tracking")
        
        progress_tracker.start_execution()
        progress_tracker.start_step(0)
        
        # Simulate some work
        import time
        time.sleep(0.1)
        
        progress_tracker.complete_step(0, True)
        
        summary = progress_tracker.get_progress_summary()
        self.assertGreater(summary['total_duration'], 0.1)
        self.assertGreater(progress_tracker.steps[0]['duration'], 0.1)


class TestErrorScenarios(unittest.TestCase):
    """
    Test various error scenarios and recovery mechanisms.
    
    Requirements: 7.5, 7.6
    """
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.logger = logging.getLogger(__name__)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_missing_csv_files(self):
        """Test behavior when CSV files are missing."""
        empty_dir = os.path.join(self.test_dir, 'empty')
        os.makedirs(empty_dir)
        
        is_valid, message = validate_environment(empty_dir, self.test_dir)
        self.assertFalse(is_valid)
        self.assertIn('missing files', message.lower())
    
    def test_permission_errors(self):
        """Test behavior with permission errors."""
        # Create a directory without write permissions
        no_write_dir = os.path.join(self.test_dir, 'no_write')
        os.makedirs(no_write_dir)
        os.chmod(no_write_dir, 0o444)  # Read-only
        
        try:
            is_valid, message = validate_environment(self.test_dir, no_write_dir)
            # Should fail due to write permission issues
            self.assertFalse(is_valid)
        finally:
            # Restore permissions for cleanup
            os.chmod(no_write_dir, 0o755)
    
    def test_keyboard_interrupt_handling(self):
        """Test handling of keyboard interrupts."""
        with patch('main.load_and_normalize_data') as mock_load:
            mock_load.side_effect = KeyboardInterrupt()
            
            with patch('sys.argv', ['main.py']):
                exit_code = main()
                self.assertEqual(exit_code, 1)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add integration tests
    test_suite.addTest(unittest.makeSuite(TestMainPipelineIntegration))
    test_suite.addTest(unittest.makeSuite(TestErrorScenarios))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)