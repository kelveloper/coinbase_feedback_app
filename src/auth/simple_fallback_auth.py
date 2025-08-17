"""
Simple Fallback Authentication System
No external dependencies required - pure Python implementation
"""

import streamlit as st
from typing import Optional, Tuple, Dict

# Simple user database - no hashing for fallback
SIMPLE_USERS = {
    'admin': {
        'password': 'admin123',
        'name': 'System Administrator',
        'role': 'admin',
        'email': 'admin@coinbase.com'
    },
    'analyst': {
        'password': 'analyst123',
        'name': 'Senior Analyst', 
        'role': 'analyst',
        'email': 'analyst@coinbase.com'
    },
    'viewer': {
        'password': 'viewer123',
        'name': 'Report Viewer',
        'role': 'viewer',
        'email': 'viewer@coinbase.com'
    }
}

def verify_simple_password(username: str, password: str) -> bool:
    """Verify username and password - simple version"""
    if username in SIMPLE_USERS:
        return SIMPLE_USERS[username]['password'] == password
    return False

def get_simple_user_info(username: str) -> Dict:
    """Get user information - simple version"""
    return SIMPLE_USERS.get(username, {})

def show_simple_login_form() -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """Show simple login form and handle authentication"""
    
    st.title("🔐 Enhanced Feedback Analytics")
    st.subheader("Secure Access Portal")
    
    # Login form
    with st.form("simple_login_form"):
        st.write("**Please enter your credentials:**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                if verify_simple_password(username, password):
                    # Store in session state
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_info = get_simple_user_info(username)
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
                    return None, False, None
            else:
                st.warning("Please enter both username and password")
                return None, None, None
    
    # Show demo credentials
    st.info("**Demo Credentials:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**👑 Admin**")
        st.code("admin / admin123")
    
    with col2:
        st.write("**📊 Analyst**") 
        st.code("analyst / analyst123")
    
    with col3:
        st.write("**👀 Viewer**")
        st.code("viewer / viewer123")
    
    return None, None, None

def check_simple_authentication() -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """Check if user is authenticated - simple version"""
    
    if st.session_state.get('authenticated', False):
        user_info = st.session_state.get('user_info', {})
        username = st.session_state.get('username')
        return user_info.get('name'), True, username
    
    return show_simple_login_form()

def simple_logout():
    """Logout user - simple version"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.rerun()

def show_simple_logout_button():
    """Show logout button in sidebar - simple version"""
    if st.sidebar.button("🚪 Logout"):
        simple_logout()

def get_simple_user_role(username: str) -> str:
    """Get role for authenticated user - simple version"""
    return SIMPLE_USERS.get(username, {}).get('role', 'viewer')