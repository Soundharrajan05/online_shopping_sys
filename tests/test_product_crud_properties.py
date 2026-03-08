"""Property-based tests for Product CRUD operations"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app.models.product import Product
from app.models.category import Category
from app.database.db import Database
from decimal import Decimal


# Feature: online-shopping-system, Property 26: Product CRUD completeness
# Validates: Requirements 8.1, 8.2, 8.3


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

description_strategy = st.text(
    min_size=0,
    max_size=500,
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))
)

price_strategy = st.decimals(
    min_value=Decimal('0.01'),
    max_value=Decimal('99999.99'),
    places=2
)

stock_strategy = st.integers(min_value=0, max_value=10000)

image_url_strategy = st.text(
    min_size=0,
    max_size=255,
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))
)


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    description=description_strategy,
    price=price_strategy,
    stock_quantity=stock_strategy,
    image_url=image_url_strategy
)
@pytest.mark.property_test
def test_product_create_operation(
    clean_products_and_categories,
    product_name,
    description,
    price,
    stock_quantity,
    image_url
):
    """
    Property: For any valid product data, creating a product should result
    in a product record that can be retrieved with all fields intact.
    
    **Validates: Requirements 8.1**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create product
    product = Product.create(
        product_name=product_name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category.category_id
    )
    
    # Verify product was created
    assert product is not None
    assert product.product_id is not None
    assert product.product_name == product_name
    assert product.description == description
    assert Decimal(str(product.price)) == price
    assert product.stock_quantity == stock_quantity
    assert product.image_url == image_url
    assert product.category_id == category.category_id
    
    # Verify product can be retrieved
    retrieved = Product.get_by_id(product.product_id)
    assert retrieved is not None
    assert retrieved.product_id == product.product_id
    assert retrieved.product_name == product_name
    assert retrieved.description == description
    assert Decimal(str(retrieved.price)) == price
    assert retrieved.stock_quantity == stock_quantity
    assert retrieved.image_url == image_url
    assert retrieved.category_id == category.category_id


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    initial_name=product_name_strategy,
    updated_name=product_name_strategy,
    initial_price=price_strategy,
    updated_price=price_strategy,
    initial_stock=stock_strategy,
    updated_stock=stock_strategy
)
@pytest.mark.property_test
def test_product_update_operation(
    clean_products_and_categories,
    initial_name,
    updated_name,
    initial_price,
    updated_price,
    initial_stock,
    updated_stock
):
    """
    Property: For any product, updating any field should persist the new value
    and be reflected in subsequent queries.
    
    **Validates: Requirements 8.2**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create initial product
    product = Product.create(
        product_name=initial_name,
        description="Initial description",
        price=initial_price,
        stock_quantity=initial_stock,
        image_url="initial.jpg",
        category_id=category.category_id
    )
    
    # Update product fields
    rows_affected = Product.update(
        product_id=product.product_id,
        product_name=updated_name,
        price=updated_price,
        stock_quantity=updated_stock
    )
    
    # Verify update was successful (should be 1 even if values are the same)
    # MySQL returns 0 if no actual change occurred, but 1 if the row was matched
    # We verify the update by checking the retrieved values
    assert rows_affected >= 0  # Update executed successfully
    
    # Retrieve updated product
    updated_product = Product.get_by_id(product.product_id)
    assert updated_product is not None
    assert updated_product.product_name == updated_name
    assert Decimal(str(updated_product.price)) == updated_price
    assert updated_product.stock_quantity == updated_stock
    # Fields not updated should remain the same
    assert updated_product.description == "Initial description"
    assert updated_product.image_url == "initial.jpg"


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    price=price_strategy,
    stock_quantity=stock_strategy
)
@pytest.mark.property_test
def test_product_delete_operation(
    clean_products_and_categories,
    product_name,
    price,
    stock_quantity
):
    """
    Property: For any product, deleting the record should result in the product
    no longer being retrievable from the database.
    
    **Validates: Requirements 8.3**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # Create product
    product = Product.create(
        product_name=product_name,
        description="Test description",
        price=price,
        stock_quantity=stock_quantity,
        image_url="test.jpg",
        category_id=category.category_id
    )
    
    product_id = product.product_id
    
    # Verify product exists
    retrieved = Product.get_by_id(product_id)
    assert retrieved is not None
    
    # Delete product
    rows_affected = Product.delete(product_id)
    assert rows_affected == 1
    
    # Verify product no longer exists
    deleted_product = Product.get_by_id(product_id)
    assert deleted_product is None


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    price=price_strategy,
    stock_quantity=stock_strategy
)
@pytest.mark.property_test
def test_product_crud_completeness(
    clean_products_and_categories,
    product_name,
    price,
    stock_quantity
):
    """
    Property: The system should support creating a product with all fields,
    updating any field, and deleting the record entirely.
    
    This is a comprehensive test that verifies the complete CRUD cycle.
    
    **Validates: Requirements 8.1, 8.2, 8.3**
    """
    # Get or create test category
    category = get_or_create_test_category()
    
    # CREATE: Create a new product
    product = Product.create(
        product_name=product_name,
        description="Original description",
        price=price,
        stock_quantity=stock_quantity,
        image_url="original.jpg",
        category_id=category.category_id
    )
    
    assert product is not None
    assert product.product_id is not None
    product_id = product.product_id
    
    # READ: Verify product can be retrieved
    retrieved = Product.get_by_id(product_id)
    assert retrieved is not None
    assert retrieved.product_id == product_id
    assert retrieved.product_name == product_name
    
    # UPDATE: Update the product
    new_description = "Updated description"
    rows_affected = Product.update(
        product_id=product_id,
        description=new_description
    )
    assert rows_affected == 1
    
    # Verify update persisted
    updated = Product.get_by_id(product_id)
    assert updated is not None
    assert updated.description == new_description
    assert updated.product_name == product_name  # Unchanged field
    
    # DELETE: Delete the product
    rows_affected = Product.delete(product_id)
    assert rows_affected == 1
    
    # Verify product is gone
    deleted = Product.get_by_id(product_id)
    assert deleted is None


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    products_data=st.lists(
        st.tuples(
            product_name_strategy,
            price_strategy,
            stock_strategy
        ),
        min_size=1,
        max_size=10
    )
)
@pytest.mark.property_test
def test_product_get_all_completeness(clean_products_and_categories, products_data):
    """
    Property: For any set of created products, get_all() should return
    all products with their complete information.
    
    **Validates: Requirements 8.5**
    """
    # Ensure clean state - delete all products first
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM products")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Get or create test category
    category = get_or_create_test_category()
    
    created_products = []
    
    # Create multiple products
    for i, (name, price, stock) in enumerate(products_data):
        product = Product.create(
            product_name=f"{name}_{i}",  # Make names unique
            description=f"Description {i}",
            price=price,
            stock_quantity=stock,
            image_url=f"image{i}.jpg",
            category_id=category.category_id
        )
        created_products.append(product)
    
    # Retrieve all products
    all_products = Product.get_all()
    
    # Verify all created products are in the result
    assert len(all_products) == len(created_products)
    
    retrieved_ids = {p.product_id for p in all_products}
    created_ids = {p.product_id for p in created_products}
    assert retrieved_ids == created_ids
    
    # Verify each product has complete information
    for product in all_products:
        assert product.product_id is not None
        assert product.product_name is not None
        assert product.price is not None
        assert product.stock_quantity is not None
        assert product.category_id == category.category_id
