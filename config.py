"""
Configuration settings for the Advanced Trade Insight Engine MVP
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "csv_mock_data"
OUTPUT_DIR = BASE_DIR / "output"
SRC_DIR = BASE_DIR / "src"
TESTS_DIR = BASE_DIR / "tests"

# Input CSV file paths
CSV_FILE_PATHS = {
    "apple_reviews": DATA_DIR / "coinbase_advance_apple_reviews.csv",
    "google_reviews": DATA_DIR / "coinbase_advanceGoogle_Play.csv", 
    "twitter_mentions": DATA_DIR / "coinbase_advanced_twitter_mentions.csv",
    "internal_sales": DATA_DIR / "coinbase_advance_internal_sales_notes.csv"
}

# Output file paths
OUTPUT_PATHS = {
    "pdf_report": OUTPUT_DIR / "weekly_insight_report.pdf",
    "processed_data": OUTPUT_DIR / "processed_feedback_data.csv"
}

# NLP Configuration
NLP_CONFIG = {
    "sentiment_values": {
        "negative": 1.5,
        "neutral": 0.5,
        "positive": 0.1
    },
    "strategic_multipliers": {
        "aligned": 2.0,
        "default": 1.0
    },
    "default_values": {
        "sentiment": "neutral",
        "theme": "Other",
        "strategic_goal": "Other",
        "severity": 1.0
    }
}

# Source weighting configuration
SOURCE_WEIGHT_CONFIG = {
    "internal_sales": {
        "arr_divisor": 50000,
        "default_weight": 1.0
    },
    "twitter": {
        "followers_divisor": 20000,
        "default_weight": 1.0
    },
    "app_store": {
        "helpful_votes_divisor": 10,
        "default_weight": 1.0
    },
    "default_weight": 1.0
}

# Dashboard configuration
DASHBOARD_CONFIG = {
    "page_title": "Advanced Trade Insight Engine",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Report configuration
REPORT_CONFIG = {
    "title": "Weekly Customer Feedback Insight Report",
    "subtitle": "Coinbase Advanced Trading Platform",
    "top_items_count": 3,
    "font_size": {
        "title": 16,
        "subtitle": 14,
        "header": 12,
        "body": 10
    }
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": OUTPUT_DIR / "insight_engine.log"
}

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)