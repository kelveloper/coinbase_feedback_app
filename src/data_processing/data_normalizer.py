"""
Data normalization module for Advanced Trade Insight Engine.

This module handles the normalization and unification of data from multiple sources
into a standardized format for analysis.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Column mapping configurations for each source type
COLUMN_MAPPINGS = {
    'ios_reviews': {
        'feedback_text_source': 'review_text',
        'author_handle_source': 'username',
        'source_channel': 'iOS App Store'
    },
    'android_reviews': {
        'feedback_text_source': 'review_text', 
        'author_handle_source': 'username',
        'source_channel': 'Google Play Store'
    },
    'sales_notes': {
        'feedback_text_source': 'note_text',
        'author_handle_source': 'account_name', 
        'source_channel': 'Internal Sales Notes'
    },
    'twitter_mentions': {
        'feedback_text_source': 'tweet_text',
        'author_handle_source': 'handle',
        'source_channel': 'Twitter (X)'
    }
}

# Standard columns that should be present in the unified DataFrame
STANDARD_COLUMNS = [
    'customer_id', 'source_channel', 'feedback_text', 'author_handle', 
    'timestamp', 'sentiment', 'theme', 'severity', 'strategic_goal'
]

# Source-specific columns to preserve
SOURCE_SPECIFIC_COLUMNS = {
    'ios_reviews': ['rating', 'helpful_votes', 'region', 'device', 'app_version'],
    'android_reviews': ['rating', 'helpful_votes', 'region', 'device', 'app_version'],
    'sales_notes': ['ARR_impact_estimate_USD', 'account_type', 'deal_stage', 'requested_feature', 'contact_role', 'region'],
    'twitter_mentions': ['followers', 'verified', 'likes', 'retweets', 'reply_count']
}


def normalize_feedback_text(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """
    Normalize feedback text column from source-specific names to 'feedback_text'.
    
    Args:
        df: DataFrame to normalize
        source_type: Type of source (ios_reviews, android_reviews, etc.)
        
    Returns:
        DataFrame with normalized feedback_text column
    """
    if source_type not in COLUMN_MAPPINGS:
        logger.error(f"Unknown source type for feedback text mapping: {source_type}")
        return df
        
    mapping = COLUMN_MAPPINGS[source_type]
    source_col = mapping['feedback_text_source']
    
    if source_col not in df.columns:
        logger.error(f"Source column '{source_col}' not found in {source_type} data")
        return df
        
    # Create normalized column
    df = df.copy()
    df['feedback_text'] = df[source_col]
    
    logger.info(f"Normalized feedback text for {source_type}: {source_col} -> feedback_text")
    return df


def normalize_author_handle(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """
    Normalize author handle column from source-specific names to 'author_handle'.
    
    Args:
        df: DataFrame to normalize
        source_type: Type of source (ios_reviews, android_reviews, etc.)
        
    Returns:
        DataFrame with normalized author_handle column
    """
    if source_type not in COLUMN_MAPPINGS:
        logger.error(f"Unknown source type for author handle mapping: {source_type}")
        return df
        
    mapping = COLUMN_MAPPINGS[source_type]
    source_col = mapping['author_handle_source']
    
    if source_col not in df.columns:
        logger.error(f"Source column '{source_col}' not found in {source_type} data")
        return df
        
    # Create normalized column
    df = df.copy()
    df['author_handle'] = df[source_col]
    
    logger.info(f"Normalized author handle for {source_type}: {source_col} -> author_handle")
    return df


def add_source_channel(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """
    Add source_channel column to identify the data origin.
    
    Args:
        df: DataFrame to add source channel to
        source_type: Type of source (ios_reviews, android_reviews, etc.)
        
    Returns:
        DataFrame with source_channel column added
    """
    if source_type not in COLUMN_MAPPINGS:
        logger.error(f"Unknown source type for source channel: {source_type}")
        return df
        
    mapping = COLUMN_MAPPINGS[source_type]
    source_channel = mapping['source_channel']
    
    df = df.copy()
    df['source_channel'] = source_channel
    
    logger.info(f"Added source_channel for {source_type}: {source_channel}")
    return df


def normalize_single_source(df: pd.DataFrame, source_type: str) -> pd.DataFrame:
    """
    Apply all normalization steps to a single source DataFrame.
    
    Args:
        df: DataFrame to normalize
        source_type: Type of source (ios_reviews, android_reviews, etc.)
        
    Returns:
        Normalized DataFrame
    """
    logger.info(f"Starting normalization for {source_type}")
    
    # Apply all normalization steps
    df_normalized = df.copy()
    df_normalized = normalize_feedback_text(df_normalized, source_type)
    df_normalized = normalize_author_handle(df_normalized, source_type)
    df_normalized = add_source_channel(df_normalized, source_type)
    
    logger.info(f"Completed normalization for {source_type}")
    return df_normalized


def unify_dataframes(loaded_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Unify multiple normalized DataFrames into a single DataFrame.
    
    Args:
        loaded_data: Dictionary mapping source types to DataFrames
        
    Returns:
        Unified DataFrame with all sources combined
    """
    if not loaded_data:
        logger.warning("No data provided for unification")
        return pd.DataFrame()
        
    normalized_dfs = []
    
    # Normalize each source
    for source_type, df in loaded_data.items():
        if df is None or df.empty:
            logger.warning(f"Skipping empty DataFrame for {source_type}")
            continue
            
        normalized_df = normalize_single_source(df, source_type)
        normalized_dfs.append(normalized_df)
        
    if not normalized_dfs:
        logger.error("No valid DataFrames to unify")
        return pd.DataFrame()
        
    # Combine all normalized DataFrames
    unified_df = pd.concat(normalized_dfs, ignore_index=True, sort=False)
    
    logger.info(f"Unified {len(normalized_dfs)} sources into DataFrame with {len(unified_df)} total records")
    return unified_df


def validate_unified_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate that the unified DataFrame has the expected structure.
    
    Args:
        df: Unified DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    if df.empty:
        logger.error("Unified DataFrame is empty")
        return False
        
    # Check for required standard columns
    missing_columns = [col for col in STANDARD_COLUMNS if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns in unified DataFrame: {missing_columns}")
        return False
        
    # Check for duplicate customer_ids (should be unique across all sources)
    if df['customer_id'].duplicated().any():
        duplicate_count = df['customer_id'].duplicated().sum()
        logger.warning(f"Found {duplicate_count} duplicate customer_ids in unified DataFrame")
        
    # Validate source_channel values
    expected_channels = set(mapping['source_channel'] for mapping in COLUMN_MAPPINGS.values())
    actual_channels = set(df['source_channel'].unique())
    unexpected_channels = actual_channels - expected_channels
    
    if unexpected_channels:
        logger.warning(f"Unexpected source channels found: {unexpected_channels}")
        
    logger.info(f"Unified DataFrame validation completed: {len(df)} records, {len(df.columns)} columns")
    return True


def get_normalization_summary(unified_df: pd.DataFrame) -> Dict[str, any]:
    """
    Generate a summary of the normalization process.
    
    Args:
        unified_df: The unified DataFrame
        
    Returns:
        Dictionary with normalization statistics
    """
    if unified_df.empty:
        return {
            'total_records': 0,
            'sources': [],
            'columns': [],
            'feedback_text_coverage': 0,
            'author_handle_coverage': 0
        }
        
    # Count records by source
    source_counts = unified_df['source_channel'].value_counts().to_dict()
    
    # Calculate coverage for key normalized fields
    feedback_coverage = (unified_df['feedback_text'].notna().sum() / len(unified_df)) * 100
    author_coverage = (unified_df['author_handle'].notna().sum() / len(unified_df)) * 100
    
    summary = {
        'total_records': len(unified_df),
        'sources': list(source_counts.keys()),
        'source_counts': source_counts,
        'columns': list(unified_df.columns),
        'feedback_text_coverage': round(feedback_coverage, 2),
        'author_handle_coverage': round(author_coverage, 2),
        'timestamp_range': {
            'earliest': unified_df['timestamp'].min() if 'timestamp' in unified_df.columns else None,
            'latest': unified_df['timestamp'].max() if 'timestamp' in unified_df.columns else None
        }
    }
    
    return summary


def normalize_and_unify_data(loaded_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Main function to normalize and unify data from multiple sources.
    
    Args:
        loaded_data: Dictionary mapping source types to DataFrames
        
    Returns:
        Unified and normalized DataFrame
    """
    logger.info("Starting data normalization and unification process")
    
    # Unify the data
    unified_df = unify_dataframes(loaded_data)
    
    # Validate the result
    if not validate_unified_dataframe(unified_df):
        logger.error("Unified DataFrame validation failed")
        return pd.DataFrame()
        
    # Generate and log summary
    summary = get_normalization_summary(unified_df)
    logger.info(f"Normalization complete: {summary['total_records']} records from {len(summary['sources'])} sources")
    
    return unified_df