"""
Unit tests for data_normalizer module.

Tests cover data normalization, column mapping, and DataFrame unification
functionality with various edge cases and error conditions.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from data_processing.data_normalizer import (
    normalize_column_names,
    map_feedback_text_column,
    map_author_handle_column,
    add_source_channel_column,
    normalize_and_unify_data
)


class TestNormalizeColumnNames(unittest.TestCase):
    """Test cases for normalize_column_names function."""
    
    def test_normalize_ios_columns(self):
        """Test column normalization for iOS data."""
        df = pd.DataFrame({
            'customer_id': ['IOS-001'],
            'source': ['iOS App Store'],
            'username': ['user1'],
            'timestamp': ['2024-01-01'],
            'rating': [4],
            'sentiment': ['positive'],
            'review_text': ['Great app'],
            'theme': ['Performance'],
            'severity': [1.0],
            'strategic_goal': ['Growth']
        })
        
        result = normalize_column_names(df, 'ios_reviews')
        
        # Check that all expected columns are present
        expected_columns = ['customer_id', 'source', 'username', 'timestamp', 
                          'rating', 'sentiment', 'review_text', 'theme', 
                          'severity', 'strategic_goal']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_normalize_twitter_columns(self):
        """Test column normalization for Twitter data."""
        df = pd.DataFrame({
            'customer_id': ['TW-001'],
            'source': ['Twitter'],
            'handle': ['@user1'],
            'followers': [1000],
            'timestamp': ['2024-01-01'],
            'sentiment': ['positive'],
            'tweet_text': ['Great platform'],
            'theme': ['Performance'],
            'severity': [1.0],
            'strategic_goal': ['Growth']
        })
        
        result = normalize_column_names(df, 'twitter_mentions')
        
        # Check that all expected columns are present
        expected_columns = ['customer_id', 'source', 'handle', 'followers',
                          'timestamp', 'sentiment', 'tweet_text', 'theme',
                          'severity', 'strategic_goal']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_normalize_unknown_source(self):
        """Test column normalization for unknown source type."""
        df = pd.DataFrame({'test_col': ['value']})
        
        result = normalize_column_names(df, 'unknown_source')
        
        # Should return original DataFrame unchanged
        self.assertTrue(result.equals(df))


class TestMapFeedbackTextColumn(unittest.TestCase):
    """Test cases for map_feedback_text_column function."""
    
    def test_map_review_text(self):
        """Test mapping review_text to feedback_text."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'review_text': ['This is a review']
        })
        
        result = map_feedback_text_column(df)
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result.iloc[0]['feedback_text'], 'This is a review')
    
    def test_map_tweet_text(self):
        """Test mapping tweet_text to feedback_text."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'tweet_text': ['This is a tweet']
        })
        
        result = map_feedback_text_column(df)
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result.iloc[0]['feedback_text'], 'This is a tweet')
    
    def test_map_note_text(self):
        """Test mapping note_text to feedback_text."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'note_text': ['This is a note']
        })
        
        result = map_feedback_text_column(df)
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result.iloc[0]['feedback_text'], 'This is a note')
    
    def test_map_no_text_columns(self):
        """Test mapping when no text columns are present."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'other_column': ['value']
        })
        
        result = map_feedback_text_column(df)
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result.iloc[0]['feedback_text'], '')
    
    def test_map_multiple_text_columns(self):
        """Test mapping when multiple text columns are present."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'review_text': ['Review text'],
            'tweet_text': ['Tweet text'],
            'note_text': ['Note text']
        })
        
        result = map_feedback_text_column(df)
        
        # Should prioritize review_text first
        self.assertEqual(result.iloc[0]['feedback_text'], 'Review text')
    
    def test_map_null_text_values(self):
        """Test mapping with null text values."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001', 'TEST-002'],
            'review_text': [None, np.nan]
        })
        
        result = map_feedback_text_column(df)
        
        # Should handle null values gracefully
        self.assertTrue(all(result['feedback_text'] == ''))


class TestMapAuthorHandleColumn(unittest.TestCase):
    """Test cases for map_author_handle_column function."""
    
    def test_map_username(self):
        """Test mapping username to author_handle."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'username': ['user123']
        })
        
        result = map_author_handle_column(df)
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result.iloc[0]['author_handle'], 'user123')
    
    def test_map_handle(self):
        """Test mapping handle to author_handle."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'handle': ['@user123']
        })
        
        result = map_author_handle_column(df)
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result.iloc[0]['author_handle'], '@user123')
    
    def test_map_account_name(self):
        """Test mapping account_name to author_handle."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'account_name': ['Account Name']
        })
        
        result = map_author_handle_column(df)
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result.iloc[0]['author_handle'], 'Account Name')
    
    def test_map_no_handle_columns(self):
        """Test mapping when no handle columns are present."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'other_column': ['value']
        })
        
        result = map_author_handle_column(df)
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result.iloc[0]['author_handle'], 'Unknown')


class TestAddSourceChannelColumn(unittest.TestCase):
    """Test cases for add_source_channel_column function."""
    
    def test_add_source_channel_ios(self):
        """Test adding source channel for iOS data."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'source': ['iOS App Store']
        })
        
        result = add_source_channel_column(df, 'ios_reviews')
        
        self.assertIn('source_channel', result.columns)
        self.assertEqual(result.iloc[0]['source_channel'], 'iOS App Store')
    
    def test_add_source_channel_twitter(self):
        """Test adding source channel for Twitter data."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'source': ['Twitter']
        })
        
        result = add_source_channel_column(df, 'twitter_mentions')
        
        self.assertIn('source_channel', result.columns)
        self.assertEqual(result.iloc[0]['source_channel'], 'Twitter (X)')
    
    def test_add_source_channel_unknown(self):
        """Test adding source channel for unknown source type."""
        df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'source': ['Unknown']
        })
        
        result = add_source_channel_column(df, 'unknown_source')
        
        self.assertIn('source_channel', result.columns)
        self.assertEqual(result.iloc[0]['source_channel'], 'Unknown')


class TestNormalizeAndUnifyData(unittest.TestCase):
    """Test cases for normalize_and_unify_data function."""
    
    def setUp(self):
        """Set up test data."""
        self.ios_data = pd.DataFrame({
            'customer_id': ['IOS-001', 'IOS-002'],
            'source': ['iOS App Store', 'iOS App Store'],
            'username': ['user1', 'user2'],
            'timestamp': ['2024-01-01', '2024-01-02'],
            'rating': [4, 5],
            'sentiment': ['positive', 'positive'],
            'review_text': ['Great app', 'Love it'],
            'theme': ['Performance', 'Features'],
            'severity': [1.0, 0.5],
            'strategic_goal': ['Growth', 'Growth']
        })
        
        self.twitter_data = pd.DataFrame({
            'customer_id': ['TW-001', 'TW-002'],
            'source': ['Twitter', 'Twitter'],
            'handle': ['@user1', '@user2'],
            'followers': [1000, 2000],
            'timestamp': ['2024-01-03', '2024-01-04'],
            'sentiment': ['positive', 'negative'],
            'tweet_text': ['Great platform', 'Having issues'],
            'theme': ['Features', 'Support'],
            'severity': [1.0, 2.0],
            'strategic_goal': ['Growth', 'CX Efficiency']
        })
    
    def test_normalize_single_source(self):
        """Test normalization with single data source."""
        loaded_data = {'ios_reviews': self.ios_data}
        
        result = normalize_and_unify_data(loaded_data)
        
        # Check unified structure
        self.assertEqual(len(result), 2)
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        self.assertIn('source_channel', result.columns)
        
        # Check data integrity
        self.assertEqual(result.iloc[0]['feedback_text'], 'Great app')
        self.assertEqual(result.iloc[0]['author_handle'], 'user1')
        self.assertEqual(result.iloc[0]['source_channel'], 'iOS App Store')
    
    def test_normalize_multiple_sources(self):
        """Test normalization with multiple data sources."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data
        }
        
        result = normalize_and_unify_data(loaded_data)
        
        # Check unified structure
        self.assertEqual(len(result), 4)  # 2 iOS + 2 Twitter
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        self.assertIn('source_channel', result.columns)
        
        # Check data from both sources
        ios_rows = result[result['source_channel'] == 'iOS App Store']
        twitter_rows = result[result['source_channel'] == 'Twitter (X)']
        
        self.assertEqual(len(ios_rows), 2)
        self.assertEqual(len(twitter_rows), 2)
    
    def test_normalize_empty_data(self):
        """Test normalization with empty data."""
        loaded_data = {}
        
        result = normalize_and_unify_data(loaded_data)
        
        # Should return empty DataFrame with expected columns
        self.assertTrue(result.empty)
        expected_columns = ['customer_id', 'source_channel', 'feedback_text', 
                          'author_handle', 'timestamp']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_normalize_with_missing_columns(self):
        """Test normalization with missing columns in source data."""
        incomplete_data = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'source': ['Test Source']
            # Missing other expected columns
        })
        
        loaded_data = {'test_source': incomplete_data}
        
        result = normalize_and_unify_data(loaded_data)
        
        # Should handle missing columns gracefully
        self.assertEqual(len(result), 1)
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        
        # Check default values
        self.assertEqual(result.iloc[0]['feedback_text'], '')
        self.assertEqual(result.iloc[0]['author_handle'], 'Unknown')
    
    def test_normalize_preserves_source_specific_columns(self):
        """Test that source-specific columns are preserved."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data
        }
        
        result = normalize_and_unify_data(loaded_data)
        
        # Check that source-specific columns are preserved
        ios_rows = result[result['source_channel'] == 'iOS App Store']
        twitter_rows = result[result['source_channel'] == 'Twitter (X)']
        
        # iOS should have rating column
        self.assertIn('rating', ios_rows.columns)
        self.assertFalse(ios_rows['rating'].isna().all())
        
        # Twitter should have followers column
        self.assertIn('followers', twitter_rows.columns)
        self.assertFalse(twitter_rows['followers'].isna().all())


if __name__ == '__main__':
    unittest.main()