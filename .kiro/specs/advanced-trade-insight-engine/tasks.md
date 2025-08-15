# Implementation Plan

- [x] 1. Set up project structure and core configuration

  - Create directory structure with src/, output/, and tests/ folders (data exists in csv_mock_data/)
  - Create **init**.py files for all Python packages
  - Set up requirements.txt with dependencies: pandas, streamlit, fpdf2
  - Create config.py with file paths pointing to csv_mock_data/ folder and configuration settings
  - _Requirements: 8.1, 8.2_

- [x] 2. Implement data processing foundation
- [x] 2.1 Create data loading module

  - Write CSV file loading functions targeting csv_mock_data/ folder files
  - Implement file validation for the four specific CSV files: coinbase_advance_apple_reviews.csv, coinbase_advanceGoogle_Play.csv, coinbase_advance_internal_sales_notes.csv, coinbase_advanced_twitter_mentions.csv
  - Add error handling for missing/corrupted files in csv_mock_data/ directory
  - Create unit tests for data loading using the existing mock CSV files
  - _Requirements: 1.1, 1.6_

- [x] 2.2 Build data normalization module

  - Implement column mapping functions (review_text/tweet_text/note_text → feedback_text)
  - Create author handle unification (username/handle/account_name → author_handle)
  - Add source_channel column identification during processing
  - Write unit tests for column mapping and data unification
  - _Requirements: 1.2, 1.3, 1.4, 1.5_

- [x] 3. Develop NLP analysis components
- [x] 3.1 Create NLP models module

  - Implement get_sentiment() function using pre-enriched CSV data
  - Implement get_theme() function for feedback categorization
  - Implement get_strategic_goal() function for business alignment
  - Add default value handling for missing NLP data
  - Write unit tests for all NLP extraction functions
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Build impact scoring system
- [x] 4.1 Implement source weighting engine

  - Create calculate_source_weight() function with channel-specific logic
  - Implement Internal Sales Notes weighting (ARR_impact / 50000)
  - Implement Twitter weighting (followers / 20000)
  - Implement App Store weighting (rating + helpful_votes/10)
  - Add default weighting fallback and error handling
  - Write unit tests for all weighting calculations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 4.2 Create impact score calculator

  - Implement sentiment value mapping (negative=1.5, neutral=0.5, positive=0.1)
  - Create strategic multiplier logic (aligned=2.0, others=1.0)
  - Build impact score formula: (sentiment × severity) × source_weight × strategic_multiplier
  - Add DataFrame column integration for calculated scores
  - Write unit tests for impact score calculations and edge cases
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 5. Develop reporting system
- [x] 5.1 Create content builder module

  - Implement theme grouping and impact score aggregation
  - Create top pain points identification (highest negative impact)
  - Build praised features detection (positive sentiment + high impact)
  - Develop strategic goal insights extraction
  - Write unit tests for content aggregation logic
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5.2 Build PDF formatter module

  - Implement PDF document structure with headers and sections
  - Create formatting functions for executive summary, pain points, and insights
  - Add professional styling and layout for business reports
  - Implement error handling for PDF generation failures
  - Write unit tests for PDF creation and content formatting
  - _Requirements: 5.5, 5.6_

- [x] 5.3 Integrate report generator orchestration

  - Create main generate_report_content() function coordinating content building
  - Implement create_pdf_report() function integrating PDF formatting
  - Add file output handling and path management
  - Write integration tests for end-to-end report generation
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Build interactive dashboard system
- [x] 6.1 Create dashboard components module

  - Implement KPI header component (total items, avg sentiment, top theme)
  - Create filterable data table component with sorting capabilities
  - Build filter controls for source channel, theme, and sentiment
  - Write unit tests for individual dashboard components
  - _Requirements: 6.1, 6.3, 6.5_

- [x] 6.2 Develop chart visualization module

  - Implement theme impact ranking bar charts
  - Create sentiment distribution visualizations
  - Build time-based trend analysis charts
  - Add interactive chart features and hover details
  - Write unit tests for chart generation and data binding
  - _Requirements: 6.2_

- [x] 6.3 Integrate main dashboard application

  - Create Streamlit main dashboard app with page layout
  - Integrate KPI components, charts, and data tables
  - Implement data loading and processing for dashboard display
  - Add error handling and user-friendly error messages
  - Write integration tests for complete dashboard functionality
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 7. Create main orchestrator and integration
- [ ] 7.1 Build main execution pipeline

  - Create main.py with complete workflow orchestration
  - Configure file paths to point to csv_mock_data/ directory for the four CSV files
  - Integrate data loading, NLP processing, and scoring pipeline using existing mock data
  - Add report generation and dashboard data preparation
  - Implement comprehensive error handling and logging
  - _Requirements: 7.1, 7.2, 7.3, 7.6_

- [ ] 7.2 Add execution status and monitoring

  - Implement progress tracking and status messages
  - Create confirmation messages with output file locations
  - Add detailed error logging with troubleshooting guidance
  - Build graceful failure handling to continue processing when possible
  - Write integration tests for complete end-to-end pipeline
  - _Requirements: 7.4, 7.5, 7.6_

- [ ] 8. Implement comprehensive testing suite
- [ ] 8.1 Create unit test coverage

  - Write unit tests for all data processing functions
  - Create unit tests for NLP models and scoring calculations
  - Build unit tests for report generation and PDF creation
  - Implement unit tests for dashboard components and charts
  - Achieve minimum 80% code coverage across all modules
  - _Requirements: 8.4_

- [ ] 8.2 Build integration and end-to-end tests

  - Create integration tests for complete data pipeline
  - Build end-to-end tests using provided mock CSV data
  - Implement error scenario testing (missing files, corrupted data)
  - Create performance tests for large dataset processing
  - Write validation tests for output quality and format correctness
  - _Requirements: 8.1, 8.3, 8.4_

- [ ] 9. Final integration and validation
- [ ] 9.1 Complete system integration testing

  - Run full pipeline with all four CSV files from csv_mock_data/ folder
  - Validate PDF report generation using real data from coinbase_advance_apple_reviews.csv, coinbase_advanceGoogle_Play.csv, coinbase_advance_internal_sales_notes.csv, and coinbase_advanced_twitter_mentions.csv
  - Test dashboard functionality with complete mock dataset
  - Verify all calculated impact scores and rankings are accurate using the existing pre-enriched data
  - Confirm error handling works correctly for various failure scenarios
  - _Requirements: 1.1, 4.4, 5.5, 6.4, 7.4_

- [ ] 9.2 Documentation and deployment preparation
  - Create README.md with installation and usage instructions
  - Document configuration options and customization points
  - Add troubleshooting guide for common issues
  - Create example usage scripts and sample outputs
  - Prepare project for handoff with clear execution instructions
  - _Requirements: 7.4, 7.5_
