"""
Report Generator Module for Advanced Trade Insight Engine

This module orchestrates the complete report generation process by coordinating
content building and PDF formatting. It provides the main interface for
generating business reports from analyzed customer feedback data.

Functions:
    generate_report_content: Main orchestration function for content building
    create_pdf_report: Main function for PDF report generation
    generate_complete_report: End-to-end report generation workflow
    validate_report_data: Validate input data before processing
"""

import pandas as pd
import os
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime

# Import content building and PDF formatting modules
from .content_builder import build_report_content
from .pdf_formatter import create_pdf_report as create_pdf_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_report_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate input DataFrame for report generation.
    
    Args:
        df (pd.DataFrame): Input DataFrame to validate
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
        
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    try:
        # Check if DataFrame is empty
        if df.empty:
            return False, "Input DataFrame is empty"
        
        # Check for required columns
        required_columns = ['theme', 'sentiment', 'impact_score']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
        
        # Check for valid sentiment values
        valid_sentiments = {'positive', 'negative', 'neutral'}
        invalid_sentiments = set(df['sentiment'].dropna().unique()) - valid_sentiments
        
        if invalid_sentiments:
            logger.warning(f"Found invalid sentiment values: {invalid_sentiments}")
        
        # Check for numeric impact scores
        if not pd.api.types.is_numeric_dtype(df['impact_score']):
            return False, "Impact score column must be numeric"
        
        # Check for null values in critical columns
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            logger.warning(f"Found null values in required columns: {null_counts.to_dict()}")
        
        logger.info(f"Data validation passed for {len(df)} records")
        return True, "Data validation successful"
        
    except Exception as e:
        logger.error(f"Error during data validation: {e}")
        return False, f"Validation error: {str(e)}"


def generate_report_content(df: pd.DataFrame, top_n: int = 3) -> Dict[str, Any]:
    """
    Generate structured report content from analyzed feedback data.
    
    This function coordinates all content building operations to create
    a comprehensive report structure ready for formatting.
    
    Args:
        df (pd.DataFrame): DataFrame with enriched feedback records
        top_n (int): Number of top items to include in each category
        
    Returns:
        Dict[str, Any]: Complete report content structure
        
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    try:
        logger.info("Starting report content generation")
        
        # Validate input data
        is_valid, validation_message = validate_report_data(df)
        if not is_valid:
            logger.error(f"Data validation failed: {validation_message}")
            return {
                'error': validation_message,
                'metadata': {
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_records_processed': 0,
                    'status': 'failed'
                }
            }
        
        # Generate report content using content builder
        report_content = build_report_content(df, top_n)
        
        if not report_content:
            logger.error("Failed to generate report content")
            return {
                'error': 'Content generation failed',
                'metadata': {
                    'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_records_processed': len(df),
                    'status': 'failed'
                }
            }
        
        # Add generation metadata
        if 'metadata' not in report_content:
            report_content['metadata'] = {}
        
        report_content['metadata'].update({
            'generation_status': 'success',
            'validation_message': validation_message,
            'top_n_items': top_n
        })
        
        logger.info("Successfully generated report content")
        return report_content
        
    except Exception as e:
        logger.error(f"Error generating report content: {e}")
        return {
            'error': f'Content generation error: {str(e)}',
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records_processed': len(df) if df is not None else 0,
                'status': 'failed'
            }
        }


def create_pdf_report(report_content: Dict[str, Any], output_path: str) -> Tuple[bool, str]:
    """
    Create PDF report from structured report content.
    
    This function handles file path management and integrates with the
    PDF formatter to generate the final report document.
    
    Args:
        report_content (Dict[str, Any]): Complete report content structure
        output_path (str): Path where PDF should be saved
        
    Returns:
        Tuple[bool, str]: (success, message)
        
    Requirements: 5.5
    """
    try:
        logger.info(f"Creating PDF report at: {output_path}")
        
        # Check if report content contains errors
        if 'error' in report_content:
            error_msg = f"Cannot create PDF from failed content generation: {report_content['error']}"
            logger.error(error_msg)
            return False, error_msg
        
        # Validate output path
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                error_msg = f"Failed to create output directory {output_dir}: {e}"
                logger.error(error_msg)
                return False, error_msg
        
        # Generate PDF using PDF formatter
        pdf_success = create_pdf_file(report_content, output_path)
        
        if pdf_success:
            # Verify file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                file_size = os.path.getsize(output_path)
                success_msg = f"PDF report successfully created: {output_path} ({file_size} bytes)"
                logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = f"PDF file was not created or is empty: {output_path}"
                logger.error(error_msg)
                return False, error_msg
        else:
            error_msg = f"PDF generation failed for: {output_path}"
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Error creating PDF report: {e}"
        logger.error(error_msg)
        return False, error_msg


def generate_complete_report(df: pd.DataFrame, output_path: str, top_n: int = 3) -> Dict[str, Any]:
    """
    Generate complete report from data to PDF in a single workflow.
    
    This is the main entry point for end-to-end report generation,
    combining content generation and PDF creation.
    
    Args:
        df (pd.DataFrame): DataFrame with enriched feedback records
        output_path (str): Path where PDF should be saved
        top_n (int): Number of top items to include in each category
        
    Returns:
        Dict[str, Any]: Report generation results and metadata
        
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    try:
        logger.info("Starting complete report generation workflow")
        
        # Step 1: Generate report content
        logger.info("Step 1: Generating report content")
        report_content = generate_report_content(df, top_n)
        
        if 'error' in report_content:
            return {
                'success': False,
                'error': report_content['error'],
                'content_generated': False,
                'pdf_created': False,
                'output_path': output_path,
                'metadata': report_content.get('metadata', {})
            }
        
        # Step 2: Create PDF report
        logger.info("Step 2: Creating PDF report")
        pdf_success, pdf_message = create_pdf_report(report_content, output_path)
        
        # Compile results
        results = {
            'success': pdf_success,
            'content_generated': True,
            'pdf_created': pdf_success,
            'output_path': output_path,
            'pdf_message': pdf_message,
            'report_content': report_content,
            'metadata': report_content.get('metadata', {})
        }
        
        if not pdf_success:
            results['error'] = pdf_message
        
        # Log final results
        if pdf_success:
            logger.info(f"Complete report generation successful: {output_path}")
        else:
            logger.error(f"Complete report generation failed: {pdf_message}")
        
        return results
        
    except Exception as e:
        error_msg = f"Error in complete report generation: {e}"
        logger.error(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'content_generated': False,
            'pdf_created': False,
            'output_path': output_path,
            'metadata': {
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records_processed': len(df) if df is not None else 0,
                'status': 'failed'
            }
        }


def get_report_summary(results: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of report generation results.
    
    Args:
        results (Dict[str, Any]): Results from generate_complete_report
        
    Returns:
        str: Formatted summary message
    """
    try:
        if results.get('success', False):
            metadata = results.get('metadata', {})
            total_records = metadata.get('total_records_processed', 0)
            generated_at = metadata.get('generated_at', 'Unknown')
            
            summary = f"""
Report Generation Summary:
✓ Status: SUCCESS
✓ Output File: {results.get('output_path', 'Unknown')}
✓ Records Processed: {total_records:,}
✓ Generated At: {generated_at}
✓ PDF Message: {results.get('pdf_message', 'PDF created successfully')}
            """.strip()
        else:
            error = results.get('error', 'Unknown error')
            summary = f"""
Report Generation Summary:
✗ Status: FAILED
✗ Error: {error}
✗ Content Generated: {results.get('content_generated', False)}
✗ PDF Created: {results.get('pdf_created', False)}
✗ Output Path: {results.get('output_path', 'Unknown')}
            """.strip()
        
        return summary
        
    except Exception as e:
        return f"Error generating report summary: {e}"