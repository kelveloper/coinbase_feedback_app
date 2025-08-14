"""
Integration tests for report_generator module.

Tests cover end-to-end report generation workflow, content orchestration,
PDF creation, and error handling scenarios.
"""

import unittest
import pandas as pd
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from reporting.report_generator import (
    validate_report_data,
    generate_report_content,
    create_pdf_report,
    generate_complete_report,
    get_report_summary
)


class TestReportGenerator(unittest.TestCase):
    """Test cases for report generator functions."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Create comprehensive sample data
        self.sample_data = pd.DataFrame({
            'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008'],
            'source_channel': ['iOS App Store', 'Twitter', 'Internal Sales', 'Google Play', 'iOS App Store', 'Twitter', 'Internal Sales', 'Google Play'],
            'feedback_text': [
                'App crashes frequently during trading sessions',
                'Love the new interface design and features',
                'Customer wants advanced order types for institutional trading',
                'Slow loading times are very frustrating during market hours',
                'Great customer support experience, very helpful team',
                'Need better mobile notifications for price alerts',
                'Request for API improvements and better documentation',
                'Excellent charting tools, very professional interface'
            ],
            'theme': ['Performance/Outages', 'UI/UX', 'Trading/Execution & Fees', 'Performance/Outages', 'Support Experience', 'Mobile Features', 'API/Integration', 'UI/UX'],
            'sentiment': ['negative', 'positive', 'neutral', 'negative', 'positive', 'negative', 'neutral', 'positive'],
            'strategic_goal': ['Trust&Safety', 'Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth', 'Growth', 'Growth'],
            'severity': [2.5, 1.0, 1.8, 3.0, 1.0, 2.0, 1.5, 1.0],
            'impact_score': [18.7, 8.2, 12.3, 22.5, 6.1, 14.2, 10.8, 9.5],
            'source_weight': [2.5, 1.8, 3.2, 2.1, 2.5, 1.8, 3.0, 2.1],
            'timestamp': [
                datetime.now() - timedelta(days=i) for i in range(8)
            ]
        })
        
        # Create minimal valid data
        self.minimal_data = pd.DataFrame({
            'theme': ['Theme1', 'Theme2'],
            'sentiment': ['positive', 'negative'],
            'impact_score': [5.0, 10.0]
        })
        
        # Create invalid data scenarios
        self.empty_data = pd.DataFrame()
        
        self.missing_columns_data = pd.DataFrame({
            'theme': ['Theme1'],
            'sentiment': ['positive']
            # Missing impact_score
        })
        
        self.invalid_sentiment_data = pd.DataFrame({
            'theme': ['Theme1'],
            'sentiment': ['invalid_sentiment'],
            'impact_score': [5.0]
        })
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_path = os.path.join(self.temp_dir, 'test_report.pdf')
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_output_path):
            os.remove(self.test_output_path)
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass  # Directory might not be empty due to other test files
    
    def test_validate_report_data_success(self):
        """Test successful data validation."""
        is_valid, message = validate_report_data(self.sample_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Data validation successful")
    
    def test_validate_report_data_empty(self):
        """Test validation with empty DataFrame."""
        is_valid, message = validate_report_data(self.empty_data)
        
        self.assertFalse(is_valid)
        self.assertIn("empty", message.lower())
    
    def test_validate_report_data_missing_columns(self):
        """Test validation with missing required columns."""
        is_valid, message = validate_report_data(self.missing_columns_data)
        
        self.assertFalse(is_valid)
        self.assertIn("missing required columns", message.lower())
        self.assertIn("impact_score", message)
    
    def test_validate_report_data_minimal_valid(self):
        """Test validation with minimal valid data."""
        is_valid, message = validate_report_data(self.minimal_data)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Data validation successful")
    
    def test_generate_report_content_success(self):
        """Test successful report content generation."""
        content = generate_report_content(self.sample_data, top_n=2)
        
        # Should not contain error
        self.assertNotIn('error', content)
        
        # Should contain expected sections
        expected_sections = ['executive_summary', 'theme_analysis', 'top_pain_points', 'praised_features', 'strategic_insights', 'metadata']
        for section in expected_sections:
            self.assertIn(section, content)
        
        # Check metadata
        metadata = content['metadata']
        self.assertIn('generation_status', metadata)
        self.assertEqual(metadata['generation_status'], 'success')
        self.assertEqual(metadata['total_records_processed'], 8)
        self.assertEqual(metadata['top_n_items'], 2)
    
    def test_generate_report_content_invalid_data(self):
        """Test report content generation with invalid data."""
        content = generate_report_content(self.empty_data)
        
        # Should contain error
        self.assertIn('error', content)
        
        # Should have metadata with failure status
        metadata = content['metadata']
        self.assertEqual(metadata['status'], 'failed')
        self.assertEqual(metadata['total_records_processed'], 0)
    
    def test_generate_report_content_minimal_data(self):
        """Test report content generation with minimal valid data."""
        content = generate_report_content(self.minimal_data, top_n=1)
        
        # Should not contain error
        self.assertNotIn('error', content)
        
        # Should contain basic sections
        self.assertIn('executive_summary', content)
        self.assertIn('metadata', content)
        
        # Check that it handles minimal data gracefully
        metadata = content['metadata']
        self.assertEqual(metadata['generation_status'], 'success')
    
    def test_create_pdf_report_success(self):
        """Test successful PDF report creation."""
        # Generate content first
        content = generate_report_content(self.sample_data)
        
        # Create PDF
        success, message = create_pdf_report(content, self.test_output_path)
        
        self.assertTrue(success)
        self.assertIn("successfully created", message.lower())
        self.assertTrue(os.path.exists(self.test_output_path))
        self.assertGreater(os.path.getsize(self.test_output_path), 0)
    
    def test_create_pdf_report_failed_content(self):
        """Test PDF creation with failed content generation."""
        failed_content = {
            'error': 'Content generation failed',
            'metadata': {'status': 'failed'}
        }
        
        success, message = create_pdf_report(failed_content, self.test_output_path)
        
        self.assertFalse(success)
        self.assertIn("failed content generation", message.lower())
    
    def test_create_pdf_report_directory_creation(self):
        """Test PDF creation with non-existent directory."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'directory', 'report.pdf')
        content = generate_report_content(self.sample_data)
        
        success, message = create_pdf_report(content, nested_path)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_path))
    
    def test_generate_complete_report_success(self):
        """Test successful end-to-end report generation."""
        results = generate_complete_report(self.sample_data, self.test_output_path, top_n=2)
        
        # Check results structure
        self.assertTrue(results['success'])
        self.assertTrue(results['content_generated'])
        self.assertTrue(results['pdf_created'])
        self.assertEqual(results['output_path'], self.test_output_path)
        self.assertIn('report_content', results)
        self.assertIn('metadata', results)
        
        # Check file was created
        self.assertTrue(os.path.exists(self.test_output_path))
        self.assertGreater(os.path.getsize(self.test_output_path), 0)
        
        # Check report content structure
        report_content = results['report_content']
        self.assertIn('executive_summary', report_content)
        self.assertIn('top_pain_points', report_content)
        self.assertIn('praised_features', report_content)
    
    def test_generate_complete_report_invalid_data(self):
        """Test complete report generation with invalid data."""
        results = generate_complete_report(self.empty_data, self.test_output_path)
        
        # Check failure results
        self.assertFalse(results['success'])
        self.assertFalse(results['content_generated'])
        self.assertFalse(results['pdf_created'])
        self.assertIn('error', results)
        
        # File should not be created
        self.assertFalse(os.path.exists(self.test_output_path))
    
    def test_generate_complete_report_minimal_data(self):
        """Test complete report generation with minimal data."""
        results = generate_complete_report(self.minimal_data, self.test_output_path, top_n=1)
        
        # Should succeed with minimal data
        self.assertTrue(results['success'])
        self.assertTrue(results['content_generated'])
        self.assertTrue(results['pdf_created'])
        
        # File should be created
        self.assertTrue(os.path.exists(self.test_output_path))
    
    @patch('src.reporting.report_generator.create_pdf_file')
    def test_generate_complete_report_pdf_failure(self, mock_create_pdf):
        """Test complete report generation with PDF creation failure."""
        # Mock PDF creation to fail
        mock_create_pdf.return_value = False
        
        results = generate_complete_report(self.sample_data, self.test_output_path)
        
        # Content should be generated but PDF should fail
        self.assertFalse(results['success'])
        self.assertTrue(results['content_generated'])
        self.assertFalse(results['pdf_created'])
        self.assertIn('error', results)
    
    def test_get_report_summary_success(self):
        """Test report summary generation for successful results."""
        results = generate_complete_report(self.sample_data, self.test_output_path)
        summary = get_report_summary(results)
        
        self.assertIn("SUCCESS", summary)
        self.assertIn(self.test_output_path, summary)
        self.assertIn("Records Processed: 8", summary)
        self.assertIn("✓", summary)  # Success indicators
    
    def test_get_report_summary_failure(self):
        """Test report summary generation for failed results."""
        results = generate_complete_report(self.empty_data, self.test_output_path)
        summary = get_report_summary(results)
        
        self.assertIn("FAILED", summary)
        self.assertIn("✗", summary)  # Failure indicators
        self.assertIn("Content Generated: False", summary)
        self.assertIn("PDF Created: False", summary)
    
    def test_error_handling_with_none_dataframe(self):
        """Test error handling when DataFrame is None."""
        try:
            results = generate_complete_report(None, self.test_output_path)
            
            # Should handle gracefully
            self.assertFalse(results['success'])
            self.assertIn('error', results)
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            self.fail(f"Should handle None DataFrame gracefully, but raised: {e}")
    
    def test_content_validation_edge_cases(self):
        """Test content validation with various edge cases."""
        # Test with non-numeric impact scores
        invalid_numeric_data = pd.DataFrame({
            'theme': ['Theme1'],
            'sentiment': ['positive'],
            'impact_score': ['not_a_number']
        })
        
        is_valid, message = validate_report_data(invalid_numeric_data)
        self.assertFalse(is_valid)
        self.assertIn("numeric", message.lower())
    
    def test_report_content_with_custom_top_n(self):
        """Test report content generation with different top_n values."""
        # Test with top_n=1
        content_1 = generate_report_content(self.sample_data, top_n=1)
        
        # Test with top_n=5 (more than available items in some categories)
        content_5 = generate_report_content(self.sample_data, top_n=5)
        
        # Both should succeed
        self.assertNotIn('error', content_1)
        self.assertNotIn('error', content_5)
        
        # Check that top_n is respected in metadata
        self.assertEqual(content_1['metadata']['top_n_items'], 1)
        self.assertEqual(content_5['metadata']['top_n_items'], 5)


if __name__ == '__main__':
    unittest.main()