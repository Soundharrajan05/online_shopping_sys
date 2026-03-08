"""Property-based tests for product listing with category join"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from app.models.product import Product
from app.models.category import Category
from app.database.db import Database
from decimal import Decimal


# Feature: online-shopping-system, Property 28: Product listing with category join
# Validates: Requirements 8.5


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


# Strategy for generating valid product data
product_name_strategy = st.text(
    min_size=1, 
    max_size=200,
    alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))
).filter(lambda x: x.strip() != '')

category_name_strategy = st.text(
    min_size=1,
    max_size=100,
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
    category_name=category_name_strategy,
    product_name=product_name_strategy,
    price=price_strategy,
    stock_quantity=stock_strategy
)
@pytest.mark.property_test
def test_product_listing_includes_category_info(
    clean_products_and_categories,
    category_name,
    product_name,
    price,
    stock_quantity
):
    """
    Property: For any product with an associated category, querying all products
    should return the product with its category information included.
    
    This test verifies that the product listing properly joins with the categories
    table and returns category information for each product.
    
    **Validates: Requirements 8.5**
    """
    # Create category with unique name to avoid duplicates
    import time
    unique_category_name = f"{category_name}_{int(time.time() * 1000000)}"
    category = Category.create(unique_category_name)
    
    # Create product with category
    product = Product.create(
        product_name=product_name,
        description="Test product",
        price=price,
        stock_quantity=stock_quantity,
        image_url="test.jpg",
        category_id=category.category_id
    )
    
    # Query products using the admin route's query pattern
    query = """
        SELECT p.product_id, p.product_name, p.description, p.price,
               p.stock_quantity, p.image_url, p.category_id, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    """
    results = Database.execute_query(query, (product.product_id,), fetch=True)
    
    # Verify product was returned with category information
    assert len(results) == 1
    row = results[0]
    
    assert row[0] == product.product_id  # product_id
    assert row[1] == product_name  # product_name
    assert row[2] == "Test product"  # description
    assert Decimal(str(row[3])) == price  # price
    assert row[4] == stock_quantity  # stock_quantity
    assert row[5] == "test.jpg"  # image_url
    assert row[6] == category.category_id  # category_id
    assert row[7] == unique_category_name  # category_name (from join)


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    categories_and_products=st.lists(
        st.tuples(
            category_name_strategy,
            st.lists(
                st.tuples(
                    product_name_strategy,
                    price_strategy,
                    stock_strategy
                ),
                min_size=1,
                max_size=5
            )
        ),
        min_size=1,
        max_size=5
    )
)
@pytest.mark.property_test
def test_multiple_products_with_categories(
    clean_products_and_categories,
    categories_and_products
):
    """
    Property: For any set of categories with products, querying all products
    should return all products with their respective category information.
    
    This test verifies that the category join works correctly for multiple
    products across multiple categories.
    
    **Validates: Requirements 8.5**
    """
    # Ensure clean state
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    created_products = []
    category_map = {}
    
    # Create categories and products
    for cat_idx, (category_name, products_data) in enumerate(categories_and_products):
        # Create unique category name to avoid duplicates
        unique_cat_name = f"{category_name}_{cat_idx}"
        category = Category.create(unique_cat_name)
        category_map[category.category_id] = unique_cat_name
        
        for prod_idx, (product_name, price, stock) in enumerate(products_data):
            # Create unique product name
            unique_prod_name = f"{product_name}_{cat_idx}_{prod_idx}"
            product = Product.create(
                product_name=unique_prod_name,
                description=f"Product {prod_idx} in category {cat_idx}",
                price=price,
                stock_quantity=stock,
                image_url=f"image_{cat_idx}_{prod_idx}.jpg",
                category_id=category.category_id
            )
            created_products.append((product, category.category_id, unique_cat_name))
    
    # Query all products with category information
    query = """
        SELECT p.product_id, p.product_name, p.description, p.price,
               p.stock_quantity, p.image_url, p.category_id, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_name
    """
    results = Database.execute_query(query, None, fetch=True)
    
    # Verify all products are returned
    assert len(results) == len(created_products)
    
    # Verify each product has category information
    for row in results:
        product_id = row[0]
        product_name = row[1]
        category_id = row[6]
        category_name = row[7]
        
        # Verify product exists in our created list
        matching_products = [p for p in created_products if p[0].product_id == product_id]
        assert len(matching_products) == 1
        
        created_product, expected_cat_id, expected_cat_name = matching_products[0]
        
        # Verify category information is correct
        assert category_id == expected_cat_id
        assert category_name == expected_cat_name
        
        # Verify all fields are present
        assert product_name is not None
        assert row[2] is not None  # description
        assert row[3] is not None  # price
        assert row[4] is not None  # stock_quantity
        assert row[5] is not None  # image_url


@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    product_name=product_name_strategy,
    price=price_strategy,
    stock_quantity=stock_strategy
)
@pytest.mark.property_test
def test_product_without_category_listing(
    clean_products_and_categories,
    product_name,
    price,
    stock_quantity
):
    """
    Property: For any product without a category (category_id = NULL),
    querying all products should still return the product with NULL category information.
    
    This test verifies that the LEFT JOIN properly handles products without categories.
    
    **Validates: Requirements 8.5**
    """
    # Create product without category (category_id = None)
    product = Product.create(
        product_name=product_name,
        description="Product without category",
        price=price,
        stock_quantity=stock_quantity,
        image_url="test.jpg",
        category_id=None
    )
    
    # Query products with category join
    query = """
        SELECT p.product_id, p.product_name, p.description, p.price,
               p.stock_quantity, p.image_url, p.category_id, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        WHERE p.product_id = %s
    """
    results = Database.execute_query(query, (product.product_id,), fetch=True)
    
    # Verify product was returned
    assert len(results) == 1
    row = results[0]
    
    assert row[0] == product.product_id  # product_id
    assert row[1] == product_name  # product_name
    assert row[6] is None  # category_id should be NULL
    assert row[7] is None  # category_name should be NULL (no join match)
    
    # Other fields should still be present
    assert row[2] == "Product without category"  # description
    assert Decimal(str(row[3])) == price  # price
    assert row[4] == stock_quantity  # stock_quantity
    assert row[5] == "test.jpg"  # image_url


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    category_name=category_name_strategy,
    products_with_category=st.lists(
        st.tuples(product_name_strategy, price_strategy, stock_strategy),
        min_size=1,
        max_size=5
    ),
    products_without_category=st.lists(
        st.tuples(product_name_strategy, price_strategy, stock_strategy),
        min_size=1,
        max_size=5
    )
)
@pytest.mark.property_test
def test_mixed_products_with_and_without_categories(
    clean_products_and_categories,
    category_name,
    products_with_category,
    products_without_category
):
    """
    Property: For any mix of products with and without categories,
    querying all products should return all products with appropriate
    category information (present or NULL).
    
    This test verifies that the LEFT JOIN works correctly for mixed scenarios.
    
    **Validates: Requirements 8.5**
    """
    # Ensure clean state
    connection = Database.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM categories")
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Create category
    category = Category.create(category_name)
    
    created_with_category = []
    created_without_category = []
    
    # Create products with category
    for idx, (name, price, stock) in enumerate(products_with_category):
        product = Product.create(
            product_name=f"{name}_with_cat_{idx}",
            description=f"Product {idx} with category",
            price=price,
            stock_quantity=stock,
            image_url=f"with_cat_{idx}.jpg",
            category_id=category.category_id
        )
        created_with_category.append(product)
    
    # Create products without category
    for idx, (name, price, stock) in enumerate(products_without_category):
        product = Product.create(
            product_name=f"{name}_no_cat_{idx}",
            description=f"Product {idx} without category",
            price=price,
            stock_quantity=stock,
            image_url=f"no_cat_{idx}.jpg",
            category_id=None
        )
        created_without_category.append(product)
    
    # Query all products with category join
    query = """
        SELECT p.product_id, p.product_name, p.description, p.price,
               p.stock_quantity, p.image_url, p.category_id, c.category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_name
    """
    results = Database.execute_query(query, None, fetch=True)
    
    # Verify all products are returned
    total_products = len(created_with_category) + len(created_without_category)
    assert len(results) == total_products
    
    # Count products with and without categories in results
    products_with_cat_in_results = [r for r in results if r[7] is not None]
    products_without_cat_in_results = [r for r in results if r[7] is None]
    
    assert len(products_with_cat_in_results) == len(created_with_category)
    assert len(products_without_cat_in_results) == len(created_without_category)
    
    # Verify products with category have correct category name
    for row in products_with_cat_in_results:
        assert row[7] == category_name  # category_name
        assert row[6] == category.category_id  # category_id
    
    # Verify products without category have NULL category info
    for row in products_without_cat_in_results:
        assert row[7] is None  # category_name
        assert row[6] is None  # category_id
