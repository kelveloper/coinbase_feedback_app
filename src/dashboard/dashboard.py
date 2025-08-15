"""
Main Dashboard Application for Advanced Trade Insight Engine

This module provides the main Streamlit dashboard application that integrates:
- KPI components and data tables from components module
- Interactive charts from charts module  
- Data loading and processing pipeline
- Error handling and user-friendly messages

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import streamlit as st
import pandas as pd
import sys
import os
from typing import Dict, Any, Optional
import logging

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_processing.data_loader import load_all_csv_files, get_loading_summary
from data_processing.data_normalizer import normalize_and_unify_data
from analysis.scoring_engine import enrich_dataframe_with_scores
from dashboard.components import (
    display_kpi_header,
    create_filter_controls,
    display_filterable_data_table,
    display_summary_stats
)
from dashboard.charts import create_comprehensive_dashboard_charts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Advanced Trade Insight Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def load_and_process_data(data_directory: str = "csv_mock_data") -> Optional[pd.DataFrame]:
    """
    Load and process all feedback data for dashboard display.
    
    Args:
        data_directory (str): Directory containing CSV files
        
    Returns:
        Optional[pd.DataFrame]: Processed DataFrame with impact scores or None if error
        
    Requirements: 6.4
    """
    try:
        with st.spinner("Loading feedback data..."):
            # Load CSV files
            loaded_data = load_all_csv_files(data_directory)
            
            if not loaded_data:
                st.error(f"No data files found in directory: {data_directory}")
                st.info("Please ensure the following files exist:")
                st.info("- coinbase_advance_apple_reviews.csv")
                st.info("- coinbase_advanceGoogle_Play.csv") 
                st.info("- coinbase_advance_internal_sales_notes.csv")
                st.info("- coinbase_advanced_twitter_mentions.csv")
                return None
            
            # Display loading summary
            summary = get_loading_summary(loaded_data)
            st.success(f"Loaded {summary['total_records']} records from {summary['sources_loaded']} sources")
            
            # Normalize data
            with st.spinner("Normalizing data..."):
                normalized_df = normalize_and_unify_data(loaded_data)
                
                if normalized_df.empty:
                    st.error("Data normalization failed - no records to process")
                    return None
                
                st.info(f"Normalized {len(normalized_df)} feedback records")
            
            # Calculate impact scores
            with st.spinner("Calculating impact scores..."):
                enriched_df = enrich_dataframe_with_scores(normalized_df)
                
                if enriched_df.empty:
                    st.error("Impact score calculation failed")
                    return None
                
                st.success(f"Calculated impact scores for {len(enriched_df)} records")
            
            logger.info(f"Successfully processed {len(enriched_df)} records for dashboard")
            return enriched_df
            
    except Exception as e:
        logger.error(f"Error loading and processing data: {e}")
        st.error(f"Error loading data: {str(e)}")
        st.info("Please check that:")
        st.info("1. The data directory exists")
        st.info("2. CSV files are properly formatted")
        st.info("3. Required columns are present in each file")
        return None


def display_sidebar_info(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    """
    Display sidebar with data information and controls.
    
    Args:
        df (Optional[pd.DataFrame]): Processed DataFrame
        
    Returns:
        Dict[str, Any]: Sidebar configuration options
        
    Requirements: 6.3
    """
    st.sidebar.title("📊 Dashboard Controls")
    
    # Data refresh button
    if st.sidebar.button("🔄 Refresh Data", help="Reload data from CSV files"):
        st.rerun()
    
    # Data information
    if df is not None and not df.empty:
        st.sidebar.subheader("📈 Data Overview")
        st.sidebar.metric("Total Records", f"{len(df):,}")
        
        if 'source_channel' in df.columns:
            source_counts = df['source_channel'].value_counts()
        elif 'source' in df.columns:
            source_counts = df['source'].value_counts()
        else:
            source_counts = pd.Series()
        
        if not source_counts.empty:
            st.sidebar.write("**Records by Source:**")
            for source, count in source_counts.items():
                st.sidebar.write(f"• {source}: {count:,}")
        
        # Impact score statistics
        if 'impact_score' in df.columns:
            st.sidebar.subheader("🎯 Impact Scores")
            st.sidebar.metric("Average Impact", f"{df['impact_score'].mean():.2f}")
            st.sidebar.metric("Max Impact", f"{df['impact_score'].max():.2f}")
            
            # Top impact record
            top_impact_idx = df['impact_score'].idxmax()
            top_record = df.loc[top_impact_idx]
            st.sidebar.write("**Highest Impact:**")
            st.sidebar.write(f"Theme: {top_record.get('theme', 'N/A')}")
            st.sidebar.write(f"Score: {top_record.get('impact_score', 0):.2f}")
    
    else:
        st.sidebar.warning("No data loaded")
    
    # Configuration options
    st.sidebar.subheader("⚙️ Configuration")
    
    config = {
        'data_directory': st.sidebar.text_input(
            "Data Directory", 
            value="csv_mock_data",
            help="Directory containing CSV files"
        ),
        'show_raw_data': st.sidebar.checkbox(
            "Show Raw Data Table", 
            value=True,
            help="Display detailed data table"
        ),
        'show_charts': st.sidebar.checkbox(
            "Show Charts", 
            value=True,
            help="Display interactive charts"
        )
    }
    
    return config


def display_main_dashboard(df: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Display the main dashboard content with KPIs, filters, charts, and data table.
    
    Args:
        df (pd.DataFrame): Processed DataFrame with impact scores
        config (Dict[str, Any]): Dashboard configuration options
        
    Requirements: 6.1, 6.2, 6.3, 6.5
    """
    try:
        # Main title
        st.title("📊 Advanced Trade Insight Engine Dashboard")
        st.markdown("---")
        
        # KPI Header
        st.subheader("🎯 Key Performance Indicators")
        kpi_values = display_kpi_header(df)
        st.markdown("---")
        
        # Filter Controls
        filters = create_filter_controls(df)
        st.markdown("---")
        
        # Apply filters to get filtered dataset
        filtered_df = df.copy()
        for filter_name, filter_value in filters.items():
            if filter_value and filter_value != 'All':
                if filter_name in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[filter_name] == filter_value]
        
        # Display filtered data summary
        if len(filtered_df) != len(df):
            st.info(f"Showing {len(filtered_df):,} of {len(df):,} records after filtering")
        
        # Charts Section
        if config.get('show_charts', True) and not filtered_df.empty:
            st.subheader("📈 Interactive Visualizations")
            chart_status = create_comprehensive_dashboard_charts(filtered_df)
            
            # Display chart creation status
            successful_charts = sum(1 for status in chart_status.values() if status)
            if successful_charts > 0:
                st.success(f"Successfully created {successful_charts} of {len(chart_status)} charts")
            else:
                st.warning("No charts could be created with current data")
            
            st.markdown("---")
        
        # Data Table Section
        if config.get('show_raw_data', True):
            filtered_result = display_filterable_data_table(filtered_df, filters)
            
            # Summary statistics for filtered data
            if not filtered_result.empty:
                st.subheader("📊 Summary Statistics")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    stats = display_summary_stats(filtered_result)
                    
                    if 'sentiment_distribution' in stats:
                        st.write("**Sentiment Distribution:**")
                        for sentiment, count in stats['sentiment_distribution'].items():
                            percentage = (count / len(filtered_result) * 100)
                            st.write(f"• {sentiment.title()}: {count} ({percentage:.1f}%)")
                
                with col2:
                    if 'impact_stats' in stats:
                        st.write("**Impact Score Statistics:**")
                        impact_stats = stats['impact_stats']
                        st.write(f"• Mean: {impact_stats['mean']:.2f}")
                        st.write(f"• Median: {impact_stats['median']:.2f}")
                        st.write(f"• Range: {impact_stats['min']:.2f} - {impact_stats['max']:.2f}")
        
        logger.info(f"Dashboard displayed successfully with {len(filtered_df)} filtered records")
        
    except Exception as e:
        logger.error(f"Error displaying main dashboard: {e}")
        st.error(f"Error displaying dashboard: {str(e)}")
        st.info("Please try refreshing the data or check the error logs")


def display_error_page(error_message: str) -> None:
    """
    Display error page with troubleshooting information.
    
    Args:
        error_message (str): Error message to display
        
    Requirements: 6.4
    """
    st.title("⚠️ Dashboard Error")
    st.error(error_message)
    
    st.subheader("🔧 Troubleshooting Steps")
    
    st.write("**1. Check Data Files**")
    st.info("Ensure all required CSV files are present in the data directory:")
    st.code("""
    csv_mock_data/
    ├── coinbase_advance_apple_reviews.csv
    ├── coinbase_advanceGoogle_Play.csv
    ├── coinbase_advance_internal_sales_notes.csv
    └── coinbase_advanced_twitter_mentions.csv
    """)
    
    st.write("**2. Verify File Format**")
    st.info("Each CSV file should contain the required columns for its source type")
    
    st.write("**3. Check File Permissions**")
    st.info("Ensure the application has read access to the data directory and files")
    
    st.write("**4. Review Error Logs**")
    st.info("Check the application logs for detailed error information")
    
    if st.button("🔄 Try Again"):
        st.rerun()


def main():
    """
    Main dashboard application entry point.
    
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """
    try:
        # Display sidebar
        config = display_sidebar_info(None)
        
        # Load and process data
        df = load_and_process_data(config.get('data_directory', 'csv_mock_data'))
        
        if df is not None and not df.empty:
            # Update sidebar with loaded data info
            config = display_sidebar_info(df)
            
            # Display main dashboard
            display_main_dashboard(df, config)
            
        else:
            # Display error page
            display_error_page("Failed to load or process feedback data")
            
    except Exception as e:
        logger.error(f"Critical error in main dashboard: {e}")
        display_error_page(f"Critical application error: {str(e)}")


if __name__ == "__main__":
    main()