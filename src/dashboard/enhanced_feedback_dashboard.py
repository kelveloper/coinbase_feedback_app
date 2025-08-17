#!/usr/bin/env python3
"""
Enhanced Feedback Dashboard for Unified Feedback Data

This dashboard specifically showcases the enhanced feedback data from the 
feedback enhancement system with unified schema, sentiment scoring, and strategic alignment.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Page configuration
st.set_page_config(
    page_title="Enhanced Feedback Analytics",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_enhanced_feedback_data(file_path: str = "output/enriched_feedback_master.csv") -> pd.DataFrame:
    """Load the enhanced feedback data from CSV."""
    try:
        if not Path(file_path).exists():
            st.error(f"Enhanced feedback data not found at: {file_path}")
            st.info("Please run the feedback enhancement system first to generate the data.")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading enhanced feedback data: {e}")
        return pd.DataFrame()


def display_enhanced_kpis(df: pd.DataFrame):
    """Display enhanced KPIs specific to the unified feedback data."""
    if df.empty:
        return
    
    st.subheader("🎯 Enhanced Feedback Analytics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_feedback = len(df)
        st.metric("Total Feedback", f"{total_feedback:,}")
    
    with col2:
        avg_sentiment = df['sentiment_score'].mean()
        sentiment_label = "Positive" if avg_sentiment > 0.2 else "Negative" if avg_sentiment < -0.2 else "Neutral"
        st.metric("Avg Sentiment", f"{avg_sentiment:.2f}", sentiment_label)
    
    with col3:
        relevant_count = df['is_relevant'].sum()
        relevance_rate = (relevant_count / len(df)) * 100
        st.metric("Relevance Rate", f"{relevance_rate:.1f}%")
    
    with col4:
        unique_themes = df['theme'].nunique()
        st.metric("Unique Themes", unique_themes)
    
    with col5:
        data_sources = df['source_channel'].nunique()
        st.metric("Data Sources", data_sources)


def create_sentiment_heatmap(df: pd.DataFrame):
    """Create a heatmap showing sentiment scores across themes and sources."""
    if df.empty:
        return None
    
    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(
        values='sentiment_score',
        index='theme',
        columns='source_channel',
        aggfunc='mean'
    )
    
    fig = px.imshow(
        heatmap_data,
        title="Sentiment Score Heatmap: Themes vs Sources",
        labels=dict(x="Source Channel", y="Theme", color="Avg Sentiment Score"),
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    
    fig.update_layout(height=600)
    return fig


def create_strategic_goal_analysis(df: pd.DataFrame):
    """Create strategic goal impact analysis."""
    if df.empty or 'strategic_goal' not in df.columns:
        return None
    
    # Calculate metrics by strategic goal
    goal_metrics = df.groupby('strategic_goal').agg({
        'sentiment_score': ['mean', 'count'],
        'source_metric': 'mean',
        'feedback_id': 'count'
    }).round(3)
    
    goal_metrics.columns = ['avg_sentiment', 'sentiment_count', 'avg_source_metric', 'feedback_count']
    goal_metrics = goal_metrics.reset_index()
    
    # Create subplot with multiple metrics
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Feedback Count by Strategic Goal',
            'Average Sentiment by Strategic Goal', 
            'Average Source Metric by Strategic Goal',
            'Strategic Goal Distribution'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )
    
    # Feedback count
    fig.add_trace(
        go.Bar(x=goal_metrics['strategic_goal'], y=goal_metrics['feedback_count'],
               name='Feedback Count', marker_color='lightblue'),
        row=1, col=1
    )
    
    # Average sentiment
    fig.add_trace(
        go.Bar(x=goal_metrics['strategic_goal'], y=goal_metrics['avg_sentiment'],
               name='Avg Sentiment', marker_color='lightgreen'),
        row=1, col=2
    )
    
    # Average source metric
    fig.add_trace(
        go.Bar(x=goal_metrics['strategic_goal'], y=goal_metrics['avg_source_metric'],
               name='Avg Source Metric', marker_color='lightcoral'),
        row=2, col=1
    )
    
    # Distribution pie chart
    fig.add_trace(
        go.Pie(labels=goal_metrics['strategic_goal'], values=goal_metrics['feedback_count'],
               name='Distribution'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, title_text="Strategic Goal Analysis Dashboard")
    return fig


def create_enhanced_time_series(df: pd.DataFrame):
    """Create enhanced time series with sentiment overlay."""
    if df.empty:
        return None
    
    # Prepare daily data
    df['date'] = df['timestamp'].dt.date
    daily_data = df.groupby('date').agg({
        'feedback_id': 'count',
        'sentiment_score': 'mean',
        'source_metric': 'mean'
    }).reset_index()
    
    daily_data['date'] = pd.to_datetime(daily_data['date'])
    
    # Create subplot
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Daily Feedback Volume', 'Average Daily Sentiment', 'Average Source Metric'),
        vertical_spacing=0.08
    )
    
    # Volume
    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['feedback_id'],
                  mode='lines+markers', name='Feedback Count',
                  line=dict(color='blue')),
        row=1, col=1
    )
    
    # Sentiment
    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['sentiment_score'],
                  mode='lines+markers', name='Avg Sentiment',
                  line=dict(color='green')),
        row=2, col=1
    )
    
    # Source metric
    fig.add_trace(
        go.Scatter(x=daily_data['date'], y=daily_data['source_metric'],
                  mode='lines+markers', name='Avg Source Metric',
                  line=dict(color='red')),
        row=3, col=1
    )
    
    fig.update_layout(height=800, title_text="Enhanced Time Series Analysis")
    return fig


def create_source_channel_comparison(df: pd.DataFrame):
    """Create detailed source channel comparison."""
    if df.empty:
        return None
    
    source_analysis = df.groupby('source_channel').agg({
        'sentiment_score': ['mean', 'std', 'count'],
        'source_metric': ['mean', 'std'],
        'feedback_id': 'count'
    }).round(3)
    
    source_analysis.columns = [
        'avg_sentiment', 'sentiment_std', 'sentiment_count',
        'avg_source_metric', 'source_metric_std', 'feedback_count'
    ]
    source_analysis = source_analysis.reset_index()
    
    # Create radar chart for multi-dimensional comparison
    categories = ['Avg Sentiment', 'Feedback Volume', 'Avg Source Metric', 'Sentiment Consistency']
    
    fig = go.Figure()
    
    for _, row in source_analysis.iterrows():
        # Normalize values for radar chart (0-1 scale)
        sentiment_norm = (row['avg_sentiment'] + 1) / 2  # Convert from [-1,1] to [0,1]
        volume_norm = row['feedback_count'] / source_analysis['feedback_count'].max()
        metric_norm = row['avg_source_metric'] / source_analysis['avg_source_metric'].max()
        consistency_norm = 1 - (row['sentiment_std'] / source_analysis['sentiment_std'].max())
        
        values = [sentiment_norm, volume_norm, metric_norm, consistency_norm]
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=categories + [categories[0]],
            fill='toself',
            name=row['source_channel']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Source Channel Multi-Dimensional Comparison"
    )
    
    return fig


def create_theme_sentiment_bubble_chart(df: pd.DataFrame):
    """Create bubble chart showing themes by sentiment and volume."""
    if df.empty:
        return None
    
    theme_data = df.groupby('theme').agg({
        'sentiment_score': 'mean',
        'feedback_id': 'count',
        'source_metric': 'mean'
    }).reset_index()
    
    fig = px.scatter(
        theme_data,
        x='sentiment_score',
        y='source_metric',
        size='feedback_id',
        hover_name='theme',
        title="Theme Analysis: Sentiment vs Source Metric (Bubble Size = Feedback Count)",
        labels={
            'sentiment_score': 'Average Sentiment Score',
            'source_metric': 'Average Source Metric',
            'feedback_id': 'Feedback Count'
        }
    )
    
    # Add quadrant lines
    fig.add_hline(y=theme_data['source_metric'].median(), line_dash="dash", line_color="gray")
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    # Add quadrant labels
    fig.add_annotation(x=0.5, y=theme_data['source_metric'].max() * 0.9,
                      text="High Impact<br>Positive Sentiment", showarrow=False)
    fig.add_annotation(x=-0.5, y=theme_data['source_metric'].max() * 0.9,
                      text="High Impact<br>Negative Sentiment", showarrow=False)
    
    return fig


def display_enhanced_filters(df: pd.DataFrame):
    """Display enhanced filtering options."""
    st.sidebar.header("🔍 Enhanced Filters")
    
    filters = {}
    
    # Date range filter
    if not df.empty:
        min_date = df['timestamp'].min().date()
        max_date = df['timestamp'].max().date()
        
        date_range = st.sidebar.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        filters['date_range'] = date_range
    
    # Source channel filter
    source_options = ['All'] + sorted(df['source_channel'].unique().tolist())
    filters['source_channel'] = st.sidebar.selectbox("Source Channel", source_options)
    
    # Theme filter
    theme_options = ['All'] + sorted(df['theme'].unique().tolist())
    filters['theme'] = st.sidebar.selectbox("Theme", theme_options)
    
    # Strategic goal filter
    goal_options = ['All'] + sorted(df['strategic_goal'].unique().tolist())
    filters['strategic_goal'] = st.sidebar.selectbox("Strategic Goal", goal_options)
    
    # Sentiment score range
    sentiment_range = st.sidebar.slider(
        "Sentiment Score Range",
        min_value=float(df['sentiment_score'].min()),
        max_value=float(df['sentiment_score'].max()),
        value=(float(df['sentiment_score'].min()), float(df['sentiment_score'].max())),
        step=0.1
    )
    filters['sentiment_range'] = sentiment_range
    
    # Relevance filter
    filters['relevance'] = st.sidebar.checkbox("Show Only Relevant Feedback", value=True)
    
    return filters


def apply_enhanced_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply the enhanced filters to the dataframe."""
    filtered_df = df.copy()
    
    # Date range filter
    if 'date_range' in filters and len(filters['date_range']) == 2:
        start_date, end_date = filters['date_range']
        filtered_df = filtered_df[
            (filtered_df['timestamp'].dt.date >= start_date) &
            (filtered_df['timestamp'].dt.date <= end_date)
        ]
    
    # Source channel filter
    if filters.get('source_channel') and filters['source_channel'] != 'All':
        filtered_df = filtered_df[filtered_df['source_channel'] == filters['source_channel']]
    
    # Theme filter
    if filters.get('theme') and filters['theme'] != 'All':
        filtered_df = filtered_df[filtered_df['theme'] == filters['theme']]
    
    # Strategic goal filter
    if filters.get('strategic_goal') and filters['strategic_goal'] != 'All':
        filtered_df = filtered_df[filtered_df['strategic_goal'] == filters['strategic_goal']]
    
    # Sentiment range filter
    if 'sentiment_range' in filters:
        min_sentiment, max_sentiment = filters['sentiment_range']
        filtered_df = filtered_df[
            (filtered_df['sentiment_score'] >= min_sentiment) &
            (filtered_df['sentiment_score'] <= max_sentiment)
        ]
    
    # Relevance filter
    if filters.get('relevance'):
        filtered_df = filtered_df[filtered_df['is_relevant'] == True]
    
    return filtered_df


def display_enhanced_data_table(df: pd.DataFrame):
    """Display enhanced data table with all unified schema columns."""
    if df.empty:
        st.warning("No data to display")
        return
    
    st.subheader(f"📊 Enhanced Feedback Data ({len(df):,} records)")
    
    # Prepare display dataframe
    display_df = df.copy()
    
    # Truncate long feedback text for better display
    display_df['feedback_text'] = display_df['feedback_text'].str[:100] + '...'
    
    # Sort by sentiment score descending
    display_df = display_df.sort_values('sentiment_score', ascending=False)
    
    # Display with enhanced column configuration
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'feedback_id': st.column_config.TextColumn('Feedback ID', width='small'),
            'source_channel': st.column_config.TextColumn('Source', width='medium'),
            'timestamp': st.column_config.DatetimeColumn('Timestamp', width='medium'),
            'feedback_text': st.column_config.TextColumn('Feedback Text', width='large'),
            'source_metric': st.column_config.NumberColumn('Source Metric', format='%.2f'),
            'is_relevant': st.column_config.CheckboxColumn('Relevant'),
            'sentiment_score': st.column_config.NumberColumn(
                'Sentiment Score',
                help='AI-generated sentiment score (-1 to 1)',
                format='%.3f',
                width='small'
            ),
            'theme': st.column_config.TextColumn('Theme', width='medium'),
            'strategic_goal': st.column_config.TextColumn('Strategic Goal', width='medium')
        }
    )


def main():
    """Main enhanced dashboard application."""
    st.title("🚀 Enhanced Feedback Analytics Dashboard")
    st.markdown("### Unified Multi-Channel Feedback Intelligence")
    
    # Load enhanced data
    df = load_enhanced_feedback_data()
    
    if df.empty:
        st.stop()
    
    # Display filters in sidebar
    filters = display_enhanced_filters(df)
    
    # Apply filters
    filtered_df = apply_enhanced_filters(df, filters)
    
    # Display filter results
    if len(filtered_df) != len(df):
        st.info(f"Showing {len(filtered_df):,} of {len(df):,} records after filtering")
    
    # Enhanced KPIs
    display_enhanced_kpis(filtered_df)
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Strategic Analysis", 
        "🎯 Sentiment Intelligence", 
        "📊 Source Comparison",
        "🕒 Time Trends",
        "📋 Data Explorer"
    ])
    
    with tab1:
        st.subheader("Strategic Goal Analysis")
        fig = create_strategic_goal_analysis(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Theme vs Sentiment Bubble Analysis")
        fig = create_theme_sentiment_bubble_chart(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Sentiment Score Heatmap")
        fig = create_sentiment_heatmap(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment distribution
        col1, col2 = st.columns(2)
        with col1:
            sentiment_dist = filtered_df['sentiment_score'].value_counts().sort_index()
            fig = px.bar(x=sentiment_dist.index, y=sentiment_dist.values,
                        title="Sentiment Score Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Theme sentiment analysis
            theme_sentiment = filtered_df.groupby('theme')['sentiment_score'].mean().sort_values(ascending=True)
            fig = px.bar(x=theme_sentiment.values, y=theme_sentiment.index, orientation='h',
                        title="Average Sentiment by Theme")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Multi-Dimensional Source Comparison")
        fig = create_source_channel_comparison(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Source metrics table
        source_metrics = filtered_df.groupby('source_channel').agg({
            'feedback_id': 'count',
            'sentiment_score': ['mean', 'std'],
            'source_metric': ['mean', 'std'],
            'is_relevant': 'sum'
        }).round(3)
        
        st.subheader("Source Channel Metrics")
        st.dataframe(source_metrics, use_container_width=True)
    
    with tab4:
        st.subheader("Enhanced Time Series Analysis")
        fig = create_enhanced_time_series(filtered_df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        display_enhanced_data_table(filtered_df)
        
        # Export functionality
        if st.button("📥 Export Filtered Data"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"filtered_feedback_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


if __name__ == "__main__":
    main()