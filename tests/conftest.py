"""Pytest configuration and shared fixtures for the test suite."""

import pytest
# db.py now re-exports from db_universal, so both import paths share one pool
from app.database.db import Database
from config import TestConfig
from app import create_app


@pytest.fixture(scope='session')
def setup_test_database():
    """
    Initialise the MySQL connection pool for the test session.
    Uses the 'test' config (shopping_system_test database).
    """
    config = {
        'DB_HOST': TestConfig.DB_HOST,
        'DB_USER': TestConfig.DB_USER,
        'DB_PASSWORD': TestConfig.DB_PASSWORD,
        'DB_NAME': TestConfig.DB_NAME,
        'DB_POOL_SIZE': 5,
    }
    # Reset any existing connection so tests always start fresh
    Database._connection = None
    Database.init_db(config)
    yield
    # Nothing to tear down — connection is reused across tests


@pytest.fixture(scope='function')
def clean_users_table(setup_test_database):
    """Truncate the users table before and after each test."""
    _truncate_users()
    yield
    _truncate_users()


def _truncate_users():
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()


@pytest.fixture(scope='function')
def client(setup_test_database):
    """Flask test client with session support."""
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client


@pytest.fixture(scope='function')
def test_db(setup_test_database):
    """Wipe all tables before and after each test for full isolation."""
    _truncate_all()
    yield
    _truncate_all()


def _truncate_all():
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
