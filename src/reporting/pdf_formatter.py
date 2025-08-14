"""
PDF Formatter Module for Advanced Trade Insight Engine

This module provides functions to create professional PDF reports from
structured report content. It handles document layout, styling, and
formatting for business reports.

Functions:
    create_pdf_document: Initialize PDF document with basic settings
    add_header_section: Add report title and metadata
    add_executive_summary: Format and add executive summary section
    add_pain_points_section: Format and add top pain points section
    add_praised_features_section: Format and add praised features section
    add_strategic_insights_section: Format and add strategic insights section
    add_theme_analysis_section: Format and add theme analysis section
    create_pdf_report: Main function to generate complete PDF report
"""

from fpdf import FPDF
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportPDF(FPDF):
    """Custom PDF class with header and footer methods."""
    
    def __init__(self, title: str = "Customer Feedback Insight Report"):
        super().__init__()
        self.report_title = title
        
    def header(self):
        """Add header to each page."""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, self.report_title, 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_pdf_document(title: str = "Weekly Customer Feedback Insight Report") -> ReportPDF:
    """
    Initialize PDF document with basic settings and styling.
    
    Args:
        title (str): Report title for header
        
    Returns:
        ReportPDF: Initialized PDF document object
        
    Requirements: 5.5
    """
    try:
        pdf = ReportPDF(title)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        logger.info("Created PDF document")
        return pdf
        
    except Exception as e:
        logger.error(f"Error creating PDF document: {e}")
        raise


def add_header_section(pdf: ReportPDF, report_content: Dict[str, Any]) -> None:
    """
    Add report title, subtitle, and generation metadata.
    
    Args:
        pdf (ReportPDF): PDF document object
        report_content (Dict): Report content with metadata
        
    Requirements: 5.5, 5.6
    """
    try:
        # Main title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Weekly Customer Feedback Insight Report', 0, 1, 'C')
        
        # Subtitle
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Coinbase Advanced Trading Platform', 0, 1, 'C')
        pdf.ln(5)
        
        # Generation info
        pdf.set_font('Arial', '', 10)
        metadata = report_content.get('metadata', {})
        generated_at = metadata.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        total_records = metadata.get('total_records_processed', 0)
        
        pdf.cell(0, 8, f'Generated: {generated_at}', 0, 1, 'L')
        pdf.cell(0, 8, f'Total Feedback Records Analyzed: {total_records}', 0, 1, 'L')
        pdf.ln(10)
        
        logger.info("Added header section to PDF")
        
    except Exception as e:
        logger.error(f"Error adding header section: {e}")
        raise


def add_executive_summary(pdf: ReportPDF, executive_summary: Dict[str, Any]) -> None:
    """
    Format and add executive summary section with key metrics.
    
    Args:
        pdf (ReportPDF): PDF document object
        executive_summary (Dict): Executive summary data
        
    Requirements: 5.5, 5.6
    """
    try:
        # Section header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'Executive Summary', 0, 1, 'L')
        pdf.ln(3)
        
        # Key metrics
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Key Metrics:', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        
        # Total feedback and customers
        total_items = executive_summary.get('total_feedback_items', 0)
        unique_customers = executive_summary.get('unique_customers', 0)
        pdf.cell(0, 6, f'- Total Feedback Items: {total_items:,}', 0, 1, 'L')
        pdf.cell(0, 6, f'- Unique Customers: {unique_customers:,}', 0, 1, 'L')
        
        # Sentiment distribution
        sentiment_dist = executive_summary.get('sentiment_distribution', {})
        pdf.cell(0, 6, f'- Sentiment Breakdown: {sentiment_dist.get("positive", 0)} Positive, {sentiment_dist.get("negative", 0)} Negative, {sentiment_dist.get("neutral", 0)} Neutral', 0, 1, 'L')
        
        # Top theme
        top_theme = executive_summary.get('top_theme', {})
        theme_name = top_theme.get('name', 'Unknown')
        theme_impact = top_theme.get('total_impact', 0)
        pdf.cell(0, 6, f'- Top Theme by Impact: {theme_name} (Impact Score: {theme_impact:.2f})', 0, 1, 'L')
        
        # Impact metrics
        impact_metrics = executive_summary.get('impact_metrics', {})
        total_impact = impact_metrics.get('total_impact', 0)
        avg_impact = impact_metrics.get('average_impact', 0)
        pdf.cell(0, 6, f'- Total Impact Score: {total_impact:.2f}', 0, 1, 'L')
        pdf.cell(0, 6, f'- Average Impact Score: {avg_impact:.2f}', 0, 1, 'L')
        
        pdf.ln(8)
        logger.info("Added executive summary section")
        
    except Exception as e:
        logger.error(f"Error adding executive summary: {e}")
        raise


def add_pain_points_section(pdf: ReportPDF, pain_points: List[Dict[str, Any]]) -> None:
    """
    Format and add top pain points section.
    
    Args:
        pdf (ReportPDF): PDF document object
        pain_points (List[Dict]): List of top pain points
        
    Requirements: 5.5, 5.6
    """
    try:
        # Section header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'Top Pain Points', 0, 1, 'L')
        pdf.ln(3)
        
        if not pain_points:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, 'No significant pain points identified in the current dataset.', 0, 1, 'L')
            pdf.ln(5)
            return
        
        for i, pain_point in enumerate(pain_points, 1):
            # Pain point header
            pdf.set_font('Arial', 'B', 11)
            theme = pain_point.get('theme', 'Unknown')
            impact = pain_point.get('impact_score', 0)
            pdf.cell(0, 8, f'{i}. {theme} (Impact Score: {impact:.2f})', 0, 1, 'L')
            
            # Details
            pdf.set_font('Arial', '', 9)
            source = pain_point.get('source_channel', 'Unknown')
            strategic_goal = pain_point.get('strategic_goal', 'Other')
            pdf.cell(0, 5, f'   Source: {source} | Strategic Goal: {strategic_goal}', 0, 1, 'L')
            
            # Feedback text (wrapped)
            feedback_text = pain_point.get('feedback_text', '')
            if feedback_text:
                pdf.set_font('Arial', 'I', 9)
                # Simple text wrapping
                words = feedback_text.split()
                line = '   "'
                for word in words:
                    if len(line + word + ' ') > 85:  # Approximate character limit per line
                        pdf.cell(0, 5, line, 0, 1, 'L')
                        line = '   ' + word + ' '
                    else:
                        line += word + ' '
                if line.strip():
                    pdf.cell(0, 5, line + '"', 0, 1, 'L')
            
            pdf.ln(3)
        
        pdf.ln(5)
        logger.info(f"Added {len(pain_points)} pain points to PDF")
        
    except Exception as e:
        logger.error(f"Error adding pain points section: {e}")
        raise


def add_praised_features_section(pdf: ReportPDF, praised_features: List[Dict[str, Any]]) -> None:
    """
    Format and add praised features section.
    
    Args:
        pdf (ReportPDF): PDF document object
        praised_features (List[Dict]): List of praised features
        
    Requirements: 5.5, 5.6
    """
    try:
        # Section header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'Top Praised Features', 0, 1, 'L')
        pdf.ln(3)
        
        if not praised_features:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, 'No significantly praised features identified in the current dataset.', 0, 1, 'L')
            pdf.ln(5)
            return
        
        for i, feature in enumerate(praised_features, 1):
            # Feature header
            pdf.set_font('Arial', 'B', 11)
            theme = feature.get('theme', 'Unknown')
            impact = feature.get('impact_score', 0)
            pdf.cell(0, 8, f'{i}. {theme} (Impact Score: {impact:.2f})', 0, 1, 'L')
            
            # Details
            pdf.set_font('Arial', '', 9)
            source = feature.get('source_channel', 'Unknown')
            strategic_goal = feature.get('strategic_goal', 'Other')
            pdf.cell(0, 5, f'   Source: {source} | Strategic Goal: {strategic_goal}', 0, 1, 'L')
            
            # Feedback text (wrapped)
            feedback_text = feature.get('feedback_text', '')
            if feedback_text:
                pdf.set_font('Arial', 'I', 9)
                # Simple text wrapping
                words = feedback_text.split()
                line = '   "'
                for word in words:
                    if len(line + word + ' ') > 85:  # Approximate character limit per line
                        pdf.cell(0, 5, line, 0, 1, 'L')
                        line = '   ' + word + ' '
                    else:
                        line += word + ' '
                if line.strip():
                    pdf.cell(0, 5, line + '"', 0, 1, 'L')
            
            pdf.ln(3)
        
        pdf.ln(5)
        logger.info(f"Added {len(praised_features)} praised features to PDF")
        
    except Exception as e:
        logger.error(f"Error adding praised features section: {e}")
        raise


def add_strategic_insights_section(pdf: ReportPDF, strategic_insights: Dict[str, Dict[str, Any]]) -> None:
    """
    Format and add strategic insights section.
    
    Args:
        pdf (ReportPDF): PDF document object
        strategic_insights (Dict): Strategic goal insights
        
    Requirements: 5.5, 5.6
    """
    try:
        # Section header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'Strategic Goal Insights', 0, 1, 'L')
        pdf.ln(3)
        
        if not strategic_insights:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, 'No strategic goal insights available.', 0, 1, 'L')
            pdf.ln(5)
            return
        
        for goal, insights in strategic_insights.items():
            # Goal header
            pdf.set_font('Arial', 'B', 11)
            total_impact = insights.get('total_impact', 0)
            feedback_count = insights.get('feedback_count', 0)
            pdf.cell(0, 8, f'{goal} (Total Impact: {total_impact:.2f}, {feedback_count} items)', 0, 1, 'L')
            
            # Metrics
            pdf.set_font('Arial', '', 9)
            avg_impact = insights.get('avg_impact', 0)
            pdf.cell(0, 5, f'   Average Impact: {avg_impact:.2f}', 0, 1, 'L')
            
            # Sentiment breakdown
            sentiment_breakdown = insights.get('sentiment_breakdown', {})
            sentiment_text = ', '.join([f'{k}: {v}' for k, v in sentiment_breakdown.items() if v > 0])
            if sentiment_text:
                pdf.cell(0, 5, f'   Sentiment: {sentiment_text}', 0, 1, 'L')
            
            # Top feedback
            top_feedback = insights.get('top_feedback')
            if top_feedback:
                pdf.set_font('Arial', 'I', 9)
                theme = top_feedback.get('theme', 'Unknown')
                feedback_text = top_feedback.get('feedback_text', '')[:100] + '...' if len(top_feedback.get('feedback_text', '')) > 100 else top_feedback.get('feedback_text', '')
                pdf.cell(0, 5, f'   Top Item ({theme}): "{feedback_text}"', 0, 1, 'L')
            
            pdf.ln(2)
        
        pdf.ln(5)
        logger.info(f"Added strategic insights for {len(strategic_insights)} goals")
        
    except Exception as e:
        logger.error(f"Error adding strategic insights section: {e}")
        raise


def add_theme_analysis_section(pdf: ReportPDF, theme_analysis: List[Dict[str, Any]]) -> None:
    """
    Format and add theme analysis section with impact rankings.
    
    Args:
        pdf (ReportPDF): PDF document object
        theme_analysis (List[Dict]): Theme analysis data
        
    Requirements: 5.5, 5.6
    """
    try:
        # Section header
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 12, 'Theme Impact Analysis', 0, 1, 'L')
        pdf.ln(3)
        
        if not theme_analysis:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, 'No theme analysis data available.', 0, 1, 'L')
            pdf.ln(5)
            return
        
        # Table header
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(60, 8, 'Theme', 1, 0, 'L')
        pdf.cell(25, 8, 'Total Impact', 1, 0, 'C')
        pdf.cell(25, 8, 'Avg Impact', 1, 0, 'C')
        pdf.cell(20, 8, 'Count', 1, 0, 'C')
        pdf.cell(20, 8, 'Negative', 1, 1, 'C')
        
        # Table rows
        pdf.set_font('Arial', '', 8)
        for theme_data in theme_analysis[:10]:  # Limit to top 10 themes
            theme = theme_data.get('theme', 'Unknown')
            if len(theme) > 25:  # Truncate long theme names
                theme = theme[:22] + '...'
            
            total_impact = theme_data.get('total_impact', 0)
            avg_impact = theme_data.get('avg_impact', 0)
            feedback_count = theme_data.get('feedback_count', 0)
            negative_count = theme_data.get('negative_count', 0)
            
            pdf.cell(60, 6, theme, 1, 0, 'L')
            pdf.cell(25, 6, f'{total_impact:.1f}', 1, 0, 'C')
            pdf.cell(25, 6, f'{avg_impact:.2f}', 1, 0, 'C')
            pdf.cell(20, 6, str(feedback_count), 1, 0, 'C')
            pdf.cell(20, 6, str(negative_count), 1, 1, 'C')
        
        pdf.ln(5)
        logger.info(f"Added theme analysis table with {len(theme_analysis)} themes")
        
    except Exception as e:
        logger.error(f"Error adding theme analysis section: {e}")
        raise


def create_pdf_report(report_content: Dict[str, Any], output_path: str) -> bool:
    """
    Create complete PDF report from structured report content.
    
    Args:
        report_content (Dict): Complete report content structure
        output_path (str): Path where PDF should be saved
        
    Returns:
        bool: True if successful, False otherwise
        
    Requirements: 5.5, 5.6
    """
    try:
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Create PDF document
        pdf = create_pdf_document()
        
        # Add all sections
        add_header_section(pdf, report_content)
        
        executive_summary = report_content.get('executive_summary', {})
        if executive_summary:
            add_executive_summary(pdf, executive_summary)
        
        pain_points = report_content.get('top_pain_points', [])
        add_pain_points_section(pdf, pain_points)
        
        praised_features = report_content.get('praised_features', [])
        add_praised_features_section(pdf, praised_features)
        
        strategic_insights = report_content.get('strategic_insights', {})
        if strategic_insights:
            add_strategic_insights_section(pdf, strategic_insights)
        
        theme_analysis = report_content.get('theme_analysis', [])
        if theme_analysis:
            add_theme_analysis_section(pdf, theme_analysis)
        
        # Save PDF
        pdf.output(output_path)
        
        logger.info(f"Successfully created PDF report: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating PDF report: {e}")
        return False