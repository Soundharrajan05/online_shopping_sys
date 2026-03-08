"""Integration tests for category management routes"""

import pytest
from app.models.category import Category
from app.models.user import User


def test_manage_categories_route_requires_admin(client, test_db):
    """
    Test that manage_categories route requires admin authentication
    
    Validates: Requirements 2.2, 11.4
    """
    # Without login - should redirect to login
    response = client.get('/admin/categories')
    assert response.status_code == 302, "Should redirect when not logged in"
    assert '/login' in response.location, "Should redirect to login page"
    
    # With customer login - should deny access
    customer_id = User.create("Customer User", "customer@test.com", "password123", "customer")
    customer = User.find_by_id(customer_id)
    
    with client.session_transaction() as sess:
        sess['user_id'] = customer.user_id
        sess['role'] = 'customer'
        sess['name'] = customer.name
    
    response = client.get('/admin/categories')
    assert response.status_code == 302, "Should redirect customer away from admin area"


def test_manage_categories_route_with_admin(client, test_db):
    """
    Test that admin can access manage_categories route
    
    Validates: Requirements 2.3, 7.2
    """
    # Create admin user
    admin_id = User.create("Admin User", "admin@test.com", "password123", "admin")
    admin = User.find_by_id(admin_id)
    
    # Login as admin
    with client.session_transaction() as sess:
        sess['user_id'] = admin.user_id
        sess['role'] = 'admin'
        sess['name'] = admin.name
    
    # Access categories page
    response = client.get('/admin/categories')
    assert response.status_code == 200, "Admin should access categories page"
    assert b'Manage Categories' in response.data, "Page should show categories management"


def test_add_category_route(client, test_db):
    """
    Test adding a new category through the route
    
    Validates: Requirements 7.1, 7.3
    """
    # Create admin user
    admin_id = User.create("Admin User", "admin@test.com", "password123", "admin")
    admin = User.find_by_id(admin_id)
    
    # Login as admin
    with client.session_transaction() as sess:
        sess['user_id'] = admin.user_id
        sess['role'] = 'admin'
        sess['name'] = admin.name
    
    # Add new category
    response = client.post('/admin/categories/add', data={
        'category_name': 'Electronics'
    }, follow_redirects=True)
    
    assert response.status_code == 200, "Should successfully add category"
    assert b'added successfully' in response.data, "Should show success message"
    
    # Verify category was created
    assert Category.exists('Electronics'), "Category should exist in database"


def test_add_duplicate_category_route(client, test_db):
    """
    Test that duplicate category names are rejected through the route
    
    Validates: Requirement 7.3
    """
    # Create admin user
    admin_id = User.create("Admin User", "admin@test.com", "password123", "admin")
    admin = User.find_by_id(admin_id)
    
    # Login as admin
    with client.session_transaction() as sess:
        sess['user_id'] = admin.user_id
        sess['role'] = 'admin'
        sess['name'] = admin.name
    
    # Add first category
    Category.create('Electronics')
    
    # Try to add duplicate
    response = client.post('/admin/categories/add', data={
        'category_name': 'Electronics'
    }, follow_redirects=True)
    
    assert response.status_code == 200, "Should handle duplicate gracefully"
    assert b'already exists' in response.data, "Should show error message for duplicate"


def test_add_empty_category_name(client, test_db):
    """
    Test that empty category names are rejected
    
    Validates: Requirement 11.1
    """
    # Create admin user
    admin_id = User.create("Admin User", "admin@test.com", "password123", "admin")
    admin = User.find_by_id(admin_id)
    
    # Login as admin
    with client.session_transaction() as sess:
        sess['user_id'] = admin.user_id
        sess['role'] = 'admin'
        sess['name'] = admin.name
    
    # Try to add empty category
    response = client.post('/admin/categories/add', data={
        'category_name': '   '
    }, follow_redirects=True)
    
    assert response.status_code == 200, "Should handle empty name gracefully"
    assert b'required' in response.data, "Should show error message for empty name"
