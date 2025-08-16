"""
Dashboard Components Module for Advanced Trade Insight Engine

This module provides reusable UI components for the Streamlit dashboard:
- KPI header component with key metrics
- Filterable data table component with sorting capabilities  
- Filter controls for source channel, theme, and sentiment

Requirements: 6.1, 6.3, 6.5
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_kpi_header(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Display KPI header component with total items, average sentiment, and top theme.
    
    Args:
        df (pd.DataFrame): Processed feedback DataFrame with impact scores
        
    Returns:
        Dict[str, Any]: Dictionary containing calculated KPI values
        
    Requirements: 6.1
    """
    try:
        if df.empty:
            st.warning("No data available for KPI display")
            return {
                'total_items': 0,
                'avg_sentiment': 'N/A',
                'top_theme': 'N/A'
            }
        
        # Calculate KPIs
        total_items = len(df)
        
        # Calculate average sentiment (weighted by impact score)
        sentiment_mapping = {'positive': 1, 'neutral': 0, 'negative': -1}
        df_with_sentiment_values = df.copy()
        df_with_sentiment_values['sentiment_numeric'] = df_with_sentiment_values['sentiment'].map(
            lambda x: sentiment_mapping.get(str(x).lower(), 0)
        )
        
        if 'impact_score' in df.columns:
            weighted_sentiment = (df_with_sentiment_values['sentiment_numeric'] * 
                                df_with_sentiment_values['impact_score']).sum()
            total_weight = df_with_sentiment_values['impact_score'].sum()
            avg_sentiment_score = weighted_sentiment / total_weight if total_weight > 0 else 0
        else:
            avg_sentiment_score = df_with_sentiment_values['sentiment_numeric'].mean()
        
        # Convert to readable format
        if avg_sentiment_score > 0.3:
            avg_sentiment = "Positive"
        elif avg_sentiment_score < -0.3:
            avg_sentiment = "Negative"
        else:
            avg_sentiment = "Neutral"
        
        # Find top theme by impact score
        if 'theme' in df.columns and 'impact_score' in df.columns:
            theme_impact = df.groupby('theme')['impact_score'].sum().sort_values(ascending=False)
            top_theme = theme_impact.index[0] if len(theme_impact) > 0 else 'N/A'
        else:
            top_theme = 'N/A'
        
        # Display KPIs in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Feedback Items",
                value=f"{total_items:,}",
                help="Total number of feedback records processed"
            )
        
        with col2:
            st.metric(
                label="Average Sentiment",
                value=avg_sentiment,
                help="Overall sentiment weighted by impact score"
            )
        
        with col3:
            st.metric(
                label="Top Theme by Impact",
                value=top_theme,
                help="Theme with highest total impact score"
            )
        
        kpi_values = {
            'total_items': total_items,
            'avg_sentiment': avg_sentiment,
            'top_theme': top_theme,
            'avg_sentiment_score': avg_sentiment_score
        }
        
        logger.info(f"KPI header displayed: {kpi_values}")
        return kpi_values
        
    except Exception as e:
        logger.error(f"Error displaying KPI header: {e}")
        st.error(f"Error calculating KPIs: {str(e)}")
        return {
            'total_items': 0,
            'avg_sentiment': 'Error',
            'top_theme': 'Error'
        }


def create_filter_controls(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create filter controls for source channel, theme, and sentiment.
    
    Args:
        df (pd.DataFrame): DataFrame to extract filter options from
        
    Returns:
        Dict[str, Any]: Dictionary containing selected filter values
        
    Requirements: 6.3, 6.5
    """
    try:
        if df.empty:
            st.warning("No data available for filters")
            return {}
        
        st.subheader("🔍 Filters")
        
        # Create filter columns
        col1, col2, col3 = st.columns(3)
        
        filters = {}
        
        with col1:
            # Source channel filter
            if 'source_channel' in df.columns:
                source_options = ['All'] + sorted(df['source_channel'].dropna().unique().tolist())
                filters['source_channel'] = st.selectbox(
                    "Source Channel",
                    options=source_options,
                    index=0,
                    key="filter_source_channel",
                    help="Filter by feedback source channel"
                )
            elif 'source' in df.columns:
                source_options = ['All'] + sorted(df['source'].dropna().unique().tolist())
                filters['source'] = st.selectbox(
                    "Source",
                    options=source_options,
                    index=0,
                    key="filter_source",
                    help="Filter by feedback source"
                )
        
        with col2:
            # Theme filter
            if 'theme' in df.columns:
                theme_options = ['All'] + sorted(df['theme'].dropna().unique().tolist())
                filters['theme'] = st.selectbox(
                    "Theme",
                    options=theme_options,
                    index=0,
                    key="filter_theme",
                    help="Filter by feedback theme"
                )
        
        with col3:
            # Sentiment filter
            if 'sentiment' in df.columns:
                sentiment_options = ['All'] + sorted(df['sentiment'].dropna().unique().tolist())
                filters['sentiment'] = st.selectbox(
                    "Sentiment",
                    options=sentiment_options,
                    index=0,
                    key="filter_sentiment",
                    help="Filter by sentiment classification"
                )
        
        logger.info(f"Filter controls created with options: {filters}")
        return filters
        
    except Exception as e:
        logger.error(f"Error creating filter controls: {e}")
        st.error(f"Error creating filters: {str(e)}")
        return {}


def apply_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply selected filters to the DataFrame.
    
    Args:
        df (pd.DataFrame): Original DataFrame
        filters (Dict[str, Any]): Dictionary of filter selections
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    try:
        filtered_df = df.copy()
        
        for filter_name, filter_value in filters.items():
            if filter_value and filter_value != 'All':
                if filter_name in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[filter_name] == filter_value]
        
        logger.info(f"Applied filters: {filters}, resulting in {len(filtered_df)} records")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error applying filters: {e}")
        return df


def display_filterable_data_table(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Display filterable data table component with sorting capabilities.
    
    Args:
        df (pd.DataFrame): DataFrame to display
        filters (Dict[str, Any]): Applied filters
        
    Returns:
        pd.DataFrame: Filtered DataFrame that was displayed
        
    Requirements: 6.3, 6.5
    """
    try:
        # Apply filters
        filtered_df = apply_filters(df, filters)
        
        if filtered_df.empty:
            st.warning("No data matches the selected filters")
            return filtered_df
        
        st.subheader(f"📊 Feedback Data ({len(filtered_df):,} records)")
        
        # Column selection for display
        display_columns = []
        if 'customer_id' in filtered_df.columns:
            display_columns.append('customer_id')
        if 'source_channel' in filtered_df.columns:
            display_columns.append('source_channel')
        elif 'source' in filtered_df.columns:
            display_columns.append('source')
        if 'feedback_text' in filtered_df.columns:
            display_columns.append('feedback_text')
        elif 'review_text' in filtered_df.columns:
            display_columns.append('review_text')
        elif 'tweet_text' in filtered_df.columns:
            display_columns.append('tweet_text')
        elif 'note_text' in filtered_df.columns:
            display_columns.append('note_text')
        if 'sentiment' in filtered_df.columns:
            display_columns.append('sentiment')
        if 'theme' in filtered_df.columns:
            display_columns.append('theme')
        if 'impact_score' in filtered_df.columns:
            display_columns.append('impact_score')
        if 'timestamp' in filtered_df.columns:
            display_columns.append('timestamp')
        
        # Ensure we have columns to display
        if not display_columns:
            display_columns = filtered_df.columns.tolist()[:10]  # Show first 10 columns
        
        # Prepare display DataFrame
        display_df = filtered_df[display_columns].copy()
        
        # Sort by impact score if available
        if 'impact_score' in display_df.columns:
            display_df = display_df.sort_values('impact_score', ascending=False)
        
        # Truncate long text fields for better display
        text_columns = ['feedback_text', 'review_text', 'tweet_text', 'note_text']
        for col in text_columns:
            if col in display_df.columns:
                display_df[col] = display_df[col].astype(str).str[:100] + '...'
        
        # Display the table with sorting enabled
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                'impact_score': st.column_config.NumberColumn(
                    'Impact Score',
                    help='Business impact priority score',
                    format='%.4f'
                ),
                'timestamp': st.column_config.DatetimeColumn(
                    'Timestamp',
                    help='When the feedback was created'
                )
            }
        )
        
        # Display summary statistics
        if len(filtered_df) > 0:
            st.caption(f"Showing {len(display_df)} records. "
                      f"Use column headers to sort data.")
        
        logger.info(f"Data table displayed with {len(display_df)} records")
        return filtered_df
        
    except Exception as e:
        logger.error(f"Error displaying data table: {e}")
        st.error(f"Error displaying data table: {str(e)}")
        return pd.DataFrame()


def display_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Display summary statistics for the current filtered dataset.
    
    Args:
        df (pd.DataFrame): Filtered DataFrame
        
    Returns:
        Dict[str, Any]: Summary statistics
    """
    try:
        if df.empty:
            return {}
        
        stats = {}
        
        # Sentiment distribution
        if 'sentiment' in df.columns:
            sentiment_counts = df['sentiment'].value_counts()
            stats['sentiment_distribution'] = sentiment_counts.to_dict()
        
        # Theme distribution
        if 'theme' in df.columns:
            theme_counts = df['theme'].value_counts()
            stats['theme_distribution'] = theme_counts.to_dict()
        
        # Source distribution
        source_col = 'source_channel' if 'source_channel' in df.columns else 'source'
        if source_col in df.columns:
            source_counts = df[source_col].value_counts()
            stats['source_distribution'] = source_counts.to_dict()
        
        # Impact score statistics
        if 'impact_score' in df.columns:
            stats['impact_stats'] = {
                'mean': df['impact_score'].mean(),
                'median': df['impact_score'].median(),
                'max': df['impact_score'].max(),
                'min': df['impact_score'].min()
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating summary stats: {e}")
        return {}