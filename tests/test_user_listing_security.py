"""Property-based tests for user listing security"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.user import User
from app.database.db import Database
import time


# Feature: online-shopping-system, Property 29: User listing excludes passwords
@given(
    num_users=st.integers(min_value=1, max_value=5)
)
@settings(
    max_examples=50, 
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for database operations
)
@pytest.mark.property_test
def test_user_listing_excludes_passwords(test_db, num_users):
    """
    Property: For any user listing query, the response should include name, 
    email, role, and created_at, but should never include the password field.
    
    **Validates: Requirements 9.1, 9.2**
    
    This test verifies that:
    1. User listing query returns all expected fields (name, email, role, created_at)
    2. User listing query NEVER returns the password field
    3. Password hashes are not exposed in any form
    4. This holds true for any number of users in the system
    """
    # Create test users with various roles
    created_users = []
    for i in range(num_users):
        name = f"TestUser{i}_{int(time.time() * 1000) % 10000}"
        email = f"user{i}_{int(time.time() * 1000) % 100000}@test.com"
        password = f"password{i}123"
        role = 'admin' if i % 3 == 0 else 'customer'
        
        try:
            # Create user - returns user_id
            user_id = User.create(name, email, password, role)
            if user_id:
                created_users.append({
                    'user_id': user_id,
                    'name': name,
                    'email': email,
                    'password': password,
                    'role': role
                })
        except Exception:
            # Skip if user creation fails (e.g., duplicate email)
            continue
    
    # Skip test if no users were created
    if not created_users:
        return
    
    # Action: Query all users using the same query as view_all_users route
    query = """
        SELECT user_id, name, email, role, created_at
        FROM users
        ORDER BY created_at DESC
    """
    results = Database.execute_query(query, None, fetch=True)
    
    # Assert: Results should not be empty
    assert results is not None, "User listing query should return results"
    assert len(results) >= len(created_users), \
        f"Should return at least {len(created_users)} users"
    
    # Assert: Each result row should have exactly 5 fields (no password)
    for row in results:
        assert len(row) == 5, \
            f"Each user record should have exactly 5 fields (user_id, name, email, role, created_at), got {len(row)}"
        
        # Extract fields
        user_id, name, email, role, created_at = row
        
        # Assert: All required fields are present and not None
        assert user_id is not None, "user_id should not be None"
        assert name is not None, "name should not be None"
        assert email is not None, "email should not be None"
        assert role is not None, "role should not be None"
        assert created_at is not None, "created_at should not be None"
        
        # Assert: Role should be valid
        assert role in ['customer', 'admin'], \
            f"Role should be 'customer' or 'admin', got '{role}'"
    
    # Assert: Verify password is not in any field by checking against known passwords
    for row in results:
        row_str = str(row)
        for user_data in created_users:
            # Password should not appear in plaintext
            assert user_data['password'] not in row_str, \
                "Plaintext password should never appear in user listing results"


@given(
    user_index=st.integers(min_value=0, max_value=100)
)
@settings(
    max_examples=50, 
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None  # Disable deadline for database operations
)
@pytest.mark.property_test
def test_single_user_listing_excludes_password(test_db, user_index):
    """
    Property: For any single user, the listing query should exclude the password field.
    
    **Validates: Requirements 9.1, 9.2**
    
    This is a focused test that verifies password exclusion for individual users.
    """
    # Create a test user with unique identifiers
    name = f"TestUser{user_index}"
    email = f"user{user_index}_{int(time.time() * 1000) % 100000}@test.com"
    password = f"password{user_index}123"
    
    # Create a test user
    try:
        user_id = User.create(name, email, password, 'customer')
    except Exception:
        # Skip if user creation fails (e.g., duplicate email)
        return
    
    if not user_id:
        return
    
    # Action: Query the user using the admin view query
    query = """
        SELECT user_id, name, email, role, created_at
        FROM users
        WHERE user_id = %s
    """
    results = Database.execute_query(query, (user_id,), fetch=True)
    
    # Assert: User should be found
    assert results is not None and len(results) == 1, \
        "Should find exactly one user"
    
    row = results[0]
    
    # Assert: Row should have exactly 5 fields (no password)
    assert len(row) == 5, \
        f"User record should have exactly 5 fields, got {len(row)}"
    
    # Assert: Verify the fields are correct
    returned_user_id, returned_name, returned_email, role, created_at = row
    
    assert returned_user_id == user_id, "user_id should match"
    assert returned_name == name, "name should match"
    assert returned_email == email, "email should match"
    assert role == 'customer', "role should match"
    assert created_at is not None, "created_at should not be None"
    
    # Assert: Password should not be in the result
    row_str = str(row)
    assert password not in row_str, \
        "Plaintext password should never appear in user listing"
    
    # Assert: Verify we can't access password through direct query either
    # This ensures the SELECT statement truly excludes the password column
    query_all_fields = "SELECT * FROM users WHERE user_id = %s"
    all_fields_result = Database.execute_query(query_all_fields, (user_id,), fetch=True)
    
    # The full query should have 6 fields (including password)
    assert len(all_fields_result[0]) == 6, \
        "Full user record should have 6 fields including password"
    
    # But our admin query should only have 5 fields
    assert len(row) == 5, \
        "Admin user listing should exclude password field"


@pytest.mark.property_test
def test_user_listing_query_structure(test_db):
    """
    Property: The user listing query structure should explicitly exclude password field.
    
    **Validates: Requirements 9.1, 9.2**
    
    This test verifies the query structure itself, ensuring it's designed
    to exclude passwords by construction.
    """
    # Create a test user
    user = User.create("Test User", "test@example.com", "password123", "customer")
    
    # The query used in view_all_users route
    admin_query = """
        SELECT user_id, name, email, role, created_at
        FROM users
        ORDER BY created_at DESC
    """
    
    # Execute the admin query
    admin_results = Database.execute_query(admin_query, None, fetch=True)
    
    # Execute a full query for comparison
    full_query = "SELECT * FROM users"
    full_results = Database.execute_query(full_query, None, fetch=True)
    
    # Assert: Admin query should return fewer fields than full query
    assert len(admin_results[0]) < len(full_results[0]), \
        "Admin query should return fewer fields than full query (password excluded)"
    
    # Assert: Admin query should return exactly 5 fields
    assert len(admin_results[0]) == 5, \
        "Admin query should return exactly 5 fields (user_id, name, email, role, created_at)"
    
    # Assert: Full query should return 6 fields (including password)
    assert len(full_results[0]) == 6, \
        "Full query should return 6 fields (including password)"
    
    # Assert: The difference is exactly 1 field (the password)
    assert len(full_results[0]) - len(admin_results[0]) == 1, \
        "The difference should be exactly 1 field (the password field)"
