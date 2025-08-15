"""
Chart Visualization Module for Advanced Trade Insight Engine

This module provides interactive chart components for the Streamlit dashboard:
- Theme impact ranking bar charts
- Sentiment distribution visualizations  
- Time-based trend analysis charts
- Interactive chart features and hover details

Requirements: 6.2
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_theme_impact_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create theme impact ranking bar chart showing themes ranked by total impact score.
    
    Args:
        df (pd.DataFrame): DataFrame with theme and impact_score columns
        
    Returns:
        Optional[go.Figure]: Plotly figure object or None if error
        
    Requirements: 6.2
    """
    try:
        if df.empty or 'theme' not in df.columns or 'impact_score' not in df.columns:
            logger.warning("Missing required columns for theme impact chart")
            return None
        
        # Group by theme and sum impact scores
        theme_impact = df.groupby('theme')['impact_score'].agg(['sum', 'count']).reset_index()
        theme_impact.columns = ['theme', 'total_impact', 'feedback_count']
        theme_impact = theme_impact.sort_values('total_impact', ascending=True)
        
        # Create horizontal bar chart
        fig = px.bar(
            theme_impact,
            x='total_impact',
            y='theme',
            orientation='h',
            title='Theme Impact Rankings',
            labels={
                'total_impact': 'Total Impact Score',
                'theme': 'Theme',
                'feedback_count': 'Feedback Count'
            },
            hover_data=['feedback_count'],
            color='total_impact',
            color_continuous_scale='Reds'
        )
        
        # Update layout for better appearance
        fig.update_layout(
            height=max(400, len(theme_impact) * 40),
            showlegend=False,
            xaxis_title="Total Impact Score",
            yaxis_title="Theme",
            title_x=0.5,
            hovermode='y unified'
        )
        
        # Update hover template
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                         "Total Impact: %{x:.2f}<br>" +
                         "Feedback Count: %{customdata[0]}<br>" +
                         "<extra></extra>"
        )
        
        logger.info(f"Created theme impact chart with {len(theme_impact)} themes")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating theme impact chart: {e}")
        return None


def create_sentiment_distribution_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create sentiment distribution visualization showing sentiment breakdown.
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment column
        
    Returns:
        Optional[go.Figure]: Plotly figure object or None if error
        
    Requirements: 6.2
    """
    try:
        if df.empty or 'sentiment' not in df.columns:
            logger.warning("Missing sentiment column for distribution chart")
            return None
        
        # Calculate sentiment distribution
        sentiment_counts = df['sentiment'].value_counts()
        sentiment_percentages = (sentiment_counts / len(df) * 100).round(1)
        
        # Define colors for sentiments
        color_map = {
            'positive': '#2E8B57',  # Sea Green
            'neutral': '#FFD700',   # Gold
            'negative': '#DC143C'   # Crimson
        }
        
        colors = [color_map.get(sentiment.lower(), '#808080') for sentiment in sentiment_counts.index]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=sentiment_counts.index,
            values=sentiment_counts.values,
            hole=0.4,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate="<b>%{label}</b><br>" +
                         "Count: %{value}<br>" +
                         "Percentage: %{percent}<br>" +
                         "<extra></extra>"
        )])
        
        # Update layout
        fig.update_layout(
            title='Sentiment Distribution',
            title_x=0.5,
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        logger.info(f"Created sentiment distribution chart with {len(sentiment_counts)} categories")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating sentiment distribution chart: {e}")
        return None


def create_time_trend_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create time-based trend analysis chart showing feedback volume and sentiment over time.
    
    Args:
        df (pd.DataFrame): DataFrame with timestamp and sentiment columns
        
    Returns:
        Optional[go.Figure]: Plotly figure object or None if error
        
    Requirements: 6.2
    """
    try:
        if df.empty or 'timestamp' not in df.columns:
            logger.warning("Missing timestamp column for time trend chart")
            return None
        
        # Ensure timestamp is datetime
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'], errors='coerce')
        df_copy = df_copy.dropna(subset=['timestamp'])
        
        if df_copy.empty:
            logger.warning("No valid timestamps for time trend chart")
            return None
        
        # Group by date and sentiment
        df_copy['date'] = df_copy['timestamp'].dt.date
        
        if 'sentiment' in df_copy.columns:
            # Create daily sentiment counts
            daily_sentiment = df_copy.groupby(['date', 'sentiment']).size().reset_index(name='count')
            daily_sentiment['date'] = pd.to_datetime(daily_sentiment['date'])
            
            # Create subplot with secondary y-axis
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Daily Feedback Volume by Sentiment', 'Total Daily Feedback'),
                vertical_spacing=0.15,
                row_heights=[0.7, 0.3]
            )
            
            # Add sentiment trend lines
            sentiments = daily_sentiment['sentiment'].unique()
            color_map = {
                'positive': '#2E8B57',
                'neutral': '#FFD700', 
                'negative': '#DC143C'
            }
            
            for sentiment in sentiments:
                sentiment_data = daily_sentiment[daily_sentiment['sentiment'] == sentiment]
                fig.add_trace(
                    go.Scatter(
                        x=sentiment_data['date'],
                        y=sentiment_data['count'],
                        mode='lines+markers',
                        name=sentiment.title(),
                        line=dict(color=color_map.get(sentiment.lower(), '#808080')),
                        hovertemplate=f"<b>{sentiment.title()}</b><br>" +
                                     "Date: %{x}<br>" +
                                     "Count: %{y}<br>" +
                                     "<extra></extra>"
                    ),
                    row=1, col=1
                )
            
            # Add total daily volume
            daily_total = df_copy.groupby('date').size().reset_index(name='total_count')
            daily_total['date'] = pd.to_datetime(daily_total['date'])
            
            fig.add_trace(
                go.Bar(
                    x=daily_total['date'],
                    y=daily_total['total_count'],
                    name='Total Volume',
                    marker_color='lightblue',
                    hovertemplate="<b>Total Feedback</b><br>" +
                                 "Date: %{x}<br>" +
                                 "Count: %{y}<br>" +
                                 "<extra></extra>"
                ),
                row=2, col=1
            )
            
        else:
            # Simple volume chart if no sentiment data
            daily_total = df_copy.groupby('date').size().reset_index(name='count')
            daily_total['date'] = pd.to_datetime(daily_total['date'])
            
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=daily_total['date'],
                    y=daily_total['count'],
                    mode='lines+markers',
                    name='Daily Feedback',
                    line=dict(color='#1f77b4'),
                    hovertemplate="<b>Daily Feedback</b><br>" +
                                 "Date: %{x}<br>" +
                                 "Count: %{y}<br>" +
                                 "<extra></extra>"
                )
            )
        
        # Update layout
        fig.update_layout(
            title='Feedback Trends Over Time',
            title_x=0.5,
            height=600,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            )
        )
        
        # Update x-axis labels
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Feedback Count")
        
        logger.info(f"Created time trend chart with {len(df_copy)} records")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating time trend chart: {e}")
        return None


def create_source_impact_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Create source channel impact comparison chart.
    
    Args:
        df (pd.DataFrame): DataFrame with source and impact_score columns
        
    Returns:
        Optional[go.Figure]: Plotly figure object or None if error
        
    Requirements: 6.2
    """
    try:
        source_col = 'source_channel' if 'source_channel' in df.columns else 'source'
        
        if df.empty or source_col not in df.columns or 'impact_score' not in df.columns:
            logger.warning(f"Missing required columns for source impact chart")
            return None
        
        # Group by source and calculate metrics
        source_metrics = df.groupby(source_col).agg({
            'impact_score': ['sum', 'mean', 'count']
        }).round(2)
        
        source_metrics.columns = ['total_impact', 'avg_impact', 'feedback_count']
        source_metrics = source_metrics.reset_index()
        source_metrics = source_metrics.sort_values('total_impact', ascending=True)
        
        # Create horizontal bar chart
        fig = px.bar(
            source_metrics,
            x='total_impact',
            y=source_col,
            orientation='h',
            title='Source Channel Impact Comparison',
            labels={
                'total_impact': 'Total Impact Score',
                source_col: 'Source Channel'
            },
            hover_data=['avg_impact', 'feedback_count'],
            color='avg_impact',
            color_continuous_scale='Blues'
        )
        
        # Update layout
        fig.update_layout(
            height=max(300, len(source_metrics) * 60),
            showlegend=False,
            title_x=0.5,
            hovermode='y unified'
        )
        
        # Update hover template
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                         "Total Impact: %{x:.2f}<br>" +
                         "Avg Impact: %{customdata[0]:.2f}<br>" +
                         "Feedback Count: %{customdata[1]}<br>" +
                         "<extra></extra>"
        )
        
        logger.info(f"Created source impact chart with {len(source_metrics)} sources")
        return fig
        
    except Exception as e:
        logger.error(f"Error creating source impact chart: {e}")
        return None


def display_chart_with_error_handling(chart_func, df: pd.DataFrame, title: str, **kwargs) -> bool:
    """
    Display a chart with proper error handling and fallback messages.
    
    Args:
        chart_func: Function that creates the chart
        df (pd.DataFrame): Data for the chart
        title (str): Chart title for error messages
        **kwargs: Additional arguments for chart function
        
    Returns:
        bool: True if chart was displayed successfully, False otherwise
    """
    try:
        fig = chart_func(df, **kwargs)
        
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
            return True
        else:
            st.warning(f"Unable to create {title} - insufficient data or missing columns")
            return False
            
    except Exception as e:
        logger.error(f"Error displaying {title}: {e}")
        st.error(f"Error creating {title}: {str(e)}")
        return False


def create_comprehensive_dashboard_charts(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Create and display all dashboard charts with error handling.
    
    Args:
        df (pd.DataFrame): Complete feedback DataFrame
        
    Returns:
        Dict[str, bool]: Status of each chart creation
        
    Requirements: 6.2
    """
    chart_status = {}
    
    if df.empty:
        st.warning("No data available for chart visualization")
        return chart_status
    
    # Create charts in columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Theme Impact Rankings")
        chart_status['theme_impact'] = display_chart_with_error_handling(
            create_theme_impact_chart, df, "Theme Impact Chart"
        )
        
        st.subheader("📈 Feedback Trends")
        chart_status['time_trends'] = display_chart_with_error_handling(
            create_time_trend_chart, df, "Time Trend Chart"
        )
    
    with col2:
        st.subheader("🎯 Sentiment Distribution")
        chart_status['sentiment_distribution'] = display_chart_with_error_handling(
            create_sentiment_distribution_chart, df, "Sentiment Distribution Chart"
        )
        
        st.subheader("🔗 Source Impact Comparison")
        chart_status['source_impact'] = display_chart_with_error_handling(
            create_source_impact_chart, df, "Source Impact Chart"
        )
    
    logger.info(f"Dashboard charts created with status: {chart_status}")
    return chart_status