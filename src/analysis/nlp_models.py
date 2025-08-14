"""
NLP Models Module for Advanced Trade Insight Engine

This module provides functions to extract sentiment, theme, and strategic goal
information from customer feedback records. For the MVP implementation, it uses
pre-enriched data from CSV columns rather than actual NLP model inference.

Functions:
    get_sentiment: Extract sentiment classification from feedback record
    get_theme: Extract theme categorization from feedback record  
    get_strategic_goal: Extract strategic goal alignment from feedback record
"""

import pandas as pd
from typing import Optional


def get_sentiment(record: pd.Series) -> str:
    """
    Extract sentiment classification from a feedback record.
    
    For MVP implementation, uses pre-enriched 'sentiment' column from CSV data.
    Future enhancement will integrate with actual NLP sentiment analysis models.
    
    Args:
        record (pd.Series): A single row from the feedback DataFrame
        
    Returns:
        str: Sentiment classification ('positive', 'negative', 'neutral')
        
    Requirements: 2.1, 2.4
    """
    try:
        sentiment = record.get('sentiment')
        
        if pd.isna(sentiment) or sentiment is None:
            return 'neutral'
            
        # Normalize sentiment value to lowercase and validate
        sentiment_str = str(sentiment).lower().strip()
        
        # Validate against expected sentiment values
        valid_sentiments = {'positive', 'negative', 'neutral'}
        if sentiment_str in valid_sentiments:
            return sentiment_str
        else:
            # Handle unexpected sentiment values
            return 'neutral'
            
    except (KeyError, AttributeError, TypeError):
        # Return default value if any error occurs
        return 'neutral'


def get_theme(record: pd.Series) -> str:
    """
    Extract theme categorization from a feedback record.
    
    For MVP implementation, uses pre-enriched 'theme' column from CSV data.
    Future enhancement will integrate with actual NLP theme classification models.
    
    Args:
        record (pd.Series): A single row from the feedback DataFrame
        
    Returns:
        str: Theme category (e.g., 'Trading/Execution & Fees', 'Performance/Outages')
        
    Requirements: 2.2, 2.4
    """
    try:
        theme = record.get('theme')
        
        if pd.isna(theme) or theme is None:
            return 'General Feedback'
            
        # Return theme as string, handling any data type conversion
        theme_str = str(theme).strip()
        
        # Return empty themes as default
        if not theme_str:
            return 'General Feedback'
            
        return theme_str
        
    except (KeyError, AttributeError, TypeError):
        # Return default value if any error occurs
        return 'General Feedback'


def get_strategic_goal(record: pd.Series) -> str:
    """
    Extract strategic goal alignment from a feedback record.
    
    For MVP implementation, uses pre-enriched 'strategic_goal' column from CSV data.
    Future enhancement will integrate with actual NLP strategic alignment models.
    
    Args:
        record (pd.Series): A single row from the feedback DataFrame
        
    Returns:
        str: Strategic goal alignment ('Growth', 'Trust&Safety', 'Onchain Adoption', 
             'CX Efficiency', 'Compliance')
             
    Requirements: 2.3, 2.4
    """
    try:
        strategic_goal = record.get('strategic_goal')
        
        if pd.isna(strategic_goal) or strategic_goal is None:
            return 'General'
            
        # Normalize strategic goal value and validate
        goal_str = str(strategic_goal).strip()
        
        # Validate against expected strategic goals
        valid_goals = {
            'Growth', 'Trust&Safety', 'Onchain Adoption', 
            'CX Efficiency', 'Compliance'
        }
        
        if goal_str in valid_goals:
            return goal_str
        else:
            # Handle unexpected strategic goal values
            return 'General'
            
    except (KeyError, AttributeError, TypeError):
        # Return default value if any error occurs
        return 'General'


def enrich_dataframe_with_nlp(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply NLP analysis to all records in a DataFrame.
    
    This function applies sentiment, theme, and strategic goal extraction
    to each row in the DataFrame, adding or updating the respective columns.
    
    Args:
        df (pd.DataFrame): DataFrame containing feedback records
        
    Returns:
        pd.DataFrame: DataFrame with NLP analysis columns added/updated
        
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """
    if df.empty:
        return df
        
    # Create a copy to avoid modifying the original DataFrame
    enriched_df = df.copy()
    
    # Apply NLP functions to each row
    enriched_df['sentiment'] = enriched_df.apply(get_sentiment, axis=1)
    enriched_df['theme'] = enriched_df.apply(get_theme, axis=1)
    enriched_df['strategic_goal'] = enriched_df.apply(get_strategic_goal, axis=1)
    
    return enriched_df