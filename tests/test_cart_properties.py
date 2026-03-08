"""
Property-based tests for shopping cart functionality

Feature: online-shopping-system
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from app.models.cart import Cart
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.database.db import Database


# Strategies for generating valid test data
valid_user_names = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)

# Strategy for generating valid email addresses
# Filter to ensure emails pass the application's email validation
import re
def is_valid_app_email(email):
    """Check if email passes the application's validation"""
    if len(email) > 90:
        return False
    # Basic email regex that matches the application's validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

valid_emails = st.emails().filter(is_valid_app_email)

valid_passwords = st.text(
    alphabet=st.characters(min_codepoint=33, max_codepoint=126),
    min_size=8,
    max_size=100
)

valid_product_names = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=200
).filter(lambda x: len(x.strip()) > 0)

valid_descriptions = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=500
)

valid_prices = st.decimals(
    min_value=0.01,
    max_value=99999.99,
    places=2
)

valid_stock_quantities = st.integers(min_value=1, max_value=100)

valid_category_names = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)

valid_quantities = st.integers(min_value=1, max_value=10)


@pytest.fixture(scope='function')
def clean_cart_tables(setup_test_database):
    """
    Clean cart, products, categories, and users tables before and after each test
    This ensures test isolation
    """
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        # Delete in correct order due to foreign key constraints
        cursor.execute("DELETE FROM cart")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        cursor.execute("DELETE FROM users")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    yield
    
    # Clean up after test
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


@settings(max_examples=20, deadline=None)
@given(
    user_name=valid_user_names,
    email=valid_emails,
    password=valid_passwords,
    category_name=valid_category_names,
    product_name=valid_product_names,
    description=valid_descriptions,
    price=valid_prices,
    stock_quantity=valid_stock_quantities,
    quantity1=valid_quantities,
    quantity2=valid_quantities
)
@pytest.mark.usefixtures('clean_cart_tables')
def test_property_cart_addition_idempotence(
    user_name, email, password, category_name, product_name, description,
    price, stock_quantity, quantity1, quantity2
):
    """
    Property 14: Cart addition idempotence
    
    **Validates: Requirements 4.1**
    
    For any product, adding it to cart multiple times should result in a single
    cart entry with accumulated quantity. This ensures that the cart doesn't
    create duplicate entries for the same product.
    
    Property: ∀ (user, product, quantity1, quantity2) →
              Cart.add_item(user, product, quantity1) then
              Cart.add_item(user, product, quantity2) results in:
              - Single cart entry for (user, product)
              - quantity = quantity1 + quantity2
    """
    # Arrange: Create a user
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"
    user_id = User.create(user_name, unique_email, password, 'customer')
    assert user_id is not None, "User creation should succeed"
    
    # Arrange: Create a category
    unique_category_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category = Category.create(unique_category_name)
    assert category is not None, "Category creation should succeed"
    
    # Arrange: Create a product with sufficient stock
    total_quantity_needed = quantity1 + quantity2
    assume(stock_quantity >= total_quantity_needed)
    
    product = Product.create(
        product_name=product_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url="test.jpg",
        category_id=category.category_id
    )
    assert product is not None, "Product creation should succeed"
    
    # Act: Add product to cart first time
    cart_id1 = Cart.add_item(user_id, product.product_id, quantity1)
    assert cart_id1 is not None, "First cart addition should succeed"
    
    # Act: Add same product to cart second time
    cart_id2 = Cart.add_item(user_id, product.product_id, quantity2)
    assert cart_id2 is not None, "Second cart addition should succeed"
    
    # Assert: Both operations should return the same cart_id (idempotence)
    assert cart_id1 == cart_id2, \
        f"Adding same product twice should update same cart entry, " \
        f"got cart_id1={cart_id1}, cart_id2={cart_id2}"
    
    # Assert: Get user's cart and verify single entry
    cart_items = Cart.get_user_cart(user_id)
    assert len(cart_items) == 1, \
        f"Cart should have exactly 1 entry for the product, got {len(cart_items)}"
    
    # Assert: Verify the quantity is accumulated
    cart_item = cart_items[0]
    expected_quantity = quantity1 + quantity2
    assert cart_item['quantity'] == expected_quantity, \
        f"Cart quantity should be {expected_quantity} (sum of {quantity1} + {quantity2}), " \
        f"got {cart_item['quantity']}"
    
    # Assert: Verify product details are correct
    assert cart_item['product_id'] == product.product_id, \
        "Cart item should reference the correct product"
    assert cart_item['user_id'] == user_id, \
        "Cart item should belong to the correct user"


@settings(max_examples=20, deadline=None)
@given(
    user_name=valid_user_names,
    email=valid_emails,
    password=valid_passwords,
    category_name=valid_category_names,
    product_name=valid_product_names,
    description=valid_descriptions,
    price=valid_prices,
    stock_quantity=valid_stock_quantities,
    requested_quantity=st.integers(min_value=1, max_value=200)
)
@pytest.mark.usefixtures('clean_cart_tables')
def test_property_stock_validation_on_cart_operations(
    user_name, email, password, category_name, product_name, description,
    price, stock_quantity, requested_quantity
):
    """
    Property 15: Stock validation on cart operations
    
    **Validates: Requirements 4.2, 4.3**
    
    For any cart operation (add or update), if the requested quantity exceeds
    available stock_quantity, the operation should be rejected. This ensures
    that customers cannot add more items to their cart than are available.
    
    Property: ∀ (product, stock, requested_quantity) where requested_quantity > stock →
              Cart.add_item() raises ValueError
              Cart.update_quantity() raises ValueError
    """
    # Only test cases where requested quantity exceeds stock
    assume(requested_quantity > stock_quantity)
    
    # Arrange: Create a user
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"
    user_id = User.create(user_name, unique_email, password, 'customer')
    assert user_id is not None, "User creation should succeed"
    
    # Arrange: Create a category
    unique_category_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category = Category.create(unique_category_name)
    assert category is not None, "Category creation should succeed"
    
    # Arrange: Create a product with limited stock
    product = Product.create(
        product_name=product_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url="test.jpg",
        category_id=category.category_id
    )
    assert product is not None, "Product creation should succeed"
    
    # Act & Assert: Try to add more than available stock - should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        Cart.add_item(user_id, product.product_id, requested_quantity)
    
    assert "Insufficient stock" in str(exc_info.value), \
        f"Error message should mention insufficient stock, got: {exc_info.value}"
    
    # Assert: Cart should be empty (no item added)
    cart_items = Cart.get_user_cart(user_id)
    assert len(cart_items) == 0, \
        "Cart should be empty when add operation fails due to insufficient stock"
    
    # Now test update_quantity with insufficient stock
    # First, add a valid quantity to cart
    valid_quantity = min(1, stock_quantity)
    if valid_quantity > 0:
        cart_id = Cart.add_item(user_id, product.product_id, valid_quantity)
        assert cart_id is not None, "Adding valid quantity should succeed"
        
        # Act & Assert: Try to update to more than available stock - should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            Cart.update_quantity(cart_id, requested_quantity)
        
        assert "Insufficient stock" in str(exc_info.value), \
            f"Update error message should mention insufficient stock, got: {exc_info.value}"
        
        # Assert: Cart quantity should remain unchanged
        cart_items = Cart.get_user_cart(user_id)
        assert len(cart_items) == 1, "Cart should still have the original item"
        assert cart_items[0]['quantity'] == valid_quantity, \
            f"Cart quantity should remain {valid_quantity} after failed update"


@settings(max_examples=20, deadline=None)
@given(
    user_name=valid_user_names,
    email=valid_emails,
    password=valid_passwords,
    category_name=valid_category_names,
    # Generate list of products with their quantities
    products_data=st.lists(
        st.tuples(
            valid_product_names,
            valid_descriptions,
            valid_prices,
            valid_stock_quantities,
            valid_quantities
        ),
        min_size=1,
        max_size=5
    )
)
@pytest.mark.usefixtures('clean_cart_tables')
def test_property_cart_total_calculation_correctness(
    user_name, email, password, category_name, products_data
):
    """
    Property 17: Cart total calculation correctness
    
    **Validates: Requirements 4.5**
    
    For any user's cart, the calculated total should equal the sum of
    (product.price × cart_item.quantity) for all items. This ensures
    accurate pricing calculations.
    
    Property: ∀ cart_items →
              Cart.calculate_total() = Σ(price_i × quantity_i) for all items i
    """
    # Arrange: Create a user
    import uuid
    unique_email = f"{uuid.uuid4().hex[:8]}_{email}"
    user_id = User.create(user_name, unique_email, password, 'customer')
    assert user_id is not None, "User creation should succeed"
    
    # Arrange: Create a category
    unique_category_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category = Category.create(unique_category_name)
    assert category is not None, "Category creation should succeed"
    
    # Arrange: Create products and add them to cart
    expected_total = 0.0
    created_products = []
    
    for i, (prod_name, description, price, stock, quantity) in enumerate(products_data):
        # Ensure stock is sufficient for quantity
        assume(stock >= quantity)
        
        # Create unique product name to avoid duplicates
        unique_prod_name = f"{prod_name}_{uuid.uuid4().hex[:8]}"
        
        product = Product.create(
            product_name=unique_prod_name,
            description=description,
            price=float(price),
            stock_quantity=stock,
            image_url=f"test{i}.jpg",
            category_id=category.category_id
        )
        assert product is not None, f"Product {i} creation should succeed"
        created_products.append((product, quantity, float(price)))
        
        # Add product to cart
        cart_id = Cart.add_item(user_id, product.product_id, quantity)
        assert cart_id is not None, f"Adding product {i} to cart should succeed"
        
        # Calculate expected total
        expected_total += float(price) * quantity
    
    # Act: Calculate cart total
    calculated_total = Cart.calculate_total(user_id)
    
    # Assert: Calculated total should match expected total
    # Use small epsilon for floating point comparison
    epsilon = 0.01
    assert abs(calculated_total - expected_total) < epsilon, \
        f"Cart total should be {expected_total:.2f}, got {calculated_total:.2f}"
    
    # Assert: Verify by getting cart items and manually calculating
    cart_items = Cart.get_user_cart(user_id)
    assert len(cart_items) == len(created_products), \
        f"Cart should have {len(created_products)} items, got {len(cart_items)}"
    
    manual_total = sum(item['price'] * item['quantity'] for item in cart_items)
    assert abs(manual_total - expected_total) < epsilon, \
        f"Manual calculation should match expected total: {expected_total:.2f}, got {manual_total:.2f}"
    
    # Assert: Each cart item's subtotal should be correct
    for item in cart_items:
        expected_subtotal = item['price'] * item['quantity']
        assert abs(item['subtotal'] - expected_subtotal) < epsilon, \
            f"Item subtotal should be {expected_subtotal:.2f}, got {item['subtotal']:.2f}"
