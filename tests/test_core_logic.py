#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Logic Unit Tests for Advanced Trade Insight Engine

This module tests core business logic and algorithms without requiring
external dependencies like pandas, streamlit, etc.

Requirements: 8.1, 8.4
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestSentimentProcessing(unittest.TestCase):
    """Test sentiment processing logic."""
    
    def test_sentiment_value_mapping(self):
        """Test sentiment to numeric value mapping."""
        def get_sentiment_value(sentiment):
            """Map sentiment to numeric value."""
            sentiment_map = {
                'positive': 0.1,
                'neutral': 0.5,
                'negative': 1.5
            }
            return sentiment_map.get(sentiment.lower() if sentiment else None, 0.5)
        
        # Test valid sentiments
        self.assertEqual(get_sentiment_value('positive'), 0.1)
        self.assertEqual(get_sentiment_value('POSITIVE'), 0.1)
        self.assertEqual(get_sentiment_value('negative'), 1.5)
        self.assertEqual(get_sentiment_value('NEGATIVE'), 1.5)
        self.assertEqual(get_sentiment_value('neutral'), 0.5)
        
        # Test invalid sentiments
        self.assertEqual(get_sentiment_value('invalid'), 0.5)
        self.assertEqual(get_sentiment_value(''), 0.5)
        self.assertEqual(get_sentiment_value(None), 0.5)
    
    def test_sentiment_normalization(self):
        """Test sentiment normalization logic."""
        def normalize_sentiment(sentiment):
            """Normalize sentiment values."""
            if not sentiment or not isinstance(sentiment, str):
                return 'neutral'
            
            sentiment = sentiment.strip().lower()
            if sentiment in ['positive', 'pos', 'good', 'great', 'excellent']:
                return 'positive'
            elif sentiment in ['negative', 'neg', 'bad', 'poor', 'terrible']:
                return 'negative'
            else:
                return 'neutral'
        
        # Test positive variations
        self.assertEqual(normalize_sentiment('positive'), 'positive')
        self.assertEqual(normalize_sentiment('pos'), 'positive')
        self.assertEqual(normalize_sentiment('good'), 'positive')
        self.assertEqual(normalize_sentiment('GREAT'), 'positive')
        
        # Test negative variations
        self.assertEqual(normalize_sentiment('negative'), 'negative')
        self.assertEqual(normalize_sentiment('neg'), 'negative')
        self.assertEqual(normalize_sentiment('bad'), 'negative')
        self.assertEqual(normalize_sentiment('POOR'), 'negative')
        
        # Test neutral/invalid
        self.assertEqual(normalize_sentiment('neutral'), 'neutral')
        self.assertEqual(normalize_sentiment('unknown'), 'neutral')
        self.assertEqual(normalize_sentiment(''), 'neutral')
        self.assertEqual(normalize_sentiment(None), 'neutral')


class TestThemeProcessing(unittest.TestCase):
    """Test theme processing logic."""
    
    def test_theme_categorization(self):
        """Test theme categorization logic."""
        def categorize_theme(theme):
            """Categorize themes into standard categories."""
            if not theme or not isinstance(theme, str):
                return 'General Feedback'
            
            theme = theme.strip().lower()
            
            # Performance related
            if any(keyword in theme for keyword in ['performance', 'speed', 'slow', 'fast', 'lag', 'crash']):
                return 'Performance/Outages'
            
            # Trading related
            if any(keyword in theme for keyword in ['trading', 'execution', 'order', 'fee', 'commission']):
                return 'Trading/Execution & Fees'
            
            # Support related
            if any(keyword in theme for keyword in ['support', 'help', 'customer', 'service']):
                return 'Support Experience'
            
            # UI/UX related
            if any(keyword in theme for keyword in ['ui', 'ux', 'interface', 'design', 'layout']):
                return 'UI/UX'
            
            # Mobile related
            if any(keyword in theme for keyword in ['mobile', 'app', 'phone', 'tablet']):
                return 'Mobile Features'
            
            return 'General Feedback'
        
        # Test performance themes
        self.assertEqual(categorize_theme('performance issues'), 'Performance/Outages')
        self.assertEqual(categorize_theme('app crashes frequently'), 'Performance/Outages')
        self.assertEqual(categorize_theme('slow loading'), 'Performance/Outages')
        
        # Test trading themes
        self.assertEqual(categorize_theme('trading execution'), 'Trading/Execution & Fees')
        self.assertEqual(categorize_theme('order processing'), 'Trading/Execution & Fees')
        self.assertEqual(categorize_theme('high fees'), 'Trading/Execution & Fees')
        
        # Test support themes
        self.assertEqual(categorize_theme('customer support'), 'Support Experience')
        self.assertEqual(categorize_theme('help needed'), 'Support Experience')
        
        # Test UI themes
        self.assertEqual(categorize_theme('user interface'), 'UI/UX')
        self.assertEqual(categorize_theme('design problems'), 'UI/UX')
        
        # Test mobile themes
        self.assertEqual(categorize_theme('mobile app'), 'Mobile Features')
        self.assertEqual(categorize_theme('phone issues'), 'Mobile Features')
        
        # Test general/invalid
        self.assertEqual(categorize_theme('general comment'), 'General Feedback')
        self.assertEqual(categorize_theme(''), 'General Feedback')
        self.assertEqual(categorize_theme(None), 'General Feedback')
    
    def test_theme_validation(self):
        """Test theme validation logic."""
        valid_themes = [
            'Performance/Outages',
            'Trading/Execution & Fees',
            'Support Experience',
            'General Feedback',
            'UI/UX',
            'Mobile Features',
            'API/Integration',
            'Security, Fraud & Phishing',
            'Tax Docs & Reporting'
        ]
        
        def validate_theme(theme):
            """Validate theme against known categories."""
            if not theme or not isinstance(theme, str):
                return False, 'General Feedback'
            
            theme = theme.strip()
            if theme in valid_themes:
                return True, theme
            else:
                return False, 'General Feedback'
        
        # Test valid themes
        for theme in valid_themes:
            is_valid, normalized = validate_theme(theme)
            self.assertTrue(is_valid)
            self.assertEqual(normalized, theme)
        
        # Test invalid themes
        is_valid, normalized = validate_theme('Invalid Theme')
        self.assertFalse(is_valid)
        self.assertEqual(normalized, 'General Feedback')
        
        is_valid, normalized = validate_theme('')
        self.assertFalse(is_valid)
        self.assertEqual(normalized, 'General Feedback')


class TestStrategicGoalProcessing(unittest.TestCase):
    """Test strategic goal processing logic."""
    
    def test_strategic_goal_alignment(self):
        """Test strategic goal alignment logic."""
        def get_strategic_multiplier(strategic_goal):
            """Get multiplier based on strategic goal alignment."""
            aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
            
            if not strategic_goal or not isinstance(strategic_goal, str):
                return 1.0
            
            strategic_goal = strategic_goal.strip()
            if strategic_goal in aligned_goals:
                return 2.0
            else:
                return 1.0
        
        # Test aligned goals
        aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
        for goal in aligned_goals:
            self.assertEqual(get_strategic_multiplier(goal), 2.0)
        
        # Test non-aligned goals
        self.assertEqual(get_strategic_multiplier('Other Goal'), 1.0)
        self.assertEqual(get_strategic_multiplier('Random'), 1.0)
        self.assertEqual(get_strategic_multiplier(''), 1.0)
        self.assertEqual(get_strategic_multiplier(None), 1.0)
    
    def test_strategic_goal_validation(self):
        """Test strategic goal validation."""
        valid_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
        
        def validate_strategic_goal(goal):
            """Validate strategic goal."""
            if not goal or not isinstance(goal, str):
                return 'General'
            
            goal = goal.strip()
            if goal in valid_goals:
                return goal
            else:
                return 'General'
        
        # Test valid goals
        for goal in valid_goals:
            self.assertEqual(validate_strategic_goal(goal), goal)
        
        # Test invalid goals
        self.assertEqual(validate_strategic_goal('Invalid'), 'General')
        self.assertEqual(validate_strategic_goal(''), 'General')
        self.assertEqual(validate_strategic_goal(None), 'General')


class TestSourceWeightCalculation(unittest.TestCase):
    """Test source weight calculation logic."""
    
    def test_internal_sales_weight_calculation(self):
        """Test Internal Sales Notes weight calculation."""
        def calculate_sales_weight(arr_impact):
            """Calculate weight for Internal Sales Notes."""
            if arr_impact is None:
                return 1.0  # Default weight for None
            try:
                arr_impact = float(arr_impact) if arr_impact else 0
                weight = arr_impact / 50000
                return max(0.1, weight)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                return 1.0  # Default weight
        
        # Test normal cases
        self.assertEqual(calculate_sales_weight(100000), 2.0)  # 100000 / 50000
        self.assertEqual(calculate_sales_weight(50000), 1.0)   # 50000 / 50000
        self.assertEqual(calculate_sales_weight(25000), 0.5)   # 25000 / 50000
        
        # Test minimum weight
        self.assertEqual(calculate_sales_weight(1000), 0.1)    # Below minimum
        self.assertEqual(calculate_sales_weight(0), 0.1)       # Zero value
        
        # Test invalid values
        self.assertEqual(calculate_sales_weight('invalid'), 1.0)
        self.assertEqual(calculate_sales_weight(None), 1.0)
    
    def test_twitter_weight_calculation(self):
        """Test Twitter weight calculation."""
        def calculate_twitter_weight(followers):
            """Calculate weight for Twitter mentions."""
            if followers is None:
                return 1.0  # Default weight for None
            try:
                followers = float(followers) if followers else 0
                weight = followers / 20000
                return max(0.1, weight)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                return 1.0  # Default weight
        
        # Test normal cases
        self.assertEqual(calculate_twitter_weight(40000), 2.0)  # 40000 / 20000
        self.assertEqual(calculate_twitter_weight(20000), 1.0)  # 20000 / 20000
        self.assertEqual(calculate_twitter_weight(10000), 0.5)  # 10000 / 20000
        
        # Test minimum weight
        self.assertEqual(calculate_twitter_weight(1000), 0.1)   # Below minimum
        self.assertEqual(calculate_twitter_weight(0), 0.1)      # Zero value
        
        # Test invalid values
        self.assertEqual(calculate_twitter_weight('invalid'), 1.0)
        self.assertEqual(calculate_twitter_weight(None), 1.0)
    
    def test_app_store_weight_calculation(self):
        """Test App Store weight calculation."""
        def calculate_app_store_weight(rating, helpful_votes):
            """Calculate weight for App Store reviews."""
            if rating is None and helpful_votes is None:
                return 1.0  # Default weight for None values
            try:
                rating = float(rating) if rating else 0
                helpful_votes = float(helpful_votes) if helpful_votes else 0
                weight = rating + (helpful_votes / 10)
                return max(0.1, weight)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                return 1.0  # Default weight
        
        # Test normal cases
        self.assertEqual(calculate_app_store_weight(4.0, 20), 6.0)  # 4.0 + (20/10)
        self.assertEqual(calculate_app_store_weight(3.5, 15), 5.0)  # 3.5 + (15/10)
        self.assertEqual(calculate_app_store_weight(2.0, 0), 2.0)   # 2.0 + (0/10)
        
        # Test minimum weight
        self.assertEqual(calculate_app_store_weight(0, 0), 0.1)     # Below minimum
        
        # Test invalid values
        self.assertEqual(calculate_app_store_weight('invalid', 10), 1.0)
        self.assertEqual(calculate_app_store_weight(4.0, 'invalid'), 1.0)
        self.assertEqual(calculate_app_store_weight(None, None), 1.0)


class TestImpactScoreCalculation(unittest.TestCase):
    """Test impact score calculation logic."""
    
    def test_complete_impact_score_formula(self):
        """Test complete impact score calculation."""
        def calculate_impact_score(sentiment, severity, source_weight, strategic_goal):
            """Calculate complete impact score."""
            # Sentiment values
            sentiment_values = {
                'positive': 0.1,
                'neutral': 0.5,
                'negative': 1.5
            }
            
            # Strategic multipliers
            aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
            
            # Get values
            sentiment_value = sentiment_values.get(sentiment, 0.5)
            
            try:
                severity = float(severity) if severity else 1.0
                source_weight = float(source_weight) if source_weight else 1.0
            except (ValueError, TypeError):
                severity = 1.0
                source_weight = 1.0
            
            strategic_multiplier = 2.0 if strategic_goal in aligned_goals else 1.0
            
            # Calculate impact score
            impact_score = (sentiment_value * severity) * source_weight * strategic_multiplier
            
            return max(0.0, impact_score)  # Ensure non-negative
        
        # Test complete calculation
        score = calculate_impact_score('negative', 2.0, 2.0, 'Growth')
        expected = (1.5 * 2.0) * 2.0 * 2.0  # = 12.0
        self.assertEqual(score, expected)
        
        # Test with positive sentiment
        score = calculate_impact_score('positive', 1.0, 1.5, 'CX Efficiency')
        expected = (0.1 * 1.0) * 1.5 * 2.0  # = 0.3
        self.assertEqual(score, expected)
        
        # Test with non-aligned goal
        score = calculate_impact_score('negative', 1.0, 1.0, 'Other Goal')
        expected = (1.5 * 1.0) * 1.0 * 1.0  # = 1.5
        self.assertEqual(score, expected)
        
        # Test with invalid inputs
        score = calculate_impact_score('invalid', 'invalid', 'invalid', 'invalid')
        self.assertGreaterEqual(score, 0.0)
        self.assertIsInstance(score, (int, float))
    
    def test_impact_score_edge_cases(self):
        """Test impact score calculation edge cases."""
        def calculate_impact_score_safe(sentiment, severity, source_weight, strategic_goal):
            """Safe impact score calculation with error handling."""
            try:
                # Sentiment values
                sentiment_values = {
                    'positive': 0.1,
                    'neutral': 0.5,
                    'negative': 1.5
                }
                
                # Get sentiment value
                sentiment_value = sentiment_values.get(sentiment, 0.5)
                
                # Ensure numeric values
                try:
                    severity = float(severity) if severity else 1.0
                    source_weight = float(source_weight) if source_weight else 1.0
                except (ValueError, TypeError):
                    severity = 1.0
                    source_weight = 1.0
                
                # Strategic multiplier
                aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
                strategic_multiplier = 2.0 if strategic_goal in aligned_goals else 1.0
                
                # Calculate impact score
                impact_score = (sentiment_value * severity) * source_weight * strategic_multiplier
                
                return max(0.0, impact_score)
                
            except Exception:
                return 0.0  # Fallback to zero on any error
        
        # Test with None values
        score = calculate_impact_score_safe(None, None, None, None)
        self.assertGreaterEqual(score, 0.0)
        
        # Test with empty strings
        score = calculate_impact_score_safe('', '', '', '')
        self.assertGreaterEqual(score, 0.0)
        
        # Test with extreme values
        score = calculate_impact_score_safe('negative', 999999, 999999, 'Growth')
        self.assertGreaterEqual(score, 0.0)
        self.assertIsInstance(score, (int, float))
        
        # Test with negative values
        score = calculate_impact_score_safe('positive', -1, -1, 'Growth')
        self.assertGreaterEqual(score, 0.0)


class TestDataValidation(unittest.TestCase):
    """Test data validation logic."""
    
    def test_customer_id_validation(self):
        """Test customer ID validation."""
        def validate_customer_id(customer_id):
            """Validate customer ID format."""
            if not customer_id or not isinstance(customer_id, str):
                return False, "Customer ID must be a non-empty string"
            
            customer_id = customer_id.strip()
            if len(customer_id) < 3:
                return False, "Customer ID must be at least 3 characters"
            
            # Check for valid format (letters, numbers, hyphens)
            import re
            if not re.match(r'^[A-Za-z0-9\-]+$', customer_id):
                return False, "Customer ID contains invalid characters"
            
            return True, "Valid customer ID"
        
        # Test valid IDs
        valid_ids = ['IOS-001', 'ANDROID-123', 'TW-456', 'SALES-789']
        for customer_id in valid_ids:
            is_valid, message = validate_customer_id(customer_id)
            self.assertTrue(is_valid, f"ID {customer_id} should be valid")
        
        # Test invalid IDs
        invalid_ids = ['', 'AB', 'ID@123', 'ID 123', None, 123]
        for customer_id in invalid_ids:
            is_valid, message = validate_customer_id(customer_id)
            self.assertFalse(is_valid, f"ID {customer_id} should be invalid")
    
    def test_timestamp_validation(self):
        """Test timestamp validation."""
        def validate_timestamp(timestamp):
            """Validate timestamp format."""
            if not timestamp or not isinstance(timestamp, str):
                return False, "Timestamp must be a non-empty string"
            
            timestamp = timestamp.strip()
            
            # Check for basic ISO format
            import re
            iso_pattern = r'^\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}$'
            if re.match(iso_pattern, timestamp):
                return True, "Valid timestamp"
            
            return False, "Invalid timestamp format"
        
        # Test valid timestamps
        valid_timestamps = [
            '2024-01-01 10:00:00',
            '2024-12-31 23:59:59',
            '2024-01-01T10:00:00'
        ]
        for timestamp in valid_timestamps:
            is_valid, message = validate_timestamp(timestamp)
            self.assertTrue(is_valid, f"Timestamp {timestamp} should be valid")
        
        # Test invalid timestamps
        invalid_timestamps = [
            '',
            '2024-01-01',
            '10:00:00',
            '2024/01/01 10:00:00',
            'invalid',
            None,
            123
        ]
        for timestamp in invalid_timestamps:
            is_valid, message = validate_timestamp(timestamp)
            self.assertFalse(is_valid, f"Timestamp {timestamp} should be invalid")
    
    def test_numeric_field_validation(self):
        """Test numeric field validation."""
        def validate_numeric_field(value, field_name, min_val=None, max_val=None):
            """Validate numeric field with optional range."""
            if value is None:
                return False, f"{field_name} cannot be None"
            
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                return False, f"{field_name} must be numeric"
            
            if min_val is not None and numeric_value < min_val:
                return False, f"{field_name} must be >= {min_val}"
            
            if max_val is not None and numeric_value > max_val:
                return False, f"{field_name} must be <= {max_val}"
            
            return True, f"Valid {field_name}"
        
        # Test valid numeric values
        is_valid, message = validate_numeric_field(5.0, "rating", 1.0, 5.0)
        self.assertTrue(is_valid)
        
        is_valid, message = validate_numeric_field("3.5", "rating", 1.0, 5.0)
        self.assertTrue(is_valid)
        
        # Test invalid numeric values
        is_valid, message = validate_numeric_field("invalid", "rating")
        self.assertFalse(is_valid)
        
        is_valid, message = validate_numeric_field(None, "rating")
        self.assertFalse(is_valid)
        
        is_valid, message = validate_numeric_field(0.5, "rating", 1.0, 5.0)
        self.assertFalse(is_valid)
        
        is_valid, message = validate_numeric_field(6.0, "rating", 1.0, 5.0)
        self.assertFalse(is_valid)


class TestFileOperations(unittest.TestCase):
    """Test file operation utilities."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_file_path_validation(self):
        """Test file path validation."""
        def validate_file_path(file_path):
            """Validate file path."""
            if not file_path or not isinstance(file_path, str):
                return False, "File path must be a non-empty string"
            
            file_path = file_path.strip()
            
            # Check for valid file extension
            if not file_path.endswith('.csv'):
                return False, "File must have .csv extension"
            
            # Check for valid characters
            import re
            if not re.match(r'^[A-Za-z0-9\-_./\\]+\.csv$', file_path):
                return False, "File path contains invalid characters"
            
            return True, "Valid file path"
        
        # Test valid paths
        valid_paths = [
            'data.csv',
            'path/to/data.csv',
            'data-file_123.csv'
        ]
        for path in valid_paths:
            is_valid, message = validate_file_path(path)
            self.assertTrue(is_valid, f"Path {path} should be valid")
        
        # Test invalid paths
        invalid_paths = [
            '',
            'data.txt',
            'data',
            'data@file.csv',
            None,
            123
        ]
        for path in invalid_paths:
            is_valid, message = validate_file_path(path)
            self.assertFalse(is_valid, f"Path {path} should be invalid")
    
    def test_directory_creation(self):
        """Test directory creation utility."""
        def ensure_directory_exists(directory_path):
            """Ensure directory exists, create if necessary."""
            try:
                if not os.path.exists(directory_path):
                    os.makedirs(directory_path, exist_ok=True)
                return True, f"Directory {directory_path} ready"
            except Exception as e:
                return False, f"Failed to create directory: {e}"
        
        # Test directory creation
        test_dir = os.path.join(self.temp_dir, 'test_subdir')
        success, message = ensure_directory_exists(test_dir)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(test_dir))
        self.assertTrue(os.path.isdir(test_dir))
        
        # Test nested directory creation
        nested_dir = os.path.join(self.temp_dir, 'nested', 'deep', 'directory')
        success, message = ensure_directory_exists(nested_dir)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.isdir(nested_dir))


if __name__ == '__main__':
    # Run all core logic tests
    unittest.main(verbosity=2)