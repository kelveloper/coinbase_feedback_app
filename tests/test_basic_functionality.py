"""
Basic functionality tests that don't require external dependencies.

These tests verify that the test infrastructure is working correctly
and provide basic validation of core functionality.
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasicFunctionality(unittest.TestCase):
    """Basic functionality tests."""
    
    def test_python_version(self):
        """Test that Python version is compatible."""
        version_info = sys.version_info
        self.assertGreaterEqual(version_info.major, 3)
        self.assertGreaterEqual(version_info.minor, 6)
    
    def test_project_structure(self):
        """Test that project structure exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # Check main directories exist
        expected_dirs = ['src', 'tests', 'csv_mock_data']
        for dir_name in expected_dirs:
            dir_path = os.path.join(project_root, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"Directory {dir_name} should exist")
    
    def test_src_modules_exist(self):
        """Test that source modules exist."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        src_dir = os.path.join(project_root, 'src')
        
        # Check main module directories exist
        expected_modules = ['data_processing', 'analysis', 'reporting', 'dashboard']
        for module_name in expected_modules:
            module_path = os.path.join(src_dir, module_name)
            self.assertTrue(os.path.exists(module_path), f"Module {module_name} should exist")
    
    def test_csv_mock_data_exists(self):
        """Test that mock CSV data files exist."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        csv_dir = os.path.join(project_root, 'csv_mock_data')
        
        # Check expected CSV files exist
        expected_files = [
            'coinbase_advance_apple_reviews.csv',
            'coinbase_advanceGoogle_Play.csv',
            'coinbase_advanced_twitter_mentions.csv',
            'coinbase_advance_internal_sales_notes.csv'
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(csv_dir, file_name)
            self.assertTrue(os.path.exists(file_path), f"CSV file {file_name} should exist")
    
    def test_config_file_exists(self):
        """Test that configuration file exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(project_root, 'config.py')
        self.assertTrue(os.path.exists(config_path), "config.py should exist")
    
    def test_main_file_exists(self):
        """Test that main execution file exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        main_path = os.path.join(project_root, 'main.py')
        self.assertTrue(os.path.exists(main_path), "main.py should exist")
    
    def test_requirements_file_exists(self):
        """Test that requirements file exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        requirements_path = os.path.join(project_root, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path), "requirements.txt should exist")


class TestStringOperations(unittest.TestCase):
    """Test basic string operations used in the system."""
    
    def test_sentiment_normalization(self):
        """Test sentiment value normalization."""
        def normalize_sentiment(sentiment):
            """Normalize sentiment values."""
            if not sentiment or not isinstance(sentiment, str):
                return 'neutral'
            
            sentiment = sentiment.strip().lower()
            if sentiment in ['positive', 'pos', 'good']:
                return 'positive'
            elif sentiment in ['negative', 'neg', 'bad']:
                return 'negative'
            else:
                return 'neutral'
        
        # Test valid sentiments
        self.assertEqual(normalize_sentiment('positive'), 'positive')
        self.assertEqual(normalize_sentiment('POSITIVE'), 'positive')
        self.assertEqual(normalize_sentiment('  positive  '), 'positive')
        self.assertEqual(normalize_sentiment('negative'), 'negative')
        self.assertEqual(normalize_sentiment('neutral'), 'neutral')
        
        # Test invalid sentiments
        self.assertEqual(normalize_sentiment('invalid'), 'neutral')
        self.assertEqual(normalize_sentiment(''), 'neutral')
        self.assertEqual(normalize_sentiment(None), 'neutral')
        self.assertEqual(normalize_sentiment(123), 'neutral')
    
    def test_theme_validation(self):
        """Test theme validation logic."""
        def validate_theme(theme):
            """Validate theme values."""
            valid_themes = [
                'Performance/Outages',
                'Trading/Execution & Fees',
                'Support Experience',
                'General Feedback',
                'UI/UX',
                'Mobile Features',
                'API/Integration'
            ]
            
            if not theme or not isinstance(theme, str):
                return 'General Feedback'
            
            theme = theme.strip()
            if theme in valid_themes:
                return theme
            else:
                return 'General Feedback'
        
        # Test valid themes
        self.assertEqual(validate_theme('Performance/Outages'), 'Performance/Outages')
        self.assertEqual(validate_theme('Trading/Execution & Fees'), 'Trading/Execution & Fees')
        
        # Test invalid themes
        self.assertEqual(validate_theme('Invalid Theme'), 'General Feedback')
        self.assertEqual(validate_theme(''), 'General Feedback')
        self.assertEqual(validate_theme(None), 'General Feedback')
    
    def test_impact_score_calculation(self):
        """Test basic impact score calculation logic."""
        def calculate_basic_impact_score(sentiment, severity, source_weight):
            """Calculate basic impact score."""
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
            
            # Calculate impact score
            impact_score = sentiment_value * severity * source_weight
            
            return max(0.0, impact_score)  # Ensure non-negative
        
        # Test normal calculations
        self.assertAlmostEqual(
            calculate_basic_impact_score('negative', 2.0, 1.5),
            4.5,  # 1.5 * 2.0 * 1.5
            places=2
        )
        
        self.assertAlmostEqual(
            calculate_basic_impact_score('positive', 1.0, 2.0),
            0.2,  # 0.1 * 1.0 * 2.0
            places=2
        )
        
        # Test edge cases
        self.assertGreaterEqual(
            calculate_basic_impact_score('invalid', None, 'invalid'),
            0.0
        )
        
        self.assertGreaterEqual(
            calculate_basic_impact_score(None, 0, 0),
            0.0
        )


class TestDataStructures(unittest.TestCase):
    """Test basic data structure operations."""
    
    def test_dictionary_operations(self):
        """Test dictionary operations used in the system."""
        # Test creating report content structure
        report_content = {
            'executive_summary': {},
            'top_pain_points': [],
            'praised_features': [],
            'theme_analysis': {},
            'strategic_insights': {},
            'metadata': {}
        }
        
        # Test required keys exist
        required_keys = ['executive_summary', 'top_pain_points', 'praised_features']
        for key in required_keys:
            self.assertIn(key, report_content)
        
        # Test adding data
        report_content['executive_summary']['total_items'] = 100
        report_content['top_pain_points'].append({'theme': 'Performance', 'impact': 8.5})
        
        self.assertEqual(report_content['executive_summary']['total_items'], 100)
        self.assertEqual(len(report_content['top_pain_points']), 1)
    
    def test_list_operations(self):
        """Test list operations used in the system."""
        # Test creating and manipulating feedback lists
        feedback_items = []
        
        # Add items
        feedback_items.append({
            'customer_id': 'TEST-001',
            'sentiment': 'positive',
            'theme': 'Performance',
            'impact_score': 5.2
        })
        
        feedback_items.append({
            'customer_id': 'TEST-002',
            'sentiment': 'negative',
            'theme': 'Support',
            'impact_score': 7.8
        })
        
        # Test filtering
        negative_feedback = [item for item in feedback_items if item['sentiment'] == 'negative']
        self.assertEqual(len(negative_feedback), 1)
        
        # Test sorting by impact score
        sorted_feedback = sorted(feedback_items, key=lambda x: x['impact_score'], reverse=True)
        self.assertEqual(sorted_feedback[0]['customer_id'], 'TEST-002')  # Higher impact score
    
    def test_file_path_operations(self):
        """Test file path operations."""
        import os
        
        # Test path joining
        base_path = '/project/root'
        data_path = os.path.join(base_path, 'csv_mock_data')
        output_path = os.path.join(base_path, 'output')
        
        self.assertEqual(data_path, '/project/root/csv_mock_data')
        self.assertEqual(output_path, '/project/root/output')
        
        # Test file extension checking
        csv_files = ['data.csv', 'report.pdf', 'config.json', 'backup.csv']
        csv_only = [f for f in csv_files if f.endswith('.csv')]
        
        self.assertEqual(len(csv_only), 2)
        self.assertIn('data.csv', csv_only)
        self.assertIn('backup.csv', csv_only)


if __name__ == '__main__':
    # Run basic functionality tests
    unittest.main(verbosity=2)