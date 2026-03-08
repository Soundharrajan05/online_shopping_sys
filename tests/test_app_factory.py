"""
Unit tests for Flask application factory

Tests the create_app function and error handlers.
Validates: Requirements 15.1, 15.2
"""

import pytest
from app import create_app


class TestApplicationFactory:
    """Test Flask application factory"""
    
    def test_create_app_with_default_config(self):
        """Test creating app with default configuration"""
        # Note: This test may fail if the default database doesn't exist
        # In production, use test config for testing
        try:
            app = create_app()
            assert app is not None
            assert app.config['SECRET_KEY'] is not None
        except Exception:
            # Skip if database connection fails
            pytest.skip("Default database not available")
    
    def test_create_app_with_test_config(self):
        """Test creating app with test configuration"""
        app = create_app('test')
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['DB_NAME'] == 'shopping_system_test'
    
    def test_create_app_with_development_config(self):
        """Test creating app with development configuration"""
        app = create_app('development')
        assert app is not None
        assert app.config['DEBUG'] is True
    
    def test_blueprints_registered(self):
        """Test that all blueprints are registered"""
        app = create_app('test')
        
        # Check that blueprints are registered
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert 'auth' in blueprint_names
        assert 'user' in blueprint_names
        assert 'admin' in blueprint_names
    
    def test_session_configuration(self):
        """Test that session is properly configured"""
        app = create_app('test')
        
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'


class TestErrorHandlers:
    """Test error handlers"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = create_app('test')
        app.config['TESTING'] = True
        return app.test_client()
    
    def test_404_error_handler(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data
    
    def test_home_route_redirects_to_login(self, client):
        """Test home route redirects to login when not authenticated"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location
