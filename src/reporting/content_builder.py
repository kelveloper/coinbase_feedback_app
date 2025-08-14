"""
Content Builder Module for Advanced Trade Insight Engine

This module provides functions to aggregate and analyze customer feedback data
to generate structured content for business reports. It identifies key insights,
pain points, praised features, and strategic goal alignments.

Functions:
    group_by_theme: Group feedback by theme and calculate aggregated metrics
    identify_top_pain_points: Find highest negative impact feedback items
    identify_praised_features: Find positive sentiment with high impact items
    extract_strategic_insights: Analyze feedback by strategic goal alignment
    generate_executive_summary: Create high-level metrics and insights
    build_report_content: Orchestrate all content building functions
"""

import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def group_by_theme(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group feedback by theme and calculate aggregated impact metrics.
    
    Args:
        df (pd.DataFrame): DataFrame with feedback records including theme and impact_score
        
    Returns:
        pd.DataFrame: Grouped data with theme-level aggregations
        
    Requirements: 5.1
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to group_by_theme")
        return pd.DataFrame()
    
    try:
        # Group by theme and calculate aggregations
        theme_groups = df.groupby('theme').agg({
            'impact_score': ['sum', 'mean', 'count'],
            'sentiment': lambda x: (x == 'negative').sum(),  # Count of negative sentiments
            'customer_id': 'nunique'  # Unique customers per theme
        }).round(4)
        
        # Flatten column names
        theme_groups.columns = [
            'total_impact', 'avg_impact', 'feedback_count', 
            'negative_count', 'unique_customers'
        ]
        
        # Reset index to make theme a column
        theme_groups = theme_groups.reset_index()
        
        # Sort by total impact score (descending)
        theme_groups = theme_groups.sort_values('total_impact', ascending=False)
        
        logger.info(f"Grouped feedback into {len(theme_groups)} themes")
        return theme_groups
        
    except Exception as e:
        logger.error(f"Error grouping by theme: {e}")
        return pd.DataFrame()


def identify_top_pain_points(df: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Identify top pain points based on highest negative impact scores.
    
    Args:
        df (pd.DataFrame): DataFrame with feedback records
        top_n (int): Number of top pain points to return
        
    Returns:
        List[Dict]: List of pain point dictionaries with details
        
    Requirements: 5.2
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to identify_top_pain_points")
        return []
    
    try:
        # Filter for negative sentiment feedback
        negative_feedback = df[df['sentiment'] == 'negative'].copy()
        
        if negative_feedback.empty:
            logger.info("No negative feedback found")
            return []
        
        # Sort by impact score (descending) and get top N
        top_pain_points = negative_feedback.nlargest(top_n, 'impact_score')
        
        pain_points = []
        for _, row in top_pain_points.iterrows():
            pain_point = {
                'theme': row.get('theme', 'Unknown'),
                'impact_score': round(row.get('impact_score', 0), 4),
                'feedback_text': row.get('feedback_text', '')[:200] + '...' if len(str(row.get('feedback_text', ''))) > 200 else row.get('feedback_text', ''),
                'source_channel': row.get('source_channel', row.get('source', 'Unknown')),
                'severity': row.get('severity', 1.0),
                'strategic_goal': row.get('strategic_goal', 'Other'),
                'customer_id': row.get('customer_id', 'Unknown')
            }
            pain_points.append(pain_point)
        
        logger.info(f"Identified {len(pain_points)} top pain points")
        return pain_points
        
    except Exception as e:
        logger.error(f"Error identifying pain points: {e}")
        return []


def identify_praised_features(df: pd.DataFrame, top_n: int = 3) -> List[Dict[str, Any]]:
    """
    Identify praised features based on positive sentiment and high impact scores.
    
    Args:
        df (pd.DataFrame): DataFrame with feedback records
        top_n (int): Number of praised features to return
        
    Returns:
        List[Dict]: List of praised feature dictionaries with details
        
    Requirements: 5.3
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to identify_praised_features")
        return []
    
    try:
        # Filter for positive sentiment feedback
        positive_feedback = df[df['sentiment'] == 'positive'].copy()
        
        if positive_feedback.empty:
            logger.info("No positive feedback found")
            return []
        
        # Sort by impact score (descending) and get top N
        top_praised = positive_feedback.nlargest(top_n, 'impact_score')
        
        praised_features = []
        for _, row in top_praised.iterrows():
            praised_feature = {
                'theme': row.get('theme', 'Unknown'),
                'impact_score': round(row.get('impact_score', 0), 4),
                'feedback_text': row.get('feedback_text', '')[:200] + '...' if len(str(row.get('feedback_text', ''))) > 200 else row.get('feedback_text', ''),
                'source_channel': row.get('source_channel', row.get('source', 'Unknown')),
                'severity': row.get('severity', 1.0),
                'strategic_goal': row.get('strategic_goal', 'Other'),
                'customer_id': row.get('customer_id', 'Unknown')
            }
            praised_features.append(praised_feature)
        
        logger.info(f"Identified {len(praised_features)} praised features")
        return praised_features
        
    except Exception as e:
        logger.error(f"Error identifying praised features: {e}")
        return []


def extract_strategic_insights(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Extract insights by strategic goal alignment and impact.
    
    Args:
        df (pd.DataFrame): DataFrame with feedback records
        
    Returns:
        Dict: Strategic goal insights with metrics and top items
        
    Requirements: 5.4
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to extract_strategic_insights")
        return {}
    
    try:
        strategic_insights = {}
        
        # Group by strategic goal
        strategic_groups = df.groupby('strategic_goal').agg({
            'impact_score': ['sum', 'mean', 'count'],
            'sentiment': lambda x: {
                'positive': (x == 'positive').sum(),
                'negative': (x == 'negative').sum(),
                'neutral': (x == 'neutral').sum()
            }
        })
        
        # Process each strategic goal
        for goal in df['strategic_goal'].unique():
            if pd.isna(goal) or goal == '':
                continue
                
            goal_data = df[df['strategic_goal'] == goal]
            
            # Calculate metrics
            total_impact = goal_data['impact_score'].sum()
            avg_impact = goal_data['impact_score'].mean()
            feedback_count = len(goal_data)
            
            # Sentiment breakdown
            sentiment_counts = goal_data['sentiment'].value_counts().to_dict()
            
            # Top feedback item for this goal
            top_item = goal_data.nlargest(1, 'impact_score')
            top_feedback = None
            if not top_item.empty:
                row = top_item.iloc[0]
                top_feedback = {
                    'theme': row.get('theme', 'Unknown'),
                    'impact_score': round(row.get('impact_score', 0), 4),
                    'feedback_text': row.get('feedback_text', '')[:150] + '...' if len(str(row.get('feedback_text', ''))) > 150 else row.get('feedback_text', ''),
                    'sentiment': row.get('sentiment', 'neutral')
                }
            
            strategic_insights[goal] = {
                'total_impact': round(total_impact, 4),
                'avg_impact': round(avg_impact, 4),
                'feedback_count': feedback_count,
                'sentiment_breakdown': sentiment_counts,
                'top_feedback': top_feedback
            }
        
        # Sort by total impact
        strategic_insights = dict(sorted(
            strategic_insights.items(), 
            key=lambda x: x[1]['total_impact'], 
            reverse=True
        ))
        
        logger.info(f"Extracted insights for {len(strategic_insights)} strategic goals")
        return strategic_insights
        
    except Exception as e:
        logger.error(f"Error extracting strategic insights: {e}")
        return {}


def generate_executive_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate executive summary with high-level metrics and key insights.
    
    Args:
        df (pd.DataFrame): DataFrame with feedback records
        
    Returns:
        Dict: Executive summary with key metrics
        
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to generate_executive_summary")
        return {}
    
    try:
        # Basic metrics
        total_feedback = len(df)
        unique_customers = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
        
        # Sentiment distribution
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        sentiment_percentages = {
            sentiment: round((count / total_feedback) * 100, 1) 
            for sentiment, count in sentiment_counts.items()
        }
        
        # Impact metrics
        total_impact = df['impact_score'].sum()
        avg_impact = df['impact_score'].mean()
        max_impact = df['impact_score'].max()
        
        # Top theme by impact
        theme_impacts = df.groupby('theme')['impact_score'].sum().sort_values(ascending=False)
        top_theme = theme_impacts.index[0] if not theme_impacts.empty else 'Unknown'
        top_theme_impact = theme_impacts.iloc[0] if not theme_impacts.empty else 0
        
        # Source distribution
        source_counts = df['source_channel'].value_counts().to_dict() if 'source_channel' in df.columns else df['source'].value_counts().to_dict() if 'source' in df.columns else {}
        
        # Time range (if timestamp available)
        time_range = {}
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            valid_timestamps = df['timestamp'].dropna()
            if not valid_timestamps.empty:
                time_range = {
                    'start_date': valid_timestamps.min().strftime('%Y-%m-%d'),
                    'end_date': valid_timestamps.max().strftime('%Y-%m-%d'),
                    'days_covered': (valid_timestamps.max() - valid_timestamps.min()).days + 1
                }
        
        summary = {
            'total_feedback_items': total_feedback,
            'unique_customers': unique_customers,
            'sentiment_distribution': sentiment_counts,
            'sentiment_percentages': sentiment_percentages,
            'impact_metrics': {
                'total_impact': round(total_impact, 4),
                'average_impact': round(avg_impact, 4),
                'maximum_impact': round(max_impact, 4)
            },
            'top_theme': {
                'name': top_theme,
                'total_impact': round(top_theme_impact, 4)
            },
            'source_distribution': source_counts,
            'time_range': time_range
        }
        
        logger.info("Generated executive summary")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {e}")
        return {}


def build_report_content(df: pd.DataFrame, top_n: int = 3) -> Dict[str, Any]:
    """
    Orchestrate all content building functions to create comprehensive report content.
    
    Args:
        df (pd.DataFrame): DataFrame with enriched feedback records
        top_n (int): Number of top items to include in each category
        
    Returns:
        Dict: Complete report content structure
        
    Requirements: 5.1, 5.2, 5.3, 5.4
    """
    if df.empty:
        logger.error("Empty DataFrame provided to build_report_content")
        return {}
    
    try:
        logger.info("Building comprehensive report content")
        
        # Generate all content sections
        executive_summary = generate_executive_summary(df)
        theme_analysis = group_by_theme(df)
        pain_points = identify_top_pain_points(df, top_n)
        praised_features = identify_praised_features(df, top_n)
        strategic_insights = extract_strategic_insights(df)
        
        # Compile complete report content
        report_content = {
            'executive_summary': executive_summary,
            'theme_analysis': theme_analysis.to_dict('records') if not theme_analysis.empty else [],
            'top_pain_points': pain_points,
            'praised_features': praised_features,
            'strategic_insights': strategic_insights,
            'metadata': {
                'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_records_processed': len(df),
                'content_sections': ['executive_summary', 'theme_analysis', 'pain_points', 'praised_features', 'strategic_insights']
            }
        }
        
        logger.info("Successfully built complete report content")
        return report_content
        
    except Exception as e:
        logger.error(f"Error building report content: {e}")
        return {}