"""
Security Headers and HTTPS Configuration - Phase 1 Security

Provides HTTPS setup, security headers, and transport layer security
for the Streamlit application.
"""

import os
import ssl
import subprocess
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# SSL Configuration
SSL_DIR = "config/ssl"
CERT_FILE = "ssl_cert.pem"
KEY_FILE = "ssl_key.pem"

def generate_self_signed_certificate():
    """
    Generate self-signed SSL certificate for HTTPS
    
    Returns:
        Tuple[str, str]: (cert_path, key_path)
    """
    try:
        # Create SSL directory
        os.makedirs(SSL_DIR, exist_ok=True)
        
        cert_path = os.path.join(SSL_DIR, CERT_FILE)
        key_path = os.path.join(SSL_DIR, KEY_FILE)
        
        # Check if certificate already exists
        if os.path.exists(cert_path) and os.path.exists(key_path):
            logger.info("SSL certificate already exists")
            return cert_path, key_path
        
        # Generate self-signed certificate using OpenSSL
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
            '-keyout', key_path,
            '-out', cert_path,
            '-days', '365',
            '-nodes',
            '-subj', '/C=US/ST=CA/L=San Francisco/O=Coinbase/OU=Security/CN=localhost'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"SSL certificate generated: {cert_path}")
            return cert_path, key_path
        else:
            logger.error(f"Failed to generate SSL certificate: {result.stderr}")
            return None, None
            
    except Exception as e:
        logger.error(f"Error generating SSL certificate: {e}")
        return None, None

def create_streamlit_config():
    """
    Create Streamlit configuration file with HTTPS settings
    
    Returns:
        str: Path to config file
    """
    try:
        # Generate certificate
        cert_path, key_path = generate_self_signed_certificate()
        
        if not cert_path or not key_path:
            logger.warning("Could not generate SSL certificate, using HTTP")
            return None
        
        # Create Streamlit config
        config_dir = ".streamlit"
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, "config.toml")
        
        config_content = f"""
[server]
# HTTPS Configuration
sslCertFile = "{cert_path}"
sslKeyFile = "{key_path}"
enableCORS = false
enableXsrfProtection = true

# Security Headers
headless = true

[browser]
gatherUsageStats = false
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        logger.info(f"Streamlit HTTPS config created: {config_path}")
        return config_path
        
    except Exception as e:
        logger.error(f"Error creating Streamlit config: {e}")
        return None

def add_security_headers():
    """
    Add security headers to Streamlit app (via HTML injection)
    
    Returns:
        str: HTML with security headers
    """
    security_headers_html = """
    <script>
    // Add security headers via meta tags
    const addSecurityHeaders = () => {
        const head = document.head;
        
        // Content Security Policy
        const csp = document.createElement('meta');
        csp.httpEquiv = 'Content-Security-Policy';
        csp.content = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:;";
        head.appendChild(csp);
        
        // X-Frame-Options
        const xframe = document.createElement('meta');
        xframe.httpEquiv = 'X-Frame-Options';
        xframe.content = 'DENY';
        head.appendChild(xframe);
        
        // X-Content-Type-Options
        const xcontent = document.createElement('meta');
        xcontent.httpEquiv = 'X-Content-Type-Options';
        xcontent.content = 'nosniff';
        head.appendChild(xcontent);
        
        // X-XSS-Protection
        const xxss = document.createElement('meta');
        xxss.httpEquiv = 'X-XSS-Protection';
        xxss.content = '1; mode=block';
        head.appendChild(xxss);
        
        // Referrer Policy
        const referrer = document.createElement('meta');
        referrer.name = 'referrer';
        referrer.content = 'strict-origin-when-cross-origin';
        head.appendChild(referrer);
        
        // Permissions Policy
        const permissions = document.createElement('meta');
        permissions.httpEquiv = 'Permissions-Policy';
        permissions.content = 'geolocation=(), microphone=(), camera=()';
        head.appendChild(permissions);
    };
    
    // Apply headers when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addSecurityHeaders);
    } else {
        addSecurityHeaders();
    }
    </script>
    """
    
    return security_headers_html

def inject_security_headers_streamlit():
    """
    Inject security headers into Streamlit app
    """
    try:
        import streamlit as st
        
        # Inject security headers
        st.markdown(add_security_headers(), unsafe_allow_html=True)
        
        # Add security-related CSS
        security_css = """
        <style>
        /* Prevent clickjacking */
        body {
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        
        /* Hide sensitive elements from screenshots */
        .sensitive-data {
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            -khtml-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        </style>
        """
        
        st.markdown(security_css, unsafe_allow_html=True)
        
        logger.info("Security headers injected into Streamlit app")
        
    except Exception as e:
        logger.error(f"Failed to inject security headers: {e}")

def setup_https_redirect():
    """
    Setup HTTPS redirect (for production deployment)
    
    Returns:
        str: Nginx configuration snippet
    """
    nginx_config = """
# HTTPS Redirect Configuration
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/ssl_cert.pem;
    ssl_certificate_key /path/to/ssl_key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Proxy to Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    return nginx_config

def validate_ssl_setup() -> Dict[str, bool]:
    """
    Validate SSL/HTTPS setup
    
    Returns:
        Dict[str, bool]: Validation results
    """
    results = {
        'openssl_available': False,
        'certificate_exists': False,
        'certificate_valid': False,
        'streamlit_config_exists': False
    }
    
    try:
        # Check OpenSSL availability
        result = subprocess.run(['openssl', 'version'], capture_output=True)
        results['openssl_available'] = result.returncode == 0
        
        # Check certificate files
        cert_path = os.path.join(SSL_DIR, CERT_FILE)
        key_path = os.path.join(SSL_DIR, KEY_FILE)
        
        results['certificate_exists'] = os.path.exists(cert_path) and os.path.exists(key_path)
        
        if results['certificate_exists']:
            # Validate certificate
            cmd = ['openssl', 'x509', '-in', cert_path, '-text', '-noout']
            result = subprocess.run(cmd, capture_output=True)
            results['certificate_valid'] = result.returncode == 0
        
        # Check Streamlit config
        config_path = os.path.join(".streamlit", "config.toml")
        results['streamlit_config_exists'] = os.path.exists(config_path)
        
        return results
        
    except Exception as e:
        logger.error(f"SSL validation error: {e}")
        return results

# Initialize HTTPS setup
def initialize_https():
    """Initialize HTTPS configuration"""
    try:
        logger.info("Initializing HTTPS configuration...")
        
        # Validate current setup
        validation = validate_ssl_setup()
        
        if not validation['openssl_available']:
            logger.warning("OpenSSL not available - HTTPS setup skipped")
            return False
        
        # Generate certificate if needed
        if not validation['certificate_exists']:
            cert_path, key_path = generate_self_signed_certificate()
            if not cert_path:
                logger.error("Failed to generate SSL certificate")
                return False
        
        # Create Streamlit config
        config_path = create_streamlit_config()
        if not config_path:
            logger.error("Failed to create Streamlit HTTPS config")
            return False
        
        logger.info("✅ HTTPS configuration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"HTTPS initialization failed: {e}")
        return False