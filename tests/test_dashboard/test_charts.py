"""
Unit tests for dashboard charts module.

Tests cover theme impact charts, sentiment distribution, time trends, and source comparisons.
Requirements: 6.2
"""

import unittest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import patch, MagicMock
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.charts import (
    create_theme_impact_chart,
    create_sentiment_distribution_chart,
    create_time_trend_chart,
    create_source_impact_chart,
    display_chart_with_error_handling,
    create_comprehensive_dashboard_charts
)


class TestDashboardCharts(unittest.TestCase):
    """Test cases for dashboard charts functionality."""
    
    def setUp(self):
        """Set up test data for chart tests."""
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'Twitter', 'iOS App Store'],
            'source': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'Twitter', 'iOS App Store'],
            'feedback_text': [
                'Great app but needs better performance',
                'Love the new features!',
                'Customer wants advanced trading tools',
                'App crashes frequently',
                'Excellent customer service',
                'Good overall experience'
            ],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'positive'],
            'theme': ['Performance', 'Features', 'Trading Tools', 'Performance', 'Support', 'Features'],
            'impact_score': [2.5, 1.2, 4.8, 3.1, 0.8, 1.5],
            'timestamp': pd.to_datetime([
                '2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05', '2024-01-06'
            ])
        })
        
        self.empty_data = pd.DataFrame()
        
        self.minimal_data = pd.DataFrame({
            'theme': ['Performance'],
            'impact_score': [1.0]
        })
    
    def test_create_theme_impact_chart_with_data(self):
        """Test theme impact chart creation with valid data."""
        fig = create_theme_impact_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify chart has data
        self.assertTrue(len(fig.data) > 0)
        
        # Verify chart type is bar
        self.assertEqual(fig.data[0].type, 'bar')
        
        # Verify orientation is horizontal
        self.assertEqual(fig.data[0].orientation, 'h')
    
    def test_create_theme_impact_chart_empty_data(self):
        """Test theme impact chart creation with empty data."""
        fig = create_theme_impact_chart(self.empty_data)
        
        # Should return None for empty data
        self.assertIsNone(fig)
    
    def test_create_theme_impact_chart_missing_columns(self):
        """Test theme impact chart creation with missing required columns."""
        incomplete_data = pd.DataFrame({
            'theme': ['Performance', 'Features'],
            # Missing impact_score column
        })
        
        fig = create_theme_impact_chart(incomplete_data)
        
        # Should return None for missing columns
        self.assertIsNone(fig)
    
    def test_create_sentiment_distribution_chart_with_data(self):
        """Test sentiment distribution chart creation with valid data."""
        fig = create_sentiment_distribution_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify chart has data
        self.assertTrue(len(fig.data) > 0)
        
        # Verify chart type is pie
        self.assertEqual(fig.data[0].type, 'pie')
        
        # Verify all sentiments are represented
        labels = fig.data[0].labels
        self.assertIn('positive', labels)
        self.assertIn('negative', labels)
    
    def test_create_sentiment_distribution_chart_empty_data(self):
        """Test sentiment distribution chart creation with empty data."""
        fig = create_sentiment_distribution_chart(self.empty_data)
        
        # Should return None for empty data
        self.assertIsNone(fig)
    
    def test_create_sentiment_distribution_chart_missing_column(self):
        """Test sentiment distribution chart creation with missing sentiment column."""
        incomplete_data = pd.DataFrame({
            'theme': ['Performance', 'Features'],
            'impact_score': [1.0, 2.0]
            # Missing sentiment column
        })
        
        fig = create_sentiment_distribution_chart(incomplete_data)
        
        # Should return None for missing column
        self.assertIsNone(fig)
    
    def test_create_time_trend_chart_with_data(self):
        """Test time trend chart creation with valid data."""
        fig = create_time_trend_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify chart has data
        self.assertTrue(len(fig.data) > 0)
        
        # Should have multiple traces for different sentiments
        self.assertGreaterEqual(len(fig.data), 3)  # At least 3 sentiment traces
    
    def test_create_time_trend_chart_empty_data(self):
        """Test time trend chart creation with empty data."""
        fig = create_time_trend_chart(self.empty_data)
        
        # Should return None for empty data
        self.assertIsNone(fig)
    
    def test_create_time_trend_chart_missing_timestamp(self):
        """Test time trend chart creation with missing timestamp column."""
        incomplete_data = pd.DataFrame({
            'sentiment': ['positive', 'negative'],
            'theme': ['Performance', 'Features']
            # Missing timestamp column
        })
        
        fig = create_time_trend_chart(incomplete_data)
        
        # Should return None for missing timestamp
        self.assertIsNone(fig)
    
    def test_create_time_trend_chart_invalid_timestamps(self):
        """Test time trend chart creation with invalid timestamp data."""
        invalid_timestamp_data = pd.DataFrame({
            'timestamp': ['invalid_date', 'another_invalid'],
            'sentiment': ['positive', 'negative']
        })
        
        fig = create_time_trend_chart(invalid_timestamp_data)
        
        # Should return None for invalid timestamps
        self.assertIsNone(fig)
    
    def test_create_source_impact_chart_with_source_channel(self):
        """Test source impact chart creation with source_channel column."""
        fig = create_source_impact_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify chart has data
        self.assertTrue(len(fig.data) > 0)
        
        # Verify chart type is bar
        self.assertEqual(fig.data[0].type, 'bar')
        
        # Verify orientation is horizontal
        self.assertEqual(fig.data[0].orientation, 'h')
    
    def test_create_source_impact_chart_with_source_column(self):
        """Test source impact chart creation with source column (fallback)."""
        # Remove source_channel column to test fallback
        data_with_source = self.sample_data.drop(columns=['source_channel'])
        
        fig = create_source_impact_chart(data_with_source)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify chart has data
        self.assertTrue(len(fig.data) > 0)
    
    def test_create_source_impact_chart_empty_data(self):
        """Test source impact chart creation with empty data."""
        fig = create_source_impact_chart(self.empty_data)
        
        # Should return None for empty data
        self.assertIsNone(fig)
    
    def test_create_source_impact_chart_missing_columns(self):
        """Test source impact chart creation with missing required columns."""
        incomplete_data = pd.DataFrame({
            'theme': ['Performance', 'Features']
            # Missing source and impact_score columns
        })
        
        fig = create_source_impact_chart(incomplete_data)
        
        # Should return None for missing columns
        self.assertIsNone(fig)
    
    @patch('dashboard.charts.st.plotly_chart')
    def test_display_chart_with_error_handling_success(self, mock_plotly_chart):
        """Test successful chart display with error handling."""
        # Mock chart function that returns a valid figure
        def mock_chart_func(df):
            return go.Figure()
        
        result = display_chart_with_error_handling(
            mock_chart_func, self.sample_data, "Test Chart"
        )
        
        # Verify success
        self.assertTrue(result)
        
        # Verify plotly_chart was called
        mock_plotly_chart.assert_called_once()
    
    @patch('dashboard.charts.st.warning')
    def test_display_chart_with_error_handling_none_result(self, mock_warning):
        """Test chart display when chart function returns None."""
        # Mock chart function that returns None
        def mock_chart_func(df):
            return None
        
        result = display_chart_with_error_handling(
            mock_chart_func, self.sample_data, "Test Chart"
        )
        
        # Verify failure
        self.assertFalse(result)
        
        # Verify warning was displayed
        mock_warning.assert_called_once()
    
    @patch('dashboard.charts.st.error')
    def test_display_chart_with_error_handling_exception(self, mock_error):
        """Test chart display when chart function raises exception."""
        # Mock chart function that raises exception
        def mock_chart_func(df):
            raise ValueError("Test error")
        
        result = display_chart_with_error_handling(
            mock_chart_func, self.sample_data, "Test Chart"
        )
        
        # Verify failure
        self.assertFalse(result)
        
        # Verify error was displayed
        mock_error.assert_called_once()
    
    @patch('dashboard.charts.st.columns')
    @patch('dashboard.charts.st.subheader')
    @patch('dashboard.charts.display_chart_with_error_handling')
    def test_create_comprehensive_dashboard_charts_with_data(self, mock_display, mock_subheader, mock_columns):
        """Test comprehensive dashboard charts creation with valid data."""
        # Mock streamlit columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        # Mock display function to return success
        mock_display.return_value = True
        
        result = create_comprehensive_dashboard_charts(self.sample_data)
        
        # Verify all charts were attempted
        self.assertIn('theme_impact', result)
        self.assertIn('sentiment_distribution', result)
        self.assertIn('time_trends', result)
        self.assertIn('source_impact', result)
        
        # Verify streamlit components were called
        mock_columns.assert_called_once_with(2)
        self.assertEqual(mock_subheader.call_count, 4)
        self.assertEqual(mock_display.call_count, 4)
    
    @patch('dashboard.charts.st.warning')
    def test_create_comprehensive_dashboard_charts_empty_data(self, mock_warning):
        """Test comprehensive dashboard charts creation with empty data."""
        result = create_comprehensive_dashboard_charts(self.empty_data)
        
        # Verify empty result
        self.assertEqual(result, {})
        
        # Verify warning was displayed
        mock_warning.assert_called_once()
    
    def test_theme_impact_chart_data_aggregation(self):
        """Test that theme impact chart properly aggregates data by theme."""
        fig = create_theme_impact_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Check that data is aggregated (should have fewer bars than original records)
        unique_themes = self.sample_data['theme'].nunique()
        self.assertEqual(len(fig.data[0].y), unique_themes)
    
    def test_sentiment_distribution_chart_percentages(self):
        """Test that sentiment distribution chart shows proper percentages."""
        fig = create_sentiment_distribution_chart(self.sample_data)
        
        # Verify chart was created
        self.assertIsInstance(fig, go.Figure)
        
        # Verify values sum to total count
        total_values = sum(fig.data[0].values)
        self.assertEqual(total_values, len(self.sample_data))
    
    def test_chart_error_handling_robustness(self):
        """Test that all chart functions handle various error conditions gracefully."""
        # Test with None input
        self.assertIsNone(create_theme_impact_chart(None))
        self.assertIsNone(create_sentiment_distribution_chart(None))
        self.assertIsNone(create_time_trend_chart(None))
        self.assertIsNone(create_source_impact_chart(None))


if __name__ == '__main__':
    unittest.main()