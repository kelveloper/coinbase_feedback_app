# Configuration Guide

This guide explains how to configure the Advanced Trade Insight Engine for different environments and use cases.

## 📁 Configuration Files

### Primary Configuration (`config.py`)

The main configuration file contains all system settings:

```python
# File paths
CSV_FILE_PATHS = {
    "apple_reviews": DATA_DIR / "coinbase_advance_apple_reviews.csv",
    "google_reviews": DATA_DIR / "coinbase_advanceGoogle_Play.csv", 
    "twitter_mentions": DATA_DIR / "coinbase_advanced_twitter_mentions.csv",
    "internal_sales": DATA_DIR / "coinbase_advance_internal_sales_notes.csv"
}

# Output locations
OUTPUT_PATHS = {
    "pdf_report": OUTPUT_DIR / "weekly_insight_report.pdf",
    "processed_data": OUTPUT_DIR / "processed_feedback_data.csv"
}
```

## ⚙️ Configuration Sections

### 1. File Paths Configuration

#### Basic Setup
```python
# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "csv_mock_data"
OUTPUT_DIR = BASE_DIR / "output"
```

#### Custom Data Sources
```python
# For production environment with different data sources
CSV_FILE_PATHS = {
    "apple_reviews": "/data/production/ios_reviews.csv",
    "google_reviews": "/data/production/android_reviews.csv",
    "twitter_mentions": "/data/production/social_mentions.csv",
    "internal_sales": "/data/production/sales_feedback.csv"
}
```

#### Network/Cloud Storage
```python
# For cloud-based data sources
import os
CSV_FILE_PATHS = {
    "apple_reviews": os.environ.get('IOS_DATA_PATH', 'default/path.csv'),
    "google_reviews": os.environ.get('ANDROID_DATA_PATH', 'default/path.csv'),
    # ... other paths
}
```

### 2. NLP Configuration

#### Sentiment Scoring
```python
NLP_CONFIG = {
    "sentiment_values": {
        "negative": 1.5,    # Higher weight for negative feedback
        "neutral": 0.5,     # Lower weight for neutral
        "positive": 0.1     # Lowest weight for positive
    }
}
```

#### Custom Sentiment Weights
```python
# For different business priorities
NLP_CONFIG = {
    "sentiment_values": {
        "negative": 2.0,    # Emphasize negative feedback more
        "neutral": 0.3,     # De-emphasize neutral feedback
        "positive": 0.05    # Minimal weight for positive
    }
}
```

#### Strategic Goal Multipliers
```python
NLP_CONFIG = {
    "strategic_multipliers": {
        "aligned": 2.0,     # Double weight for aligned goals
        "default": 1.0      # Standard weight for others
    }
}
```

#### Default Values for Missing Data
```python
NLP_CONFIG = {
    "default_values": {
        "sentiment": "neutral",
        "theme": "General Feedback",
        "strategic_goal": "Other",
        "severity": 1.0
    }
}
```

### 3. Source Weighting Configuration

#### Internal Sales Notes Weighting
```python
SOURCE_WEIGHT_CONFIG = {
    "internal_sales": {
        "arr_divisor": 50000,      # $50k ARR = weight of 1.0
        "default_weight": 1.0      # Fallback weight
    }
}
```

#### Twitter/Social Media Weighting
```python
SOURCE_WEIGHT_CONFIG = {
    "twitter": {
        "followers_divisor": 20000,  # 20k followers = weight of 1.0
        "default_weight": 1.0        # Fallback weight
    }
}
```

#### App Store Review Weighting
```python
SOURCE_WEIGHT_CONFIG = {
    "app_store": {
        "helpful_votes_divisor": 10,  # 10 helpful votes = +1.0 to rating
        "default_weight": 1.0         # Fallback weight
    }
}
```

#### Custom Weighting Formula
```python
# Example: Emphasize enterprise customers more
SOURCE_WEIGHT_CONFIG = {
    "internal_sales": {
        "arr_divisor": 25000,      # Lower divisor = higher weights
        "default_weight": 2.0      # Higher default for enterprise
    },
    "twitter": {
        "followers_divisor": 50000,  # Higher divisor = lower weights
        "default_weight": 0.5        # Lower default for social
    }
}
```

### 4. Dashboard Configuration

#### Basic Dashboard Settings
```python
DASHBOARD_CONFIG = {
    "page_title": "Advanced Trade Insight Engine",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}
```

#### Custom Branding
```python
DASHBOARD_CONFIG = {
    "page_title": "Your Company - Customer Insights",
    "page_icon": "🏢",
    "layout": "centered",
    "initial_sidebar_state": "collapsed"
}
```

### 5. Report Configuration

#### PDF Report Settings
```python
REPORT_CONFIG = {
    "title": "Weekly Customer Feedback Insight Report",
    "subtitle": "Coinbase Advanced Trading Platform",
    "top_items_count": 3,           # Number of top items to show
    "font_size": {
        "title": 16,
        "subtitle": 14,
        "header": 12,
        "body": 10
    }
}
```

#### Custom Report Format
```python
REPORT_CONFIG = {
    "title": "Monthly Executive Summary",
    "subtitle": "Customer Experience Analysis",
    "top_items_count": 5,           # Show top 5 instead of 3
    "include_charts": True,         # Add charts to PDF
    "font_size": {
        "title": 18,
        "subtitle": 16,
        "header": 14,
        "body": 11
    }
}
```

### 6. Logging Configuration

#### Basic Logging
```python
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": OUTPUT_DIR / "insight_engine.log"
}
```

#### Debug Logging
```python
LOGGING_CONFIG = {
    "level": "DEBUG",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    "log_file": OUTPUT_DIR / "debug.log",
    "max_file_size": "10MB",
    "backup_count": 5
}
```

## 🌍 Environment-Specific Configurations

### Development Environment

Create `config_dev.py`:
```python
from config import *

# Override for development
DATA_DIR = BASE_DIR / "test_data"
OUTPUT_DIR = BASE_DIR / "dev_output"

# More verbose logging
LOGGING_CONFIG["level"] = "DEBUG"

# Faster processing for development
REPORT_CONFIG["top_items_count"] = 2
```

### Staging Environment

Create `config_staging.py`:
```python
from config import *
import os

# Use environment variables
DATA_DIR = Path(os.environ.get('STAGING_DATA_DIR', 'staging_data'))
OUTPUT_DIR = Path(os.environ.get('STAGING_OUTPUT_DIR', 'staging_output'))

# Staging-specific settings
DASHBOARD_CONFIG["page_title"] = "STAGING - Customer Insights"
```

### Production Environment

Create `config_prod.py`:
```python
from config import *
import os

# Production data sources
CSV_FILE_PATHS = {
    "apple_reviews": os.environ['PROD_IOS_DATA'],
    "google_reviews": os.environ['PROD_ANDROID_DATA'],
    "twitter_mentions": os.environ['PROD_SOCIAL_DATA'],
    "internal_sales": os.environ['PROD_SALES_DATA']
}

# Production output
OUTPUT_DIR = Path(os.environ['PROD_OUTPUT_DIR'])

# Production logging
LOGGING_CONFIG = {
    "level": "WARNING",  # Less verbose in production
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "log_file": OUTPUT_DIR / "production.log"
}
```

## 🔧 Advanced Configuration

### Custom Data Processing

#### Column Mapping Customization
```python
# Add to config.py
COLUMN_MAPPING = {
    "ios_reviews": {
        "feedback_text_source": "review_text",
        "author_source": "username",
        "rating_source": "rating"
    },
    "android_reviews": {
        "feedback_text_source": "review_text", 
        "author_source": "username",
        "rating_source": "rating"
    },
    "twitter": {
        "feedback_text_source": "tweet_text",
        "author_source": "handle",
        "rating_source": None  # No rating for Twitter
    },
    "sales_notes": {
        "feedback_text_source": "note_text",
        "author_source": "account_name",
        "rating_source": None  # No rating for sales notes
    }
}
```

#### Custom Theme Categories
```python
THEME_CONFIG = {
    "categories": [
        "Trading/Execution & Fees",
        "Performance/Outages", 
        "Support Experience",
        "Onboarding/KYC & Account Holds",
        "Payments, Deposits & Withdrawals",
        "Security, Fraud & Phishing",
        "Tax Docs & Reporting",
        "Wallet & On-chain UX",
        "General Feedback"
    ],
    "default_theme": "General Feedback"
}
```

#### Strategic Goal Mapping
```python
STRATEGIC_GOALS = {
    "categories": [
        "Growth",
        "Trust&Safety", 
        "Onchain Adoption",
        "CX Efficiency",
        "Compliance"
    ],
    "alignment_keywords": {
        "Growth": ["revenue", "acquisition", "conversion", "retention"],
        "Trust&Safety": ["security", "fraud", "safety", "trust"],
        "Onchain Adoption": ["wallet", "defi", "blockchain", "crypto"],
        "CX Efficiency": ["support", "experience", "usability", "interface"],
        "Compliance": ["kyc", "regulation", "legal", "compliance"]
    }
}
```

### Performance Optimization

#### Memory Management
```python
PERFORMANCE_CONFIG = {
    "chunk_size": 1000,           # Process data in chunks
    "max_memory_usage": "1GB",    # Memory limit
    "enable_caching": True,       # Cache processed results
    "parallel_processing": False   # Enable for large datasets
}
```

#### Processing Limits
```python
PROCESSING_LIMITS = {
    "max_records_per_source": 10000,  # Limit per data source
    "max_total_records": 50000,       # Overall limit
    "timeout_seconds": 300,           # Processing timeout
    "retry_attempts": 3               # Retry failed operations
}
```

## 🔒 Security Configuration

### Data Privacy
```python
PRIVACY_CONFIG = {
    "anonymize_customer_ids": True,
    "hash_author_handles": True,
    "remove_pii": True,
    "data_retention_days": 90
}
```

### Access Control
```python
ACCESS_CONFIG = {
    "require_authentication": False,  # Set to True for production
    "allowed_users": [],              # List of authorized users
    "admin_users": [],                # Users with admin privileges
    "read_only_users": []             # Users with read-only access
}
```

## 📊 Monitoring Configuration

### Health Checks
```python
MONITORING_CONFIG = {
    "enable_health_checks": True,
    "health_check_interval": 300,     # 5 minutes
    "alert_thresholds": {
        "processing_time": 600,       # Alert if processing > 10 min
        "error_rate": 0.05,          # Alert if error rate > 5%
        "memory_usage": 0.8          # Alert if memory > 80%
    }
}
```

### Metrics Collection
```python
METRICS_CONFIG = {
    "collect_metrics": True,
    "metrics_retention_days": 30,
    "export_format": "json",         # json, csv, or prometheus
    "metrics_endpoint": None         # URL for external metrics system
}
```

## 🚀 Using Custom Configurations

### Method 1: Environment Variables
```bash
# Set environment variables
export INSIGHT_CONFIG_ENV=production
export PROD_DATA_DIR=/data/production
export PROD_OUTPUT_DIR=/output/production

# Run with environment config
python3 main.py
```

### Method 2: Configuration File Selection
```python
# In main.py
import os
config_env = os.environ.get('INSIGHT_CONFIG_ENV', 'development')

if config_env == 'production':
    from config_prod import *
elif config_env == 'staging':
    from config_staging import *
else:
    from config import *
```

### Method 3: Command Line Override
```bash
# Override specific settings
python3 main.py --data-dir /custom/data --output-dir /custom/output --verbose
```

### Method 4: Runtime Configuration
```python
# Modify config at runtime
import config

# Override data directory
config.DATA_DIR = Path('/new/data/location')

# Update file paths
config.CSV_FILE_PATHS['apple_reviews'] = config.DATA_DIR / 'ios_data.csv'

# Run with modified config
from main import main
main()
```

## ✅ Configuration Validation

### Validation Script
Create `validate_config.py`:
```python
#!/usr/bin/env python3
import config
from pathlib import Path

def validate_configuration():
    """Validate all configuration settings"""
    errors = []
    warnings = []
    
    # Check file paths
    for name, path in config.CSV_FILE_PATHS.items():
        if not Path(path).exists():
            errors.append(f"Missing data file: {name} -> {path}")
    
    # Check output directory
    if not config.OUTPUT_DIR.exists():
        warnings.append(f"Output directory will be created: {config.OUTPUT_DIR}")
    
    # Check NLP config
    required_sentiments = ['positive', 'negative', 'neutral']
    for sentiment in required_sentiments:
        if sentiment not in config.NLP_CONFIG['sentiment_values']:
            errors.append(f"Missing sentiment value: {sentiment}")
    
    # Display results
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("✅ Configuration is valid")
    
    return len(errors) == 0

if __name__ == "__main__":
    validate_configuration()
```

Run validation:
```bash
python3 validate_config.py
```

## 🔄 Configuration Migration

### Upgrading Configuration
When upgrading to new versions, use this migration pattern:

```python
# config_migration.py
def migrate_config_v1_to_v2():
    """Migrate configuration from v1 to v2 format"""
    
    # Read old config
    with open('config_v1.py', 'r') as f:
        old_config = f.read()
    
    # Apply transformations
    new_config = old_config.replace('OLD_SETTING', 'NEW_SETTING')
    
    # Write new config
    with open('config.py', 'w') as f:
        f.write(new_config)
    
    print("✅ Configuration migrated to v2")
```

---

**Remember**: Always backup your configuration files before making changes, and test configurations in a development environment before deploying to production.