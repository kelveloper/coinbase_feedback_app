"""
Data loading module for Advanced Trade Insight Engine.

This module handles loading and validation of CSV files from multiple sources:
- iOS App Store reviews
- Google Play Store reviews  
- Internal sales notes
- Twitter mentions
"""

import pandas as pd
import os
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expected CSV files and their identifiers
EXPECTED_FILES = {
    'ios_reviews': 'coinbase_advance_apple_reviews.csv',
    'android_reviews': 'coinbase_advanceGoogle_Play.csv', 
    'sales_notes': 'coinbase_advance_internal_sales_notes.csv',
    'twitter_mentions': 'coinbase_advanced_twitter_mentions.csv'
}

# Required columns for each source type
REQUIRED_COLUMNS = {
    'ios_reviews': ['customer_id', 'source', 'username', 'timestamp', 'rating', 'sentiment', 'review_text', 'theme', 'severity', 'strategic_goal'],
    'android_reviews': ['customer_id', 'source', 'username', 'timestamp', 'rating', 'sentiment', 'review_text', 'theme', 'severity', 'strategic_goal'],
    'sales_notes': ['customer_id', 'source', 'account_name', 'timestamp', 'sentiment', 'note_text', 'theme', 'severity', 'strategic_goal', 'ARR_impact_estimate_USD'],
    'twitter_mentions': ['customer_id', 'source', 'handle', 'followers', 'timestamp', 'sentiment', 'tweet_text', 'theme', 'severity', 'strategic_goal']
}


def validate_file_exists(file_path: str) -> bool:
    """
    Validate that a CSV file exists and is readable.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        bool: True if file exists and is readable, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
        
    if not os.path.isfile(file_path):
        logger.error(f"Path is not a file: {file_path}")
        return False
        
    if not os.access(file_path, os.R_OK):
        logger.error(f"File is not readable: {file_path}")
        return False
        
    return True


def validate_csv_structure(df: pd.DataFrame, source_type: str, file_path: str) -> bool:
    """
    Validate that a DataFrame has the required columns for its source type.
    
    Args:
        df: DataFrame to validate
        source_type: Type of source (ios_reviews, android_reviews, etc.)
        file_path: Path to the original file (for error reporting)
        
    Returns:
        bool: True if structure is valid, False otherwise
    """
    if source_type not in REQUIRED_COLUMNS:
        logger.error(f"Unknown source type: {source_type}")
        return False
        
    required_cols = REQUIRED_COLUMNS[source_type]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        logger.error(f"Missing required columns in {file_path}: {missing_cols}")
        return False
        
    if df.empty:
        logger.warning(f"File {file_path} is empty")
        return False
        
    return True


def load_csv_file(file_path: str, source_type: str) -> Optional[pd.DataFrame]:
    """
    Load a single CSV file with validation and error handling.
    
    Args:
        file_path: Path to the CSV file
        source_type: Type of source for validation
        
    Returns:
        DataFrame if successful, None if failed
    """
    try:
        # Validate file exists
        if not validate_file_exists(file_path):
            return None
            
        # Load CSV file
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} records from {file_path}")
        
        # Validate structure
        if not validate_csv_structure(df, source_type, file_path):
            return None
            
        # Convert timestamp column to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        return df
        
    except pd.errors.EmptyDataError:
        logger.error(f"Empty CSV file: {file_path}")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"CSV parsing error in {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error loading {file_path}: {str(e)}")
        return None


def load_all_csv_files(data_directory: str = "csv_mock_data") -> Dict[str, pd.DataFrame]:
    """
    Load all expected CSV files from the specified directory.
    
    Args:
        data_directory: Directory containing the CSV files
        
    Returns:
        Dictionary mapping source types to DataFrames
    """
    loaded_data = {}
    
    for source_type, filename in EXPECTED_FILES.items():
        file_path = os.path.join(data_directory, filename)
        
        logger.info(f"Loading {source_type} from {file_path}")
        df = load_csv_file(file_path, source_type)
        
        if df is not None:
            loaded_data[source_type] = df
            logger.info(f"Successfully loaded {source_type}: {len(df)} records")
        else:
            logger.warning(f"Failed to load {source_type} from {file_path}")
    
    return loaded_data


def get_loading_summary(loaded_data: Dict[str, pd.DataFrame]) -> Dict[str, int]:
    """
    Generate a summary of loaded data.
    
    Args:
        loaded_data: Dictionary of loaded DataFrames
        
    Returns:
        Dictionary with record counts per source
    """
    summary = {}
    total_records = 0
    
    for source_type, df in loaded_data.items():
        record_count = len(df)
        summary[source_type] = record_count
        total_records += record_count
        
    summary['total_records'] = total_records
    summary['sources_loaded'] = len(loaded_data)
    summary['sources_expected'] = len(EXPECTED_FILES)
    
    return summary


def validate_data_directory(data_directory: str) -> Tuple[bool, List[str]]:
    """
    Validate that the data directory exists and contains expected files.
    
    Args:
        data_directory: Path to the data directory
        
    Returns:
        Tuple of (is_valid, list_of_missing_files)
    """
    if not os.path.exists(data_directory):
        logger.error(f"Data directory does not exist: {data_directory}")
        return False, list(EXPECTED_FILES.values())
        
    if not os.path.isdir(data_directory):
        logger.error(f"Path is not a directory: {data_directory}")
        return False, list(EXPECTED_FILES.values())
        
    missing_files = []
    for source_type, filename in EXPECTED_FILES.items():
        file_path = os.path.join(data_directory, filename)
        if not os.path.exists(file_path):
            missing_files.append(filename)
            
    if missing_files:
        logger.warning(f"Missing files in {data_directory}: {missing_files}")
        
    return len(missing_files) == 0, missing_files