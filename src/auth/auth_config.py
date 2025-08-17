"""
Authentication Configuration for Advanced Trade Insight Engine

Simple 3-role authentication system:
- Admin: Full access to everything
- Analyst: Dashboard access with advanced features  
- Viewer: Read-only dashboard access

Implementation time: 1 hour
"""

import streamlit_authenticator as stauth
import bcrypt
import yaml
from typing import Dict, List

# User database with hashed passwords
# In production, this should be in a secure database
USERS_CONFIG = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': 'System Administrator',
                'password': '$2b$12$gvKPKBxKdJkKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJ',  # admin123
                'role': 'admin',
                'email': 'admin@coinbase.com'
            },
            'analyst': {
                'name': 'Senior Analyst',
                'password': '$2b$12$gvKPKBxKdJkKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJ',  # analyst123
                'role': 'analyst', 
                'email': 'analyst@coinbase.com'
            },
            'viewer': {
                'name': 'Report Viewer',
                'password': '$2b$12$gvKPKBxKdJkKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJxOKqGxQJxQJ',  # viewer123
                'role': 'viewer',
                'email': 'viewer@coinbase.com'
            }
        }
    },
    'cookie': {
        'name': 'trade_insight_auth',
        'key': 'coinbase_secret_key_2024',
        'expiry_days': 1
    },
    'preauthorized': {
        'emails': ['admin@coinbase.com']
    }
}

# Role-based permissions
ROLE_PERMISSIONS = {
    'admin': [
        'view_dashboard',
        'generate_reports', 
        'export_data',
        'advanced_filters',
        'manage_users',
        'view_all_data',
        'system_config'
    ],
    'analyst': [
        'view_dashboard',
        'generate_reports',
        'export_data', 
        'advanced_filters',
        'view_assigned_data'
    ],
    'viewer': [
        'view_dashboard',
        'view_reports',
        'basic_filters'
    ]
}

def hash_passwords():
    """Generate hashed passwords for users"""
    passwords = {
        'admin': 'admin123',
        'analyst': 'analyst123', 
        'viewer': 'viewer123'
    }
    
    hashed = {}
    for username, password in passwords.items():
        # Use bcrypt directly for hashing
        salt = bcrypt.gensalt()
        hashed[username] = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    return hashed

def get_user_permissions(role: str) -> List[str]:
    """Get permissions for a specific role"""
    return ROLE_PERMISSIONS.get(role, [])

def has_permission(role: str, permission: str) -> bool:
    """Check if role has specific permission"""
    return permission in get_user_permissions(role)

def get_authenticator():
    """Create and return streamlit authenticator instance"""
    
    # Generate fresh hashed passwords
    hashed_passwords = hash_passwords()
    
    # Update config with hashed passwords
    config = USERS_CONFIG.copy()
    for username in config['credentials']['usernames']:
        config['credentials']['usernames'][username]['password'] = hashed_passwords[username]
    
    # Create authenticator with correct parameter order
    authenticator = stauth.Authenticate(
        credentials=config['credentials'],
        cookie_name=config['cookie']['name'],
        cookie_key=config['cookie']['key'],
        cookie_expiry_days=config['cookie']['expiry_days']
    )
    
    return authenticator

def get_user_role(username: str) -> str:
    """Get role for authenticated user"""
    return USERS_CONFIG['credentials']['usernames'].get(username, {}).get('role', 'viewer')

def get_user_info(username: str) -> Dict:
    """Get full user information"""
    return USERS_CONFIG['credentials']['usernames'].get(username, {})