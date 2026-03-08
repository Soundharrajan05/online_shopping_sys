"""
Property-based tests for authentication module

Feature: online-shopping-system
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.user import User
from werkzeug.security import check_password_hash


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


@settings(max_examples=20, deadline=None)
@given(
    name=valid_names,
    email=valid_emails,
    password=valid_passwords
)
@pytest.mark.usefixtures('clean_users_table')
def test_property_user_registration_creates_customer_accounts(name, email, password):
    """
    Property 1: User registration creates customer accounts
    
    **Validates: Requirements 1.1, 1.5**
    
    For any valid registration data (name, email, password), creating a new user account
    should result in a user record with role='customer' and a hashed password that does
    not match the plaintext password.
    
    Property: ∀ (name, email, password) where valid(name, email, password) →
              User.create(name, email, password) creates user with:
              - role = 'customer'
              - stored_password ≠ plaintext_password
              - check_password_hash(stored_password, plaintext_password) = True
    """
    # Make email unique to avoid collisions across test examples
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"[:100]
    
    # Act: Create a new user with the generated data
    user_id = User.create(name, unique_email, password, role='customer')
    
    # Assert: User was created successfully
    assert user_id is not None, "User creation should return a valid user ID"
    assert user_id > 0, "User ID should be a positive integer"
    
    # Retrieve the created user from database
    created_user = User.find_by_id(user_id)
    
    # Assert: User exists in database
    assert created_user is not None, "Created user should be retrievable from database"
    
    # Assert: User has correct role
    assert created_user.role == 'customer', \
        f"User role should be 'customer', but got '{created_user.role}'"
    
    # Assert: User has correct name and email
    assert created_user.name == name, \
        f"User name should be '{name}', but got '{created_user.name}'"
    assert created_user.email == unique_email, \
        f"User email should be '{unique_email}', but got '{created_user.email}'"
    
    # Assert: Password is hashed (not stored as plaintext)
    assert created_user.password != password, \
        "Password should be hashed, not stored as plaintext"
    
    # Assert: Hashed password can be verified
    assert check_password_hash(created_user.password, password), \
        "Hashed password should verify correctly against original password"
    
    # Assert: Password hash is not empty
    assert len(created_user.password) > 0, \
        "Password hash should not be empty"
    
    # Assert: Password hash looks like a proper hash (contains hash algorithm prefix)
    assert created_user.password.startswith('pbkdf2:sha256:'), \
        "Password should be hashed using pbkdf2:sha256 algorithm"


@settings(max_examples=20, deadline=None)
@given(
    name=valid_names,
    email=valid_emails,
    password=valid_passwords
)
@pytest.mark.usefixtures('clean_users_table')
def test_property_password_hashing_is_irreversible(name, email, password):
    """
    Property 2: Password hashing is irreversible
    
    **Validates: Requirements 1.5**
    
    For any user in the database, the stored password hash should never equal
    the plaintext password. This ensures passwords are properly hashed and not
    stored in plaintext, making them irreversible.
    
    Property: ∀ (user, plaintext_password) →
              user.stored_password ≠ plaintext_password
    """
    # Make email unique to avoid collisions across test examples
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"[:100]
    
    # Act: Create a new user with the generated password
    user_id = User.create(name, unique_email, password, role='customer')
    
    # Assert: User was created successfully
    assert user_id is not None, "User creation should return a valid user ID"
    
    # Retrieve the created user from database
    created_user = User.find_by_id(user_id)
    
    # Assert: User exists in database
    assert created_user is not None, "Created user should be retrievable from database"
    
    # Assert: Stored password never equals plaintext password (irreversibility)
    assert created_user.password != password, \
        f"Stored password hash should NEVER equal plaintext password. " \
        f"This indicates password is not being hashed properly."
    
    # Assert: Password hash is significantly different from plaintext
    # (hashes should be much longer and contain different characters)
    assert len(created_user.password) > len(password), \
        "Password hash should be longer than plaintext password"
    
    # Assert: Password hash contains hash algorithm identifier
    assert 'pbkdf2:sha256:' in created_user.password, \
        "Password hash should contain algorithm identifier, confirming it's hashed"
    
    # Assert: Even if we create another user with the same password,
    # the hashes should be different (due to salt)
    # This further proves irreversibility and proper hashing
    different_email = f"{uuid.uuid4().hex[:8]}_different_{email}"[:100]
    user_id_2 = User.create(name, different_email, password, role='customer')
    created_user_2 = User.find_by_id(user_id_2)
    
    # The same password should produce different hashes (salted hashing)
    assert created_user.password != created_user_2.password, \
        "Same password should produce different hashes due to salting"
    
    # But both should verify correctly against the original password
    assert check_password_hash(created_user.password, password), \
        "First user's password hash should verify correctly"
    assert check_password_hash(created_user_2.password, password), \
        "Second user's password hash should verify correctly"


@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    name=valid_names,
    email=valid_emails,
    password=valid_passwords
)
@pytest.mark.usefixtures('setup_test_database')
def test_property_valid_login_creates_authenticated_session(name, email, password):
    """
    Property 3: Valid login creates authenticated session
    
    **Validates: Requirements 1.3, 12.1**
    
    For any registered user with correct credentials, logging in should create
    a session containing user_id and role. This ensures proper session management
    and authentication state tracking.
    
    Property: ∀ (user, correct_credentials) →
              login(user, correct_credentials) creates session with:
              - session['user_id'] = user.user_id
              - session['role'] = user.role
    """
    from app import create_app
    from app.database.db import Database
    
    # Make email unique to avoid collisions across test examples
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"[:100]
    
    # Clean the users table before this example
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", (unique_email,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create Flask test client for this example
    app = create_app('test')
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    client = app.test_client()
    
    # Arrange: Create a user in the database
    user_id = User.create(name, unique_email, password, role='customer')
    assert user_id is not None, "User creation should succeed"
    
    # Retrieve the created user to verify
    created_user = User.find_by_id(user_id)
    assert created_user is not None, "User should exist in database"
    
    # Act: Attempt to login with valid credentials
    response = client.post('/auth/login', data={
        'email': unique_email,
        'password': password
    }, follow_redirects=False)
    
    # Assert: Login should succeed (redirect to appropriate page)
    assert response.status_code in [302, 303], \
        f"Login should redirect on success, got status {response.status_code}"
    
    # Assert: Session should be created with user_id
    with client.session_transaction() as sess:
        assert 'user_id' in sess, \
            "Session should contain user_id after successful login"
        assert sess['user_id'] == user_id, \
            f"Session user_id should be {user_id}, got {sess.get('user_id')}"
        
        # Assert: Session should contain role
        assert 'role' in sess, \
            "Session should contain role after successful login"
        assert sess['role'] == 'customer', \
            f"Session role should be 'customer', got {sess.get('role')}"
        
        # Assert: Session should contain user name
        assert 'name' in sess, \
            "Session should contain user name after successful login"
        assert sess['name'] == name, \
            f"Session name should be '{name}', got {sess.get('name')}"
    
    # Assert: Redirect location should be appropriate for customer role
    assert response.location is not None, "Redirect location should be set"
    # Customer should be redirected to browse products
    assert 'browse_products' in response.location or '/user/' in response.location, \
        f"Customer should be redirected to product browsing, got {response.location}"
    
    # Clean up after this example
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE email = %s", (unique_email,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
