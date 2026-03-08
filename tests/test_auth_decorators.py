"""Unit tests for authorization decorators"""

import pytest
from flask import session
from app.models.user import User
from app.database.db import Database


@pytest.fixture
def test_user(client, clean_users_table):
    """Create a test customer user"""
    # Create test user
    user_id = User.create('Test User', 'testuser@example.com', 'password123', role='customer')
    user = User.find_by_id(user_id)
    return user


@pytest.fixture
def test_admin(client, clean_users_table):
    """Create a test admin user"""
    # Create test admin
    user_id = User.create('Test Admin', 'testadmin@example.com', 'password123', role='admin')
    user = User.find_by_id(user_id)
    return user


class TestLoginRequiredDecorator:
    """Test cases for login_required decorator"""
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login page"""
        # Try to access protected user route without login
        response = client.get('/user/products', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_authenticated_user_can_access_protected_route(self, client, test_user):
        """Test that authenticated users can access protected routes"""
        # Login first
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.user_id
            sess['role'] = test_user.role
            sess['name'] = test_user.name
        
        # Access protected route
        response = client.get('/user/products')
        
        # Should succeed
        assert response.status_code == 200
    
    def test_flash_message_shown_on_unauthorized_access(self, client):
        """Test that flash message is shown when unauthorized user tries to access protected route"""
        # Try to access protected route without login
        response = client.get('/user/products', follow_redirects=True)
        
        # Should show flash message
        assert b'Please login to access this page' in response.data


class TestAdminRequiredDecorator:
    """Test cases for admin_required decorator"""
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login page"""
        # Try to access admin route without login
        response = client.get('/admin/dashboard', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_customer_user_denied_access_to_admin_route(self, client, test_user):
        """Test that customer users cannot access admin routes (Requirement 2.2)"""
        # Login as customer
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.user_id
            sess['role'] = test_user.role
            sess['name'] = test_user.name
        
        # Try to access admin route
        response = client.get('/admin/dashboard', follow_redirects=False)
        
        # Should redirect to customer area
        assert response.status_code == 302
        assert '/user/products' in response.location
    
    def test_admin_user_can_access_admin_route(self, client, test_admin):
        """Test that admin users can access admin routes (Requirement 2.3)"""
        # Login as admin
        with client.session_transaction() as sess:
            sess['user_id'] = test_admin.user_id
            sess['role'] = test_admin.role
            sess['name'] = test_admin.name
        
        # Access admin route
        response = client.get('/admin/dashboard')
        
        # Should succeed
        assert response.status_code == 200
    
    def test_flash_message_shown_on_customer_accessing_admin_route(self, client, test_user):
        """Test that flash message is shown when customer tries to access admin route"""
        # Login as customer
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.user_id
            sess['role'] = test_user.role
            sess['name'] = test_user.name
        
        # Try to access admin route
        response = client.get('/admin/dashboard', follow_redirects=True)
        
        # Should show flash message
        assert b'Access denied. Admin privileges required.' in response.data


class TestSessionValidation:
    """Test cases for session validation (Requirement 12.2, 12.4)"""
    
    def test_missing_session_prevents_access(self, client):
        """Test that missing session data prevents access to protected resources"""
        # Try to access protected route without any session
        response = client.get('/user/products', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_invalid_session_prevents_access(self, client):
        """Test that invalid session data prevents access"""
        # Set invalid session (missing user_id)
        with client.session_transaction() as sess:
            sess['role'] = 'customer'
            sess['name'] = 'Test'
        
        # Try to access protected route
        response = client.get('/user/products', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_valid_session_allows_access(self, client, test_user):
        """Test that valid session allows access to protected resources"""
        # Set valid session
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.user_id
            sess['role'] = test_user.role
            sess['name'] = test_user.name
        
        # Access protected route
        response = client.get('/user/products')
        
        # Should succeed
        assert response.status_code == 200
