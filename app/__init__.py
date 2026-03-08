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
    
    # Add products endpoint
    @app.route('/add-products')
    def add_products():
        """Add sample products to database"""
        from app.database.db_universal import Database
        
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Check if products already exist
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            
            if count > 0:
                cursor.close()
                Database.release_connection(conn)
                return f'<strong style="color: orange;">Products already exist ({count} products)</strong><br><br><a href="/test-db">Check database status</a><br><a href="/user/products">Browse products</a>'
            
            # Add products
            products = [
                ('HP Victus Gaming Laptop', 1, 899.99, 25, 'High-performance gaming laptop', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500'),
                ('Dell XPS 13', 1, 1299.99, 15, 'Premium ultrabook', 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500'),
                ('iPhone 14 Pro', 1, 999.99, 50, 'Latest iPhone model', 'https://images.unsplash.com/photo-1678652197831-2d180705cd2c?w=500'),
                ('Samsung Galaxy S23', 1, 899.99, 40, 'Flagship Android phone', 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500'),
                ('Clean Code by Robert Martin', 2, 44.99, 50, 'Software engineering book', 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500'),
                ('The Pragmatic Programmer', 2, 49.99, 30, 'Programming best practices', 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500'),
                ('Men\'s T-Shirt', 3, 19.99, 100, 'Comfortable cotton t-shirt', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500'),
                ('Women\'s Dress', 3, 59.99, 50, 'Elegant summer dress', 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500'),
                ('Sony WH-1000XM5', 1, 399.99, 20, 'Noise-cancelling headphones', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500'),
                ('MacBook Pro 14"', 1, 1999.99, 10, 'Apple laptop for professionals', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'),
            ]
            
            for name, cat_id, price, stock, desc, img in products:
                cursor.execute("""
                    INSERT INTO products (product_name, category_id, price, stock_quantity, description, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, cat_id, price, stock, desc, img))
            
            conn.commit()
            cursor.close()
            Database.release_connection(conn)
            
            return f'<strong style="color: green;">✓ Successfully added {len(products)} products!</strong><br><br><a href="/test-db">Check database status</a><br><a href="/user/products">Browse products</a>'
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc().replace('\n', '<br>')
            return f'<strong style="color: red;">Error adding products:</strong><br>{str(e)}<br><br><pre>{error_trace}</pre>', 500
    
    return app

