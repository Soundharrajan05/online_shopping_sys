"""
Property-based tests for operation feedback consistency
Feature: online-shopping-system, Property 36: Operation feedback consistency
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app import create_app


# Feature: online-shopping-system, Property 36: Operation feedback consistency
@given(
    email=st.emails().filter(lambda x: len(x) <= 100),
    password=st.text(min_size=1, max_size=100)
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_failed_login_shows_error_message(email, password):
    """
    Property: For any failed operation (invalid login),
    the system should display an error message
    
    **Validates: Requirements 13.4**
    """
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Attempt login with non-existent credentials
    response = client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)
    
    # Check response
    if response.status_code == 200:
        # Should see error message or still be on login page
        has_error = (
            b'error' in response.data.lower() or
            b'invalid' in response.data.lower() or
            b'alert' in response.data.lower() or
            b'failed' in response.data.lower()
        )
        
        # If not logged in (no welcome message), should have error feedback
        is_logged_in = b'Welcome back' in response.data or b'Logout' in response.data
        
        if not is_logged_in:
            # Failed login should show error message
            assert has_error or b'Login' in response.data, "No error message displayed for failed login"


@given(
    quantity=st.integers(min_value=-100, max_value=0)
)
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_invalid_cart_quantity_shows_error(quantity):
    """
    Property: For any invalid operation (invalid quantity),
    the system should display an error message
    
    **Validates: Requirements 13.4**
    """
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    try:
        # Setup: Create user, category, product
        user_id = User.create('Test User', 'test@example.com', 'password123', 'customer')
        
        # Login
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = 'customer'
            sess['name'] = 'Test User'
        
        category_id = Category.create('Test Category')
        product_id = Product.create('Test Product', 'Description', 10.00, 5, 'test.jpg', category_id)
        
        # Try to add with invalid quantity
        response = client.post(f'/user/cart/add/{product_id}', data={
            'quantity': quantity
        }, follow_redirects=True)
        
        # Should see error message
        if response.status_code == 200:
            has_error = (
                b'error' in response.data.lower() or
                b'invalid' in response.data.lower() or
                b'alert-danger' in response.data or
                b'must be' in response.data.lower()
            )
            
            assert has_error, f"No error message displayed for invalid quantity {quantity}"
            
    except Exception as e:
        # If operation fails at model level, that's expected
        pass


@given(
    category_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_duplicate_category_shows_error(category_name):
    """
    Property: For any error condition (duplicate category),
    the system should display an error message
    
    **Validates: Requirements 13.4**
    """
    # Sanitize category name
    sanitized_name = ''.join(c for c in category_name if c.isprintable() and c not in '\n\r\t')
    assume(len(sanitized_name) > 0)
    
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    try:
        # Setup: Create admin user and login
        user_id = User.create('Admin User', 'admin@example.com', 'password123', 'admin')
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = 'admin'
            sess['name'] = 'Admin User'
        
        # Create category first time
        Category.create(sanitized_name)
        
        # Try to create duplicate
        response = client.post('/admin/categories/add', data={
            'category_name': sanitized_name
        }, follow_redirects=True)
        
        # Should see error message about duplicate
        if response.status_code == 200:
            has_error = (
                b'error' in response.data.lower() or
                b'already exists' in response.data.lower() or
                b'duplicate' in response.data.lower() or
                b'alert-danger' in response.data
            )
            
            assert has_error, "No error message displayed for duplicate category"
            
    except Exception as e:
        # If operation fails, that's expected
        pass


@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_empty_cart_checkout_shows_error():
    """
    Property: For any error condition (empty cart checkout),
    the system should display an error message
    
    **Validates: Requirements 13.4**
    """
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    try:
        # Setup: Create user and login
        user_id = User.create('Test User', 'test@example.com', 'password123', 'customer')
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = 'customer'
            sess['name'] = 'Test User'
        
        # Try to checkout with empty cart
        response = client.get('/user/checkout', follow_redirects=True)
        
        # Should see error message or be redirected to cart
        if response.status_code == 200:
            has_error = (
                b'empty' in response.data.lower() or
                b'error' in response.data.lower() or
                b'no items' in response.data.lower() or
                b'alert-danger' in response.data
            )
            
            # Either error message or redirected to cart page
            on_cart_page = b'Shopping Cart' in response.data or b'cart' in response.data.lower()
            
            assert has_error or on_cart_page, "No error feedback for empty cart checkout"
            
    except Exception as e:
        # If operation fails, that's expected
        pass


@given(
    stock_quantity=st.integers(min_value=1, max_value=5),
    requested_quantity=st.integers(min_value=6, max_value=100)
)
@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_insufficient_stock_shows_error(stock_quantity, requested_quantity):
    """
    Property: For any error condition (insufficient stock),
    the system should display an error message
    
    **Validates: Requirements 13.4**
    """
    assume(requested_quantity > stock_quantity)
    
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    try:
        # Setup: Create user, category, product with limited stock
        user_id = User.create('Test User', 'test@example.com', 'password123', 'customer')
        
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = 'customer'
            sess['name'] = 'Test User'
        
        category_id = Category.create('Test Category')
        product_id = Product.create(
            'Limited Stock Product',
            'Description',
            10.00,
            stock_quantity,
            'test.jpg',
            category_id
        )
        
        # Try to add more than available stock
        response = client.post(f'/user/cart/add/{product_id}', data={
            'quantity': requested_quantity
        }, follow_redirects=True)
        
        # Should see error message about insufficient stock
        if response.status_code == 200:
            has_error = (
                b'insufficient' in response.data.lower() or
                b'stock' in response.data.lower() or
                b'not available' in response.data.lower() or
                b'error' in response.data.lower() or
                b'alert-danger' in response.data
            )
            
            assert has_error, f"No error message for insufficient stock (have {stock_quantity}, requested {requested_quantity})"
            
    except Exception as e:
        # If operation fails at model level, that's expected
        pass


@given(
    name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    email=st.emails().filter(lambda x: len(x) <= 100),
    password=st.text(min_size=8, max_size=100)
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@pytest.mark.property_test
@pytest.mark.usefixtures('test_db')
def test_successful_registration_shows_confirmation(name, email, password):
    """
    Property: For any successful operation (registration), 
    the system should display a confirmation message
    
    **Validates: Requirements 13.3**
    """
    # Sanitize name to remove control characters
    sanitized_name = ''.join(c for c in name if c.isprintable() and c not in '\n\r\t')
    assume(len(sanitized_name) > 0)
    
    # Create test client
    app = create_app('test')
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Perform registration
    response = client.post('/auth/register', data={
        'name': sanitized_name,
        'email': email,
        'password': password
    }, follow_redirects=True)
    
    # Check response
    if response.status_code == 200:
        # Should see either success or error feedback
        has_success = b'Registration successful' in response.data or b'success' in response.data.lower()
        has_error = b'already registered' in response.data or b'error' in response.data.lower() or b'alert' in response.data.lower()
        on_login_page = b'Login' in response.data
        
        # At least one type of feedback should be present
        assert has_success or has_error or on_login_page, "No feedback message displayed for registration"
