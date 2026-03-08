"""Integration tests for complete user workflows"""

import pytest
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.order import Order, OrderItem


class TestCustomerWorkflow:
    """Test complete customer workflow: register → browse → cart → order"""
    
    def test_complete_customer_journey(self, client, test_db):
        """
        Integration test for complete customer workflow
        
        Tests the following flow:
        1. Register a new customer account
        2. Login with the new account
        3. Browse products
        4. Add products to cart
        5. View cart
        6. Place order
        7. View order history
        8. View order details
        """
        # Step 1: Register a new customer account
        register_response = client.post('/auth/register', data={
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'SecurePass123'
        }, follow_redirects=True)
        
        assert register_response.status_code == 200
        assert b'Registration successful' in register_response.data or b'login' in register_response.data.lower()
        
        # Step 2: Login with the new account
        login_response = client.post('/auth/login', data={
            'email': 'john.doe@example.com',
            'password': 'SecurePass123'
        }, follow_redirects=True)
        
        assert login_response.status_code == 200
        assert b'Welcome' in register_response.data or b'products' in login_response.data.lower()
        
        # Verify session was created
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['role'] == 'customer'
        
        # Step 3: Create test data - categories and products
        category = Category.create('Electronics')
        category_id = category.category_id
        product1_id = Product.create('Laptop', 'Gaming laptop', 999.99, 10, 'laptop.jpg', category_id).product_id
        product2_id = Product.create('Mouse', 'Wireless mouse', 29.99, 50, 'mouse.jpg', category_id).product_id
        
        # Browse products
        browse_response = client.get('/user/products')
        assert browse_response.status_code == 200
        assert b'Laptop' in browse_response.data
        assert b'Mouse' in browse_response.data
        
        # Step 4: Add products to cart
        add_cart_response1 = client.post(f'/user/cart/add/{product1_id}', data={
            'quantity': 1
        }, follow_redirects=True)
        assert add_cart_response1.status_code == 200
        assert b'added to cart' in add_cart_response1.data.lower() or b'cart' in add_cart_response1.data.lower()
        
        add_cart_response2 = client.post(f'/user/cart/add/{product2_id}', data={
            'quantity': 2
        }, follow_redirects=True)
        assert add_cart_response2.status_code == 200
        
        # Step 5: View cart
        cart_response = client.get('/user/cart')
        assert cart_response.status_code == 200
        assert b'Laptop' in cart_response.data
        assert b'Mouse' in cart_response.data
        
        # Verify cart total calculation
        with client.session_transaction() as sess:
            user_id = sess['user_id']
        
        cart_total = Cart.calculate_total(user_id)
        expected_total = 999.99 + (29.99 * 2)
        assert abs(cart_total - expected_total) < 0.01
        
        # Step 6: Place order
        checkout_response = client.get('/user/checkout')
        assert checkout_response.status_code == 200
        
        place_order_response = client.post('/user/checkout', follow_redirects=True)
        assert place_order_response.status_code == 200
        assert b'Order placed successfully' in place_order_response.data or b'payment' in place_order_response.data.lower()
        
        # Verify order was created
        orders = Order.get_user_orders(user_id)
        assert len(orders) == 1
        assert abs(float(orders[0].total_amount) - expected_total) < 0.01
        
        # Verify cart was cleared
        cart_items = Cart.get_user_cart(user_id)
        assert len(cart_items) == 0
        
        # Verify stock was reduced
        updated_product1 = Product.get_by_id(product1_id)
        updated_product2 = Product.get_by_id(product2_id)
        assert updated_product1.stock_quantity == 9  # 10 - 1
        assert updated_product2.stock_quantity == 48  # 50 - 2
        
        # Step 7: View order history
        order_history_response = client.get('/user/orders')
        assert order_history_response.status_code == 200
        assert b'Pending' in order_history_response.data or b'order' in order_history_response.data.lower()
        
        # Step 8: View order details
        order_id = orders[0].order_id
        order_detail_response = client.get(f'/user/orders/{order_id}')
        assert order_detail_response.status_code == 200
        assert b'Laptop' in order_detail_response.data
        assert b'Mouse' in order_detail_response.data


class TestAdminWorkflow:
    """Test complete admin workflow: login → manage products → manage orders"""
    
    def test_complete_admin_journey(self, client, test_db):
        """
        Integration test for complete admin workflow
        
        Tests the following flow:
        1. Create admin user
        2. Login as admin
        3. Access admin dashboard
        4. Create category
        5. Create product
        6. Update product
        7. View all users
        8. View all orders
        9. Update order status
        """
        # Step 1: Create admin user
        admin_id = User.create('Admin User', 'admin@shop.com', 'admin123', role='admin')
        assert admin_id is not None
        
        # Step 2: Login as admin
        login_response = client.post('/auth/login', data={
            'email': 'admin@shop.com',
            'password': 'admin123'
        }, follow_redirects=True)
        
        assert login_response.status_code == 200
        
        # Verify admin session
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert sess['role'] == 'admin'
        
        # Step 3: Access admin dashboard
        dashboard_response = client.get('/admin/dashboard')
        assert dashboard_response.status_code == 200
        assert b'dashboard' in dashboard_response.data.lower() or b'admin' in dashboard_response.data.lower()
        
        # Step 4: Create category
        category_response = client.post('/admin/categories/add', data={
            'category_name': 'Electronics'
        }, follow_redirects=True)
        assert category_response.status_code == 200
        assert b'Electronics' in category_response.data or b'added successfully' in category_response.data.lower()
        
        # Verify category was created
        categories = Category.get_all()
        assert len(categories) == 1
        assert categories[0].category_name == 'Electronics'
        category_id = categories[0].category_id
        
        # Step 5: Create product
        add_product_response = client.post('/admin/products/add', data={
            'product_name': 'Test Laptop',
            'description': 'A test laptop for integration testing',
            'price': '1299.99',
            'stock_quantity': '25',
            'image_url': 'https://example.com/laptop.jpg',
            'category_id': str(category_id)
        }, follow_redirects=True)
        assert add_product_response.status_code == 200
        assert b'added successfully' in add_product_response.data.lower() or b'Test Laptop' in add_product_response.data
        
        # Verify product was created
        products = Product.get_all()
        assert len(products) == 1
        assert products[0].product_name == 'Test Laptop'
        assert products[0].stock_quantity == 25
        product_id = products[0].product_id
        
        # Step 6: Update product
        update_product_response = client.post(f'/admin/products/edit/{product_id}', data={
            'product_name': 'Test Laptop Pro',
            'description': 'An updated test laptop',
            'price': '1499.99',
            'stock_quantity': '30',
            'image_url': 'https://example.com/laptop-pro.jpg',
            'category_id': str(category_id)
        }, follow_redirects=True)
        assert update_product_response.status_code == 200
        assert b'updated successfully' in update_product_response.data.lower() or b'Test Laptop Pro' in update_product_response.data
        
        # Verify product was updated
        updated_product = Product.get_by_id(product_id)
        assert updated_product.product_name == 'Test Laptop Pro'
        assert updated_product.stock_quantity == 30
        assert abs(float(updated_product.price) - 1499.99) < 0.01
        
        # Step 7: View all users
        users_response = client.get('/admin/users')
        assert users_response.status_code == 200
        assert b'admin@shop.com' in users_response.data
        
        # Step 8: Create a test order to manage
        # First create a customer
        customer_id = User.create('Test Customer', 'customer@test.com', 'password123', role='customer')
        
        # Create an order for the customer
        Cart.add_item(customer_id, product_id, 2)
        
        # Place order using model methods directly
        from app.database.db import Database
        connection = Database.get_connection()
        cursor = connection.cursor()
        
        try:
            # Create order
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, order_status)
                VALUES (%s, %s, 'Pending')
            """, (customer_id, 2999.98))
            order_id = cursor.lastrowid
            
            # Create order items
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, 2, 1499.99))
            
            # Reduce stock
            cursor.execute("""
                UPDATE products SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s
            """, (2, product_id))
            
            # Clear cart
            cursor.execute("DELETE FROM cart WHERE user_id = %s", (customer_id,))
            
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        
        # View all orders
        orders_response = client.get('/admin/orders')
        assert orders_response.status_code == 200
        assert b'Pending' in orders_response.data or b'order' in orders_response.data.lower()
        
        # Step 9: Update order status
        update_status_response = client.post(f'/admin/orders/{order_id}/update-status', data={
            'order_status': 'Shipped'
        }, follow_redirects=True)
        assert update_status_response.status_code == 200
        assert b'Shipped' in update_status_response.data or b'updated' in update_status_response.data.lower()
        
        # Verify order status was updated
        updated_order = Order.get_by_id(order_id)
        assert updated_order.order_status == 'Shipped'


class TestAuthorizationBoundaries:
    """Test authorization boundaries between customer and admin roles"""
    
    def test_customer_cannot_access_admin_routes(self, client, test_db):
        """
        Test that customers are denied access to admin routes
        
        Validates: Requirements 2.2
        """
        # Create and login as customer
        customer_id = User.create('Customer User', 'customer@test.com', 'password123', role='customer')
        
        login_response = client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        assert login_response.status_code in [200, 302]
        
        # Verify customer session
        with client.session_transaction() as sess:
            assert sess['role'] == 'customer'
        
        # Attempt to access admin dashboard
        dashboard_response = client.get('/admin/dashboard', follow_redirects=False)
        assert dashboard_response.status_code == 302  # Should redirect
        
        # Attempt to access admin categories
        categories_response = client.get('/admin/categories', follow_redirects=False)
        assert categories_response.status_code == 302
        
        # Attempt to access admin products
        products_response = client.get('/admin/products', follow_redirects=False)
        assert products_response.status_code == 302
        
        # Attempt to access admin users
        users_response = client.get('/admin/users', follow_redirects=False)
        assert users_response.status_code == 302
        
        # Attempt to access admin orders
        orders_response = client.get('/admin/orders', follow_redirects=False)
        assert orders_response.status_code == 302
    
    def test_admin_can_access_admin_routes(self, client, test_db):
        """
        Test that admins can access admin routes
        
        Validates: Requirements 2.3
        """
        # Create and login as admin
        admin_id = User.create('Admin User', 'admin@test.com', 'admin123', role='admin')
        
        login_response = client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'admin123'
        }, follow_redirects=False)
        
        assert login_response.status_code in [200, 302]
        
        # Verify admin session
        with client.session_transaction() as sess:
            assert sess['role'] == 'admin'
        
        # Access admin dashboard
        dashboard_response = client.get('/admin/dashboard')
        assert dashboard_response.status_code == 200
        
        # Access admin categories
        categories_response = client.get('/admin/categories')
        assert categories_response.status_code == 200
        
        # Access admin products
        products_response = client.get('/admin/products')
        assert products_response.status_code == 200
        
        # Access admin users
        users_response = client.get('/admin/users')
        assert users_response.status_code == 200
        
        # Access admin orders
        orders_response = client.get('/admin/orders')
        assert orders_response.status_code == 200
    
    def test_unauthenticated_user_cannot_access_protected_routes(self, client, test_db):
        """
        Test that unauthenticated users are redirected to login
        
        Validates: Requirements 12.4
        """
        # Attempt to access customer routes without login
        products_response = client.get('/user/products', follow_redirects=False)
        assert products_response.status_code == 302  # Should redirect to login
        
        cart_response = client.get('/user/cart', follow_redirects=False)
        assert cart_response.status_code == 302
        
        orders_response = client.get('/user/orders', follow_redirects=False)
        assert orders_response.status_code == 302
        
        # Attempt to access admin routes without login
        dashboard_response = client.get('/admin/dashboard', follow_redirects=False)
        assert dashboard_response.status_code == 302
        
        categories_response = client.get('/admin/categories', follow_redirects=False)
        assert categories_response.status_code == 302
    
    def test_customer_can_only_view_own_orders(self, client, test_db):
        """
        Test that customers can only view their own orders
        
        Validates: Requirements 6.1, 11.4
        """
        # Create two customers
        customer1_id = User.create('Customer One', 'customer1@test.com', 'password123', role='customer')
        customer2_id = User.create('Customer Two', 'customer2@test.com', 'password123', role='customer')
        
        # Create a product
        category = Category.create('Electronics')
        category_id = category.category_id
        product_id = Product.create('Laptop', 'Test laptop', 999.99, 10, 'laptop.jpg', category_id).product_id
        
        # Create order for customer1
        from app.database.db import Database
        connection = Database.get_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, order_status)
                VALUES (%s, %s, 'Pending')
            """, (customer1_id, 999.99))
            customer1_order_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (customer1_order_id, product_id, 1, 999.99))
            
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        
        # Login as customer2
        login_response = client.post('/auth/login', data={
            'email': 'customer2@test.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Attempt to view customer1's order
        order_detail_response = client.get(f'/user/orders/{customer1_order_id}', follow_redirects=True)
        assert order_detail_response.status_code == 200
        # Should be redirected or show error
        assert b'Unauthorized' in order_detail_response.data or b'not found' in order_detail_response.data.lower()
    
    def test_session_persistence_across_requests(self, client, test_db):
        """
        Test that session persists across multiple requests
        
        Validates: Requirements 12.1, 12.2
        """
        # Create and login as customer
        customer_id = User.create('Test Customer', 'customer@test.com', 'password123', role='customer')
        
        login_response = client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Make multiple requests and verify session persists
        for _ in range(3):
            with client.session_transaction() as sess:
                assert 'user_id' in sess
                assert sess['role'] == 'customer'
                assert sess['user_id'] == customer_id
            
            # Make a request
            response = client.get('/user/products')
            assert response.status_code == 200
    
    def test_logout_clears_session(self, client, test_db):
        """
        Test that logout properly clears session data
        
        Validates: Requirements 1.6, 12.3
        """
        # Create and login as customer
        customer_id = User.create('Test Customer', 'customer@test.com', 'password123', role='customer')
        
        login_response = client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        }, follow_redirects=False)
        
        # Verify session exists
        with client.session_transaction() as sess:
            assert 'user_id' in sess
        
        # Logout
        logout_response = client.get('/auth/logout', follow_redirects=False)
        assert logout_response.status_code == 302
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'role' not in sess
        
        # Verify cannot access protected routes
        products_response = client.get('/user/products', follow_redirects=False)
        assert products_response.status_code == 302  # Should redirect to login


class TestCrossFunctionalIntegration:
    """Test cross-functional integration scenarios"""
    
    def test_order_status_update_visible_to_customer(self, client, test_db):
        """
        Test that admin order status updates are visible to customers
        
        Validates: Requirements 6.3, 10.2
        """
        # Create admin and customer
        admin_id = User.create('Admin', 'admin@test.com', 'admin123', role='admin')
        customer_id = User.create('Customer', 'customer@test.com', 'password123', role='customer')
        
        # Create product and order
        category = Category.create('Electronics')
        category_id = category.category_id
        product_id = Product.create('Laptop', 'Test laptop', 999.99, 10, 'laptop.jpg', category_id).product_id
        
        from app.database.db import Database
        connection = Database.get_connection()
        cursor = connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO orders (user_id, total_amount, order_status)
                VALUES (%s, %s, 'Pending')
            """, (customer_id, 999.99))
            order_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, 1, 999.99))
            
            connection.commit()
        finally:
            cursor.close()
            connection.close()
        
        # Login as admin and update order status
        client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'admin123'
        })
        
        update_response = client.post(f'/admin/orders/{order_id}/update-status', data={
            'order_status': 'Shipped'
        }, follow_redirects=True)
        assert update_response.status_code == 200
        
        # Logout admin
        client.get('/auth/logout')
        
        # Login as customer and verify status update is visible
        client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        order_detail_response = client.get(f'/user/orders/{order_id}')
        assert order_detail_response.status_code == 200
        assert b'Shipped' in order_detail_response.data
    
    def test_product_stock_consistency_across_operations(self, client, test_db):
        """
        Test that product stock remains consistent across cart and order operations
        
        Validates: Requirements 4.2, 5.3, 5.6
        """
        # Create customer and product
        customer_id = User.create('Customer', 'customer@test.com', 'password123', role='customer')
        category = Category.create('Electronics')
        category_id = category.category_id
        product = Product.create('Limited Item', 'Only 5 in stock', 99.99, 5, 'item.jpg', category_id)
        product_id = product.product_id
        
        # Login as customer
        client.post('/auth/login', data={
            'email': 'customer@test.com',
            'password': 'password123'
        })
        
        # Add 3 items to cart
        client.post(f'/user/cart/add/{product_id}', data={'quantity': 3})
        
        # Verify stock is still 5 (not reduced until order)
        product = Product.get_by_id(product_id)
        assert product.stock_quantity == 5
        
        # Place order
        client.post('/user/checkout', follow_redirects=True)
        
        # Verify stock is now 2
        product = Product.get_by_id(product_id)
        assert product.stock_quantity == 2
        
        # Try to add 3 more to cart (should fail - insufficient stock)
        add_response = client.post(f'/user/cart/add/{product_id}', data={'quantity': 3}, follow_redirects=True)
        assert b'Insufficient stock' in add_response.data or b'error' in add_response.data.lower()
