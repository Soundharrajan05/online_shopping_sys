"""
Property-based tests for session validation

Feature: online-shopping-system
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app


# Strategy for generating protected route paths
# These are the routes that require authentication
protected_user_routes = st.sampled_from([
    '/user/products',
    '/user/cart',
    '/user/orders'
])

protected_admin_routes = st.sampled_from([
    '/admin/dashboard'
])

# Combined strategy for all protected routes
all_protected_routes = st.one_of(protected_user_routes, protected_admin_routes)


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(route=all_protected_routes)
def test_property_session_validation_protects_resources(route):
    """
    Property 6: Session validation protects resources
    
    **Validates: Requirements 12.2, 12.4**
    
    For any protected route, requests without valid session data should be 
    rejected and redirected to login.
    
    This property verifies:
    1. Protected routes validate session before processing (Requirement 12.2)
    2. Unauthenticated requests are redirected to login page (Requirement 12.4)
    3. No protected operations are processed without valid session
    
    Property: ∀ (route) where route is protected →
              - GET route without session → 302 redirect
              - redirect location = '/auth/login'
              - no protected operations executed
    """
    # Create Flask test client for this example
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    client = app.test_client()
    
    # Act: Try to access protected route without authentication
    # Ensure no session data exists
    with client.session_transaction() as sess:
        sess.clear()
    
    response = client.get(route, follow_redirects=False)
    
    # Assert: Request should be rejected with redirect (Requirement 12.2)
    assert response.status_code == 302, \
        f"Protected route {route} should redirect unauthenticated requests, got status {response.status_code}"
    
    # Assert: Redirect should point to login page (Requirement 12.4)
    assert '/auth/login' in response.location, \
        f"Unauthenticated request to {route} should redirect to login, got {response.location}"


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    route=all_protected_routes,
    invalid_session_data=st.dictionaries(
        keys=st.text(min_size=1, max_size=20).filter(lambda x: x not in ['user_id', 'role']),
        values=st.one_of(st.integers(), st.text(), st.booleans()),
        min_size=0,
        max_size=5
    )
)
def test_property_session_validation_rejects_invalid_sessions(route, invalid_session_data):
    """
    Property 6: Session validation protects resources (invalid session variant)
    
    **Validates: Requirements 12.2, 12.4**
    
    For any protected route, requests with invalid or incomplete session data 
    (missing user_id) should be rejected and redirected to login.
    
    This property verifies:
    1. Session validation checks for required fields (user_id)
    2. Invalid sessions are treated as unauthenticated
    3. Partial session data doesn't grant access
    
    Property: ∀ (route, session_data) where route is protected ∧ 'user_id' ∉ session_data →
              - GET route with invalid session → 302 redirect
              - redirect location = '/auth/login'
    """
    # Create Flask test client for this example
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    client = app.test_client()
    
    # Act: Set invalid session data (without user_id)
    with client.session_transaction() as sess:
        sess.clear()
        sess.update(invalid_session_data)
        # Ensure user_id is NOT in session
        if 'user_id' in sess:
            del sess['user_id']
    
    response = client.get(route, follow_redirects=False)
    
    # Assert: Request should be rejected with redirect
    assert response.status_code == 302, \
        f"Protected route {route} should redirect requests with invalid session, got status {response.status_code}"
    
    # Assert: Redirect should point to login page
    assert '/auth/login' in response.location, \
        f"Invalid session request to {route} should redirect to login, got {response.location}"


def test_session_validation_example_user_route(client):
    """
    Property 6: Session validation protects resources - Example test for user routes
    
    **Validates: Requirements 12.2, 12.4**
    
    Concrete example: Unauthenticated request to /user/products should redirect to login.
    """
    # Ensure no session exists
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try to access user products page
    response = client.get('/user/products', follow_redirects=False)
    
    # Should be redirected to login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_session_validation_example_admin_route(client):
    """
    Property 6: Session validation protects resources - Example test for admin routes
    
    **Validates: Requirements 12.2, 12.4**
    
    Concrete example: Unauthenticated request to /admin/dashboard should redirect to login.
    """
    # Ensure no session exists
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try to access admin dashboard
    response = client.get('/admin/dashboard', follow_redirects=False)
    
    # Should be redirected to login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_session_validation_example_cart_route(client):
    """
    Property 6: Session validation protects resources - Example test for cart route
    
    **Validates: Requirements 12.2, 12.4**
    
    Concrete example: Unauthenticated request to /user/cart should redirect to login.
    """
    # Ensure no session exists
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try to access cart page
    response = client.get('/user/cart', follow_redirects=False)
    
    # Should be redirected to login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_session_validation_example_orders_route(client):
    """
    Property 6: Session validation protects resources - Example test for orders route
    
    **Validates: Requirements 12.2, 12.4**
    
    Concrete example: Unauthenticated request to /user/orders should redirect to login.
    """
    # Ensure no session exists
    with client.session_transaction() as sess:
        sess.clear()
    
    # Try to access orders page
    response = client.get('/user/orders', follow_redirects=False)
    
    # Should be redirected to login
    assert response.status_code == 302
    assert '/auth/login' in response.location
