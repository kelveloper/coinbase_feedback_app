#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic Integration Tests for Advanced Trade Insight Engine

This module tests integration between components without requiring
external dependencies like pandas, streamlit, etc.

Requirements: 8.2, 8.3, 8.4
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockDataGenerator:
    """Generate mock data for testing without external dependencies."""
    
    @staticmethod
    def create_mock_csv_data():
        """Create mock CSV data as dictionaries."""
        ios_data = [
            {
                'customer_id': 'IOS-001',
                'source': 'iOS App Store',
                'username': 'user1',
                'timestamp': '2024-01-01 10:00:00',
                'rating': '4',
                'sentiment': 'positive',
                'review_text': 'Great app!',
                'theme': 'Performance',
                'severity': '1.0',
                'strategic_goal': 'Growth',
                'helpful_votes': '5'
            },
            {
                'customer_id': 'IOS-002',
                'source': 'iOS App Store',
                'username': 'user2',
                'timestamp': '2024-01-02 11:00:00',
                'rating': '2',
                'sentiment': 'negative',
                'review_text': 'Needs improvement',
                'theme': 'Trading/Execution & Fees',
                'severity': '2.0',
                'strategic_goal': 'CX Efficiency',
                'helpful_votes': '10'
            }
        ]
        
        twitter_data = [
            {
                'customer_id': 'TW-001',
                'source': 'Twitter (X)',
                'handle': '@trader1',
                'followers': '148860',
                'timestamp': '2024-01-05 14:00:00',
                'sentiment': 'positive',
                'tweet_text': 'Great trading experience!',
                'theme': 'Trading/Execution & Fees',
                'severity': '1.0',
                'strategic_goal': 'Growth'
            },
            {
                'customer_id': 'TW-002',
                'source': 'Twitter (X)',
                'handle': '@trader2',
                'followers': '106574',
                'timestamp': '2024-01-06 15:00:00',
                'sentiment': 'negative',
                'tweet_text': 'Having issues',
                'theme': 'Support Experience',
                'severity': '2.0',
                'strategic_goal': 'CX Efficiency'
            }
        ]
        
        sales_data = [
            {
                'customer_id': 'SALES-001',
                'source': 'Internal Sales Notes',
                'account_name': 'Enterprise Corp',
                'timestamp': '2024-01-07 16:00:00',
                'sentiment': 'positive',
                'note_text': 'Customer very satisfied',
                'theme': 'Performance',
                'severity': '1.0',
                'strategic_goal': 'Growth',
                'ARR_impact_estimate_USD': '75000'
            },
            {
                'customer_id': 'SALES-002',
                'source': 'Internal Sales Notes',
                'account_name': 'Startup Inc',
                'timestamp': '2024-01-08 17:00:00',
                'sentiment': 'neutral',
                'note_text': 'Customer has concerns',
                'theme': 'Trading/Execution & Fees',
                'severity': '1.5',
                'strategic_goal': 'CX Efficiency',
                'ARR_impact_estimate_USD': '25000'
            }
        ]
        
        return {
            'ios_reviews': ios_data,
            'twitter_mentions': twitter_data,
            'sales_notes': sales_data
        }
    
    @staticmethod
    def create_csv_files(directory):
        """Create actual CSV files in the specified directory."""
        mock_data = MockDataGenerator.create_mock_csv_data()
        
        # iOS reviews
        ios_file = os.path.join(directory, 'coinbase_advance_apple_reviews.csv')
        with open(ios_file, 'w') as f:
            if mock_data['ios_reviews']:
                # Write header
                headers = list(mock_data['ios_reviews'][0].keys())
                f.write(','.join(headers) + '\n')
                
                # Write data
                for row in mock_data['ios_reviews']:
                    values = [str(row[header]) for header in headers]
                    f.write(','.join(values) + '\n')
        
        # Twitter mentions
        twitter_file = os.path.join(directory, 'coinbase_advanced_twitter_mentions.csv')
        with open(twitter_file, 'w') as f:
            if mock_data['twitter_mentions']:
                # Write header
                headers = list(mock_data['twitter_mentions'][0].keys())
                f.write(','.join(headers) + '\n')
                
                # Write data
                for row in mock_data['twitter_mentions']:
                    values = [str(row[header]) for header in headers]
                    f.write(','.join(values) + '\n')
        
        # Sales notes
        sales_file = os.path.join(directory, 'coinbase_advance_internal_sales_notes.csv')
        with open(sales_file, 'w') as f:
            if mock_data['sales_notes']:
                # Write header
                headers = list(mock_data['sales_notes'][0].keys())
                f.write(','.join(headers) + '\n')
                
                # Write data
                for row in mock_data['sales_notes']:
                    values = [str(row[header]) for header in headers]
                    f.write(','.join(values) + '\n')
        
        return [ios_file, twitter_file, sales_file]


class TestDataPipelineIntegration(unittest.TestCase):
    """Test integration of data pipeline components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'csv_mock_data')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create mock CSV files
        self.csv_files = MockDataGenerator.create_csv_files(self.data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_csv_file_creation(self):
        """Test that mock CSV files are created correctly."""
        # Verify files exist
        for csv_file in self.csv_files:
            self.assertTrue(os.path.exists(csv_file), f"CSV file {csv_file} should exist")
            
            # Verify file has content
            with open(csv_file, 'r') as f:
                content = f.read()
                self.assertGreater(len(content), 0, f"CSV file {csv_file} should have content")
                
                # Verify has header and data
                lines = content.strip().split('\n')
                self.assertGreater(len(lines), 1, f"CSV file {csv_file} should have header and data")
    
    def test_data_loading_simulation(self):
        """Test data loading simulation without pandas."""
        def load_csv_simple(file_path):
            """Simple CSV loader without pandas."""
            data = []
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    if len(lines) < 2:
                        return data
                    
                    # Parse header
                    headers = [h.strip() for h in lines[0].strip().split(',')]
                    
                    # Parse data rows
                    for line in lines[1:]:
                        values = [v.strip() for v in line.strip().split(',')]
                        if len(values) == len(headers):
                            row = dict(zip(headers, values))
                            data.append(row)
                
                return data
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                return data
        
        # Test loading each CSV file
        total_records = 0
        for csv_file in self.csv_files:
            data = load_csv_simple(csv_file)
            self.assertGreater(len(data), 0, f"Should load data from {csv_file}")
            
            # Verify data structure
            for record in data:
                self.assertIn('customer_id', record)
                self.assertIn('source', record)
                self.assertIn('timestamp', record)
                self.assertIn('sentiment', record)
            
            total_records += len(data)
        
        # Verify total records loaded
        self.assertGreater(total_records, 0, "Should load records from all files")
        print(f"✅ Loaded {total_records} records from {len(self.csv_files)} files")
    
    def test_data_normalization_simulation(self):
        """Test data normalization simulation."""
        def normalize_feedback_text(record, source_type):
            """Normalize feedback text based on source type."""
            if source_type == 'ios_reviews' and 'review_text' in record:
                return record['review_text']
            elif source_type == 'twitter_mentions' and 'tweet_text' in record:
                return record['tweet_text']
            elif source_type == 'sales_notes' and 'note_text' in record:
                return record['note_text']
            else:
                return ''
        
        def normalize_author_handle(record, source_type):
            """Normalize author handle based on source type."""
            if source_type == 'ios_reviews' and 'username' in record:
                return record['username']
            elif source_type == 'twitter_mentions' and 'handle' in record:
                return record['handle']
            elif source_type == 'sales_notes' and 'account_name' in record:
                return record['account_name']
            else:
                return ''
        
        # Load mock data
        mock_data = MockDataGenerator.create_mock_csv_data()
        
        # Test normalization for each source type
        for source_type, records in mock_data.items():
            for record in records:
                # Test feedback text normalization
                feedback_text = normalize_feedback_text(record, source_type)
                self.assertIsInstance(feedback_text, str)
                self.assertGreater(len(feedback_text), 0, f"Should normalize feedback text for {source_type}")
                
                # Test author handle normalization
                author_handle = normalize_author_handle(record, source_type)
                self.assertIsInstance(author_handle, str)
                self.assertGreater(len(author_handle), 0, f"Should normalize author handle for {source_type}")
        
        print("✅ Data normalization simulation completed successfully")
    
    def test_nlp_processing_simulation(self):
        """Test NLP processing simulation."""
        def extract_sentiment(record):
            """Extract sentiment from record."""
            sentiment = record.get('sentiment', '').lower().strip()
            if sentiment in ['positive', 'negative', 'neutral']:
                return sentiment
            else:
                return 'neutral'
        
        def extract_theme(record):
            """Extract theme from record."""
            theme = record.get('theme', '').strip()
            if theme:
                return theme
            else:
                return 'General Feedback'
        
        def extract_strategic_goal(record):
            """Extract strategic goal from record."""
            goal = record.get('strategic_goal', '').strip()
            valid_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
            if goal in valid_goals:
                return goal
            else:
                return 'General'
        
        # Load mock data
        mock_data = MockDataGenerator.create_mock_csv_data()
        
        # Test NLP processing for each record
        total_processed = 0
        for source_type, records in mock_data.items():
            for record in records:
                # Test sentiment extraction
                sentiment = extract_sentiment(record)
                self.assertIn(sentiment, ['positive', 'negative', 'neutral'])
                
                # Test theme extraction
                theme = extract_theme(record)
                self.assertIsInstance(theme, str)
                self.assertGreater(len(theme), 0)
                
                # Test strategic goal extraction
                strategic_goal = extract_strategic_goal(record)
                self.assertIsInstance(strategic_goal, str)
                self.assertGreater(len(strategic_goal), 0)
                
                total_processed += 1
        
        print(f"✅ NLP processing simulation completed for {total_processed} records")
    
    def test_scoring_integration(self):
        """Test scoring integration simulation."""
        def calculate_source_weight_simple(record):
            """Calculate source weight based on record."""
            source = record.get('source', '').lower()
            
            if 'internal sales' in source:
                try:
                    arr_impact = float(record.get('ARR_impact_estimate_USD', 0))
                    weight = arr_impact / 50000
                    return max(0.1, weight)
                except (ValueError, TypeError):
                    return 1.0
            
            elif 'twitter' in source:
                try:
                    followers = float(record.get('followers', 0))
                    weight = followers / 20000
                    return max(0.1, weight)
                except (ValueError, TypeError):
                    return 1.0
            
            elif 'app store' in source or 'play' in source:
                try:
                    rating = float(record.get('rating', 0))
                    helpful_votes = float(record.get('helpful_votes', 0))
                    weight = rating + (helpful_votes / 10)
                    return max(0.1, weight)
                except (ValueError, TypeError):
                    return 1.0
            
            else:
                return 1.0
        
        def calculate_impact_score_simple(record, source_weight):
            """Calculate impact score."""
            # Sentiment values
            sentiment_values = {
                'positive': 0.1,
                'neutral': 0.5,
                'negative': 1.5
            }
            
            sentiment = record.get('sentiment', 'neutral').lower()
            sentiment_value = sentiment_values.get(sentiment, 0.5)
            
            try:
                severity = float(record.get('severity', 1.0))
            except (ValueError, TypeError):
                severity = 1.0
            
            # Strategic multiplier
            strategic_goal = record.get('strategic_goal', '')
            aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
            strategic_multiplier = 2.0 if strategic_goal in aligned_goals else 1.0
            
            # Calculate impact score
            impact_score = (sentiment_value * severity) * source_weight * strategic_multiplier
            
            return max(0.0, impact_score)
        
        # Load mock data
        mock_data = MockDataGenerator.create_mock_csv_data()
        
        # Test scoring for each record
        total_scored = 0
        for source_type, records in mock_data.items():
            for record in records:
                # Calculate source weight
                source_weight = calculate_source_weight_simple(record)
                self.assertIsInstance(source_weight, (int, float))
                self.assertGreater(source_weight, 0)
                
                # Calculate impact score
                impact_score = calculate_impact_score_simple(record, source_weight)
                self.assertIsInstance(impact_score, (int, float))
                self.assertGreaterEqual(impact_score, 0)
                
                total_scored += 1
        
        print(f"✅ Scoring integration completed for {total_scored} records")


class TestEndToEndWorkflowSimulation(unittest.TestCase):
    """Test end-to-end workflow simulation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'csv_mock_data')
        self.output_dir = os.path.join(self.temp_dir, 'output')
        
        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create mock CSV files
        self.csv_files = MockDataGenerator.create_csv_files(self.data_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_workflow_simulation(self):
        """Test complete end-to-end workflow simulation."""
        # Step 1: Data Loading
        def load_all_data(data_directory):
            """Load all CSV data from directory."""
            all_data = {}
            
            for filename in os.listdir(data_directory):
                if filename.endswith('.csv'):
                    file_path = os.path.join(data_directory, filename)
                    data = []
                    
                    try:
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                            if len(lines) < 2:
                                continue
                            
                            # Parse header
                            headers = [h.strip() for h in lines[0].strip().split(',')]
                            
                            # Parse data rows
                            for line in lines[1:]:
                                values = [v.strip() for v in line.strip().split(',')]
                                if len(values) == len(headers):
                                    row = dict(zip(headers, values))
                                    data.append(row)
                        
                        if data:
                            all_data[filename] = data
                    
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
            
            return all_data
        
        # Step 2: Data Processing
        def process_all_data(loaded_data):
            """Process all loaded data."""
            processed_records = []
            
            for filename, records in loaded_data.items():
                for record in records:
                    # Normalize data
                    processed_record = record.copy()
                    
                    # Add normalized fields
                    if 'review_text' in record:
                        processed_record['feedback_text'] = record['review_text']
                        processed_record['author_handle'] = record.get('username', '')
                        processed_record['source_channel'] = 'iOS App Store'
                    elif 'tweet_text' in record:
                        processed_record['feedback_text'] = record['tweet_text']
                        processed_record['author_handle'] = record.get('handle', '')
                        processed_record['source_channel'] = 'Twitter (X)'
                    elif 'note_text' in record:
                        processed_record['feedback_text'] = record['note_text']
                        processed_record['author_handle'] = record.get('account_name', '')
                        processed_record['source_channel'] = 'Internal Sales Notes'
                    
                    # Calculate source weight
                    source = record.get('source', '').lower()
                    if 'internal sales' in source:
                        try:
                            arr_impact = float(record.get('ARR_impact_estimate_USD', 0))
                            source_weight = max(0.1, arr_impact / 50000)
                        except (ValueError, TypeError):
                            source_weight = 1.0
                    elif 'twitter' in source:
                        try:
                            followers = float(record.get('followers', 0))
                            source_weight = max(0.1, followers / 20000)
                        except (ValueError, TypeError):
                            source_weight = 1.0
                    else:
                        source_weight = 1.0
                    
                    processed_record['source_weight'] = source_weight
                    
                    # Calculate impact score
                    sentiment_values = {'positive': 0.1, 'neutral': 0.5, 'negative': 1.5}
                    sentiment = record.get('sentiment', 'neutral').lower()
                    sentiment_value = sentiment_values.get(sentiment, 0.5)
                    
                    try:
                        severity = float(record.get('severity', 1.0))
                    except (ValueError, TypeError):
                        severity = 1.0
                    
                    strategic_goal = record.get('strategic_goal', '')
                    aligned_goals = ['Growth', 'Trust&Safety', 'Onchain Adoption', 'CX Efficiency', 'Compliance']
                    strategic_multiplier = 2.0 if strategic_goal in aligned_goals else 1.0
                    
                    impact_score = (sentiment_value * severity) * source_weight * strategic_multiplier
                    processed_record['impact_score'] = max(0.0, impact_score)
                    
                    processed_records.append(processed_record)
            
            return processed_records
        
        # Step 3: Report Generation
        def generate_report_summary(processed_records):
            """Generate report summary."""
            if not processed_records:
                return {}
            
            # Calculate summary statistics
            total_records = len(processed_records)
            
            # Sentiment distribution
            sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
            for record in processed_records:
                sentiment = record.get('sentiment', 'neutral').lower()
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1
            
            # Top themes by impact
            theme_impacts = {}
            for record in processed_records:
                theme = record.get('theme', 'General Feedback')
                impact = record.get('impact_score', 0)
                if theme not in theme_impacts:
                    theme_impacts[theme] = []
                theme_impacts[theme].append(impact)
            
            # Calculate theme totals
            theme_totals = {}
            for theme, impacts in theme_impacts.items():
                theme_totals[theme] = sum(impacts)
            
            # Sort themes by total impact
            top_themes = sorted(theme_totals.items(), key=lambda x: x[1], reverse=True)
            
            return {
                'total_records': total_records,
                'sentiment_distribution': sentiment_counts,
                'top_themes': top_themes[:3],
                'total_impact': sum(record.get('impact_score', 0) for record in processed_records)
            }
        
        # Execute complete workflow
        print("🚀 Starting end-to-end workflow simulation...")
        
        # Step 1: Load data
        loaded_data = load_all_data(self.data_dir)
        self.assertGreater(len(loaded_data), 0, "Should load data files")
        print(f"✅ Step 1: Loaded {len(loaded_data)} data files")
        
        # Step 2: Process data
        processed_records = process_all_data(loaded_data)
        self.assertGreater(len(processed_records), 0, "Should process records")
        print(f"✅ Step 2: Processed {len(processed_records)} records")
        
        # Verify processed records have required fields
        for record in processed_records:
            self.assertIn('feedback_text', record)
            self.assertIn('author_handle', record)
            self.assertIn('source_channel', record)
            self.assertIn('source_weight', record)
            self.assertIn('impact_score', record)
        
        # Step 3: Generate report
        report_summary = generate_report_summary(processed_records)
        self.assertIn('total_records', report_summary)
        self.assertIn('sentiment_distribution', report_summary)
        self.assertIn('top_themes', report_summary)
        print(f"✅ Step 3: Generated report summary")
        
        # Step 4: Save results
        output_file = os.path.join(self.output_dir, 'workflow_results.json')
        with open(output_file, 'w') as f:
            json.dump(report_summary, f, indent=2)
        
        self.assertTrue(os.path.exists(output_file), "Should create output file")
        print(f"✅ Step 4: Saved results to {output_file}")
        
        # Verify final results
        self.assertEqual(report_summary['total_records'], len(processed_records))
        self.assertGreater(report_summary['total_impact'], 0)
        
        print("🎉 End-to-end workflow simulation completed successfully!")
        print(f"   Total Records: {report_summary['total_records']}")
        print(f"   Total Impact: {report_summary['total_impact']:.2f}")
        print(f"   Sentiment Distribution: {report_summary['sentiment_distribution']}")


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling in integration scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_missing_data_directory_handling(self):
        """Test handling of missing data directory."""
        def load_data_safe(data_directory):
            """Safely load data with error handling."""
            try:
                if not os.path.exists(data_directory):
                    return {}, "Directory does not exist"
                
                if not os.path.isdir(data_directory):
                    return {}, "Path is not a directory"
                
                files = os.listdir(data_directory)
                csv_files = [f for f in files if f.endswith('.csv')]
                
                if not csv_files:
                    return {}, "No CSV files found"
                
                return {'status': 'success', 'files': csv_files}, "Success"
                
            except Exception as e:
                return {}, f"Error: {e}"
        
        # Test with nonexistent directory
        nonexistent_dir = os.path.join(self.temp_dir, 'nonexistent')
        result, message = load_data_safe(nonexistent_dir)
        
        self.assertEqual(result, {})
        self.assertIn("does not exist", message)
        
        # Test with empty directory
        empty_dir = os.path.join(self.temp_dir, 'empty')
        os.makedirs(empty_dir)
        result, message = load_data_safe(empty_dir)
        
        self.assertEqual(result, {})
        self.assertIn("No CSV files", message)
        
        print("✅ Missing data directory handling tested")
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted data."""
        def process_record_safe(record):
            """Safely process record with error handling."""
            try:
                # Validate required fields
                required_fields = ['customer_id', 'source', 'timestamp']
                for field in required_fields:
                    if field not in record or not record[field]:
                        return None, f"Missing required field: {field}"
                
                # Validate data types
                try:
                    if 'rating' in record and record['rating']:
                        rating = float(record['rating'])
                        if rating < 1 or rating > 5:
                            return None, "Invalid rating range"
                except (ValueError, TypeError):
                    return None, "Invalid rating format"
                
                # Process successfully
                processed = record.copy()
                processed['processed'] = True
                
                return processed, "Success"
                
            except Exception as e:
                return None, f"Processing error: {e}"
        
        # Test with valid record
        valid_record = {
            'customer_id': 'TEST-001',
            'source': 'Test Source',
            'timestamp': '2024-01-01 10:00:00',
            'rating': '4'
        }
        
        result, message = process_record_safe(valid_record)
        self.assertIsNotNone(result)
        self.assertEqual(message, "Success")
        
        # Test with missing required field
        invalid_record = {
            'source': 'Test Source',
            'timestamp': '2024-01-01 10:00:00'
            # Missing customer_id
        }
        
        result, message = process_record_safe(invalid_record)
        self.assertIsNone(result)
        self.assertIn("Missing required field", message)
        
        # Test with invalid rating
        invalid_rating_record = {
            'customer_id': 'TEST-001',
            'source': 'Test Source',
            'timestamp': '2024-01-01 10:00:00',
            'rating': 'invalid'
        }
        
        result, message = process_record_safe(invalid_rating_record)
        self.assertIsNone(result)
        self.assertIn("Invalid rating", message)
        
        print("✅ Corrupted data handling tested")


if __name__ == '__main__':
    # Run all integration tests
    unittest.main(verbosity=2)