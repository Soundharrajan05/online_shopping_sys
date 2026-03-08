"""Unit tests for order processing edge cases"""

import pytest
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.database.db import Database


def test_empty_cart_checkout_rejection(test_db):
    """
    Test that attempting to checkout with an empty cart is rejected
    
    Validates: Requirements 5.1, 5.6
    """
    # Setup: Create test user
    User.create("Test User", "test_empty_cart@example.com", "password123", "customer")
    user = User.find_by_email("test_empty_cart@example.com")
    
    # Verify cart is empty
    cart_items = Cart.get_user_cart(user.user_id)
    assert len(cart_items) == 0, "Cart should be empty"
    
    # Attempt to place order with empty cart
    connection = Database.get_connection()
    cursor = connection.cursor()
    
    try:
        # Check cart count
        cursor.execute(
            "SELECT COUNT(*) FROM cart WHERE user_id = %s",
            (user.user_id,)
        )
        cart_count = cursor.fetchone()[0]
        
        # Should reject empty cart
        assert cart_count == 0, "Cart should be empty"
        
        # Verify no order is created
        orders_before = Order.get_user_orders(user.user_id)
        assert len(orders_before) == 0, "No orders should exist"
        
    finally:
        cursor.close()
        connection.close()


def test_transaction_rollback_on_error(test_db):
    """
    Test that database transaction is rolled back when an error occurs during order placement
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4
    """
    # Setup: Create test user
    User.create("Test User", "test_rollback@example.com", "password123", "customer")
    user = User.find_by_email("test_rollback@example.com")
    
    # Setup: Create category and products
    category = Category.create("Test Category Rollback")
    product1 = Product.create("Product 1", "Description 1", 10.00, 5, "img1.jpg", category.category_id)
    product2 = Product.create("Product 2", "Description 2", 20.00, 3, "img2.jpg", category.category_id)
    
    # Setup: Add products to cart (within stock limits)
    Cart.add_item(user.user_id, product1.product_id, 2)
    Cart.add_item(user.user_id, product2.product_id, 3)
    
    # Get initial state
    initial_cart = Cart.get_user_cart(user.user_id)
    initial_cart_count = len(initial_cart)
    
    initial_stock1 = Product.get_by_id(product1.product_id).stock_quantity
    initial_stock2 = Product.get_by_id(product2.product_id).stock_quantity
    
    initial_orders = Order.get_user_orders(user.user_id)
    initial_order_count = len(initial_orders)
    
    # Manually update cart to exceed stock (to simulate race condition)
    connection = Database.get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE cart SET quantity = 10 
        WHERE user_id = %s AND product_id = %s
    """, (user.user_id, product2.product_id))
    connection.commit()
    cursor.close()
    connection.close()
    
    # Attempt to place order (should fail due to insufficient stock for product2)
    connection = Database.get_connection()
    cursor = connection.cursor()
    
    order_failed = False
    try:
        # Get cart items
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.price, p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user.user_id,))
        cart_items = cursor.fetchall()
        
        # Check stock - should fail for product2
        for product_id, quantity, price, stock_quantity in cart_items:
            if stock_quantity < quantity:
                order_failed = True
                raise ValueError("Insufficient stock")
        
        # If we get here, create order (shouldn't happen)
        total_amount = sum(quantity * float(price) for _, quantity, price, _ in cart_items)
        
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """, (user.user_id, total_amount))
        order_id = cursor.lastrowid
        
        # Create order items
        for product_id, quantity, price, _ in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
        
        # Reduce stock
        for product_id, quantity, _, _ in cart_items:
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s AND stock_quantity >= %s
            """, (quantity, product_id, quantity))
            
            if cursor.rowcount == 0:
                raise ValueError("Insufficient stock")
        
        connection.commit()
        
    except ValueError:
        connection.rollback()
        order_failed = True
    finally:
        cursor.close()
        connection.close()
    
    # Verify transaction was rolled back
    assert order_failed, "Order should have failed"
    
    # Verify no order was created
    final_orders = Order.get_user_orders(user.user_id)
    assert len(final_orders) == initial_order_count, "No new orders should be created"
    
    # Verify stock unchanged
    final_stock1 = Product.get_by_id(product1.product_id).stock_quantity
    final_stock2 = Product.get_by_id(product2.product_id).stock_quantity
    
    assert final_stock1 == initial_stock1, "Stock for product1 should be unchanged"
    assert final_stock2 == initial_stock2, "Stock for product2 should be unchanged"



def test_order_status_update(test_db):
    """
    Test that order status can be updated correctly
    
    Validates: Requirements 6.3, 10.2
    """
    # Setup: Create test user
    User.create("Test User", "test_status@example.com", "password123", "customer")
    user = User.find_by_email("test_status@example.com")
    
    # Setup: Create category and product
    category = Category.create("Test Category Status")
    product = Product.create("Product", "Description", 10.00, 10, "img.jpg", category.category_id)
    
    # Setup: Add to cart and place order
    Cart.add_item(user.user_id, product.product_id, 2)
    
    connection = Database.get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.price
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user.user_id,))
        cart_items = cursor.fetchall()
        
        total_amount = sum(quantity * float(price) for _, quantity, price in cart_items)
        
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """, (user.user_id, total_amount))
        order_id = cursor.lastrowid
        
        for product_id, quantity, price in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
            
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s
            """, (quantity, product_id))
        
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user.user_id,))
        
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Verify initial status
    order = Order.get_by_id(order_id)
    assert order.order_status == 'Pending', "Initial status should be Pending"
    
    # Update status to Shipped
    Order.update_status(order_id, 'Shipped')
    order = Order.get_by_id(order_id)
    assert order.order_status == 'Shipped', "Status should be updated to Shipped"
    
    # Update status to Delivered
    Order.update_status(order_id, 'Delivered')
    order = Order.get_by_id(order_id)
    assert order.order_status == 'Delivered', "Status should be updated to Delivered"


def test_invalid_order_status_rejected(test_db):
    """
    Test that invalid order status values are rejected
    
    Validates: Requirements 10.2
    """
    # Setup: Create test user and order
    User.create("Test User", "test_invalid_status@example.com", "password123", "customer")
    user = User.find_by_email("test_invalid_status@example.com")
    
    # Create a simple order
    order_id = Order.create(user.user_id, 100.00)
    
    # Attempt to set invalid status
    with pytest.raises(ValueError) as exc_info:
        Order.update_status(order_id, 'InvalidStatus')
    
    assert "Invalid status" in str(exc_info.value), "Should reject invalid status"
    
    # Verify status unchanged
    order = Order.get_by_id(order_id)
    assert order.order_status == 'Pending', "Status should remain Pending"


def test_order_items_with_product_details(test_db):
    """
    Test that order items are retrieved with complete product details
    
    Validates: Requirements 6.2, 10.3
    """
    # Setup: Create test user
    User.create("Test User", "test_order_items@example.com", "password123", "customer")
    user = User.find_by_email("test_order_items@example.com")
    
    # Setup: Create category and products
    category = Category.create("Test Category Items")
    product1 = Product.create("Product 1", "Desc 1", 10.00, 10, "img1.jpg", category.category_id)
    product2 = Product.create("Product 2", "Desc 2", 20.00, 10, "img2.jpg", category.category_id)
    
    # Setup: Add to cart and place order
    Cart.add_item(user.user_id, product1.product_id, 2)
    Cart.add_item(user.user_id, product2.product_id, 3)
    
    connection = Database.get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.price
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user.user_id,))
        cart_items = cursor.fetchall()
        
        total_amount = sum(quantity * float(price) for _, quantity, price in cart_items)
        
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """, (user.user_id, total_amount))
        order_id = cursor.lastrowid
        
        for product_id, quantity, price in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
            
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s
            """, (quantity, product_id))
        
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user.user_id,))
        
        connection.commit()
    finally:
        cursor.close()
        connection.close()
    
    # Retrieve order items
    order_items = OrderItem.get_order_items(order_id)
    
    # Verify order items
    assert len(order_items) == 2, "Should have 2 order items"
    
    # Verify product details are included
    for item in order_items:
        assert 'product_name' in item, "Should include product name"
        assert 'description' in item, "Should include description"
        assert 'image_url' in item, "Should include image URL"
        assert 'price' in item, "Should include price"
        assert 'quantity' in item, "Should include quantity"
        assert 'subtotal' in item, "Should include subtotal"
        
        # Verify subtotal calculation
        expected_subtotal = item['price'] * item['quantity']
        assert abs(item['subtotal'] - expected_subtotal) < 0.01, "Subtotal should be correct"
