"""Pytest configuration and fixtures for testing"""

import pytest
from app.database.db import Database
from config import TestConfig
from app import create_app


@pytest.fixture(scope='session')
def setup_test_database():
    """
    Initialize test database connection pool for database tests
    This fixture runs once per test session when explicitly requested
    """
    config = {
        'DB_HOST': TestConfig.DB_HOST,
        'DB_USER': TestConfig.DB_USER,
        'DB_PASSWORD': TestConfig.DB_PASSWORD,
        'DB_NAME': TestConfig.DB_NAME,
        'DB_POOL_SIZE': TestConfig.DB_POOL_SIZE
    }
    Database.init_db(config)
    yield
    # Cleanup after all tests complete


@pytest.fixture(scope='function')
def clean_users_table(setup_test_database):
    """
    Clean users table before each test
    This ensures test isolation
    Requires setup_test_database fixture
    """
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        # Delete all users from test database
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    yield
    
    # Clean up after test
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@pytest.fixture(scope='function')
def client(setup_test_database):
    """
    Create Flask test client for testing routes and sessions
    This fixture provides a test client with session support
    """
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(scope='function')
def test_db(setup_test_database):
    """
    Clean all tables before each test for complete isolation
    This fixture ensures a fresh database state for each test
    """
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        # Clean all tables in reverse order of dependencies
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM cart")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    yield
    
    # Clean up after test
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM order_items")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM cart")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()

