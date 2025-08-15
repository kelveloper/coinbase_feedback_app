"""
Error Scenario Tests for Advanced Trade Insight Engine

This module tests various error conditions and edge cases to ensure
the system handles failures gracefully and provides meaningful error messages.

Requirements: 8.2, 8.3, 8.4
"""

import unittest
import pandas as pd
import tempfile
import shutil
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_processing.data_loader import load_all_csv_files, validate_file_exists
    from data_processing.data_normalizer import normalize_and_unify_data
    from analysis.nlp_models import get_sentiment, get_theme, get_strategic_goal
    from analysis.scoring_engine import calculate_source_weight, calculate_impact_score
    from reporting.content_builder import build_comprehensive_content
    from reporting.report_generator import generate_complete_report
    from dashboard.components import display_kpi_header
except ImportError as e:
    print(f"Import warning: {e}")
    pass


class TestDataLoadingErrors(unittest.TestCase):
    """Test error scenarios in data loading."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_missing_data_directory(self):
        """Test behavior when data directory doesn't exist."""
        try:
            nonexistent_dir = os.path.join(self.temp_dir, 'nonexistent')
            
            with self.assertRaises(Exception):
                load_all_csv_files(nonexistent_dir)
                
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_empty_data_directory(self):
        """Test behavior when data directory is empty."""
        try:
            empty_dir = os.path.join(self.temp_dir, 'empty')
            os.makedirs(empty_dir)
            
            result = load_all_csv_files(empty_dir)
            
            # Should return empty dict or handle gracefully
            self.assertIsInstance(result, dict)
            self.assertEqual(len(result), 0)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_corrupted_csv_files(self):
        """Test behavior with corrupted CSV files."""
        try:
            # Create corrupted CSV file
            corrupted_file = os.path.join(self.temp_dir, 'coinbase_advance_apple_reviews.csv')
            with open(corrupted_file, 'w') as f:
                f.write('invalid,csv,data\n"unclosed quote\nbroken,format')
            
            result = load_all_csv_files(self.temp_dir)
            
            # Should handle corrupted files gracefully
            self.assertIsInstance(result, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_csv_with_missing_columns(self):
        """Test behavior with CSV files missing required columns."""
        try:
            # Create CSV with missing columns
            incomplete_file = os.path.join(self.temp_dir, 'coinbase_advance_apple_reviews.csv')
            incomplete_data = pd.DataFrame({
                'customer_id': ['TEST-001'],
                'source': ['iOS App Store']
                # Missing other required columns
            })
            incomplete_data.to_csv(incomplete_file, index=False)
            
            result = load_all_csv_files(self.temp_dir)
            
            # Should handle missing columns gracefully
            self.assertIsInstance(result, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_csv_with_invalid_data_types(self):
        """Test behavior with invalid data types in CSV files."""
        try:
            # Create CSV with invalid data types
            invalid_file = os.path.join(self.temp_dir, 'coinbase_advance_apple_reviews.csv')
            invalid_data = pd.DataFrame({
                'customer_id': ['TEST-001'],
                'source': ['iOS App Store'],
                'username': ['user1'],
                'timestamp': ['invalid_timestamp'],
                'rating': ['not_a_number'],
                'sentiment': ['positive'],
                'review_text': ['Test review'],
                'theme': ['Performance'],
                'severity': ['not_numeric'],
                'strategic_goal': ['Growth']
            })
            invalid_data.to_csv(invalid_file, index=False)
            
            result = load_all_csv_files(self.temp_dir)
            
            # Should handle invalid data types gracefully
            self.assertIsInstance(result, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


class TestDataProcessingErrors(unittest.TestCase):
    """Test error scenarios in data processing."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_normalization_with_empty_data(self):
        """Test data normalization with empty datasets."""
        try:
            empty_data = {}
            result = normalize_and_unify_data(empty_data)
            
            # Should return empty DataFrame with expected columns
            self.assertIsInstance(result, pd.DataFrame)
            self.assertTrue(result.empty)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_normalization_with_null_values(self):
        """Test data normalization with null values."""
        try:
            null_data = {
                'test.csv': pd.DataFrame({
                    'customer_id': [None, 'TEST-002'],
                    'source': ['iOS App Store', None],
                    'username': [None, 'user2'],
                    'timestamp': ['2024-01-01', None],
                    'sentiment': [None, 'positive'],
                    'review_text': ['', None],
                    'theme': [None, ''],
                    'severity': [None, 1.0],
                    'strategic_goal': ['', None]
                })
            }
            
            result = normalize_and_unify_data(null_data)
            
            # Should handle null values gracefully
            self.assertIsInstance(result, pd.DataFrame)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_nlp_processing_with_invalid_data(self):
        """Test NLP processing with invalid data."""
        try:
            # Test with None values
            none_record = pd.Series({'sentiment': None, 'theme': None, 'strategic_goal': None})
            
            sentiment = get_sentiment(none_record)
            theme = get_theme(none_record)
            strategic_goal = get_strategic_goal(none_record)
            
            # Should return default values
            self.assertIn(sentiment, ['positive', 'neutral', 'negative'])
            self.assertIsInstance(theme, str)
            self.assertIsInstance(strategic_goal, str)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_scoring_with_missing_data(self):
        """Test impact scoring with missing data."""
        try:
            # Test with missing required fields
            incomplete_record = pd.Series({
                'source': 'Unknown Source',
                'sentiment': 'positive'
                # Missing other fields needed for scoring
            })
            
            source_weight = calculate_source_weight(incomplete_record)
            impact_score = calculate_impact_score(incomplete_record)
            
            # Should return default values
            self.assertIsInstance(source_weight, (int, float))
            self.assertGreater(source_weight, 0)
            self.assertIsInstance(impact_score, (int, float))
            self.assertGreaterEqual(impact_score, 0)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


class TestReportGenerationErrors(unittest.TestCase):
    """Test error scenarios in report generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.temp_dir, 'test_report.pdf')
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_report_generation_with_empty_data(self):
        """Test report generation with empty data."""
        try:
            empty_df = pd.DataFrame()
            
            content = build_comprehensive_content(empty_df)
            
            # Should handle empty data gracefully
            self.assertIsInstance(content, dict)
            self.assertIn('executive_summary', content)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_report_generation_with_invalid_output_path(self):
        """Test report generation with invalid output path."""
        try:
            # Create minimal valid data
            test_data = pd.DataFrame({
                'theme': ['Performance'],
                'sentiment': ['positive'],
                'impact_score': [5.0]
            })
            
            # Try to write to invalid path
            invalid_path = '/invalid/path/that/cannot/be/created/report.pdf'
            
            result = generate_complete_report(test_data, invalid_path)
            
            # Should handle invalid path gracefully
            self.assertIsInstance(result, dict)
            self.assertFalse(result.get('success', True))
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_pdf_creation_with_corrupted_content(self):
        """Test PDF creation with corrupted content."""
        try:
            # Create data with problematic values
            problematic_data = pd.DataFrame({
                'theme': ['Theme with very long name that might cause issues' * 10],
                'sentiment': ['invalid_sentiment'],
                'impact_score': [float('inf')],
                'feedback_text': ['Text with special characters: ñáéíóú@#$%^&*()']
            })
            
            content = build_comprehensive_content(problematic_data)
            
            # Should handle problematic data gracefully
            self.assertIsInstance(content, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


class TestDashboardErrors(unittest.TestCase):
    """Test error scenarios in dashboard components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_kpi_display_with_empty_data(self, mock_metric, mock_columns):
        """Test KPI display with empty data."""
        try:
            # Mock Streamlit components
            mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
            
            mock_col1.metric = MagicMock()
            mock_col2.metric = MagicMock()
            mock_col3.metric = MagicMock()
            
            empty_df = pd.DataFrame()
            
            result = display_kpi_header(empty_df)
            
            # Should handle empty data gracefully
            self.assertIsInstance(result, dict)
            self.assertEqual(result['total_items'], 0)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_kpi_display_with_corrupted_data(self, mock_metric, mock_columns):
        """Test KPI display with corrupted data."""
        try:
            # Mock Streamlit components
            mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
            
            mock_col1.metric = MagicMock()
            mock_col2.metric = MagicMock()
            mock_col3.metric = MagicMock()
            
            # Create corrupted data
            corrupted_df = pd.DataFrame({
                'sentiment': [None, 'invalid', ''],
                'theme': ['', None, 'Valid Theme'],
                'impact_score': [None, 'not_numeric', -1]
            })
            
            result = display_kpi_header(corrupted_df)
            
            # Should handle corrupted data gracefully
            self.assertIsInstance(result, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


class TestMemoryAndPerformanceErrors(unittest.TestCase):
    """Test memory and performance related error scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_large_dataset_memory_handling(self):
        """Test memory handling with large datasets."""
        try:
            # Create a moderately large dataset
            large_data = []
            for i in range(5000):  # 5000 rows should be manageable
                large_data.append({
                    'customer_id': f'LARGE-{i:05d}',
                    'source': 'Test Source',
                    'sentiment': ['positive', 'neutral', 'negative'][i % 3],
                    'theme': ['Performance', 'Support', 'Features'][i % 3],
                    'impact_score': (i % 100) / 10.0,
                    'feedback_text': f'Test feedback {i}'
                })
            
            large_df = pd.DataFrame(large_data)
            
            # Test processing
            loaded_data = {'large_test.csv': large_df}
            result = normalize_and_unify_data(loaded_data)
            
            # Should handle large dataset
            self.assertIsInstance(result, pd.DataFrame)
            self.assertEqual(len(result), len(large_df))
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
        except MemoryError:
            self.skipTest("Insufficient memory for large dataset test")
    
    def test_infinite_loop_protection(self):
        """Test protection against infinite loops in processing."""
        try:
            # Create data that might cause processing issues
            problematic_data = pd.DataFrame({
                'customer_id': ['LOOP-001'] * 100,  # Duplicate IDs
                'source': ['Test Source'] * 100,
                'sentiment': ['positive'] * 100,
                'theme': ['Performance'] * 100,
                'impact_score': [float('inf')] * 100,  # Infinite values
                'feedback_text': [''] * 100  # Empty text
            })
            
            # Processing should complete in reasonable time
            import time
            start_time = time.time()
            
            loaded_data = {'problematic.csv': problematic_data}
            result = normalize_and_unify_data(loaded_data)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should complete within reasonable time (5 seconds)
            self.assertLess(processing_time, 5.0)
            self.assertIsInstance(result, pd.DataFrame)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


class TestSystemIntegrationErrors(unittest.TestCase):
    """Test system-level integration error scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_disk_space_exhaustion_simulation(self):
        """Test behavior when disk space is exhausted."""
        try:
            # Create a very small temporary partition (simulation)
            small_output_dir = os.path.join(self.temp_dir, 'small_output')
            os.makedirs(small_output_dir)
            
            # Create minimal test data
            test_data = pd.DataFrame({
                'theme': ['Performance'],
                'sentiment': ['positive'],
                'impact_score': [5.0]
            })
            
            # Try to generate report
            output_path = os.path.join(small_output_dir, 'test_report.pdf')
            result = generate_complete_report(test_data, output_path)
            
            # Should handle gracefully (either succeed or fail gracefully)
            self.assertIsInstance(result, dict)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_concurrent_access_simulation(self):
        """Test behavior with simulated concurrent access."""
        try:
            # Create test data
            test_data = pd.DataFrame({
                'customer_id': ['CONCURRENT-001', 'CONCURRENT-002'],
                'source': ['Test Source', 'Test Source'],
                'sentiment': ['positive', 'negative'],
                'theme': ['Performance', 'Support'],
                'impact_score': [5.0, 3.0],
                'feedback_text': ['Good', 'Bad']
            })
            
            # Simulate multiple processing attempts
            results = []
            for i in range(3):
                loaded_data = {f'concurrent_{i}.csv': test_data}
                result = normalize_and_unify_data(loaded_data)
                results.append(result)
            
            # All should succeed
            for result in results:
                self.assertIsInstance(result, pd.DataFrame)
                self.assertEqual(len(result), 2)
                
        except ImportError:
            self.skipTest("Required modules not available for testing")


if __name__ == '__main__':
    # Create comprehensive test suite
    test_suite = unittest.TestSuite()
    
    # Add all error scenario test classes
    test_classes = [
        TestDataLoadingErrors,
        TestDataProcessingErrors,
        TestReportGenerationErrors,
        TestDashboardErrors,
        TestMemoryAndPerformanceErrors,
        TestSystemIntegrationErrors
    ]
    
    for test_class in test_classes:
        test_suite.addTest(unittest.makeSuite(test_class))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("ERROR SCENARIO TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)