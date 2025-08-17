"""
Simple Custom Authentication System
Fallback if streamlit-authenticator has API issues
"""

import streamlit as st
import bcrypt
from typing import Optional, Tuple

# Simple user database
USERS = {
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

def verify_password(username: str, password: str) -> bool:
    """Verify username and password"""
    if username in USERS:
        return USERS[username]['password'] == password
    return False

def get_user_info(username: str) -> dict:
    """Get user information"""
    return USERS.get(username, {})

def show_login_form() -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """Show login form and handle authentication"""
    
    st.title("🔐 Advanced Trade Insight Engine")
    st.subheader("Secure Access Portal")
    
    # Login form
    with st.form("login_form"):
        st.write("**Please enter your credentials:**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                if verify_password(username, password):
                    # Store in session state
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.user_info = get_user_info(username)
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

def check_authentication() -> Tuple[Optional[str], Optional[bool], Optional[str]]:
    """Check if user is authenticated"""
    
    if st.session_state.get('authenticated', False):
        user_info = st.session_state.get('user_info', {})
        username = st.session_state.get('username')
        return user_info.get('name'), True, username
    
    return show_login_form()

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = None
    st.rerun()

def show_logout_button():
    """Show logout button in sidebar"""
    if st.sidebar.button("🚪 Logout"):
        logout()