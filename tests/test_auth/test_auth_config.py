"""
Quick tests for authentication system
"""

import unittest
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from auth.auth_config import (
    get_user_permissions,
    has_permission,
    get_user_role,
    hash_passwords,
    ROLE_PERMISSIONS
)

class TestAuthConfig(unittest.TestCase):
    """Test authentication configuration"""
    
    def test_role_permissions(self):
        """Test role permission system"""
        # Admin should have all permissions
        admin_perms = get_user_permissions('admin')
        self.assertIn('view_dashboard', admin_perms)
        self.assertIn('manage_users', admin_perms)
        
        # Analyst should have dashboard but not user management
        analyst_perms = get_user_permissions('analyst')
        self.assertIn('view_dashboard', analyst_perms)
        self.assertNotIn('manage_users', analyst_perms)
        
        # Viewer should have minimal permissions
        viewer_perms = get_user_permissions('viewer')
        self.assertIn('view_dashboard', viewer_perms)
        self.assertNotIn('export_data', viewer_perms)
    
    def test_permission_checking(self):
        """Test permission checking function"""
        self.assertTrue(has_permission('admin', 'manage_users'))
        self.assertFalse(has_permission('viewer', 'export_data'))
        self.assertTrue(has_permission('analyst', 'generate_reports'))
    
    def test_user_roles(self):
        """Test user role retrieval"""
        self.assertEqual(get_user_role('admin'), 'admin')
        self.assertEqual(get_user_role('analyst'), 'analyst')
        self.assertEqual(get_user_role('viewer'), 'viewer')
        self.assertEqual(get_user_role('nonexistent'), 'viewer')  # Default
    
    def test_password_hashing(self):
        """Test password hashing function"""
        hashed = hash_passwords()
        self.assertIn('admin', hashed)
        self.assertIn('analyst', hashed)
        self.assertIn('viewer', hashed)
        
        # Hashed passwords should not be plain text
        self.assertNotEqual(hashed['admin'], 'admin123')

if __name__ == '__main__':
    unittest.main()