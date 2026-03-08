"""Property-based tests for admin order management"""

import pytest
import uuid
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderItem


# Feature: online-shopping-system, Property 24: Status update propagation
@given(
    new_status=st.sampled_from(['Pending', 'Shipped', 'Delivered'])
)
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.property_test
def test_status_update_propagation(test_db, new_status):
    """
    Property: For any order, when an admin updates the order_status, 
    the new status should be immediately visible in the customer's order history.
    
    **Validates: Requirements 6.3, 10.2**
    """
    try:
        # Generate unique identifier for this test run
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: Create test user (customer)
        user_email = f"test_status_{unique_id}@example.com"
        User.create("Test Customer", user_email, "password123", "customer")
        user = User.find_by_email(user_email)
        assume(user is not None)
        
        # Setup: Create category and product
        category = Category.create(f"Test Category Status {unique_id}")
        product = Product.create(
            f"Test Product {unique_id}",
            "Description",
            10.00,
            100,
            "image.jpg",
            category.category_id
        )
        
        # Setup: Create order with initial status 'Pending'
        order_id = Order.create(user.user_id, 10.00)
        OrderItem.create(order_id, product.product_id, 1, 10.00)
        
        # Verify initial status
        initial_order = Order.get_by_id(order_id)
        assert initial_order is not None, "Order should exist"
        assert initial_order.order_status == 'Pending', "Initial status should be Pending"
        
        # Action: Admin updates order status
        Order.update_status(order_id, new_status)
        
        # Verify: Status update is visible when querying by order ID
        updated_order = Order.get_by_id(order_id)
        assert updated_order is not None, "Order should still exist after update"
        assert updated_order.order_status == new_status, \
            f"Order status should be updated to {new_status}. Got: {updated_order.order_status}"
        
        # Verify: Status update is visible in customer's order history
        customer_orders = Order.get_user_orders(user.user_id)
        assert len(customer_orders) > 0, "Customer should have at least one order"
        
        # Find the updated order in customer's history
        found_order = None
        for order in customer_orders:
            if order.order_id == order_id:
                found_order = order
                break
        
        assert found_order is not None, \
            f"Order {order_id} should be in customer's order history"
        assert found_order.order_status == new_status, \
            f"Status in customer's order history should be {new_status}. Got: {found_order.order_status}"
        
        # Verify: Status update is visible in admin's all orders view
        all_orders = Order.get_all_orders()
        admin_order = None
        for order in all_orders:
            if order['order_id'] == order_id:
                admin_order = order
                break
        
        assert admin_order is not None, \
            f"Order {order_id} should be in admin's all orders view"
        assert admin_order['order_status'] == new_status, \
            f"Status in admin view should be {new_status}. Got: {admin_order['order_status']}"
        
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")


# Feature: online-shopping-system, Property 30: Admin order visibility
@given(
    num_customers=st.integers(min_value=2, max_value=5),
    orders_per_customer=st.integers(min_value=1, max_value=3)
)
@settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.property_test
def test_admin_order_visibility(test_db, num_customers, orders_per_customer):
    """
    Property: For any admin order listing, all orders from all users 
    should be returned with order details.
    
    **Validates: Requirements 10.1**
    """
    try:
        # Generate unique identifier for this test run
        unique_id = str(uuid.uuid4())[:8]
        
        # Setup: Create category and product
        category = Category.create(f"Test Category Admin {unique_id}")
        product = Product.create(
            f"Test Product {unique_id}",
            "Description",
            10.00,
            1000,
            "image.jpg",
            category.category_id
        )
        
        # Setup: Create multiple customers with orders
        created_order_ids = []
        customer_ids = []
        
        for i in range(num_customers):
            # Create customer
            customer_email = f"customer_{unique_id}_{i}@example.com"
            User.create(f"Customer {i}", customer_email, "password123", "customer")
            customer = User.find_by_email(customer_email)
            assume(customer is not None)
            customer_ids.append(customer.user_id)
            
            # Create orders for this customer
            for j in range(orders_per_customer):
                order_id = Order.create(customer.user_id, 10.00 * (j + 1))
                OrderItem.create(order_id, product.product_id, j + 1, 10.00)
                created_order_ids.append(order_id)
        
        # Action: Get all orders (admin view)
        all_orders = Order.get_all_orders()
        
        # Verify: All created orders are present in admin view
        returned_order_ids = [order['order_id'] for order in all_orders]
        
        for order_id in created_order_ids:
            assert order_id in returned_order_ids, \
                f"Order {order_id} should be visible in admin's all orders view"
        
        # Verify: Orders from all customers are included
        returned_user_ids = set(order['user_id'] for order in all_orders if order['order_id'] in created_order_ids)
        
        for customer_id in customer_ids:
            assert customer_id in returned_user_ids, \
                f"Orders from customer {customer_id} should be visible in admin view"
        
        # Verify: Each order has complete details
        for order in all_orders:
            if order['order_id'] in created_order_ids:
                # Check required fields
                assert 'order_id' in order, "Order should have order_id"
                assert 'user_id' in order, "Order should have user_id"
                assert 'total_amount' in order, "Order should have total_amount"
                assert 'order_date' in order, "Order should have order_date"
                assert 'order_status' in order, "Order should have order_status"
                assert 'user_name' in order, "Order should have user_name"
                assert 'user_email' in order, "Order should have user_email"
                
                # Verify user_id matches one of our created customers
                assert order['user_id'] in customer_ids, \
                    f"Order user_id should match one of the created customers"
                
                # Verify order status is valid
                assert order['order_status'] in ['Pending', 'Shipped', 'Delivered'], \
                    f"Order status should be valid. Got: {order['order_status']}"
        
        # Verify: At least the expected number of orders are returned
        matching_orders = [o for o in all_orders if o['order_id'] in created_order_ids]
        expected_total = num_customers * orders_per_customer
        assert len(matching_orders) == expected_total, \
            f"Should return exactly {expected_total} orders. Got: {len(matching_orders)}"
        
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")
