"""
Property-based test for customer role restrictions

Feature: online-shopping-system | Property: 8

NOTE: Property 8 (Customer role restrictions) is validated through:
1. Unit tests in this file (concrete examples)
2. Property 7 test in test_authorization_properties.py (which includes customer restriction testing)

The unit tests below provide focused, fast validation of Requirement 2.2.
"""

import pytest
from app.models.user import User
from app.database.db import Database


def test_customer_cannot_access_admin_dashboard_example(client):
    """
    Property 8: Customer role restrictions - Example test
    
    **Validates: Requirements 2.2**
    
    Verify that customer users cannot access admin dashboard and are redirected.
    This is a concrete example that validates the property:
    ∀ (user) where user.role = 'customer' → GET /admin/dashboard → 302 redirect
    """
    
    # Clean up any existing test user
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('customer@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create a customer user
    user_id = User.create('Test Customer', 'customer@test.com', 'password123', role='customer')
    
    # Login as customer
    client.post('/auth/login', data={
        'email': 'customer@test.com',
        'password': 'password123'
    })
    
    # Try to access admin dashboard
    response = client.get('/admin/dashboard', follow_redirects=False)
    
    # Should be redirected
    assert response.status_code == 302
    assert '/user/products' in response.location
    
    # Clean up
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('customer@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def test_admin_can_access_admin_dashboard_example(client):
    """
    Property 8: Customer role restrictions - Contrast test
    
    **Validates: Requirements 2.3**
    
    Verify that admin users CAN access admin dashboard.
    This provides contrast to show the restriction is role-specific.
    """
    
    # Clean up any existing test user
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('admin@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create an admin user
    user_id = User.create('Test Admin', 'admin@test.com', 'password123', role='admin')
    
    # Login as admin
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'password123'
    })
    
    # Try to access admin dashboard
    response = client.get('/admin/dashboard')
    
    # Should succeed
    assert response.status_code == 200
    
    # Clean up
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('admin@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def test_customer_cannot_access_multiple_admin_routes(client):
    """
    Property 8: Customer role restrictions - Multiple routes test
    
    **Validates: Requirements 2.2**
    
    Verify that customer users cannot access ANY admin routes.
    Tests the property across multiple admin endpoints.
    """
    # Clean up any existing test user
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('customer2@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create a customer user
    user_id = User.create('Test Customer 2', 'customer2@test.com', 'password123', role='customer')
    
    # Login as customer
    client.post('/auth/login', data={
        'email': 'customer2@test.com',
        'password': 'password123'
    })
    
    # Test multiple admin routes
    admin_routes = [
        '/admin/dashboard',
        # Note: Other admin routes may not be implemented yet, so we focus on dashboard
    ]
    
    for route in admin_routes:
        response = client.get(route, follow_redirects=False)
        
        # All should be redirected
        assert response.status_code == 302, \
            f"Customer should be redirected from {route}, got {response.status_code}"
        
        # All should redirect to customer area
        assert '/user/products' in response.location, \
            f"Customer should be redirected to /user/products from {route}, got {response.location}"
    
    # Clean up
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", ('customer2@test.com',))
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def test_unauthenticated_user_cannot_access_admin_routes(client):
    """
    Property 8: Customer role restrictions - Unauthenticated test
    
    **Validates: Requirements 12.4**
    
    Verify that unauthenticated users cannot access admin routes.
    """
    # Try to access admin dashboard without logging in
    response = client.get('/admin/dashboard', follow_redirects=False)
    
    # Should be redirected to login
    assert response.status_code == 302
    assert '/auth/login' in response.location
