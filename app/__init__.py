"""
Flask application factory module

Implements the application factory pattern for the Online Shopping System.
Initialises the database connection, registers blueprints, and sets up error
handlers.

Validates: Requirements 15.1, 15.2
"""

from flask import Flask, render_template, session
from config import config


def create_app(config_name='default'):
    """
    Create and configure a Flask application instance.

    Args:
        config_name: One of 'development', 'production', 'test', 'default'.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ------------------------------------------------------------------ #
    # Session cookie security
    # ------------------------------------------------------------------ #
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    # Secure cookies in production (HTTPS); disabled in debug/test mode
    app.config['SESSION_COOKIE_SECURE'] = not app.config.get('DEBUG', False)

    # ------------------------------------------------------------------ #
    # Database initialisation (lazy — connect on first request)
    # ------------------------------------------------------------------ #
    # We register a before_request hook so the DB connection is attempted
    # on the first actual HTTP request, not at import time. This prevents
    # the app from crashing at startup when MySQL isn't running yet, and
    # also works correctly in Vercel's serverless environment.
    from app.database.db_universal import init_db

    @app.before_request
    def ensure_db():
        from app.database.db_universal import UniversalDatabase
        if UniversalDatabase._connection is None or not UniversalDatabase._is_connection_alive():
            init_db(app.config)

    # ------------------------------------------------------------------ #
    # Blueprint registration
    # ------------------------------------------------------------------ #
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.user import user_bp
    app.register_blueprint(user_bp)

    from app.admin import admin_bp
    app.register_blueprint(admin_bp)

    # ------------------------------------------------------------------ #
    # Error handlers
    # ------------------------------------------------------------------ #
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        from app.utils.error_handler import log_error
        log_error(error, "Internal Server Error")
        return render_template('errors/500.html'), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400

    # ------------------------------------------------------------------ #
    # Home route — redirects based on authentication status and role
    # ------------------------------------------------------------------ #
    @app.route('/')
    def index():
        from flask import redirect, url_for
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            return redirect(url_for('user.browse_products'))
        return redirect(url_for('auth.login'))

    return app
