"""Property-based tests for category management"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.category import Category


# Feature: online-shopping-system, Property 25: Category creation persistence
@given(category_name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip() != ''))
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.property_test
def test_category_creation_persistence(test_db, category_name):
    """
    Property: For any valid category name, creating a category should result 
    in a category record that appears in subsequent category listings.
    
    **Validates: Requirements 7.1, 7.2**
    
    This test verifies that:
    1. A category can be created with any valid name
    2. The created category persists in the database
    3. The category appears in the list of all categories
    4. The category name matches what was provided
    """
    # Normalize the category name (strip whitespace)
    normalized_name = category_name.strip()
    
    # Skip if category already exists (for test isolation)
    if Category.exists(normalized_name):
        return
    
    # Action: Create a new category
    created_category = Category.create(normalized_name)
    
    # Assert: Category was created successfully
    assert created_category is not None, "Category creation should return a Category instance"
    assert created_category.category_name == normalized_name, "Created category name should match input"
    assert created_category.category_id is not None, "Created category should have an ID"
    
    # Assert: Category appears in listings
    all_categories = Category.get_all()
    category_names = [cat.category_name for cat in all_categories]
    
    assert normalized_name in category_names, \
        f"Created category '{normalized_name}' should appear in category listings"
    
    # Assert: Category can be verified to exist
    assert Category.exists(normalized_name), \
        f"Category.exists() should return True for created category '{normalized_name}'"
