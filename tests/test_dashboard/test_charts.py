"""
Unit tests for dashboard charts module.

Tests cover chart creation, data visualization, and interactive chart
functionality for the dashboard.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dashboard.charts import (
    create_theme_impact_chart,
    create_sentiment_distribution_chart,
    create_source_channel_chart,
    create_time_trend_chart,
    create_strategic_goal_chart,
    create_comprehensive_dashboard_charts,
    prepare_chart_data,
    format_chart_colors
)


class TestCreateThemeImpactChart(unittest.TestCase):
    """Test cases for create_theme_impact_chart function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'theme': ['Performance', 'Features', 'Support', 'Performance', 'UI/UX', 'Features'],
            'impact_score': [8.5, 6.2, 4.8, 7.1, 5.3, 5.9],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'positive']
        })
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_theme_impact_chart_basic(self, mock_plotly_chart, mock_px_bar):
        """Test basic theme impact chart creation."""
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_bar.return_value = mock_fig
        
        result = create_theme_impact_chart(self.sample_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertIn('chart_type', result)
        self.assertEqual(result['chart_type'], 'theme_impact')
        
        # Verify plotly calls
        mock_px_bar.assert_called_once()
        mock_plotly_chart.assert_called_once_with(mock_fig, use_container_width=True)
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_theme_impact_chart_empty_data(self, mock_plotly_chart, mock_px_bar):
        """Test theme impact chart creation with empty data."""
        empty_df = pd.DataFrame()
        
        result = create_theme_impact_chart(empty_df)
        
        # Should handle empty data gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        
        # Should not call plotly functions
        mock_px_bar.assert_not_called()
        mock_plotly_chart.assert_not_called()
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_theme_impact_chart_missing_columns(self, mock_plotly_chart, mock_px_bar):
        """Test theme impact chart creation with missing columns."""
        incomplete_data = pd.DataFrame({
            'theme': ['Performance', 'Features'],
            'other_column': [1, 2]
            # Missing impact_score
        })
        
        result = create_theme_impact_chart(incomplete_data)
        
        # Should handle missing columns gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_theme_impact_chart_single_theme(self, mock_plotly_chart, mock_px_bar):
        """Test theme impact chart creation with single theme."""
        single_theme_data = pd.DataFrame({
            'theme': ['Performance'],
            'impact_score': [8.5],
            'sentiment': ['negative']
        })
        
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_bar.return_value = mock_fig
        
        result = create_theme_impact_chart(single_theme_data)
        
        # Should handle single theme
        self.assertTrue(result['success'])
        mock_px_bar.assert_called_once()


class TestCreateSentimentDistributionChart(unittest.TestCase):
    """Test cases for create_sentiment_distribution_chart function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative', 'positive'],
            'impact_score': [6.2, 8.5, 4.8, 5.9, 7.1, 5.3],
            'theme': ['Features', 'Performance', 'Support', 'Features', 'Performance', 'UI/UX']
        })
    
    @patch('dashboard.charts.px.pie')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_sentiment_distribution_chart_basic(self, mock_plotly_chart, mock_px_pie):
        """Test basic sentiment distribution chart creation."""
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_pie.return_value = mock_fig
        
        result = create_sentiment_distribution_chart(self.sample_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertEqual(result['chart_type'], 'sentiment_distribution')
        
        # Verify plotly calls
        mock_px_pie.assert_called_once()
        mock_plotly_chart.assert_called_once_with(mock_fig, use_container_width=True)
    
    @patch('dashboard.charts.px.pie')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_sentiment_distribution_chart_empty_data(self, mock_plotly_chart, mock_px_pie):
        """Test sentiment distribution chart creation with empty data."""
        empty_df = pd.DataFrame()
        
        result = create_sentiment_distribution_chart(empty_df)
        
        # Should handle empty data gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('dashboard.charts.px.pie')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_sentiment_distribution_chart_single_sentiment(self, mock_plotly_chart, mock_px_pie):
        """Test sentiment distribution chart with single sentiment type."""
        single_sentiment_data = pd.DataFrame({
            'sentiment': ['positive', 'positive', 'positive'],
            'impact_score': [6.2, 5.9, 5.3]
        })
        
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_pie.return_value = mock_fig
        
        result = create_sentiment_distribution_chart(single_sentiment_data)
        
        # Should handle single sentiment type
        self.assertTrue(result['success'])
        mock_px_pie.assert_called_once()


class TestCreateSourceChannelChart(unittest.TestCase):
    """Test cases for create_source_channel_chart function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store', 'Twitter'],
            'impact_score': [6.2, 8.5, 4.8, 5.9, 7.1, 5.3],
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative', 'positive']
        })
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_source_channel_chart_basic(self, mock_plotly_chart, mock_px_bar):
        """Test basic source channel chart creation."""
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_bar.return_value = mock_fig
        
        result = create_source_channel_chart(self.sample_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertEqual(result['chart_type'], 'source_channel')
        
        # Verify plotly calls
        mock_px_bar.assert_called_once()
        mock_plotly_chart.assert_called_once_with(mock_fig, use_container_width=True)
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_source_channel_chart_empty_data(self, mock_plotly_chart, mock_px_bar):
        """Test source channel chart creation with empty data."""
        empty_df = pd.DataFrame()
        
        result = create_source_channel_chart(empty_df)
        
        # Should handle empty data gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCreateTimeTrendChart(unittest.TestCase):
    """Test cases for create_time_trend_chart function."""
    
    def setUp(self):
        """Set up test data with timestamps."""
        from datetime import datetime, timedelta
        
        self.sample_data = pd.DataFrame({
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(6)
            ],
            'impact_score': [6.2, 8.5, 4.8, 5.9, 7.1, 5.3],
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative', 'positive']
        })
    
    @patch('dashboard.charts.px.line')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_time_trend_chart_basic(self, mock_plotly_chart, mock_px_line):
        """Test basic time trend chart creation."""
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_line.return_value = mock_fig
        
        result = create_time_trend_chart(self.sample_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertEqual(result['chart_type'], 'time_trend')
        
        # Verify plotly calls
        mock_px_line.assert_called_once()
        mock_plotly_chart.assert_called_once_with(mock_fig, use_container_width=True)
    
    @patch('dashboard.charts.px.line')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_time_trend_chart_missing_timestamp(self, mock_plotly_chart, mock_px_line):
        """Test time trend chart creation with missing timestamp column."""
        data_without_timestamp = pd.DataFrame({
            'impact_score': [6.2, 8.5, 4.8],
            'sentiment': ['positive', 'negative', 'neutral']
        })
        
        result = create_time_trend_chart(data_without_timestamp)
        
        # Should handle missing timestamp gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCreateStrategicGoalChart(unittest.TestCase):
    """Test cases for create_strategic_goal_chart function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'strategic_goal': ['Growth', 'Trust&Safety', 'CX Efficiency', 'Growth', 'Trust&Safety', 'Growth'],
            'impact_score': [6.2, 8.5, 4.8, 5.9, 7.1, 5.3],
            'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative', 'positive']
        })
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_strategic_goal_chart_basic(self, mock_plotly_chart, mock_px_bar):
        """Test basic strategic goal chart creation."""
        # Mock plotly figure
        mock_fig = MagicMock()
        mock_px_bar.return_value = mock_fig
        
        result = create_strategic_goal_chart(self.sample_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertEqual(result['chart_type'], 'strategic_goal')
        
        # Verify plotly calls
        mock_px_bar.assert_called_once()
        mock_plotly_chart.assert_called_once_with(mock_fig, use_container_width=True)
    
    @patch('dashboard.charts.px.bar')
    @patch('dashboard.charts.st.plotly_chart')
    def test_create_strategic_goal_chart_empty_data(self, mock_plotly_chart, mock_px_bar):
        """Test strategic goal chart creation with empty data."""
        empty_df = pd.DataFrame()
        
        result = create_strategic_goal_chart(empty_df)
        
        # Should handle empty data gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)


class TestCreateComprehensiveDashboardCharts(unittest.TestCase):
    """Test cases for create_comprehensive_dashboard_charts function."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        from datetime import datetime, timedelta
        
        self.comprehensive_data = pd.DataFrame({
            'theme': ['Performance', 'Features', 'Support', 'Performance', 'UI/UX', 'Features'],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'positive'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store', 'Twitter'],
            'strategic_goal': ['Trust&Safety', 'Growth', 'CX Efficiency', 'Trust&Safety', 'Growth', 'Growth'],
            'impact_score': [8.5, 6.2, 4.8, 7.1, 5.3, 5.9],
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(6)
            ]
        })
    
    @patch('dashboard.charts.create_theme_impact_chart')
    @patch('dashboard.charts.create_sentiment_distribution_chart')
    @patch('dashboard.charts.create_source_channel_chart')
    @patch('dashboard.charts.create_time_trend_chart')
    @patch('dashboard.charts.create_strategic_goal_chart')
    @patch('dashboard.charts.st.subheader')
    @patch('dashboard.charts.st.columns')
    def test_create_comprehensive_dashboard_charts_success(self, mock_columns, mock_subheader,
                                                         mock_strategic_chart, mock_time_chart,
                                                         mock_source_chart, mock_sentiment_chart,
                                                         mock_theme_chart):
        """Test comprehensive dashboard charts creation."""
        # Mock successful chart creation
        success_result = {'success': True, 'chart_type': 'test'}
        mock_theme_chart.return_value = success_result
        mock_sentiment_chart.return_value = success_result
        mock_source_chart.return_value = success_result
        mock_time_chart.return_value = success_result
        mock_strategic_chart.return_value = success_result
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        result = create_comprehensive_dashboard_charts(self.comprehensive_data)
        
        # Should return success status
        self.assertTrue(result['success'])
        self.assertIn('charts_created', result)
        self.assertEqual(result['charts_created'], 5)
        
        # Verify all chart functions called
        mock_theme_chart.assert_called_once()
        mock_sentiment_chart.assert_called_once()
        mock_source_chart.assert_called_once()
        mock_time_chart.assert_called_once()
        mock_strategic_chart.assert_called_once()
    
    @patch('dashboard.charts.create_theme_impact_chart')
    @patch('dashboard.charts.create_sentiment_distribution_chart')
    @patch('dashboard.charts.create_source_channel_chart')
    @patch('dashboard.charts.create_time_trend_chart')
    @patch('dashboard.charts.create_strategic_goal_chart')
    @patch('dashboard.charts.st.subheader')
    @patch('dashboard.charts.st.columns')
    def test_create_comprehensive_dashboard_charts_partial_failure(self, mock_columns, mock_subheader,
                                                                 mock_strategic_chart, mock_time_chart,
                                                                 mock_source_chart, mock_sentiment_chart,
                                                                 mock_theme_chart):
        """Test comprehensive dashboard charts with some chart failures."""
        # Mock mixed success/failure results
        success_result = {'success': True, 'chart_type': 'test'}
        failure_result = {'success': False, 'error': 'Test error'}
        
        mock_theme_chart.return_value = success_result
        mock_sentiment_chart.return_value = failure_result
        mock_source_chart.return_value = success_result
        mock_time_chart.return_value = failure_result
        mock_strategic_chart.return_value = success_result
        
        # Mock columns
        mock_col1, mock_col2 = MagicMock(), MagicMock()
        mock_columns.return_value = [mock_col1, mock_col2]
        
        result = create_comprehensive_dashboard_charts(self.comprehensive_data)
        
        # Should return partial success
        self.assertTrue(result['success'])
        self.assertEqual(result['charts_created'], 3)  # 3 successful, 2 failed
        self.assertEqual(result['charts_failed'], 2)
    
    @patch('dashboard.charts.st.error')
    def test_create_comprehensive_dashboard_charts_empty_data(self, mock_error):
        """Test comprehensive dashboard charts with empty data."""
        empty_df = pd.DataFrame()
        
        result = create_comprehensive_dashboard_charts(empty_df)
        
        # Should handle empty data gracefully
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        mock_error.assert_called_once()


class TestPrepareChartData(unittest.TestCase):
    """Test cases for prepare_chart_data function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'theme': ['Performance', 'Features', 'Support', 'Performance', 'UI/UX'],
            'impact_score': [8.5, 6.2, 4.8, 7.1, 5.3],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive']
        })
    
    def test_prepare_chart_data_theme_aggregation(self):
        """Test chart data preparation for theme aggregation."""
        chart_data = prepare_chart_data(self.sample_data, group_by='theme', agg_column='impact_score')
        
        # Should group by theme and aggregate impact scores
        self.assertIn('Performance', chart_data.index)
        self.assertIn('Features', chart_data.index)
        
        # Check aggregated values
        performance_total = chart_data.loc['Performance']
        self.assertAlmostEqual(performance_total, 15.6, places=1)  # 8.5 + 7.1
    
    def test_prepare_chart_data_sentiment_aggregation(self):
        """Test chart data preparation for sentiment aggregation."""
        chart_data = prepare_chart_data(self.sample_data, group_by='sentiment', agg_column='impact_score')
        
        # Should group by sentiment
        self.assertIn('negative', chart_data.index)
        self.assertIn('positive', chart_data.index)
        self.assertIn('neutral', chart_data.index)
    
    def test_prepare_chart_data_count_aggregation(self):
        """Test chart data preparation with count aggregation."""
        chart_data = prepare_chart_data(self.sample_data, group_by='theme', agg_function='count')
        
        # Should count occurrences
        performance_count = chart_data.loc['Performance']
        self.assertEqual(performance_count, 2)  # 2 Performance entries
    
    def test_prepare_chart_data_empty_data(self):
        """Test chart data preparation with empty data."""
        empty_df = pd.DataFrame()
        
        chart_data = prepare_chart_data(empty_df, group_by='theme', agg_column='impact_score')
        
        # Should return empty Series
        self.assertTrue(chart_data.empty)
    
    def test_prepare_chart_data_missing_columns(self):
        """Test chart data preparation with missing columns."""
        incomplete_data = pd.DataFrame({
            'theme': ['Performance', 'Features'],
            'other_column': [1, 2]
            # Missing impact_score
        })
        
        chart_data = prepare_chart_data(incomplete_data, group_by='theme', agg_column='impact_score')
        
        # Should handle missing columns gracefully
        self.assertTrue(chart_data.empty)


class TestFormatChartColors(unittest.TestCase):
    """Test cases for format_chart_colors function."""
    
    def test_format_chart_colors_sentiment(self):
        """Test chart color formatting for sentiment data."""
        colors = format_chart_colors('sentiment')
        
        # Should return sentiment-specific colors
        self.assertIsInstance(colors, dict)
        self.assertIn('positive', colors)
        self.assertIn('negative', colors)
        self.assertIn('neutral', colors)
        
        # Check color values
        self.assertEqual(colors['positive'], '#2E8B57')  # Green
        self.assertEqual(colors['negative'], '#DC143C')  # Red
        self.assertEqual(colors['neutral'], '#4682B4')   # Blue
    
    def test_format_chart_colors_theme(self):
        """Test chart color formatting for theme data."""
        colors = format_chart_colors('theme')
        
        # Should return theme-specific colors
        self.assertIsInstance(colors, list)
        self.assertGreater(len(colors), 0)
        
        # Should contain valid color codes
        for color in colors:
            self.assertTrue(color.startswith('#'))
            self.assertEqual(len(color), 7)  # #RRGGBB format
    
    def test_format_chart_colors_default(self):
        """Test chart color formatting for default/unknown type."""
        colors = format_chart_colors('unknown_type')
        
        # Should return default color scheme
        self.assertIsInstance(colors, list)
        self.assertGreater(len(colors), 0)
    
    def test_format_chart_colors_source_channel(self):
        """Test chart color formatting for source channel data."""
        colors = format_chart_colors('source_channel')
        
        # Should return source-specific colors
        self.assertIsInstance(colors, list)
        self.assertGreater(len(colors), 0)


if __name__ == '__main__':
    unittest.main()