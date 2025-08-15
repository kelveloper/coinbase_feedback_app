"""
Unit tests for NLP Models Module

Tests the sentiment, theme, and strategic goal extraction functions
using various input scenarios including edge cases and error conditions.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analysis.nlp_models import (
    get_sentiment, 
    get_theme, 
    get_strategic_goal,
    enrich_dataframe_with_nlp
)


class TestGetSentiment(unittest.TestCase):
    """Test cases for get_sentiment function"""
    
    def test_valid_positive_sentiment(self):
        """Test extraction of positive sentiment"""
        record = pd.Series({'sentiment': 'positive'})
        result = get_sentiment(record)
        self.assertEqual(result, 'positive')
    
    def test_valid_negative_sentiment(self):
        """Test extraction of negative sentiment"""
        record = pd.Series({'sentiment': 'negative'})
        result = get_sentiment(record)
        self.assertEqual(result, 'negative')
    
    def test_valid_neutral_sentiment(self):
        """Test extraction of neutral sentiment"""
        record = pd.Series({'sentiment': 'neutral'})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')
    
    def test_case_insensitive_sentiment(self):
        """Test sentiment extraction with different cases"""
        record = pd.Series({'sentiment': 'POSITIVE'})
        result = get_sentiment(record)
        self.assertEqual(result, 'positive')
        
        record = pd.Series({'sentiment': 'Negative'})
        result = get_sentiment(record)
        self.assertEqual(result, 'negative')
    
    def test_sentiment_with_whitespace(self):
        """Test sentiment extraction with whitespace"""
        record = pd.Series({'sentiment': '  positive  '})
        result = get_sentiment(record)
        self.assertEqual(result, 'positive')
    
    def test_missing_sentiment_column(self):
        """Test default value when sentiment column is missing"""
        record = pd.Series({'other_column': 'value'})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')
    
    def test_null_sentiment_value(self):
        """Test default value when sentiment is null"""
        record = pd.Series({'sentiment': None})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')
        
        record = pd.Series({'sentiment': np.nan})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')
    
    def test_invalid_sentiment_value(self):
        """Test default value for invalid sentiment"""
        record = pd.Series({'sentiment': 'invalid_sentiment'})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')
        
        record = pd.Series({'sentiment': 123})
        result = get_sentiment(record)
        self.assertEqual(result, 'neutral')


class TestGetTheme(unittest.TestCase):
    """Test cases for get_theme function"""   
 
    def test_valid_theme_extraction(self):
        """Test extraction of valid theme"""
        record = pd.Series({'theme': 'Trading/Execution & Fees'})
        result = get_theme(record)
        self.assertEqual(result, 'Trading/Execution & Fees')
    
    def test_theme_with_whitespace(self):
        """Test theme extraction with whitespace"""
        record = pd.Series({'theme': '  Performance/Outages  '})
        result = get_theme(record)
        self.assertEqual(result, 'Performance/Outages')
    
    def test_missing_theme_column(self):
        """Test default value when theme column is missing"""
        record = pd.Series({'other_column': 'value'})
        result = get_theme(record)
        self.assertEqual(result, 'General Feedback')
    
    def test_null_theme_value(self):
        """Test default value when theme is null"""
        record = pd.Series({'theme': None})
        result = get_theme(record)
        self.assertEqual(result, 'General Feedback')
        
        record = pd.Series({'theme': np.nan})
        result = get_theme(record)
        self.assertEqual(result, 'General Feedback')
    
    def test_empty_theme_value(self):
        """Test default value for empty theme"""
        record = pd.Series({'theme': ''})
        result = get_theme(record)
        self.assertEqual(result, 'General Feedback')
        
        record = pd.Series({'theme': '   '})
        result = get_theme(record)
        self.assertEqual(result, 'General Feedback')
    
    def test_numeric_theme_conversion(self):
        """Test theme extraction with numeric input"""
        record = pd.Series({'theme': 123})
        result = get_theme(record)
        self.assertEqual(result, '123')


class TestGetStrategicGoal(unittest.TestCase):
    """Test cases for get_strategic_goal function"""
    
    def test_valid_strategic_goals(self):
        """Test extraction of all valid strategic goals"""
        valid_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
        
        for goal in valid_goals:
            record = pd.Series({'strategic_goal': goal})
            result = get_strategic_goal(record)
            self.assertEqual(result, goal)
    
    def test_missing_strategic_goal_column(self):
        """Test default value when strategic_goal column is missing"""
        record = pd.Series({'other_column': 'value'})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'General')
    
    def test_null_strategic_goal_value(self):
        """Test default value when strategic_goal is null"""
        record = pd.Series({'strategic_goal': None})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'General')
        
        record = pd.Series({'strategic_goal': np.nan})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'General')
    
    def test_invalid_strategic_goal_value(self):
        """Test default value for invalid strategic goal"""
        record = pd.Series({'strategic_goal': 'Invalid Goal'})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'General')
        
        record = pd.Series({'strategic_goal': 123})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'General')
    
    def test_strategic_goal_with_whitespace(self):
        """Test strategic goal extraction with whitespace"""
        record = pd.Series({'strategic_goal': '  Growth  '})
        result = get_strategic_goal(record)
        self.assertEqual(result, 'Growth')


class TestEnrichDataframeWithNlp(unittest.TestCase):
    """Test cases for enrich_dataframe_with_nlp function"""  
  
    def test_enrich_empty_dataframe(self):
        """Test enrichment of empty DataFrame"""
        df = pd.DataFrame()
        result = enrich_dataframe_with_nlp(df)
        self.assertTrue(result.empty)
        self.assertTrue(result.equals(df))
    
    def test_enrich_complete_dataframe(self):
        """Test enrichment of DataFrame with complete data"""
        df = pd.DataFrame({
            'customer_id': ['TEST-001', 'TEST-002'],
            'sentiment': ['positive', 'negative'],
            'theme': ['Trading/Execution & Fees', 'Performance/Outages'],
            'strategic_goal': ['Growth', 'Trust&Safety'],
            'feedback_text': ['Great app!', 'App is slow']
        })
        
        result = enrich_dataframe_with_nlp(df)
        
        # Check that all NLP columns are present
        self.assertIn('sentiment', result.columns)
        self.assertIn('theme', result.columns)
        self.assertIn('strategic_goal', result.columns)
        
        # Check values are correctly extracted
        self.assertEqual(result.loc[0, 'sentiment'], 'positive')
        self.assertEqual(result.loc[1, 'sentiment'], 'negative')
        self.assertEqual(result.loc[0, 'theme'], 'Trading/Execution & Fees')
        self.assertEqual(result.loc[1, 'theme'], 'Performance/Outages')
        self.assertEqual(result.loc[0, 'strategic_goal'], 'Growth')
        self.assertEqual(result.loc[1, 'strategic_goal'], 'Trust&Safety')
    
    def test_enrich_dataframe_with_missing_columns(self):
        """Test enrichment of DataFrame with missing NLP columns"""
        df = pd.DataFrame({
            'customer_id': ['TEST-001', 'TEST-002'],
            'feedback_text': ['Great app!', 'App is slow']
        })
        
        result = enrich_dataframe_with_nlp(df)
        
        # Check that NLP columns are added with default values
        self.assertIn('sentiment', result.columns)
        self.assertIn('theme', result.columns)
        self.assertIn('strategic_goal', result.columns)
        
        # Check default values are applied
        self.assertTrue(all(result['sentiment'] == 'neutral'))
        self.assertTrue(all(result['theme'] == 'General Feedback'))
        self.assertTrue(all(result['strategic_goal'] == 'General'))
    
    def test_enrich_dataframe_with_null_values(self):
        """Test enrichment of DataFrame with null NLP values"""
        df = pd.DataFrame({
            'customer_id': ['TEST-001', 'TEST-002'],
            'sentiment': [None, np.nan],
            'theme': [None, ''],
            'strategic_goal': [np.nan, 'Invalid Goal'],
            'feedback_text': ['Great app!', 'App is slow']
        })
        
        result = enrich_dataframe_with_nlp(df)
        
        # Check that null values are replaced with defaults
        self.assertTrue(all(result['sentiment'] == 'neutral'))
        self.assertTrue(all(result['theme'] == 'General Feedback'))
        self.assertTrue(all(result['strategic_goal'] == 'General'))
    
    def test_enrich_dataframe_preserves_original(self):
        """Test that enrichment doesn't modify the original DataFrame"""
        original_df = pd.DataFrame({
            'customer_id': ['TEST-001'],
            'sentiment': ['positive'],
            'theme': ['Trading/Execution & Fees'],
            'strategic_goal': ['Growth']
        })
        
        # Create a copy to compare
        original_copy = original_df.copy()
        
        # Enrich the DataFrame
        result = enrich_dataframe_with_nlp(original_df)
        
        # Check that original DataFrame is unchanged
        pd.testing.assert_frame_equal(original_df, original_copy)
        
        # Check that result is different object
        self.assertIsNot(result, original_df)
    
    def test_enrich_dataframe_mixed_valid_invalid_data(self):
        """Test enrichment with mix of valid and invalid data"""
        df = pd.DataFrame({
            'customer_id': ['TEST-001', 'TEST-002', 'TEST-003'],
            'sentiment': ['positive', 'invalid', None],
            'theme': ['Trading/Execution & Fees', '', 'Support Experience'],
            'strategic_goal': ['Growth', 'Invalid Goal', 'Compliance']
        })
        
        result = enrich_dataframe_with_nlp(df)
        
        # Check mixed results
        self.assertEqual(result.loc[0, 'sentiment'], 'positive')
        self.assertEqual(result.loc[1, 'sentiment'], 'neutral')  # invalid -> default
        self.assertEqual(result.loc[2, 'sentiment'], 'neutral')  # None -> default
        
        self.assertEqual(result.loc[0, 'theme'], 'Trading/Execution & Fees')
        self.assertEqual(result.loc[1, 'theme'], 'General Feedback')  # empty -> default
        self.assertEqual(result.loc[2, 'theme'], 'Support Experience')
        
        self.assertEqual(result.loc[0, 'strategic_goal'], 'Growth')
        self.assertEqual(result.loc[1, 'strategic_goal'], 'General')  # invalid -> default
        self.assertEqual(result.loc[2, 'strategic_goal'], 'Compliance')


if __name__ == '__main__':
    unittest.main()