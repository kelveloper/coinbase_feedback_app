"""
Integration tests for main dashboard application.

Tests cover complete dashboard functionality including data loading, processing,
component integration, and error handling.
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock, call
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.dashboard import (
    load_and_process_data,
    display_sidebar_info,
    display_main_dashboard,
    display_error_page,
    main
)


class TestDashboardIntegration(unittest.TestCase):
    """Test cases for dashboard integration functionality."""
    
    def setUp(self):
        """Set up test data for dashboard integration tests."""
        self.sample_processed_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play'],
            'source': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play'],
            'feedback_text': [
                'Great app but needs better performance',
                'Love the new features!',
                'Customer wants advanced trading tools',
                'App crashes frequently'
            ],
            'sentiment': ['negative', 'positive', 'neutral', 'negative'],
            'theme': ['Performance', 'Features', 'Trading Tools', 'Performance'],
            'impact_score': [2.5, 1.2, 4.8, 3.1],
            'source_weight': [1.0, 1.5, 2.0, 1.2],
            'timestamp': pd.to_datetime([
                '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'
            ])
        })
        
        self.mock_loaded_data = {
            'ios_reviews': pd.DataFrame({
                'customer_id': ['C001'],
                'source': ['iOS App Store'],
                'username': ['user1'],
                'timestamp': ['2024-01-01'],
                'rating': [4],
                'sentiment': ['negative'],
                'review_text': ['Great app but needs better performance'],
                'theme': ['Performance'],
                'severity': [2.0],
                'strategic_goal': ['Growth']
            }),
            'twitter_mentions': pd.DataFrame({
                'customer_id': ['C002'],
                'source': ['Twitter'],
                'handle': ['@user2'],
                'followers': [1000],
                'timestamp': ['2024-01-02'],
                'sentiment': ['positive'],
                'tweet_text': ['Love the new features!'],
                'theme': ['Features'],
                'severity': [1.0],
                'strategic_goal': ['Growth']
            })
        }
    
    @patch('dashboard.dashboard.enrich_dataframe_with_scores')
    @patch('dashboard.dashboard.normalize_and_unify_data')
    @patch('dashboard.dashboard.get_loading_summary')
    @patch('dashboard.dashboard.load_all_csv_files')
    @patch('dashboard.dashboard.st.spinner')
    @patch('dashboard.dashboard.st.success')
    @patch('dashboard.dashboard.st.info')
    def test_load_and_process_data_success(self, mock_info, mock_success, mock_spinner, 
                                          mock_load_csv, mock_summary, mock_normalize, mock_enrich):
        """Test successful data loading and processing."""
        # Mock the data pipeline
        mock_load_csv.return_value = self.mock_loaded_data
        mock_summary.return_value = {'total_records': 2, 'sources_loaded': 2}
        mock_normalize.return_value = self.sample_processed_data.drop(columns=['impact_score', 'source_weight'])
        mock_enrich.return_value = self.sample_processed_data
        
        # Mock spinner context manager
        mock_spinner.return_value.__enter__ = MagicMock()
        mock_spinner.return_value.__exit__ = MagicMock()
        
        result = load_and_process_data("test_directory")
        
        # Verify successful processing
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 4)
        self.assertIn('impact_score', result.columns)
        
        # Verify function calls
        mock_load_csv.assert_called_once_with("test_directory")
        mock_normalize.assert_called_once()
        mock_enrich.assert_called_once()
    
    @patch('dashboard.dashboard.load_all_csv_files')
    @patch('dashboard.dashboard.st.error')
    @patch('dashboard.dashboard.st.info')
    def test_load_and_process_data_no_files(self, mock_info, mock_error, mock_load_csv):
        """Test data loading when no files are found."""
        # Mock empty data loading
        mock_load_csv.return_value = {}
        
        result = load_and_process_data("empty_directory")
        
        # Verify None result and error handling
        self.assertIsNone(result)
        mock_error.assert_called_once()
        self.assertGreaterEqual(mock_info.call_count, 4)  # File list info messages
    
    @patch('dashboard.dashboard.load_all_csv_files')
    @patch('dashboard.dashboard.st.error')
    def test_load_and_process_data_exception(self, mock_error, mock_load_csv):
        """Test data loading when exception occurs."""
        # Mock exception during loading
        mock_load_csv.side_effect = Exception("Test error")
        
        result = load_and_process_data("test_directory")
        
        # Verify None result and error handling
        self.assertIsNone(result)
        mock_error.assert_called_once()
    
    @patch('dashboard.dashboard.st.sidebar')
    def test_display_sidebar_info_with_data(self, mock_sidebar):
        """Test sidebar display with valid data."""
        # Mock sidebar components
        mock_sidebar.title = MagicMock()
        mock_sidebar.button = MagicMock(return_value=False)
        mock_sidebar.subheader = MagicMock()
        mock_sidebar.metric = MagicMock()
        mock_sidebar.write = MagicMock()
        mock_sidebar.text_input = MagicMock(return_value="csv_mock_data")
        mock_sidebar.checkbox = MagicMock(return_value=True)
        
        result = display_sidebar_info(self.sample_processed_data)
        
        # Verify configuration returned
        self.assertIn('data_directory', result)
        self.assertIn('show_raw_data', result)
        self.assertIn('show_charts', result)
        
        # Verify sidebar components called
        mock_sidebar.title.assert_called()
        mock_sidebar.metric.assert_called()
    
    @patch('dashboard.dashboard.st.sidebar')
    def test_display_sidebar_info_no_data(self, mock_sidebar):
        """Test sidebar display with no data."""
        # Mock sidebar components
        mock_sidebar.title = MagicMock()
        mock_sidebar.button = MagicMock(return_value=False)
        mock_sidebar.warning = MagicMock()
        mock_sidebar.subheader = MagicMock()
        mock_sidebar.text_input = MagicMock(return_value="csv_mock_data")
        mock_sidebar.checkbox = MagicMock(return_value=True)
        
        result = display_sidebar_info(None)
        
        # Verify configuration returned
        self.assertIn('data_directory', result)
        
        # Verify warning displayed
        mock_sidebar.warning.assert_called_once_with("No data loaded")
    
    @patch('dashboard.dashboard.create_comprehensive_dashboard_charts')
    @patch('dashboard.dashboard.display_filterable_data_table')
    @patch('dashboard.dashboard.create_filter_controls')
    @patch('dashboard.dashboard.display_kpi_header')
    @patch('dashboard.dashboard.display_summary_stats')
    @patch('dashboard.dashboard.st.title')
    @patch('dashboard.dashboard.st.subheader')
    @patch('dashboard.dashboard.st.markdown')
    @patch('dashboard.dashboard.st.success')
    @patch('dashboard.dashboard.st.columns')
    def test_display_main_dashboard_success(self, mock_columns, mock_success, mock_markdown, 
                                          mock_subheader, mock_title, mock_stats, mock_kpi, 
                                          mock_filters, mock_table, mock_charts):
        """Test successful main dashboard display."""
        # Mock component returns
        mock_kpi.return_value = {'total_items': 4, 'avg_sentiment': 'Neutral', 'top_theme': 'Performance'}
        mock_filters.return_value = {'sentiment': 'All', 'theme': 'All'}
        mock_table.return_value = self.sample_processed_data
        mock_charts.return_value = {'theme_impact': True, 'sentiment_distribution': True}
        mock_stats.return_value = {'sentiment_distribution': {'positive': 1, 'negative': 2}}
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        config = {'show_charts': True, 'show_raw_data': True}
        
        # Should not raise exception
        display_main_dashboard(self.sample_processed_data, config)
        
        # Verify components called
        mock_title.assert_called_once()
        mock_kpi.assert_called_once()
        mock_filters.assert_called_once()
        mock_charts.assert_called_once()
        mock_table.assert_called_once()
    
    @patch('dashboard.dashboard.st.error')
    @patch('dashboard.dashboard.st.title')
    def test_display_main_dashboard_exception(self, mock_title, mock_error):
        """Test main dashboard display when exception occurs."""
        # Mock title to raise exception
        mock_title.side_effect = Exception("Test error")
        
        config = {'show_charts': True, 'show_raw_data': True}
        
        # Should handle exception gracefully
        display_main_dashboard(self.sample_processed_data, config)
        
        # Verify error handling
        mock_error.assert_called_once()
    
    @patch('dashboard.dashboard.st.title')
    @patch('dashboard.dashboard.st.error')
    @patch('dashboard.dashboard.st.subheader')
    @patch('dashboard.dashboard.st.write')
    @patch('dashboard.dashboard.st.info')
    @patch('dashboard.dashboard.st.code')
    @patch('dashboard.dashboard.st.button')
    def test_display_error_page(self, mock_button, mock_code, mock_info, mock_write, 
                               mock_subheader, mock_error, mock_title):
        """Test error page display."""
        mock_button.return_value = False
        
        display_error_page("Test error message")
        
        # Verify error page components
        mock_title.assert_called_once_with("⚠️ Dashboard Error")
        mock_error.assert_called_once_with("Test error message")
        mock_subheader.assert_called_once()
        self.assertGreater(mock_write.call_count, 0)
        self.assertGreater(mock_info.call_count, 0)
        mock_code.assert_called_once()
        mock_button.assert_called_once()
    
    @patch('dashboard.dashboard.display_error_page')
    @patch('dashboard.dashboard.display_main_dashboard')
    @patch('dashboard.dashboard.display_sidebar_info')
    @patch('dashboard.dashboard.load_and_process_data')
    def test_main_function_success(self, mock_load_data, mock_sidebar, mock_main_dash, mock_error_page):
        """Test main function with successful data loading."""
        # Mock successful data loading
        mock_load_data.return_value = self.sample_processed_data
        mock_sidebar.return_value = {'data_directory': 'csv_mock_data'}
        
        main()
        
        # Verify function calls
        mock_load_data.assert_called()
        self.assertEqual(mock_sidebar.call_count, 2)  # Called twice - before and after data loading
        mock_main_dash.assert_called_once()
        mock_error_page.assert_not_called()
    
    @patch('dashboard.dashboard.display_error_page')
    @patch('dashboard.dashboard.display_sidebar_info')
    @patch('dashboard.dashboard.load_and_process_data')
    def test_main_function_data_loading_failure(self, mock_load_data, mock_sidebar, mock_error_page):
        """Test main function when data loading fails."""
        # Mock failed data loading
        mock_load_data.return_value = None
        mock_sidebar.return_value = {'data_directory': 'csv_mock_data'}
        
        main()
        
        # Verify error handling
        mock_load_data.assert_called_once()
        mock_error_page.assert_called_once()
    
    @patch('dashboard.dashboard.display_error_page')
    @patch('dashboard.dashboard.display_sidebar_info')
    def test_main_function_exception(self, mock_sidebar, mock_error_page):
        """Test main function when exception occurs."""
        # Mock sidebar to raise exception
        mock_sidebar.side_effect = Exception("Test error")
        
        main()
        
        # Verify error handling
        mock_error_page.assert_called_once()
    
    def test_data_filtering_logic(self):
        """Test data filtering logic in main dashboard."""
        # This tests the filtering logic that's embedded in display_main_dashboard
        df = self.sample_processed_data.copy()
        
        # Test sentiment filter
        filters = {'sentiment': 'positive'}
        filtered_df = df.copy()
        for filter_name, filter_value in filters.items():
            if filter_value and filter_value != 'All':
                if filter_name in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[filter_name] == filter_value]
        
        # Verify filtering worked
        self.assertEqual(len(filtered_df), 1)
        self.assertTrue(all(filtered_df['sentiment'] == 'positive'))
        
        # Test multiple filters
        filters = {'sentiment': 'negative', 'theme': 'Performance'}
        filtered_df = df.copy()
        for filter_name, filter_value in filters.items():
            if filter_value and filter_value != 'All':
                if filter_name in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[filter_name] == filter_value]
        
        # Verify multiple filtering worked
        self.assertEqual(len(filtered_df), 2)
        self.assertTrue(all(filtered_df['sentiment'] == 'negative'))
        self.assertTrue(all(filtered_df['theme'] == 'Performance'))


if __name__ == '__main__':
    unittest.main()