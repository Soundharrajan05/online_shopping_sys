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
        
        # Test 3: Users (show ALL users)
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            results.append(f"<br>✓ Users table has {count} users")
            
            if count > 0:
                cursor.execute("SELECT user_id, email, role, name FROM users ORDER BY user_id")
                users = cursor.fetchall()
                results.append("<br><strong>All users:</strong>")
                for user_id, email, role, name in users:
                    results.append(f"&nbsp;&nbsp;{user_id}. {email} ({role}) - {name}")
            
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Users table check failed: {str(e)}")
        
        # Test 4: Categories
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM categories")
            cat_count = cursor.fetchone()[0]
            results.append(f"<br>✓ Categories: {cat_count}")
            
            if cat_count > 0:
                cursor.execute("SELECT category_id, category_name FROM categories")
                categories = cursor.fetchall()
                for cat_id, cat_name in categories:
                    results.append(f"&nbsp;&nbsp;{cat_id}. {cat_name}")
            else:
                results.append("&nbsp;&nbsp;<a href='/add-products'>Click to add categories and products</a>")
            
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Categories check failed: {str(e)}")
        
        # Test 5: Products
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM products")
            prod_count = cursor.fetchone()[0]
            results.append(f"<br>✓ Products: {prod_count}")
            
            if prod_count == 0:
                results.append("&nbsp;&nbsp;<a href='/add-products'>Click to add products</a>")
            
            cursor.close()
            Database.release_connection(conn)
        except Exception as e:
            results.append(f"✗ Products check failed: {str(e)}")
        
        results.append("<br><br><strong>Quick Links:</strong>")
        results.append("<a href='/add-products'>Add Products</a> | <a href='/auth/login'>Login</a> | <a href='/auth/register'>Register</a>")
        
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
    
    # Debug login endpoint
    @app.route('/debug-login')
    def debug_login():
        """Debug login issues - test password verification"""
        from app.database.db_universal import Database
        from werkzeug.security import check_password_hash
        
        results = []
        results.append("<h2>Login Debug Tool</h2>")
        
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Get all users with their password hashes
            cursor.execute("SELECT user_id, email, password, role, name FROM users ORDER BY user_id")
            users = cursor.fetchall()
            
            results.append(f"<p>Found {len(users)} users in database:</p>")
            
            for user_id, email, password_hash, role, name in users:
                results.append(f"<hr><strong>User {user_id}:</strong> {email}")
                results.append(f"<br>Name: {name}")
                results.append(f"<br>Role: {role}")
                results.append(f"<br>Password hash: {password_hash[:50]}...")
                
                # Test common passwords
                test_passwords = ['customer123', 'admin123', 'password', '123456']
                for test_pwd in test_passwords:
                    if check_password_hash(password_hash, test_pwd):
                        results.append(f"<br><span style='color: green;'>✓ Password is: {test_pwd}</span>")
                        break
                else:
                    results.append(f"<br><span style='color: red;'>✗ Password is NOT any of: {', '.join(test_passwords)}</span>")
            
            cursor.close()
            Database.release_connection(conn)
            
            results.append("<hr><h3>Test Login:</h3>")
            results.append("<p>Try these credentials:</p>")
            results.append("<ul>")
            results.append("<li>customer@test.com / customer123</li>")
            results.append("<li>admin@shop.com / admin123</li>")
            results.append("</ul>")
            results.append("<a href='/auth/login'>Go to Login Page</a>")
            
        except Exception as e:
            import traceback
            results.append(f"<p style='color: red;'>Error: {str(e)}</p>")
            results.append(f"<pre>{traceback.format_exc()}</pre>")
        
        return "<br>".join(results)
    
    # Add products endpoint
    @app.route('/add-products')
    def add_products():
        """Add sample categories and products to database"""
        from app.database.db_universal import Database
        
        try:
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            results = []
            
            # Step 1: Add categories first
            cursor.execute("SELECT COUNT(*) FROM categories")
            cat_count = cursor.fetchone()[0]
            
            if cat_count == 0:
                results.append("Adding categories...")
                categories = [
                    ('Electronics',),
                    ('Books',),
                    ('Clothing',)
                ]
                
                for (name,) in categories:
                    cursor.execute(
                        "INSERT INTO categories (category_name) VALUES (%s)",
                        (name,)
                    )
                conn.commit()
                results.append(f"✓ Added {len(categories)} categories")
            else:
                results.append(f"✓ Categories already exist ({cat_count} categories)")
            
            # Step 2: Check if products already exist
            cursor.execute("SELECT COUNT(*) FROM products")
            prod_count = cursor.fetchone()[0]
            
            if prod_count > 0:
                cursor.close()
                Database.release_connection(conn)
                results.append(f"✓ Products already exist ({prod_count} products)")
                html = '<br>'.join(results)
                html += '<br><br><a href="/test-db">Check database status</a><br><a href="/user/products">Browse products</a>'
                return html
            
            # Step 3: Add products
            results.append("Adding products...")
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
            
            results.append(f"✓ Added {len(products)} products")
            results.append("<br><strong style='color: green;'>✓ Setup complete!</strong>")
            
            html = '<br>'.join(results)
            html += '<br><br><a href="/test-db">Check database status</a><br><a href="/user/products">Browse products</a>'
            return html
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc().replace('\n', '<br>')
            return f'<strong style="color: red;">Error adding products:</strong><br>{str(e)}<br><br><pre>{error_trace}</pre>', 500
    
    # Debug registration endpoint
    @app.route('/debug-register', methods=['GET', 'POST'])
    def debug_register():
        """Debug registration issues"""
        from app.database.db_universal import Database
        from werkzeug.security import generate_password_hash
        
        if request.method == 'POST':
            email = request.form.get('email', '')
            password = request.form.get('password', 'test123')
            name = request.form.get('name', 'Test User')
            
            results = []
            results.append(f"<h2>Registration Debug</h2>")
            results.append(f"<p>Attempting to register: {email}</p>")
            
            try:
                # Check if email exists
                conn = Database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT user_id, email FROM users WHERE email = %s", (email,))
                existing = cursor.fetchone()
                
                if existing:
                    results.append(f"<p style='color: red;'>✗ Email already exists: User ID {existing[0]}</p>")
                else:
                    results.append(f"<p style='color: green;'>✓ Email is available</p>")
                    
                    # Try to create user
                    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                    results.append(f"<p>✓ Password hashed successfully</p>")
                    
                    cursor.execute("""
                        INSERT INTO users (name, email, password, role)
                        VALUES (%s, %s, %s, %s)
                        RETURNING user_id
                    """, (name, email, hashed_password, 'customer'))
                    
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    results.append(f"<p style='color: green;'>✓ User created successfully! User ID: {user_id}</p>")
                    results.append(f"<p>Login with: {email} / {password}</p>")
                    results.append(f"<a href='/auth/login'>Go to Login</a>")
                
                cursor.close()
                Database.release_connection(conn)
                
            except Exception as e:
                import traceback
                results.append(f"<p style='color: red;'>✗ Error: {str(e)}</p>")
                results.append(f"<pre>{traceback.format_exc()}</pre>")
            
            return "<br>".join(results)
        
        # GET request - show form
        return """
        <h2>Debug Registration</h2>
        <form method="POST">
            <p>
                <label>Email:</label><br>
                <input type="email" name="email" required placeholder="test@example.com" style="width: 300px; padding: 5px;">
            </p>
            <p>
                <label>Name:</label><br>
                <input type="text" name="name" value="Test User" style="width: 300px; padding: 5px;">
            </p>
            <p>
                <label>Password:</label><br>
                <input type="text" name="password" value="test123" style="width: 300px; padding: 5px;">
            </p>
            <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;">
                Test Registration
            </button>
        </form>
        <hr>
        <p><a href="/test-db">Check Database Status</a></p>
        """
    
    return app

