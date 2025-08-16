"""
FastAPI Backend for Susbase Insights

This module provides REST API endpoints that expose the existing Python data processing
pipeline to the React frontend. It maintains all the existing functionality while providing
a modern API interface.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import pandas as pd
import sys
import os
import logging
from datetime import datetime
import tempfile
import json

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import existing modules
from data_processing.data_loader import load_all_csv_files, get_loading_summary
from data_processing.data_normalizer import normalize_and_unify_data
from analysis.nlp_models import enrich_dataframe_with_nlp
from analysis.scoring_engine import enrich_dataframe_with_scores
from reporting.report_generator import generate_complete_report
from config import CSV_FILE_PATHS, OUTPUT_PATHS, DATA_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Susbase Insights API",
    description="REST API for customer feedback analysis and insights",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API responses
class KPIResponse(BaseModel):
    total_items: int
    average_sentiment: str
    top_theme: str
    high_impact_count: int

class ThemeData(BaseModel):
    theme: str
    impact: float
    count: int

class SentimentData(BaseModel):
    sentiment: str
    count: int
    percentage: float

class FeedbackItem(BaseModel):
    source: str
    theme: str
    sentiment: str
    impact_score: float
    content: Optional[str] = None

class DashboardData(BaseModel):
    kpis: KPIResponse
    theme_rankings: List[ThemeData]
    sentiment_distribution: List[SentimentData]
    recent_feedback: List[FeedbackItem]

class DataProcessingResponse(BaseModel):
    success: bool
    message: str
    records_processed: int
    processing_time: float

# Global variable to cache processed data
_cached_data: Optional[pd.DataFrame] = None
_cache_timestamp: Optional[datetime] = None

def get_processed_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Get processed feedback data with caching.
    
    Args:
        force_refresh (bool): Whether to force refresh the cache
        
    Returns:
        pd.DataFrame: Processed feedback data with impact scores
    """
    global _cached_data, _cache_timestamp
    
    # Check if we need to refresh the cache
    if force_refresh or _cached_data is None or (
        _cache_timestamp and 
        (datetime.now() - _cache_timestamp).seconds > 300  # 5 minutes cache
    ):
        logger.info("Loading and processing data...")
        start_time = datetime.now()
        
        try:
            # Load CSV files
            loaded_data = load_all_csv_files(str(DATA_DIR))
            if not loaded_data:
                raise HTTPException(status_code=404, detail="No data files found")
            
            # Normalize data
            normalized_df = normalize_and_unify_data(loaded_data)
            if normalized_df.empty:
                raise HTTPException(status_code=422, detail="Data normalization failed")
            
            # Apply NLP processing
            enriched_df = enrich_dataframe_with_nlp(normalized_df)
            if enriched_df.empty:
                raise HTTPException(status_code=422, detail="NLP processing failed")
            
            # Calculate impact scores
            processed_df = enrich_dataframe_with_scores(enriched_df)
            if processed_df.empty:
                raise HTTPException(status_code=422, detail="Impact scoring failed")
            
            # Update cache
            _cached_data = processed_df
            _cache_timestamp = datetime.now()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Data processed successfully in {processing_time:.2f}s - {len(processed_df)} records")
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise HTTPException(status_code=500, detail=f"Data processing error: {str(e)}")
    
    return _cached_data

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Susbase Insights API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_status": "active" if _cached_data is not None else "empty"
    }

@app.get("/api/kpis", response_model=KPIResponse)
async def get_kpis():
    """Get key performance indicators."""
    try:
        df = get_processed_data()
        
        # Calculate KPIs
        total_items = len(df)
        
        # Calculate average sentiment
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
        
        # Count high impact items (top 25%)
        if 'impact_score' in df.columns:
            impact_threshold = df['impact_score'].quantile(0.75)
            high_impact_count = len(df[df['impact_score'] >= impact_threshold])
        else:
            high_impact_count = 0
        
        return KPIResponse(
            total_items=total_items,
            average_sentiment=avg_sentiment,
            top_theme=top_theme,
            high_impact_count=high_impact_count
        )
        
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        raise HTTPException(status_code=500, detail=f"KPI calculation error: {str(e)}")

@app.get("/api/themes", response_model=List[ThemeData])
async def get_theme_rankings(limit: int = Query(10, ge=1, le=50)):
    """Get theme rankings by impact score."""
    try:
        df = get_processed_data()
        
        if 'theme' not in df.columns or 'impact_score' not in df.columns:
            return []
        
        # Group by theme and calculate impact
        theme_stats = df.groupby('theme').agg({
            'impact_score': ['sum', 'count']
        }).reset_index()
        
        theme_stats.columns = ['theme', 'impact', 'count']
        theme_stats = theme_stats.sort_values('impact', ascending=False).head(limit)
        
        return [
            ThemeData(
                theme=row['theme'],
                impact=float(row['impact']),
                count=int(row['count'])
            )
            for _, row in theme_stats.iterrows()
        ]
        
    except Exception as e:
        logger.error(f"Error getting theme rankings: {e}")
        raise HTTPException(status_code=500, detail=f"Theme ranking error: {str(e)}")

@app.get("/api/sentiment", response_model=List[SentimentData])
async def get_sentiment_distribution():
    """Get sentiment distribution."""
    try:
        df = get_processed_data()
        
        if 'sentiment' not in df.columns:
            return []
        
        # Calculate sentiment distribution
        sentiment_counts = df['sentiment'].value_counts()
        total_count = len(df)
        
        return [
            SentimentData(
                sentiment=sentiment,
                count=int(count),
                percentage=round((count / total_count) * 100, 1)
            )
            for sentiment, count in sentiment_counts.items()
        ]
        
    except Exception as e:
        logger.error(f"Error getting sentiment distribution: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis error: {str(e)}")

@app.get("/api/feedback", response_model=List[FeedbackItem])
async def get_recent_feedback(
    limit: int = Query(20, ge=1, le=100),
    theme: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    source: Optional[str] = Query(None)
):
    """Get recent feedback items with optional filtering."""
    try:
        df = get_processed_data()
        
        # Apply filters
        filtered_df = df.copy()
        
        if theme:
            filtered_df = filtered_df[filtered_df['theme'] == theme]
        if sentiment:
            filtered_df = filtered_df[filtered_df['sentiment'] == sentiment]
        if source:
            filtered_df = filtered_df[filtered_df['source_channel'] == source]
        
        # Sort by impact score and get top items
        if 'impact_score' in filtered_df.columns:
            filtered_df = filtered_df.sort_values('impact_score', ascending=False)
        
        filtered_df = filtered_df.head(limit)
        
        return [
            FeedbackItem(
                source=row.get('source_channel', row.get('source', 'Unknown')),
                theme=row.get('theme', 'Other'),
                sentiment=row.get('sentiment', 'neutral'),
                impact_score=float(row.get('impact_score', 0)),
                content=row.get('content', row.get('text', None))
            )
            for _, row in filtered_df.iterrows()
        ]
        
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback retrieval error: {str(e)}")

@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard_data():
    """Get complete dashboard data in a single request."""
    try:
        # Get all data components
        kpis = await get_kpis()
        themes = await get_theme_rankings(limit=5)
        sentiment = await get_sentiment_distribution()
        feedback = await get_recent_feedback(limit=10)
        
        return DashboardData(
            kpis=kpis,
            theme_rankings=themes,
            sentiment_distribution=sentiment,
            recent_feedback=feedback
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard data error: {str(e)}")

@app.post("/api/refresh", response_model=DataProcessingResponse)
async def refresh_data():
    """Force refresh of processed data."""
    try:
        start_time = datetime.now()
        df = get_processed_data(force_refresh=True)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DataProcessingResponse(
            success=True,
            message="Data refreshed successfully",
            records_processed=len(df),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return DataProcessingResponse(
            success=False,
            message=f"Data refresh failed: {str(e)}",
            records_processed=0,
            processing_time=0
        )

@app.get("/api/report")
async def generate_pdf_report():
    """Generate and download PDF report."""
    try:
        df = get_processed_data()
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Generate PDF report
        report_results = generate_complete_report(df, pdf_path, top_n=3)
        
        if report_results.get('success', False):
            return FileResponse(
                pdf_path,
                media_type='application/pdf',
                filename='insight_report.pdf'
            )
        else:
            raise HTTPException(status_code=500, detail="PDF generation failed")
            
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@app.get("/api/export")
async def export_data():
    """Export processed data as CSV."""
    try:
        df = get_processed_data()
        
        # Create temporary file for CSV
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w') as tmp_file:
            csv_path = tmp_file.name
        
        # Export to CSV
        df.to_csv(csv_path, index=False)
        
        return FileResponse(
            csv_path,
            media_type='text/csv',
            filename='feedback_data.csv'
        )
        
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(status_code=500, detail=f"Data export error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Susbase Insights API server...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
