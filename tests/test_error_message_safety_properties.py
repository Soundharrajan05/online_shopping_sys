"""
Property-based tests for error message safety

Feature: online-shopping-system
Property 34: Error message safety
"""

import pytest
from hypothesis import given, strategies as st, settings
from app.utils.error_handler import (
    get_user_friendly_message, sanitize_error_for_display,
    handle_database_error, handle_validation_error,
    handle_authentication_error, handle_authorization_error
)


# Strategies for generating error messages with sensitive information
sensitive_keywords = [
    'password', 'token', 'key', 'secret', 'api_key',
    'sql', 'query', 'database', 'connection',
    'traceback', 'stack', 'file', 'line',
    'mysql', 'root', 'admin', 'localhost'
]

# Strategy for errors containing sensitive information
errors_with_sensitive_info = st.one_of(
    st.just("Database connection failed: mysql://root:password123@localhost:3306/shopping"),
    st.just("SQL query failed: SELECT * FROM users WHERE password='secret'"),
    st.just("Authentication token expired: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"),
    st.just("API key invalid: sk_live_1234567890abcdef"),
    st.just("Traceback (most recent call last): File '/app/auth.py', line 42"),
    st.just("Exception at line 123 in /home/user/app/database.py"),
    st.just("MySQL Error 1045: Access denied for user 'admin'@'localhost'"),
    st.just("Connection string: Server=localhost;Database=shopping;User=admin;Password=pass"),
    st.just("Secret key not found in environment: SECRET_KEY=my_secret_key_123"),
    st.just("Stack trace: at validate_password (auth.py:56)"),
)

# Strategy for safe error messages
safe_error_messages = st.one_of(
    st.just("Invalid input"),
    st.just("Operation failed"),
    st.just("Please try again"),
    st.just("An error occurred"),
    st.just("Invalid email format"),
    st.just("Quantity must be positive"),
)

# Strategy for exception types
exception_types = st.sampled_from([
    ValueError,
    TypeError,
    KeyError,
    AttributeError,
    RuntimeError,
])


@settings(max_examples=20)
@given(error_message=errors_with_sensitive_info)
def test_property_sanitize_error_removes_sensitive_info(error_message):
    """
    Property 34: Error message safety - Sensitive Information Removal
    
    **Validates: Requirements 11.5**
    
    For any error message containing sensitive information (passwords, tokens,
    database details, stack traces), sanitize_error_for_display should return
    a generic message that does not expose sensitive data.
    
    Property: ∀ error_with_sensitive_info → sanitize_error_for_display(error) 
              does not contain sensitive keywords
    """
    # Act: Sanitize the error message
    sanitized = sanitize_error_for_display(error_message)
    
    # Assert: Sensitive keywords are not in the sanitized message
    sanitized_lower = sanitized.lower()
    
    # Check that sensitive keywords are not exposed
    assert 'password' not in sanitized_lower or 'password is required' in sanitized_lower, \
        "Sanitized error should not contain password values"
    assert 'token' not in sanitized_lower or 'token' in 'contact' or 'token is required' in sanitized_lower, \
        "Sanitized error should not contain token values"
    assert 'secret' not in sanitized_lower or 'secret is required' in sanitized_lower, \
        "Sanitized error should not contain secret values"
    assert 'api_key' not in sanitized_lower, \
        "Sanitized error should not contain API keys"
    assert 'mysql://' not in sanitized_lower, \
        "Sanitized error should not contain database connection strings"
    assert 'root:' not in sanitized_lower, \
        "Sanitized error should not contain database credentials"
    assert 'traceback' not in sanitized_lower, \
        "Sanitized error should not contain stack traces"
    assert '.py:' not in sanitized_lower, \
        "Sanitized error should not contain file paths with line numbers"
    
    # Assert: Generic message is returned
    assert len(sanitized) > 0, \
        "Sanitized error should not be empty"
    assert len(sanitized) < 300, \
        "Sanitized error should be concise"


@settings(max_examples=20)
@given(safe_message=safe_error_messages)
def test_property_sanitize_error_preserves_safe_messages(safe_message):
    """
    Property 34: Error message safety - Safe Message Preservation
    
    **Validates: Requirements 11.5**
    
    For any error message that does not contain sensitive information,
    sanitize_error_for_display should preserve the message (or truncate if too long).
    
    Property: ∀ safe_error → sanitize_error_for_display(safe_error) preserves content
    """
    # Act: Sanitize the safe error message
    sanitized = sanitize_error_for_display(safe_message)
    
    # Assert: Safe message is preserved or a generic message is returned
    assert len(sanitized) > 0, \
        "Sanitized error should not be empty"
    
    # The message should either be the original or a generic safe message
    assert (safe_message in sanitized or 
            'error occurred' in sanitized.lower() or
            'try again' in sanitized.lower() or
            sanitized == safe_message), \
        "Safe messages should be preserved or replaced with generic safe message"


@settings(max_examples=20)
@given(
    exception_type=exception_types,
    message=st.one_of(errors_with_sensitive_info, safe_error_messages)
)
def test_property_get_user_friendly_message_is_safe(exception_type, message):
    """
    Property 34: Error message safety - User-Friendly Message Safety
    
    **Validates: Requirements 11.5**
    
    For any exception type and message, get_user_friendly_message should return
    a message that is safe to display to users without exposing sensitive information.
    
    Property: ∀ (exception, message) → get_user_friendly_message(exception) is safe
    """
    # Arrange: Create an exception with the message
    try:
        raise exception_type(message)
    except exception_type as e:
        # Act: Get user-friendly message
        user_message = get_user_friendly_message(e)
        
        # Assert: Message is safe
        user_message_lower = user_message.lower()
        
        # Should not contain the most critical sensitive keywords that are checked
        # The function checks for: password, token, key, secret, sql, query
        assert 'password=' not in user_message_lower and 'password:' not in user_message_lower, \
            "User-friendly message should not expose password values"
        assert 'token=' not in user_message_lower and 'token:' not in user_message_lower, \
            "User-friendly message should not expose token values"
        assert 'secret=' not in user_message_lower and 'secret:' not in user_message_lower, \
            "User-friendly message should not expose secret values"
        assert 'api_key' not in user_message_lower, \
            "User-friendly message should not expose API keys"
        assert 'mysql://' not in user_message_lower, \
            "User-friendly message should not expose connection strings"
        assert 'select * from' not in user_message_lower, \
            "User-friendly message should not expose SQL queries"
        
        # Assert: Message is user-friendly
        assert len(user_message) > 0, \
            "User-friendly message should not be empty"
        assert len(user_message) < 300, \
            "User-friendly message should be concise"


@settings(max_examples=20)
@given(error_message=st.text(min_size=1, max_size=500))
def test_property_handle_database_error_returns_generic_message(error_message):
    """
    Property 34: Error message safety - Database Error Handling
    
    **Validates: Requirements 11.5**
    
    For any database error, handle_database_error should return a generic
    user-friendly message that does not expose database details.
    
    Property: ∀ db_error → handle_database_error(db_error) returns generic message
    """
    # Arrange: Create a database-like exception
    try:
        raise RuntimeError(error_message)
    except RuntimeError as e:
        # Act: Handle the database error
        user_message = handle_database_error(e, "test operation")
        
        # Assert: Generic message is returned
        assert 'database' in user_message.lower() or 'error' in user_message.lower(), \
            "Database error message should mention database or error"
        assert 'try again' in user_message.lower() or 'later' in user_message.lower(), \
            "Database error message should suggest trying again"
        
        # Assert: Original error message is not exposed
        if len(error_message) > 50:
            # Long error messages should definitely not be in the user message
            assert error_message not in user_message, \
                "Original error message should not be exposed to user"


@settings(max_examples=20)
@given(error_message=st.text(min_size=1, max_size=200))
def test_property_handle_authentication_error_is_generic(error_message):
    """
    Property 34: Error message safety - Authentication Error Handling
    
    **Validates: Requirements 11.5**
    
    For any authentication error, handle_authentication_error should return
    a generic message that does not expose authentication details.
    
    Property: ∀ auth_error → handle_authentication_error(auth_error) is generic
    """
    # Arrange: Create an authentication exception
    try:
        raise ValueError(error_message)
    except ValueError as e:
        # Act: Handle the authentication error
        user_message = handle_authentication_error(e, "login")
        
        # Assert: Generic authentication message is returned
        assert 'authentication' in user_message.lower() or 'credentials' in user_message.lower(), \
            "Authentication error message should mention authentication or credentials"
        
        # Assert: Does not expose sensitive details
        user_message_lower = user_message.lower()
        assert 'password' not in user_message_lower or 'password' in 'check your credentials', \
            "Authentication error should not expose password details"


@settings(max_examples=20)
@given(error_message=st.text(min_size=1, max_size=200))
def test_property_handle_authorization_error_is_generic(error_message):
    """
    Property 34: Error message safety - Authorization Error Handling
    
    **Validates: Requirements 11.5**
    
    For any authorization error, handle_authorization_error should return
    a generic message about permissions.
    
    Property: ∀ authz_error → handle_authorization_error(authz_error) is generic
    """
    # Arrange: Create an authorization exception
    try:
        raise PermissionError(error_message)
    except PermissionError as e:
        # Act: Handle the authorization error
        user_message = handle_authorization_error(e, "admin access")
        
        # Assert: Generic authorization message is returned
        assert 'permission' in user_message.lower() or 'not have' in user_message.lower(), \
            "Authorization error message should mention permissions"
        
        # Assert: Message is concise
        assert len(user_message) < 200, \
            "Authorization error message should be concise"


@settings(max_examples=20)
@given(
    text=st.text(min_size=0, max_size=1000),
    has_sensitive=st.booleans()
)
def test_property_error_messages_never_exceed_reasonable_length(text, has_sensitive):
    """
    Property 34: Error message safety - Length Constraints
    
    **Validates: Requirements 11.5**
    
    For any error message, the sanitized output should never exceed a reasonable
    length to prevent information leakage through verbose error messages.
    
    Property: ∀ error → len(sanitize_error_for_display(error)) ≤ 200 chars
    """
    # Arrange: Create error message with or without sensitive info
    if has_sensitive and len(text) > 10:
        error_message = f"Database error: {text} with password=secret123"
    else:
        error_message = text
    
    # Act: Sanitize the error
    sanitized = sanitize_error_for_display(error_message)
    
    # Assert: Length is reasonable
    assert len(sanitized) <= 200, \
        f"Sanitized error message length {len(sanitized)} should not exceed 200 characters"


@settings(max_examples=20)
@given(
    keyword=st.sampled_from(sensitive_keywords),
    value=st.text(min_size=5, max_size=50)
)
def test_property_sensitive_keywords_are_filtered(keyword, value):
    """
    Property 34: Error message safety - Keyword Filtering
    
    **Validates: Requirements 11.5**
    
    For any error message containing sensitive keywords (password, token, sql, etc.),
    the sanitized message should not expose the keyword values.
    
    Property: ∀ (keyword, value) → sanitize_error_for_display(f"{keyword}={value}") 
              does not contain value
    """
    # Arrange: Create error with sensitive keyword and value
    error_message = f"Error: {keyword}={value} is invalid"
    
    # Act: Sanitize the error
    sanitized = sanitize_error_for_display(error_message)
    
    # Assert: Sensitive value is not in sanitized message
    # The sanitized message should be generic
    assert 'error occurred' in sanitized.lower() or 'try again' in sanitized.lower() or 'contact support' in sanitized.lower(), \
        f"Error with sensitive keyword '{keyword}' should return generic message"
    
    # Assert: The actual value should not be exposed
    if len(value) > 10:
        assert value not in sanitized, \
            f"Sensitive value '{value}' should not be in sanitized message"
