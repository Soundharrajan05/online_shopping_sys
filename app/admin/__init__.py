"""Admin blueprint for admin features"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.auth.decorators import admin_required
from app.database.db import Database
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.utils.validation import (
    validate_category_name, validate_product_name, validate_product_description,
    validate_price, validate_stock_quantity, validate_url, validate_order_status,
    validate_positive_integer
)
from app.utils.error_handler import log_error, get_user_friendly_message

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """
    Display admin dashboard with statistics and recent orders
    
    Queries:
    - Total number of users
    - Total number of products
    - Total number of orders
    - Recent orders (last 10)
    
    Validates: Requirements 15.1, 11.5
    """
    try:
        # Query total users
        total_users_query = "SELECT COUNT(*) FROM users"
        total_users_result = Database.execute_query(total_users_query, None, fetch=True)
        total_users = total_users_result[0][0] if total_users_result else 0
        
        # Query total products
        total_products_query = "SELECT COUNT(*) FROM products"
        total_products_result = Database.execute_query(total_products_query, None, fetch=True)
        total_products = total_products_result[0][0] if total_products_result else 0
        
        # Query total orders
        total_orders_query = "SELECT COUNT(*) FROM orders"
        total_orders_result = Database.execute_query(total_orders_query, None, fetch=True)
        total_orders = total_orders_result[0][0] if total_orders_result else 0
        
        # Query recent orders (last 10) with user information
        recent_orders_query = """
            SELECT o.order_id, o.user_id, o.total_amount, o.order_date, o.order_status,
                   u.name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.order_date DESC
            LIMIT 10
        """
        recent_orders_result = Database.execute_query(recent_orders_query, None, fetch=True)
        
        # Format recent orders
        recent_orders = []
        for row in recent_orders_result:
            recent_orders.append({
                'order_id': row[0],
                'user_id': row[1],
                'total_amount': float(row[2]),
                'order_date': row[3],
                'order_status': row[4],
                'user_name': row[5],
                'user_email': row[6]
            })
        
        return render_template(
            'admin/dashboard.html',
            total_users=total_users,
            total_products=total_products,
            total_orders=total_orders,
            recent_orders=recent_orders
        )
    except Exception as e:
        log_error(e, "admin_dashboard")
        flash('Failed to load dashboard statistics. Please try again.', 'error')
        return render_template(
            'admin/dashboard.html',
            total_users=0,
            total_products=0,
            total_orders=0,
            recent_orders=[]
        )


@admin_bp.route('/categories')
@admin_required
def manage_categories():
    """
    Display and manage categories
    
    Retrieves all categories from the database and displays them
    in the category management template.
    
    Validates: Requirements 7.2, 11.5
    """
    try:
        categories = Category.get_all()
        return render_template('admin/categories.html', categories=categories)
    except Exception as e:
        log_error(e, "manage_categories")
        flash('Failed to load categories. Please try again.', 'error')
        return render_template('admin/categories.html', categories=[])


@admin_bp.route('/categories/add', methods=['POST'])
@admin_required
def add_category():
    """
    Add a new category
    
    Validates that the category name doesn't already exist before creating.
    Displays error message if duplicate name is detected.
    
    Validates: Requirements 7.1, 7.3, 11.1
    """
    category_name = request.form.get('category_name', '')
    
    # Validate and sanitize category name
    is_valid, sanitized_name, error_msg = validate_category_name(category_name)
    if not is_valid:
        flash(error_msg, 'error')
        return redirect(url_for('admin.manage_categories'))
    
    try:
        # Check if category already exists
        if Category.exists(sanitized_name):
            flash(f'Category "{sanitized_name}" already exists', 'error')
            return redirect(url_for('admin.manage_categories'))
        
        # Create new category
        Category.create(sanitized_name)
        flash(f'Category "{sanitized_name}" added successfully', 'success')
    except Exception as e:
        log_error(e, "add_category")
        flash('Failed to add category. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_categories'))



@admin_bp.route('/products')
@admin_required
def manage_products():
    """
    Display all products for management
    
    Retrieves all products with their category information
    and displays them in the product management template.
    
    Validates: Requirements 8.5, 11.5
    """
    try:
        # Query all products with category information
        query = """
            SELECT p.product_id, p.product_name, p.description, p.price,
                   p.stock_quantity, p.image_url, p.category_id, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_name
        """
        results = Database.execute_query(query, None, fetch=True)
        
        products = []
        for row in results:
            products.append({
                'product_id': row[0],
                'product_name': row[1],
                'description': row[2],
                'price': float(row[3]),
                'stock_quantity': row[4],
                'image_url': row[5],
                'category_id': row[6],
                'category_name': row[7] if row[7] else 'Uncategorized'
            })
        
        return render_template('admin/products.html', products=products)
    except Exception as e:
        log_error(e, "manage_products")
        flash('Failed to load products. Please try again.', 'error')
        return render_template('admin/products.html', products=[])


@admin_bp.route('/products/add', methods=['GET', 'POST'])
@admin_required
def add_product():
    """
    Add a new product
    
    GET: Display the add product form with category dropdown
    POST: Validate input and create new product
    
    Validates: Requirements 8.1, 11.1
    """
    if request.method == 'GET':
        # Get all categories for dropdown
        try:
            categories = Category.get_all()
            return render_template('admin/add_product.html', categories=categories)
        except Exception as e:
            log_error(e, "add_product - load categories")
            flash('Failed to load categories. Please try again.', 'error')
            return render_template('admin/add_product.html', categories=[])
    
    # POST request - process form submission
    product_name = request.form.get('product_name', '')
    description = request.form.get('description', '')
    price = request.form.get('price', '')
    stock_quantity = request.form.get('stock_quantity', '')
    image_url = request.form.get('image_url', '')
    category_id = request.form.get('category_id', '')
    
    # Validate product name
    name_valid, sanitized_name, name_error = validate_product_name(product_name)
    if not name_valid:
        flash(name_error, 'error')
        return redirect(url_for('admin.add_product'))
    
    # Validate description
    desc_valid, sanitized_desc, desc_error = validate_product_description(description)
    if not desc_valid:
        flash(desc_error, 'error')
        return redirect(url_for('admin.add_product'))
    
    # Validate price
    price_valid, price_value, price_error = validate_price(price)
    if not price_valid:
        flash(price_error, 'error')
        return redirect(url_for('admin.add_product'))
    
    # Validate stock quantity
    stock_valid, stock_value, stock_error = validate_stock_quantity(stock_quantity)
    if not stock_valid:
        flash(stock_error, 'error')
        return redirect(url_for('admin.add_product'))
    
    # Validate image URL (optional)
    url_valid, sanitized_url, url_error = validate_url(image_url, field_name="Image URL", required=False)
    if not url_valid:
        flash(url_error, 'error')
        return redirect(url_for('admin.add_product'))
    
    # Validate category_id (optional)
    category_id_value = None
    if category_id:
        cat_valid, category_id_value, cat_error = validate_positive_integer(
            category_id, field_name="Category", min_value=1
        )
        if not cat_valid:
            flash(cat_error, 'error')
            return redirect(url_for('admin.add_product'))
    
    # Create product
    try:
        Product.create(
            sanitized_name, sanitized_desc, price_value, 
            stock_value, sanitized_url, category_id_value
        )
        flash(f'Product "{sanitized_name}" added successfully', 'success')
        return redirect(url_for('admin.manage_products'))
    except Exception as e:
        log_error(e, "add_product - create product")
        flash('Failed to add product. Please try again.', 'error')
        return redirect(url_for('admin.add_product'))


@admin_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def update_product(product_id):
    """
    Update an existing product
    
    GET: Display the edit product form with current values
    POST: Validate input and update product
    
    Validates: Requirements 8.2, 8.4, 11.1
    """
    if request.method == 'GET':
        # Get product and categories for form
        try:
            product = Product.get_by_id(product_id)
            if not product:
                flash('Product not found', 'error')
                return redirect(url_for('admin.manage_products'))
            
            categories = Category.get_all()
            return render_template('admin/edit_product.html', product=product, categories=categories)
        except Exception as e:
            log_error(e, "update_product - load product")
            flash('Failed to load product. Please try again.', 'error')
            return redirect(url_for('admin.manage_products'))
    
    # POST request - process form submission
    product_name = request.form.get('product_name', '')
    description = request.form.get('description', '')
    price = request.form.get('price', '')
    stock_quantity = request.form.get('stock_quantity', '')
    image_url = request.form.get('image_url', '')
    category_id = request.form.get('category_id', '')
    
    # Validate product name
    name_valid, sanitized_name, name_error = validate_product_name(product_name)
    if not name_valid:
        flash(name_error, 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Validate description
    desc_valid, sanitized_desc, desc_error = validate_product_description(description)
    if not desc_valid:
        flash(desc_error, 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Validate price
    price_valid, price_value, price_error = validate_price(price)
    if not price_valid:
        flash(price_error, 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Validate stock quantity
    stock_valid, stock_value, stock_error = validate_stock_quantity(stock_quantity)
    if not stock_valid:
        flash(stock_error, 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Validate image URL (optional)
    url_valid, sanitized_url, url_error = validate_url(image_url, field_name="Image URL", required=False)
    if not url_valid:
        flash(url_error, 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Validate category_id (optional)
    category_id_value = None
    if category_id:
        cat_valid, category_id_value, cat_error = validate_positive_integer(
            category_id, field_name="Category", min_value=1
        )
        if not cat_valid:
            flash(cat_error, 'error')
            return redirect(url_for('admin.update_product', product_id=product_id))
    
    # Update product
    try:
        Product.update(
            product_id,
            product_name=sanitized_name,
            description=sanitized_desc,
            price=price_value,
            stock_quantity=stock_value,
            image_url=sanitized_url,
            category_id=category_id_value
        )
        flash(f'Product "{sanitized_name}" updated successfully', 'success')
        return redirect(url_for('admin.manage_products'))
    except Exception as e:
        log_error(e, "update_product - update product")
        flash('Failed to update product. Please try again.', 'error')
        return redirect(url_for('admin.update_product', product_id=product_id))


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product(product_id):
    """
    Delete a product
    
    Removes the product from the database.
    
    Validates: Requirements 8.3, 11.5
    """
    try:
        product = Product.get_by_id(product_id)
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('admin.manage_products'))
        
        product_name = product.product_name
        Product.delete(product_id)
        flash(f'Product "{product_name}" deleted successfully', 'success')
    except Exception as e:
        log_error(e, "delete_product")
        flash('Failed to delete product. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_products'))


@admin_bp.route('/users')
@admin_required
def view_all_users():
    """
    Display all registered users
    
    Retrieves all users from the database excluding password field
    for security. Displays user details including name, email, role,
    and registration date.
    
    Validates: Requirements 9.1, 9.2, 11.5
    """
    try:
        # Query all users excluding password field
        query = """
            SELECT user_id, name, email, role, created_at
            FROM users
            ORDER BY created_at DESC
        """
        results = Database.execute_query(query, None, fetch=True)
        
        users = []
        for row in results:
            users.append({
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[3],
                'created_at': row[4]
            })
        
        return render_template('admin/users.html', users=users)
    except Exception as e:
        log_error(e, "view_all_users")
        flash('Failed to load users. Please try again.', 'error')
        return render_template('admin/users.html', users=[])



@admin_bp.route('/orders')
@admin_required
def view_all_orders():
    """
    Display all orders from all customers
    
    Retrieves all orders with user information and displays them
    in the order management template.
    
    Validates: Requirements 10.1, 11.5
    """
    try:
        orders = Order.get_all_orders()
        return render_template('admin/orders.html', orders=orders)
    except Exception as e:
        log_error(e, "view_all_orders")
        flash('Failed to load orders. Please try again.', 'error')
        return render_template('admin/orders.html', orders=[])


@admin_bp.route('/orders/<int:order_id>')
@admin_required
def view_order_detail(order_id):
    """
    Display detailed order information (admin version)
    
    Retrieves complete order information including customer details
    and all order items with product information.
    
    Validates: Requirements 10.3, 11.5
    """
    try:
        # Get order details
        order = Order.get_by_id(order_id)
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin.view_all_orders'))
        
        # Get customer information
        customer_query = """
            SELECT user_id, name, email
            FROM users
            WHERE user_id = %s
        """
        customer_result = Database.execute_query(customer_query, (order.user_id,), fetch=True)
        
        if not customer_result:
            flash('Customer information not found', 'error')
            return redirect(url_for('admin.view_all_orders'))
        
        customer = {
            'user_id': customer_result[0][0],
            'name': customer_result[0][1],
            'email': customer_result[0][2]
        }
        
        # Get order items
        order_items = OrderItem.get_order_items(order_id)
        
        return render_template(
            'admin/order_detail.html',
            order=order,
            customer=customer,
            order_items=order_items
        )
    except Exception as e:
        log_error(e, "view_order_detail (admin)")
        flash('Failed to load order details. Please try again.', 'error')
        return redirect(url_for('admin.view_all_orders'))


@admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """
    Update order status
    
    Validates the new status and updates the order record.
    Status updates are immediately visible to customers.
    
    Validates: Requirements 10.2, 6.3, 11.1
    """
    new_status = request.form.get('order_status', '')
    
    # Validate order status
    status_valid, sanitized_status, status_error = validate_order_status(new_status)
    if not status_valid:
        flash(status_error, 'error')
        return redirect(url_for('admin.view_order_detail', order_id=order_id))
    
    try:
        # Verify order exists
        order = Order.get_by_id(order_id)
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin.view_all_orders'))
        
        # Update status
        Order.update_status(order_id, sanitized_status)
        flash(f'Order status updated to {sanitized_status}', 'success')
        return redirect(url_for('admin.view_order_detail', order_id=order_id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('admin.view_order_detail', order_id=order_id))
    except Exception as e:
        log_error(e, "update_order_status")
        flash('Failed to update order status. Please try again.', 'error')
        return redirect(url_for('admin.view_order_detail', order_id=order_id))
