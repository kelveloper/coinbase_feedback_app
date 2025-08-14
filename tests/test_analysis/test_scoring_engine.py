"""
Unit tests for the scoring engine module.

Tests cover source weight calculations, impact score calculations,
and DataFrame enrichment functionality with various edge cases.
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from analysis.scoring_engine import (
    calculate_source_weight,
    calculate_impact_score,
    enrich_dataframe_with_scores
)


class TestSourceWeighting(unittest.TestCase):
    """Test cases for source weight calculation functionality."""
    
    def test_internal_sales_notes_weighting(self):
        """Test Internal Sales Notes weighting formula: ARR_impact / 50000"""
        # Test normal case
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': 100000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 2.0)  # 100000 / 50000 = 2.0
        
        # Test with smaller ARR impact
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': 25000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.5)  # 25000 / 50000 = 0.5
        
        # Test minimum weight enforcement
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': 1000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)  # Should be minimum 0.1
    
    def test_internal_sales_notes_missing_arr(self):
        """Test Internal Sales Notes with missing ARR_impact_estimate_USD"""
        record = pd.Series({
            'source': 'Internal Sales Notes'
            # Missing ARR_impact_estimate_USD
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)  # Should use minimum weight
        
        # Test with None value
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': None
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)
        
        # Test with NaN value
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': np.nan
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)
    
    def test_twitter_weighting(self):
        """Test Twitter weighting formula: followers / 20000"""
        # Test normal case
        record = pd.Series({
            'source': 'Twitter (X)',
            'followers': 40000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 2.0)  # 40000 / 20000 = 2.0
        
        # Test with smaller follower count
        record = pd.Series({
            'source': 'Twitter (X)',
            'followers': 10000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.5)  # 10000 / 20000 = 0.5
        
        # Test minimum weight enforcement
        record = pd.Series({
            'source': 'Twitter (X)',
            'followers': 1000
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)  # Should be minimum 0.1
    
    def test_twitter_missing_followers(self):
        """Test Twitter with missing followers"""
        record = pd.Series({
            'source': 'Twitter (X)'
            # Missing followers
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)
        
        # Test with None value
        record = pd.Series({
            'source': 'Twitter (X)',
            'followers': None
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)
    
    def test_app_store_weighting(self):
        """Test App Store weighting formula: rating + (helpful_votes / 10)"""
        # Test iOS App Store
        record = pd.Series({
            'source': 'iOS App Store',
            'rating': 4.0,
            'helpful_votes': 20
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 6.0)  # 4.0 + (20 / 10) = 6.0
        
        # Test Google Play Store
        record = pd.Series({
            'source': 'Google Play Store',
            'rating': 3.5,
            'helpful_votes': 15
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 5.0)  # 3.5 + (15 / 10) = 5.0
        
        # Test with zero helpful votes
        record = pd.Series({
            'source': 'iOS App Store',
            'rating': 2.0,
            'helpful_votes': 0
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 2.0)  # 2.0 + (0 / 10) = 2.0
    
    def test_app_store_missing_fields(self):
        """Test App Store with missing rating or helpful_votes"""
        # Missing both fields
        record = pd.Series({
            'source': 'iOS App Store'
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 0.1)  # Should use minimum weight
        
        # Missing rating
        record = pd.Series({
            'source': 'iOS App Store',
            'helpful_votes': 10
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)  # 0 + (10 / 10) = 1.0
        
        # Missing helpful_votes
        record = pd.Series({
            'source': 'iOS App Store',
            'rating': 3.0
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 3.0)  # 3.0 + (0 / 10) = 3.0
    
    def test_default_weighting(self):
        """Test default weighting for unknown sources"""
        record = pd.Series({
            'source': 'Unknown Source'
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)
        
        # Test with empty source
        record = pd.Series({
            'source': ''
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)
        
        # Test with missing source
        record = pd.Series({})
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)
    
    def test_case_insensitive_source_matching(self):
        """Test that source matching is case insensitive"""
        # Test various case combinations
        sources = [
            'INTERNAL SALES NOTES',
            'internal sales notes',
            'Internal Sales Notes',
            'TWITTER (X)',
            'twitter (x)',
            'IOS APP STORE',
            'ios app store'
        ]
        
        for source in sources:
            record = pd.Series({
                'source': source,
                'ARR_impact_estimate_USD': 50000,
                'followers': 20000,
                'rating': 4.0,
                'helpful_votes': 10
            })
            weight = calculate_source_weight(record)
            self.assertGreater(weight, 0)  # Should calculate some weight
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types in weighting calculations"""
        # Test invalid ARR impact
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'ARR_impact_estimate_USD': 'invalid'
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)  # Should fallback to default
        
        # Test invalid followers
        record = pd.Series({
            'source': 'Twitter (X)',
            'followers': 'invalid'
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)
        
        # Test invalid rating
        record = pd.Series({
            'source': 'iOS App Store',
            'rating': 'invalid',
            'helpful_votes': 10
        })
        weight = calculate_source_weight(record)
        self.assertEqual(weight, 1.0)


class TestImpactScoring(unittest.TestCase):
    """Test cases for impact score calculation functionality."""
    
    def test_sentiment_value_mapping(self):
        """Test sentiment value mapping: negative=1.5, neutral=0.5, positive=0.1"""
        base_record = pd.Series({
            'source': 'Test Source',
            'severity': 1.0,
            'strategic_goal': 'General'
        })
        
        # Test negative sentiment
        record = base_record.copy()
        record['sentiment'] = 'negative'
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 1.5 * 1.0 * 1.0 * 1.0  # sentiment * severity * source_weight * strategic_multiplier
        self.assertEqual(score, expected)
        
        # Test neutral sentiment
        record = base_record.copy()
        record['sentiment'] = 'neutral'
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 0.5 * 1.0 * 1.0 * 1.0
        self.assertEqual(score, expected)
        
        # Test positive sentiment
        record = base_record.copy()
        record['sentiment'] = 'positive'
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 0.1 * 1.0 * 1.0 * 1.0
        self.assertEqual(score, expected)
    
    def test_strategic_multiplier_logic(self):
        """Test strategic multiplier: aligned=2.0, others=1.0"""
        base_record = pd.Series({
            'source': 'Test Source',
            'sentiment': 'negative',
            'severity': 1.0
        })
        
        # Test aligned strategic goals
        aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
        
        for goal in aligned_goals:
            record = base_record.copy()
            record['strategic_goal'] = goal
            score = calculate_impact_score(record, source_weight=1.0)
            expected = 1.5 * 1.0 * 1.0 * 2.0  # Should use 2.0 multiplier
            self.assertEqual(score, expected)
        
        # Test non-aligned strategic goal
        record = base_record.copy()
        record['strategic_goal'] = 'Other Goal'
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 1.5 * 1.0 * 1.0 * 1.0  # Should use 1.0 multiplier
        self.assertEqual(score, expected)
    
    def test_complete_impact_score_formula(self):
        """Test complete impact score formula with all components"""
        record = pd.Series({
            'source': 'Internal Sales Notes',
            'sentiment': 'negative',
            'severity': 2.0,
            'strategic_goal': 'Growth',
            'ARR_impact_estimate_USD': 100000
        })
        
        # Calculate expected values
        sentiment_value = 1.5  # negative
        severity = 2.0
        source_weight = 2.0  # 100000 / 50000
        strategic_multiplier = 2.0  # Growth is aligned
        
        expected = (sentiment_value * severity) * source_weight * strategic_multiplier
        expected = (1.5 * 2.0) * 2.0 * 2.0  # = 12.0
        
        score = calculate_impact_score(record)
        self.assertEqual(score, expected)
    
    def test_missing_sentiment_handling(self):
        """Test handling of missing sentiment values"""
        record = pd.Series({
            'source': 'Test Source',
            'severity': 1.0,
            'strategic_goal': 'General'
        })
        
        # Test missing sentiment
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 0.5 * 1.0 * 1.0 * 1.0  # Should default to neutral (0.5)
        self.assertEqual(score, expected)
        
        # Test None sentiment
        record['sentiment'] = None
        score = calculate_impact_score(record, source_weight=1.0)
        self.assertEqual(score, expected)
        
        # Test NaN sentiment
        record['sentiment'] = np.nan
        score = calculate_impact_score(record, source_weight=1.0)
        self.assertEqual(score, expected)
    
    def test_missing_severity_handling(self):
        """Test handling of missing severity values"""
        record = pd.Series({
            'source': 'Test Source',
            'sentiment': 'negative',
            'strategic_goal': 'General'
        })
        
        # Test missing severity
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 1.5 * 1.0 * 1.0 * 1.0  # Should default to 1.0
        self.assertEqual(score, expected)
        
        # Test None severity
        record['severity'] = None
        score = calculate_impact_score(record, source_weight=1.0)
        self.assertEqual(score, expected)
        
        # Test invalid severity
        record['severity'] = 'invalid'
        score = calculate_impact_score(record, source_weight=1.0)
        self.assertEqual(score, expected)
    
    def test_missing_strategic_goal_handling(self):
        """Test handling of missing strategic goal values"""
        record = pd.Series({
            'source': 'Test Source',
            'sentiment': 'negative',
            'severity': 1.0
        })
        
        # Test missing strategic_goal
        score = calculate_impact_score(record, source_weight=1.0)
        expected = 1.5 * 1.0 * 1.0 * 1.0  # Should default to 1.0 multiplier
        self.assertEqual(score, expected)
        
        # Test None strategic_goal
        record['strategic_goal'] = None
        score = calculate_impact_score(record, source_weight=1.0)
        self.assertEqual(score, expected)
    
    def test_source_weight_calculation_integration(self):
        """Test that impact score calculates source weight when not provided"""
        record = pd.Series({
            'source': 'Twitter (X)',
            'sentiment': 'negative',
            'severity': 1.0,
            'strategic_goal': 'Growth',
            'followers': 40000
        })
        
        # Don't provide source_weight, should calculate it
        score = calculate_impact_score(record)
        
        # Expected calculation:
        # source_weight = 40000 / 20000 = 2.0
        # sentiment_value = 1.5, severity = 1.0, strategic_multiplier = 2.0
        expected = (1.5 * 1.0) * 2.0 * 2.0  # = 6.0
        self.assertEqual(score, expected)


class TestDataFrameEnrichment(unittest.TestCase):
    """Test cases for DataFrame enrichment functionality."""
    
    def test_enrich_empty_dataframe(self):
        """Test enrichment of empty DataFrame"""
        df = pd.DataFrame()
        enriched_df = enrich_dataframe_with_scores(df)
        self.assertTrue(enriched_df.empty)
    
    def test_enrich_single_record(self):
        """Test enrichment of single record DataFrame"""
        df = pd.DataFrame([{
            'source': 'Internal Sales Notes',
            'sentiment': 'negative',
            'severity': 1.0,
            'strategic_goal': 'Growth',
            'ARR_impact_estimate_USD': 50000
        }])
        
        enriched_df = enrich_dataframe_with_scores(df)
        
        # Check that new columns were added
        self.assertIn('source_weight', enriched_df.columns)
        self.assertIn('impact_score', enriched_df.columns)
        
        # Check calculated values
        expected_weight = 1.0  # 50000 / 50000
        expected_score = (1.5 * 1.0) * 1.0 * 2.0  # = 3.0
        
        self.assertEqual(enriched_df.iloc[0]['source_weight'], expected_weight)
        self.assertEqual(enriched_df.iloc[0]['impact_score'], expected_score)
    
    def test_enrich_multiple_records(self):
        """Test enrichment of multiple records with different sources"""
        df = pd.DataFrame([
            {
                'source': 'Internal Sales Notes',
                'sentiment': 'negative',
                'severity': 1.0,
                'strategic_goal': 'Growth',
                'ARR_impact_estimate_USD': 100000
            },
            {
                'source': 'Twitter (X)',
                'sentiment': 'positive',
                'severity': 0.5,
                'strategic_goal': 'General',
                'followers': 20000
            },
            {
                'source': 'iOS App Store',
                'sentiment': 'neutral',
                'severity': 1.5,
                'strategic_goal': 'CX Efficiency',
                'rating': 4.0,
                'helpful_votes': 10
            }
        ])
        
        enriched_df = enrich_dataframe_with_scores(df)
        
        # Check that all records were processed
        self.assertEqual(len(enriched_df), 3)
        self.assertIn('source_weight', enriched_df.columns)
        self.assertIn('impact_score', enriched_df.columns)
        
        # Verify no NaN values in calculated columns
        self.assertFalse(enriched_df['source_weight'].isna().any())
        self.assertFalse(enriched_df['impact_score'].isna().any())
        
        # Verify all scores are positive numbers
        self.assertTrue((enriched_df['source_weight'] > 0).all())
        self.assertTrue((enriched_df['impact_score'] >= 0).all())
    
    def test_original_dataframe_unchanged(self):
        """Test that original DataFrame is not modified during enrichment"""
        original_df = pd.DataFrame([{
            'source': 'Test Source',
            'sentiment': 'negative',
            'severity': 1.0,
            'strategic_goal': 'Growth'
        }])
        
        original_columns = original_df.columns.tolist()
        enriched_df = enrich_dataframe_with_scores(original_df)
        
        # Original DataFrame should be unchanged
        self.assertEqual(original_df.columns.tolist(), original_columns)
        self.assertNotIn('source_weight', original_df.columns)
        self.assertNotIn('impact_score', original_df.columns)
        
        # Enriched DataFrame should have new columns
        self.assertIn('source_weight', enriched_df.columns)
        self.assertIn('impact_score', enriched_df.columns)


if __name__ == '__main__':
    unittest.main()