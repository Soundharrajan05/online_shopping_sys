"""
Property-based tests for product browsing functionality

Feature: online-shopping-system
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from app.models.product import Product
from app.models.category import Category
from app.database.db import Database


# Strategies for generating valid product data
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

valid_stock_quantities = st.integers(min_value=0, max_value=10000)

valid_image_urls = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=0,
    max_size=255
)

valid_category_names = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)


@pytest.fixture(scope='function')
def clean_products_and_categories(setup_test_database):
    """
    Clean products and categories tables before and after each test
    This ensures test isolation
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


@settings(max_examples=20, deadline=None)
@given(
    category_name=valid_category_names,
    product_name=valid_product_names,
    description=valid_descriptions,
    price=valid_prices,
    stock_quantity=valid_stock_quantities,
    image_url=valid_image_urls
)
@pytest.mark.usefixtures('clean_products_and_categories')
def test_property_product_catalog_completeness(
    category_name, product_name, description, price, stock_quantity, image_url
):
    """
    Property 10: Product catalog completeness
    
    **Validates: Requirements 3.1**
    
    For any product catalog query, all products in the database should be returned
    with name, price, image_url, and stock_quantity fields. This ensures that the
    product browsing functionality displays complete product information.
    
    Property: ∀ products in database →
              Product.get_all() returns all products with required fields:
              - product_name (not null)
              - price (not null)
              - image_url (may be null but field exists)
              - stock_quantity (not null)
    """
    # Arrange: Create a category first (required for foreign key)
    # Use a unique category name to avoid duplicate key errors
    import uuid
    unique_category_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category = Category.create(unique_category_name)
    assert category is not None, "Category creation should succeed"
    
    # Arrange: Create a product in the database
    product = Product.create(
        product_name=product_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category.category_id
    )
    assert product is not None, "Product creation should succeed"
    
    # Act: Retrieve all products from the catalog
    all_products = Product.get_all()
    
    # Assert: At least one product should be returned (the one we just created)
    assert len(all_products) >= 1, \
        "Product catalog should return at least the product we created"
    
    # Assert: Find our created product in the results
    found_product = None
    for p in all_products:
        if p.product_id == product.product_id:
            found_product = p
            break
    
    assert found_product is not None, \
        "Created product should be present in the catalog"
    
    # Assert: Product has all required fields (completeness check)
    assert hasattr(found_product, 'product_name'), \
        "Product should have product_name field"
    assert found_product.product_name is not None, \
        "Product name should not be null"
    assert found_product.product_name == product_name, \
        f"Product name should be '{product_name}', got '{found_product.product_name}'"
    
    assert hasattr(found_product, 'price'), \
        "Product should have price field"
    assert found_product.price is not None, \
        "Product price should not be null"
    assert float(found_product.price) == float(price), \
        f"Product price should be {price}, got {found_product.price}"
    
    assert hasattr(found_product, 'image_url'), \
        "Product should have image_url field"
    # image_url can be null/empty, but field must exist
    assert found_product.image_url == image_url, \
        f"Product image_url should be '{image_url}', got '{found_product.image_url}'"
    
    assert hasattr(found_product, 'stock_quantity'), \
        "Product should have stock_quantity field"
    assert found_product.stock_quantity is not None, \
        "Product stock_quantity should not be null"
    assert found_product.stock_quantity == stock_quantity, \
        f"Product stock_quantity should be {stock_quantity}, got {found_product.stock_quantity}"
    
    # Assert: Product also has other expected fields
    assert hasattr(found_product, 'product_id'), \
        "Product should have product_id field"
    assert found_product.product_id > 0, \
        "Product ID should be a positive integer"
    
    assert hasattr(found_product, 'description'), \
        "Product should have description field"
    
    assert hasattr(found_product, 'category_id'), \
        "Product should have category_id field"
    assert found_product.category_id == category.category_id, \
        f"Product category_id should be {category.category_id}, got {found_product.category_id}"


@settings(max_examples=20, deadline=None)
@given(
    category_name=valid_category_names,
    product_name=valid_product_names,
    description=valid_descriptions,
    price=valid_prices,
    stock_quantity=valid_stock_quantities,
    image_url=valid_image_urls
)
@pytest.mark.usefixtures('clean_products_and_categories')
def test_property_category_filtering_correctness(
    category_name, product_name, description, price, stock_quantity, image_url
):
    """
    Property 11: Category filtering correctness
    
    **Validates: Requirements 3.2**
    
    For any category filter, all returned products should have category_id matching
    the filter, and no products from that category should be excluded. This ensures
    that category filtering works correctly and completely.
    
    Property: ∀ (category_id, products) →
              Product.get_all(category_id=category_id) returns only products where:
              - product.category_id = category_id
              - all products with category_id are included
    """
    # Arrange: Create two different categories with unique names
    import uuid
    unique_category1_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category1 = Category.create(unique_category1_name)
    assert category1 is not None, "First category creation should succeed"
    
    # Create a second category with a different name
    unique_category2_name = f"Different_{category_name}_{uuid.uuid4().hex[:8]}"
    category2 = Category.create(unique_category2_name)
    assert category2 is not None, "Second category creation should succeed"
    
    # Arrange: Create a product in category1
    product1 = Product.create(
        product_name=product_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category1.category_id
    )
    assert product1 is not None, "Product 1 creation should succeed"
    
    # Arrange: Create a product in category2
    product2_name = f"Other_{product_name}"
    product2 = Product.create(
        product_name=product2_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category2.category_id
    )
    assert product2 is not None, "Product 2 creation should succeed"
    
    # Act: Filter products by category1
    filtered_products = Product.get_all(category_id=category1.category_id)
    
    # Assert: At least one product should be returned
    assert len(filtered_products) >= 1, \
        "Filtered results should contain at least one product"
    
    # Assert: All returned products should belong to category1
    for product in filtered_products:
        assert product.category_id == category1.category_id, \
            f"All filtered products should have category_id={category1.category_id}, " \
            f"but found product with category_id={product.category_id}"
    
    # Assert: Our product1 should be in the filtered results
    product1_found = any(p.product_id == product1.product_id for p in filtered_products)
    assert product1_found, \
        "Product from the filtered category should be included in results"
    
    # Assert: Product2 (from different category) should NOT be in the filtered results
    product2_found = any(p.product_id == product2.product_id for p in filtered_products)
    assert not product2_found, \
        "Products from other categories should NOT be included in filtered results"
    
    # Act: Filter products by category2
    filtered_products2 = Product.get_all(category_id=category2.category_id)
    
    # Assert: Product2 should be in category2 results
    product2_found_in_cat2 = any(p.product_id == product2.product_id for p in filtered_products2)
    assert product2_found_in_cat2, \
        "Product from category2 should be included when filtering by category2"
    
    # Assert: Product1 should NOT be in category2 results
    product1_found_in_cat2 = any(p.product_id == product1.product_id for p in filtered_products2)
    assert not product1_found_in_cat2, \
        "Product from category1 should NOT be included when filtering by category2"


@settings(max_examples=20, deadline=None)
@given(
    category_name=valid_category_names,
    product_name=valid_product_names,
    description=valid_descriptions,
    price=valid_prices,
    stock_quantity=valid_stock_quantities,
    image_url=valid_image_urls,
    search_term=st.text(
        alphabet=st.characters(min_codepoint=48, max_codepoint=122, blacklist_characters='%_\\'),
        min_size=1,
        max_size=20
    ).filter(lambda x: len(x.strip()) > 0)
)
@pytest.mark.usefixtures('clean_products_and_categories')
def test_property_search_term_matching(
    category_name, product_name, description, price, stock_quantity, image_url, search_term
):
    """
    Property 12: Search term matching
    
    **Validates: Requirements 3.3**
    
    For any search query, all returned products should have product_name containing
    the search term (case-insensitive). This ensures that search functionality works
    correctly and returns relevant results.
    
    Property: ∀ (search_term, products) →
              Product.get_all(search_term=search_term) returns only products where:
              - search_term.lower() in product.product_name.lower()
    """
    # Arrange: Create a category with unique name
    import uuid
    unique_category_name = f"{category_name}_{uuid.uuid4().hex[:8]}"
    category = Category.create(unique_category_name)
    assert category is not None, "Category creation should succeed"
    
    # Arrange: Create a product with the search term embedded in its name
    # This ensures we have at least one matching product
    # Use a safe format that won't conflict with SQL wildcards
    product_with_search_term = f"Product_{search_term}_test"
    product1 = Product.create(
        product_name=product_with_search_term,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category.category_id
    )
    assert product1 is not None, "Product 1 creation should succeed"
    
    # Arrange: Create a product that does NOT contain the search term
    # Use a completely different string that won't match
    non_matching_name = "ZZZZZ_NOMATCH_ZZZZZ_UNIQUE"
    assume(search_term.lower() not in non_matching_name.lower())
    
    product2 = Product.create(
        product_name=non_matching_name,
        description=description,
        price=float(price),
        stock_quantity=stock_quantity,
        image_url=image_url,
        category_id=category.category_id
    )
    assert product2 is not None, "Product 2 creation should succeed"
    
    # Act: Search for products using the search term
    search_results = Product.get_all(search_term=search_term)
    
    # Assert: At least one product should be returned (the matching one)
    assert len(search_results) >= 1, \
        f"Search should return at least one product matching '{search_term}'"
    
    # Assert: All returned products should contain the search term (case-insensitive)
    for product in search_results:
        assert search_term.lower() in product.product_name.lower(), \
            f"Product name '{product.product_name}' should contain search term '{search_term}' " \
            f"(case-insensitive)"
    
    # Assert: Our matching product should be in the results
    product1_found = any(p.product_id == product1.product_id for p in search_results)
    assert product1_found, \
        f"Product with name containing '{search_term}' should be in search results"
    
    # Assert: The non-matching product should NOT be in the results
    product2_found = any(p.product_id == product2.product_id for p in search_results)
    assert not product2_found, \
        f"Product with name '{non_matching_name}' should NOT be in search results " \
        f"for search term '{search_term}'"
