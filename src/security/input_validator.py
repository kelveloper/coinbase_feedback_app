"""
Input Validation Module - Phase 1 Security

Provides comprehensive CSV file validation and sanitization
to prevent malicious uploads and data injection attacks.
"""

import pandas as pd
import os
import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
MAX_FILE_SIZE_MB = 50
ALLOWED_EXTENSIONS = ['.csv']
MAX_ROWS = 100000
MAX_COLUMNS = 100

# Expected column patterns for each source type
EXPECTED_COLUMNS = {
    'ios_reviews': ['customer_id', 'source', 'username', 'timestamp', 'rating', 'sentiment', 'review_text', 'theme'],
    'android_reviews': ['customer_id', 'source', 'username', 'timestamp', 'rating', 'sentiment', 'review_text', 'theme'],
    'sales_notes': ['customer_id', 'source', 'account_name', 'timestamp', 'sentiment', 'note_text', 'theme', 'ARR_impact_estimate_USD'],
    'twitter_mentions': ['customer_id', 'source', 'handle', 'followers', 'timestamp', 'sentiment', 'tweet_text', 'theme']
}

# Malicious patterns to detect
MALICIOUS_PATTERNS = [
    r'<script.*?>.*?</script>',  # XSS attempts
    r'javascript:',              # JavaScript injection
    r'data:text/html',          # Data URI attacks
    r'SELECT.*FROM',            # SQL injection
    r'DROP\s+TABLE',            # SQL injection
    r'INSERT\s+INTO',           # SQL injection
    r'UPDATE.*SET',             # SQL injection
    r'DELETE\s+FROM',           # SQL injection
    r'UNION\s+SELECT',          # SQL injection
    r'exec\s*\(',               # Code execution
    r'eval\s*\(',               # Code execution
    r'system\s*\(',             # System commands
    r'__import__',              # Python imports
    r'subprocess',              # Process execution
]

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class CSVValidator:
    """Comprehensive CSV file validator"""
    
    def __init__(self):
        self.validation_results = {}
    
    def validate_file_basic(self, file_path: str) -> Dict[str, any]:
        """
        Basic file validation: size, extension, existence
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            Dict[str, any]: Validation results
            
        Raises:
            ValidationError: If validation fails
        """
        results = {
            'file_exists': False,
            'size_valid': False,
            'extension_valid': False,
            'file_size_mb': 0
        }
        
        try:
            # Check file existence
            if not os.path.exists(file_path):
                raise ValidationError(f"File does not exist: {file_path}")
            results['file_exists'] = True
            
            # Check file size
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            results['file_size_mb'] = round(file_size_mb, 2)
            
            if file_size_mb > MAX_FILE_SIZE_MB:
                raise ValidationError(f"File too large: {file_size_mb:.2f}MB (max: {MAX_FILE_SIZE_MB}MB)")
            results['size_valid'] = True
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(f"Invalid file extension: {file_ext} (allowed: {ALLOWED_EXTENSIONS})")
            results['extension_valid'] = True
            
            logger.info(f"Basic validation passed for {file_path} ({file_size_mb:.2f}MB)")
            return results
            
        except Exception as e:
            logger.error(f"Basic validation failed for {file_path}: {e}")
            raise ValidationError(f"Basic validation failed: {str(e)}")
    
    def validate_csv_structure(self, file_path: str, source_type: Optional[str] = None) -> Dict[str, any]:
        """
        Validate CSV structure and content
        
        Args:
            file_path (str): Path to the CSV file
            source_type (str, optional): Expected source type for column validation
            
        Returns:
            Dict[str, any]: Structure validation results
        """
        results = {
            'readable': False,
            'row_count': 0,
            'column_count': 0,
            'columns': [],
            'structure_valid': False,
            'expected_columns_present': False
        }
        
        try:
            # Try to read CSV
            df = pd.read_csv(file_path, nrows=1)  # Read just header first
            results['readable'] = True
            results['columns'] = df.columns.tolist()
            results['column_count'] = len(df.columns)
            
            # Check column count
            if results['column_count'] > MAX_COLUMNS:
                raise ValidationError(f"Too many columns: {results['column_count']} (max: {MAX_COLUMNS})")
            
            # Read full file to check row count
            df_full = pd.read_csv(file_path)
            results['row_count'] = len(df_full)
            
            if results['row_count'] > MAX_ROWS:
                raise ValidationError(f"Too many rows: {results['row_count']} (max: {MAX_ROWS})")
            
            # Validate column names (no special characters)
            for col in results['columns']:
                if not re.match(r'^[a-zA-Z0-9_\s]+$', str(col)):
                    raise ValidationError(f"Invalid column name: {col}")
            
            results['structure_valid'] = True
            
            # Check expected columns if source type provided
            if source_type and source_type in EXPECTED_COLUMNS:
                expected_cols = EXPECTED_COLUMNS[source_type]
                missing_cols = [col for col in expected_cols if col not in results['columns']]
                if not missing_cols:
                    results['expected_columns_present'] = True
                else:
                    logger.warning(f"Missing expected columns for {source_type}: {missing_cols}")
            
            logger.info(f"Structure validation passed: {results['row_count']} rows, {results['column_count']} columns")
            return results
            
        except pd.errors.EmptyDataError:
            raise ValidationError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValidationError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            logger.error(f"Structure validation failed: {e}")
            raise ValidationError(f"Structure validation failed: {str(e)}")
    
    def scan_for_malicious_content(self, file_path: str, sample_size: int = 1000) -> Dict[str, any]:
        """
        Scan CSV content for malicious patterns
        
        Args:
            file_path (str): Path to the CSV file
            sample_size (int): Number of rows to sample for scanning
            
        Returns:
            Dict[str, any]: Security scan results
        """
        results = {
            'scan_completed': False,
            'threats_found': [],
            'rows_scanned': 0,
            'is_safe': True
        }
        
        try:
            # Read sample of data
            df = pd.read_csv(file_path, nrows=sample_size)
            results['rows_scanned'] = len(df)
            
            # Convert all data to strings for pattern matching
            text_data = df.astype(str).values.flatten()
            
            # Scan for malicious patterns
            for i, text in enumerate(text_data):
                if pd.isna(text) or text == 'nan':
                    continue
                    
                for pattern in MALICIOUS_PATTERNS:
                    if re.search(pattern, text, re.IGNORECASE):
                        threat = {
                            'pattern': pattern,
                            'found_in': text[:100],  # First 100 chars
                            'position': i
                        }
                        results['threats_found'].append(threat)
                        results['is_safe'] = False
                        logger.warning(f"Malicious pattern detected: {pattern}")
            
            results['scan_completed'] = True
            
            if results['is_safe']:
                logger.info(f"Security scan passed: {results['rows_scanned']} rows scanned, no threats found")
            else:
                logger.error(f"Security threats found: {len(results['threats_found'])} patterns detected")
            
            return results
            
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            raise ValidationError(f"Security scan failed: {str(e)}")
    
    def sanitize_csv_data(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Sanitize CSV data by removing/cleaning suspicious content
        
        Args:
            file_path (str): Path to input CSV file
            output_path (str, optional): Path for sanitized output file
            
        Returns:
            str: Path to sanitized file
        """
        try:
            if output_path is None:
                output_path = file_path.replace('.csv', '_sanitized.csv')
            
            # Read CSV
            df = pd.read_csv(file_path)
            
            # Sanitize text columns
            text_columns = df.select_dtypes(include=['object']).columns
            
            for col in text_columns:
                if col in df.columns:
                    # Remove HTML tags
                    df[col] = df[col].astype(str).str.replace(r'<[^>]+>', '', regex=True)
                    
                    # Remove JavaScript
                    df[col] = df[col].str.replace(r'javascript:', '', regex=True, flags=re.IGNORECASE)
                    
                    # Remove data URIs
                    df[col] = df[col].str.replace(r'data:text/html', '', regex=True, flags=re.IGNORECASE)
                    
                    # Clean SQL injection attempts
                    sql_patterns = ['SELECT', 'DROP', 'INSERT', 'UPDATE', 'DELETE', 'UNION']
                    for pattern in sql_patterns:
                        df[col] = df[col].str.replace(pattern, '', regex=True, flags=re.IGNORECASE)
            
            # Save sanitized file
            df.to_csv(output_path, index=False)
            
            logger.info(f"Data sanitized and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Data sanitization failed: {e}")
            raise ValidationError(f"Data sanitization failed: {str(e)}")
    
    def validate_csv_file(self, file_path: str, source_type: Optional[str] = None, 
                         sanitize: bool = True) -> Dict[str, any]:
        """
        Complete CSV file validation pipeline
        
        Args:
            file_path (str): Path to the CSV file
            source_type (str, optional): Expected source type
            sanitize (bool): Whether to sanitize the file
            
        Returns:
            Dict[str, any]: Complete validation results
        """
        validation_results = {
            'file_path': file_path,
            'validation_passed': False,
            'basic_validation': {},
            'structure_validation': {},
            'security_scan': {},
            'sanitized_file': None,
            'errors': []
        }
        
        try:
            # Step 1: Basic validation
            logger.info(f"Starting validation for: {file_path}")
            validation_results['basic_validation'] = self.validate_file_basic(file_path)
            
            # Step 2: Structure validation
            validation_results['structure_validation'] = self.validate_csv_structure(file_path, source_type)
            
            # Step 3: Security scan
            validation_results['security_scan'] = self.scan_for_malicious_content(file_path)
            
            # Step 4: Sanitization (if requested and threats found)
            if sanitize and not validation_results['security_scan']['is_safe']:
                validation_results['sanitized_file'] = self.sanitize_csv_data(file_path)
                logger.info("File sanitized due to security threats")
            
            # Overall validation result
            validation_results['validation_passed'] = (
                validation_results['basic_validation']['extension_valid'] and
                validation_results['basic_validation']['size_valid'] and
                validation_results['structure_validation']['structure_valid'] and
                (validation_results['security_scan']['is_safe'] or sanitize)
            )
            
            if validation_results['validation_passed']:
                logger.info(f"✅ Complete validation passed for: {file_path}")
            else:
                logger.error(f"❌ Validation failed for: {file_path}")
            
            return validation_results
            
        except ValidationError as e:
            validation_results['errors'].append(str(e))
            logger.error(f"Validation error: {e}")
            return validation_results
        except Exception as e:
            validation_results['errors'].append(f"Unexpected error: {str(e)}")
            logger.error(f"Unexpected validation error: {e}")
            return validation_results


def validate_csv_upload(file_path: str, source_type: Optional[str] = None) -> Tuple[bool, Dict[str, any]]:
    """
    Quick validation function for CSV uploads
    
    Args:
        file_path (str): Path to uploaded CSV file
        source_type (str, optional): Expected source type
        
    Returns:
        Tuple[bool, Dict]: (is_valid, validation_results)
    """
    validator = CSVValidator()
    results = validator.validate_csv_file(file_path, source_type, sanitize=True)
    return results['validation_passed'], results


def get_validation_summary(validation_results: Dict[str, any]) -> str:
    """
    Generate human-readable validation summary
    
    Args:
        validation_results (Dict): Results from validation
        
    Returns:
        str: Formatted summary
    """
    if validation_results['validation_passed']:
        return f"✅ Validation passed for {validation_results['file_path']}"
    else:
        errors = validation_results.get('errors', ['Unknown error'])
        return f"❌ Validation failed: {'; '.join(errors)}"