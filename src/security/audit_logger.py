"""
Audit Logging Module - Phase 1 Security

Comprehensive logging system for tracking user actions,
security events, and system access for compliance and monitoring.
"""

import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
import inspect

# Configure audit logging
AUDIT_LOG_DIR = "logs"
AUDIT_LOG_FILE = "audit.log"
MAX_LOG_SIZE_MB = 100
BACKUP_COUNT = 5

# Ensure log directory exists
os.makedirs(AUDIT_LOG_DIR, exist_ok=True)

# Configure audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)

# Create rotating file handler
from logging.handlers import RotatingFileHandler
audit_handler = RotatingFileHandler(
    os.path.join(AUDIT_LOG_DIR, AUDIT_LOG_FILE),
    maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024,
    backupCount=BACKUP_COUNT
)

# Create formatter
audit_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)

# Event types
class AuditEventType:
    """Audit event type constants"""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_EXPORT = "DATA_EXPORT"
    FILE_UPLOAD = "FILE_UPLOAD"
    DASHBOARD_VIEW = "DASHBOARD_VIEW"
    REPORT_GENERATE = "REPORT_GENERATE"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"

class AuditLogger:
    """Centralized audit logging system"""
    
    @staticmethod
    def log_event(event_type: str, user_id: Optional[str] = None, 
                  details: Optional[Dict[str, Any]] = None, 
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None) -> None:
        """
        Log a security/audit event
        
        Args:
            event_type (str): Type of event (use AuditEventType constants)
            user_id (str, optional): User identifier
            details (Dict, optional): Additional event details
            ip_address (str, optional): Client IP address
            user_agent (str, optional): Client user agent
        """
        try:
            # Create audit record
            audit_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'event_type': event_type,
                'user_id': user_id or 'anonymous',
                'ip_address': ip_address or 'unknown',
                'user_agent': user_agent or 'unknown',
                'details': details or {},
                'session_id': AuditLogger._get_session_id()
            }
            
            # Log as JSON for structured logging
            audit_logger.info(json.dumps(audit_record))
            
        except Exception as e:
            # Fallback logging if audit logging fails
            logging.error(f"Audit logging failed: {e}")
    
    @staticmethod
    def _get_session_id() -> str:
        """Get current session ID (Streamlit specific)"""
        try:
            import streamlit as st
            return getattr(st.session_state, 'session_id', 'no_session')
        except:
            return 'no_session'
    
    @staticmethod
    def log_login_success(user_id: str, ip_address: Optional[str] = None) -> None:
        """Log successful login"""
        AuditLogger.log_event(
            AuditEventType.LOGIN_SUCCESS,
            user_id=user_id,
            ip_address=ip_address,
            details={'status': 'success'}
        )
    
    @staticmethod
    def log_login_failure(attempted_user: str, reason: str, ip_address: Optional[str] = None) -> None:
        """Log failed login attempt"""
        AuditLogger.log_event(
            AuditEventType.LOGIN_FAILURE,
            user_id=attempted_user,
            ip_address=ip_address,
            details={'reason': reason, 'status': 'failed'}
        )
    
    @staticmethod
    def log_logout(user_id: str) -> None:
        """Log user logout"""
        AuditLogger.log_event(
            AuditEventType.LOGOUT,
            user_id=user_id,
            details={'status': 'logged_out'}
        )
    
    @staticmethod
    def log_data_access(user_id: str, data_source: str, record_count: int) -> None:
        """Log data access event"""
        AuditLogger.log_event(
            AuditEventType.DATA_ACCESS,
            user_id=user_id,
            details={
                'data_source': data_source,
                'record_count': record_count,
                'action': 'data_loaded'
            }
        )
    
    @staticmethod
    def log_data_export(user_id: str, export_type: str, record_count: int, file_name: Optional[str] = None) -> None:
        """Log data export event"""
        AuditLogger.log_event(
            AuditEventType.DATA_EXPORT,
            user_id=user_id,
            details={
                'export_type': export_type,
                'record_count': record_count,
                'file_name': file_name,
                'action': 'data_exported'
            }
        )
    
    @staticmethod
    def log_file_upload(user_id: str, file_name: str, file_size: int, validation_passed: bool) -> None:
        """Log file upload event"""
        AuditLogger.log_event(
            AuditEventType.FILE_UPLOAD,
            user_id=user_id,
            details={
                'file_name': file_name,
                'file_size_bytes': file_size,
                'validation_passed': validation_passed,
                'action': 'file_uploaded'
            }
        )
    
    @staticmethod
    def log_dashboard_view(user_id: str, dashboard_section: str) -> None:
        """Log dashboard access"""
        AuditLogger.log_event(
            AuditEventType.DASHBOARD_VIEW,
            user_id=user_id,
            details={
                'dashboard_section': dashboard_section,
                'action': 'dashboard_accessed'
            }
        )
    
    @staticmethod
    def log_report_generation(user_id: str, report_type: str, record_count: int) -> None:
        """Log report generation"""
        AuditLogger.log_event(
            AuditEventType.REPORT_GENERATE,
            user_id=user_id,
            details={
                'report_type': report_type,
                'record_count': record_count,
                'action': 'report_generated'
            }
        )
    
    @staticmethod
    def log_security_violation(user_id: str, violation_type: str, details: Dict[str, Any]) -> None:
        """Log security violation"""
        AuditLogger.log_event(
            AuditEventType.SECURITY_VIOLATION,
            user_id=user_id,
            details={
                'violation_type': violation_type,
                'violation_details': details,
                'severity': 'high'
            }
        )
    
    @staticmethod
    def log_permission_denied(user_id: str, attempted_action: str, required_permission: str) -> None:
        """Log permission denied event"""
        AuditLogger.log_event(
            AuditEventType.PERMISSION_DENIED,
            user_id=user_id,
            details={
                'attempted_action': attempted_action,
                'required_permission': required_permission,
                'result': 'access_denied'
            }
        )

def audit_action(event_type: str, include_args: bool = False):
    """
    Decorator for automatic audit logging of function calls
    
    Args:
        event_type (str): Type of audit event
        include_args (bool): Whether to include function arguments in log
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Get user context
                user_id = 'system'
                try:
                    import streamlit as st
                    user_id = st.session_state.get('username', 'anonymous')
                except:
                    pass
                
                # Prepare details
                details = {
                    'function': func.__name__,
                    'module': func.__module__
                }
                
                if include_args:
                    # Safely include arguments (avoid sensitive data)
                    safe_args = []
                    for arg in args:
                        if isinstance(arg, (str, int, float, bool)):
                            safe_args.append(str(arg)[:100])  # Truncate long strings
                        else:
                            safe_args.append(type(arg).__name__)
                    details['args'] = safe_args
                    details['kwargs'] = {k: str(v)[:100] for k, v in kwargs.items()}
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Log successful execution
                details['status'] = 'success'
                AuditLogger.log_event(event_type, user_id=user_id, details=details)
                
                return result
                
            except Exception as e:
                # Log failed execution
                details['status'] = 'error'
                details['error'] = str(e)
                AuditLogger.log_event(AuditEventType.SYSTEM_ERROR, user_id=user_id, details=details)
                raise
        
        return wrapper
    return decorator

def get_audit_summary(hours: int = 24) -> Dict[str, Any]:
    """
    Get audit log summary for the last N hours
    
    Args:
        hours (int): Number of hours to look back
        
    Returns:
        Dict[str, Any]: Audit summary statistics
    """
    try:
        audit_file = os.path.join(AUDIT_LOG_DIR, AUDIT_LOG_FILE)
        if not os.path.exists(audit_file):
            return {'error': 'Audit log file not found'}
        
        # Read recent log entries
        cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
        events = []
        
        with open(audit_file, 'r') as f:
            for line in f:
                try:
                    # Parse log line
                    parts = line.strip().split(' | ')
                    if len(parts) >= 3:
                        timestamp_str = parts[0]
                        message = parts[2]
                        
                        # Try to parse as JSON
                        if message.startswith('{'):
                            event = json.loads(message)
                            event_time = datetime.fromisoformat(event['timestamp']).timestamp()
                            
                            if event_time >= cutoff_time:
                                events.append(event)
                except:
                    continue
        
        # Generate summary
        summary = {
            'total_events': len(events),
            'time_range_hours': hours,
            'event_types': {},
            'users': set(),
            'security_events': 0
        }
        
        for event in events:
            # Count event types
            event_type = event.get('event_type', 'unknown')
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            # Track users
            summary['users'].add(event.get('user_id', 'unknown'))
            
            # Count security events
            if event_type in [AuditEventType.LOGIN_FAILURE, AuditEventType.SECURITY_VIOLATION, 
                             AuditEventType.PERMISSION_DENIED]:
                summary['security_events'] += 1
        
        summary['unique_users'] = len(summary['users'])
        summary['users'] = list(summary['users'])
        
        return summary
        
    except Exception as e:
        return {'error': f'Failed to generate audit summary: {str(e)}'}

# Initialize audit logging
AuditLogger.log_event(AuditEventType.SYSTEM_ERROR, details={'message': 'Audit logging system initialized'})