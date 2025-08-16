# Advanced Trade Insight Engine - Testing Suite

This directory contains a comprehensive testing suite for the Advanced Trade Insight Engine, providing thorough coverage of all system components and functionality.

## Test Structure

### Unit Tests (`test_*` directories)

#### Data Processing Tests
- **`test_data_processing/test_data_loader.py`** - Tests CSV file loading, validation, and error handling
- **`test_data_processing/test_data_normalizer.py`** - Tests data normalization, column mapping, and unification

#### Analysis Tests  
- **`test_analysis/test_nlp_models.py`** - Tests sentiment, theme, and strategic goal extraction
- **`test_analysis/test_scoring_engine.py`** - Tests source weighting and impact score calculations

#### Reporting Tests
- **`test_reporting/test_content_builder.py`** - Tests report content aggregation and insight generation
- **`test_reporting/test_pdf_formatter.py`** - Tests PDF document creation and formatting
- **`test_reporting/test_report_generator.py`** - Tests end-to-end report generation workflow

#### Dashboard Tests
- **`test_dashboard/test_components.py`** - Tests KPI displays, filters, and UI components
- **`test_dashboard/test_charts.py`** - Tests chart creation and data visualization
- **`test_dashboard/test_dashboard.py`** - Tests complete dashboard integration

### Integration Tests

#### Main Pipeline Tests
- **`test_integration/test_main_pipeline.py`** - Tests complete end-to-end workflow integration
  - Environment validation
  - Data loading and normalization
  - NLP processing and scoring
  - Report generation
  - Dashboard data preparation
  - Progress tracking
  - Error handling

### End-to-End Tests
- **`test_e2e_workflow.py`** - Tests complete system workflow with real mock data
  - Complete data pipeline validation
  - NLP processing workflow
  - Impact scoring workflow
  - Report generation workflow
  - Data consistency validation

### Error Scenario Tests
- **`test_error_scenarios.py`** - Tests various error conditions and edge cases
  - Data loading errors (missing files, corrupted data)
  - Data processing errors (null values, invalid types)
  - Report generation errors (invalid paths, corrupted content)
  - Dashboard errors (empty data, corrupted data)
  - Memory and performance errors
  - System integration errors

### Performance Tests
- **`test_performance.py`** - Tests system performance characteristics
  - Large dataset processing performance
  - NLP processing performance
  - Impact scoring performance
  - Memory usage validation
  - Report generation performance
  - Concurrent processing simulation

### Basic Functionality Tests
- **`test_basic_functionality.py`** - Tests basic system functionality without external dependencies
  - Project structure validation
  - String operations and data validation
  - Basic calculation logic
  - Data structure operations

## Test Configuration

### Fixtures and Mock Data
- **`conftest.py`** - Shared test configuration and fixtures
  - Mock CSV data generation
  - Temporary directory management
  - Common test utilities
  - Progress tracking mocks

### Test Runners

#### Comprehensive Test Runner
- **`run_all_tests.py`** - Comprehensive test runner for all test suites
  ```bash
  python tests/run_all_tests.py [--verbose] [--coverage] [--performance]
  ```

#### Legacy Test Runner
- **`run_comprehensive_tests.py`** - Original comprehensive test runner with pytest support

## Running Tests

### Individual Test Categories

```bash
# Run unit tests only
python -m unittest discover tests/test_data_processing -v
python -m unittest discover tests/test_analysis -v
python -m unittest discover tests/test_reporting -v
python -m unittest discover tests/test_dashboard -v

# Run integration tests
python -m unittest tests.test_integration.test_main_pipeline -v

# Run end-to-end tests
python -m unittest tests.test_e2e_workflow -v

# Run error scenario tests
python -m unittest tests.test_error_scenarios -v

# Run performance tests
python -m unittest tests.test_performance -v

# Run basic functionality tests
python -m unittest tests.test_basic_functionality -v
```

### All Tests

```bash
# Run all tests with comprehensive runner
python tests/run_all_tests.py --verbose

# Run all tests with performance testing
python tests/run_all_tests.py --verbose --performance

# Run basic unittest discovery
python -m unittest discover tests -v
```

## Test Coverage

The testing suite provides comprehensive coverage of:

### Functional Coverage
- ✅ **Data Loading** - CSV file loading, validation, error handling
- ✅ **Data Normalization** - Column mapping, data unification, source identification
- ✅ **NLP Processing** - Sentiment extraction, theme categorization, strategic goal alignment
- ✅ **Impact Scoring** - Source weighting, impact calculation, ranking
- ✅ **Report Generation** - Content building, PDF creation, formatting
- ✅ **Dashboard Components** - KPI displays, charts, filters, data tables
- ✅ **Main Pipeline** - End-to-end workflow orchestration

### Error Handling Coverage
- ✅ **Missing Files** - Graceful handling of missing CSV files
- ✅ **Corrupted Data** - Processing of malformed or incomplete data
- ✅ **Invalid Input** - Handling of null values, wrong data types
- ✅ **System Errors** - Memory issues, disk space, permissions
- ✅ **Edge Cases** - Empty datasets, single records, extreme values

### Performance Coverage
- ✅ **Large Datasets** - Processing of 1000+ records
- ✅ **Memory Usage** - Efficient memory management
- ✅ **Processing Speed** - Reasonable execution times
- ✅ **Concurrent Access** - Simulated concurrent processing

## Test Quality Standards

### Code Coverage Target
- **Minimum**: 80% code coverage across all modules
- **Current**: Comprehensive test coverage of all major functions and classes
- **Validation**: Tests cover both happy path and error scenarios

### Test Reliability
- **Deterministic**: All tests produce consistent results
- **Isolated**: Tests don't depend on external resources or state
- **Fast**: Unit tests complete in seconds, integration tests in minutes
- **Maintainable**: Clear test structure and documentation

### Error Scenarios
- **Graceful Degradation**: System continues operation when possible
- **Clear Error Messages**: Meaningful error reporting for troubleshooting
- **Recovery Mechanisms**: Automatic retry and fallback strategies
- **Data Integrity**: No data corruption during error conditions

## Dependencies

### Required for Testing
- Python 3.8+
- unittest (built-in)
- tempfile (built-in)
- pathlib (built-in)

### Optional for Enhanced Testing
- pandas (for data processing tests)
- streamlit (for dashboard tests)
- fpdf2 (for PDF generation tests)
- plotly (for chart tests)

### Mock Strategy
- Tests are designed to work with or without external dependencies
- Mock objects and data are used when dependencies are unavailable
- Tests gracefully skip when required modules are not installed

## Continuous Integration

### Test Automation
The testing suite is designed for automated execution in CI/CD pipelines:

```yaml
# Example CI configuration
test:
  script:
    - python tests/run_all_tests.py --verbose
    - python -m unittest tests.test_basic_functionality -v
  coverage: 80%
```

### Quality Gates
- All tests must pass before deployment
- Minimum 80% code coverage required
- Performance tests must complete within time limits
- Error scenario tests must demonstrate graceful failure handling

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# If pandas/streamlit not available
python -m unittest tests.test_basic_functionality -v
```

#### Permission Errors
```bash
# Ensure write permissions for temporary directories
chmod 755 /tmp
```

#### Memory Issues
```bash
# Run tests with smaller datasets
python tests/run_all_tests.py --verbose
```

### Test Debugging
- Use `--verbose` flag for detailed test output
- Check individual test files for specific functionality
- Review mock data in `conftest.py` for test data issues
- Examine temporary directories for file-related test failures

## Contributing

### Adding New Tests
1. Follow existing test structure and naming conventions
2. Include both positive and negative test cases
3. Add appropriate mock data and fixtures
4. Update this README with new test descriptions
5. Ensure tests work with and without external dependencies

### Test Guidelines
- Write clear, descriptive test names
- Include docstrings explaining test purpose
- Use appropriate assertions for validation
- Handle expected exceptions properly
- Clean up resources in tearDown methods

## Requirements Traceability

This testing suite fulfills the following requirements:

- **8.1** - Unit test coverage for all modules ✅
- **8.2** - Integration and end-to-end tests ✅  
- **8.3** - Error scenario testing ✅
- **8.4** - Performance and validation tests ✅

The comprehensive testing suite ensures system reliability, maintainability, and quality standards for the Advanced Trade Insight Engine.