"""Property-based tests for stock update persistence"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.product import Product
from app.models.category import Category
from app.database.db import Database
from decimal import Decimal


# Feature: online-shopping-system, Property 27: Stock update persistence
# Validates: Requirements 8.4


@pytest.fixture(scope='function')
def clean_products_and_categories(setup_test_database):
    """
    Clean products and categories tables before and after each test
    """
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        # Delete in correct order due to foreign key constraints
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    yield
    
    # Clean up after test
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_or_create_test_category():
    """Helper function to get or create a test category for property tests"""
    # Try to get existing category
    categories = Category.get_all()
    if categories:
        return categories[0]
    # Create new category if none exists
    return Category.create("Test Category")


# Strategy for generating valid product data
product_name_strategy = st.text(
    min_size=1, 
    max_size=200,
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))
).filter(lambda x: x.strip() != '')

price_strategy = st.decimals(
    min_value=Decimal('0.01'),
    max_value=Decimal('99999.99'),
    places=2
)

stock_strategy = st.integers(min_value=0, max_value=10000)


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    initial_price=price_strategy,
    initial_stock=stock_strategy,
    updated_stock=stock_strategy
)
@pytest.mark.property_test
def test_stock_update_persistence(
    clean_products_and_categories,
    product_name,
    initial_price,
    initial_stock,
    updated_stock
):
    """
    Property: For any product, updating the stock_quantity should persist
    the new value and be reflected in subsequent queries.
    
    This test verifies that stock updates are correctly saved to the database
    and can be retrieved accurately.
    
    **Validates: Requirements 8.4**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create product with initial stock
    product = Product.create(
        product_name=product_name,
        description="Test product for stock update",
        price=initial_price,
        stock_quantity=initial_stock,
        image_url="test.jpg",
        category_id=category.category_id
    )
    
    product_id = product.product_id
    
    # Verify initial stock
    retrieved = Product.get_by_id(product_id)
    assert retrieved is not None
    assert retrieved.stock_quantity == initial_stock
    
    # Update stock quantity
    rows_affected = Product.update(
        product_id=product_id,
        stock_quantity=updated_stock
    )
    
    # Verify update was executed
    assert rows_affected >= 0
    
    # Retrieve product again and verify stock was updated
    updated_product = Product.get_by_id(product_id)
    assert updated_product is not None
    assert updated_product.stock_quantity == updated_stock
    
    # Verify other fields remain unchanged
    assert updated_product.product_name == product_name
    assert Decimal(str(updated_product.price)) == initial_price
    assert updated_product.description == "Test product for stock update"
    assert updated_product.image_url == "test.jpg"
    assert updated_product.category_id == category.category_id


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    price=price_strategy,
    initial_stock=stock_strategy,
    stock_updates=st.lists(
        stock_strategy,
        min_size=1,
        max_size=5
    )
)
@pytest.mark.property_test
def test_multiple_stock_updates_persistence(
    clean_products_and_categories,
    product_name,
    price,
    initial_stock,
    stock_updates
):
    """
    Property: For any product, multiple sequential stock updates should
    each persist correctly, with the final query returning the last updated value.
    
    This test verifies that stock updates are idempotent and that each update
    correctly overwrites the previous value.
    
    **Validates: Requirements 8.4**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create product with initial stock
    product = Product.create(
        product_name=product_name,
        description="Test product for multiple stock updates",
        price=price,
        stock_quantity=initial_stock,
        image_url="test.jpg",
        category_id=category.category_id
    )
    
    product_id = product.product_id
    
    # Perform multiple stock updates
    for new_stock in stock_updates:
        Product.update(
            product_id=product_id,
            stock_quantity=new_stock
        )
        
        # Verify each update persists immediately
        retrieved = Product.get_by_id(product_id)
        assert retrieved is not None
        assert retrieved.stock_quantity == new_stock
    
    # Final verification: the last update should be the current value
    final_product = Product.get_by_id(product_id)
    assert final_product is not None
    assert final_product.stock_quantity == stock_updates[-1]


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    products_data=st.lists(
        st.tuples(
            product_name_strategy,
            price_strategy,
            stock_strategy,
            stock_strategy  # updated stock
        ),
        min_size=1,
        max_size=10
    )
)
@pytest.mark.property_test
def test_stock_update_isolation(
    clean_products_and_categories,
    products_data
):
    """
    Property: For any set of products, updating the stock of one product
    should not affect the stock of other products.
    
    This test verifies that stock updates are properly isolated per product.
    
    **Validates: Requirements 8.4**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create multiple products
    created_products = []
    for i, (name, price, initial_stock, _) in enumerate(products_data):
        product = Product.create(
            product_name=f"{name}_{i}",  # Make names unique
            description=f"Product {i}",
            price=price,
            stock_quantity=initial_stock,
            image_url=f"image{i}.jpg",
            category_id=category.category_id
        )
        created_products.append((product, initial_stock))
    
    # Update stock for each product and verify isolation
    for i, (name, price, initial_stock, updated_stock) in enumerate(products_data):
        product, _ = created_products[i]
        
        # Update this product's stock
        Product.update(
            product_id=product.product_id,
            stock_quantity=updated_stock
        )
        
        # Verify this product's stock was updated
        updated_product = Product.get_by_id(product.product_id)
        assert updated_product is not None
        assert updated_product.stock_quantity == updated_stock
        
        # Verify other products' stock remained unchanged
        for j, (other_product, other_initial_stock) in enumerate(created_products):
            if i != j:
                other_retrieved = Product.get_by_id(other_product.product_id)
                assert other_retrieved is not None
                # Should still have initial stock (or previously updated stock if j < i)
                if j < i:
                    # This product was already updated
                    expected_stock = products_data[j][3]  # updated_stock
                else:
                    # This product hasn't been updated yet
                    expected_stock = other_initial_stock
                assert other_retrieved.stock_quantity == expected_stock
