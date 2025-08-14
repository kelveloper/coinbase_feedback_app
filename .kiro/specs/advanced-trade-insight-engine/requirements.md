# Requirements Document

## Introduction

The Advanced Trade Insight Engine MVP is an automated system that analyzes multi-channel customer feedback for the Coinbase Advanced Trading platform. The system ingests feedback from four distinct sources (iOS App Store reviews, Google Play Store reviews, Twitter mentions, and internal sales notes), normalizes the data, applies strategic impact scoring, and generates actionable insights through both PDF reports and an interactive dashboard.

The engine prioritizes feedback based on business impact, sentiment analysis, and strategic alignment to help product teams focus on the most critical customer pain points and opportunities.

## Requirements

### Requirement 1

**User Story:** As a product manager, I want to automatically ingest and normalize feedback from multiple channels, so that I can analyze all customer feedback in a unified format.

#### Acceptance Criteria

1. WHEN the system processes CSV files from four sources THEN it SHALL create a unified DataFrame with standardized column names
2. WHEN normalizing data THEN the system SHALL map review_text, tweet_text, and note_text to a common feedback_text column
3. WHEN normalizing data THEN the system SHALL map username and handle to a common author_handle column
4. WHEN processing each source THEN the system SHALL add a source_channel column identifying the origin
5. WHEN merging data THEN the system SHALL preserve source-specific metrics (rating, likes, followers, ARR_impact_estimate_USD)
6. IF any CSV file is missing or corrupted THEN the system SHALL log an error and continue processing available files

### Requirement 2

**User Story:** As a data analyst, I want NLP analysis functions that can extract sentiment, themes, and strategic goals from feedback, so that I can categorize and prioritize customer input effectively.

#### Acceptance Criteria

1. WHEN analyzing a feedback record THEN the system SHALL return sentiment classification (positive, negative, neutral)
2. WHEN analyzing a feedback record THEN the system SHALL return theme categorization from predefined categories
3. WHEN analyzing a feedback record THEN the system SHALL return strategic goal alignment (Growth, Trust&Safety, Onchain Adoption, CX Efficiency, Compliance)
4. WHEN processing feedback THEN the system SHALL use existing pre-enriched data from CSV columns for MVP implementation
5. IF sentiment, theme, or strategic_goal data is missing THEN the system SHALL return default values

### Requirement 3

**User Story:** As a business stakeholder, I want feedback to be weighted by source credibility and business impact, so that high-value customer input receives appropriate priority.

#### Acceptance Criteria

1. WHEN calculating source weight for Internal Sales Notes THEN the system SHALL use formula: ARR_impact_estimate_USD / 50000
2. WHEN calculating source weight for Twitter mentions THEN the system SHALL use formula: followers / 20000
3. WHEN calculating source weight for App Store reviews THEN the system SHALL use formula: rating + (helpful_votes / 10)
4. WHEN no specific weighting applies THEN the system SHALL return default weight of 1.0
5. IF required fields for weighting are missing THEN the system SHALL use default weight of 1.0

### Requirement 4

**User Story:** As a product manager, I want an impact scoring system that combines sentiment, severity, source weight, and strategic alignment, so that I can prioritize the most critical feedback items.

#### Acceptance Criteria

1. WHEN calculating impact score THEN the system SHALL assign sentiment values: negative = 1.5, neutral = 0.5, positive = 0.1
2. WHEN calculating impact score THEN the system SHALL apply strategic multiplier: aligned goals = 2.0, others = 1.0
3. WHEN calculating impact score THEN the system SHALL use formula: (sentiment_value * severity) * source_weight * strategic_multiplier
4. WHEN processing feedback THEN the system SHALL add impact_score as a new column to the DataFrame
5. IF any component of the impact score calculation is missing THEN the system SHALL use default values

### Requirement 5

**User Story:** As an executive, I want automated PDF reports that summarize key insights and trends, so that I can quickly understand customer feedback priorities without manual analysis.

#### Acceptance Criteria

1. WHEN generating a report THEN the system SHALL group feedback by theme and calculate total impact scores
2. WHEN generating a report THEN the system SHALL identify top 3 pain points by impact score
3. WHEN generating a report THEN the system SHALL identify top 3 praised features by positive sentiment and impact
4. WHEN generating a report THEN the system SHALL highlight key strategic goal insights
5. WHEN creating PDF output THEN the system SHALL save to /output/weekly_insight_report.pdf
6. WHEN PDF generation fails THEN the system SHALL log error details and continue execution

### Requirement 6

**User Story:** As a data analyst, I want an interactive dashboard to explore feedback data dynamically, so that I can drill down into specific themes, time periods, and customer segments.

#### Acceptance Criteria

1. WHEN loading the dashboard THEN the system SHALL display key metrics: Total Feedback Items, Average Sentiment, Top Theme by Impact
2. WHEN viewing the dashboard THEN the system SHALL show interactive charts of themes ranked by impact score
3. WHEN using the dashboard THEN the system SHALL provide sortable and filterable data tables
4. WHEN accessing the dashboard THEN the system SHALL load processed DataFrame with impact scores
5. IF the dashboard fails to load THEN the system SHALL display error message with troubleshooting guidance

### Requirement 7

**User Story:** As a system administrator, I want a main orchestrator that coordinates all components and provides clear execution status, so that I can run the complete analysis pipeline reliably.

#### Acceptance Criteria

1. WHEN executing the main script THEN the system SHALL load and normalize data from all four CSV sources
2. WHEN processing data THEN the system SHALL calculate source weights and impact scores for all records
3. WHEN generating outputs THEN the system SHALL create both PDF report and prepare dashboard data
4. WHEN execution completes THEN the system SHALL display confirmation message with output file location
5. IF any step fails THEN the system SHALL log detailed error information and attempt to continue with remaining steps
6. WHEN the system encounters missing input files THEN it SHALL provide clear error messages indicating which files are missing

### Requirement 8

**User Story:** As a developer, I want modular code architecture that separates concerns, so that individual components can be maintained, tested, and enhanced independently.

#### Acceptance Criteria

1. WHEN organizing code THEN the system SHALL separate data loading, NLP processing, scoring engine, reporting, and dashboard into distinct modules
2. WHEN implementing functions THEN each module SHALL have clear interfaces and minimal dependencies
3. WHEN adding new features THEN the system SHALL support extension without modifying existing core logic
4. WHEN testing components THEN each module SHALL be testable in isolation
5. IF module dependencies change THEN the system SHALL maintain backward compatibility where possible