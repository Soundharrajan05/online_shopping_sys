"""
Property-based tests for authorization and role-based access control

Feature: online-shopping-system
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.user import User
from app.database.db import Database
from app import create_app


# Strategy for generating valid user names (1-100 characters, not empty)
valid_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'), min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)

# Strategy for generating valid email addresses
# Filter to ensure emails pass the application's email validation
import re
def is_valid_app_email(email):
    """Check if email passes the application's validation"""
    if len(email) > 100:
        return False
    # Basic email regex that matches the application's validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

valid_emails = st.emails().filter(is_valid_app_email)

# Strategy for generating valid passwords (at least 8 characters)
valid_passwords = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=8,
    max_size=50
)

# Strategy for generating user roles
user_roles = st.sampled_from(['customer', 'admin'])


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    name=valid_names,
    email=valid_emails,
    password=valid_passwords,
    role=user_roles
)
@pytest.mark.usefixtures('setup_test_database')
def test_property_role_based_access_control(name, email, password, role):
    """
    Property 7: Role-based access control
    
    **Validates: Requirements 2.1, 2.4**
    
    For any user, the assigned role should be either 'customer' or 'admin',
    and access to routes should be restricted based on this role.
    
    This property verifies:
    1. Users can only have valid roles ('customer' or 'admin')
    2. Session stores the user's role (Requirement 2.4)
    3. Admin routes reject customer users
    4. Admin routes allow admin users
    5. Customer routes allow authenticated users
    
    Property: ∀ (user, role) where role ∈ {'customer', 'admin'} →
              - user.role ∈ {'customer', 'admin'}
              - session['role'] = user.role after login
              - if role = 'customer' → admin_routes return 302 redirect
              - if role = 'admin' → admin_routes return 200 OK
              - if authenticated → customer_routes return 200 OK
    """
    # Clean the users table before this example
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create Flask test client for this example
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    client = app.test_client()
    
    # Arrange: Create a user with the specified role
    user_id = User.create(name, email, password, role=role)
    assert user_id is not None, "User creation should succeed"
    
    # Retrieve the created user to verify role assignment
    created_user = User.find_by_id(user_id)
    assert created_user is not None, "User should exist in database"
    
    # Property 1: User role must be either 'customer' or 'admin' (Requirement 2.1)
    assert created_user.role in ['customer', 'admin'], \
        f"User role must be 'customer' or 'admin', got '{created_user.role}'"
    
    # Property 2: User role should match the assigned role
    assert created_user.role == role, \
        f"User role should be '{role}', got '{created_user.role}'"
    
    # Act: Login with the created user
    response = client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=False)
    
    # Assert: Login should succeed
    assert response.status_code in [302, 303], \
        f"Login should redirect on success, got status {response.status_code}"
    
    # Property 3: Session should store the user's role (Requirement 2.4)
    with client.session_transaction() as sess:
        assert 'role' in sess, \
            "Session should contain role after successful login (Requirement 2.4)"
        assert sess['role'] == role, \
            f"Session role should be '{role}', got '{sess.get('role')}'"
        assert sess['user_id'] == user_id, \
            f"Session user_id should be {user_id}, got {sess.get('user_id')}"
    
    # Property 4: Test access control based on role
    if role == 'customer':
        # Customer users should NOT be able to access admin routes (Requirement 2.2)
        admin_response = client.get('/admin/dashboard', follow_redirects=False)
        
        assert admin_response.status_code == 302, \
            f"Customer should be redirected from admin routes, got status {admin_response.status_code}"
        
        assert '/user/products' in admin_response.location, \
            f"Customer should be redirected to customer area, got {admin_response.location}"
        
        # Customer users SHOULD be able to access customer routes
        customer_response = client.get('/user/products')
        
        assert customer_response.status_code == 200, \
            f"Customer should access customer routes, got status {customer_response.status_code}"
    
    elif role == 'admin':
        # Admin users SHOULD be able to access admin routes (Requirement 2.3)
        admin_response = client.get('/admin/dashboard')
        
        assert admin_response.status_code == 200, \
            f"Admin should access admin routes, got status {admin_response.status_code}"
        
        # Admin users SHOULD also be able to access customer routes
        # (admins have all permissions)
        customer_response = client.get('/user/products')
        
        assert customer_response.status_code == 200, \
            f"Admin should access customer routes, got status {customer_response.status_code}"
    
    # Clean up after this example
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
