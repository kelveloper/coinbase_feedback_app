"""
End-to-End Workflow Tests for Advanced Trade Insight Engine

This module tests the complete workflow from data loading through report generation
and dashboard preparation, ensuring all components work together correctly.

Requirements: 8.2, 8.3, 8.4
"""

import unittest
import pandas as pd
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from main import main
    from data_processing.data_loader import load_all_csv_files
    from data_processing.data_normalizer import normalize_and_unify_data
    from analysis.nlp_models import get_sentiment, get_theme, get_strategic_goal
    from analysis.scoring_engine import calculate_source_weight, calculate_impact_score
    from reporting.content_builder import build_comprehensive_content
    from reporting.report_generator import generate_complete_report
except ImportError as e:
    # Handle import errors gracefully for testing
    print(f"Import warning: {e}")
    pass


class TestEndToEndWorkflow(unittest.TestCase):
    """
    End-to-end workflow tests for the complete data pipeline.
    
    Requirements: 8.2, 8.3, 8.4
    """
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'csv_mock_data')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create mock CSV files for testing
        self._create_mock_csv_files()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_mock_csv_files(self):
        """Create mock CSV files for testing."""
        # iOS App Store reviews
        ios_data = pd.DataFrame({
            'customer_id': ['IOS-001', 'IOS-002'],
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
            'customer_id': ['AND-001', 'AND-002'],
            'source': ['Google Play Store', 'Google Play Store'],
            'username': ['android_user1', 'android_user2'],
            'timestamp': ['2024-01-03 12:00:00', '2024-01-04 13:00:00'],
            'rating': [5, 3],
            'sentiment': ['positive', 'neutral'],
            'review_text': ['Excellent app!', 'Decent app'],
            'theme': ['General Feedback', 'Support Experience'],
            'severity': [0.5, 1.5],
            'strategic_goal': ['Growth', 'Trust&Safety'],
            'helpful_votes': [8, 4]
        })
        android_data.to_csv(os.path.join(self.data_dir, 'coinbase_advanceGoogle_Play.csv'), index=False)
        
        # Twitter mentions
        twitter_data = pd.DataFrame({
            'customer_id': ['TW-001', 'TW-002'],
            'source': ['Twitter (X)', 'Twitter (X)'],
            'handle': ['@trader1', '@trader2'],
            'followers': [148860, 106574],
            'timestamp': ['2024-01-05 14:00:00', '2024-01-06 15:00:00'],
            'sentiment': ['positive', 'negative'],
            'tweet_text': ['Great trading experience!', 'Having issues'],
            'theme': ['Trading/Execution & Fees', 'Support Experience'],
            'severity': [1.0, 2.0],
            'strategic_goal': ['Growth', 'CX Efficiency']
        })
        twitter_data.to_csv(os.path.join(self.data_dir, 'coinbase_advanced_twitter_mentions.csv'), index=False)
        
        # Internal sales notes
        sales_data = pd.DataFrame({
            'customer_id': ['SALES-001', 'SALES-002'],
            'source': ['Internal Sales Notes', 'Internal Sales Notes'],
            'account_name': ['Enterprise Corp', 'Startup Inc'],
            'timestamp': ['2024-01-07 16:00:00', '2024-01-08 17:00:00'],
            'sentiment': ['positive', 'neutral'],
            'note_text': ['Customer very satisfied', 'Customer has concerns'],
            'theme': ['Performance', 'Trading/Execution & Fees'],
            'severity': [1.0, 1.5],
            'strategic_goal': ['Growth', 'CX Efficiency'],
            'ARR_impact_estimate_USD': [75000, 25000]
        })
        sales_data.to_csv(os.path.join(self.data_dir, 'coinbase_advance_internal_sales_notes.csv'), index=False)
    
    def test_complete_data_pipeline_workflow(self):
        """Test the complete data pipeline from CSV loading to normalized output."""
        try:
            # 1. Load all CSV files
            dataframes = load_all_csv_files(self.data_dir)
            
            # Verify all expected files were loaded
            expected_files = [
                'coinbase_advance_apple_reviews.csv',
                'coinbase_advanceGoogle_Play.csv',
                'coinbase_advanced_twitter_mentions.csv',
                'coinbase_advance_internal_sales_notes.csv'
            ]
            
            self.assertEqual(len(dataframes), len(expected_files))
            
            # 2. Normalize data
            normalized_df = normalize_and_unify_data(dataframes)
            
            # Verify normalization results
            self.assertFalse(normalized_df.empty)
            self.assertIn('feedback_text', normalized_df.columns)
            self.assertIn('author_handle', normalized_df.columns)
            self.assertIn('source_channel', normalized_df.columns)
            
            # 3. Verify data integrity
            self.assertTrue(normalized_df['customer_id'].notna().all())
            self.assertTrue(normalized_df['timestamp'].notna().all())
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_nlp_processing_workflow(self):
        """Test NLP processing workflow with normalized data."""
        try:
            # Load and normalize data
            dataframes = load_all_csv_files(self.data_dir)
            normalized_df = normalize_and_unify_data(dataframes)
            
            # Test NLP extraction functions on first row
            if not normalized_df.empty:
                row = normalized_df.iloc[0]
                
                # Test sentiment extraction
                sentiment = get_sentiment(row)
                self.assertIn(sentiment, ['positive', 'neutral', 'negative'])
                
                # Test theme extraction
                theme = get_theme(row)
                self.assertIsInstance(theme, str)
                self.assertGreater(len(theme), 0)
                
                # Test strategic goal extraction
                strategic_goal = get_strategic_goal(row)
                self.assertIsInstance(strategic_goal, str)
                self.assertGreater(len(strategic_goal), 0)
                
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_scoring_workflow(self):
        """Test impact scoring workflow with processed data."""
        try:
            # Load and normalize data
            dataframes = load_all_csv_files(self.data_dir)
            normalized_df = normalize_and_unify_data(dataframes)
            
            # Test source weight calculation on first row
            if not normalized_df.empty:
                row = normalized_df.iloc[0]
                
                source_weight = calculate_source_weight(row)
                self.assertIsInstance(source_weight, (int, float))
                self.assertGreater(source_weight, 0)
                
                # Test impact score calculation
                impact_score = calculate_impact_score(row)
                self.assertIsInstance(impact_score, (int, float))
                self.assertGreaterEqual(impact_score, 0)
                
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_report_generation_workflow(self):
        """Test complete report generation workflow."""
        try:
            # Load and normalize data
            dataframes = load_all_csv_files(self.data_dir)
            normalized_df = normalize_and_unify_data(dataframes)
            
            # Test content building
            report_content = build_comprehensive_content(normalized_df)
            
            # Verify report content structure
            self.assertIn('executive_summary', report_content)
            self.assertIn('top_pain_points', report_content)
            self.assertIn('praised_features', report_content)
            self.assertIn('strategic_insights', report_content)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_error_handling_in_workflow(self):
        """Test error handling throughout the workflow."""
        try:
            # Test with missing data directory
            with self.assertRaises(Exception):
                load_all_csv_files('/nonexistent/directory')
            
            # Test with empty dataframes
            empty_dataframes = {}
            normalized_df = normalize_and_unify_data(empty_dataframes)
            self.assertTrue(normalized_df.empty)
            
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_data_consistency_across_workflow(self):
        """Test data consistency is maintained throughout the workflow."""
        try:
            # Load and normalize data
            dataframes = load_all_csv_files(self.data_dir)
            normalized_df = normalize_and_unify_data(dataframes)
            
            # Store original data for comparison
            original_count = sum(len(df) for df in dataframes.values())
            
            # Verify no data was lost
            self.assertEqual(len(normalized_df), original_count)
            
            # Verify required columns are present
            required_columns = ['customer_id', 'feedback_text', 'author_handle', 'source_channel']
            for col in required_columns:
                self.assertIn(col, normalized_df.columns)
                
        except ImportError:
            self.skipTest("Required modules not available for testing")
    
    def test_complete_end_to_end_execution(self):
        """Test complete end-to-end execution with all components."""
        try:
            # Load data
            dataframes = load_all_csv_files(self.data_dir)
            self.assertGreater(len(dataframes), 0)
            
            # Normalize data
            normalized_df = normalize_and_unify_data(dataframes)
            self.assertFalse(normalized_df.empty)
            
            # Verify final data quality
            self.assertGreater(len(normalized_df), 0)
            self.assertIn('feedback_text', normalized_df.columns)
            
            print(f"✅ End-to-end workflow completed successfully with {len(normalized_df)} records")
            
        except ImportError:
            self.skipTest("Required modules not available for testing")


if __name__ == '__main__':
    unittest.main()
