"""
Unit tests for content_builder module.

Tests cover content aggregation, insight generation, and data analysis
functionality for report generation.
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from reporting.content_builder import (
    calculate_executive_summary,
    identify_top_pain_points,
    identify_praised_features,
    analyze_theme_impact,
    generate_strategic_insights,
    build_comprehensive_content
)


class TestCalculateExecutiveSummary(unittest.TestCase):
    """Test cases for calculate_executive_summary function."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play'],
            'feedback_text': ['Great app', 'Love it', 'Customer satisfied', 'Good platform'],
            'sentiment': ['positive', 'positive', 'positive', 'negative'],
            'theme': ['Performance', 'Features', 'Support', 'Performance'],
            'impact_score': [5.2, 3.8, 8.1, 6.5],
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(4)
            ]
        })
    
    def test_executive_summary_calculation(self):
        """Test executive summary calculation with valid data."""
        summary = calculate_executive_summary(self.sample_data)
        
        # Check required fields
        self.assertIn('total_feedback_items', summary)
        self.assertIn('average_sentiment_score', summary)
        self.assertIn('top_theme_by_impact', summary)
        self.assertIn('total_impact_score', summary)
        self.assertIn('sentiment_distribution', summary)
        
        # Check values
        self.assertEqual(summary['total_feedback_items'], 4)
        self.assertEqual(summary['top_theme_by_impact'], 'Support')  # Highest impact score
        self.assertAlmostEqual(summary['total_impact_score'], 23.6, places=1)
    
    def test_executive_summary_empty_data(self):
        """Test executive summary with empty DataFrame."""
        empty_df = pd.DataFrame()
        summary = calculate_executive_summary(empty_df)
        
        # Should handle empty data gracefully
        self.assertEqual(summary['total_feedback_items'], 0)
        self.assertEqual(summary['average_sentiment_score'], 0.0)
        self.assertEqual(summary['top_theme_by_impact'], 'No data available')
        self.assertEqual(summary['total_impact_score'], 0.0)
    
    def test_executive_summary_single_item(self):
        """Test executive summary with single data item."""
        single_item = self.sample_data.iloc[:1].copy()
        summary = calculate_executive_summary(single_item)
        
        self.assertEqual(summary['total_feedback_items'], 1)
        self.assertEqual(summary['top_theme_by_impact'], 'Performance')
        self.assertAlmostEqual(summary['total_impact_score'], 5.2, places=1)


class TestIdentifyTopPainPoints(unittest.TestCase):
    """Test cases for identify_top_pain_points function."""
    
    def setUp(self):
        """Set up test data with pain points."""
        self.pain_point_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'feedback_text': [
                'App crashes frequently',
                'Slow loading times',
                'Great performance',
                'Login issues persist',
                'Excellent features'
            ],
            'sentiment': ['negative', 'negative', 'positive', 'negative', 'positive'],
            'theme': ['Performance', 'Performance', 'Performance', 'Authentication', 'Features'],
            'impact_score': [8.5, 7.2, 3.1, 6.8, 2.9],
            'source_channel': ['iOS App Store', 'Google Play', 'Twitter', 'Internal Sales', 'iOS App Store']
        })
    
    def test_identify_top_pain_points_default(self):
        """Test identifying top pain points with default parameters."""
        pain_points = identify_top_pain_points(self.pain_point_data)
        
        # Should return top 3 by default
        self.assertEqual(len(pain_points), 3)
        
        # Should be sorted by impact score (descending)
        self.assertGreaterEqual(pain_points[0]['impact_score'], pain_points[1]['impact_score'])
        self.assertGreaterEqual(pain_points[1]['impact_score'], pain_points[2]['impact_score'])
        
        # Should only include negative sentiment
        for point in pain_points:
            self.assertEqual(point['sentiment'], 'negative')
    
    def test_identify_top_pain_points_custom_count(self):
        """Test identifying top pain points with custom count."""
        pain_points = identify_top_pain_points(self.pain_point_data, top_n=2)
        
        self.assertEqual(len(pain_points), 2)
        
        # Check highest impact negative item is first
        self.assertEqual(pain_points[0]['impact_score'], 8.5)
        self.assertEqual(pain_points[0]['theme'], 'Performance')
    
    def test_identify_pain_points_no_negative_sentiment(self):
        """Test pain point identification with no negative sentiment."""
        positive_data = self.pain_point_data[self.pain_point_data['sentiment'] == 'positive'].copy()
        pain_points = identify_top_pain_points(positive_data)
        
        # Should return empty list
        self.assertEqual(len(pain_points), 0)
    
    def test_identify_pain_points_empty_data(self):
        """Test pain point identification with empty data."""
        empty_df = pd.DataFrame()
        pain_points = identify_top_pain_points(empty_df)
        
        self.assertEqual(len(pain_points), 0)


class TestIdentifyPraisedFeatures(unittest.TestCase):
    """Test cases for identify_praised_features function."""
    
    def setUp(self):
        """Set up test data with praised features."""
        self.praised_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'feedback_text': [
                'Love the new interface',
                'Excellent trading tools',
                'App crashes often',
                'Great customer support',
                'Poor performance'
            ],
            'sentiment': ['positive', 'positive', 'negative', 'positive', 'negative'],
            'theme': ['UI/UX', 'Trading Tools', 'Performance', 'Support', 'Performance'],
            'impact_score': [6.2, 8.1, 5.5, 7.3, 4.8],
            'source_channel': ['iOS App Store', 'Twitter', 'Google Play', 'Internal Sales', 'iOS App Store']
        })
    
    def test_identify_praised_features_default(self):
        """Test identifying praised features with default parameters."""
        praised_features = identify_praised_features(self.praised_data)
        
        # Should return top 3 by default
        self.assertEqual(len(praised_features), 3)
        
        # Should be sorted by impact score (descending)
        self.assertGreaterEqual(praised_features[0]['impact_score'], praised_features[1]['impact_score'])
        
        # Should only include positive sentiment
        for feature in praised_features:
            self.assertEqual(feature['sentiment'], 'positive')
    
    def test_identify_praised_features_custom_count(self):
        """Test identifying praised features with custom count."""
        praised_features = identify_praised_features(self.praised_data, top_n=1)
        
        self.assertEqual(len(praised_features), 1)
        
        # Check highest impact positive item
        self.assertEqual(praised_features[0]['impact_score'], 8.1)
        self.assertEqual(praised_features[0]['theme'], 'Trading Tools')
    
    def test_identify_praised_features_no_positive_sentiment(self):
        """Test praised feature identification with no positive sentiment."""
        negative_data = self.praised_data[self.praised_data['sentiment'] == 'negative'].copy()
        praised_features = identify_praised_features(negative_data)
        
        # Should return empty list
        self.assertEqual(len(praised_features), 0)


class TestAnalyzeThemeImpact(unittest.TestCase):
    """Test cases for analyze_theme_impact function."""
    
    def setUp(self):
        """Set up test data for theme analysis."""
        self.theme_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006'],
            'theme': ['Performance', 'Performance', 'Features', 'Support', 'Features', 'Performance'],
            'impact_score': [8.5, 7.2, 6.1, 5.8, 4.3, 9.1],
            'sentiment': ['negative', 'negative', 'positive', 'neutral', 'positive', 'negative']
        })
    
    def test_analyze_theme_impact_aggregation(self):
        """Test theme impact analysis and aggregation."""
        theme_analysis = analyze_theme_impact(self.theme_data)
        
        # Should group by theme and aggregate
        self.assertIn('Performance', theme_analysis)
        self.assertIn('Features', theme_analysis)
        self.assertIn('Support', theme_analysis)
        
        # Check Performance theme (highest total impact)
        performance = theme_analysis['Performance']
        self.assertEqual(performance['feedback_count'], 3)
        self.assertAlmostEqual(performance['total_impact'], 24.8, places=1)  # 8.5 + 7.2 + 9.1
        self.assertAlmostEqual(performance['average_impact'], 8.27, places=1)
    
    def test_analyze_theme_impact_sorting(self):
        """Test that themes are sorted by total impact."""
        theme_analysis = analyze_theme_impact(self.theme_data)
        
        # Convert to list to check ordering
        themes_by_impact = list(theme_analysis.keys())
        
        # Performance should be first (highest total impact)
        self.assertEqual(themes_by_impact[0], 'Performance')
    
    def test_analyze_theme_impact_empty_data(self):
        """Test theme analysis with empty data."""
        empty_df = pd.DataFrame()
        theme_analysis = analyze_theme_impact(empty_df)
        
        self.assertEqual(len(theme_analysis), 0)


class TestGenerateStrategicInsights(unittest.TestCase):
    """Test cases for generate_strategic_insights function."""
    
    def setUp(self):
        """Set up test data for strategic insights."""
        self.strategic_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005'],
            'strategic_goal': ['Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth'],
            'impact_score': [8.5, 6.2, 7.8, 5.1, 4.9],
            'sentiment': ['negative', 'positive', 'negative', 'neutral', 'positive'],
            'theme': ['Performance', 'Features', 'Security', 'Support', 'UI/UX']
        })
    
    def test_generate_strategic_insights_aggregation(self):
        """Test strategic insights generation and aggregation."""
        insights = generate_strategic_insights(self.strategic_data)
        
        # Should group by strategic goal
        self.assertIn('Growth', insights)
        self.assertIn('Trust&Safety', insights)
        self.assertIn('CX Efficiency', insights)
        
        # Check Growth goal (most feedback items)
        growth = insights['Growth']
        self.assertEqual(growth['feedback_count'], 3)
        self.assertAlmostEqual(growth['total_impact'], 19.6, places=1)  # 8.5 + 6.2 + 4.9
    
    def test_generate_strategic_insights_sentiment_breakdown(self):
        """Test sentiment breakdown in strategic insights."""
        insights = generate_strategic_insights(self.strategic_data)
        
        growth = insights['Growth']
        
        # Check sentiment distribution
        self.assertIn('sentiment_breakdown', growth)
        sentiment_breakdown = growth['sentiment_breakdown']
        
        self.assertEqual(sentiment_breakdown['negative'], 1)
        self.assertEqual(sentiment_breakdown['positive'], 2)
        self.assertEqual(sentiment_breakdown['neutral'], 0)
    
    def test_generate_strategic_insights_empty_data(self):
        """Test strategic insights with empty data."""
        empty_df = pd.DataFrame()
        insights = generate_strategic_insights(empty_df)
        
        self.assertEqual(len(insights), 0)


class TestBuildComprehensiveContent(unittest.TestCase):
    """Test cases for build_comprehensive_content function."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        self.comprehensive_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store', 'Twitter'],
            'feedback_text': [
                'App crashes frequently during trading',
                'Love the new charting features',
                'Customer wants advanced order types',
                'Slow loading times are frustrating',
                'Excellent customer support experience',
                'Need better mobile notifications'
            ],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'negative'],
            'theme': ['Performance', 'Features', 'Trading Tools', 'Performance', 'Support', 'Mobile'],
            'strategic_goal': ['Trust&Safety', 'Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth'],
            'impact_score': [8.7, 6.2, 7.3, 6.8, 5.1, 4.9],
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(6)
            ]
        })
    
    def test_build_comprehensive_content_structure(self):
        """Test comprehensive content building structure."""
        content = build_comprehensive_content(self.comprehensive_data, top_n=2)
        
        # Check all required sections
        required_sections = [
            'executive_summary',
            'top_pain_points',
            'praised_features',
            'theme_analysis',
            'strategic_insights',
            'metadata'
        ]
        
        for section in required_sections:
            self.assertIn(section, content)
    
    def test_build_comprehensive_content_metadata(self):
        """Test metadata in comprehensive content."""
        content = build_comprehensive_content(self.comprehensive_data, top_n=3)
        
        metadata = content['metadata']
        
        # Check metadata fields
        self.assertIn('generation_timestamp', metadata)
        self.assertIn('total_records_processed', metadata)
        self.assertIn('top_n_items', metadata)
        self.assertIn('data_sources', metadata)
        
        # Check values
        self.assertEqual(metadata['total_records_processed'], 6)
        self.assertEqual(metadata['top_n_items'], 3)
        self.assertEqual(len(metadata['data_sources']), 4)  # 4 unique sources
    
    def test_build_comprehensive_content_top_n_parameter(self):
        """Test top_n parameter in comprehensive content building."""
        content = build_comprehensive_content(self.comprehensive_data, top_n=1)
        
        # Check that top_n is respected
        self.assertEqual(len(content['top_pain_points']), 1)
        self.assertEqual(len(content['praised_features']), 1)
        self.assertEqual(content['metadata']['top_n_items'], 1)
    
    def test_build_comprehensive_content_empty_data(self):
        """Test comprehensive content building with empty data."""
        empty_df = pd.DataFrame()
        content = build_comprehensive_content(empty_df)
        
        # Should handle empty data gracefully
        self.assertIn('executive_summary', content)
        self.assertEqual(content['executive_summary']['total_feedback_items'], 0)
        self.assertEqual(len(content['top_pain_points']), 0)
        self.assertEqual(len(content['praised_features']), 0)
    
    def test_build_comprehensive_content_data_quality(self):
        """Test content building with various data quality issues."""
        # Create data with missing values and edge cases
        problematic_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003'],
            'feedback_text': ['Valid feedback', None, ''],
            'sentiment': ['positive', None, 'invalid'],
            'theme': ['Performance', '', None],
            'impact_score': [5.5, np.nan, -1.0],
            'strategic_goal': ['Growth', None, 'Invalid Goal']
        })
        
        # Should handle problematic data without crashing
        content = build_comprehensive_content(problematic_data)
        
        self.assertIn('executive_summary', content)
        self.assertIn('metadata', content)
        
        # Should process at least some records
        self.assertGreaterEqual(content['metadata']['total_records_processed'], 0)


if __name__ == '__main__':
    unittest.main()