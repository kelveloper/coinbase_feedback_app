#!/usr/bin/env python3
"""
Main Orchestrator for Advanced Trade Insight Engine MVP

This module provides the main execution pipeline that coordinates all components:
- Data loading and normalization from CSV sources
- NLP processing and impact scoring
- Report generation and dashboard data preparation
- Comprehensive error handling and logging

Usage:
    python main.py [--data-dir csv_mock_data] [--output-dir output] [--verbose]

Requirements: 7.1, 7.2, 7.3, 7.6
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import time
import traceback

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import all required modules
from data_processing.data_loader import load_all_csv_files, get_loading_summary, validate_data_directory
from data_processing.data_normalizer import normalize_and_unify_data
from analysis.nlp_models import enrich_dataframe_with_nlp
from analysis.scoring_engine import enrich_dataframe_with_scores
from reporting.report_generator import generate_complete_report, get_report_summary

# Import configuration
from config import (
    CSV_FILE_PATHS, OUTPUT_PATHS, LOGGING_CONFIG, 
    DATA_DIR, OUTPUT_DIR
)


class ProgressTracker:
    """
    Progress tracking utility for monitoring execution status.
    
    Requirements: 7.4, 7.5
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.steps = []
        self.current_step = 0
        self.start_time = None
        self.step_start_time = None
    
    def add_step(self, name: str, description: str):
        """Add a step to track."""
        self.steps.append({
            'name': name,
            'description': description,
            'status': 'pending',
            'start_time': None,
            'end_time': None,
            'duration': None,
            'error': None
        })
    
    def start_execution(self):
        """Start tracking execution."""
        self.start_time = time.time()
        self.logger.info(f"🚀 Starting execution with {len(self.steps)} steps")
    
    def start_step(self, step_index: int):
        """Start tracking a specific step."""
        if 0 <= step_index < len(self.steps):
            self.current_step = step_index
            self.step_start_time = time.time()
            self.steps[step_index]['status'] = 'running'
            self.steps[step_index]['start_time'] = self.step_start_time
            
            step = self.steps[step_index]
            progress = f"[{step_index + 1}/{len(self.steps)}]"
            self.logger.info(f"⏳ {progress} {step['name']}: {step['description']}")
    
    def complete_step(self, step_index: int, success: bool = True, error: str = None):
        """Mark a step as completed."""
        if 0 <= step_index < len(self.steps):
            end_time = time.time()
            self.steps[step_index]['end_time'] = end_time
            self.steps[step_index]['duration'] = end_time - self.steps[step_index]['start_time']
            
            if success:
                self.steps[step_index]['status'] = 'completed'
                duration = self.steps[step_index]['duration']
                self.logger.info(f"✅ Step {step_index + 1} completed successfully ({duration:.2f}s)")
            else:
                self.steps[step_index]['status'] = 'failed'
                self.steps[step_index]['error'] = error
                duration = self.steps[step_index]['duration']
                self.logger.error(f"❌ Step {step_index + 1} failed ({duration:.2f}s): {error}")
    
    def get_progress_summary(self) -> Dict[str, Any]:
        """Get current progress summary."""
        completed = sum(1 for step in self.steps if step['status'] == 'completed')
        failed = sum(1 for step in self.steps if step['status'] == 'failed')
        running = sum(1 for step in self.steps if step['status'] == 'running')
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            'total_steps': len(self.steps),
            'completed': completed,
            'failed': failed,
            'running': running,
            'pending': len(self.steps) - completed - failed - running,
            'total_duration': total_duration,
            'steps': self.steps
        }
    
    def display_final_summary(self):
        """Display final execution summary."""
        summary = self.get_progress_summary()
        
        self.logger.info("=" * 60)
        self.logger.info("📊 EXECUTION PROGRESS SUMMARY")
        self.logger.info("=" * 60)
        
        self.logger.info(f"Total Steps: {summary['total_steps']}")
        self.logger.info(f"✅ Completed: {summary['completed']}")
        self.logger.info(f"❌ Failed: {summary['failed']}")
        self.logger.info(f"⏳ Running: {summary['running']}")
        self.logger.info(f"⏸️  Pending: {summary['pending']}")
        self.logger.info(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
        
        self.logger.info("\nStep Details:")
        for i, step in enumerate(self.steps):
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'running': '⏳',
                'pending': '⏸️'
            }.get(step['status'], '❓')
            
            duration_str = f"({step['duration']:.2f}s)" if step['duration'] else ""
            error_str = f" - {step['error']}" if step['error'] else ""
            
            self.logger.info(f"  {i+1}. {status_icon} {step['name']} {duration_str}{error_str}")


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the main orchestrator with enhanced monitoring.
    
    Args:
        verbose (bool): Enable verbose logging
        
    Returns:
        logging.Logger: Configured logger instance
        
    Requirements: 7.4, 7.5
    """
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Configure logging level
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create enhanced formatter with more context
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    try:
        # Create timestamped log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"insight_engine_{timestamp}.log"
        log_filepath = OUTPUT_DIR / log_filename
        
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for file
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Also create/update the main log file
        main_log_handler = logging.FileHandler(LOGGING_CONFIG['log_file'])
        main_log_handler.setLevel(logging.INFO)
        main_log_handler.setFormatter(formatter)
        root_logger.addHandler(main_log_handler)
        
    except Exception as e:
        print(f"Warning: Could not create log file: {e}")
    
    # Get module logger
    logger = logging.getLogger(__name__)
    logger.info("Enhanced logging configured successfully")
    
    return logger


def validate_environment(data_dir: str, output_dir: str) -> Tuple[bool, str]:
    """
    Validate the execution environment and required directories.
    
    Args:
        data_dir (str): Path to data directory
        output_dir (str): Path to output directory
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    try:
        # Check data directory
        is_valid, missing_files = validate_data_directory(data_dir)
        
        if not is_valid:
            return False, f"Data directory validation failed. Missing files: {missing_files}"
        
        # Check/create output directory
        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return False, f"Cannot create output directory {output_dir}: {e}"
        
        # Check write permissions
        test_file = output_path / "test_write.tmp"
        try:
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            return False, f"No write permission in output directory {output_dir}: {e}"
        
        return True, "Environment validation successful"
        
    except Exception as e:
        return False, f"Environment validation error: {e}"


def load_and_normalize_data(data_dir: str, logger: logging.Logger) -> Optional[Any]:
    """
    Load and normalize data from all CSV sources.
    
    Args:
        data_dir (str): Directory containing CSV files
        logger (logging.Logger): Logger instance
        
    Returns:
        Optional[pd.DataFrame]: Normalized DataFrame or None if failed
    """
    try:
        logger.info("=" * 60)
        logger.info("STEP 1: LOADING AND NORMALIZING DATA")
        logger.info("=" * 60)
        
        # Load CSV files
        logger.info(f"Loading CSV files from: {data_dir}")
        loaded_data = load_all_csv_files(data_dir)
        
        if not loaded_data:
            logger.error("No data files could be loaded")
            return None
        
        # Display loading summary
        summary = get_loading_summary(loaded_data)
        logger.info(f"Successfully loaded {summary['total_records']} records from {summary['sources_loaded']} sources")
        
        for source, count in summary.items():
            if source not in ['total_records', 'sources_loaded', 'sources_expected']:
                logger.info(f"  - {source}: {count:,} records")
        
        # Normalize and unify data
        logger.info("Normalizing and unifying data across sources...")
        normalized_df = normalize_and_unify_data(loaded_data)
        
        if normalized_df.empty:
            logger.error("Data normalization failed - no records to process")
            return None
        
        logger.info(f"Successfully normalized {len(normalized_df)} feedback records")
        logger.info("Data loading and normalization completed successfully")
        
        return normalized_df
        
    except Exception as e:
        logger.error(f"Error in data loading and normalization: {e}")
        return None


def process_nlp_and_scoring(df: Any, logger: logging.Logger) -> Optional[Any]:
    """
    Apply NLP processing and impact scoring to the normalized data.
    
    Args:
        df (pd.DataFrame): Normalized DataFrame
        logger (logging.Logger): Logger instance
        
    Returns:
        Optional[pd.DataFrame]: Enriched DataFrame or None if failed
    """
    try:
        logger.info("=" * 60)
        logger.info("STEP 2: NLP PROCESSING AND IMPACT SCORING")
        logger.info("=" * 60)
        
        # Apply NLP enrichment
        logger.info("Applying NLP analysis (sentiment, theme, strategic goal)...")
        enriched_df = enrich_dataframe_with_nlp(df)
        
        if enriched_df.empty:
            logger.error("NLP enrichment failed")
            return None
        
        logger.info(f"NLP analysis completed for {len(enriched_df)} records")
        
        # Calculate impact scores
        logger.info("Calculating source weights and impact scores...")
        scored_df = enrich_dataframe_with_scores(enriched_df)
        
        if scored_df.empty:
            logger.error("Impact scoring failed")
            return None
        
        logger.info(f"Impact scoring completed for {len(scored_df)} records")
        
        # Display scoring statistics
        if 'impact_score' in scored_df.columns:
            impact_stats = scored_df['impact_score'].describe()
            logger.info("Impact Score Statistics:")
            logger.info(f"  - Mean: {impact_stats['mean']:.4f}")
            logger.info(f"  - Median: {impact_stats['50%']:.4f}")
            logger.info(f"  - Max: {impact_stats['max']:.4f}")
            logger.info(f"  - Min: {impact_stats['min']:.4f}")
        
        logger.info("NLP processing and impact scoring completed successfully")
        return scored_df
        
    except Exception as e:
        logger.error(f"Error in NLP processing and scoring: {e}")
        return None


def generate_reports(df: Any, output_dir: str, logger: logging.Logger) -> Dict[str, Any]:
    """
    Generate PDF reports from the processed data.
    
    Args:
        df (pd.DataFrame): Processed DataFrame with impact scores
        output_dir (str): Output directory for reports
        logger (logging.Logger): Logger instance
        
    Returns:
        Dict[str, Any]: Report generation results
    """
    try:
        logger.info("=" * 60)
        logger.info("STEP 3: GENERATING REPORTS")
        logger.info("=" * 60)
        
        # Prepare output path
        pdf_output_path = os.path.join(output_dir, "weekly_insight_report.pdf")
        logger.info(f"Generating PDF report: {pdf_output_path}")
        
        # Generate complete report
        report_results = generate_complete_report(df, pdf_output_path, top_n=3)
        
        # Log results
        if report_results.get('success', False):
            logger.info("PDF report generated successfully")
            logger.info(f"Report saved to: {pdf_output_path}")
            
            # Display report summary
            summary = get_report_summary(report_results)
            for line in summary.split('\n'):
                if line.strip():
                    logger.info(f"  {line.strip()}")
        else:
            logger.error(f"PDF report generation failed: {report_results.get('error', 'Unknown error')}")
        
        return report_results
        
    except Exception as e:
        logger.error(f"Error generating reports: {e}")
        return {
            'success': False,
            'error': f'Report generation error: {str(e)}',
            'content_generated': False,
            'pdf_created': False
        }


def prepare_dashboard_data(df: Any, output_dir: str, logger: logging.Logger) -> bool:
    """
    Prepare and save processed data for dashboard use.
    
    Args:
        df (pd.DataFrame): Processed DataFrame with impact scores
        output_dir (str): Output directory for processed data
        logger (logging.Logger): Logger instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("=" * 60)
        logger.info("STEP 4: PREPARING DASHBOARD DATA")
        logger.info("=" * 60)
        
        # Save processed data for dashboard
        dashboard_data_path = os.path.join(output_dir, "processed_feedback_data.csv")
        logger.info(f"Saving processed data for dashboard: {dashboard_data_path}")
        
        df.to_csv(dashboard_data_path, index=False)
        
        # Verify file was created
        if os.path.exists(dashboard_data_path):
            file_size = os.path.getsize(dashboard_data_path)
            logger.info(f"Dashboard data saved successfully ({file_size:,} bytes)")
            logger.info(f"Data contains {len(df)} records with {len(df.columns)} columns")
            
            # Log column information
            logger.info("Available columns for dashboard:")
            for col in df.columns:
                logger.info(f"  - {col}")
            
            return True
        else:
            logger.error("Failed to save dashboard data file")
            return False
            
    except Exception as e:
        logger.error(f"Error preparing dashboard data: {e}")
        return False


def display_enhanced_execution_summary(
    start_time: datetime,
    results: Dict[str, Any],
    output_dir: str,
    logger: logging.Logger,
    progress_tracker: ProgressTracker
) -> None:
    """
    Display comprehensive execution summary with enhanced monitoring information.
    
    Args:
        start_time (datetime): Execution start time
        results (Dict[str, Any]): Execution results
        output_dir (str): Output directory path
        logger (logging.Logger): Logger instance
        progress_tracker (ProgressTracker): Progress tracking instance
        
    Requirements: 7.4, 7.5
    """
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Display progress summary first
    progress_tracker.display_final_summary()
    
    logger.info("=" * 60)
    logger.info("📋 DETAILED EXECUTION SUMMARY")
    logger.info("=" * 60)
    
    # Overall status
    critical_success = results['data_loaded'] and results['processing_success']
    overall_success = (
        critical_success and 
        results['report_results'].get('success', False) and 
        results['dashboard_success']
    )
    
    if overall_success:
        status = "🎉 COMPLETE SUCCESS"
    elif critical_success:
        status = "⚠️  PARTIAL SUCCESS"
    else:
        status = "❌ FAILED"
    
    logger.info(f"Overall Status: {status}")
    logger.info(f"Execution Time: {duration.total_seconds():.2f} seconds")
    logger.info(f"Completed At: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Data processing results
    if results['normalized_df'] is not None:
        logger.info(f"Records Processed: {len(results['normalized_df']):,}")
    
    if results['processed_df'] is not None:
        logger.info(f"Records Scored: {len(results['processed_df']):,}")
        
        # Impact score statistics
        if 'impact_score' in results['processed_df'].columns:
            impact_stats = results['processed_df']['impact_score'].describe()
            logger.info(f"Impact Score Range: {impact_stats['min']:.4f} - {impact_stats['max']:.4f}")
    
    # Output files and locations
    logger.info(f"\n📁 Output Directory: {output_dir}")
    
    output_files = []
    if results['report_results'].get('success', False):
        pdf_path = results['report_results'].get('output_path', 'weekly_insight_report.pdf')
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            output_files.append(f"✅ PDF Report: {pdf_path} ({file_size:,} bytes)")
        else:
            output_files.append(f"❓ PDF Report: {pdf_path} (file not found)")
    else:
        output_files.append("❌ PDF Report: Generation failed")
    
    if results['dashboard_success']:
        dashboard_path = os.path.join(output_dir, "processed_feedback_data.csv")
        if os.path.exists(dashboard_path):
            file_size = os.path.getsize(dashboard_path)
            output_files.append(f"✅ Dashboard Data: {dashboard_path} ({file_size:,} bytes)")
        else:
            output_files.append(f"❓ Dashboard Data: {dashboard_path} (file not found)")
    else:
        output_files.append("❌ Dashboard Data: Preparation failed")
    
    # Log files
    log_files = [f for f in os.listdir(output_dir) if f.endswith('.log')]
    if log_files:
        latest_log = max(log_files, key=lambda f: os.path.getctime(os.path.join(output_dir, f)))
        log_path = os.path.join(output_dir, latest_log)
        log_size = os.path.getsize(log_path)
        output_files.append(f"📝 Latest Log: {log_path} ({log_size:,} bytes)")
    
    for file_info in output_files:
        logger.info(f"  {file_info}")
    
    # Next steps and recommendations
    logger.info("\n🎯 Next Steps:")
    
    if overall_success:
        logger.info("  1. 📊 Review the generated PDF report for key insights")
        logger.info("  2. 🌐 Launch the dashboard: streamlit run src/dashboard/dashboard.py")
        logger.info("  3. 📤 Share findings with stakeholders")
        logger.info("  4. 🔄 Schedule regular execution for ongoing monitoring")
    elif critical_success:
        logger.info("  1. 📊 Core data processing completed successfully")
        logger.info("  2. 🔍 Review error logs for output generation issues")
        logger.info("  3. 🛠️  Fix output issues and re-run if needed")
        logger.info("  4. 🌐 Try launching dashboard if data was prepared")
    else:
        logger.info("  1. 🔍 Review error messages and logs above")
        logger.info("  2. 🛠️  Check data file integrity and permissions")
        logger.info("  3. 📋 Verify all required CSV files are present")
        logger.info("  4. 🔄 Retry execution after resolving issues")
    
    # Performance insights
    progress_summary = progress_tracker.get_progress_summary()
    if progress_summary['total_duration'] > 0:
        logger.info(f"\n⚡ Performance Insights:")
        logger.info(f"  • Average step duration: {progress_summary['total_duration'] / len(progress_tracker.steps):.2f}s")
        
        # Find slowest step
        slowest_step = max(
            (step for step in progress_tracker.steps if step['duration']), 
            key=lambda s: s['duration'],
            default=None
        )
        if slowest_step:
            logger.info(f"  • Slowest step: {slowest_step['name']} ({slowest_step['duration']:.2f}s)")


def display_execution_summary(
    start_time: datetime,
    data_loaded: bool,
    processing_success: bool,
    report_results: Dict[str, Any],
    dashboard_success: bool,
    output_dir: str,
    logger: logging.Logger
) -> None:
    """
    Display comprehensive execution summary.
    
    Args:
        start_time (datetime): Execution start time
        data_loaded (bool): Whether data loading succeeded
        processing_success (bool): Whether NLP/scoring succeeded
        report_results (Dict[str, Any]): Report generation results
        dashboard_success (bool): Whether dashboard prep succeeded
        output_dir (str): Output directory path
        logger (logging.Logger): Logger instance
    """
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("EXECUTION SUMMARY")
    logger.info("=" * 60)
    
    # Overall status
    overall_success = (
        data_loaded and 
        processing_success and 
        report_results.get('success', False) and 
        dashboard_success
    )
    
    status = "SUCCESS" if overall_success else "PARTIAL SUCCESS"
    logger.info(f"Overall Status: {status}")
    logger.info(f"Execution Time: {duration.total_seconds():.2f} seconds")
    logger.info(f"Completed At: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step-by-step results
    logger.info("\nStep Results:")
    logger.info(f"  1. Data Loading & Normalization: {'✓ SUCCESS' if data_loaded else '✗ FAILED'}")
    logger.info(f"  2. NLP Processing & Scoring: {'✓ SUCCESS' if processing_success else '✗ FAILED'}")
    logger.info(f"  3. PDF Report Generation: {'✓ SUCCESS' if report_results.get('success', False) else '✗ FAILED'}")
    logger.info(f"  4. Dashboard Data Preparation: {'✓ SUCCESS' if dashboard_success else '✗ FAILED'}")
    
    # Output files
    logger.info(f"\nOutput Directory: {output_dir}")
    
    if report_results.get('success', False):
        logger.info(f"  ✓ PDF Report: {report_results.get('output_path', 'weekly_insight_report.pdf')}")
    
    if dashboard_success:
        logger.info(f"  ✓ Dashboard Data: processed_feedback_data.csv")
    
    # Next steps
    logger.info("\nNext Steps:")
    if overall_success:
        logger.info("  • Review the generated PDF report for key insights")
        logger.info("  • Launch the dashboard: streamlit run src/dashboard/dashboard.py")
        logger.info("  • Share findings with stakeholders")
    else:
        logger.info("  • Review error messages above")
        logger.info("  • Check data file integrity and permissions")
        logger.info("  • Retry execution after resolving issues")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Advanced Trade Insight Engine - Main Execution Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Use default directories
  python main.py --data-dir data --verbose         # Custom data dir with verbose logging
  python main.py --output-dir reports               # Custom output directory
        """
    )
    
    parser.add_argument(
        '--data-dir',
        default='csv_mock_data',
        help='Directory containing CSV data files (default: csv_mock_data)'
    )
    
    parser.add_argument(
        '--output-dir', 
        default='output',
        help='Directory for output files (default: output)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Advanced Trade Insight Engine MVP v1.0'
    )
    
    return parser.parse_args()


def handle_graceful_failure(
    step_name: str, 
    error: Exception, 
    logger: logging.Logger, 
    progress_tracker: ProgressTracker,
    continue_execution: bool = True
) -> bool:
    """
    Handle failures gracefully with detailed logging and recovery options.
    
    Args:
        step_name (str): Name of the failed step
        error (Exception): The exception that occurred
        logger (logging.Logger): Logger instance
        progress_tracker (ProgressTracker): Progress tracker instance
        continue_execution (bool): Whether to continue with remaining steps
        
    Returns:
        bool: Whether execution should continue
        
    Requirements: 7.5, 7.6
    """
    error_msg = str(error)
    
    # Log detailed error information
    logger.error(f"❌ FAILURE in {step_name}")
    logger.error(f"Error Type: {type(error).__name__}")
    logger.error(f"Error Message: {error_msg}")
    
    # Log stack trace in debug mode
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Full stack trace:")
        logger.debug(traceback.format_exc())
    
    # Provide troubleshooting guidance
    troubleshooting_tips = {
        'data loading': [
            "Check that all required CSV files exist in the data directory",
            "Verify file permissions and read access",
            "Ensure CSV files are properly formatted with required columns",
            "Check for file corruption or encoding issues"
        ],
        'nlp processing': [
            "Verify that input data contains required columns (sentiment, theme, etc.)",
            "Check for null or invalid values in text fields",
            "Ensure data types are correct for processing"
        ],
        'impact scoring': [
            "Verify numeric fields (ARR_impact, followers, rating) are valid",
            "Check for missing or null values in scoring columns",
            "Ensure source channel identification is working correctly"
        ],
        'report generation': [
            "Check write permissions in output directory",
            "Verify sufficient disk space for PDF creation",
            "Ensure processed data contains required columns for reporting"
        ],
        'dashboard preparation': [
            "Check write permissions in output directory",
            "Verify processed data integrity",
            "Ensure CSV export functionality is working"
        ]
    }
    
    step_lower = step_name.lower()
    for key, tips in troubleshooting_tips.items():
        if key in step_lower:
            logger.info(f"💡 Troubleshooting tips for {step_name}:")
            for i, tip in enumerate(tips, 1):
                logger.info(f"   {i}. {tip}")
            break
    
    if continue_execution:
        logger.warning(f"⚠️  Continuing execution despite {step_name} failure")
        logger.info("Some functionality may be limited due to this failure")
        return True
    else:
        logger.error(f"🛑 Stopping execution due to critical {step_name} failure")
        return False


def main() -> int:
    """
    Main execution pipeline orchestrator with enhanced monitoring and error handling.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
        
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    """
    start_time = datetime.now()
    logger = None
    progress_tracker = None
    
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup logging
        logger = setup_logging(args.verbose)
        
        # Initialize progress tracker
        progress_tracker = ProgressTracker(logger)
        
        # Define execution steps
        progress_tracker.add_step("Environment Validation", "Validate directories and permissions")
        progress_tracker.add_step("Data Loading", "Load and normalize CSV data from all sources")
        progress_tracker.add_step("NLP Processing", "Apply sentiment analysis and impact scoring")
        progress_tracker.add_step("Report Generation", "Generate PDF reports with insights")
        progress_tracker.add_step("Dashboard Preparation", "Prepare data for interactive dashboard")
        
        # Start execution tracking
        progress_tracker.start_execution()
        
        logger.info("=" * 60)
        logger.info("🚀 ADVANCED TRADE INSIGHT ENGINE - MAIN PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Data Directory: {args.data_dir}")
        logger.info(f"Output Directory: {args.output_dir}")
        logger.info(f"Verbose Logging: {args.verbose}")
        
        # Step 0: Validate environment
        progress_tracker.start_step(0)
        try:
            env_valid, env_message = validate_environment(args.data_dir, args.output_dir)
            if not env_valid:
                progress_tracker.complete_step(0, False, env_message)
                logger.error(f"Environment validation failed: {env_message}")
                return 1
            progress_tracker.complete_step(0, True)
            logger.info("✅ Environment validation successful")
        except Exception as e:
            progress_tracker.complete_step(0, False, str(e))
            if not handle_graceful_failure("Environment Validation", e, logger, progress_tracker, False):
                return 1
        
        # Initialize result tracking
        results = {
            'data_loaded': False,
            'processing_success': False,
            'report_results': {'success': False},
            'dashboard_success': False,
            'normalized_df': None,
            'processed_df': None
        }
        
        # Step 1: Load and normalize data
        progress_tracker.start_step(1)
        try:
            normalized_df = load_and_normalize_data(args.data_dir, logger)
            results['data_loaded'] = normalized_df is not None
            results['normalized_df'] = normalized_df
            
            if not results['data_loaded']:
                progress_tracker.complete_step(1, False, "Data loading returned None")
                if not handle_graceful_failure("Data Loading", Exception("No data loaded"), logger, progress_tracker, False):
                    return 1
            else:
                progress_tracker.complete_step(1, True)
                logger.info(f"✅ Successfully loaded and normalized {len(normalized_df)} records")
                
        except Exception as e:
            progress_tracker.complete_step(1, False, str(e))
            if not handle_graceful_failure("Data Loading", e, logger, progress_tracker, False):
                return 1
        
        # Step 2: NLP processing and impact scoring
        progress_tracker.start_step(2)
        try:
            if results['normalized_df'] is not None:
                processed_df = process_nlp_and_scoring(results['normalized_df'], logger)
                results['processing_success'] = processed_df is not None
                results['processed_df'] = processed_df
                
                if not results['processing_success']:
                    progress_tracker.complete_step(2, False, "NLP processing returned None")
                    if not handle_graceful_failure("NLP Processing", Exception("Processing failed"), logger, progress_tracker, False):
                        return 1
                else:
                    progress_tracker.complete_step(2, True)
                    logger.info(f"✅ Successfully processed {len(processed_df)} records with impact scores")
            else:
                progress_tracker.complete_step(2, False, "No normalized data available")
                logger.error("Cannot proceed with NLP processing - no normalized data")
                
        except Exception as e:
            progress_tracker.complete_step(2, False, str(e))
            if not handle_graceful_failure("NLP Processing and Scoring", e, logger, progress_tracker, False):
                return 1
        
        # Step 3: Generate reports
        progress_tracker.start_step(3)
        try:
            if results['processed_df'] is not None:
                report_results = generate_reports(results['processed_df'], args.output_dir, logger)
                results['report_results'] = report_results
                
                if report_results.get('success', False):
                    progress_tracker.complete_step(3, True)
                    logger.info("✅ PDF report generated successfully")
                else:
                    error_msg = report_results.get('error', 'Unknown report generation error')
                    progress_tracker.complete_step(3, False, error_msg)
                    handle_graceful_failure("Report Generation", Exception(error_msg), logger, progress_tracker, True)
            else:
                progress_tracker.complete_step(3, False, "No processed data available")
                logger.warning("⚠️  Skipping report generation - no processed data")
                
        except Exception as e:
            progress_tracker.complete_step(3, False, str(e))
            handle_graceful_failure("Report Generation", e, logger, progress_tracker, True)
        
        # Step 4: Prepare dashboard data
        progress_tracker.start_step(4)
        try:
            if results['processed_df'] is not None:
                dashboard_success = prepare_dashboard_data(results['processed_df'], args.output_dir, logger)
                results['dashboard_success'] = dashboard_success
                
                if dashboard_success:
                    progress_tracker.complete_step(4, True)
                    logger.info("✅ Dashboard data prepared successfully")
                else:
                    progress_tracker.complete_step(4, False, "Dashboard preparation failed")
                    handle_graceful_failure("Dashboard Preparation", Exception("Preparation failed"), logger, progress_tracker, True)
            else:
                progress_tracker.complete_step(4, False, "No processed data available")
                logger.warning("⚠️  Skipping dashboard preparation - no processed data")
                
        except Exception as e:
            progress_tracker.complete_step(4, False, str(e))
            handle_graceful_failure("Dashboard Preparation", e, logger, progress_tracker, True)
        
        # Display comprehensive final summary
        display_enhanced_execution_summary(
            start_time, results, args.output_dir, logger, progress_tracker
        )
        
        # Determine exit code based on critical steps
        critical_success = (
            results['data_loaded'] and 
            results['processing_success']
        )
        
        overall_success = (
            critical_success and
            results['report_results'].get('success', False) and 
            results['dashboard_success']
        )
        
        if overall_success:
            logger.info("🎉 All steps completed successfully!")
            return 0
        elif critical_success:
            logger.warning("⚠️  Core processing completed, but some outputs failed")
            return 0  # Still return success if core processing worked
        else:
            logger.error("❌ Critical steps failed - execution unsuccessful")
            return 1
        
    except KeyboardInterrupt:
        if logger:
            logger.warning("⚠️  Execution interrupted by user (Ctrl+C)")
        else:
            print("\n⚠️  Execution interrupted by user")
        
        if progress_tracker:
            progress_tracker.display_final_summary()
        
        return 1
        
    except Exception as e:
        error_msg = f"Critical error in main pipeline: {e}"
        
        if logger:
            logger.error(f"💥 {error_msg}")
            logger.debug("Full stack trace:")
            logger.debug(traceback.format_exc())
        else:
            print(f"💥 {error_msg}")
            print(traceback.format_exc())
        
        if progress_tracker:
            progress_tracker.display_final_summary()
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)