"""
Unit tests for dashboard components module.

Tests cover KPI displays, filter controls, data tables, and other
reusable dashboard UI components.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.components import (
    display_kpi_header,
    create_filter_controls,
    display_filterable_data_table,
    display_summary_stats,
    format_impact_score,
    format_sentiment_display,
    get_unique_filter_values
)


class TestDisplayKpiHeader(unittest.TestCase):
    """Test cases for display_kpi_header function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004'],
            'sentiment': ['positive', 'negative', 'neutral', 'positive'],
            'theme': ['Performance', 'Features', 'Support', 'Performance'],
            'impact_score': [5.2, 8.1, 3.7, 6.4],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play']
        })
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_display_kpi_header_basic(self, mock_metric, mock_columns):
        """Test basic KPI header display."""
        # Mock columns
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock metric calls
        mock_col1.metric = MagicMock()
        mock_col2.metric = MagicMock()
        mock_col3.metric = MagicMock()
        
        result = display_kpi_header(self.sample_data)
        
        # Should return KPI data
        self.assertIn('total_items', result)
        self.assertIn('avg_sentiment', result)
        self.assertIn('top_theme', result)
        
        # Check calculated values
        self.assertEqual(result['total_items'], 4)
        self.assertEqual(result['top_theme'], 'Performance')  # Most frequent theme
        
        # Verify Streamlit calls
        mock_columns.assert_called_once_with(3)
        self.assertEqual(mock_col1.metric.call_count, 1)
        self.assertEqual(mock_col2.metric.call_count, 1)
        self.assertEqual(mock_col3.metric.call_count, 1)
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_display_kpi_header_empty_data(self, mock_metric, mock_columns):
        """Test KPI header display with empty data."""
        empty_df = pd.DataFrame()
        
        # Mock columns
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock metric calls
        mock_col1.metric = MagicMock()
        mock_col2.metric = MagicMock()
        mock_col3.metric = MagicMock()
        
        result = display_kpi_header(empty_df)
        
        # Should handle empty data gracefully
        self.assertEqual(result['total_items'], 0)
        self.assertEqual(result['avg_sentiment'], 'No data')
        self.assertEqual(result['top_theme'], 'No data')
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_display_kpi_header_single_item(self, mock_metric, mock_columns):
        """Test KPI header display with single data item."""
        single_item = self.sample_data.iloc[:1].copy()
        
        # Mock columns
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock metric calls
        mock_col1.metric = MagicMock()
        mock_col2.metric = MagicMock()
        mock_col3.metric = MagicMock()
        
        result = display_kpi_header(single_item)
        
        # Should handle single item
        self.assertEqual(result['total_items'], 1)
        self.assertEqual(result['top_theme'], 'Performance')


class TestCreateFilterControls(unittest.TestCase):
    """Test cases for create_filter_controls function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative'],
            'theme': ['Performance', 'Features', 'Support', 'Performance', 'UI/UX'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store'],
            'strategic_goal': ['Growth', 'Trust&Safety', 'CX Efficiency', 'Growth', 'Growth']
        })
    
    @patch('dashboard.components.st.sidebar')
    def test_create_filter_controls_basic(self, mock_sidebar):
        """Test basic filter controls creation."""
        # Mock sidebar components
        mock_sidebar.subheader = MagicMock()
        mock_sidebar.selectbox = MagicMock(side_effect=['All', 'All', 'All', 'All'])
        
        filters = create_filter_controls(self.sample_data)
        
        # Should return filter dictionary
        self.assertIn('sentiment', filters)
        self.assertIn('theme', filters)
        self.assertIn('source_channel', filters)
        self.assertIn('strategic_goal', filters)
        
        # Verify sidebar calls
        mock_sidebar.subheader.assert_called_once()
        self.assertEqual(mock_sidebar.selectbox.call_count, 4)
    
    @patch('dashboard.components.st.sidebar')
    def test_create_filter_controls_empty_data(self, mock_sidebar):
        """Test filter controls creation with empty data."""
        empty_df = pd.DataFrame()
        
        # Mock sidebar components
        mock_sidebar.subheader = MagicMock()
        mock_sidebar.selectbox = MagicMock(side_effect=['All', 'All', 'All', 'All'])
        
        filters = create_filter_controls(empty_df)
        
        # Should handle empty data gracefully
        self.assertIn('sentiment', filters)
        self.assertIn('theme', filters)
        self.assertIn('source_channel', filters)
        self.assertIn('strategic_goal', filters)
    
    @patch('dashboard.components.st.sidebar')
    def test_create_filter_controls_missing_columns(self, mock_sidebar):
        """Test filter controls creation with missing columns."""
        incomplete_data = pd.DataFrame({
            'sentiment': ['positive', 'negative'],
            'other_column': ['value1', 'value2']
            # Missing theme, source_channel, strategic_goal
        })
        
        # Mock sidebar components
        mock_sidebar.subheader = MagicMock()
        mock_sidebar.selectbox = MagicMock(side_effect=['All', 'All', 'All', 'All'])
        
        filters = create_filter_controls(incomplete_data)
        
        # Should handle missing columns gracefully
        self.assertIn('sentiment', filters)
        self.assertIn('theme', filters)
        self.assertIn('source_channel', filters)
        self.assertIn('strategic_goal', filters)


class TestDisplayFilterableDataTable(unittest.TestCase):
    """Test cases for display_filterable_data_table function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004'],
            'feedback_text': ['Great app', 'Needs work', 'Good support', 'Love features'],
            'sentiment': ['positive', 'negative', 'positive', 'positive'],
            'theme': ['Performance', 'Performance', 'Support', 'Features'],
            'impact_score': [5.2, 8.1, 3.7, 6.4],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play']
        })
        
        self.filters = {
            'sentiment': 'All',
            'theme': 'All',
            'source_channel': 'All',
            'strategic_goal': 'All'
        }
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    def test_display_filterable_data_table_no_filters(self, mock_dataframe, mock_subheader):
        """Test data table display with no filters applied."""
        result_df = display_filterable_data_table(self.sample_data, self.filters)
        
        # Should return original data
        self.assertEqual(len(result_df), 4)
        
        # Verify Streamlit calls
        mock_subheader.assert_called_once()
        mock_dataframe.assert_called_once()
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    def test_display_filterable_data_table_with_sentiment_filter(self, mock_dataframe, mock_subheader):
        """Test data table display with sentiment filter."""
        filters_with_sentiment = self.filters.copy()
        filters_with_sentiment['sentiment'] = 'positive'
        
        result_df = display_filterable_data_table(self.sample_data, filters_with_sentiment)
        
        # Should filter to positive sentiment only
        self.assertEqual(len(result_df), 3)
        self.assertTrue(all(result_df['sentiment'] == 'positive'))
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    def test_display_filterable_data_table_with_theme_filter(self, mock_dataframe, mock_subheader):
        """Test data table display with theme filter."""
        filters_with_theme = self.filters.copy()
        filters_with_theme['theme'] = 'Performance'
        
        result_df = display_filterable_data_table(self.sample_data, filters_with_theme)
        
        # Should filter to Performance theme only
        self.assertEqual(len(result_df), 2)
        self.assertTrue(all(result_df['theme'] == 'Performance'))
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    def test_display_filterable_data_table_multiple_filters(self, mock_dataframe, mock_subheader):
        """Test data table display with multiple filters."""
        multiple_filters = {
            'sentiment': 'positive',
            'theme': 'Performance',
            'source_channel': 'All',
            'strategic_goal': 'All'
        }
        
        result_df = display_filterable_data_table(self.sample_data, multiple_filters)
        
        # Should filter by both sentiment and theme
        self.assertEqual(len(result_df), 1)
        self.assertEqual(result_df.iloc[0]['sentiment'], 'positive')
        self.assertEqual(result_df.iloc[0]['theme'], 'Performance')
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    @patch('dashboard.components.st.info')
    def test_display_filterable_data_table_no_results(self, mock_info, mock_dataframe, mock_subheader):
        """Test data table display when filters return no results."""
        no_results_filters = {
            'sentiment': 'positive',
            'theme': 'NonexistentTheme',
            'source_channel': 'All',
            'strategic_goal': 'All'
        }
        
        result_df = display_filterable_data_table(self.sample_data, no_results_filters)
        
        # Should return empty DataFrame
        self.assertEqual(len(result_df), 0)
        
        # Should show info message
        mock_info.assert_called_once()


class TestDisplaySummaryStats(unittest.TestCase):
    """Test cases for display_summary_stats function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative'],
            'theme': ['Performance', 'Features', 'Support', 'Performance', 'UI/UX'],
            'impact_score': [5.2, 8.1, 3.7, 6.4, 4.8],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store']
        })
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.columns')
    def test_display_summary_stats_basic(self, mock_columns, mock_subheader):
        """Test basic summary statistics display."""
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock column methods
        mock_col1.write = MagicMock()
        mock_col2.write = MagicMock()
        
        result = display_summary_stats(self.sample_data)
        
        # Should return statistics
        self.assertIn('sentiment_distribution', result)
        self.assertIn('theme_distribution', result)
        self.assertIn('source_distribution', result)
        self.assertIn('impact_stats', result)
        
        # Check sentiment distribution
        sentiment_dist = result['sentiment_distribution']
        self.assertEqual(sentiment_dist['positive'], 2)
        self.assertEqual(sentiment_dist['negative'], 2)
        self.assertEqual(sentiment_dist['neutral'], 1)
        
        # Verify Streamlit calls
        mock_subheader.assert_called_once()
        mock_columns.assert_called_once()
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.columns')
    def test_display_summary_stats_empty_data(self, mock_columns, mock_subheader):
        """Test summary statistics display with empty data."""
        empty_df = pd.DataFrame()
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock column methods
        mock_col1.write = MagicMock()
        mock_col2.write = MagicMock()
        
        result = display_summary_stats(empty_df)
        
        # Should handle empty data gracefully
        self.assertIn('sentiment_distribution', result)
        self.assertIn('theme_distribution', result)
        self.assertIn('source_distribution', result)
        self.assertIn('impact_stats', result)


class TestFormatImpactScore(unittest.TestCase):
    """Test cases for format_impact_score function."""
    
    def test_format_impact_score_normal(self):
        """Test formatting normal impact scores."""
        self.assertEqual(format_impact_score(5.234), "5.23")
        self.assertEqual(format_impact_score(10.0), "10.00")
        self.assertEqual(format_impact_score(0.567), "0.57")
    
    def test_format_impact_score_high_values(self):
        """Test formatting high impact scores."""
        self.assertEqual(format_impact_score(123.456), "123.46")
        self.assertEqual(format_impact_score(1000.0), "1000.00")
    
    def test_format_impact_score_edge_cases(self):
        """Test formatting edge case impact scores."""
        self.assertEqual(format_impact_score(0), "0.00")
        self.assertEqual(format_impact_score(0.001), "0.00")
        self.assertEqual(format_impact_score(None), "0.00")
        self.assertEqual(format_impact_score(np.nan), "0.00")
    
    def test_format_impact_score_negative(self):
        """Test formatting negative impact scores."""
        self.assertEqual(format_impact_score(-5.234), "-5.23")
        self.assertEqual(format_impact_score(-0.001), "-0.00")


class TestFormatSentimentDisplay(unittest.TestCase):
    """Test cases for format_sentiment_display function."""
    
    def test_format_sentiment_display_valid(self):
        """Test formatting valid sentiment values."""
        self.assertEqual(format_sentiment_display('positive'), '😊 Positive')
        self.assertEqual(format_sentiment_display('negative'), '😞 Negative')
        self.assertEqual(format_sentiment_display('neutral'), '😐 Neutral')
    
    def test_format_sentiment_display_case_insensitive(self):
        """Test formatting sentiment values with different cases."""
        self.assertEqual(format_sentiment_display('POSITIVE'), '😊 Positive')
        self.assertEqual(format_sentiment_display('Negative'), '😞 Negative')
        self.assertEqual(format_sentiment_display('NEUTRAL'), '😐 Neutral')
    
    def test_format_sentiment_display_invalid(self):
        """Test formatting invalid sentiment values."""
        self.assertEqual(format_sentiment_display('invalid'), '❓ Unknown')
        self.assertEqual(format_sentiment_display(''), '❓ Unknown')
        self.assertEqual(format_sentiment_display(None), '❓ Unknown')
        self.assertEqual(format_sentiment_display(123), '❓ Unknown')


class TestGetUniqueFilterValues(unittest.TestCase):
    """Test cases for get_unique_filter_values function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'sentiment': ['positive', 'negative', 'neutral', 'positive', None],
            'theme': ['Performance', 'Features', 'Support', 'Performance', ''],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store']
        })
    
    def test_get_unique_filter_values_sentiment(self):
        """Test getting unique sentiment values."""
        values = get_unique_filter_values(self.sample_data, 'sentiment')
        
        # Should include 'All' option and unique values
        self.assertIn('All', values)
        self.assertIn('positive', values)
        self.assertIn('negative', values)
        self.assertIn('neutral', values)
        
        # Should not include None or empty values
        self.assertNotIn(None, values)
        self.assertNotIn('', values)
    
    def test_get_unique_filter_values_theme(self):
        """Test getting unique theme values."""
        values = get_unique_filter_values(self.sample_data, 'theme')
        
        # Should include 'All' option and unique values
        self.assertIn('All', values)
        self.assertIn('Performance', values)
        self.assertIn('Features', values)
        self.assertIn('Support', values)
        
        # Should not include empty values
        self.assertNotIn('', values)
    
    def test_get_unique_filter_values_missing_column(self):
        """Test getting unique values for missing column."""
        values = get_unique_filter_values(self.sample_data, 'nonexistent_column')
        
        # Should return just 'All' option
        self.assertEqual(values, ['All'])
    
    def test_get_unique_filter_values_empty_data(self):
        """Test getting unique values from empty DataFrame."""
        empty_df = pd.DataFrame()
        values = get_unique_filter_values(empty_df, 'sentiment')
        
        # Should return just 'All' option
        self.assertEqual(values, ['All'])
    
    def test_get_unique_filter_values_all_null(self):
        """Test getting unique values when all values are null."""
        null_data = pd.DataFrame({
            'test_column': [None, np.nan, '', None]
        })
        
        values = get_unique_filter_values(null_data, 'test_column')
        
        # Should return just 'All' option
        self.assertEqual(values, ['All'])


if __name__ == '__main__':
    unittest.main()