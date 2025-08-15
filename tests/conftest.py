"""
Shared test configuration and fixtures for the Advanced Trade Insight Engine.

This module provides common test setup, mock data, and utility functions
used across all test modules to ensure consistency and reduce duplication.

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import pytest
import pandas as pd
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory with mock CSV data for testing."""
    test_dir = tempfile.mkdtemp()
    data_dir = os.path.join(test_dir, 'csv_mock_data')
    os.makedirs(data_dir)
    
    # Create comprehensive mock data for all four CSV files
    create_mock_csv_files(data_dir)
    
    yield data_dir
    
    # Cleanup
    shutil.rmtree(test_dir)


@pytest.fixture(scope="session")
def test_output_dir():
    """Create a temporary output directory for test results."""
    output_dir = tempfile.mkdtemp()
    yield output_dir
    shutil.rmtree(output_dir)


@pytest.fixture(scope="function")
def sample_ios_data():
    """Sample iOS App Store review data for testing."""
    return pd.DataFrame({
        'customer_id': ['IOS-001', 'IOS-002', 'IOS-003', 'IOS-004', 'IOS-005'],
        'source': ['iOS App Store'] * 5,
        'username': [f'user{i}' for i in range(1, 6)],
        'timestamp': [
            '2024-01-01 10:00:00', '2024-01-02 11:00:00', '2024-01-03 12:00:00',
            '2024-01-04 13:00:00', '2024-01-05 14:00:00'
        ],
        'rating': [4, 2, 5, 3, 1],
        'sentiment': ['positive', 'negative', 'positive', 'neutral', 'negative'],
        'review_text': [
            'Great app! Very fast and reliable.',
            'Needs improvement. Too many bugs.',
            'Love it! Best trading app ever.',
            'It\'s okay, could be better.',
            'Terrible experience. App crashes constantly.'
        ],
        'theme': [
            'Performance', 'Trading/Execution & Fees', 'General Feedback',
            'Support Experience', 'Performance'
        ],
        'severity': [1.0, 2.0, 0.5, 1.5, 2.5],
        'strategic_goal': ['Growth', 'CX Efficiency', 'Growth', 'Trust&Safety', 'CX Efficiency'],
        'helpful_votes': [5, 10, 15, 7, 12]
    })


@pytest.fixture(scope="function")
def sample_android_data():
    """Sample Google Play Store review data for testing."""
    return pd.DataFrame({
        'customer_id': ['AND-001', 'AND-002', 'AND-003', 'AND-004', 'AND-005'],
        'source': ['Google Play Store'] * 5,
        'username': [f'android_user{i}' for i in range(1, 6)],
        'handle': [f'@android{i}' for i in range(1, 6)],
        'timestamp': [
            '2024-01-06 15:00:00', '2024-01-07 16:00:00', '2024-01-08 17:00:00',
            '2024-01-09 18:00:00', '2024-01-10 19:00:00'
        ],
        'rating': [5, 3, 4, 2, 5],
        'sentiment': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'review_text': [
            'Excellent app! Smooth interface.',
            'Decent app, some issues.',
            'Very good trading platform.',
            'Frustrating to use.',
            'Outstanding performance!'
        ],
        'theme': [
            'General Feedback', 'Support Experience', 'Trading/Execution & Fees',
            'Performance', 'General Feedback'
        ],
        'severity': [0.5, 1.5, 1.0, 2.0, 0.5],
        'strategic_goal': ['Growth', 'Trust&Safety', 'Growth', 'CX Efficiency', 'Growth'],
        'helpful_votes': [8, 4, 9, 6, 11]
    })


@pytest.fixture(scope="function")
def sample_twitter_data():
    """Sample Twitter mention data for testing."""
    return pd.DataFrame({
        'customer_id': ['TW-001', 'TW-002', 'TW-003', 'TW-004', 'TW-005'],
        'source': ['Twitter (X)'] * 5,
        'handle': [f'@trader{i}' for i in range(1, 6)],
        'followers': [148860, 106574, 89234, 156789, 234567],
        'timestamp': [
            '2024-01-11 20:00:00', '2024-01-12 21:00:00', '2024-01-13 22:00:00',
            '2024-01-14 23:00:00', '2024-01-15 00:00:00'
        ],
        'sentiment': ['positive', 'positive', 'neutral', 'negative', 'positive'],
        'tweet_text': [
            'Great trading experience with @Coinbase!',
            'Love the new features!',
            'Interesting platform, still exploring.',
            'Having issues with withdrawals.',
            'Best crypto exchange hands down!'
        ],
        'theme': [
            'Trading/Execution & Fees', 'General Feedback', 'General Feedback',
            'Support Experience', 'General Feedback'
        ],
        'severity': [1.0, 0.5, 1.5, 2.0, 0.5],
        'strategic_goal': ['Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth']
    })


@pytest.fixture(scope="function")
def sample_sales_data():
    """Sample internal sales notes data for testing."""
    return pd.DataFrame({
        'customer_id': ['SALES-001', 'SALES-002', 'SALES-003', 'SALES-004', 'SALES-005'],
        'source': ['Internal Sales Notes'] * 5,
        'account_name': [
            'Enterprise Corp', 'Startup Inc', 'MidMarket LLC', 'Fortune 500 Co', 'Tech Startup'
        ],
        'timestamp': [
            '2024-01-16 01:00:00', '2024-01-17 02:00:00', '2024-01-18 03:00:00',
            '2024-01-19 04:00:00', '2024-01-20 05:00:00'
        ],
        'sentiment': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'note_text': [
            'Customer very satisfied with platform performance.',
            'Customer has some concerns about pricing.',
            'Excellent feedback on new features.',
            'Customer experiencing technical difficulties.',
            'Great partnership opportunity identified.'
        ],
        'theme': [
            'Performance', 'Trading/Execution & Fees', 'General Feedback',
            'Support Experience', 'General Feedback'
        ],
        'severity': [1.0, 1.5, 0.5, 2.0, 0.5],
        'strategic_goal': ['Growth', 'CX Efficiency', 'Growth', 'Trust&Safety', 'Growth'],
        'ARR_impact': [75000, 25000, 50000, 100000, 15000]
    })


@pytest.fixture(scope="function")
def large_dataset():
    """Create a large dataset for performance testing."""
    # Generate 1000 rows of synthetic data
    data = []
    for i in range(1000):
        data.append({
            'customer_id': f'PERF-{i:03d}',
            'source': 'Performance Test',
            'username': f'perf_user_{i}',
            'timestamp': f'2024-01-{i % 30 + 1:02d} 12:00:00',
            'rating': (i % 5) + 1,
            'sentiment': ['positive', 'neutral', 'negative'][i % 3],
            'review_text': f'Performance test review {i}',
            'theme': ['Performance', 'Support', 'Trading'][i % 3],
            'severity': (i % 3) + 0.5,
            'strategic_goal': ['Growth', 'CX Efficiency', 'Trust&Safety'][i % 3],
            'helpful_votes': (i % 20) + 1
        })
    return pd.DataFrame(data)


def create_mock_csv_files(data_dir):
    """Create mock CSV files with comprehensive test data."""
    # iOS App Store reviews
    ios_data = pd.DataFrame({
        'customer_id': ['IOS-001', 'IOS-002', 'IOS-003', 'IOS-004', 'IOS-005'],
        'source': ['iOS App Store'] * 5,
        'username': [f'user{i}' for i in range(1, 6)],
        'timestamp': [
            '2024-01-01 10:00:00', '2024-01-02 11:00:00', '2024-01-03 12:00:00',
            '2024-01-04 13:00:00', '2024-01-05 14:00:00'
        ],
        'rating': [4, 2, 5, 3, 1],
        'sentiment': ['positive', 'negative', 'positive', 'neutral', 'negative'],
        'review_text': [
            'Great app! Very fast and reliable.',
            'Needs improvement. Too many bugs.',
            'Love it! Best trading app ever.',
            'It\'s okay, could be better.',
            'Terrible experience. App crashes constantly.'
        ],
        'theme': [
            'Performance', 'Trading/Execution & Fees', 'General Feedback',
            'Support Experience', 'Performance'
        ],
        'severity': [1.0, 2.0, 0.5, 1.5, 2.5],
        'strategic_goal': ['Growth', 'CX Efficiency', 'Growth', 'Trust&Safety', 'CX Efficiency'],
        'helpful_votes': [5, 10, 15, 7, 12]
    })
    ios_data.to_csv(os.path.join(data_dir, 'coinbase_advance_apple_reviews.csv'), index=False)
    
    # Google Play Store reviews
    android_data = pd.DataFrame({
        'customer_id': ['AND-001', 'AND-002', 'AND-003', 'AND-004', 'AND-005'],
        'source': ['Google Play Store'] * 5,
        'username': [f'android_user{i}' for i in range(1, 6)],
        'timestamp': [
            '2024-01-06 15:00:00', '2024-01-07 16:00:00', '2024-01-08 17:00:00',
            '2024-01-09 18:00:00', '2024-01-10 19:00:00'
        ],
        'rating': [5, 3, 4, 2, 5],
        'sentiment': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'review_text': [
            'Excellent app! Smooth interface.',
            'Decent app, some issues.',
            'Very good trading platform.',
            'Frustrating to use.',
            'Outstanding performance!'
        ],
        'theme': [
            'General Feedback', 'Support Experience', 'Trading/Execution & Fees',
            'Performance', 'General Feedback'
        ],
        'severity': [0.5, 1.5, 1.0, 2.0, 0.5],
        'strategic_goal': ['Growth', 'Trust&Safety', 'Growth', 'CX Efficiency', 'Growth'],
        'helpful_votes': [8, 4, 9, 6, 11]
    })
    android_data.to_csv(os.path.join(data_dir, 'coinbase_advanceGoogle_Play.csv'), index=False)
    
    # Twitter mentions
    twitter_data = pd.DataFrame({
        'customer_id': ['TW-001', 'TW-002', 'TW-003', 'TW-004', 'TW-005'],
        'source': ['Twitter (X)'] * 5,
        'handle': [f'@trader{i}' for i in range(1, 6)],
        'followers': [148860, 106574, 89234, 156789, 234567],
        'timestamp': [
            '2024-01-11 20:00:00', '2024-01-12 21:00:00', '2024-01-13 22:00:00',
            '2024-01-14 23:00:00', '2024-01-15 00:00:00'
        ],
        'sentiment': ['positive', 'positive', 'neutral', 'negative', 'positive'],
        'tweet_text': [
            'Great trading experience with @Coinbase!',
            'Love the new features!',
            'Interesting platform, still exploring.',
            'Having issues with withdrawals.',
            'Best crypto exchange hands down!'
        ],
        'theme': [
            'Trading/Execution & Fees', 'General Feedback', 'General Feedback',
            'Support Experience', 'General Feedback'
        ],
        'severity': [1.0, 0.5, 1.5, 2.0, 0.5],
        'strategic_goal': ['Growth', 'Growth', 'Trust&Safety', 'CX Efficiency', 'Growth']
    })
    twitter_data.to_csv(os.path.join(data_dir, 'coinbase_advanced_twitter_mentions.csv'), index=False)
    
    # Internal sales notes
    sales_data = pd.DataFrame({
        'customer_id': ['SALES-001', 'SALES-002', 'SALES-003', 'SALES-004', 'SALES-005'],
        'source': ['Internal Sales Notes'] * 5,
        'account_name': [
            'Enterprise Corp', 'Startup Inc', 'MidMarket LLC', 'Fortune 500 Co', 'Tech Startup'
        ],
        'timestamp': [
            '2024-01-16 01:00:00', '2024-01-17 02:00:00', '2024-01-18 03:00:00',
            '2024-01-19 04:00:00', '2024-01-20 05:00:00'
        ],
        'sentiment': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'note_text': [
            'Customer very satisfied with platform performance.',
            'Customer has some concerns about pricing.',
            'Excellent feedback on new features.',
            'Customer experiencing technical difficulties.',
            'Great partnership opportunity identified.'
        ],
        'theme': [
            'Performance', 'Trading/Execution & Fees', 'General Feedback',
            'Support Experience', 'General Feedback'
        ],
        'severity': [1.0, 1.5, 0.5, 2.0, 0.5],
        'strategic_goal': ['Growth', 'CX Efficiency', 'Growth', 'Trust&Safety', 'Growth'],
        'ARR_impact': [75000, 25000, 50000, 100000, 15000]
    })
    sales_data.to_csv(os.path.join(data_dir, 'coinbase_advance_internal_sales_notes.csv'), index=False)


@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for testing logging functionality."""
    return MagicMock()


@pytest.fixture(scope="function")
def mock_progress_tracker():
    """Mock progress tracker for testing progress functionality."""
    tracker = MagicMock()
    tracker.update_progress = MagicMock()
    tracker.log_status = MagicMock()
    tracker.log_error = MagicMock()
    return tracker
