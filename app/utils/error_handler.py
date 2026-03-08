"""
Centralized error handling module

This module provides error handling functions that log errors
without exposing sensitive information to users.

Validates: Requirements 11.5
"""

import logging
import traceback
from functools import wraps
from flask import flash, redirect, url_for, render_template


# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app_errors.log'
)

logger = logging.getLogger(__name__)


def log_error(error, context=""):
    """
    Log error with full details for debugging
    
    Args:
        error: Exception object
        context: Additional context about where the error occurred
    """
    error_message = f"Error in {context}: {str(error)}"
    logger.error(error_message)
    logger.error(traceback.format_exc())


def get_user_friendly_message(error, default_message="An error occurred. Please try again."):
    """
    Convert exception to user-friendly message without exposing sensitive information
    
    Args:
        error: Exception object
        default_message: Default message to return
    
    Returns:
        User-friendly error message (string)
    """
    # Map specific error types to user-friendly messages
    error_type = type(error).__name__
    
    # Database errors
    if 'mysql' in error_type.lower() or 'database' in error_type.lower():
        return "Database error occurred. Please try again later."
    
    # Connection errors
    if 'connection' in error_type.lower():
        return "Connection error. Please check your internet connection and try again."
    
    # Value errors (often from validation)
    if error_type == 'ValueError':
        # If the error message is safe (doesn't contain sensitive info), use it
        error_str = str(error)
        if not any(keyword in error_str.lower() for keyword in ['password', 'token', 'key', 'secret', 'sql', 'query']):
            return error_str
    
    # Default safe message
    return default_message


def handle_database_error(error, context="database operation"):
    """
    Handle database errors with logging and user-friendly messages
    
    Args:
        error: Exception object
        context: Context of the operation
    
    Returns:
        User-friendly error message
    """
    log_error(error, context)
    return "A database error occurred. Please try again later."


def handle_validation_error(error, context="validation"):
    """
    Handle validation errors
    
    Args:
        error: Exception object
        context: Context of the validation
    
    Returns:
        User-friendly error message
    """
    log_error(error, context)
    error_str = str(error)
    
    # Validation errors are usually safe to show to users
    if not any(keyword in error_str.lower() for keyword in ['password', 'token', 'key', 'secret', 'sql', 'query']):
        return error_str
    
    return "Invalid input. Please check your data and try again."


def handle_authentication_error(error, context="authentication"):
    """
    Handle authentication errors
    
    Args:
        error: Exception object
        context: Context of the authentication
    
    Returns:
        User-friendly error message
    """
    log_error(error, context)
    return "Authentication failed. Please check your credentials and try again."


def handle_authorization_error(error, context="authorization"):
    """
    Handle authorization errors
    
    Args:
        error: Exception object
        context: Context of the authorization
    
    Returns:
        User-friendly error message
    """
    log_error(error, context)
    return "You do not have permission to perform this action."


def safe_database_operation(operation_name):
    """
    Decorator to wrap database operations with error handling
    
    Args:
        operation_name: Name of the operation for logging
    
    Usage:
        @safe_database_operation("create user")
        def create_user(name, email, password):
            # database operations
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error(e, f"{operation_name} - {func.__name__}")
                raise  # Re-raise to let caller handle
        return wrapper
    return decorator


def safe_route_handler(redirect_url=None, error_message=None):
    """
    Decorator to wrap route handlers with error handling
    
    Args:
        redirect_url: URL to redirect to on error (optional)
        error_message: Custom error message (optional)
    
    Usage:
        @app.route('/some-route')
        @safe_route_handler(redirect_url='index', error_message='Failed to load page')
        def some_route():
            # route logic
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error with full details
                log_error(e, f"route handler - {func.__name__}")
                
                # Get user-friendly message
                user_message = error_message or get_user_friendly_message(e)
                flash(user_message, 'error')
                
                # Redirect if URL provided
                if redirect_url:
                    return redirect(url_for(redirect_url))
                
                # Otherwise render error page
                return render_template('error.html', error_message=user_message), 500
        
        return wrapper
    return decorator


def sanitize_error_for_display(error):
    """
    Sanitize error message to ensure no sensitive information is exposed
    
    Args:
        error: Exception object or error string
    
    Returns:
        Sanitized error message safe for display
    """
    error_str = str(error)
    
    # List of sensitive keywords that should not appear in user-facing messages
    sensitive_keywords = [
        'password', 'token', 'key', 'secret', 'api_key',
        'sql', 'query', 'database', 'connection',
        'traceback', 'stack', 'file', 'line',
        'mysql', 'root', 'admin', 'localhost',
        'exception', 'error at', 'failed at'
    ]
    
    # Check if error contains sensitive information
    error_lower = error_str.lower()
    for keyword in sensitive_keywords:
        if keyword in error_lower:
            return "An error occurred. Please try again or contact support."
    
    # If no sensitive info, return the error (truncated if too long)
    if len(error_str) > 200:
        return error_str[:200] + "..."
    
    return error_str


class SafeError(Exception):
    """
    Custom exception class for errors that are safe to display to users
    
    Use this for validation errors and business logic errors that don't
    contain sensitive information.
    """
    pass


class DatabaseError(Exception):
    """
    Custom exception class for database errors
    
    These errors will be logged with full details but shown to users
    with a generic message.
    """
    pass


class AuthenticationError(Exception):
    """
    Custom exception class for authentication errors
    """
    pass


class AuthorizationError(Exception):
    """
    Custom exception class for authorization errors
    """
    pass
