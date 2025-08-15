"""
Unit tests for dashboard components module.

Tests cover KPI header component, filter controls, and data table functionality.
Requirements: 6.1, 6.3, 6.5
"""

import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.components import (
    display_kpi_header,
    create_filter_controls, 
    apply_filters,
    display_filterable_data_table,
    display_summary_stats
)


class TestDashboardComponents(unittest.TestCase):
    """Test cases for dashboard components functionality."""
    
    def setUp(self):
        """Set up test data for dashboard components tests."""
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'Twitter'],
            'source': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'Twitter'],
            'feedback_text': [
                'Great app but needs better performance',
                'Love the new features!',
                'Customer wants advanced trading tools',
                'App crashes frequently',
                'Excellent customer service'
            ],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive'],
            'theme': ['Performance', 'Features', 'Trading Tools', 'Performance', 'Support'],
            'impact_score': [2.5, 1.2, 4.8, 3.1, 0.8],
            'timestamp': pd.to_datetime([
                '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05'
            ])
        })
        
        self.empty_data = pd.DataFrame()
    
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.metric')
    def test_display_kpi_header_with_data(self, mock_metric, mock_columns):
        """Test KPI header display with valid data."""
        # Mock streamlit columns
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Test KPI calculation
        result = display_kpi_header(self.sample_data)
        
        # Verify KPI values
        self.assertEqual(result['total_items'], 5)
        self.assertIn(result['avg_sentiment'], ['Positive', 'Negative', 'Neutral'])
        self.assertIn(result['top_theme'], ['Performance', 'Features', 'Trading Tools', 'Support'])
        
        # Verify streamlit calls
        mock_columns.assert_called_once_with(3)
        self.assertEqual(mock_metric.call_count, 3)
    
    @patch('dashboard.components.st.warning')
    def test_display_kpi_header_empty_data(self, mock_warning):
        """Test KPI header display with empty data."""
        result = display_kpi_header(self.empty_data)
        
        # Verify default values for empty data
        self.assertEqual(result['total_items'], 0)
        self.assertEqual(result['avg_sentiment'], 'N/A')
        self.assertEqual(result['top_theme'], 'N/A')
        
        # Verify warning is displayed
        mock_warning.assert_called_once()
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.columns')
    @patch('dashboard.components.st.selectbox')
    def test_create_filter_controls_with_data(self, mock_selectbox, mock_columns, mock_subheader):
        """Test filter controls creation with valid data."""
        # Mock streamlit components
        mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
        
        # Mock selectbox returns
        mock_selectbox.side_effect = ['All', 'All', 'All']
        
        # Test filter creation
        result = create_filter_controls(self.sample_data)
        
        # Verify filter structure
        self.assertIn('source_channel', result)
        self.assertIn('theme', result)
        self.assertIn('sentiment', result)
        
        # Verify streamlit calls
        mock_subheader.assert_called_once()
        mock_columns.assert_called_once_with(3)
        self.assertEqual(mock_selectbox.call_count, 3)
    
    @patch('dashboard.components.st.warning')
    def test_create_filter_controls_empty_data(self, mock_warning):
        """Test filter controls creation with empty data."""
        result = create_filter_controls(self.empty_data)
        
        # Verify empty result
        self.assertEqual(result, {})
        
        # Verify warning is displayed
        mock_warning.assert_called_once()
    
    def test_apply_filters_source_channel(self):
        """Test applying source channel filter."""
        filters = {'source_channel': 'Twitter'}
        result = apply_filters(self.sample_data, filters)
        
        # Verify filtering
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['source_channel'] == 'Twitter'))
    
    def test_apply_filters_sentiment(self):
        """Test applying sentiment filter."""
        filters = {'sentiment': 'positive'}
        result = apply_filters(self.sample_data, filters)
        
        # Verify filtering
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['sentiment'] == 'positive'))
    
    def test_apply_filters_multiple(self):
        """Test applying multiple filters."""
        filters = {
            'sentiment': 'negative',
            'theme': 'Performance'
        }
        result = apply_filters(self.sample_data, filters)
        
        # Verify filtering
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['sentiment'] == 'negative'))
        self.assertTrue(all(result['theme'] == 'Performance'))
    
    def test_apply_filters_all_option(self):
        """Test applying filters with 'All' option."""
        filters = {
            'source_channel': 'All',
            'sentiment': 'positive'
        }
        result = apply_filters(self.sample_data, filters)
        
        # Verify only sentiment filter is applied
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['sentiment'] == 'positive'))
    
    def test_apply_filters_no_matches(self):
        """Test applying filters with no matching records."""
        filters = {'sentiment': 'nonexistent'}
        result = apply_filters(self.sample_data, filters)
        
        # Verify empty result
        self.assertEqual(len(result), 0)
    
    @patch('dashboard.components.st.subheader')
    @patch('dashboard.components.st.dataframe')
    @patch('dashboard.components.st.caption')
    def test_display_filterable_data_table_with_data(self, mock_caption, mock_dataframe, mock_subheader):
        """Test data table display with valid data."""
        filters = {'sentiment': 'positive'}
        
        result = display_filterable_data_table(self.sample_data, filters)
        
        # Verify filtered result
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['sentiment'] == 'positive'))
        
        # Verify streamlit calls
        mock_subheader.assert_called_once()
        mock_dataframe.assert_called_once()
        mock_caption.assert_called_once()
    
    @patch('dashboard.components.st.warning')
    def test_display_filterable_data_table_no_matches(self, mock_warning):
        """Test data table display with no matching records."""
        filters = {'sentiment': 'nonexistent'}
        
        result = display_filterable_data_table(self.sample_data, filters)
        
        # Verify empty result
        self.assertEqual(len(result), 0)
        
        # Verify warning is displayed
        mock_warning.assert_called_once()
    
    def test_display_summary_stats_with_data(self):
        """Test summary statistics calculation with valid data."""
        result = display_summary_stats(self.sample_data)
        
        # Verify statistics structure
        self.assertIn('sentiment_distribution', result)
        self.assertIn('theme_distribution', result)
        self.assertIn('source_distribution', result)
        self.assertIn('impact_stats', result)
        
        # Verify sentiment distribution
        sentiment_dist = result['sentiment_distribution']
        self.assertEqual(sentiment_dist['negative'], 2)
        self.assertEqual(sentiment_dist['positive'], 2)
        self.assertEqual(sentiment_dist['neutral'], 1)
        
        # Verify impact statistics
        impact_stats = result['impact_stats']
        self.assertAlmostEqual(impact_stats['mean'], 2.48, places=2)
        self.assertEqual(impact_stats['max'], 4.8)
        self.assertEqual(impact_stats['min'], 0.8)
    
    def test_display_summary_stats_empty_data(self):
        """Test summary statistics calculation with empty data."""
        result = display_summary_stats(self.empty_data)
        
        # Verify empty result
        self.assertEqual(result, {})
    
    def test_kpi_header_sentiment_calculation(self):
        """Test sentiment calculation logic in KPI header."""
        # Create test data with known sentiment distribution
        test_data = pd.DataFrame({
            'sentiment': ['positive', 'positive', 'negative'],
            'impact_score': [1.0, 1.0, 1.0]
        })
        
        with patch('dashboard.components.st.columns') as mock_columns, patch('dashboard.components.st.metric'):
            mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
            result = display_kpi_header(test_data)
        
        # Verify sentiment calculation
        self.assertIn('avg_sentiment_score', result)
        self.assertIsInstance(result['avg_sentiment_score'], (int, float))
    
    def test_filter_controls_column_handling(self):
        """Test filter controls with different column names."""
        # Test data with 'source' instead of 'source_channel'
        test_data = pd.DataFrame({
            'source': ['Twitter', 'iOS'],
            'theme': ['Performance', 'Features'],
            'sentiment': ['positive', 'negative']
        })
        
        with patch('dashboard.components.st.subheader'), \
             patch('dashboard.components.st.columns') as mock_columns, \
             patch('dashboard.components.st.selectbox') as mock_selectbox:
            mock_col1, mock_col2, mock_col3 = MagicMock(), MagicMock(), MagicMock()
            mock_columns.return_value = [mock_col1, mock_col2, mock_col3]
            mock_selectbox.side_effect = ['All', 'All', 'All']
            result = create_filter_controls(test_data)
        
        # Verify 'source' is used when 'source_channel' is not available
        self.assertIn('source', result)


if __name__ == '__main__':
    unittest.main()