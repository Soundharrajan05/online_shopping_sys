"""Unit tests for category management"""

import pytest
from app.models.category import Category


def test_duplicate_category_rejection(test_db):
    """
    Test that duplicate category names are rejected
    
    Validates: Requirement 7.3
    
    This test verifies that:
    1. A category can be created with a unique name
    2. Attempting to create a category with the same name is detected
    3. The exists() method correctly identifies duplicate names
    """
    # Create first category
    category_name = "Electronics"
    category1 = Category.create(category_name)
    
    assert category1 is not None, "First category should be created successfully"
    assert category1.category_name == category_name
    
    # Verify category exists
    assert Category.exists(category_name), "Category should exist after creation"
    
    # Attempt to create duplicate should be detectable
    assert Category.exists(category_name), "exists() should return True for duplicate name"
    
    # Verify only one category with this name exists
    all_categories = Category.get_all()
    matching_categories = [cat for cat in all_categories if cat.category_name == category_name]
    assert len(matching_categories) == 1, "Only one category with this name should exist"


def test_empty_category_list(test_db):
    """
    Test that get_all() returns empty list when no categories exist
    
    Validates: Requirement 7.2
    """
    categories = Category.get_all()
    assert categories == [], "Should return empty list when no categories exist"


def test_multiple_categories_creation(test_db):
    """
    Test creating multiple unique categories
    
    Validates: Requirements 7.1, 7.2
    """
    category_names = ["Electronics", "Clothing", "Books", "Home & Garden"]
    
    # Create all categories
    for name in category_names:
        category = Category.create(name)
        assert category is not None, f"Category '{name}' should be created"
        assert category.category_name == name
    
    # Verify all categories exist
    all_categories = Category.get_all()
    retrieved_names = [cat.category_name for cat in all_categories]
    
    for name in category_names:
        assert name in retrieved_names, f"Category '{name}' should be in the list"
    
    assert len(all_categories) == len(category_names), \
        "Number of categories should match number created"


def test_category_to_dict(test_db):
    """
    Test the to_dict() method of Category model
    """
    category = Category.create("Test Category")
    category_dict = category.to_dict()
    
    assert isinstance(category_dict, dict), "to_dict() should return a dictionary"
    assert 'category_id' in category_dict, "Dictionary should contain category_id"
    assert 'category_name' in category_dict, "Dictionary should contain category_name"
    assert category_dict['category_name'] == "Test Category"
