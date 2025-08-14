"""
Unit tests for content_builder module.

Tests cover theme grouping, pain point identification, praised feature detection,
strategic insights extraction, and executive summary generation.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from reporting.content_builder import (
    group_by_theme,
    identify_top_pain_points,
    identify_praised_features,
    extract_strategic_insights,
    generate_executive_summary,
    build_report_content
)


class TestContentBuilder(unittest.TestCase):
    """Test cases for content builder functions."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create sample feedback data
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store', 'Twitter'],
            'feedback_text': [
                'App crashes frequently during trading',
                'Love the new interface design',
                'Customer wants advanced order types',
                'Slow loading times are frustrating',
                'Great customer support experience',
                'Need better mobile notifications'
            ],
            'theme': ['Performance/Outages', 'UI/UX', 'Trading/Execution & Fees', 'Performance/Outages', 'Support Experience', 'Mobile Features'],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'negative'],
            'strategic_goal': ['Trust&Safety', 'Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth'],
            'severity': [2.0, 1.0, 1.5, 2.5, 1.0, 1.8],
            'impact_score': [15.5, 8.2, 12.3, 18.7, 6.1, 14.2],
            'source_weight': [2.5, 1.8, 3.2, 2.1, 2.5, 1.8],
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(6)
            ]
        })
        
        # Empty DataFrame for edge case testing
        self.empty_data = pd.DataFrame()
    
    def test_group_by_theme(self):
        """Test theme grouping and aggregation."""
        result = group_by_theme(self.sample_data)
        
        # Check that result is not empty
        self.assertFalse(result.empty)
        
        # Check expected columns
        expected_columns = ['theme', 'total_impact', 'avg_impact', 'feedback_count', 'negative_count', 'unique_customers']
        self.assertEqual(list(result.columns), expected_columns)
        
        # Check that themes are grouped correctly
        theme_counts = result.set_index('theme')['feedback_count'].to_dict()
        self.assertEqual(theme_counts['Performance/Outages'], 2)  # Two performance issues
        
        # Check sorting (should be by total_impact descending)
        self.assertTrue(result['total_impact'].iloc[0] >= result['total_impact'].iloc[1])
    
    def test_group_by_theme_empty_data(self):
        """Test theme grouping with empty DataFrame."""
        result = group_by_theme(self.empty_data)
        self.assertTrue(result.empty)
    
    def test_identify_top_pain_points(self):
        """Test identification of top pain points."""
        result = identify_top_pain_points(self.sample_data, top_n=2)
        
        # Should return list of dictionaries
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)  # Should not exceed top_n
        
        # Check that all returned items have negative sentiment
        for pain_point in result:
            self.assertIn('theme', pain_point)
            self.assertIn('impact_score', pain_point)
            self.assertIn('feedback_text', pain_point)
            self.assertIn('source_channel', pain_point)
        
        # Check sorting (highest impact first)
        if len(result) > 1:
            self.assertGreaterEqual(result[0]['impact_score'], result[1]['impact_score'])
    
    def test_identify_top_pain_points_no_negative(self):
        """Test pain point identification with no negative feedback."""
        positive_data = self.sample_data.copy()
        positive_data['sentiment'] = 'positive'
        
        result = identify_top_pain_points(positive_data)
        self.assertEqual(len(result), 0)
    
    def test_identify_praised_features(self):
        """Test identification of praised features."""
        result = identify_praised_features(self.sample_data, top_n=2)
        
        # Should return list of dictionaries
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)  # Should not exceed top_n
        
        # Check structure of returned items
        for praised_feature in result:
            self.assertIn('theme', praised_feature)
            self.assertIn('impact_score', praised_feature)
            self.assertIn('feedback_text', praised_feature)
            self.assertIn('source_channel', praised_feature)
        
        # Check sorting (highest impact first)
        if len(result) > 1:
            self.assertGreaterEqual(result[0]['impact_score'], result[1]['impact_score'])
    
    def test_identify_praised_features_no_positive(self):
        """Test praised feature identification with no positive feedback."""
        negative_data = self.sample_data.copy()
        negative_data['sentiment'] = 'negative'
        
        result = identify_praised_features(negative_data)
        self.assertEqual(len(result), 0)
    
    def test_extract_strategic_insights(self):
        """Test strategic insights extraction."""
        result = extract_strategic_insights(self.sample_data)
        
        # Should return dictionary
        self.assertIsInstance(result, dict)
        
        # Check that strategic goals are present
        expected_goals = ['Trust&Safety', 'Growth', 'CX Efficiency']
        for goal in expected_goals:
            if goal in result:
                insight = result[goal]
                self.assertIn('total_impact', insight)
                self.assertIn('avg_impact', insight)
                self.assertIn('feedback_count', insight)
                self.assertIn('sentiment_breakdown', insight)
                self.assertIn('top_feedback', insight)
    
    def test_extract_strategic_insights_empty_data(self):
        """Test strategic insights with empty data."""
        result = extract_strategic_insights(self.empty_data)
        self.assertEqual(result, {})
    
    def test_generate_executive_summary(self):
        """Test executive summary generation."""
        result = generate_executive_summary(self.sample_data)
        
        # Should return dictionary with expected keys
        self.assertIsInstance(result, dict)
        expected_keys = [
            'total_feedback_items', 'unique_customers', 'sentiment_distribution',
            'sentiment_percentages', 'impact_metrics', 'top_theme', 'source_distribution'
        ]
        
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check specific values
        self.assertEqual(result['total_feedback_items'], 6)
        self.assertEqual(result['unique_customers'], 6)
        
        # Check sentiment distribution
        sentiment_dist = result['sentiment_distribution']
        self.assertEqual(sentiment_dist['negative'], 3)
        self.assertEqual(sentiment_dist['positive'], 2)
        self.assertEqual(sentiment_dist['neutral'], 1)
        
        # Check impact metrics structure
        impact_metrics = result['impact_metrics']
        self.assertIn('total_impact', impact_metrics)
        self.assertIn('average_impact', impact_metrics)
        self.assertIn('maximum_impact', impact_metrics)
    
    def test_generate_executive_summary_empty_data(self):
        """Test executive summary with empty data."""
        result = generate_executive_summary(self.empty_data)
        self.assertEqual(result, {})
    
    def test_build_report_content(self):
        """Test complete report content building."""
        result = build_report_content(self.sample_data, top_n=2)
        
        # Should return dictionary with all sections
        self.assertIsInstance(result, dict)
        expected_sections = [
            'executive_summary', 'theme_analysis', 'top_pain_points',
            'praised_features', 'strategic_insights', 'metadata'
        ]
        
        for section in expected_sections:
            self.assertIn(section, result)
        
        # Check metadata
        metadata = result['metadata']
        self.assertIn('generated_at', metadata)
        self.assertIn('total_records_processed', metadata)
        self.assertEqual(metadata['total_records_processed'], 6)
        
        # Check that sections contain expected data types
        self.assertIsInstance(result['executive_summary'], dict)
        self.assertIsInstance(result['theme_analysis'], list)
        self.assertIsInstance(result['top_pain_points'], list)
        self.assertIsInstance(result['praised_features'], list)
        self.assertIsInstance(result['strategic_insights'], dict)
    
    def test_build_report_content_empty_data(self):
        """Test report content building with empty data."""
        result = build_report_content(self.empty_data)
        self.assertEqual(result, {})
    
    def test_feedback_text_truncation(self):
        """Test that long feedback text is properly truncated."""
        long_text_data = self.sample_data.copy()
        long_text_data.loc[0, 'feedback_text'] = 'A' * 300  # Very long text
        
        pain_points = identify_top_pain_points(long_text_data, top_n=1)
        if pain_points:
            # Should be truncated to ~200 chars + '...'
            self.assertLessEqual(len(pain_points[0]['feedback_text']), 210)
            if len(pain_points[0]['feedback_text']) > 200:
                self.assertTrue(pain_points[0]['feedback_text'].endswith('...'))
    
    def test_missing_columns_handling(self):
        """Test handling of missing columns in DataFrame."""
        minimal_data = pd.DataFrame({
            'theme': ['Theme1', 'Theme2'],
            'sentiment': ['positive', 'negative'],
            'impact_score': [5.0, 10.0]
        })
        
        # Should not crash with missing columns
        result = generate_executive_summary(minimal_data)
        self.assertIsInstance(result, dict)
        
        # Should handle missing customer_id gracefully
        self.assertEqual(result['unique_customers'], 0)


if __name__ == '__main__':
    unittest.main()