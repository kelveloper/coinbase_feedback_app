# Troubleshooting Guide

This guide provides solutions to common issues you may encounter when using the Advanced Trade Insight Engine.

## 🚨 Common Error Messages

### 1. Module Import Errors

#### Error: `ModuleNotFoundError: No module named 'pandas'`
**Cause**: Missing Python dependencies  
**Solution**:
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install pandas streamlit fpdf2 plotly pytest
```

#### Error: `ImportError: cannot import name 'main' from 'dashboard.dashboard'`
**Cause**: Python path issues or corrupted installation  
**Solution**:
```bash
# Verify Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Or run from project root
cd coinbase_feedback_app
python3 main.py
```

### 2. File and Data Errors

#### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'csv_mock_data/...'`
**Cause**: Missing CSV data files or incorrect paths  
**Solution**:
```bash
# Check if files exist
ls -la csv_mock_data/

# Use custom data directory
python3 main.py --data-dir /path/to/your/csv/files

# Verify file permissions
chmod 644 csv_mock_data/*.csv
```

#### Error: `pandas.errors.EmptyDataError: No columns to parse from file`
**Cause**: Empty or corrupted CSV files  
**Solution**:
```bash
# Check file contents
head -5 csv_mock_data/coinbase_advance_apple_reviews.csv

# Verify file size
ls -lh csv_mock_data/

# Re-download or restore backup files if corrupted
```

#### Error: `KeyError: 'feedback_text'` or similar column errors
**Cause**: Missing required columns in CSV files  
**Solution**:
1. Verify CSV headers match expected format:
   ```bash
   head -1 csv_mock_data/*.csv
   ```
2. Required columns by file type:
   - **Apple/Google Reviews**: `customer_id`, `username`, `review_text`, `sentiment`, `theme`
   - **Twitter**: `customer_id`, `handle`, `tweet_text`, `sentiment`, `theme`
   - **Sales Notes**: `customer_id`, `account_name`, `note_text`, `sentiment`, `theme`

### 3. PDF Generation Errors

#### Error: `Character "—" at index X is outside the range of characters supported`
**Cause**: Unicode characters in feedback text  
**Solution**: The system automatically sanitizes text, but if issues persist:
```bash
# Check for problematic characters
python3 -c "
import pandas as pd
df = pd.read_csv('csv_mock_data/coinbase_advance_apple_reviews.csv')
print('Checking for unicode characters...')
for col in ['review_text', 'theme']:
    if col in df.columns:
        for i, text in enumerate(df[col]):
            if any(ord(char) > 127 for char in str(text)):
                print(f'Unicode found in row {i}, column {col}: {text}')
"
```

#### Error: `PermissionError: [Errno 13] Permission denied: 'output/weekly_insight_report.pdf'`
**Cause**: File is open in another application or permission issues  
**Solution**:
```bash
# Close PDF viewer and retry
# Or change output directory
python3 main.py --output-dir /tmp/insight_reports

# Fix permissions
chmod 755 output/
```

### 4. Dashboard Errors

#### Error: `streamlit: command not found`
**Cause**: Streamlit not installed or not in PATH  
**Solution**:
```bash
# Install streamlit
pip install streamlit

# Or use python module syntax
python3 -m streamlit run src/dashboard/dashboard.py
```

#### Error: Dashboard shows "No data available"
**Cause**: Missing processed data file  
**Solution**:
```bash
# Run main pipeline first
python3 main.py

# Verify output file exists
ls -la output/processed_feedback_data.csv

# Check file contents
head -5 output/processed_feedback_data.csv
```

### 5. Memory and Performance Issues

#### Error: `MemoryError` or system becomes unresponsive
**Cause**: Insufficient RAM for large datasets  
**Solution**:
```bash
# Check available memory
free -h  # Linux/Mac
# Or Activity Monitor on Mac

# Process smaller datasets
# Split large CSV files into chunks
split -l 1000 large_file.csv chunk_

# Increase virtual memory if possible
```

#### Issue: Very slow processing
**Cause**: Large dataset or system resource constraints  
**Solution**:
```bash
# Monitor resource usage
top  # or htop on Linux

# Use verbose mode to identify bottlenecks
python3 main.py --verbose

# Consider processing subsets of data for testing
head -100 csv_mock_data/coinbase_advance_apple_reviews.csv > test_data.csv
```

## 🔧 System Diagnostics

### Quick Health Check

Run this comprehensive system check:

```bash
python3 -c "
import sys
import os
import pandas as pd

print('=== SYSTEM DIAGNOSTICS ===')
print(f'Python Version: {sys.version}')
print(f'Current Directory: {os.getcwd()}')
print(f'Python Path: {sys.path[:3]}...')

# Check dependencies
try:
    import pandas
    print(f'✅ Pandas: {pandas.__version__}')
except ImportError:
    print('❌ Pandas: Not installed')

try:
    import streamlit
    print(f'✅ Streamlit: {streamlit.__version__}')
except ImportError:
    print('❌ Streamlit: Not installed')

try:
    from fpdf import FPDF
    print('✅ FPDF2: Available')
except ImportError:
    print('❌ FPDF2: Not installed')

# Check data files
data_dir = 'csv_mock_data'
if os.path.exists(data_dir):
    files = os.listdir(data_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    print(f'✅ Data Directory: {len(csv_files)} CSV files found')
    for f in csv_files:
        size = os.path.getsize(os.path.join(data_dir, f))
        print(f'  - {f}: {size:,} bytes')
else:
    print('❌ Data Directory: csv_mock_data not found')

# Check output directory
output_dir = 'output'
if os.path.exists(output_dir):
    print(f'✅ Output Directory: Exists')
    if os.access(output_dir, os.W_OK):
        print('✅ Write Permissions: OK')
    else:
        print('❌ Write Permissions: Denied')
else:
    print('⚠️  Output Directory: Will be created')

print('=== END DIAGNOSTICS ===')
"
```

### Test Data Integrity

Verify your CSV data meets requirements:

```bash
python3 -c "
import pandas as pd
import os

def check_csv_file(filepath, required_cols):
    try:
        df = pd.read_csv(filepath)
        print(f'\\n📁 {os.path.basename(filepath)}:')
        print(f'  Rows: {len(df):,}')
        print(f'  Columns: {len(df.columns)}')
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f'  ❌ Missing columns: {missing_cols}')
        else:
            print(f'  ✅ All required columns present')
            
        # Check for empty values in critical columns
        for col in ['sentiment', 'theme']:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    print(f'  ⚠️  {col}: {empty_count} empty values')
                else:
                    print(f'  ✅ {col}: No empty values')
                    
    except Exception as e:
        print(f'❌ Error reading {filepath}: {e}')

# Check each file type
files_to_check = [
    ('csv_mock_data/coinbase_advance_apple_reviews.csv', ['customer_id', 'username', 'review_text', 'sentiment', 'theme']),
    ('csv_mock_data/coinbase_advanceGoogle_Play.csv', ['customer_id', 'username', 'review_text', 'sentiment', 'theme']),
    ('csv_mock_data/coinbase_advanced_twitter_mentions.csv', ['customer_id', 'handle', 'tweet_text', 'sentiment', 'theme']),
    ('csv_mock_data/coinbase_advance_internal_sales_notes.csv', ['customer_id', 'account_name', 'note_text', 'sentiment', 'theme'])
]

print('=== DATA INTEGRITY CHECK ===')
for filepath, required_cols in files_to_check:
    if os.path.exists(filepath):
        check_csv_file(filepath, required_cols)
    else:
        print(f'❌ File not found: {filepath}')
"
```

## 🐛 Debugging Steps

### 1. Enable Verbose Logging

Always start with verbose logging to get detailed information:

```bash
python3 main.py --verbose 2>&1 | tee debug.log
```

### 2. Test Individual Components

Test each system component separately:

```bash
# Test data loading only
python3 -c "
import sys
sys.path.insert(0, 'src')
from data_processing.data_loader import load_all_csv_files
result = load_all_csv_files('csv_mock_data')
print(f'Loaded {len(result)} data sources')
"

# Test NLP processing
python3 -c "
import sys, pandas as pd
sys.path.insert(0, 'src')
from analysis.nlp_models import get_sentiment
test_record = pd.Series({'sentiment': 'positive'})
result = get_sentiment(test_record)
print(f'NLP test result: {result}')
"

# Test impact scoring
python3 -c "
import sys, pandas as pd
sys.path.insert(0, 'src')
from analysis.scoring_engine import calculate_impact_score
test_record = pd.Series({'sentiment': 'negative', 'severity': 2.0, 'strategic_goal': 'Growth'})
result = calculate_impact_score(test_record, 1.0)
print(f'Impact score test: {result}')
"
```

### 3. Validate Configuration

Check your configuration settings:

```bash
python3 -c "
from config import CSV_FILE_PATHS, OUTPUT_PATHS, NLP_CONFIG
import os

print('=== CONFIGURATION CHECK ===')
print('CSV File Paths:')
for name, path in CSV_FILE_PATHS.items():
    exists = '✅' if os.path.exists(path) else '❌'
    print(f'  {exists} {name}: {path}')

print('\\nOutput Paths:')
for name, path in OUTPUT_PATHS.items():
    dir_exists = '✅' if os.path.exists(os.path.dirname(path)) else '❌'
    print(f'  {dir_exists} {name}: {path}')

print('\\nNLP Configuration:')
print(f'  Sentiment values: {NLP_CONFIG[\"sentiment_values\"]}')
print(f'  Strategic multipliers: {NLP_CONFIG[\"strategic_multipliers\"]}')
"
```

## 🔄 Recovery Procedures

### Reset to Clean State

If the system is in an inconsistent state:

```bash
# 1. Clean output directory
rm -rf output/*

# 2. Verify data integrity
python3 -c "
import pandas as pd
for file in ['csv_mock_data/coinbase_advance_apple_reviews.csv']:
    try:
        df = pd.read_csv(file)
        print(f'✅ {file}: {len(df)} records')
    except Exception as e:
        print(f'❌ {file}: {e}')
"

# 3. Run with minimal options
python3 main.py --verbose

# 4. Check outputs
ls -la output/
```

### Restore Default Configuration

If configuration is corrupted:

```bash
# Backup current config
cp config.py config.py.backup

# Reset to defaults (you may need to restore from version control)
# Or manually edit config.py to restore default values
```

### Emergency Data Recovery

If CSV files are corrupted:

```bash
# Check file encoding
file csv_mock_data/*.csv

# Try to recover readable portions
python3 -c "
import pandas as pd
import os

for file in os.listdir('csv_mock_data'):
    if file.endswith('.csv'):
        try:
            df = pd.read_csv(f'csv_mock_data/{file}', encoding='utf-8', error_bad_lines=False)
            print(f'✅ {file}: {len(df)} records recovered')
            # Save cleaned version
            df.to_csv(f'csv_mock_data/{file}.cleaned', index=False)
        except Exception as e:
            print(f'❌ {file}: {e}')
"
```

## 📞 Getting Help

### Before Seeking Help

1. **Run the system diagnostics** (see above)
2. **Check log files** in the `output/` directory
3. **Try the recovery procedures**
4. **Test with minimal data** (single CSV file with few records)

### Information to Provide

When reporting issues, include:

1. **Error message** (full traceback)
2. **System information**:
   ```bash
   python3 --version
   pip list | grep -E "(pandas|streamlit|fpdf)"
   uname -a  # Linux/Mac
   ```
3. **Data characteristics**:
   ```bash
   wc -l csv_mock_data/*.csv
   head -1 csv_mock_data/*.csv
   ```
4. **Log files** from the `output/` directory

### Self-Help Resources

1. **Test Suite**: Run `python3 -m pytest tests/ -v` to verify system integrity
2. **Configuration**: Review `config.py` for customization options
3. **Source Code**: Check `src/` modules for implementation details
4. **Sample Data**: Use provided `csv_mock_data/` for testing

---

**Remember**: Most issues are related to missing dependencies, incorrect file paths, or data format problems. The diagnostic scripts above will help identify the root cause quickly.