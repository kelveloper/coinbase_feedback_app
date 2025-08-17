#!/usr/bin/env python3
"""
Feedback Enhancement System

This system transforms fragmented, multi-channel customer feedback data into a unified,
strategically-aware dataset. It processes raw feedback from four distinct sources
(Apple App Store, Google Play Store, Twitter/X, and Internal Sales Notes) and creates
a single master CSV file with standardized schema, AI-driven insights, and strategic alignment.
"""

import argparse
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import pandas as pd


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up comprehensive logging configuration for the feedback enhancement system.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger('feedback_enhancement_system')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler with simple format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with detailed format
    try:
        file_handler = logging.FileHandler('feedback_enhancement.log', mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file handler: {e}")
    
    # Set pandas logging to WARNING to reduce noise
    logging.getLogger('pandas').setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized with level: {log_level}")
    return logger


class ProcessingTimer:
    """Context manager for timing processing steps with automatic logging."""
    
    def __init__(self, step_name: str, logger: logging.Logger = None):
        self.step_name = step_name
        self.logger = logger or logging.getLogger('feedback_enhancement_system')
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.step_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_time = time.time() - self.start_time
        if exc_type is None:
            self.logger.info(f"Completed {self.step_name} in {elapsed_time:.2f} seconds")
        else:
            self.logger.error(f"Failed {self.step_name} after {elapsed_time:.2f} seconds: {exc_val}")


def log_processing_summary(step_name: str, input_count: int, output_count: int, 
                          processing_time: float = None, logger: logging.Logger = None) -> None:
    """
    Log standardized processing summary with record counts and timing.
    
    Args:
        step_name: Name of the processing step
        input_count: Number of input records
        output_count: Number of output records
        processing_time: Time taken in seconds (optional)
        logger: Logger instance (optional)
    """
    if logger is None:
        logger = logging.getLogger('feedback_enhancement_system')
    
    summary_msg = f"{step_name} Summary: {input_count:,} → {output_count:,} records"
    
    if processing_time is not None:
        summary_msg += f" ({processing_time:.2f}s)"
        
    if input_count > 0:
        retention_rate = (output_count / input_count) * 100
        summary_msg += f" [{retention_rate:.1f}% retention]"
    
    logger.info(summary_msg)


def validate_input_directory(input_dir: str) -> bool:
    """
    Validate that the input directory exists and contains required CSV files.
    
    Args:
        input_dir: Path to the directory containing CSV files
        
    Returns:
        bool: True if directory is valid, False otherwise
    """
    required_files = [
        'coinbase_advance_apple_reviews.csv',
        'coinbase_advanceGoogle_Play.csv', 
        'coinbase_advanced_twitter_mentions.csv',
        'coinbase_advance_internal_sales_notes.csv'
    ]
    
    input_path = Path(input_dir)
    if not input_path.exists():
        logging.error(f"Input directory does not exist: {input_dir}")
        return False
    
    missing_files = []
    for file_name in required_files:
        file_path = input_path / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    if missing_files:
        logging.error(f"Missing required CSV files: {', '.join(missing_files)}")
        return False
    
    logging.info(f"Input directory validation successful: {input_dir}")
    return True


def validate_output_directory(output_dir: str) -> bool:
    """
    Validate that the output directory exists or can be created.
    
    Args:
        output_dir: Path to the output directory
        
    Returns:
        bool: True if directory is valid/created, False otherwise
    """
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Test write permissions
        test_file = output_path / '.write_test'
        test_file.touch()
        test_file.unlink()
        
        logging.info(f"Output directory validation successful: {output_dir}")
        return True
    except Exception as e:
        logging.error(f"Output directory validation failed: {e}")
        return False


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for the feedback enhancement system.
    
    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Transform multi-channel customer feedback into unified dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python feedback_enhancement_system.py
  python feedback_enhancement_system.py --input-dir ./csv_mock_data --output-dir ./output
  python feedback_enhancement_system.py --log-level DEBUG
        """
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        default='csv_mock_data',
        help='Directory containing input CSV files (default: csv_mock_data)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str,
        default='output',
        help='Directory for output files (default: output)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--output-filename',
        type=str,
        default='enriched_feedback_master.csv',
        help='Name of the output CSV file (default: enriched_feedback_master.csv)'
    )
    
    return parser.parse_args()


def validate_loaded_dataframes(dataframes: Dict[str, pd.DataFrame]) -> Tuple[bool, List[str]]:
    """
    Validate loaded DataFrames for basic data quality checks.
    
    Args:
        dataframes: Dictionary of loaded DataFrames
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    for source_name, df in dataframes.items():
        # Check if DataFrame is empty
        if df.empty:
            errors.append(f"{source_name}: DataFrame is empty")
            continue
            
        # Check if DataFrame has any columns
        if len(df.columns) == 0:
            errors.append(f"{source_name}: DataFrame has no columns")
            continue
            
        # Check for completely null DataFrames
        if df.isnull().all().all():
            errors.append(f"{source_name}: DataFrame contains only null values")
            continue
            
        # Log successful validation with details
        null_count = df.isnull().sum().sum()
        logging.info(f"{source_name} validation passed: {len(df)} rows, {len(df.columns)} columns, {null_count} null values")
    
    is_valid = len(errors) == 0
    
    if not is_valid:
        for error in errors:
            logging.error(f"DataFrame validation error: {error}")
    else:
        logging.info("All DataFrames passed validation checks")
    
    return is_valid, errors


def log_dataframe_summary(dataframes: Dict[str, pd.DataFrame]) -> None:
    """
    Log comprehensive summary statistics for all loaded DataFrames.
    
    Args:
        dataframes: Dictionary of loaded DataFrames
    """
    logging.info("=== DataFrame Loading Summary ===")
    
    total_records = 0
    for source_name, df in dataframes.items():
        record_count = len(df)
        total_records += record_count
        column_count = len(df.columns)
        memory_usage = df.memory_usage(deep=True).sum()
        
        logging.info(f"{source_name}:")
        logging.info(f"  - Records: {record_count:,}")
        logging.info(f"  - Columns: {column_count}")
        logging.info(f"  - Memory usage: {memory_usage / 1024:.2f} KB")
        
        # Log column names for debugging
        logging.debug(f"  - Columns: {list(df.columns)}")
    
    logging.info(f"Total records across all sources: {total_records:,}")
    logging.info("=== End Summary ===")


def load_csv_sources(data_directory: str) -> Dict[str, pd.DataFrame]:
    """
    Load all four CSV data sources into separate DataFrames.
    
    Args:
        data_directory: Path to directory containing CSV files
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary mapping source names to DataFrames
        
    Raises:
        FileNotFoundError: If required CSV files are missing
        pd.errors.EmptyDataError: If CSV files are empty
        pd.errors.ParserError: If CSV files are malformed
    """
    logger = logging.getLogger('feedback_enhancement_system')
    
    # Define the mapping of source names to file names
    source_files = {
        'apple_reviews': 'coinbase_advance_apple_reviews.csv',
        'google_reviews': 'coinbase_advanceGoogle_Play.csv',
        'twitter_mentions': 'coinbase_advanced_twitter_mentions.csv',
        'sales_notes': 'coinbase_advance_internal_sales_notes.csv'
    }
    
    loaded_dataframes = {}
    data_path = Path(data_directory)
    
    logger.info(f"Starting to load CSV files from directory: {data_directory}")
    
    for source_name, file_name in source_files.items():
        file_path = data_path / file_name
        
        with ProcessingTimer(f"Loading {source_name}", logger):
            try:
                # Validate file path for reading
                is_valid, error_msg = validate_file_path(str(file_path), mode='r')
                if not is_valid:
                    raise FileNotFoundError(error_msg)
                
                # Get file size for logging
                file_size = file_path.stat().st_size
                logger.debug(f"File {file_name} size: {file_size:,} bytes")
                
                # Load the CSV file
                logger.info(f"Loading {source_name} from {file_name}")
                df = pd.read_csv(file_path)
                
                # Comprehensive validation of loaded DataFrame
                basic_columns = ['customer_id', 'timestamp']  # Minimum expected columns
                is_valid, validation_errors = validate_dataframe_schema(df, basic_columns, source_name)
                
                if not is_valid:
                    error_context = {"file": file_name, "source": source_name}
                    detailed_error = handle_processing_error(
                        ValueError(f"Schema validation failed: {'; '.join(validation_errors)}"),
                        f"Loading {source_name}",
                        error_context
                    )
                    raise ValueError(detailed_error)
                
                loaded_dataframes[source_name] = df
                logger.info(f"Successfully loaded {source_name}: {len(df):,} records, {len(df.columns)} columns")
                
            except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as e:
                error_context = {"file": file_name, "source": source_name}
                handle_processing_error(e, f"Loading {source_name}", error_context)
                raise
            except Exception as e:
                error_context = {"file": file_name, "source": source_name}
                handle_processing_error(e, f"Loading {source_name}", error_context)
                raise
    
    # Perform comprehensive validation on loaded DataFrames
    logger.info("Performing comprehensive DataFrame validation")
    is_valid, validation_errors = validate_loaded_dataframes(loaded_dataframes)
    
    if not is_valid:
        error_msg = f"DataFrame validation failed: {'; '.join(validation_errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Log comprehensive summary of loaded data
    log_dataframe_summary(loaded_dataframes)
    
    return loaded_dataframes


def standardize_apple_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Apple App Store reviews to unified schema.
    
    Args:
        df: Raw Apple reviews DataFrame
        
    Returns:
        pd.DataFrame: Standardized DataFrame with unified schema
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Standardizing Apple App Store reviews: {len(df):,} input records")
    
    # Create a copy to avoid modifying the original DataFrame
    standardized_df = df.copy()
    
    # Generate unique feedback_id with "apple-" prefix
    standardized_df['feedback_id'] = 'apple-' + standardized_df['customer_id'].astype(str)
    logger.debug(f"Generated {len(standardized_df)} unique feedback IDs with 'apple-' prefix")
    
    # Map columns to unified schema
    column_mapping = {
        'review_text': 'feedback_text',
        'helpful_votes': 'source_metric'
    }
    
    # Rename columns according to mapping
    standardized_df = standardized_df.rename(columns=column_mapping)
    logger.debug(f"Mapped columns: {column_mapping}")
    
    # Add source_channel column
    standardized_df['source_channel'] = 'Apple App Store'
    
    # Ensure timestamp is datetime type
    if 'timestamp' in standardized_df.columns:
        standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
        logger.debug("Converted timestamp column to datetime")
    else:
        logger.warning("No timestamp column found in Apple reviews data")
    
    # Ensure source_metric is float type
    if 'source_metric' in standardized_df.columns:
        original_nulls = standardized_df['source_metric'].isnull().sum()
        standardized_df['source_metric'] = pd.to_numeric(standardized_df['source_metric'], errors='coerce')
        new_nulls = standardized_df['source_metric'].isnull().sum()
        if new_nulls > original_nulls:
            logger.warning(f"Conversion to numeric created {new_nulls - original_nulls} additional null values in source_metric")
    
    log_processing_summary("Apple Reviews Standardization", len(df), len(standardized_df), logger=logger)
    return standardized_df


def standardize_google_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Google Play Store reviews to unified schema.
    
    Args:
        df: Raw Google Play reviews DataFrame
        
    Returns:
        pd.DataFrame: Standardized DataFrame with unified schema
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Standardizing Google Play Store reviews: {len(df):,} input records")
    
    # Create a copy to avoid modifying the original DataFrame
    standardized_df = df.copy()
    
    # Generate unique feedback_id with "google-" prefix
    standardized_df['feedback_id'] = 'google-' + standardized_df['customer_id'].astype(str)
    logger.debug(f"Generated {len(standardized_df)} unique feedback IDs with 'google-' prefix")
    
    # Map columns to unified schema (same mapping as Apple reviews)
    column_mapping = {
        'review_text': 'feedback_text',
        'helpful_votes': 'source_metric'
    }
    
    # Rename columns according to mapping
    standardized_df = standardized_df.rename(columns=column_mapping)
    logger.debug(f"Mapped columns: {column_mapping}")
    
    # Add source_channel column
    standardized_df['source_channel'] = 'Google Play Store'
    
    # Ensure timestamp is datetime type
    if 'timestamp' in standardized_df.columns:
        standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
        logger.debug("Converted timestamp column to datetime")
    else:
        logger.warning("No timestamp column found in Google reviews data")
    
    # Ensure source_metric is float type
    if 'source_metric' in standardized_df.columns:
        original_nulls = standardized_df['source_metric'].isnull().sum()
        standardized_df['source_metric'] = pd.to_numeric(standardized_df['source_metric'], errors='coerce')
        new_nulls = standardized_df['source_metric'].isnull().sum()
        if new_nulls > original_nulls:
            logger.warning(f"Conversion to numeric created {new_nulls - original_nulls} additional null values in source_metric")
    
    log_processing_summary("Google Reviews Standardization", len(df), len(standardized_df), logger=logger)
    return standardized_df


def standardize_twitter_mentions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize Twitter mentions to unified schema.
    
    Args:
        df: Raw Twitter mentions DataFrame
        
    Returns:
        pd.DataFrame: Standardized DataFrame with unified schema
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Standardizing Twitter mentions: {len(df):,} input records")
    
    # Create a copy to avoid modifying the original DataFrame
    standardized_df = df.copy()
    
    # Generate unique feedback_id with "twitter-" prefix
    standardized_df['feedback_id'] = 'twitter-' + standardized_df['customer_id'].astype(str)
    logger.debug(f"Generated {len(standardized_df)} unique feedback IDs with 'twitter-' prefix")
    
    # Map columns to unified schema
    column_mapping = {
        'tweet_text': 'feedback_text',
        'followers': 'source_metric'
    }
    
    # Rename columns according to mapping
    standardized_df = standardized_df.rename(columns=column_mapping)
    logger.debug(f"Mapped columns: {column_mapping}")
    
    # Add source_channel column
    standardized_df['source_channel'] = 'Twitter (X)'
    
    # Ensure timestamp is datetime type
    if 'timestamp' in standardized_df.columns:
        standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
        logger.debug("Converted timestamp column to datetime")
    else:
        logger.warning("No timestamp column found in Twitter mentions data")
    
    # Ensure source_metric is float type
    if 'source_metric' in standardized_df.columns:
        original_nulls = standardized_df['source_metric'].isnull().sum()
        standardized_df['source_metric'] = pd.to_numeric(standardized_df['source_metric'], errors='coerce')
        new_nulls = standardized_df['source_metric'].isnull().sum()
        if new_nulls > original_nulls:
            logger.warning(f"Conversion to numeric created {new_nulls - original_nulls} additional null values in source_metric")
    
    log_processing_summary("Twitter Mentions Standardization", len(df), len(standardized_df), logger=logger)
    return standardized_df


def standardize_sales_notes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize internal sales notes to unified schema.
    
    Args:
        df: Raw internal sales notes DataFrame
        
    Returns:
        pd.DataFrame: Standardized DataFrame with unified schema
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Standardizing internal sales notes: {len(df):,} input records")
    
    # Create a copy to avoid modifying the original DataFrame
    standardized_df = df.copy()
    
    # Generate unique feedback_id with "sales-" prefix
    standardized_df['feedback_id'] = 'sales-' + standardized_df['customer_id'].astype(str)
    logger.debug(f"Generated {len(standardized_df)} unique feedback IDs with 'sales-' prefix")
    
    # Map columns to unified schema
    column_mapping = {
        'note_text': 'feedback_text',
        'ARR_impact_estimate_USD': 'source_metric'
    }
    
    # Rename columns according to mapping
    standardized_df = standardized_df.rename(columns=column_mapping)
    logger.debug(f"Mapped columns: {column_mapping}")
    
    # Add source_channel column
    standardized_df['source_channel'] = 'Internal Sales Notes'
    
    # Ensure timestamp is datetime type
    if 'timestamp' in standardized_df.columns:
        standardized_df['timestamp'] = pd.to_datetime(standardized_df['timestamp'])
        logger.debug("Converted timestamp column to datetime")
    else:
        logger.warning("No timestamp column found in sales notes data")
    
    # Ensure source_metric is float type
    if 'source_metric' in standardized_df.columns:
        original_nulls = standardized_df['source_metric'].isnull().sum()
        standardized_df['source_metric'] = pd.to_numeric(standardized_df['source_metric'], errors='coerce')
        new_nulls = standardized_df['source_metric'].isnull().sum()
        if new_nulls > original_nulls:
            logger.warning(f"Conversion to numeric created {new_nulls - original_nulls} additional null values in source_metric")
    
    log_processing_summary("Sales Notes Standardization", len(df), len(standardized_df), logger=logger)
    return standardized_df


def enhance_with_ai_insights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add AI-driven insights including sentiment scoring and relevance classification.
    
    Args:
        df: Standardized DataFrame to enhance
        
    Returns:
        pd.DataFrame: Enhanced DataFrame with sentiment_score and is_relevant columns
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Starting AI-driven enhancement processing: {len(df):,} input records")
    
    # Create a copy to avoid modifying the original DataFrame
    enhanced_df = df.copy()
    
    # Define sentiment mapping according to requirements
    sentiment_mapping = {
        'negative': -0.8,
        'neutral': 0.0,
        'positive': 0.7
    }
    logger.debug(f"Using sentiment mapping: {sentiment_mapping}")
    
    # Initialize sentiment_score column with default neutral value
    enhanced_df['sentiment_score'] = 0.0
    
    # Process sentiment column if it exists
    if 'sentiment' in enhanced_df.columns:
        logger.info("Processing sentiment column for scoring")
        
        # Convert sentiment text to lowercase for consistent matching
        enhanced_df['sentiment_lower'] = enhanced_df['sentiment'].astype(str).str.lower().str.strip()
        
        # Count original sentiment distribution
        original_sentiment_counts = enhanced_df['sentiment_lower'].value_counts()
        logger.info(f"Original sentiment distribution: {dict(original_sentiment_counts)}")
        
        # Map sentiment values to numerical scores
        mapped_count = 0
        for sentiment_text, score in sentiment_mapping.items():
            mask = enhanced_df['sentiment_lower'] == sentiment_text
            count = mask.sum()
            enhanced_df.loc[mask, 'sentiment_score'] = score
            mapped_count += count
            logger.debug(f"Mapped {count:,} '{sentiment_text}' records to score {score}")
        
        # Handle edge cases for missing or invalid sentiment values
        invalid_sentiment_mask = ~enhanced_df['sentiment_lower'].isin(sentiment_mapping.keys())
        invalid_count = invalid_sentiment_mask.sum()
        
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count:,} records with invalid sentiment values, defaulting to neutral (0.0)")
            invalid_values = enhanced_df.loc[invalid_sentiment_mask, 'sentiment_lower'].unique()
            logger.debug(f"Invalid sentiment values found: {list(invalid_values)}")
        
        logger.info(f"Successfully mapped {mapped_count:,} sentiment values to scores")
        
        # Clean up temporary column
        enhanced_df = enhanced_df.drop(columns=['sentiment_lower'])
    else:
        logger.warning("No 'sentiment' column found, all records will have neutral sentiment score (0.0)")
    
    # Ensure sentiment_score is float type and within valid range
    enhanced_df['sentiment_score'] = pd.to_numeric(enhanced_df['sentiment_score'], errors='coerce')
    
    # Validate sentiment_score range (-1.0 to 1.0)
    out_of_range_mask = (enhanced_df['sentiment_score'] < -1.0) | (enhanced_df['sentiment_score'] > 1.0)
    out_of_range_count = out_of_range_mask.sum()
    
    if out_of_range_count > 0:
        logger.warning(f"Found {out_of_range_count:,} sentiment scores out of range [-1.0, 1.0], clamping to valid range")
        enhanced_df.loc[enhanced_df['sentiment_score'] < -1.0, 'sentiment_score'] = -1.0
        enhanced_df.loc[enhanced_df['sentiment_score'] > 1.0, 'sentiment_score'] = 1.0
    
    # Handle any NaN values in sentiment_score (from conversion errors)
    nan_sentiment_mask = enhanced_df['sentiment_score'].isna()
    nan_count = nan_sentiment_mask.sum()
    
    if nan_count > 0:
        logger.warning(f"Found {nan_count:,} NaN sentiment scores, defaulting to neutral (0.0)")
        enhanced_df.loc[nan_sentiment_mask, 'sentiment_score'] = 0.0
    
    # Add relevance classification - set all records as relevant (True)
    enhanced_df['is_relevant'] = True
    logger.info("Set all records as relevant (is_relevant = True)")
    
    # Ensure is_relevant is boolean type
    enhanced_df['is_relevant'] = enhanced_df['is_relevant'].astype(bool)
    
    # Validate final data types
    if not enhanced_df['sentiment_score'].dtype in ['float64', 'float32']:
        logger.error("sentiment_score column is not float type after processing")
        raise ValueError("Failed to ensure sentiment_score is float type")
    
    if enhanced_df['is_relevant'].dtype != 'bool':
        logger.error("is_relevant column is not boolean type after processing")
        raise ValueError("Failed to ensure is_relevant is boolean type")
    
    # Log enhancement summary
    sentiment_distribution = enhanced_df['sentiment_score'].value_counts().sort_index()
    logger.info("AI Enhancement Summary:")
    logger.info(f"  - Records processed: {len(enhanced_df):,}")
    logger.info(f"  - Sentiment score distribution: {dict(sentiment_distribution)}")
    logger.info(f"  - All records marked as relevant: {enhanced_df['is_relevant'].all()}")
    logger.info(f"  - Data types: sentiment_score={enhanced_df['sentiment_score'].dtype}, is_relevant={enhanced_df['is_relevant'].dtype}")
    
    log_processing_summary("AI Enhancement", len(df), len(enhanced_df), logger=logger)
    return enhanced_df


def validate_required_columns(df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate that all required columns exist in the DataFrame.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_missing_columns)
    """
    missing_columns = []
    
    for column in required_columns:
        if column not in df.columns:
            missing_columns.append(column)
    
    is_valid = len(missing_columns) == 0
    
    if not is_valid:
        logging.error(f"Missing required columns: {missing_columns}")
    
    return is_valid, missing_columns


def unify_datasets(standardized_dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Combine all standardized DataFrames into a single master dataset.
    
    Args:
        standardized_dfs: Dictionary of standardized DataFrames from each source
        
    Returns:
        pd.DataFrame: Unified master dataset with target schema columns
        
    Raises:
        ValueError: If required columns are missing or data validation fails
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info("Starting dataset unification process")
    
    # Define target schema columns as specified in requirements
    target_columns = [
        'feedback_id',
        'source_channel', 
        'timestamp',
        'feedback_text',
        'source_metric',
        'is_relevant',
        'sentiment_score',
        'theme',
        'strategic_goal'
    ]
    
    # Validate that all DataFrames have required columns
    enhanced_dfs = []
    total_records = 0
    
    for source_name, df in standardized_dfs.items():
        logger.info(f"Processing {source_name} for unification: {len(df):,} records")
        
        # Comprehensive schema validation
        is_valid, validation_errors = validate_dataframe_schema(df, target_columns, source_name)
        
        if not is_valid:
            error_context = {"source": source_name, "records": len(df)}
            detailed_error = handle_processing_error(
                ValueError(f"Schema validation failed: {'; '.join(validation_errors)}"),
                f"Unifying {source_name}",
                error_context
            )
            raise ValueError(detailed_error)
        
        # Data integrity validation
        integrity_valid, integrity_errors = validate_data_integrity(df, source_name)
        if not integrity_valid:
            logger.warning(f"Data integrity issues in {source_name} (proceeding with caution):")
            for error in integrity_errors:
                logger.warning(f"  - {error}")
        
        # Data type validation for critical columns
        expected_types = {
            'sentiment_score': 'float',
            'is_relevant': 'bool',
            'timestamp': 'datetime'
        }
        type_valid, type_errors = validate_data_types(df, expected_types, source_name)
        if not type_valid:
            logger.warning(f"Data type issues in {source_name} (will attempt conversion):")
            for error in type_errors:
                logger.warning(f"  - {error}")
        
        # Select only target schema columns
        df_selected = df[target_columns].copy()
        
        # Validate data types for critical columns
        if 'sentiment_score' in df_selected.columns:
            if not df_selected['sentiment_score'].dtype in ['float64', 'float32']:
                logging.warning(f"Converting sentiment_score to float for {source_name}")
                df_selected['sentiment_score'] = pd.to_numeric(df_selected['sentiment_score'], errors='coerce')
        
        if 'is_relevant' in df_selected.columns:
            if df_selected['is_relevant'].dtype != 'bool':
                logging.warning(f"Converting is_relevant to boolean for {source_name}")
                df_selected['is_relevant'] = df_selected['is_relevant'].astype(bool)
        
        if 'timestamp' in df_selected.columns:
            if not pd.api.types.is_datetime64_any_dtype(df_selected['timestamp']):
                logging.warning(f"Converting timestamp to datetime for {source_name}")
                df_selected['timestamp'] = pd.to_datetime(df_selected['timestamp'])
        
        enhanced_dfs.append(df_selected)
        total_records += len(df_selected)
        
        logging.info(f"Successfully processed {source_name}: {len(df_selected)} records")
    
    # Combine all DataFrames
    logging.info(f"Combining {len(enhanced_dfs)} DataFrames with total {total_records} records")
    
    try:
        unified_df = pd.concat(enhanced_dfs, ignore_index=True, sort=False)
    except Exception as e:
        error_msg = f"Failed to concatenate DataFrames: {e}"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Handle duplicate records if any
    initial_count = len(unified_df)
    
    # Check for duplicate feedback_ids
    duplicate_ids = unified_df['feedback_id'].duplicated()
    duplicate_count = duplicate_ids.sum()
    
    if duplicate_count > 0:
        logging.warning(f"Found {duplicate_count} duplicate feedback_ids, keeping first occurrence")
        unified_df = unified_df.drop_duplicates(subset=['feedback_id'], keep='first')
    
    final_count = len(unified_df)
    
    # Ensure data consistency - validate final dataset
    logging.info("Validating unified dataset consistency")
    
    # Check for null feedback_ids
    null_ids = unified_df['feedback_id'].isnull().sum()
    if null_ids > 0:
        error_msg = f"Found {null_ids} null feedback_ids in unified dataset"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Check for empty feedback_text
    empty_text = unified_df['feedback_text'].isnull().sum()
    if empty_text > 0:
        logging.warning(f"Found {empty_text} null feedback_text entries")
    
    # Validate sentiment_score range
    invalid_sentiment = ((unified_df['sentiment_score'] < -1.0) | 
                        (unified_df['sentiment_score'] > 1.0)).sum()
    if invalid_sentiment > 0:
        error_msg = f"Found {invalid_sentiment} sentiment_scores outside valid range [-1.0, 1.0]"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Final validation - ensure all target columns are present
    final_is_valid, final_missing = validate_required_columns(unified_df, target_columns)
    if not final_is_valid:
        error_msg = f"Final dataset missing required columns: {final_missing}"
        logging.error(error_msg)
        raise ValueError(error_msg)
    
    # Log unification summary
    logging.info("=== Dataset Unification Summary ===")
    logging.info(f"Total input records: {total_records}")
    logging.info(f"Records after deduplication: {final_count}")
    logging.info(f"Duplicates removed: {initial_count - final_count}")
    logging.info(f"Final columns: {list(unified_df.columns)}")
    
    # Log source distribution
    source_distribution = unified_df['source_channel'].value_counts()
    logging.info("Records by source channel:")
    for source, count in source_distribution.items():
        logging.info(f"  - {source}: {count:,} records")
    
    # Log data type summary
    logging.info("Final data types:")
    for column in target_columns:
        dtype = unified_df[column].dtype
        logging.info(f"  - {column}: {dtype}")
    
    logging.info("=== End Unification Summary ===")
    
    logging.info(f"Dataset unification completed successfully: {len(unified_df)} records")
    return unified_df


def validate_dataframe_schema(df: pd.DataFrame, required_columns: List[str], 
                             source_name: str = "DataFrame") -> Tuple[bool, List[str]]:
    """
    Comprehensive validation of DataFrame schema and data quality.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        source_name: Name of the data source for error reporting
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_validation_errors)
    """
    logger = logging.getLogger('feedback_enhancement_system')
    validation_errors = []
    
    # Check if DataFrame is None
    if df is None:
        validation_errors.append(f"{source_name}: DataFrame is None")
        return False, validation_errors
    
    # Check if DataFrame is empty
    if df.empty:
        validation_errors.append(f"{source_name}: DataFrame is empty (no rows)")
    
    # Check if DataFrame has columns
    if len(df.columns) == 0:
        validation_errors.append(f"{source_name}: DataFrame has no columns")
        return False, validation_errors
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation_errors.append(f"{source_name}: Missing required columns: {missing_columns}")
    
    # Check for completely null columns
    null_columns = []
    for col in df.columns:
        if df[col].isnull().all():
            null_columns.append(col)
    
    if null_columns:
        validation_errors.append(f"{source_name}: Columns with all null values: {null_columns}")
    
    # Check for duplicate column names
    duplicate_columns = df.columns[df.columns.duplicated()].tolist()
    if duplicate_columns:
        validation_errors.append(f"{source_name}: Duplicate column names: {duplicate_columns}")
    
    # Data quality checks
    if not df.empty:
        # Check for excessive null values (>90% null in any column)
        high_null_columns = []
        for col in df.columns:
            null_percentage = (df[col].isnull().sum() / len(df)) * 100
            if null_percentage > 90:
                high_null_columns.append(f"{col} ({null_percentage:.1f}% null)")
        
        if high_null_columns:
            validation_errors.append(f"{source_name}: Columns with >90% null values: {high_null_columns}")
    
    is_valid = len(validation_errors) == 0
    
    if validation_errors:
        logger.warning(f"Schema validation issues found for {source_name}:")
        for error in validation_errors:
            logger.warning(f"  - {error}")
    else:
        logger.debug(f"Schema validation passed for {source_name}")
    
    return is_valid, validation_errors


def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str], 
                       source_name: str = "DataFrame") -> Tuple[bool, List[str]]:
    """
    Validate that DataFrame columns have expected data types.
    
    Args:
        df: DataFrame to validate
        expected_types: Dictionary mapping column names to expected type strings
        source_name: Name of the data source for error reporting
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_type_errors)
    """
    logger = logging.getLogger('feedback_enhancement_system')
    type_errors = []
    
    for column, expected_type in expected_types.items():
        if column not in df.columns:
            continue  # Skip missing columns (handled by schema validation)
        
        actual_type = str(df[column].dtype)
        
        # Check type compatibility
        type_compatible = False
        if expected_type == 'datetime':
            type_compatible = pd.api.types.is_datetime64_any_dtype(df[column])
        elif expected_type == 'float':
            type_compatible = pd.api.types.is_numeric_dtype(df[column])
        elif expected_type == 'int':
            type_compatible = pd.api.types.is_integer_dtype(df[column])
        elif expected_type == 'bool':
            type_compatible = pd.api.types.is_bool_dtype(df[column])
        elif expected_type == 'string':
            type_compatible = pd.api.types.is_string_dtype(df[column]) or actual_type == 'object'
        
        if not type_compatible:
            type_errors.append(f"{source_name}: Column '{column}' has type '{actual_type}', expected '{expected_type}'")
    
    is_valid = len(type_errors) == 0
    
    if type_errors:
        logger.warning(f"Data type validation issues found for {source_name}:")
        for error in type_errors:
            logger.warning(f"  - {error}")
    else:
        logger.debug(f"Data type validation passed for {source_name}")
    
    return is_valid, type_errors


def validate_data_integrity(df: pd.DataFrame, source_name: str = "DataFrame") -> Tuple[bool, List[str]]:
    """
    Validate data integrity and consistency within the DataFrame.
    
    Args:
        df: DataFrame to validate
        source_name: Name of the data source for error reporting
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_integrity_errors)
    """
    logger = logging.getLogger('feedback_enhancement_system')
    integrity_errors = []
    
    if df.empty:
        return True, []  # Empty DataFrame is technically valid
    
    # Check for duplicate feedback_ids if column exists
    if 'feedback_id' in df.columns:
        duplicate_ids = df['feedback_id'].duplicated()
        duplicate_count = duplicate_ids.sum()
        if duplicate_count > 0:
            integrity_errors.append(f"{source_name}: Found {duplicate_count} duplicate feedback_id values")
    
    # Check sentiment_score range if column exists
    if 'sentiment_score' in df.columns:
        out_of_range = ((df['sentiment_score'] < -1.0) | (df['sentiment_score'] > 1.0)).sum()
        if out_of_range > 0:
            integrity_errors.append(f"{source_name}: Found {out_of_range} sentiment_score values outside [-1.0, 1.0] range")
        
        # Check for NaN sentiment scores
        nan_scores = df['sentiment_score'].isnull().sum()
        if nan_scores > 0:
            integrity_errors.append(f"{source_name}: Found {nan_scores} null sentiment_score values")
    
    # Check for empty feedback_text if column exists
    if 'feedback_text' in df.columns:
        empty_text = df['feedback_text'].isnull().sum()
        completely_empty = (df['feedback_text'].astype(str).str.strip() == '').sum()
        if empty_text > 0:
            integrity_errors.append(f"{source_name}: Found {empty_text} null feedback_text values")
        if completely_empty > 0:
            integrity_errors.append(f"{source_name}: Found {completely_empty} empty feedback_text values")
    
    # Check timestamp validity if column exists
    if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        # Check for future dates (more than 1 day in the future)
        future_dates = (df['timestamp'] > pd.Timestamp.now() + pd.Timedelta(days=1)).sum()
        if future_dates > 0:
            integrity_errors.append(f"{source_name}: Found {future_dates} timestamps in the future")
        
        # Check for very old dates (before 2000)
        old_dates = (df['timestamp'] < pd.Timestamp('2000-01-01')).sum()
        if old_dates > 0:
            integrity_errors.append(f"{source_name}: Found {old_dates} timestamps before year 2000")
    
    is_valid = len(integrity_errors) == 0
    
    if integrity_errors:
        logger.warning(f"Data integrity issues found for {source_name}:")
        for error in integrity_errors:
            logger.warning(f"  - {error}")
    else:
        logger.debug(f"Data integrity validation passed for {source_name}")
    
    return is_valid, integrity_errors


def create_error_recovery_suggestions(validation_errors: List[str]) -> List[str]:
    """
    Generate actionable suggestions for resolving validation errors.
    
    Args:
        validation_errors: List of validation error messages
        
    Returns:
        List[str]: List of suggested recovery actions
    """
    suggestions = []
    
    for error in validation_errors:
        error_lower = error.lower()
        
        if 'missing required columns' in error_lower:
            suggestions.append("Check input CSV file structure and ensure all required columns are present")
        elif 'duplicate column names' in error_lower:
            suggestions.append("Remove duplicate column names from input CSV files")
        elif 'empty' in error_lower and 'dataframe' in error_lower:
            suggestions.append("Verify input CSV files contain data and are not corrupted")
        elif 'null values' in error_lower:
            suggestions.append("Clean input data to remove excessive null values or provide default values")
        elif 'sentiment_score' in error_lower and 'range' in error_lower:
            suggestions.append("Review sentiment scoring logic and ensure values are between -1.0 and 1.0")
        elif 'duplicate feedback_id' in error_lower:
            suggestions.append("Ensure unique customer_id values in source data or modify ID generation logic")
        elif 'timestamp' in error_lower:
            suggestions.append("Verify timestamp format and values in source CSV files")
        elif 'data type' in error_lower or 'type' in error_lower:
            suggestions.append("Check data types in source CSV files and ensure proper formatting")
        elif 'file not found' in error_lower or 'missing' in error_lower:
            suggestions.append("Ensure all required CSV files are present in the input directory")
        elif 'permission' in error_lower:
            suggestions.append("Check file and directory permissions for read/write access")
        else:
            suggestions.append("Review the specific error message and check corresponding data or configuration")
    
    return list(set(suggestions))  # Remove duplicates


def validate_file_path(file_path: str, mode: str = 'w') -> Tuple[bool, str]:
    """
    Validate file path for read/write operations with comprehensive error handling.
    
    Args:
        file_path: Path to the file
        mode: File access mode ('r' for read, 'w' for write)
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    logger = logging.getLogger('feedback_enhancement_system')
    
    try:
        path_obj = Path(file_path)
        
        if mode == 'w':
            # Check if parent directory exists or can be created
            parent_dir = path_obj.parent
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {parent_dir}")
                except PermissionError as e:
                    return False, f"Permission denied creating directory {parent_dir}: {e}"
                except OSError as e:
                    return False, f"OS error creating directory {parent_dir}: {e}"
                except Exception as e:
                    return False, f"Cannot create parent directory {parent_dir}: {e}"
            
            # Test write permissions by creating a temporary file
            try:
                test_file = parent_dir / f".write_test_{os.getpid()}"
                test_file.touch()
                test_file.unlink()
                logger.debug(f"Write permission verified for directory: {parent_dir}")
            except PermissionError as e:
                return False, f"No write permission for directory {parent_dir}: {e}"
            except OSError as e:
                return False, f"OS error testing write permission in {parent_dir}: {e}"
            except Exception as e:
                return False, f"Cannot write to directory {parent_dir}: {e}"
        
        elif mode == 'r':
            # Check if file exists and is readable
            if not path_obj.exists():
                return False, f"File does not exist: {file_path}"
            
            if not path_obj.is_file():
                return False, f"Path is not a file: {file_path}"
            
            # Test read permissions
            try:
                with open(path_obj, 'r') as f:
                    f.read(1)  # Try to read one character
                logger.debug(f"Read permission verified for file: {file_path}")
            except PermissionError as e:
                return False, f"No read permission for file {file_path}: {e}"
            except Exception as e:
                return False, f"Cannot read file {file_path}: {e}"
        
        return True, ""
        
    except Exception as e:
        return False, f"File path validation error: {e}"


def handle_processing_error(error: Exception, step_name: str, context: Dict = None) -> str:
    """
    Handle processing errors with context-aware error messages and recovery suggestions.
    
    Args:
        error: The exception that occurred
        step_name: Name of the processing step where error occurred
        context: Optional dictionary with additional context information
        
    Returns:
        str: Formatted error message with recovery suggestions
    """
    logger = logging.getLogger('feedback_enhancement_system')
    
    error_type = type(error).__name__
    error_message = str(error)
    
    # Create detailed error message
    detailed_message = f"Error in {step_name}: {error_type} - {error_message}"
    
    if context:
        context_info = ", ".join([f"{k}={v}" for k, v in context.items()])
        detailed_message += f" (Context: {context_info})"
    
    # Generate recovery suggestions based on error type
    suggestions = []
    
    if isinstance(error, FileNotFoundError):
        suggestions.extend([
            "Verify that all required CSV files are present in the input directory",
            "Check file names match expected patterns exactly",
            "Ensure the input directory path is correct"
        ])
    elif isinstance(error, pd.errors.EmptyDataError):
        suggestions.extend([
            "Check that CSV files contain data and are not empty",
            "Verify CSV file format and structure",
            "Ensure files are not corrupted"
        ])
    elif isinstance(error, pd.errors.ParserError):
        suggestions.extend([
            "Verify CSV file format and encoding",
            "Check for malformed CSV structure (quotes, delimiters)",
            "Ensure consistent column structure across all rows"
        ])
    elif isinstance(error, ValueError):
        if "column" in error_message.lower():
            suggestions.extend([
                "Check that all required columns exist in source data",
                "Verify column names match expected schema",
                "Ensure data types are compatible with processing requirements"
            ])
        else:
            suggestions.extend([
                "Verify data values are within expected ranges",
                "Check for data type compatibility issues",
                "Review data quality and format requirements"
            ])
    elif isinstance(error, (PermissionError, OSError)):
        suggestions.extend([
            "Check file and directory permissions",
            "Ensure sufficient disk space is available",
            "Verify write access to output directory",
            "Check if files are locked by other processes"
        ])
    elif isinstance(error, KeyError):
        suggestions.extend([
            "Verify that all expected columns exist in the data",
            "Check column name spelling and case sensitivity",
            "Review data schema requirements"
        ])
    else:
        suggestions.extend([
            "Review the error details and check data quality",
            "Verify system resources (memory, disk space)",
            "Check for data corruption or format issues"
        ])
    
    # Log the error and suggestions
    logger.error(detailed_message)
    logger.info("Recovery suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        logger.info(f"  {i}. {suggestion}")
    
    return detailed_message


def export_master_csv(df: pd.DataFrame, output_path: str) -> bool:
    """
    Save the unified dataset to CSV format as enriched_feedback_master.csv.
    
    Args:
        df: Unified master dataset DataFrame
        output_path: Full path where the CSV file should be saved
        
    Returns:
        bool: True if export successful, False otherwise
        
    Raises:
        ValueError: If DataFrame is empty or invalid
        IOError: If file cannot be written
    """
    logger = logging.getLogger('feedback_enhancement_system')
    logger.info(f"Starting CSV export to: {output_path}")
    
    # Comprehensive DataFrame validation
    target_columns = [
        'feedback_id', 'source_channel', 'timestamp', 'feedback_text',
        'source_metric', 'is_relevant', 'sentiment_score', 'theme', 'strategic_goal'
    ]
    
    is_valid, validation_errors = validate_dataframe_schema(df, target_columns, "Export DataFrame")
    
    if not is_valid:
        error_context = {"output_path": output_path, "records": len(df) if df is not None else 0}
        detailed_error = handle_processing_error(
            ValueError(f"Export validation failed: {'; '.join(validation_errors)}"),
            "CSV Export",
            error_context
        )
        raise ValueError(detailed_error)
    
    # Data integrity validation before export
    integrity_valid, integrity_errors = validate_data_integrity(df, "Export DataFrame")
    if not integrity_valid:
        logger.warning("Data integrity issues found before export (proceeding with caution):")
        for error in integrity_errors:
            logger.warning(f"  - {error}")
    
    # Validate file path and directory creation
    is_valid, error_message = validate_file_path(output_path, mode='w')
    
    if not is_valid:
        error_context = {"output_path": output_path}
        detailed_error = handle_processing_error(
            IOError(error_message),
            "CSV Export Path Validation",
            error_context
        )
        raise IOError(detailed_error)
    
    try:
        # Export CSV without DataFrame index as specified in requirements
        df.to_csv(output_path, index=False)
        
        # Verify the file was created successfully
        output_file = Path(output_path)
        
        if not output_file.exists():
            error_msg = f"Export failed: Output file was not created at {output_path}"
            logging.error(error_msg)
            raise IOError(error_msg)
        
        # Get file size for confirmation
        file_size = output_file.stat().st_size
        
        # Verify file is not empty
        if file_size == 0:
            error_msg = f"Export failed: Output file is empty at {output_path}"
            logging.error(error_msg)
            raise IOError(error_msg)
        
        # Log export success with details
        logging.info(f"CSV export completed successfully:")
        logging.info(f"  - File path: {output_path}")
        logging.info(f"  - Records exported: {len(df):,}")
        logging.info(f"  - Columns exported: {len(df.columns)}")
        logging.info(f"  - File size: {file_size:,} bytes")
        
        # Log column names for verification
        logging.debug(f"  - Exported columns: {list(df.columns)}")
        
        return True
        
    except PermissionError as e:
        error_msg = f"Permission denied writing to {output_path}: {e}"
        logging.error(error_msg)
        raise IOError(error_msg)
    
    except OSError as e:
        error_msg = f"OS error writing to {output_path}: {e}"
        logging.error(error_msg)
        raise IOError(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error during CSV export to {output_path}: {e}"
        logging.error(error_msg)
        raise IOError(error_msg)


def main() -> int:
    """
    Main execution function for the feedback enhancement system.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    start_time = time.time()
    logger = None
    
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Set up logging
        logger = setup_logging(args.log_level)
        
        logger.info("=" * 60)
        logger.info("FEEDBACK ENHANCEMENT SYSTEM - STARTING EXECUTION")
        logger.info("=" * 60)
        logger.info(f"Configuration:")
        logger.info(f"  - Input directory: {args.input_dir}")
        logger.info(f"  - Output directory: {args.output_dir}")
        logger.info(f"  - Output filename: {args.output_filename}")
        logger.info(f"  - Log level: {args.log_level}")
        
        # Step 1: Validate directories
        with ProcessingTimer("Directory Validation", logger):
            if not validate_input_directory(args.input_dir):
                logger.error("Input directory validation failed")
                return 1
                
            if not validate_output_directory(args.output_dir):
                logger.error("Output directory validation failed")
                return 1
        
        # Step 2: Load CSV data sources
        with ProcessingTimer("Data Loading", logger):
            try:
                dataframes = load_csv_sources(args.input_dir)
                total_input_records = sum(len(df) for df in dataframes.values())
                logger.info(f"Data loading completed: {total_input_records:,} total records from {len(dataframes)} sources")
            except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, ValueError) as e:
                logger.error("=" * 50)
                logger.error("DATA LOADING FAILED")
                logger.error("=" * 50)
                
                # Generate and log recovery suggestions
                validation_errors = [str(e)]
                suggestions = create_error_recovery_suggestions(validation_errors)
                logger.error("Recovery suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    logger.error(f"  {i}. {suggestion}")
                
                return 1
        
        # Step 3: Schema standardization
        with ProcessingTimer("Schema Standardization", logger):
            try:
                standardized_dfs = {}
                
                # Standardize each data source
                if 'apple_reviews' in dataframes:
                    standardized_dfs['apple_reviews'] = standardize_apple_reviews(dataframes['apple_reviews'])
                    
                if 'google_reviews' in dataframes:
                    standardized_dfs['google_reviews'] = standardize_google_reviews(dataframes['google_reviews'])
                    
                if 'twitter_mentions' in dataframes:
                    standardized_dfs['twitter_mentions'] = standardize_twitter_mentions(dataframes['twitter_mentions'])
                    
                if 'sales_notes' in dataframes:
                    standardized_dfs['sales_notes'] = standardize_sales_notes(dataframes['sales_notes'])
                
                total_standardized_records = sum(len(df) for df in standardized_dfs.values())
                log_processing_summary("Schema Standardization", total_input_records, 
                                     total_standardized_records, logger=logger)
                
            except Exception as e:
                logger.error("=" * 50)
                logger.error("SCHEMA STANDARDIZATION FAILED")
                logger.error("=" * 50)
                
                # Generate and log recovery suggestions
                validation_errors = [str(e)]
                suggestions = create_error_recovery_suggestions(validation_errors)
                logger.error("Recovery suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    logger.error(f"  {i}. {suggestion}")
                
                logger.debug("Full traceback:", exc_info=True)
                return 1
        
        # Step 4: AI Enhancement
        with ProcessingTimer("AI Enhancement", logger):
            try:
                enhanced_dfs = {}
                for source_name, df in standardized_dfs.items():
                    enhanced_dfs[source_name] = enhance_with_ai_insights(df)
                
                total_enhanced_records = sum(len(df) for df in enhanced_dfs.values())
                log_processing_summary("AI Enhancement", total_standardized_records, 
                                     total_enhanced_records, logger=logger)
                
            except Exception as e:
                logger.error("=" * 50)
                logger.error("AI ENHANCEMENT FAILED")
                logger.error("=" * 50)
                
                # Generate and log recovery suggestions
                validation_errors = [str(e)]
                suggestions = create_error_recovery_suggestions(validation_errors)
                logger.error("Recovery suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    logger.error(f"  {i}. {suggestion}")
                
                logger.debug("Full traceback:", exc_info=True)
                return 1
        
        # Step 5: Data Unification
        with ProcessingTimer("Data Unification", logger):
            try:
                unified_df = unify_datasets(enhanced_dfs)
                log_processing_summary("Data Unification", total_enhanced_records, 
                                     len(unified_df), logger=logger)
                
            except Exception as e:
                logger.error("=" * 50)
                logger.error("DATA UNIFICATION FAILED")
                logger.error("=" * 50)
                
                # Generate and log recovery suggestions
                validation_errors = [str(e)]
                suggestions = create_error_recovery_suggestions(validation_errors)
                logger.error("Recovery suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    logger.error(f"  {i}. {suggestion}")
                
                logger.debug("Full traceback:", exc_info=True)
                return 1
        
        # Step 6: CSV Export
        output_path = Path(args.output_dir) / args.output_filename
        with ProcessingTimer("CSV Export", logger):
            try:
                success = export_master_csv(unified_df, str(output_path))
                if not success:
                    logger.error("CSV export failed")
                    return 1
                    
            except (ValueError, IOError) as e:
                logger.error("=" * 50)
                logger.error("CSV EXPORT FAILED")
                logger.error("=" * 50)
                
                # Generate and log recovery suggestions
                validation_errors = [str(e)]
                suggestions = create_error_recovery_suggestions(validation_errors)
                logger.error("Recovery suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    logger.error(f"  {i}. {suggestion}")
                
                return 1
        
        # Final summary
        total_time = time.time() - start_time
        logger.info("=" * 60)
        logger.info("EXECUTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Processing Summary:")
        logger.info(f"  - Total execution time: {total_time:.2f} seconds")
        logger.info(f"  - Input records processed: {total_input_records:,}")
        logger.info(f"  - Final records exported: {len(unified_df):,}")
        logger.info(f"  - Data sources processed: {len(dataframes)}")
        logger.info(f"  - Output file: {output_path}")
        logger.info(f"  - Processing rate: {total_input_records/total_time:.0f} records/second")
        
        # Log final data distribution by source
        source_distribution = unified_df['source_channel'].value_counts()
        logger.info("Final data distribution:")
        for source, count in source_distribution.items():
            percentage = (count / len(unified_df)) * 100
            logger.info(f"  - {source}: {count:,} records ({percentage:.1f}%)")
        
        return 0
        
    except KeyboardInterrupt:
        if logger:
            logger.info("Process interrupted by user (Ctrl+C)")
        else:
            print("Process interrupted by user")
        return 1
    except Exception as e:
        if logger:
            logger.error(f"Unexpected error occurred: {e}")
            logger.debug("Full traceback:", exc_info=True)
        else:
            print(f"Unexpected error occurred: {e}")
        return 1
    finally:
        if logger:
            total_time = time.time() - start_time
            logger.info(f"Total execution time: {total_time:.2f} seconds")
            logger.info("Feedback Enhancement System execution ended")


if __name__ == "__main__":
    sys.exit(main())