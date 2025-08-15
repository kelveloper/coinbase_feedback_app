"""
Unit tests for pdf_formatter module.

Tests cover PDF document creation, formatting, styling, and content layout
functionality for report generation.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from reporting.pdf_formatter import (
    create_pdf_document,
    add_header_section,
    add_executive_summary_section,
    add_pain_points_section,
    add_praised_features_section,
    add_theme_analysis_section,
    add_strategic_insights_section,
    add_footer_section,
    create_pdf_file
)


class TestCreatePdfDocument(unittest.TestCase):
    """Test cases for create_pdf_document function."""
    
    def test_create_pdf_document_basic(self):
        """Test basic PDF document creation."""
        pdf = create_pdf_document()
        
        # Should return FPDF object
        self.assertIsNotNone(pdf)
        
        # Check basic properties
        self.assertEqual(pdf.format, 'A4')
        self.assertEqual(pdf.unit, 'mm')
    
    def test_create_pdf_document_with_title(self):
        """Test PDF document creation with custom title."""
        title = "Custom Report Title"
        pdf = create_pdf_document(title=title)
        
        self.assertIsNotNone(pdf)
        # Title should be set in metadata
        self.assertEqual(pdf.title, title)


class TestAddHeaderSection(unittest.TestCase):
    """Test cases for add_header_section function."""
    
    def setUp(self):
        """Set up test PDF document."""
        self.pdf = create_pdf_document()
    
    def test_add_header_section_basic(self):
        """Test adding basic header section."""
        add_header_section(self.pdf, "Test Report Title")
        
        # Should add a page
        self.assertEqual(self.pdf.page_no(), 1)
    
    def test_add_header_section_with_subtitle(self):
        """Test adding header section with subtitle."""
        add_header_section(self.pdf, "Main Title", "Subtitle Text")
        
        # Should add content to the page
        self.assertEqual(self.pdf.page_no(), 1)
    
    def test_add_header_section_empty_title(self):
        """Test adding header section with empty title."""
        add_header_section(self.pdf, "")
        
        # Should handle empty title gracefully
        self.assertEqual(self.pdf.page_no(), 1)


class TestAddExecutiveSummarySection(unittest.TestCase):
    """Test cases for add_executive_summary_section function."""
    
    def setUp(self):
        """Set up test data and PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
        
        self.executive_summary = {
            'total_feedback_items': 150,
            'average_sentiment_score': 2.3,
            'top_theme_by_impact': 'Performance Issues',
            'total_impact_score': 245.7,
            'sentiment_distribution': {
                'positive': 45,
                'neutral': 60,
                'negative': 45
            },
            'time_period': '2024-01-01 to 2024-01-31'
        }
    
    def test_add_executive_summary_section_complete(self):
        """Test adding complete executive summary section."""
        add_executive_summary_section(self.pdf, self.executive_summary)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_executive_summary_section_minimal(self):
        """Test adding executive summary with minimal data."""
        minimal_summary = {
            'total_feedback_items': 10,
            'average_sentiment_score': 1.5,
            'top_theme_by_impact': 'General',
            'total_impact_score': 25.0
        }
        
        add_executive_summary_section(self.pdf, minimal_summary)
        
        # Should handle minimal data
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_executive_summary_section_empty(self):
        """Test adding executive summary with empty data."""
        empty_summary = {}
        
        # Should handle empty data gracefully
        add_executive_summary_section(self.pdf, empty_summary)
        self.assertGreater(self.pdf.page_no(), 0)


class TestAddPainPointsSection(unittest.TestCase):
    """Test cases for add_pain_points_section function."""
    
    def setUp(self):
        """Set up test data and PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
        
        self.pain_points = [
            {
                'feedback_text': 'App crashes frequently during peak trading hours',
                'theme': 'Performance Issues',
                'impact_score': 8.7,
                'source_channel': 'iOS App Store',
                'customer_id': 'C001'
            },
            {
                'feedback_text': 'Login process is extremely slow and unreliable',
                'theme': 'Authentication',
                'impact_score': 7.2,
                'source_channel': 'Google Play Store',
                'customer_id': 'C002'
            },
            {
                'feedback_text': 'Charts not loading properly on mobile devices',
                'theme': 'Mobile Experience',
                'impact_score': 6.8,
                'source_channel': 'Twitter',
                'customer_id': 'C003'
            }
        ]
    
    def test_add_pain_points_section_complete(self):
        """Test adding complete pain points section."""
        add_pain_points_section(self.pdf, self.pain_points)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_pain_points_section_empty(self):
        """Test adding pain points section with empty list."""
        add_pain_points_section(self.pdf, [])
        
        # Should handle empty list gracefully
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_pain_points_section_single_item(self):
        """Test adding pain points section with single item."""
        single_pain_point = [self.pain_points[0]]
        
        add_pain_points_section(self.pdf, single_pain_point)
        
        # Should handle single item
        self.assertGreater(self.pdf.page_no(), 0)


class TestAddPraisedFeaturesSection(unittest.TestCase):
    """Test cases for add_praised_features_section function."""
    
    def setUp(self):
        """Set up test data and PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
        
        self.praised_features = [
            {
                'feedback_text': 'Love the new charting interface, very intuitive',
                'theme': 'UI/UX Improvements',
                'impact_score': 6.5,
                'source_channel': 'iOS App Store',
                'customer_id': 'C004'
            },
            {
                'feedback_text': 'Excellent customer support, very responsive team',
                'theme': 'Customer Support',
                'impact_score': 5.8,
                'source_channel': 'Internal Sales Notes',
                'customer_id': 'C005'
            }
        ]
    
    def test_add_praised_features_section_complete(self):
        """Test adding complete praised features section."""
        add_praised_features_section(self.pdf, self.praised_features)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_praised_features_section_empty(self):
        """Test adding praised features section with empty list."""
        add_praised_features_section(self.pdf, [])
        
        # Should handle empty list gracefully
        self.assertGreater(self.pdf.page_no(), 0)


class TestAddThemeAnalysisSection(unittest.TestCase):
    """Test cases for add_theme_analysis_section function."""
    
    def setUp(self):
        """Set up test data and PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
        
        self.theme_analysis = {
            'Performance Issues': {
                'feedback_count': 25,
                'total_impact': 187.5,
                'average_impact': 7.5,
                'sentiment_breakdown': {'negative': 20, 'neutral': 3, 'positive': 2}
            },
            'UI/UX Improvements': {
                'feedback_count': 18,
                'total_impact': 98.4,
                'average_impact': 5.5,
                'sentiment_breakdown': {'positive': 15, 'neutral': 2, 'negative': 1}
            },
            'Customer Support': {
                'feedback_count': 12,
                'total_impact': 67.2,
                'average_impact': 5.6,
                'sentiment_breakdown': {'positive': 8, 'neutral': 3, 'negative': 1}
            }
        }
    
    def test_add_theme_analysis_section_complete(self):
        """Test adding complete theme analysis section."""
        add_theme_analysis_section(self.pdf, self.theme_analysis)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_theme_analysis_section_empty(self):
        """Test adding theme analysis section with empty data."""
        add_theme_analysis_section(self.pdf, {})
        
        # Should handle empty data gracefully
        self.assertGreater(self.pdf.page_no(), 0)


class TestAddStrategicInsightsSection(unittest.TestCase):
    """Test cases for add_strategic_insights_section function."""
    
    def setUp(self):
        """Set up test data and PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
        
        self.strategic_insights = {
            'Growth': {
                'feedback_count': 45,
                'total_impact': 234.7,
                'average_impact': 5.2,
                'sentiment_breakdown': {'positive': 25, 'neutral': 12, 'negative': 8},
                'top_themes': ['UI/UX', 'Features', 'Performance']
            },
            'Trust&Safety': {
                'feedback_count': 32,
                'total_impact': 198.4,
                'average_impact': 6.2,
                'sentiment_breakdown': {'negative': 20, 'neutral': 8, 'positive': 4},
                'top_themes': ['Security', 'Performance', 'Authentication']
            }
        }
    
    def test_add_strategic_insights_section_complete(self):
        """Test adding complete strategic insights section."""
        add_strategic_insights_section(self.pdf, self.strategic_insights)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_strategic_insights_section_empty(self):
        """Test adding strategic insights section with empty data."""
        add_strategic_insights_section(self.pdf, {})
        
        # Should handle empty data gracefully
        self.assertGreater(self.pdf.page_no(), 0)


class TestAddFooterSection(unittest.TestCase):
    """Test cases for add_footer_section function."""
    
    def setUp(self):
        """Set up test PDF."""
        self.pdf = create_pdf_document()
        self.pdf.add_page()
    
    def test_add_footer_section_basic(self):
        """Test adding basic footer section."""
        add_footer_section(self.pdf)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)
    
    def test_add_footer_section_with_metadata(self):
        """Test adding footer section with metadata."""
        metadata = {
            'generation_timestamp': '2024-01-15 10:30:00',
            'total_records_processed': 150,
            'data_sources': ['iOS App Store', 'Google Play', 'Twitter', 'Internal Sales']
        }
        
        add_footer_section(self.pdf, metadata)
        
        # Should add content without errors
        self.assertGreater(self.pdf.page_no(), 0)


class TestCreatePdfFile(unittest.TestCase):
    """Test cases for create_pdf_file function."""
    
    def setUp(self):
        """Set up test data and temporary file."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file_path = os.path.join(self.temp_dir, 'test_report.pdf')
        
        self.report_content = {
            'executive_summary': {
                'total_feedback_items': 100,
                'average_sentiment_score': 2.1,
                'top_theme_by_impact': 'Performance',
                'total_impact_score': 456.7
            },
            'top_pain_points': [
                {
                    'feedback_text': 'App crashes frequently',
                    'theme': 'Performance',
                    'impact_score': 8.5,
                    'source_channel': 'iOS App Store'
                }
            ],
            'praised_features': [
                {
                    'feedback_text': 'Great new features',
                    'theme': 'Features',
                    'impact_score': 6.2,
                    'source_channel': 'Twitter'
                }
            ],
            'theme_analysis': {
                'Performance': {
                    'feedback_count': 30,
                    'total_impact': 245.6,
                    'average_impact': 8.2
                }
            },
            'strategic_insights': {
                'Growth': {
                    'feedback_count': 50,
                    'total_impact': 300.5,
                    'average_impact': 6.0
                }
            },
            'metadata': {
                'generation_timestamp': '2024-01-15 10:30:00',
                'total_records_processed': 100
            }
        }
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
        os.rmdir(self.temp_dir)
    
    def test_create_pdf_file_success(self):
        """Test successful PDF file creation."""
        success = create_pdf_file(self.report_content, self.test_file_path)
        
        # Should succeed
        self.assertTrue(success)
        
        # File should be created
        self.assertTrue(os.path.exists(self.test_file_path))
        
        # File should have content
        self.assertGreater(os.path.getsize(self.test_file_path), 0)
    
    def test_create_pdf_file_directory_creation(self):
        """Test PDF file creation with non-existent directory."""
        nested_path = os.path.join(self.temp_dir, 'nested', 'directory', 'report.pdf')
        
        success = create_pdf_file(self.report_content, nested_path)
        
        # Should succeed and create directories
        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_path))
    
    def test_create_pdf_file_minimal_content(self):
        """Test PDF file creation with minimal content."""
        minimal_content = {
            'executive_summary': {},
            'top_pain_points': [],
            'praised_features': [],
            'theme_analysis': {},
            'strategic_insights': {},
            'metadata': {}
        }
        
        success = create_pdf_file(minimal_content, self.test_file_path)
        
        # Should handle minimal content
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file_path))
    
    def test_create_pdf_file_missing_sections(self):
        """Test PDF file creation with missing sections."""
        incomplete_content = {
            'executive_summary': {'total_feedback_items': 50}
            # Missing other sections
        }
        
        success = create_pdf_file(incomplete_content, self.test_file_path)
        
        # Should handle missing sections gracefully
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file_path))
    
    @patch('reporting.pdf_formatter.create_pdf_document')
    def test_create_pdf_file_pdf_creation_error(self, mock_create_pdf):
        """Test PDF file creation when PDF creation fails."""
        # Mock PDF creation to raise exception
        mock_create_pdf.side_effect = Exception("PDF creation failed")
        
        success = create_pdf_file(self.report_content, self.test_file_path)
        
        # Should handle error gracefully
        self.assertFalse(success)
        self.assertFalse(os.path.exists(self.test_file_path))
    
    def test_create_pdf_file_invalid_path(self):
        """Test PDF file creation with invalid file path."""
        # Use invalid path (directory that can't be created)
        invalid_path = '/invalid/path/that/cannot/be/created/report.pdf'
        
        success = create_pdf_file(self.report_content, invalid_path)
        
        # Should handle invalid path gracefully
        self.assertFalse(success)
    
    def test_create_pdf_file_empty_content(self):
        """Test PDF file creation with empty content."""
        empty_content = {}
        
        success = create_pdf_file(empty_content, self.test_file_path)
        
        # Should handle empty content
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_file_path))


if __name__ == '__main__':
    unittest.main()