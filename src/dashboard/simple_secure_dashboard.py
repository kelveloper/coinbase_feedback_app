"""
Simple Secure Dashboard - Fallback Authentication

This version uses a custom authentication system that's guaranteed to work.
Run with: streamlit run src/dashboard/simple_secure_dashboard.py
"""

import streamlit as st
import sys
import os
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from auth.simple_auth import check_authentication, show_logout_button, get_user_info
from auth.auth_config import get_user_role, has_permission
from dashboard.dashboard import (
    load_and_process_data,
    display_main_dashboard,
    display_error_page
)

# Phase 1 Security Integration
from security.audit_logger import AuditLogger, AuditEventType, audit_action
from security.input_validator import validate_csv_upload
from security.security_headers import inject_security_headers_streamlit, initialize_https

# Page configuration
st.set_page_config(
    page_title="🔐 Secure Trade Insight Engine",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    """Main application with simple authentication and Phase 1 security"""
    
    # Initialize security features
    inject_security_headers_streamlit()
    
    # Check authentication
    name, authentication_status, username = check_authentication()
    
    if authentication_status == True and username:
        # Log successful authentication
        AuditLogger.log_login_success(username)
        AuditLogger.log_dashboard_view(username, "main_dashboard")
        
        # User is authenticated
        user_role = get_user_role(username)
        
        # Show user info in sidebar
        show_user_info_sidebar(name, username, user_role)
        
        # Logout button with audit logging
        if st.sidebar.button("🚪 Logout"):
            AuditLogger.log_logout(username)
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_info = None
            st.rerun()
        
        # Role-specific welcome message
        st.title(f"📊 Advanced Trade Insight Engine")
        st.write(f"Welcome back, **{name}**! 👋")
        
        # Show role-specific features
        show_role_specific_features(user_role)
        
        try:
            # Load and process data with audit logging
            with st.spinner("Loading secure dashboard..."):
                df = load_and_process_data('csv_mock_data')
                
                if df is not None and not df.empty:
                    # Log data access
                    AuditLogger.log_data_access(username, 'csv_mock_data', len(df))
            
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
                    
                else:
                    st.error("Access denied - Invalid role configuration")
                    
            else:
                display_error_page("Failed to load dashboard data")
                
        except Exception as e:
            st.error(f"Dashboard error: {str(e)}")
            display_error_page(f"Application error: {str(e)}")
    
    else:
        # User is not authenticated - login form is already shown by check_authentication()
        pass

if __name__ == "__main__":
    main()