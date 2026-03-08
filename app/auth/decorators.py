"""Authorization decorators for protecting routes"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorator to require authentication
    
    Checks if user_id exists in session. If not authenticated,
    redirects to login page with a flash message.
    
    Usage:
        @login_required
        def protected_route():
            # Route logic here
    
    Validates: Requirements 11.4, 12.2, 12.4
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to require admin role
    
    Checks if user_id exists in session AND role is 'admin'.
    If not authenticated, redirects to login page.
    If authenticated but not admin, redirects to customer area.
    
    Usage:
        @admin_required
        def admin_route():
            # Admin route logic here
    
    Validates: Requirements 2.2, 2.3, 11.4, 12.2, 12.4
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('user.browse_products'))
        
        return f(*args, **kwargs)
    return decorated_function
