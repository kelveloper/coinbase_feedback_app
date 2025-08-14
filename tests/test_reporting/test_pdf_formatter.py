"""
Unit tests for pdf_formatter module.

Tests cover PDF document creation, section formatting, and error handling.
"""

import unittest
import pandas as pd
import os
import tempfile
import sys
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from reporting.pdf_formatter import (
    ReportPDF,
    create_pdf_document,
    add_header_section,
    add_executive_summary,
    add_pain_points_section,
    add_praised_features_section,
    add_strategic_insights_section,
    add_theme_analysis_section,
    create_pdf_report
)


class TestPDFFormatter(unittest.TestCase):
    """Test cases for PDF formatter functions."""
    
    def setUp(self):
        """Set up test data for each test."""
        # Sample report content
        self.sample_report_content = {
            'executive_summary': {
                'total_feedback_items': 100,
                'unique_customers': 85,
                'sentiment_distribution': {'positive': 30, 'negative': 40, 'neutral': 30},
                'sentiment_percentages': {'positive': 30.0, 'negative': 40.0, 'neutral': 30.0},
                'impact_metrics': {
                    'total_impact': 250.5,
                    'average_impact': 2.5,
                    'maximum_impact': 15.2
                },
                'top_theme': {
                    'name': 'Performance/Outages',
                    'total_impact': 85.3
                },
                'source_distribution': {'iOS App Store': 40, 'Twitter': 35, 'Internal Sales': 25}
            },
            'top_pain_points': [
                {
                    'theme': 'Performance/Outages',
                    'impact_score': 15.2,
                    'feedback_text': 'App crashes frequently during high volume trading sessions',
                    'source_channel': 'iOS App Store',
                    'strategic_goal': 'Trust&Safety',
                    'severity': 2.5
                },
                {
                    'theme': 'Trading/Execution & Fees',
                    'impact_score': 12.8,
                    'feedback_text': 'Order execution delays causing missed opportunities',
                    'source_channel': 'Twitter',
                    'strategic_goal': 'Growth',
                    'severity': 2.0
                }
            ],
            'praised_features': [
                {
                    'theme': 'UI/UX',
                    'impact_score': 8.5,
                    'feedback_text': 'Love the new charting interface, very intuitive',
                    'source_channel': 'Google Play',
                    'strategic_goal': 'Growth',
                    'severity': 1.0
                }
            ],
            'strategic_insights': {
                'Trust&Safety': {
                    'total_impact': 45.2,
                    'avg_impact': 3.2,
                    'feedback_count': 14,
                    'sentiment_breakdown': {'negative': 8, 'positive': 3, 'neutral': 3},
                    'top_feedback': {
                        'theme': 'Performance/Outages',
                        'impact_score': 15.2,
                        'feedback_text': 'App crashes frequently',
                        'sentiment': 'negative'
                    }
                },
                'Growth': {
                    'total_impact': 38.7,
                    'avg_impact': 2.8,
                    'feedback_count': 14,
                    'sentiment_breakdown': {'negative': 5, 'positive': 6, 'neutral': 3},
                    'top_feedback': {
                        'theme': 'Trading/Execution & Fees',
                        'impact_score': 12.8,
                        'feedback_text': 'Order execution delays',
                        'sentiment': 'negative'
                    }
                }
            },
            'theme_analysis': [
                {
                    'theme': 'Performance/Outages',
                    'total_impact': 85.3,
                    'avg_impact': 4.2,
                    'feedback_count': 20,
                    'negative_count': 15,
                    'unique_customers': 18
                },
                {
                    'theme': 'Trading/Execution & Fees',
                    'total_impact': 72.1,
                    'avg_impact': 3.8,
                    'feedback_count': 19,
                    'negative_count': 12,
                    'unique_customers': 17
                }
            ],
            'metadata': {
                'generated_at': '2024-01-15 10:30:00',
                'total_records_processed': 100,
                'content_sections': ['executive_summary', 'theme_analysis', 'pain_points', 'praised_features', 'strategic_insights']
            }
        }
        
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.test_output_path = os.path.join(self.temp_dir, 'test_report.pdf')
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_output_path):
            os.remove(self.test_output_path)
        os.rmdir(self.temp_dir)
    
    def test_create_pdf_document(self):
        """Test PDF document creation."""
        pdf = create_pdf_document("Test Report")
        
        # Check that PDF object is created
        self.assertIsInstance(pdf, ReportPDF)
        self.assertEqual(pdf.report_title, "Test Report")
        
        # Check that page is added
        self.assertEqual(pdf.page_no(), 1)
    
    def test_report_pdf_class(self):
        """Test custom ReportPDF class functionality."""
        pdf = ReportPDF("Custom Title")
        
        # Test initialization
        self.assertEqual(pdf.report_title, "Custom Title")
        
        # Test that header and footer methods exist
        self.assertTrue(hasattr(pdf, 'header'))
        self.assertTrue(hasattr(pdf, 'footer'))
    
    def test_add_header_section(self):
        """Test adding header section to PDF."""
        pdf = create_pdf_document()
        
        # Should not raise exception
        try:
            add_header_section(pdf, self.sample_report_content)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_executive_summary(self):
        """Test adding executive summary section."""
        pdf = create_pdf_document()
        executive_summary = self.sample_report_content['executive_summary']
        
        # Should not raise exception
        try:
            add_executive_summary(pdf, executive_summary)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_pain_points_section(self):
        """Test adding pain points section."""
        pdf = create_pdf_document()
        pain_points = self.sample_report_content['top_pain_points']
        
        # Should not raise exception
        try:
            add_pain_points_section(pdf, pain_points)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_pain_points_section_empty(self):
        """Test adding pain points section with empty data."""
        pdf = create_pdf_document()
        
        # Should handle empty list gracefully
        try:
            add_pain_points_section(pdf, [])
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_praised_features_section(self):
        """Test adding praised features section."""
        pdf = create_pdf_document()
        praised_features = self.sample_report_content['praised_features']
        
        # Should not raise exception
        try:
            add_praised_features_section(pdf, praised_features)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_praised_features_section_empty(self):
        """Test adding praised features section with empty data."""
        pdf = create_pdf_document()
        
        # Should handle empty list gracefully
        try:
            add_praised_features_section(pdf, [])
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_strategic_insights_section(self):
        """Test adding strategic insights section."""
        pdf = create_pdf_document()
        strategic_insights = self.sample_report_content['strategic_insights']
        
        # Should not raise exception
        try:
            add_strategic_insights_section(pdf, strategic_insights)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_strategic_insights_section_empty(self):
        """Test adding strategic insights section with empty data."""
        pdf = create_pdf_document()
        
        # Should handle empty dict gracefully
        try:
            add_strategic_insights_section(pdf, {})
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_theme_analysis_section(self):
        """Test adding theme analysis section."""
        pdf = create_pdf_document()
        theme_analysis = self.sample_report_content['theme_analysis']
        
        # Should not raise exception
        try:
            add_theme_analysis_section(pdf, theme_analysis)
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_add_theme_analysis_section_empty(self):
        """Test adding theme analysis section with empty data."""
        pdf = create_pdf_document()
        
        # Should handle empty list gracefully
        try:
            add_theme_analysis_section(pdf, [])
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)
    
    def test_create_pdf_report_success(self):
        """Test successful PDF report creation."""
        result = create_pdf_report(self.sample_report_content, self.test_output_path)
        
        # Should return True for success
        self.assertTrue(result)
        
        # Should create the file
        self.assertTrue(os.path.exists(self.test_output_path))
        
        # File should have content (not empty)
        self.assertGreater(os.path.getsize(self.test_output_path), 0)
    
    def test_create_pdf_report_empty_content(self):
        """Test PDF report creation with minimal content."""
        minimal_content = {
            'executive_summary': {},
            'top_pain_points': [],
            'praised_features': [],
            'strategic_insights': {},
            'theme_analysis': [],
            'metadata': {'generated_at': '2024-01-15 10:30:00', 'total_records_processed': 0}
        }
        
        result = create_pdf_report(minimal_content, self.test_output_path)
        
        # Should still succeed with empty content
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_output_path))
    
    def test_create_pdf_report_directory_creation(self):
        """Test PDF report creation with non-existent directory."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'directory', 'report.pdf')
        
        result = create_pdf_report(self.sample_report_content, nested_path)
        
        # Should create directory and file
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_path))
    
    @patch('src.reporting.pdf_formatter.ReportPDF')
    def test_create_pdf_report_error_handling(self, mock_pdf_class):
        """Test error handling in PDF report creation."""
        # Mock PDF class to raise exception
        mock_pdf_class.side_effect = Exception("PDF creation failed")
        
        result = create_pdf_report(self.sample_report_content, self.test_output_path)
        
        # Should return False on error
        self.assertFalse(result)
    
    def test_long_text_handling(self):
        """Test handling of long feedback text in sections."""
        # Create content with very long feedback text
        long_text_content = self.sample_report_content.copy()
        long_text_content['top_pain_points'] = [{
            'theme': 'Test Theme',
            'impact_score': 10.0,
            'feedback_text': 'A' * 500,  # Very long text
            'source_channel': 'Test Source',
            'strategic_goal': 'Test Goal',
            'severity': 2.0
        }]
        
        result = create_pdf_report(long_text_content, self.test_output_path)
        
        # Should handle long text without errors
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_output_path))
    
    def test_missing_optional_fields(self):
        """Test handling of missing optional fields in content."""
        minimal_pain_point = {
            'theme': 'Test Theme',
            'impact_score': 5.0
            # Missing optional fields like feedback_text, source_channel, etc.
        }
        
        pdf = create_pdf_document()
        
        # Should handle missing fields gracefully
        try:
            add_pain_points_section(pdf, [minimal_pain_point])
            success = True
        except Exception:
            success = False
        
        self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()