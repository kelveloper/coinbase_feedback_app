"""
Scoring Engine Module for Advanced Trade Insight Engine

This module provides functions to calculate source weights and impact scores
for customer feedback records. The scoring system prioritizes feedback based
on business impact, sentiment analysis, and strategic alignment.

Functions:
    calculate_source_weight: Calculate credibility weight based on source channel
    calculate_impact_score: Calculate business impact score for prioritization
    enrich_dataframe_with_scores: Apply scoring to entire DataFrame
"""

import pandas as pd
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_source_weight(record: pd.Series) -> float:
    """
    Calculate source credibility weight based on channel-specific logic.
    
    Weighting formulas by source:
    - Internal Sales Notes: ARR_impact_estimate_USD / 50000
    - Twitter: followers / 20000  
    - App Store (iOS/Google Play): rating + (helpful_votes / 10)
    - Default: 1.0
    
    Args:
        record (pd.Series): A single row from the feedback DataFrame
        
    Returns:
        float: Source weight value (minimum 0.1, default 1.0)
        
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """
    try:
        source = record.get('source', '').lower()
        
        # Internal Sales Notes weighting
        if 'internal sales' in source or 'sales' in source:
            arr_impact = record.get('ARR_impact_estimate_USD', 0)
            if pd.isna(arr_impact) or arr_impact is None:
                arr_impact = 0
            
            try:
                arr_impact = float(arr_impact)
                weight = arr_impact / 50000
                return max(weight, 0.1)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                logger.warning(f"Invalid ARR_impact_estimate_USD value: {arr_impact}")
                return 1.0
        
        # Twitter weighting
        elif 'twitter' in source or 'x' in source:
            followers = record.get('followers', 0)
            if pd.isna(followers) or followers is None:
                followers = 0
                
            try:
                followers = float(followers)
                weight = followers / 20000
                return max(weight, 0.1)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                logger.warning(f"Invalid followers value: {followers}")
                return 1.0
        
        # App Store weighting (iOS and Google Play)
        elif 'app store' in source or 'ios' in source or 'google play' in source or 'android' in source:
            rating = record.get('rating', 0)
            helpful_votes = record.get('helpful_votes', 0)
            
            # Handle missing values
            if pd.isna(rating) or rating is None:
                rating = 0
            if pd.isna(helpful_votes) or helpful_votes is None:
                helpful_votes = 0
                
            try:
                rating = float(rating)
                helpful_votes = float(helpful_votes)
                weight = rating + (helpful_votes / 10)
                return max(weight, 0.1)  # Minimum weight of 0.1
            except (ValueError, TypeError):
                logger.warning(f"Invalid rating or helpful_votes values: {rating}, {helpful_votes}")
                return 1.0
        
        # Default weight for unknown sources
        else:
            return 1.0
            
    except (KeyError, AttributeError, TypeError) as e:
        logger.warning(f"Error calculating source weight: {e}")
        return 1.0


def calculate_impact_score(record: pd.Series, source_weight: Optional[float] = None) -> float:
    """
    Calculate business impact score combining sentiment, severity, source weight, and strategic alignment.
    
    Formula: (sentiment_value × severity) × source_weight × strategic_multiplier
    
    Sentiment values: negative=1.5, neutral=0.5, positive=0.1
    Strategic multiplier: aligned goals=2.0, others=1.0
    
    Args:
        record (pd.Series): A single row from the feedback DataFrame
        source_weight (Optional[float]): Pre-calculated source weight (will calculate if None)
        
    Returns:
        float: Impact score for business prioritization
        
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    try:
        # Get sentiment value
        sentiment = record.get('sentiment', 'neutral')
        if pd.isna(sentiment):
            sentiment = 'neutral'
        
        sentiment_str = str(sentiment).lower().strip()
        sentiment_values = {
            'negative': 1.5,
            'neutral': 0.5,
            'positive': 0.1
        }
        sentiment_value = sentiment_values.get(sentiment_str, 0.5)
        
        # Get severity
        severity = record.get('severity', 1.0)
        if pd.isna(severity) or severity is None:
            severity = 1.0
        
        try:
            severity = float(severity)
        except (ValueError, TypeError):
            logger.warning(f"Invalid severity value: {severity}")
            severity = 1.0
        
        # Calculate or use provided source weight
        if source_weight is None:
            source_weight = calculate_source_weight(record)
        
        # Get strategic goal multiplier
        strategic_goal = record.get('strategic_goal', '')
        if pd.isna(strategic_goal):
            strategic_goal = ''
        
        strategic_goal_str = str(strategic_goal).strip()
        
        # Define aligned strategic goals (these get 2.0 multiplier)
        aligned_goals = {
            'Growth', 'Trust&Safety', 'Onchain Adoption', 
            'CX Efficiency', 'Compliance'
        }
        
        strategic_multiplier = 2.0 if strategic_goal_str in aligned_goals else 1.0
        
        # Calculate final impact score
        impact_score = (sentiment_value * severity) * source_weight * strategic_multiplier
        
        return round(impact_score, 4)
        
    except (KeyError, AttributeError, TypeError) as e:
        logger.warning(f"Error calculating impact score: {e}")
        return 0.0


def enrich_dataframe_with_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply source weighting and impact scoring to all records in a DataFrame.
    
    This function calculates source weights and impact scores for each row
    in the DataFrame, adding the respective columns.
    
    Args:
        df (pd.DataFrame): DataFrame containing feedback records
        
    Returns:
        pd.DataFrame: DataFrame with source_weight and impact_score columns added
        
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 4.5
    """
    if df.empty:
        return df
        
    # Create a copy to avoid modifying the original DataFrame
    enriched_df = df.copy()
    
    # Calculate source weights for all rows
    enriched_df['source_weight'] = enriched_df.apply(calculate_source_weight, axis=1)
    
    # Calculate impact scores using the calculated source weights
    def calculate_impact_with_weight(row):
        return calculate_impact_score(row, row['source_weight'])
    
    enriched_df['impact_score'] = enriched_df.apply(calculate_impact_with_weight, axis=1)
    
    logger.info(f"Enriched {len(enriched_df)} records with source weights and impact scores")
    
    return enriched_df