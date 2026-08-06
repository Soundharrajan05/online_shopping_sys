"""
Application entry point for the Online Shopping System

This script creates and runs the Flask application using the application factory pattern.
The configuration environment can be set using the FLASK_CONFIG environment variable.

Usage:
    python run.py

Environment Variables:
    FLASK_CONFIG: Configuration environment ('development', 'production', 'test')
                  Defaults to 'development' if not set

The application will run on:
    Host: 0.0.0.0 (accessible from all network interfaces)
    Port: 5000
    Debug: Based on configuration (enabled for development/test, disabled for production)

Validates: Requirements 15.3
"""

import os
from app import create_app


# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_CONFIG') or 'development'

# Create Flask application using the factory pattern
app = create_app(config_name)


if __name__ == '__main__':
    # Run the application
    # host='0.0.0.0' makes the server accessible from other devices on the network
    # port=5000 is the default Flask port
    # debug mode is controlled by the configuration
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

