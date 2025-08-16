# Advanced Trade Insight Engine MVP

An automated system that analyzes multi-channel customer feedback for the Coinbase Advanced Trading platform. The system ingests feedback from four distinct sources, normalizes the data, applies strategic impact scoring, and generates actionable insights through both PDF reports and an interactive dashboard.

## 🚀 Features

- **Multi-Channel Data Ingestion**: Processes feedback from iOS App Store, Google Play Store, Twitter mentions, and internal sales notes
- **Intelligent Impact Scoring**: Combines sentiment analysis, source credibility, and strategic alignment for prioritization
- **Automated PDF Reports**: Generates professional business reports with key insights and recommendations
- **Interactive Dashboard**: Streamlit-based web interface for dynamic data exploration
- **Comprehensive Testing**: Full test suite with unit, integration, and end-to-end tests

## 📊 System Overview

The engine processes customer feedback through a modular pipeline:

1. **Data Loading & Normalization**: Unifies disparate CSV sources into standardized format
2. **NLP Processing**: Extracts sentiment, themes, and strategic goal alignment
3. **Impact Scoring**: Calculates business impact based on multiple factors
4. **Report Generation**: Creates PDF reports and prepares dashboard data
5. **Interactive Visualization**: Provides web-based exploration interface

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd coinbase_feedback_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python3 main.py --help
   ```

### Dependencies

The system requires the following Python packages:
- `pandas>=1.5.0` - Data manipulation and analysis
- `streamlit>=1.28.0` - Interactive dashboard framework
- `fpdf2>=2.7.0` - PDF report generation
- `plotly>=5.15.0` - Interactive charts and visualizations
- `pytest>=7.0.0` - Testing framework

## 📁 Project Structure

```
coinbase_feedback_app/
├── main.py                     # Main execution pipeline
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── csv_mock_data/             # Sample data files
│   ├── coinbase_advance_apple_reviews.csv
│   ├── coinbase_advanceGoogle_Play.csv
│   ├── coinbase_advance_internal_sales_notes.csv
│   └── coinbase_advanced_twitter_mentions.csv
├── src/                       # Source code modules
│   ├── data_processing/       # Data loading and normalization
│   ├── analysis/             # NLP models and scoring engine
│   ├── reporting/            # PDF report generation
│   └── dashboard/            # Interactive web interface
├── tests/                    # Comprehensive test suite
├── output/                   # Generated reports and processed data
└── README.md                 # This documentation
```

## 🚀 Usage

### Basic Execution

Run the complete analysis pipeline with default settings:

```bash
python3 main.py
```

### Advanced Options

```bash
# Use custom data directory
python3 main.py --data-dir /path/to/csv/files

# Specify output directory
python3 main.py --output-dir /path/to/output

# Enable verbose logging
python3 main.py --verbose

# Show help
python3 main.py --help
```

### Expected Output

The system generates the following outputs in the `output/` directory:

1. **PDF Report**: `weekly_insight_report.pdf` - Executive summary with key insights
2. **Dashboard Data**: `processed_feedback_data.csv` - Processed data for interactive exploration
3. **Log Files**: Detailed execution logs with timestamps

### Launch Interactive Dashboard

After running the main pipeline, launch the web dashboard:

```bash
streamlit run src/dashboard/dashboard.py
```

The dashboard will be available at `http://localhost:8501` and provides:
- Key performance indicators (KPIs)
- Interactive charts and visualizations
- Filterable data tables
- Drill-down capabilities

## 📊 Data Requirements

### Input Data Format

The system expects four CSV files with specific column structures:

#### iOS App Store Reviews (`coinbase_advance_apple_reviews.csv`)
- `customer_id`, `username`, `rating`, `review_text`, `sentiment`, `theme`, `strategic_goal`, `severity`, `helpful_votes`

#### Google Play Store Reviews (`coinbase_advanceGoogle_Play.csv`)
- `customer_id`, `username`, `rating`, `review_text`, `sentiment`, `theme`, `strategic_goal`, `severity`, `helpful_votes`

#### Twitter Mentions (`coinbase_advanced_twitter_mentions.csv`)
- `customer_id`, `handle`, `followers`, `tweet_text`, `sentiment`, `theme`, `strategic_goal`, `severity`

#### Internal Sales Notes (`coinbase_advance_internal_sales_notes.csv`)
- `customer_id`, `account_name`, `note_text`, `sentiment`, `theme`, `strategic_goal`, `severity`, `ARR_impact_estimate_USD`

### Data Quality Requirements

- All CSV files must have headers matching the expected column names
- Required fields: `customer_id`, `sentiment`, `theme`, `strategic_goal`
- Numeric fields should be properly formatted (no currency symbols, etc.)
- Text fields should be UTF-8 encoded

## ⚙️ Configuration

### Basic Configuration

Edit `config.py` to customize:

```python
# File paths
CSV_FILE_PATHS = {
    "apple_reviews": "path/to/apple_reviews.csv",
    "google_reviews": "path/to/google_reviews.csv",
    # ... other paths
}

# Impact scoring parameters
NLP_CONFIG = {
    "sentiment_values": {
        "negative": 1.5,
        "neutral": 0.5,
        "positive": 0.1
    }
}
```

### Advanced Configuration

#### Source Weighting

Customize how different feedback sources are weighted:

```python
SOURCE_WEIGHT_CONFIG = {
    "internal_sales": {"arr_divisor": 50000},
    "twitter": {"followers_divisor": 20000},
    "app_store": {"helpful_votes_divisor": 10}
}
```

#### Dashboard Settings

Modify dashboard appearance and behavior:

```python
DASHBOARD_CONFIG = {
    "page_title": "Your Custom Title",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
```

## 🧪 Testing

### Run All Tests

```bash
# Run complete test suite
python3 -m pytest tests/ -v

# Run with coverage report
python3 -m pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
python3 -m pytest tests/test_analysis/ tests/test_data_processing/ -v

# Integration tests
python3 -m pytest tests/test_integration/ -v

# End-to-end workflow test
python3 -m pytest tests/test_e2e_workflow.py -v
```

### Test Data

The test suite uses the provided mock data in `csv_mock_data/` directory. Tests verify:
- Data loading and normalization accuracy
- Impact scoring calculations
- Report generation functionality
- Dashboard data preparation
- Error handling scenarios

## 🔧 Troubleshooting

### Common Issues

#### 1. Missing Dependencies
```bash
# Error: ModuleNotFoundError
# Solution: Install requirements
pip install -r requirements.txt
```

#### 2. CSV File Not Found
```bash
# Error: FileNotFoundError
# Solution: Verify file paths in config.py or use --data-dir flag
python3 main.py --data-dir /correct/path/to/csv/files
```

#### 3. PDF Generation Fails
```bash
# Error: Unicode character issues
# Solution: The system automatically sanitizes text, but ensure input data is UTF-8 encoded
```

#### 4. Dashboard Won't Start
```bash
# Error: Streamlit import issues
# Solution: Ensure streamlit is installed and try:
pip install streamlit --upgrade
streamlit run src/dashboard/dashboard.py
```

### Performance Issues

#### Large Dataset Processing
- The system processes data in memory; for very large datasets (>100k records), consider:
  - Increasing available RAM
  - Processing data in chunks
  - Using more powerful hardware

#### Slow PDF Generation
- PDF generation time scales with data size and complexity
- For faster processing, consider reducing the number of feedback examples included in reports

### Logging and Debugging

Enable verbose logging for detailed troubleshooting:

```bash
python3 main.py --verbose
```

Log files are saved in the `output/` directory with timestamps for easy identification.

## 📈 Performance Metrics

### Typical Processing Times

Based on the provided mock dataset (200 records):

- **Data Loading**: ~0.3 seconds
- **NLP Processing**: ~0.2 seconds  
- **Impact Scoring**: ~0.1 seconds
- **Report Generation**: ~0.5 seconds
- **Dashboard Preparation**: ~0.1 seconds
- **Total Pipeline**: ~1.2 seconds

### Scalability Guidelines

| Dataset Size | Expected Processing Time | Memory Usage |
|-------------|-------------------------|--------------|
| 1K records  | ~5 seconds             | ~50 MB       |
| 10K records | ~30 seconds            | ~200 MB      |
| 100K records| ~5 minutes             | ~1 GB        |

## 🤝 Contributing

### Development Setup

1. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest-cov pytest-html
   ```

2. **Run tests before committing**
   ```bash
   python3 -m pytest tests/ --cov=src
   ```

3. **Follow code style guidelines**
   - Use descriptive variable names
   - Add docstrings to functions
   - Maintain test coverage above 80%

### Adding New Features

1. **Data Sources**: Add new CSV loaders in `src/data_processing/`
2. **Analysis Methods**: Extend NLP models in `src/analysis/`
3. **Visualizations**: Add charts in `src/dashboard/charts.py`
4. **Report Sections**: Extend PDF formatter in `src/reporting/`

## 📄 License

This project is developed for Coinbase Advanced Trading platform analysis. Please ensure compliance with your organization's data handling and privacy policies when processing customer feedback.

## 🆘 Support

For technical issues or questions:

1. **Check the troubleshooting section** above
2. **Review log files** in the `output/` directory
3. **Run tests** to verify system integrity
4. **Check configuration** in `config.py`

### System Requirements Verification

Run this command to verify your system meets all requirements:

```bash
python3 -c "
import sys
print(f'Python version: {sys.version}')
try:
    import pandas, streamlit, fpdf
    print('✅ All required packages available')
except ImportError as e:
    print(f'❌ Missing package: {e}')
"
```

---

**Last Updated**: August 2025  
**Version**: 1.0.0  
**Compatibility**: Python 3.8+