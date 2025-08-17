"""
Phase 1 Security Tests

Quick tests to verify Phase 1 security implementation
"""

import unittest
import os
import tempfile
import pandas as pd
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from security.input_validator import CSVValidator, validate_csv_upload
from security.audit_logger import AuditLogger, AuditEventType

class TestPhase1Security(unittest.TestCase):
    """Test Phase 1 security features"""
    
    def setUp(self):
        """Set up test environment"""
        self.validator = CSVValidator()
        
        # Create test CSV file
        self.test_data = pd.DataFrame({
            'customer_id': ['C001', 'C002'],
            'source': ['test', 'test'],
            'feedback_text': ['Good product', 'Needs improvement'],
            'sentiment': ['positive', 'negative']
        })
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.test_data.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test environment"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_csv_validation_basic(self):
        """Test basic CSV validation"""
        results = self.validator.validate_file_basic(self.temp_file.name)
        
        self.assertTrue(results['file_exists'])
        self.assertTrue(results['size_valid'])
        self.assertTrue(results['extension_valid'])
    
    def test_csv_structure_validation(self):
        """Test CSV structure validation"""
        results = self.validator.validate_csv_structure(self.temp_file.name)
        
        self.assertTrue(results['readable'])
        self.assertTrue(results['structure_valid'])
        self.assertEqual(results['row_count'], 2)
        self.assertEqual(results['column_count'], 4)
    
    def test_malicious_content_scan(self):
        """Test malicious content scanning"""
        results = self.validator.scan_for_malicious_content(self.temp_file.name)
        
        self.assertTrue(results['scan_completed'])
        self.assertTrue(results['is_safe'])
        self.assertEqual(len(results['threats_found']), 0)
    
    def test_complete_validation(self):
        """Test complete validation pipeline"""
        is_valid, results = validate_csv_upload(self.temp_file.name)
        
        self.assertTrue(is_valid)
        self.assertTrue(results['validation_passed'])
    
    def test_audit_logging(self):
        """Test audit logging functionality"""
        # Test basic event logging
        AuditLogger.log_login_success('test_user')
        AuditLogger.log_data_access('test_user', 'test_source', 100)
        AuditLogger.log_logout('test_user')
        
        # Verify log file exists
        log_file = os.path.join('logs', 'audit.log')
        self.assertTrue(os.path.exists(log_file))
    
    def test_malicious_csv_detection(self):
        """Test detection of malicious CSV content"""
        # Create malicious CSV
        malicious_data = pd.DataFrame({
            'customer_id': ['C001'],
            'feedback_text': ['<script>alert("xss")</script>'],
            'sentiment': ['positive']
        })
        
        malicious_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        malicious_data.to_csv(malicious_file.name, index=False)
        malicious_file.close()
        
        try:
            results = self.validator.scan_for_malicious_content(malicious_file.name)
            
            self.assertTrue(results['scan_completed'])
            self.assertFalse(results['is_safe'])
            self.assertGreater(len(results['threats_found']), 0)
            
        finally:
            os.unlink(malicious_file.name)

if __name__ == '__main__':
    unittest.main()