"""
Secure Dashboard Application with Authentication

This is the main entry point for the authenticated dashboard.
Run with: streamlit run src/dashboard/secure_dashboard.py

Features:
- Login/logout functionality
- Role-based access control (Admin, Analyst, Viewer)
- Session management
- Secure password hashing

Implementation time: 1 hour
"""

import streamlit as st
import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from auth.auth_config import get_authenticator, get_user_role, has_permission, get_user_info
from dashboard.dashboard import (
    load_and_process_data,
    display_main_dashboard,
    display_error_page
)

# Page configuration
st.set_page_config(
    page_title="🔐 Secure Trade Insight Engine",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def show_login_page():
    """Display the login page"""
    st.title("🔐 Advanced Trade Insight Engine")
    st.subheader("Secure Access Portal")
    
    # Login instructions
    st.info("**Demo Credentials:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**👑 Admin Access**")
        st.code("Username: admin\nPassword: admin123")
        st.caption("Full system access")
    
    with col2:
        st.write("**📊 Analyst Access**") 
        st.code("Username: analyst\nPassword: analyst123")
        st.caption("Dashboard + Reports")
    
    with col3:
        st.write("**👀 Viewer Access**")
        st.code("Username: viewer\nPassword: viewer123") 
        st.caption("Read-only access")

def show_user_info_sidebar(name: str, username: str, role: str):
    """Display user information in sidebar"""
    st.sidebar.title("👤 User Profile")
    
    # User info
    st.sidebar.write(f"**Name:** {name}")
    st.sidebar.write(f"**Username:** {username}")
    st.sidebar.write(f"**Role:** {role.title()}")
    
    # Role badge
    role_colors = {
        'admin': '🔴',
        'analyst': '🟡', 
        'viewer': '🟢'
    }
    st.sidebar.write(f"**Access Level:** {role_colors.get(role, '⚪')} {role.title()}")
    
    st.sidebar.markdown("---")

def customize_dashboard_by_role(role: str, df):
    """Customize dashboard features based on user role"""
    
    # Admin gets full access
    if role == 'admin':
        st.success("🔴 **Admin Access** - Full system privileges")
        config = {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': True,
            'show_advanced_filters': True,
            'data_directory': 'csv_mock_data'
        }
        
    # Analyst gets dashboard + reports
    elif role == 'analyst':
        st.info("🟡 **Analyst Access** - Dashboard and reporting privileges")
        config = {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': True,
            'show_advanced_filters': True,
            'data_directory': 'csv_mock_data'
        }
        
    # Viewer gets read-only
    elif role == 'viewer':
        st.warning("🟢 **Viewer Access** - Read-only privileges")
        config = {
            'show_charts': True,
            'show_raw_data': True,
            'show_export': False,
            'show_advanced_filters': False,
            'data_directory': 'csv_mock_data'
        }
        
    else:
        st.error("❌ **Unknown Role** - Access denied")
        return None
    
    return config

def show_role_specific_features(role: str):
    """Show role-specific features and limitations"""
    
    if role == 'admin':
        with st.expander("🔴 Admin Features"):
            st.write("✅ Full dashboard access")
            st.write("✅ All data sources")
            st.write("✅ Export capabilities")
            st.write("✅ Advanced filtering")
            st.write("✅ User management (future)")
            st.write("✅ System configuration")
            
    elif role == 'analyst':
        with st.expander("🟡 Analyst Features"):
            st.write("✅ Full dashboard access")
            st.write("✅ All data sources")
            st.write("✅ Export capabilities")
            st.write("✅ Advanced filtering")
            st.write("❌ User management")
            st.write("❌ System configuration")
            
    elif role == 'viewer':
        with st.expander("🟢 Viewer Features"):
            st.write("✅ Dashboard viewing")
            st.write("✅ Basic filtering")
            st.write("✅ Chart interactions")
            st.write("❌ Data export")
            st.write("❌ Advanced filtering")
            st.write("❌ User management")

def main():
    """Main application with authentication"""
    
    # Initialize authenticator
    authenticator = get_authenticator()
    
    # Login widget
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    # Handle authentication states
    if authentication_status == False:
        st.error('Username/password is incorrect')
        show_login_page()
        
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        show_login_page()
        
    elif authentication_status == True:
        # User is authenticated
        user_role = get_user_role(username)
        user_info = get_user_info(username)
        
        # Show user info in sidebar
        show_user_info_sidebar(name, username, user_role)
        
        # Logout button
        authenticator.logout('Logout', 'sidebar')
        
        # Role-specific welcome message
        st.title(f"📊 Advanced Trade Insight Engine")
        st.write(f"Welcome back, **{name}**! 👋")
        
        # Show role-specific features
        show_role_specific_features(user_role)
        
        try:
            # Load and process data
            with st.spinner("Loading secure dashboard..."):
                df = load_and_process_data('csv_mock_data')
            
            if df is not None and not df.empty:
                # Get role-based configuration
                config = customize_dashboard_by_role(user_role, df)
                
                if config:
                    # Display main dashboard with role restrictions
                    display_main_dashboard(df, config)
                    
                    # Show session info
                    st.sidebar.markdown("---")
                    st.sidebar.subheader("🔒 Session Info")
                    st.sidebar.write(f"**Records:** {len(df):,}")
                    st.sidebar.write(f"**Sources:** {df['source_channel'].nunique()}")
                    st.sidebar.write(f"**Login Time:** {st.session_state.get('login_time', 'Unknown')}")
                    
                else:
                    st.error("Access denied - Invalid role configuration")
                    
            else:
                display_error_page("Failed to load dashboard data")
                
        except Exception as e:
            st.error(f"Dashboard error: {str(e)}")
            display_error_page(f"Application error: {str(e)}")

if __name__ == "__main__":
    # Store login time
    if 'login_time' not in st.session_state:
        import datetime
        st.session_state.login_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    main()