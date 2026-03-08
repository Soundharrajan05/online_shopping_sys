"""
Flask application factory module

This module implements the application factory pattern for creating Flask applications.
It initializes the database connection, registers blueprints, sets up error handlers,
and configures session management.

The factory pattern allows creating multiple application instances with different
configurations, which is useful for testing and deployment.

Validates: Requirements 15.1, 15.2
"""

from flask import Flask, render_template, session
from config import config


def create_app(config_name='default'):
    """
    Flask application factory
    
    Creates and configures a Flask application instance with the specified configuration.
    This function:
    1. Loads configuration from config module
    2. Configures secure session management
    3. Initializes database connection pool
    4. Registers blueprints (auth, user, admin)
    5. Sets up error handlers (404, 403, 500, 400)
    6. Defines home route with role-based redirection
    
    Args:
        config_name: Configuration name ('development', 'production', 'test', 'default')
                    Defaults to 'default' which maps to DevelopmentConfig
    
    Returns:
        Flask application instance configured and ready to run
    
    Example:
        app = create_app('production')
        app.run()
    
    Validates: Requirements 15.1, 15.2
    """
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration from config module
    app.config.from_object(config[config_name])
    
    # Configure session management for security
    # httponly: Prevents JavaScript access to session cookies (XSS protection)
    # samesite: Prevents CSRF attacks by restricting cross-site cookie sending
    # secure: Ensures cookies only sent over HTTPS (should be True in production)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    if not app.config.get('TESTING'):
        app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    
    # Initialize database connection pool
    # This creates a connection pool for efficient database access
    # Use universal database module that supports both MySQL and PostgreSQL
    from app.database.db_universal import init_db
    init_db(app.config)
    
    # Register blueprints for modular application structure
    # Each blueprint handles a specific area of functionality
    
    # Authentication blueprint: login, register, logout
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # User blueprint: customer-facing features (browse, cart, orders)
    from app.user import user_bp
    app.register_blueprint(user_bp)
    
    # Admin blueprint: administrator features (dashboard, management)
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # Set up error handlers for common HTTP errors
    # These provide user-friendly error pages instead of default Flask errors
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Handle 404 Not Found errors
        
        Triggered when a requested URL doesn't exist.
        Returns a custom 404 error page.
        """
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """
        Handle 403 Forbidden errors
        
        Triggered when a user tries to access a resource they don't have permission for.
        Returns a custom 403 error page.
        """
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        Handle 500 Internal Server errors
        
        Triggered when an unhandled exception occurs in the application.
        Logs the error for debugging and returns a custom 500 error page.
        """
        from app.utils.error_handler import log_error
        log_error(error, "Internal Server Error")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """
        Handle 400 Bad Request errors
        
        Triggered when the client sends a malformed request.
        Returns a custom 400 error page.
        """
        return render_template('errors/400.html'), 400
    
    # Home route - redirects based on authentication and role
    @app.route('/')
    def index():
        """
        Home route with role-based redirection
        
        Redirects users to appropriate pages based on their authentication status and role:
        - Unauthenticated users → Login page
        - Authenticated admin users → Admin dashboard
        - Authenticated customer users → Product browsing page
        
        Returns:
            Redirect response to appropriate page
        """
        from flask import redirect, url_for
        
        # Check if user is authenticated
        if 'user_id' in session:
            # Redirect based on user role
            if session.get('role') == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.browse_products'))
        
        # Not authenticated - redirect to login
        return redirect(url_for('auth.login'))
    
    return app

