# Advanced Trade Insight Engine MVP

An automated customer feedback analysis system for Coinbase Advanced Trading platform that processes multi-channel feedback data and generates actionable business insights.

## 🎯 Overview

The Advanced Trade Insight Engine MVP analyzes customer feedback from four distinct sources:
- iOS App Store reviews
- Google Play Store reviews  
- Twitter/X mentions
- Internal sales notes

The system normalizes disparate data sources, applies strategic impact scoring, and delivers insights through automated PDF reports and an interactive dashboard.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CSV Sources   │───▶│  Data Pipeline   │───▶│    Outputs      │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • App Store     │    │ • Data Loading   │    │ • PDF Reports   │
│ • Google Play   │    │ • Normalization  │    │ • Dashboard     │
│ • Twitter/X     │    │ • NLP Analysis   │    │ • Insights      │
│ • Sales Notes   │    │ • Impact Scoring │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📊 Key Features

### Impact Scoring System
- **Source Weighting**: Different channels weighted by business value
- **Sentiment Analysis**: Negative feedback prioritized for action
- **Strategic Alignment**: Issues aligned with business goals get higher priority
- **Severity Integration**: Technical severity scores factored into impact

### Automated Reporting
- **Executive Summaries**: Key metrics and trends at a glance
- **Pain Point Analysis**: Top 3 critical issues requiring attention
- **Feature Praise**: Top 3 most appreciated features
- **Strategic Insights**: Goal-specific recommendations

### Interactive Dashboard
- **Real-time Filtering**: By source, theme, sentiment, time period
- **Visual Analytics**: Charts and graphs for trend analysis
- **Drill-down Capability**: Detailed feedback exploration
- **Export Functions**: Data export for further analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd advanced-trade-insights-mvp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify data files**
   Ensure these CSV files exist in `csv_mock_data/`:
   - `coinbase_advance_apple_reviews.csv`
   - `coinbase_advanceGoogle_Play.csv`
   - `coinbase_advance_internal_sales_notes.csv`
   - `coinbase_advanced_twitter_mentions.csv`

### Usage

#### Generate Weekly Report
```bash
python main.py
```
This will:
- Process all CSV data sources
- Calculate impact scores
- Generate PDF report in `output/weekly_insight_report.pdf`
- Prepare dashboard data

#### Launch Interactive Dashboard
```bash
streamlit run dashboard.py
```
Access the dashboard at `http://localhost:8501`

## 📁 Project Structure

```
advanced-trade-insights-mvp/
├── csv_mock_data/                    # Input data files
│   ├── coinbase_advance_apple_reviews.csv
│   ├── coinbase_advanceGoogle_Play.csv
│   ├── coinbase_advance_internal_sales_notes.csv
│   └── coinbase_advanced_twitter_mentions.csv
├── src/                              # Source code modules
│   ├── data_processing/
│   │   ├── data_loader.py           # CSV loading and validation
│   │   └── data_normalizer.py       # Column mapping and unification
│   ├── analysis/
│   │   ├── nlp_models.py            # Sentiment and theme extraction
│   │   ├── scoring_engine.py        # Source weight calculation
│   │   └── impact_calculator.py     # Impact score computation
│   ├── reporting/
│   │   ├── report_generator.py      # Report orchestration
│   │   ├── pdf_formatter.py         # PDF layout and styling
│   │   └── content_builder.py       # Data aggregation
│   ├── dashboard/
│   │   ├── dashboard.py             # Main Streamlit app
│   │   ├── components.py            # UI components
│   │   └── charts.py                # Visualization logic
│   └── utils/
│       ├── config.py                # Configuration settings
│       └── helpers.py               # Utility functions
├── output/                          # Generated reports
│   └── weekly_insight_report.pdf
├── tests/                           # Test suites
├── main.py                          # Main execution script
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 🔧 Configuration

### File Paths
Update `src/utils/config.py` to modify:
- Input data file locations
- Output directory paths
- Report formatting options

### Scoring Parameters
Adjust impact scoring in `src/analysis/scoring_engine.py`:
- Source weight multipliers
- Sentiment value mappings
- Strategic goal priorities

### Dashboard Settings
Customize dashboard appearance in `src/dashboard/dashboard.py`:
- Color schemes
- Chart types
- Filter options

## 📈 Impact Scoring Formula

```
Impact Score = (Sentiment Value × Severity) × Source Weight × Strategic Multiplier
```

### Components:
- **Sentiment Values**: Negative=1.5, Neutral=0.5, Positive=0.1
- **Source Weights**: 
  - Sales Notes: ARR Impact / $50K
  - Twitter: Followers / 20K
  - App Stores: Rating + (Helpful Votes / 10)
- **Strategic Multiplier**: Aligned Goals=2.0, Others=1.0

## 🧪 Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/
```

### Run Integration Tests
```bash
python -m pytest tests/integration/
```

### Run All Tests
```bash
python -m pytest
```

## 📊 Sample Output

### PDF Report Sections
1. **Executive Summary**: Key metrics and trends
2. **Top Pain Points**: Critical issues by impact score
3. **Praised Features**: Positive feedback highlights
4. **Strategic Insights**: Goal-specific recommendations
5. **Theme Analysis**: Feedback categorization and trends

### Dashboard Views
- **Overview**: KPIs and summary metrics
- **Theme Analysis**: Impact scores by category
- **Sentiment Trends**: Feedback sentiment over time
- **Source Breakdown**: Channel-specific insights
- **Detailed Data**: Filterable feedback table

## 🔍 Data Sources

### App Store Reviews
- **Metrics**: Rating, helpful votes, device info
- **Content**: Review text, user sentiment
- **Weighting**: Based on rating and community validation

### Twitter/X Mentions
- **Metrics**: Followers, engagement (likes, retweets)
- **Content**: Tweet text, user influence
- **Weighting**: Based on follower count and reach

### Internal Sales Notes
- **Metrics**: ARR impact, deal stage, account type
- **Content**: Sales feedback, feature requests
- **Weighting**: Based on revenue potential

## 🚨 Troubleshooting

### Common Issues

**Missing CSV Files**
```
Error: Could not find csv_mock_data/[filename].csv
Solution: Ensure all four CSV files are present in csv_mock_data/ directory
```

**PDF Generation Failed**
```
Error: Permission denied writing to output/
Solution: Check write permissions for output/ directory
```

**Dashboard Won't Load**
```
Error: Streamlit module not found
Solution: pip install streamlit
```

**Memory Issues with Large Datasets**
```
Error: MemoryError during processing
Solution: Implement chunked processing in data_loader.py
```

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export DEBUG=true
python main.py
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Maintain test coverage above 80%
- Keep modules under 400 lines
- Document all public functions

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the project documentation in `.kiro/specs/`
3. Open an issue with detailed error information

## 🗺️ Roadmap

### Phase 1 (Current MVP)
- ✅ Multi-source data ingestion
- ✅ Impact scoring system
- ✅ PDF report generation
- ✅ Interactive dashboard

### Phase 2 (Future Enhancements)
- [ ] Real-time data ingestion
- [ ] Advanced NLP models
- [ ] Machine learning predictions
- [ ] API endpoints
- [ ] Database integration
- [ ] Multi-language support

---

**Built with ❤️ for better customer insights**