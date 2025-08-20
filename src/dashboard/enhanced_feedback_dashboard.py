#!/usr/bin/env python3
"""
Secure Enhanced Feedback Dashboard for Unified Feedback Data

This dashboard combines secure authentication with enhanced feedback analytics,
showcasing unified feedback data with sentiment scoring and strategic alignment.

Features:
- Secure login with role-based access control
- Enhanced feedback analytics and visualizations
- Multi-dimensional data analysis
- Export capabilities (role-dependent)

Run with: streamlit run src/dashboard/enhanced_feedback_dashboard.py
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
from typing import Optional, Dict, Any

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import authentication modules with multiple fallbacks
try:
    from auth.auth_config import get_authenticator, get_user_role, has_permission, get_user_info
    AUTH_AVAILABLE = True
    AUTH_TYPE = 'full'
except ImportError:
    try:
        # First fallback - simple auth with bcrypt
        from auth.simple_auth import check_authentication, show_logout_button
        AUTH_AVAILABLE = True
        AUTH_TYPE = 'simple'
    except ImportError:
        # Final fallback - no dependencies
        from auth.simple_fallback_auth import (
            check_simple_authentication as check_authentication,
            show_simple_logout_button as show_logout_button,
            get_simple_user_role
        )
        AUTH_AVAILABLE = True
        AUTH_TYPE = 'fallback'

# Page configuration
st.set_page_config(
    page_title="🔐 Secure Enhanced Feedback Analytics",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme
def load_custom_css():
    """Load custom CSS theme for the dashboard."""
    css = """
    <style>
    :root {
      --background-color: #0d0e12;
      --card-background: #1c1e21;
      --text-primary: #f8f8f8;
      --text-secondary: #9aa0a6;
      --positive-color: #28a745;
      --negative-color: #dc3545;
      --border-color: #2d3036;
    }

    /* Streamlit Global Styles */
    .stApp {
      background-color: var(--background-color) !important;
      color: var(--text-primary) !important;
      font-weight: 200 !important;
    }

    /* Main Container */
    .main .block-container {
      background-color: var(--background-color) !important;
      padding: 20px !important;
    }

    /* Streamlit Elements */
    .stMarkdown, .stText, .stMetric, .stDataFrame {
      color: var(--text-primary) !important;
      font-weight: 200 !important;
    }

    /* Global Font Weight Override */
    * {
      font-weight: 200 !important;
    }

    /* Specific Element Font Weights */
    h1, h2, h3, h4, h5, h6 {
      font-weight: 200 !important;
    }

    p, span, div, label, input, button, select, textarea {
      font-weight: 200 !important;
    }

    /* Animated Cards - New Theme */
    .container {
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      flex-wrap: wrap !important;
      padding: 20px 0 !important;
      gap: 0 !important;
    }

    .container .box {
      position: relative !important;
      width: 280px !important;
      height: 320px !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      margin: 20px 15px !important;
      transition: 0.5s !important;
    }

    .container .box::before {
      content: ' ' !important;
      position: absolute !important;
      top: 0 !important;
      left: 50px !important;
      width: 50% !important;
      height: 100% !important;
      text-decoration: none !important;
      background: #fff !important;
      border-radius: 8px !important;
      transform: skewX(15deg) !important;
      transition: 0.5s !important;
    }

    .container .box::after {
      content: '' !important;
      position: absolute !important;
      top: 0 !important;
      left: 50px !important;
      width: 50% !important;
      height: 100% !important;
      background: #fff !important;
      border-radius: 8px !important;
      transform: skewX(15deg) !important;
      transition: 0.5s !important;
      filter: blur(30px) !important;
    }

    .container .box:hover:before,
    .container .box:hover:after {
      transform: skewX(0deg) !important;
      left: 20px !important;
      width: calc(100% - 90px) !important;
    }

    .container .box:nth-child(1):before,
    .container .box:nth-child(1):after {
      background: linear-gradient(315deg, #ffbc00, #ff0058) !important;
    }

    .container .box:nth-child(2):before,
    .container .box:nth-child(2):after {
      background: linear-gradient(315deg, #03a9f4, #ff0058) !important;
    }

    .container .box:nth-child(3):before,
    .container .box:nth-child(3):after {
      background: linear-gradient(315deg, #4dff03, #00d0ff) !important;
    }

    .container .box span {
      display: block !important;
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      right: 0 !important;
      bottom: 0 !important;
      z-index: 5 !important;
      pointer-events: none !important;
    }

    .container .box span::before {
      content: '' !important;
      position: absolute !important;
      top: 0 !important;
      left: 0 !important;
      width: 0 !important;
      height: 0 !important;
      border-radius: 8px !important;
      background: rgba(255, 255, 255, 0.1) !important;
      backdrop-filter: blur(10px) !important;
      opacity: 0 !important;
      transition: 0.1s !important;
      animation: animate 2s ease-in-out infinite !important;
      box-shadow: 0 5px 15px rgba(0,0,0,0.08) !important;
    }

    .container .box:hover span::before {
      top: -50px !important;
      left: 50px !important;
      width: 100px !important;
      height: 100px !important;
      opacity: 1 !important;
    }

    .container .box span::after {
      content: '' !important;
      position: absolute !important;
      bottom: 0 !important;
      right: 0 !important;
      width: 100% !important;
      height: 100% !important;
      border-radius: 8px !important;
      background: rgba(255, 255, 255, 0.1) !important;
      backdrop-filter: blur(10px) !important;
      opacity: 0 !important;
      transition: 0.5s !important;
      animation: animate 2s ease-in-out infinite !important;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08) !important;
      animation-delay: -1s !important;
    }

    .container .box:hover span:after {
      bottom: -50px !important;
      right: 50px !important;
      width: 100px !important;
      height: 100px !important;
      opacity: 1 !important;
    }

    @keyframes animate {
      0%, 100% {
        transform: translateY(10px) !important;
      }
      50% {
        transform: translateY(-10px) !important;
      }
    }

    .container .box .content {
      position: relative !important;
      left: 0 !important;
      padding: 16px 24px !important;
      background: rgba(255, 255, 255, 0.05) !important;
      backdrop-filter: blur(10px) !important;
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1) !important;
      border-radius: 8px !important;
      z-index: 1 !important;
      transform: 0.5s !important;
      color: #fff !important;
    }

    .container .box:hover .content {
      left: -20px !important;
      padding: 40px 24px !important;
    }

    .container .box .content h2 {
      font-size: 1.5em !important;
      color: #fff !important;
      margin-bottom: 8px !important;
      font-weight: 200 !important;
    }

    .container .box .content p {
      font-size: 0.9em !important;
      margin-bottom: 8px !important;
      line-height: 1.3em !important;
      font-weight: 200 !important;
    }

    .container .box .content a {
      display: inline-block !important;
      font-size: 0.9em !important;
      color: #111 !important;
      background: #fff !important;
      padding: 8px 12px !important;
      border-radius: 4px !important;
      text-decoration: none !important;
      font-weight: 700 !important;
      margin-top: 5px !important;
    }

    .container .box .content a:hover {
      background: #ffcf4d !important;
      border: 1px solid rgba(255, 0, 88, 0.4) !important;
      box-shadow: 0 1px 15px rgba(1, 1, 1, 0.2) !important;
    }

    /* Dashboard Card Styling */
    .dashboard-card {
      background-color: var(--card-background) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 12px !important;
      padding: 24px !important;
      flex: 1 !important;
      min-width: 250px !important;
      max-width: calc(33.33% - 14px) !important;
      box-sizing: border-box !important;
      display: flex !important;
      flex-direction: column !important;
      margin-bottom: 20px !important;
    }

    .card-header {
      display: flex !important;
      justify-content: space-between !important;
      align-items: center !important;
      margin-bottom: 8px !important;
    }

    .card-title {
      font-size: 16px !important;
      font-weight: 500 !important;
      color: var(--text-secondary) !important;
    }

    .icon-placeholder {
      width: 24px !important;
      height: 24px !important;
    }

    .card-metric {
      font-size: 32px !important;
      font-weight: bold !important;
      margin-bottom: 8px !important;
      color: var(--text-primary) !important;
    }

    .card-footer {
      display: flex !important;
      align-items: center !important;
      font-size: 14px !important;
      font-weight: 600 !important;
      gap: 4px !important;
    }

    .card-footer.positive {
      color: var(--positive-color) !important;
    }

    .card-footer.negative {
      color: var(--negative-color) !important;
    }

    /* Card Container */
    .card-container {
      display: flex !important;
      flex-wrap: wrap !important;
      gap: 20px !important;
      justify-content: flex-start !important;
    }

    /* Streamlit Metric Overrides */
    .stMetric {
      background-color: var(--card-background) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 12px !important;
      padding: 24px !important;
      box-shadow: none !important;
    }

    .stMetric > div {
      background-color: transparent !important;
    }

    .stMetric [data-testid="metric-container"] {
      background-color: transparent !important;
    }

    .stMetric [data-testid="metric-container"] label {
      color: var(--text-secondary) !important;
      font-size: 16px !important;
      font-weight: 500 !important;
    }

    .stMetric [data-testid="metric-container"] div[data-testid="metric-container"] {
      color: var(--text-primary) !important;
      font-size: 32px !important;
      font-weight: bold !important;
    }

    /* Charts and DataFrames */
    .stPlotlyChart, .stDataFrame {
      background-color: var(--card-background) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 12px !important;
      padding: 24px !important;
      margin-bottom: 20px !important;
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
      background-color: var(--card-background) !important;
      color: var(--text-primary) !important;
      border-right: 1px solid var(--border-color) !important;
    }

    .sidebar .sidebar-content .stMarkdown {
      color: var(--text-primary) !important;
    }

    /* Button Styling */
    .stButton > button {
      background-color: var(--card-background) !important;
      color: var(--text-primary) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 8px !important;
      padding: 8px 16px !important;
    }

    .stButton > button:hover {
      background-color: rgba(248, 248, 248, 0.1) !important;
      border-color: var(--text-secondary) !important;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
      background-color: var(--card-background) !important;
      color: var(--text-primary) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 8px !important;
    }

    .stSelectbox > div > div > div {
      background-color: var(--card-background) !important;
      color: var(--text-primary) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 8px !important;
    }



    /* Tab Navigation Bar Styling with Hover Underline Effects */
    .tab-navbar {
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      padding: 15px 0 !important;
      margin-bottom: 20px !important;
      background-color: rgba(255, 255, 255, 0.02) !important;
      border-radius: 8px !important;
      border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    .tab-nav-list {
      display: flex !important;
      gap: 30px !important;
      list-style: none !important;
      margin: 0 !important;
      padding: 0 !important;
    }

    .tab-nav-item {
      font-size: 1rem !important;
      color: #cccccc !important;
      position: relative !important;
      display: inline-block !important;
      cursor: pointer !important;
      text-decoration: none !important;
      font-family: Arial, sans-serif !important;
      font-weight: 200 !important;
      text-transform: uppercase !important;
      letter-spacing: 0.05em !important;
      transition: color 0.3s ease !important;
    }

    .tab-nav-item:hover {
      color: #ffffff !important;
    }

    .tab-nav-item.active {
      color: #ffffff !important;
    }

    .tab-nav-item::after,
    .tab-nav-item::before {
      content: '' !important;
      position: absolute !important;
      width: 100% !important;
      height: 1px !important;
      background: linear-gradient(to right, #ff0000, #00ffff) !important;
      bottom: -3px !important;
      left: 0 !important;
      transform: scaleX(0) !important;
      transform-origin: right !important;
      transition: transform 0.3s ease-out !important;
    }

    .tab-nav-item::before {
      top: -3px !important;
      transform-origin: left !important;
    }

    .tab-nav-item:hover::after,
    .tab-nav-item:hover::before,
    .tab-nav-item.active::after,
    .tab-nav-item.active::before {
      transform: scaleX(1) !important;
    }

    /* Responsive Design */
    @media (max-width: 1024px) {
      .dashboard-card {
        max-width: calc(50% - 10px) !important;
      }
    }

    @media (max-width: 600px) {
      .main .block-container {
        padding: 20px !important;
      }
      
      .dashboard-card {
        max-width: 100% !important;
      }

      .navbar {
        padding: 20px !important;
      }

      .nav-list {
        flex-direction: column !important;
        gap: 15px !important;
      }

      .nav-item {
        width: 60px !important;
        height: 60px !important;
      }

      .nav-item:hover {
        width: 180px !important;
      }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Load custom CSS theme
load_custom_css()



def create_custom_metric_card(title: str, value: str, change: str, is_positive: bool = True):
    """Create a custom styled metric card with the new theme."""
    change_icon = "▲" if is_positive else "▼"
    change_class = "positive" if is_positive else "negative"
    
    card_html = f"""
    <div class="dashboard-card">
        <div class="card-header">
            <span class="card-title">{title}</span>
            <div class="icon-placeholder"></div>
        </div>
        <div class="card-metric">{value}</div>
        <div class="card-footer {change_class}">
            <span class="change-icon">{change_icon}</span>
            <span class="change-percentage">{change}</span>
        </div>
    </div>
    """
    return card_html


def load_enhanced_feedback_data(file_path: str = "../../output/processed_feedback_data.csv") -> pd.DataFrame:
    """Load the enhanced feedback data from CSV."""
    try:
        if not Path(file_path).exists():
            st.error(f"Enhanced feedback data not found at: {file_path}")
            st.info("Please run the feedback enhancement system first to generate the data.")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Map CSV columns to dashboard expected columns
        if 'sentiment' in df.columns:
            # Convert sentiment text to numeric scores
            sentiment_map = {'positive': 1.0, 'negative': -1.0, 'neutral': 0.0}
            df['sentiment_score'] = df['sentiment'].map(sentiment_map)
        
        if 'source_weight' in df.columns:
            df['source_metric'] = df['source_weight']
        
        # Add is_relevant column (mark all as relevant for demo)
        df['is_relevant'] = True
        
        return df
    except Exception as e:
        st.error(f"Error loading enhanced feedback data: {e}")
        return pd.DataFrame()


def display_enhanced_kpis(df: pd.DataFrame):
    """Display enhanced KPIs specific to the unified feedback data."""
    if df.empty:
        return
    
    st.subheader("Data Snapshot")
    
    # Create animated cards with the new theme
    card_html = f"""
    <div class="container">
        <div class="box">
            <span></span>
            <div class="content">
                <h2>Total Feedback</h2>
                <p>Comprehensive collection of user feedback across all channels and sources.</p>
                <a href="#">{len(df):,}</a>
            </div>
        </div>
        <div class="box">
            <span></span>
            <div class="content">
                <h2>Sentiment Score</h2>
                <p>Average sentiment analysis across all feedback entries and themes.</p>
                <a href="#">{df['sentiment_score'].mean():.2f}</a>
            </div>
        </div>
        <div class="box">
            <span></span>
            <div class="content">
                <h2>Relevance Rate</h2>
                <p>Percentage of feedback marked as relevant and actionable for business insights.</p>
                <a href="#">{(df['is_relevant'].sum() / len(df)) * 100:.1f}%</a>
            </div>
        </div>
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)


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
        'customer_id': 'count'
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
        'customer_id': 'count',
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
        go.Scatter(x=daily_data['date'], y=daily_data['customer_id'],
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
        'customer_id': 'count'
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
        'customer_id': 'count',
        'source_metric': 'mean'
    }).reset_index()
    
    fig = px.scatter(
        theme_data,
        x='sentiment_score',
        y='source_metric',
        size='customer_id',
        hover_name='theme',
        title="Theme Analysis: Sentiment vs Source Metric (Bubble Size = Feedback Count)",
        labels={
            'sentiment_score': 'Average Sentiment Score',
            'source_metric': 'Average Source Metric',
            'customer_id': 'Feedback Count'
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
            'customer_id': st.column_config.TextColumn('Customer ID', width='small'),
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


# Authentication and Role Management Functions
def show_login_page():
    """Display the login page with demo credentials"""
    st.title("🔐 Secure Enhanced Feedback Analytics")
    st.subheader("Advanced Trade Insight Engine - Secure Access Portal")
    
    # Login instructions
    st.info("**Demo Credentials:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**👑 Admin Access**")
        st.code("Username: admin\nPassword: admin123")
        st.caption("Full system access + export")
    
    with col2:
        st.write("**📊 Analyst Access**") 
        st.code("Username: analyst\nPassword: analyst123")
        st.caption("Dashboard + advanced filters + export")
    
    with col3:
        st.write("**👀 Viewer Access**")
        st.code("Username: viewer\nPassword: viewer123") 
        st.caption("Read-only dashboard access")

def show_user_info_sidebar(name: str, username: str, role: str):
    """Display user information in sidebar"""
    st.sidebar.title("👤 User Profile")
    
    # User info
    st.sidebar.write(f"**Name:** {name}")
    st.sidebar.write(f"**Username:** {username}")
    st.sidebar.write(f"**Role:** {role.title()}")
    
    # Role badge
    role_colors = {
        'admin': '🔴',
        'analyst': '🟡', 
        'viewer': '🟢'
    }
    st.sidebar.write(f"**Access Level:** {role_colors.get(role, '⚪')} {role.title()}")
    
    st.sidebar.markdown("---")

def get_role_permissions(role: str) -> Dict[str, bool]:
    """Get permissions for a specific role"""
    permissions = {
        'admin': {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': True,
            'show_advanced_filters': True,
            'show_all_tabs': True
        },
        'analyst': {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': True,
            'show_advanced_filters': True,
            'show_all_tabs': True
        },
        'viewer': {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': False,
            'show_advanced_filters': False,
            'show_all_tabs': True
        }
    }
    return permissions.get(role, permissions['viewer'])

def show_role_specific_features(role: str):
    """Show role-specific features and limitations"""
    
    if role == 'admin':
        with st.expander("🔴 Admin Features"):
            st.write("✅ Full dashboard access")
            st.write("✅ All data sources and analytics")
            st.write("✅ Data export capabilities")
            st.write("✅ Advanced filtering options")
            st.write("✅ All visualization tabs")
            st.write("✅ System administration")
            
    elif role == 'analyst':
        st.info("🟡 **Analyst Access** - Dashboard and reporting privileges")
        with st.expander("🟡 Analyst Features"):
            st.write("✅ Full dashboard access")
            st.write("✅ All data sources and analytics")
            st.write("✅ Data export capabilities")
            st.write("✅ Advanced filtering options")
            st.write("✅ All visualization tabs")
            st.write("❌ System administration")
            
    elif role == 'viewer':
        st.warning("🟢 **Viewer Access** - Read-only privileges")
        with st.expander("🟢 Viewer Features"):
            st.write("✅ Dashboard viewing")
            st.write("✅ Basic data analytics")
            st.write("✅ Chart interactions")
            st.write("✅ Basic filtering")
            st.write("❌ Data export")
            st.write("❌ Advanced filtering")
            st.write("❌ System administration")

def display_enhanced_filters_with_permissions(df: pd.DataFrame, permissions: Dict[str, bool]):
    """Display enhanced filtering options based on user permissions"""
    st.sidebar.header("🔍 Enhanced Filters")
    
    filters = {}
    
    # Date range filter (available to all)
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
    
    # Basic filters (available to all)
    source_options = ['All'] + sorted(df['source_channel'].unique().tolist())
    filters['source_channel'] = st.sidebar.selectbox("Source Channel", source_options)
    
    theme_options = ['All'] + sorted(df['theme'].unique().tolist())
    filters['theme'] = st.sidebar.selectbox("Theme", theme_options)
    
    # Advanced filters (only for admin/analyst)
    if permissions.get('show_advanced_filters', False):
        st.sidebar.markdown("### 🔧 Advanced Filters")
        
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
    else:
        # Default values for viewers
        filters['strategic_goal'] = 'All'
        filters['sentiment_range'] = (float(df['sentiment_score'].min()), float(df['sentiment_score'].max()))
        filters['relevance'] = True
    
    return filters

def display_enhanced_data_table_with_permissions(df: pd.DataFrame, permissions: Dict[str, bool]):
    """Display enhanced data table with role-based permissions"""
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
            'customer_id': st.column_config.TextColumn('Customer ID', width='small'),
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
    
    # Export functionality (only for admin/analyst)
    if permissions.get('show_export', False):
        if st.button("📥 Export Filtered Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"filtered_feedback_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("💡 Export functionality requires Analyst or Admin access")

def main():
    """Main secure enhanced dashboard application with authentication"""
    
    # Authentication check based on available auth type
    if AUTH_TYPE == 'full':
        # Use streamlit-authenticator
        authenticator = get_authenticator()
        
        try:
            name, authentication_status, username = authenticator.login('Login')
        except Exception as e:
            st.error(f"Login system error: {e}")
            name, authentication_status, username = None, None, None
        
        # Handle authentication states
        if authentication_status == False:
            st.error('Username/password is incorrect')
            show_login_page()
            return
            
        elif authentication_status == None:
            st.warning('Please enter your username and password')
            show_login_page()
            return
            
        elif authentication_status == True:
            # User is authenticated
            user_role = get_user_role(username)
            user_info = get_user_info(username)
            
            # Show user info in sidebar
            show_user_info_sidebar(name, username, user_role)
            
            # Logout button
            try:
                authenticator.logout('Logout', 'sidebar')
            except:
                if st.sidebar.button('Logout'):
                    st.session_state.clear()
                    st.rerun()
    
    elif AUTH_TYPE == 'simple':
        # Use simple authentication with bcrypt
        name, authentication_status, username = check_authentication()
        
        if not authentication_status:
            return
        
        # Get user role from session state
        user_info = st.session_state.get('user_info', {})
        user_role = user_info.get('role', 'viewer')
        
        # Show logout button
        show_logout_button()
    
    elif AUTH_TYPE == 'fallback':
        # Use simple fallback authentication (no dependencies)
        name, authentication_status, username = check_authentication()
        
        if not authentication_status:
            return
        
        # Set default user role for demo
        user_role = 'admin'
        
        # Set user info in session state
        if 'user_info' not in st.session_state:
            st.session_state['user_info'] = {'role': user_role}
        
        # Show user info in sidebar if authenticated
        if name and username:
            show_user_info_sidebar(name, username, user_role)
        
        # Show logout button
        show_logout_button()
    
    else:
        st.error("Authentication system not available")
        return
    
    # Main dashboard for authenticated users
    st.title("Susbase Analytics Dashboard")
    st.write(f"Welcome back, **{name}**! 👋")
    
    # Show role-specific features
    show_role_specific_features(user_role)
    
    # Get role permissions
    permissions = get_role_permissions(user_role)
    
    try:
        # Load enhanced data
        with st.spinner("Loading secure enhanced dashboard..."):
            df = load_enhanced_feedback_data()
        
        if df.empty:
            st.error("No enhanced feedback data available. Please run the feedback enhancement system first.")
            st.info("Run: `python feedback_enhancement_system.py` to generate the required data.")
            return
        
        # Display filters in sidebar with permissions
        filters = display_enhanced_filters_with_permissions(df, permissions)
        
        # Apply filters
        filtered_df = apply_enhanced_filters(df, filters)
        
        # Display filter results
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df):,} of {len(df):,} records after filtering")
        

        
        # Enhanced KPIs
        display_enhanced_kpis(filtered_df)
        
        st.markdown("---")
        
        # Create custom tab navigation with hover underline effects
        if permissions.get('show_all_tabs', True):
            # Custom Tab Navigation (Visual Only)
            tab_nav_html = """
            <div class="tab-navbar">
                <ul class="tab-nav-list">
                    <li class="tab-nav-item" onclick="switchToTab('tab1')">📈 Strategic Analysis</li>
                    <li class="tab-nav-item" onclick="switchToTab('tab2')">🎯 Sentiment Intelligence</li>
                    <li class="tab-nav-item" onclick="switchToTab('tab3')">📊 Source Comparison</li>
                    <li class="tab-nav-item" onclick="switchToTab('tab4')">🕒 Time Trends</li>
                    <li class="tab-nav-item" onclick="switchToTab('tab5')">📋 Data Explorer</li>
                </ul>
            </div>
            """
            st.markdown(tab_nav_html, unsafe_allow_html=True)
            
            # Streamlit Native Tabs (Hidden but Functional)
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "Strategic Analysis", 
                "Sentiment Intelligence", 
                "Source Comparison",
                "Time Trends",
                "Data Explorer"
            ])
            
            # Hide the default Streamlit tabs
            hide_streamlit_tabs = """
            <style>
            [data-testid="stTabs"] > div:first-child {
                display: none;
            }
            </style>
            """
            st.markdown(hide_streamlit_tabs, unsafe_allow_html=True)
            
            # JavaScript to sync underline tabs with Streamlit tabs
            tab_js = """
            <script>
            let currentTab = 'tab1';
                
            function switchToTab(tabId) {
                // Update active state in underline navbar
                const tabItems = document.querySelectorAll('.tab-nav-item');
                tabItems.forEach(item => item.classList.remove('active'));
                event.target.classList.add('active');
                
                // Store current tab for Streamlit
                currentTab = tabId;
                
                // Trigger Streamlit tab change
                const streamlitTabs = document.querySelectorAll('[data-testid*="stTabs"] button');
                const tabIndex = parseInt(tabId.replace('tab', '')) - 1;
                if (streamlitTabs[tabIndex]) {
                    streamlitTabs[tabIndex].click();
                }
            }
            
            // Set first tab as active by default
                document.addEventListener('DOMContentLoaded', function() {
                    const firstTab = document.querySelector('.tab-nav-item');
                    if (firstTab) {
                        firstTab.classList.add('active');
                    }
                });

            </script>
            """
            st.markdown(tab_js, unsafe_allow_html=True)
            
            # Tab 1: Strategic Analysis
            with tab1:
                # Strategic Goal Analysis
                if st.button("📊 Strategic Goal Analysis", key="goal_analysis_btn"):
                    st.session_state.show_goal_analysis = not st.session_state.get('show_goal_analysis', True)
                
                if st.session_state.get('show_goal_analysis', True):
                    fig = create_strategic_goal_analysis(filtered_df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Theme vs Sentiment Bubble Analysis
                if st.button("🎯 Theme vs Sentiment Bubble Analysis", key="theme_bubble_btn"):
                    st.session_state.show_theme_bubble = not st.session_state.get('show_theme_bubble', True)
                
                if st.session_state.get('show_theme_bubble', True):
                    fig = create_theme_sentiment_bubble_chart(filtered_df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            # Tab 2: Sentiment Intelligence
            with tab2:
                # Sentiment Score Heatmap
                if st.button("🔥 Sentiment Score Heatmap", key="heatmap_btn"):
                    st.session_state.show_heatmap = not st.session_state.get('show_heatmap', True)
                
                if st.session_state.get('show_heatmap', True):
                    fig = create_sentiment_heatmap(filtered_df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Sentiment Distribution Analysis
                if st.button("📈 Sentiment Distribution Analysis", key="sentiment_dist_btn"):
                    st.session_state.show_sentiment_dist = not st.session_state.get('show_sentiment_dist', True)
                
                if st.session_state.get('show_sentiment_dist', True):
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
            
            # Tab 3: Source Comparison
            with tab3:
                # Multi-Dimensional Source Comparison
                if st.button("📊 Multi-Dimensional Source Comparison", key="source_comp_btn"):
                    st.session_state.show_source_comp = not st.session_state.get('show_source_comp', True)
                
                if st.session_state.get('show_source_comp', True):
                    fig = create_source_channel_comparison(filtered_df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Source Channel Metrics Table
                if st.button("📋 Source Channel Metrics Table", key="source_metrics_btn"):
                    st.session_state.show_source_metrics = not st.session_state.get('show_source_metrics', True)
                
                if st.session_state.get('show_source_metrics', True):
                    source_metrics = filtered_df.groupby('source_channel').agg({
                        'customer_id': 'count',
                        'sentiment_score': ['mean', 'std'],
                        'source_metric': ['mean', 'std'],
                        'is_relevant': 'sum'
                    }).round(3)
                    
                    st.dataframe(source_metrics, use_container_width=True)
            
            # Tab 4: Time Trends
            with tab4:
                # Enhanced Time Series Analysis
                if st.button("🕒 Enhanced Time Series Analysis", key="time_series_btn"):
                    st.session_state.show_time_series = not st.session_state.get('show_time_series', True)
                
                if st.session_state.get('show_time_series', True):
                    fig = create_enhanced_time_series(filtered_df)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
            
            # Tab 5: Data Explorer
            with tab5:
                # Enhanced Data Table
                if st.button("📋 Enhanced Feedback Data Table", key="data_table_btn"):
                    st.session_state.show_data_table = not st.session_state.get('show_data_table', True)
                
                if st.session_state.get('show_data_table', True):
                    display_enhanced_data_table_with_permissions(filtered_df, permissions)
        
        # Show session info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔒 Session Info")
        st.sidebar.write(f"**Records:** {len(df):,}")
        st.sidebar.write(f"**Filtered:** {len(filtered_df):,}")
        st.sidebar.write(f"**Sources:** {df['source_channel'].nunique()}")
        if 'login_time' not in st.session_state:
            import datetime
            st.session_state.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.sidebar.write(f"**Login Time:** {st.session_state.get('login_time', 'Unknown')}")
        
    except Exception as e:
        st.error(f"Dashboard error: {str(e)}")
        st.error("Please check that all required data files are available and try again.")


if __name__ == "__main__":
    main()