"""
Unit tests for data_loader module.
"""

import unittest
import pandas as pd
import os
import tempfile
import shutil
from unittest.mock import patch, mock_open
from src.data_processing.data_loader import (
    validate_file_exists,
    validate_csv_structure,
    load_csv_file,
    load_all_csv_files,
    get_loading_summary,
    validate_data_directory,
    EXPECTED_FILES,
    REQUIRED_COLUMNS
)


class TestDataLoader(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Sample data for testing
        self.sample_ios_data = {
            'customer_id': ['IOS-001', 'IOS-002'],
            'source': ['iOS App Store', 'iOS App Store'],
            'username': ['user1', 'user2'],
            'timestamp': ['2025-06-23T19:01:00', '2025-06-11T17:07:00'],
            'rating': [4, 5],
            'sentiment': ['positive', 'positive'],
            'review_text': ['Great app', 'Love it'],
            'theme': ['Trading/Execution & Fees', 'Support Experience'],
            'severity': [0.28, 0.54],
            'strategic_goal': ['Growth', 'CX Efficiency']
        }
        
        self.sample_twitter_data = {
            'customer_id': ['TW-001', 'TW-002'],
            'source': ['Twitter (X)', 'Twitter (X)'],
            'handle': ['@trader1', '@trader2'],
            'followers': [148860, 106574],
            'timestamp': ['2025-06-05T21:08:00', '2025-07-01T11:49:00'],
            'sentiment': ['positive', 'positive'],
            'tweet_text': ['Great trading', 'Nice charts'],
            'theme': ['Performance/Outages', 'Tax Docs & Reporting'],
            'severity': [0.29, 0.27],
            'strategic_goal': ['Trust&Safety', 'Compliance']
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_validate_file_exists_valid_file(self):
        """Test file validation with existing file."""
        # Create a test file
        test_file = os.path.join(self.test_dir, 'test.csv')
        with open(test_file, 'w') as f:
            f.write('test,data\n1,2\n')
        
        self.assertTrue(validate_file_exists(test_file))
    
    def test_validate_file_exists_missing_file(self):
        """Test file validation with missing file."""
        missing_file = os.path.join(self.test_dir, 'missing.csv')
        self.assertFalse(validate_file_exists(missing_file))
    
    def test_validate_csv_structure_valid(self):
        """Test CSV structure validation with valid DataFrame."""
        df = pd.DataFrame(self.sample_ios_data)
        self.assertTrue(validate_csv_structure(df, 'ios_reviews', 'test.csv'))
    
    def test_validate_csv_structure_missing_columns(self):
        """Test CSV structure validation with missing columns."""
        # Remove required column
        incomplete_data = self.sample_ios_data.copy()
        del incomplete_data['customer_id']
        df = pd.DataFrame(incomplete_data)
        
        self.assertFalse(validate_csv_structure(df, 'ios_reviews', 'test.csv'))
    
    def test_validate_csv_structure_empty_dataframe(self):
        """Test CSV structure validation with empty DataFrame."""
        df = pd.DataFrame()
        self.assertFalse(validate_csv_structure(df, 'ios_reviews', 'test.csv'))
    
    def test_validate_csv_structure_unknown_source(self):
        """Test CSV structure validation with unknown source type."""
        df = pd.DataFrame(self.sample_ios_data)
        self.assertFalse(validate_csv_structure(df, 'unknown_source', 'test.csv'))
    
    def test_load_csv_file_success(self):
        """Test successful CSV file loading."""
        # Create test CSV file
        test_file = os.path.join(self.test_dir, 'test_ios.csv')
        df_original = pd.DataFrame(self.sample_ios_data)
        df_original.to_csv(test_file, index=False)
        
        # Load the file
        df_loaded = load_csv_file(test_file, 'ios_reviews')
        
        self.assertIsNotNone(df_loaded)
        self.assertEqual(len(df_loaded), 2)
        self.assertIn('customer_id', df_loaded.columns)
        # Check timestamp conversion
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_loaded['timestamp']))
    
    def test_load_csv_file_missing_file(self):
        """Test CSV loading with missing file."""
        missing_file = os.path.join(self.test_dir, 'missing.csv')
        result = load_csv_file(missing_file, 'ios_reviews')
        self.assertIsNone(result)
    
    def test_load_csv_file_corrupted_data(self):
        """Test CSV loading with corrupted data."""
        # Create corrupted CSV file
        test_file = os.path.join(self.test_dir, 'corrupted.csv')
        with open(test_file, 'w') as f:
            f.write('invalid,csv,data\n"unclosed quote\n')
        
        result = load_csv_file(test_file, 'ios_reviews')
        self.assertIsNone(result)
    
    def test_load_all_csv_files_success(self):
        """Test loading all CSV files successfully."""
        # Create all expected files
        ios_file = os.path.join(self.test_dir, EXPECTED_FILES['ios_reviews'])
        pd.DataFrame(self.sample_ios_data).to_csv(ios_file, index=False)
        
        twitter_file = os.path.join(self.test_dir, EXPECTED_FILES['twitter_mentions'])
        pd.DataFrame(self.sample_twitter_data).to_csv(twitter_file, index=False)
        
        # Create minimal valid data for other files
        android_data = self.sample_ios_data.copy()  # Same structure as iOS
        android_file = os.path.join(self.test_dir, EXPECTED_FILES['android_reviews'])
        pd.DataFrame(android_data).to_csv(android_file, index=False)
        
        sales_data = {
            'customer_id': ['INT-001'],
            'source': ['Internal Sales Notes'],
            'account_name': ['Acct-001'],
            'timestamp': ['2025-04-18T08:35:00'],
            'sentiment': ['positive'],
            'note_text': ['Test note'],
            'theme': ['Security, Fraud & Phishing'],
            'severity': [0.34],
            'strategic_goal': ['Trust&Safety'],
            'ARR_impact_estimate_USD': [20000]
        }
        sales_file = os.path.join(self.test_dir, EXPECTED_FILES['sales_notes'])
        pd.DataFrame(sales_data).to_csv(sales_file, index=False)
        
        # Load all files
        loaded_data = load_all_csv_files(self.test_dir)
        
        self.assertEqual(len(loaded_data), 4)  # All 4 sources loaded
        self.assertIn('ios_reviews', loaded_data)
        self.assertIn('twitter_mentions', loaded_data)
    
    def test_load_all_csv_files_partial_success(self):
        """Test loading CSV files with some missing."""
        # Create only iOS file
        ios_file = os.path.join(self.test_dir, EXPECTED_FILES['ios_reviews'])
        pd.DataFrame(self.sample_ios_data).to_csv(ios_file, index=False)
        
        # Load files (should succeed for iOS, fail for others)
        loaded_data = load_all_csv_files(self.test_dir)
        
        self.assertEqual(len(loaded_data), 1)
        self.assertIn('ios_reviews', loaded_data)
        self.assertNotIn('twitter_mentions', loaded_data)
    
    def test_get_loading_summary(self):
        """Test loading summary generation."""
        # Create sample loaded data
        loaded_data = {
            'ios_reviews': pd.DataFrame(self.sample_ios_data),
            'twitter_mentions': pd.DataFrame(self.sample_twitter_data)
        }
        
        summary = get_loading_summary(loaded_data)
        
        self.assertEqual(summary['ios_reviews'], 2)
        self.assertEqual(summary['twitter_mentions'], 2)
        self.assertEqual(summary['total_records'], 4)
        self.assertEqual(summary['sources_loaded'], 2)
        self.assertEqual(summary['sources_expected'], 4)
    
    def test_validate_data_directory_valid(self):
        """Test data directory validation with all files present."""
        # Create all expected files
        for filename in EXPECTED_FILES.values():
            file_path = os.path.join(self.test_dir, filename)
            with open(file_path, 'w') as f:
                f.write('test,data\n1,2\n')
        
        is_valid, missing_files = validate_data_directory(self.test_dir)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(missing_files), 0)
    
    def test_validate_data_directory_missing_files(self):
        """Test data directory validation with missing files."""
        # Create only some files
        ios_file = os.path.join(self.test_dir, EXPECTED_FILES['ios_reviews'])
        with open(ios_file, 'w') as f:
            f.write('test,data\n1,2\n')
        
        is_valid, missing_files = validate_data_directory(self.test_dir)
        
        self.assertFalse(is_valid)
        self.assertEqual(len(missing_files), 3)  # 3 files missing
        self.assertIn(EXPECTED_FILES['android_reviews'], missing_files)
    
    def test_validate_data_directory_nonexistent(self):
        """Test data directory validation with nonexistent directory."""
        nonexistent_dir = os.path.join(self.test_dir, 'nonexistent')
        
        is_valid, missing_files = validate_data_directory(nonexistent_dir)
        
        self.assertFalse(is_valid)
        self.assertEqual(len(missing_files), 4)  # All files missing


if __name__ == '__main__':
    unittest.main()