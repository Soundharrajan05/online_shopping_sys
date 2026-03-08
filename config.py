"""
Configuration module for the Online Shopping System

This module defines configuration classes for different environments:
- Development: Local development with debug mode enabled
- Production: Production deployment with security hardening
- Test: Testing environment with separate test database

Environment variables can be set in .env file or system environment.

Required environment variables for production:
- SECRET_KEY: Flask secret key for session management
- DB_HOST: MySQL database host
- DB_USER: MySQL database user
- DB_PASSWORD: MySQL database password
- DB_NAME: MySQL database name

Validates: Requirements 15.4
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class
    
    Contains common configuration settings shared across all environments.
    Other configuration classes inherit from this base class.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    
    # Database configuration
    # Support both DATABASE_URL (Render.com) and individual variables (local)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'shopping_system'
    DB_POOL_SIZE = 5


class DevelopmentConfig(Config):
    """
    Development configuration
    
    Used for local development with debug mode enabled.
    Uses default database 'shopping_system'.
    """
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """
    Production configuration
    
    Used for production deployment with security hardening.
    Requires SECRET_KEY environment variable to be set.
    Debug mode is disabled for security.
    """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production


class TestConfig(Config):
    """
    Test configuration
    
    Used for running automated tests.
    Uses separate test database 'shopping_system_test' to avoid
    interfering with development or production data.
    """
    DEBUG = True
    TESTING = True
    DB_NAME = 'shopping_system_test'


# Configuration dictionary mapping names to configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}

