"""
Unit tests for data_normalizer module.
"""

import unittest
import pandas as pd
from src.data_processing.data_normalizer import (
    normalize_feedback_text,
    normalize_author_handle,
    add_source_channel,
    normalize_single_source,
    unify_dataframes,
    validate_unified_dataframe,
    get_normalization_summary,
    normalize_and_unify_data,
    COLUMN_MAPPINGS,
    STANDARD_COLUMNS
)


class TestDataNormalizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample iOS reviews data
        self.ios_data = pd.DataFrame({
            'customer_id': ['IOS-001', 'IOS-002'],
            'source': ['iOS App Store', 'iOS App Store'],
            'username': ['user1', 'user2'],
            'timestamp': ['2025-06-23T19:01:00', '2025-06-11T17:07:00'],
            'rating': [4, 5],
            'sentiment': ['positive', 'positive'],
            'review_text': ['Great app', 'Love it'],
            'theme': ['Trading/Execution & Fees', 'Support Experience'],
            'severity': [0.28, 0.54],
            'strategic_goal': ['Growth', 'CX Efficiency'],
            'helpful_votes': [17, 23],
            'region': ['US-NY', 'CA'],
            'device': ['iPhone 13', 'iPhone 14'],
            'app_version': ['11.2.1', '11.2.0']
        })
        
        # Sample Twitter data
        self.twitter_data = pd.DataFrame({
            'customer_id': ['TW-001', 'TW-002'],
            'source': ['Twitter (X)', 'Twitter (X)'],
            'handle': ['@trader1', '@trader2'],
            'followers': [148860, 106574],
            'timestamp': ['2025-06-05T21:08:00', '2025-07-01T11:49:00'],
            'sentiment': ['positive', 'positive'],
            'tweet_text': ['Great trading', 'Nice charts'],
            'theme': ['Performance/Outages', 'Tax Docs & Reporting'],
            'severity': [0.29, 0.27],
            'strategic_goal': ['Trust&Safety', 'Compliance'],
            'verified': [True, True],
            'likes': [133, 157],
            'retweets': [80, 118],
            'reply_count': [25, 16]
        })
        
        # Sample sales notes data
        self.sales_data = pd.DataFrame({
            'customer_id': ['INT-001', 'INT-002'],
            'source': ['Internal Sales Notes', 'Internal Sales Notes'],
            'account_name': ['Acct-001', 'Acct-002'],
            'timestamp': ['2025-04-18T08:35:00', '2025-03-06T11:59:00'],
            'sentiment': ['positive', 'positive'],
            'note_text': ['Pricing acceptable', 'Migration approved'],
            'theme': ['Security, Fraud & Phishing', 'Security, Fraud & Phishing'],
            'severity': [0.34, 0.45],
            'strategic_goal': ['Trust&Safety', 'Trust&Safety'],
            'ARR_impact_estimate_USD': [20000, 20000],
            'account_type': ['Enterprise', 'Mid-Market'],
            'deal_stage': ['Negotiation', 'Evaluation'],
            'requested_feature': ['Post-trade Receipt', 'None'],
            'contact_role': ['CTO', 'PM'],
            'region': ['AU', 'JP']
        })
    
    def test_normalize_feedback_text_ios(self):
        """Test feedback text normalization for iOS reviews."""
        result = normalize_feedback_text(self.ios_data, 'ios_reviews')
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result['feedback_text'].iloc[0], 'Great app')
        self.assertEqual(result['feedback_text'].iloc[1], 'Love it')
    
    def test_normalize_feedback_text_twitter(self):
        """Test feedback text normalization for Twitter mentions."""
        result = normalize_feedback_text(self.twitter_data, 'twitter_mentions')
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result['feedback_text'].iloc[0], 'Great trading')
        self.assertEqual(result['feedback_text'].iloc[1], 'Nice charts')
    
    def test_normalize_feedback_text_sales(self):
        """Test feedback text normalization for sales notes."""
        result = normalize_feedback_text(self.sales_data, 'sales_notes')
        
        self.assertIn('feedback_text', result.columns)
        self.assertEqual(result['feedback_text'].iloc[0], 'Pricing acceptable')
        self.assertEqual(result['feedback_text'].iloc[1], 'Migration approved')
    
    def test_normalize_feedback_text_unknown_source(self):
        """Test feedback text normalization with unknown source type."""
        result = normalize_feedback_text(self.ios_data, 'unknown_source')
        
        # Should return original DataFrame unchanged
        self.assertNotIn('feedback_text', result.columns)
    
    def test_normalize_feedback_text_missing_column(self):
        """Test feedback text normalization with missing source column."""
        # Remove the review_text column
        incomplete_data = self.ios_data.drop('review_text', axis=1)
        result = normalize_feedback_text(incomplete_data, 'ios_reviews')
        
        # Should return original DataFrame unchanged
        self.assertNotIn('feedback_text', result.columns)
    
    def test_normalize_author_handle_ios(self):
        """Test author handle normalization for iOS reviews."""
        result = normalize_author_handle(self.ios_data, 'ios_reviews')
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result['author_handle'].iloc[0], 'user1')
        self.assertEqual(result['author_handle'].iloc[1], 'user2')
    
    def test_normalize_author_handle_twitter(self):
        """Test author handle normalization for Twitter mentions."""
        result = normalize_author_handle(self.twitter_data, 'twitter_mentions')
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result['author_handle'].iloc[0], '@trader1')
        self.assertEqual(result['author_handle'].iloc[1], '@trader2')
    
    def test_normalize_author_handle_sales(self):
        """Test author handle normalization for sales notes."""
        result = normalize_author_handle(self.sales_data, 'sales_notes')
        
        self.assertIn('author_handle', result.columns)
        self.assertEqual(result['author_handle'].iloc[0], 'Acct-001')
        self.assertEqual(result['author_handle'].iloc[1], 'Acct-002')
    
    def test_add_source_channel_ios(self):
        """Test source channel addition for iOS reviews."""
        result = add_source_channel(self.ios_data, 'ios_reviews')
        
        self.assertIn('source_channel', result.columns)
        self.assertTrue((result['source_channel'] == 'iOS App Store').all())
    
    def test_add_source_channel_twitter(self):
        """Test source channel addition for Twitter mentions."""
        result = add_source_channel(self.twitter_data, 'twitter_mentions')
        
        self.assertIn('source_channel', result.columns)
        self.assertTrue((result['source_channel'] == 'Twitter (X)').all())
    
    def test_add_source_channel_sales(self):
        """Test source channel addition for sales notes."""
        result = add_source_channel(self.sales_data, 'sales_notes')
        
        self.assertIn('source_channel', result.columns)
        self.assertTrue((result['source_channel'] == 'Internal Sales Notes').all())
    
    def test_normalize_single_source_ios(self):
        """Test complete normalization of iOS reviews."""
        result = normalize_single_source(self.ios_data, 'ios_reviews')
        
        # Check all normalized columns are present
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        self.assertIn('source_channel', result.columns)
        
        # Check values are correct
        self.assertEqual(result['feedback_text'].iloc[0], 'Great app')
        self.assertEqual(result['author_handle'].iloc[0], 'user1')
        self.assertEqual(result['source_channel'].iloc[0], 'iOS App Store')
    
    def test_normalize_single_source_twitter(self):
        """Test complete normalization of Twitter mentions."""
        result = normalize_single_source(self.twitter_data, 'twitter_mentions')
        
        # Check all normalized columns are present
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        self.assertIn('source_channel', result.columns)
        
        # Check values are correct
        self.assertEqual(result['feedback_text'].iloc[0], 'Great trading')
        self.assertEqual(result['author_handle'].iloc[0], '@trader1')
        self.assertEqual(result['source_channel'].iloc[0], 'Twitter (X)')
    
    def test_unify_dataframes_success(self):
        """Test successful unification of multiple DataFrames."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data
        }
        
        result = unify_dataframes(loaded_data)
        
        # Check total records
        self.assertEqual(len(result), 4)  # 2 iOS + 2 Twitter
        
        # Check normalized columns exist
        self.assertIn('feedback_text', result.columns)
        self.assertIn('author_handle', result.columns)
        self.assertIn('source_channel', result.columns)
        
        # Check source channels are correct
        source_channels = result['source_channel'].unique()
        self.assertIn('iOS App Store', source_channels)
        self.assertIn('Twitter (X)', source_channels)
    
    def test_unify_dataframes_empty_input(self):
        """Test unification with empty input."""
        result = unify_dataframes({})
        
        self.assertTrue(result.empty)
    
    def test_unify_dataframes_with_none_values(self):
        """Test unification with None values in input."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': None,
            'sales_notes': pd.DataFrame()  # Empty DataFrame
        }
        
        result = unify_dataframes(loaded_data)
        
        # Should only include iOS data
        self.assertEqual(len(result), 2)
        self.assertTrue((result['source_channel'] == 'iOS App Store').all())
    
    def test_validate_unified_dataframe_valid(self):
        """Test validation of valid unified DataFrame."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data
        }
        unified_df = unify_dataframes(loaded_data)
        
        self.assertTrue(validate_unified_dataframe(unified_df))
    
    def test_validate_unified_dataframe_empty(self):
        """Test validation of empty DataFrame."""
        empty_df = pd.DataFrame()
        
        self.assertFalse(validate_unified_dataframe(empty_df))
    
    def test_validate_unified_dataframe_missing_columns(self):
        """Test validation of DataFrame with missing required columns."""
        # Create DataFrame missing required columns
        incomplete_df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'feedback_text': ['Test feedback']
            # Missing other required columns
        })
        
        self.assertFalse(validate_unified_dataframe(incomplete_df))
    
    def test_get_normalization_summary(self):
        """Test normalization summary generation."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data
        }
        unified_df = unify_dataframes(loaded_data)
        summary = get_normalization_summary(unified_df)
        
        self.assertEqual(summary['total_records'], 4)
        self.assertEqual(len(summary['sources']), 2)
        self.assertIn('iOS App Store', summary['sources'])
        self.assertIn('Twitter (X)', summary['sources'])
        self.assertEqual(summary['feedback_text_coverage'], 100.0)
        self.assertEqual(summary['author_handle_coverage'], 100.0)
    
    def test_get_normalization_summary_empty(self):
        """Test normalization summary for empty DataFrame."""
        empty_df = pd.DataFrame()
        summary = get_normalization_summary(empty_df)
        
        self.assertEqual(summary['total_records'], 0)
        self.assertEqual(len(summary['sources']), 0)
        self.assertEqual(summary['feedback_text_coverage'], 0)
        self.assertEqual(summary['author_handle_coverage'], 0)
    
    def test_normalize_and_unify_data_complete(self):
        """Test complete normalization and unification process."""
        loaded_data = {
            'ios_reviews': self.ios_data,
            'twitter_mentions': self.twitter_data,
            'sales_notes': self.sales_data
        }
        
        result = normalize_and_unify_data(loaded_data)
        
        # Check total records
        self.assertEqual(len(result), 6)  # 2 iOS + 2 Twitter + 2 Sales
        
        # Check all required columns exist
        for col in STANDARD_COLUMNS:
            self.assertIn(col, result.columns)
        
        # Check source channels
        source_channels = result['source_channel'].unique()
        self.assertEqual(len(source_channels), 3)
        self.assertIn('iOS App Store', source_channels)
        self.assertIn('Twitter (X)', source_channels)
        self.assertIn('Internal Sales Notes', source_channels)
        
        # Check feedback text normalization worked
        ios_records = result[result['source_channel'] == 'iOS App Store']
        self.assertEqual(ios_records['feedback_text'].iloc[0], 'Great app')
        
        twitter_records = result[result['source_channel'] == 'Twitter (X)']
        self.assertEqual(twitter_records['feedback_text'].iloc[0], 'Great trading')
        
        sales_records = result[result['source_channel'] == 'Internal Sales Notes']
        self.assertEqual(sales_records['feedback_text'].iloc[0], 'Pricing acceptable')


if __name__ == '__main__':
    unittest.main()