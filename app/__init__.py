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
    
    # Test endpoint to check database status (for debugging)
    @app.route('/test-db')
    def test_db():
        """Test database connection and tables - for debugging only"""
        from app.database.db_universal import Database
        
        results = []
        
        # Test 1: Connection
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            results.append(f"✓ Database connected: {version[:50]}")
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Connection failed: {str(e)}")
            return "<br>".join(results), 500
        
        # Test 2: Tables
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                results.append(f"✓ Found {len(tables)} tables: {', '.join(tables)}")
            else:
                results.append("✗ No tables found! <a href='/init-db'>Click here to initialize database</a>")
            
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Table check failed: {str(e)}")
        
        # Test 3: Users
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            results.append(f"✓ Users table has {count} users")
            
            if count > 0:
                cursor.execute("SELECT email, role FROM users LIMIT 5")
                users = cursor.fetchall()
                results.append(f"Sample users: {', '.join([f'{email} ({role})' for email, role in users])}")
            
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Users table check failed: {str(e)}")
        
        return "<br>".join(results)
    
    # Manual database initialization endpoint (for free tier without Shell)
    @app.route('/init-db')
    def init_db_manual():
        """Manually initialize database - for free tier users without Shell access"""
        try:
            from auto_init_db import main as auto_init
            
            # Capture output
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            # Run initialization
            success = auto_init()
            
            # Get output
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            # Format output for HTML
            html_output = output.replace('\n', '<br>').replace(' ', '&nbsp;')
            
            if success:
                html_output += '<br><br><strong style="color: green;">✓ Database initialized successfully!</strong>'
                html_output += '<br><br><a href="/test-db">Check database status</a>'
                html_output += '<br><a href="/auth/register">Go to registration</a>'
            else:
                html_output += '<br><br><strong style="color: red;">✗ Initialization failed!</strong>'
                html_output += '<br><br><a href="/test-db">Check database status</a>'
            
            return html_output
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc().replace('\n', '<br>')
            return f'<strong style="color: red;">Error:</strong><br>{str(e)}<br><br><pre>{error_trace}</pre>', 500
    
    return app

