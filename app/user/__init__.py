"""User blueprint for customer-facing features"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth.decorators import login_required
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.order import Order, OrderItem
from app.database.db_universal import Database
from app.utils.validation import validate_cart_quantity, validate_positive_integer
from app.utils.error_handler import log_error, get_user_friendly_message

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/products')
@login_required
def browse_products():
    """
    Display product catalog with optional category filter and search
    
    Query Parameters:
        category_id: Optional category ID to filter products
        search: Optional search term to filter by product name
    
    Validates: Requirements 3.1, 3.2, 3.3, 11.1
    """
    category_id = request.args.get('category_id', type=int)
    search_term = request.args.get('search', '').strip()
    
    # Validate category_id if provided
    if category_id is not None:
        cat_valid, cat_value, cat_error = validate_positive_integer(
            category_id, field_name="Category ID", min_value=1
        )
        if not cat_valid:
            flash(cat_error, 'error')
            category_id = None
    
    try:
        # Get all categories for the filter dropdown
        categories = Category.get_all()
        
        # Get products with optional filters
        products = Product.get_all(
            category_id=category_id,
            search_term=search_term if search_term else None
        )
        
        return render_template(
            'user/products.html',
            products=products,
            categories=categories,
            selected_category=category_id,
            search_term=search_term
        )
    except Exception as e:
        log_error(e, "browse_products")
        flash('Error loading products. Please try again.', 'error')
        return render_template(
            'user/products.html',
            products=[],
            categories=[],
            selected_category=None,
            search_term=''
        )


@user_bp.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    """
    Display detailed product information
    
    Args:
        product_id: ID of the product to display
    
    Validates: Requirements 3.4, 3.5, 11.5
    """
    try:
        product = Product.get_by_id(product_id)
        
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('user.browse_products'))
        
        # Get category information
        categories = Category.get_all()
        category_name = None
        for cat in categories:
            if cat.category_id == product.category_id:
                category_name = cat.category_name
                break
        
        return render_template(
            'user/product_detail.html',
            product=product,
            category_name=category_name
        )
    except Exception as e:
        log_error(e, "product_detail")
        flash('Error loading product details. Please try again.', 'error')
        return redirect(url_for('user.browse_products'))


@user_bp.route('/cart')
@login_required
def view_cart():
    """
    Display user's shopping cart with items and total
    
    Validates: Requirements 4.5, 4.6, 11.5
    """
    try:
        user_id = session.get('user_id')
        cart_items = Cart.get_user_cart(user_id)
        total = Cart.calculate_total(user_id)
        
        return render_template(
            'user/cart.html',
            cart_items=cart_items,
            total=total
        )
    except Exception as e:
        log_error(e, "view_cart")
        flash('Error loading cart. Please try again.', 'error')
        return render_template(
            'user/cart.html',
            cart_items=[],
            total=0.0
        )


@user_bp.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """
    Add product to user's cart with stock validation
    
    Args:
        product_id: ID of the product to add
    
    Form Data:
        quantity: Quantity to add (default: 1)
    
    Validates: Requirements 4.1, 4.2, 11.1
    """
    try:
        user_id = session.get('user_id')
        quantity = request.form.get('quantity', 1)
        
        # Validate quantity
        qty_valid, qty_value, qty_error = validate_cart_quantity(quantity)
        if not qty_valid:
            flash(qty_error, 'error')
            return redirect(url_for('user.product_detail', product_id=product_id))
        
        Cart.add_item(user_id, product_id, qty_value)
        flash('Product added to cart successfully', 'success')
        return redirect(url_for('user.view_cart'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('user.product_detail', product_id=product_id))
    except Exception as e:
        log_error(e, "add_to_cart")
        flash('Error adding product to cart. Please try again.', 'error')
        return redirect(url_for('user.product_detail', product_id=product_id))


@user_bp.route('/cart/update/<int:cart_id>', methods=['POST'])
@login_required
def update_cart_item(cart_id):
    """
    Update quantity of cart item with stock validation
    
    Args:
        cart_id: ID of the cart item to update
    
    Form Data:
        quantity: New quantity
    
    Validates: Requirements 4.3, 11.1
    """
    try:
        quantity = request.form.get('quantity', 0)
        
        # Validate quantity (allow 0 for removal)
        qty_valid, qty_value, qty_error = validate_positive_integer(
            quantity, field_name="Quantity", min_value=0, max_value=9999
        )
        if not qty_valid:
            flash(qty_error, 'error')
            return redirect(url_for('user.view_cart'))
        
        Cart.update_quantity(cart_id, qty_value)
        
        if qty_value == 0:
            flash('Item removed from cart', 'success')
        else:
            flash('Cart updated successfully', 'success')
        
        return redirect(url_for('user.view_cart'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('user.view_cart'))
    except Exception as e:
        log_error(e, "update_cart_item")
        flash('Error updating cart. Please try again.', 'error')
        return redirect(url_for('user.view_cart'))


@user_bp.route('/cart/remove/<int:cart_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_id):
    """
    Remove item from cart
    
    Args:
        cart_id: ID of the cart item to remove
    
    Validates: Requirements 4.4, 11.5
    """
    try:
        Cart.remove_item(cart_id)
        flash('Item removed from cart successfully', 'success')
        return redirect(url_for('user.view_cart'))
        
    except Exception as e:
        log_error(e, "remove_from_cart")
        flash('Error removing item from cart. Please try again.', 'error')
        return redirect(url_for('user.view_cart'))


@user_bp.route('/orders')
@login_required
def view_order_history():
    """
    Display user's order history
    
    Validates: Requirements 6.1, 11.5
    """
    user_id = session.get('user_id')
    
    try:
        # Query all orders for current user
        orders = Order.get_user_orders(user_id)
        
        return render_template(
            'user/order_history.html',
            orders=orders
        )
    except Exception as e:
        log_error(e, "view_order_history")
        flash('Error loading order history. Please try again.', 'error')
        return render_template(
            'user/order_history.html',
            orders=[]
        )


@user_bp.route('/orders/<int:order_id>')
@login_required
def view_order_detail(order_id):
    """
    Display detailed order information
    
    Args:
        order_id: ID of the order to display
    
    Validates: Requirements 6.2, 11.5
    """
    user_id = session.get('user_id')
    
    try:
        # Verify order exists and belongs to current user
        order = Order.get_by_id(order_id)
        
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('user.view_order_history'))
        
        if order.user_id != user_id:
            flash('Unauthorized access to order', 'error')
            return redirect(url_for('user.view_order_history'))
        
        # Get order items with product details
        order_items = OrderItem.get_order_items(order_id)
        
        return render_template(
            'user/order_detail.html',
            order=order,
            order_items=order_items
        )
    except Exception as e:
        log_error(e, "view_order_detail")
        flash('Error loading order details. Please try again.', 'error')
        return redirect(url_for('user.view_order_history'))


@user_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def place_order():
    """
    Process order from cart with database transaction
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.6
    """
    user_id = session.get('user_id')
    
    if request.method == 'GET':
        # Display checkout page
        try:
            cart_items = Cart.get_user_cart(user_id)
            
            if not cart_items:
                flash('Your cart is empty. Add items before checkout.', 'error')
                return redirect(url_for('user.view_cart'))
            
            total = Cart.calculate_total(user_id)
            
            return render_template(
                'user/checkout.html',
                cart_items=cart_items,
                total=total
            )
        except Exception as e:
            flash('Error loading checkout page. Please try again.', 'error')
            return redirect(url_for('user.view_cart'))
    
    # POST - Process the order
    connection = None
    cursor = None
    try:
        # Get database connection for transaction
        connection = Database.get_connection()
        cursor = connection.cursor()
        
        # 1. Validate cart not empty
        cursor.execute(
            "SELECT COUNT(*) FROM cart WHERE user_id = %s",
            (user_id,)
        )
        cart_count = cursor.fetchone()[0]
        
        if cart_count == 0:
            flash('Your cart is empty. Cannot place order.', 'error')
            return redirect(url_for('user.view_cart'))
        
        # 2. Get cart items with product details
        cursor.execute("""
            SELECT c.product_id, c.quantity, p.price, p.stock_quantity, p.product_name
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """, (user_id,))
        cart_items = cursor.fetchall()
        
        # 3. Check stock for all items
        for product_id, quantity, price, stock_quantity, product_name in cart_items:
            if stock_quantity < quantity:
                flash(f'Insufficient stock for {product_name}. Available: {stock_quantity}, Requested: {quantity}', 'error')
                cursor.close()
                connection.close()
                return redirect(url_for('user.view_cart'))
        
        # 4. Calculate total amount
        total_amount = sum(quantity * float(price) for _, quantity, price, _, _ in cart_items)
        
        # 5. Create order record with 'Pending' status
        cursor.execute("""
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """, (user_id, total_amount))
        order_id = cursor.lastrowid
        
        # 6. Create order_items records
        for product_id, quantity, price, _, _ in cart_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (order_id, product_id, quantity, price))
        
        # 7. Reduce stock quantities
        for product_id, quantity, _, _, _ in cart_items:
            cursor.execute("""
                UPDATE products
                SET stock_quantity = stock_quantity - %s
                WHERE product_id = %s AND stock_quantity >= %s
            """, (quantity, product_id, quantity))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Insufficient stock for product {product_id}")
        
        # 8. Clear cart
        cursor.execute("DELETE FROM cart WHERE user_id = %s", (user_id,))
        
        # Commit transaction
        connection.commit()
        cursor.close()
        connection.close()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('user.simulate_payment', order_id=order_id))
        
    except Exception as e:
        # Rollback on any error
        if connection:
            connection.rollback()
            if cursor:
                cursor.close()
            connection.close()
        
        log_error(e, "place_order")
        flash('Error placing order. Please try again.', 'error')
        return redirect(url_for('user.view_cart'))


@user_bp.route('/payment/<int:order_id>', methods=['GET', 'POST'])
@login_required
def simulate_payment(order_id):
    """
    Simulate payment processing for an order
    
    Args:
        order_id: ID of the order to process payment for
    
    Validates: Requirements 5.5, 11.5
    """
    user_id = session.get('user_id')
    
    try:
        # Verify order exists and belongs to current user
        order = Order.get_by_id(order_id)
        
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('user.view_order_history'))
        
        if order.user_id != user_id:
            flash('Unauthorized access to order', 'error')
            return redirect(url_for('user.view_order_history'))
        
        if request.method == 'GET':
            # Display payment form
            return render_template(
                'user/payment.html',
                order=order
            )
        
        # POST - Process payment simulation
        # In a real system, this would integrate with a payment gateway
        # For simulation, we just confirm the order
        
        # Update order status to confirmed (keeping as Pending for now)
        # In a real system, you might change to 'Confirmed' or 'Processing'
        
        flash('Payment processed successfully!', 'success')
        return redirect(url_for('user.order_confirmation', order_id=order_id))
        
    except Exception as e:
        log_error(e, "simulate_payment")
        flash('Error processing payment. Please try again.', 'error')
        return redirect(url_for('user.view_order_history'))


@user_bp.route('/order-confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    """
    Display order confirmation page
    
    Args:
        order_id: ID of the confirmed order
    
    Validates: Requirements 13.1, 11.5
    """
    user_id = session.get('user_id')
    
    try:
        # Verify order exists and belongs to current user
        order = Order.get_by_id(order_id)
        
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('user.view_order_history'))
        
        if order.user_id != user_id:
            flash('Unauthorized access to order', 'error')
            return redirect(url_for('user.view_order_history'))
        
        # Get order items
        order_items = OrderItem.get_order_items(order_id)
        
        return render_template(
            'user/order_confirmation.html',
            order=order,
            order_items=order_items
        )
        
    except Exception as e:
        log_error(e, "order_confirmation")
        flash('Error loading order confirmation. Please try again.', 'error')
        return redirect(url_for('user.view_order_history'))




@user_bp.app_context_processor
def inject_cart_count():
    """
    Inject cart item count into all templates
    This makes cart_count available in all templates rendered by this blueprint
    """
    cart_count = 0
    if 'user_id' in session and session.get('role') == 'customer':
        try:
            cart_items = Cart.get_user_cart(session['user_id'])
            cart_count = len(cart_items) if cart_items else 0
        except Exception:
            cart_count = 0
    return dict(cart_count=cart_count)
