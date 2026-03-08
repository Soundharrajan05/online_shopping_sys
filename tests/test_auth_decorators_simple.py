"""Simple unit tests for authorization decorators without database dependency"""

import pytest
from flask import Flask, session, Blueprint
from app.auth.decorators import login_required, admin_required


@pytest.fixture
def app():
    """Create minimal test application"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Create mock auth blueprint
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
    
    @auth_bp.route('/login')
    def login():
        from flask import get_flashed_messages
        messages = get_flashed_messages()
        return 'Login page' + ''.join(messages)
    
    # Create mock user blueprint
    user_bp = Blueprint('user', __name__, url_prefix='/user')
    
    @user_bp.route('/products')
    def browse_products():
        from flask import get_flashed_messages
        messages = get_flashed_messages()
        return 'Browse products page' + ''.join(messages)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    # Create test routes using the decorators
    @app.route('/protected')
    @login_required
    def protected_route():
        return 'Protected content'
    
    @app.route('/admin')
    @admin_required
    def admin_route():
        return 'Admin content'
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestLoginRequiredDecorator:
    """Test cases for login_required decorator"""
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login page (Requirement 12.4)"""
        response = client.get('/protected', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_authenticated_user_can_access_protected_route(self, client):
        """Test that authenticated users can access protected routes (Requirement 12.2)"""
        # Set session to simulate logged-in user
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'customer'
            sess['name'] = 'Test User'
        
        response = client.get('/protected')
        
        # Should succeed
        assert response.status_code == 200
        assert b'Protected content' in response.data
    
    def test_flash_message_shown_on_unauthorized_access(self, client):
        """Test that flash message is shown when unauthorized user tries to access protected route"""
        response = client.get('/protected', follow_redirects=True)
        
        # Should show flash message
        assert b'Please login to access this page' in response.data


class TestAdminRequiredDecorator:
    """Test cases for admin_required decorator"""
    
    def test_unauthenticated_user_redirected_to_login(self, client):
        """Test that unauthenticated users are redirected to login page (Requirement 12.4)"""
        response = client.get('/admin', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_customer_user_denied_access_to_admin_route(self, client):
        """Test that customer users cannot access admin routes (Requirement 2.2)"""
        # Set session to simulate logged-in customer
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'customer'
            sess['name'] = 'Test Customer'
        
        response = client.get('/admin', follow_redirects=False)
        
        # Should redirect to customer area
        assert response.status_code == 302
        assert '/user/products' in response.location
    
    def test_admin_user_can_access_admin_route(self, client):
        """Test that admin users can access admin routes (Requirement 2.3)"""
        # Set session to simulate logged-in admin
        with client.session_transaction() as sess:
            sess['user_id'] = 2
            sess['role'] = 'admin'
            sess['name'] = 'Test Admin'
        
        response = client.get('/admin')
        
        # Should succeed
        assert response.status_code == 200
        assert b'Admin content' in response.data
    
    def test_flash_message_shown_on_customer_accessing_admin_route(self, client):
        """Test that flash message is shown when customer tries to access admin route"""
        # Set session to simulate logged-in customer
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'customer'
            sess['name'] = 'Test Customer'
        
        response = client.get('/admin', follow_redirects=True)
        
        # Should show flash message
        assert b'Access denied. Admin privileges required.' in response.data


class TestSessionValidation:
    """Test cases for session validation (Requirement 11.4, 12.2, 12.4)"""
    
    def test_missing_session_prevents_access(self, client):
        """Test that missing session data prevents access to protected resources"""
        response = client.get('/protected', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_invalid_session_prevents_access(self, client):
        """Test that invalid session data prevents access"""
        # Set invalid session (missing user_id)
        with client.session_transaction() as sess:
            sess['role'] = 'customer'
            sess['name'] = 'Test'
        
        response = client.get('/protected', follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code == 302
        assert '/auth/login' in response.location
    
    def test_valid_session_allows_access(self, client):
        """Test that valid session allows access to protected resources"""
        # Set valid session
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['role'] = 'customer'
            sess['name'] = 'Test User'
        
        response = client.get('/protected')
        
        # Should succeed
        assert response.status_code == 200
        assert b'Protected content' in response.data
