"""
Unit tests for shopping cart edge cases

Feature: online-shopping-system
"""

import pytest
from app.models.cart import Cart
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.database.db import Database


@pytest.fixture(scope='function')
def clean_cart_tables(setup_test_database):
    """
    Clean cart, products, categories, and users tables before and after each test
    """
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM cart")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    yield
    
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM cart")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@pytest.fixture
def test_user(clean_cart_tables):
    """Create a test user"""
    user_id = User.create("Test User", "test@example.com", "password123", "customer")
    return user_id


@pytest.fixture
def test_category(clean_cart_tables):
    """Create a test category"""
    category = Category.create("Electronics")
    return category


@pytest.fixture
def test_product(test_category):
    """Create a test product"""
    product = Product.create(
        product_name="Test Laptop",
        description="A test laptop",
        price=999.99,
        stock_quantity=10,
        image_url="laptop.jpg",
        category_id=test_category.category_id
    )
    return product


def test_empty_cart_display(test_user):
    """
    Test empty cart display
    
    Validates: Requirements 4.6
    
    When a customer's cart is empty, the system should display
    an empty cart message and return empty list.
    """
    # Act: Get cart for user with no items
    cart_items = Cart.get_user_cart(test_user)
    
    # Assert: Cart should be empty
    assert cart_items == [], "Empty cart should return empty list"
    assert len(cart_items) == 0, "Empty cart should have length 0"
    
    # Act: Calculate total for empty cart
    total = Cart.calculate_total(test_user)
    
    # Assert: Total should be 0.0
    assert total == 0.0, "Empty cart total should be 0.0"


def test_cart_removal(test_user, test_product):
    """
    Test cart item removal
    
    Validates: Requirements 4.4
    
    When a customer removes an item from cart, the system should
    delete the cart entry completely.
    """
    # Arrange: Add item to cart
    cart_id = Cart.add_item(test_user, test_product.product_id, 2)
    assert cart_id is not None, "Item should be added to cart"
    
    # Verify item is in cart
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 1, "Cart should have 1 item"
    
    # Act: Remove item from cart
    rows_affected = Cart.remove_item(cart_id)
    
    # Assert: Item should be removed
    assert rows_affected == 1, "One row should be affected"
    
    # Verify cart is now empty
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 0, "Cart should be empty after removal"
    assert cart_items == [], "Cart should return empty list"


def test_stock_validation_error_on_add(test_user, test_product):
    """
    Test stock validation error when adding to cart
    
    Validates: Requirements 4.2
    
    When a customer adds a product with insufficient stock,
    the system should reject the addition and display an error message.
    """
    # Act & Assert: Try to add more than available stock
    with pytest.raises(ValueError) as exc_info:
        Cart.add_item(test_user, test_product.product_id, 100)  # Stock is only 10
    
    # Assert: Error message should mention insufficient stock
    assert "Insufficient stock" in str(exc_info.value), \
        "Error should mention insufficient stock"
    
    # Assert: Cart should remain empty
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 0, "Cart should be empty when add fails"


def test_stock_validation_error_on_update(test_user, test_product):
    """
    Test stock validation error when updating cart quantity
    
    Validates: Requirements 4.3
    
    When a customer updates cart item quantity to exceed available stock,
    the system should reject the update and display an error message.
    """
    # Arrange: Add valid quantity to cart
    cart_id = Cart.add_item(test_user, test_product.product_id, 2)
    assert cart_id is not None, "Item should be added to cart"
    
    # Act & Assert: Try to update to more than available stock
    with pytest.raises(ValueError) as exc_info:
        Cart.update_quantity(cart_id, 100)  # Stock is only 10
    
    # Assert: Error message should mention insufficient stock
    assert "Insufficient stock" in str(exc_info.value), \
        "Error should mention insufficient stock"
    
    # Assert: Cart quantity should remain unchanged
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 1, "Cart should still have 1 item"
    assert cart_items[0]['quantity'] == 2, "Quantity should remain 2"


def test_update_quantity_to_zero_removes_item(test_user, test_product):
    """
    Test updating quantity to zero removes the item
    
    Validates: Requirements 4.3, 4.4
    
    When a customer updates cart item quantity to 0,
    the system should remove the item from cart.
    """
    # Arrange: Add item to cart
    cart_id = Cart.add_item(test_user, test_product.product_id, 3)
    assert cart_id is not None, "Item should be added to cart"
    
    # Verify item is in cart
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 1, "Cart should have 1 item"
    
    # Act: Update quantity to 0
    rows_affected = Cart.update_quantity(cart_id, 0)
    
    # Assert: Item should be removed
    assert rows_affected == 1, "One row should be affected"
    
    # Verify cart is now empty
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 0, "Cart should be empty after updating to 0"


def test_negative_quantity_rejected(test_user, test_product):
    """
    Test that negative quantities are rejected
    
    Validates: Requirements 11.1 (Input validation)
    
    The system should reject negative quantities for cart operations.
    """
    # Act & Assert: Try to add negative quantity
    with pytest.raises(ValueError) as exc_info:
        Cart.add_item(test_user, test_product.product_id, -5)
    
    assert "Quantity must be positive" in str(exc_info.value), \
        "Error should mention positive quantity requirement"
    
    # Arrange: Add valid item to cart
    cart_id = Cart.add_item(test_user, test_product.product_id, 2)
    
    # Act & Assert: Try to update to negative quantity
    with pytest.raises(ValueError) as exc_info:
        Cart.update_quantity(cart_id, -3)
    
    assert "Quantity cannot be negative" in str(exc_info.value), \
        "Error should mention negative quantity rejection"


def test_clear_cart(test_user, test_product, test_category):
    """
    Test clearing entire cart
    
    Validates: Requirements 5.4
    
    When an order is created, the system should clear the customer's cart.
    This test verifies the clear_cart functionality.
    """
    # Arrange: Add multiple items to cart
    Cart.add_item(test_user, test_product.product_id, 2)
    
    # Create another product and add it
    product2 = Product.create(
        product_name="Test Mouse",
        description="A test mouse",
        price=29.99,
        stock_quantity=50,
        image_url="mouse.jpg",
        category_id=test_category.category_id
    )
    Cart.add_item(test_user, product2.product_id, 3)
    
    # Verify cart has items
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 2, "Cart should have 2 items"
    
    # Act: Clear cart
    rows_affected = Cart.clear_cart(test_user)
    
    # Assert: All items should be removed
    assert rows_affected == 2, "Two rows should be affected"
    
    # Verify cart is empty
    cart_items = Cart.get_user_cart(test_user)
    assert len(cart_items) == 0, "Cart should be empty after clearing"
    assert Cart.calculate_total(test_user) == 0.0, "Total should be 0.0"


def test_cart_with_multiple_products(test_user, test_product, test_category):
    """
    Test cart with multiple different products
    
    Validates: Requirements 4.1, 4.5
    
    The system should correctly handle multiple products in cart
    and calculate the total accurately.
    """
    # Arrange: Add first product
    Cart.add_item(test_user, test_product.product_id, 2)
    
    # Create and add second product
    product2 = Product.create(
        product_name="Test Keyboard",
        description="A test keyboard",
        price=79.99,
        stock_quantity=30,
        image_url="keyboard.jpg",
        category_id=test_category.category_id
    )
    Cart.add_item(test_user, product2.product_id, 1)
    
    # Act: Get cart items
    cart_items = Cart.get_user_cart(test_user)
    
    # Assert: Cart should have 2 items
    assert len(cart_items) == 2, "Cart should have 2 items"
    
    # Assert: Calculate total
    expected_total = (999.99 * 2) + (79.99 * 1)
    calculated_total = Cart.calculate_total(test_user)
    
    assert abs(calculated_total - expected_total) < 0.01, \
        f"Total should be {expected_total:.2f}, got {calculated_total:.2f}"


def test_nonexistent_product_error(test_user):
    """
    Test adding nonexistent product to cart
    
    Validates: Requirements 11.1 (Input validation)
    
    The system should reject attempts to add nonexistent products.
    """
    # Act & Assert: Try to add nonexistent product
    with pytest.raises(ValueError) as exc_info:
        Cart.add_item(test_user, 99999, 1)  # Nonexistent product ID
    
    assert "not found" in str(exc_info.value).lower(), \
        "Error should mention product not found"
