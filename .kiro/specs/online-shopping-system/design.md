# Design Document: Online Shopping System

## Overview

The Online Shopping System is a full-stack web application built with Flask (Python), MySQL, and Bootstrap 5. It implements a three-tier architecture (Presentation, Application, Database) with role-based access control supporting two user roles: Customer and Administrator.

The system follows the MVC (Model-View-Controller) pattern and uses Flask Blueprints for modular organization. Security is paramount, with password hashing, SQL injection prevention, session management, and input validation throughout.

## Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│     Presentation Layer (Tier 1)         │
│  HTML5, CSS3, Bootstrap 5, JavaScript   │
│         Jinja2 Templates                │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│     Application Layer (Tier 2)          │
│    Flask Framework + Blueprints         │
│   Business Logic & Controllers          │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│      Database Layer (Tier 3)            │
│         MySQL Database                  │
│      Data Models & Access               │
└─────────────────────────────────────────┘
```

### Flask Blueprint Structure

The application is organized into modular blueprints:

- **auth**: Authentication (login, register, logout)
- **user**: Customer-facing features (browse, cart, orders)
- **admin**: Administrator features (dashboard, management)
- **api**: Internal API endpoints for AJAX operations

### Project Directory Structure

```
online-shopping-system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py            # Auth routes
│   │   └── forms.py             # Auth forms
│   ├── user/
│   │   ├── __init__.py
│   │   ├── routes.py            # Customer routes
│   │   └── forms.py             # Customer forms
│   ├── admin/
│   │   ├── __init__.py
│   │   ├── routes.py            # Admin routes
│   │   └── forms.py             # Admin forms
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── product.py           # Product model
│   │   ├── category.py          # Category model
│   │   ├── cart.py              # Cart model
│   │   └── order.py             # Order model
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                # Database connection
│   ├── templates/
│   │   ├── base.html
│   │   ├── auth/
│   │   ├── user/
│   │   └── admin/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── config.py                     # Configuration
├── run.py                        # Application entry point
└── requirements.txt              # Python dependencies
```

## Components and Interfaces

### 1. Authentication Module (auth blueprint)

**Responsibilities:**
- User registration
- User login/logout
- Password hashing and verification
- Session creation and management

**Key Functions:**

```python
def register():
    """
    Handle user registration
    Input: name, email, password (from form)
    Process:
      - Validate input
      - Check if email exists
      - Hash password using werkzeug.security
      - Insert user into database with 'customer' role
    Output: Redirect to login or show error
    """

def login():
    """
    Handle user login
    Input: email, password (from form)
    Process:
      - Validate credentials
      - Verify password hash
      - Create session with user_id and role
    Output: Redirect to appropriate dashboard
    """

def logout():
    """
    Handle user logout
    Process:
      - Clear session data
    Output: Redirect to login page
    """
```

**Security Measures:**
- Password hashing: `werkzeug.security.generate_password_hash(password, method='pbkdf2:sha256')`
- Password verification: `werkzeug.security.check_password_hash(stored_hash, password)`
- Session security: Flask's secure session with secret key

### 2. User Management Module (user blueprint)

**Responsibilities:**
- Product browsing and search
- Cart operations
- Order placement
- Order history viewing

**Key Functions:**

```python
def browse_products(category_id=None, search_term=None):
    """
    Display product catalog with optional filtering
    Input: category_id (optional), search_term (optional)
    Process:
      - Query products from database
      - Filter by category if provided
      - Filter by search term if provided
      - Join with categories table
    Output: Render product list template
    """

def product_detail(product_id):
    """
    Display detailed product information
    Input: product_id
    Process:
      - Query product by ID with category
      - Check stock availability
    Output: Render product detail template
    """

def add_to_cart(product_id, quantity):
    """
    Add product to user's cart
    Input: product_id, quantity
    Process:
      - Verify user is logged in
      - Check product stock availability
      - Check if product already in cart
        - If yes: update quantity
        - If no: insert new cart entry
    Output: Success/error message, redirect to cart
    """

def view_cart():
    """
    Display user's shopping cart
    Process:
      - Query cart items for current user
      - Join with products table
      - Calculate total amount
    Output: Render cart template with items and total
    """

def update_cart_item(cart_id, quantity):
    """
    Update quantity of cart item
    Input: cart_id, new quantity
    Process:
      - Verify cart item belongs to current user
      - Check stock availability
      - Update quantity or remove if quantity = 0
    Output: Success/error message
    """

def remove_from_cart(cart_id):
    """
    Remove item from cart
    Input: cart_id
    Process:
      - Verify cart item belongs to current user
      - Delete cart entry
    Output: Success message, redirect to cart
    """

def place_order():
    """
    Process order from cart
    Process:
      - Start database transaction
      - Verify cart is not empty
      - Calculate total amount
      - Check stock for all items
      - Create order record with 'Pending' status
      - Create order_items records
      - Reduce stock quantities
      - Clear cart
      - Commit transaction
    Output: Redirect to payment simulation
    """

def simulate_payment(order_id):
    """
    Simulate payment processing
    Input: order_id
    Process:
      - Verify order belongs to current user
      - Display payment form
      - On submission: mark order as confirmed
    Output: Redirect to order confirmation
    """

def view_order_history():
    """
    Display user's order history
    Process:
      - Query orders for current user
      - Order by date descending
    Output: Render order history template
    """

def view_order_detail(order_id):
    """
    Display detailed order information
    Input: order_id
    Process:
      - Verify order belongs to current user
      - Query order with order_items
      - Join with products table
    Output: Render order detail template
    """
```

### 3. Admin Management Module (admin blueprint)

**Responsibilities:**
- Dashboard overview
- Category management
- Product management
- User viewing
- Order management

**Key Functions:**

```python
def admin_dashboard():
    """
    Display admin dashboard with statistics
    Process:
      - Verify user has admin role
      - Query statistics (total users, products, orders)
      - Query recent orders
    Output: Render dashboard template
    """

def manage_categories():
    """
    Display and manage categories
    Process:
      - Verify admin role
      - Query all categories
    Output: Render categories management template
    """

def add_category(category_name):
    """
    Add new category
    Input: category_name
    Process:
      - Verify admin role
      - Check if category name exists
      - Insert category record
    Output: Success/error message
    """

def manage_products():
    """
    Display all products for management
    Process:
      - Verify admin role
      - Query all products with categories
    Output: Render products management template
    """

def add_product(name, description, price, stock, image_url, category_id):
    """
    Add new product
    Input: product details
    Process:
      - Verify admin role
      - Validate input
      - Insert product record
    Output: Success/error message
    """

def update_product(product_id, name, description, price, stock, image_url, category_id):
    """
    Update existing product
    Input: product_id, updated details
    Process:
      - Verify admin role
      - Validate input
      - Update product record
    Output: Success/error message
    """

def delete_product(product_id):
    """
    Delete product
    Input: product_id
    Process:
      - Verify admin role
      - Delete product record
    Output: Success message
    """

def view_all_users():
    """
    Display all registered users
    Process:
      - Verify admin role
      - Query all users (exclude password)
    Output: Render users list template
    """

def view_all_orders():
    """
    Display all orders from all customers
    Process:
      - Verify admin role
      - Query all orders with user information
    Output: Render orders management template
    """

def update_order_status(order_id, new_status):
    """
    Update order status
    Input: order_id, new_status ('Pending', 'Shipped', 'Delivered')
    Process:
      - Verify admin role
      - Validate status value
      - Update order record
    Output: Success message
    """
```

### 4. Authorization Decorator

```python
def login_required(f):
    """
    Decorator to require authentication
    Process:
      - Check if user_id in session
      - If not: redirect to login
      - If yes: proceed to route
    """

def admin_required(f):
    """
    Decorator to require admin role
    Process:
      - Check if user_id in session
      - Check if role == 'admin'
      - If not: redirect to customer area
      - If yes: proceed to route
    """
```

## Data Models

### Database Schema

```sql
-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed
    role ENUM('customer', 'admin') DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- Products Table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

-- Cart Table
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- Orders Table
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status ENUM('Pending', 'Shipped', 'Delivered') DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Order_Items Table
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,  -- Price at time of order
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);
```

### Entity Relationships

```
users (1) ──────< (M) cart
users (1) ──────< (M) orders
categories (1) ──< (M) products
products (1) ────< (M) cart
products (1) ────< (M) order_items
orders (1) ──────< (M) order_items
```

### Python Model Classes

```python
class User:
    def __init__(self, user_id, name, email, password, role, created_at):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password  # Hashed
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def create(name, email, password, role='customer'):
        """Insert new user into database"""
    
    @staticmethod
    def find_by_email(email):
        """Query user by email"""
    
    @staticmethod
    def find_by_id(user_id):
        """Query user by ID"""

class Category:
    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name
    
    @staticmethod
    def create(category_name):
        """Insert new category"""
    
    @staticmethod
    def get_all():
        """Query all categories"""
    
    @staticmethod
    def exists(category_name):
        """Check if category name exists"""

class Product:
    def __init__(self, product_id, product_name, description, price, 
                 stock_quantity, image_url, category_id):
        self.product_id = product_id
        self.product_name = product_name
        self.description = description
        self.price = price
        self.stock_quantity = stock_quantity
        self.image_url = image_url
        self.category_id = category_id
    
    @staticmethod
    def create(product_name, description, price, stock_quantity, image_url, category_id):
        """Insert new product"""
    
    @staticmethod
    def get_all(category_id=None, search_term=None):
        """Query products with optional filters"""
    
    @staticmethod
    def get_by_id(product_id):
        """Query product by ID"""
    
    @staticmethod
    def update(product_id, **kwargs):
        """Update product fields"""
    
    @staticmethod
    def delete(product_id):
        """Delete product"""
    
    @staticmethod
    def reduce_stock(product_id, quantity):
        """Reduce stock quantity"""

class Cart:
    def __init__(self, cart_id, user_id, product_id, quantity):
        self.cart_id = cart_id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
    
    @staticmethod
    def add_item(user_id, product_id, quantity):
        """Add or update cart item"""
    
    @staticmethod
    def get_user_cart(user_id):
        """Query all cart items for user with product details"""
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Update cart item quantity"""
    
    @staticmethod
    def remove_item(cart_id):
        """Delete cart item"""
    
    @staticmethod
    def clear_cart(user_id):
        """Delete all cart items for user"""
    
    @staticmethod
    def calculate_total(user_id):
        """Calculate total amount for user's cart"""

class Order:
    def __init__(self, order_id, user_id, total_amount, order_date, order_status):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.order_status = order_status
    
    @staticmethod
    def create(user_id, total_amount):
        """Insert new order"""
    
    @staticmethod
    def get_user_orders(user_id):
        """Query all orders for user"""
    
    @staticmethod
    def get_all_orders():
        """Query all orders (admin)"""
    
    @staticmethod
    def get_by_id(order_id):
        """Query order by ID"""
    
    @staticmethod
    def update_status(order_id, status):
        """Update order status"""

class OrderItem:
    def __init__(self, order_item_id, order_id, product_id, quantity, price):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def create(order_id, product_id, quantity, price):
        """Insert new order item"""
    
    @staticmethod
    def get_order_items(order_id):
        """Query all items for an order with product details"""
```

## Database Connection Management

```python
import mysql.connector
from mysql.connector import pooling

class Database:
    def __init__(self, config):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="shopping_pool",
            pool_size=5,
            host=config['host'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
    
    def get_connection(self):
        """Get connection from pool"""
        return self.pool.get_connection()
    
    def execute_query(self, query, params=None, fetch=True):
        """
        Execute parameterized query
        Input: query string, parameters tuple
        Process:
          - Get connection from pool
          - Create cursor
          - Execute with parameters
          - Fetch results if SELECT
          - Commit if INSERT/UPDATE/DELETE
        Output: Query results or affected rows
        """
```



## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Authentication and Security Properties

**Property 1: User registration creates customer accounts**
*For any* valid registration data (name, email, password), creating a new user account should result in a user record with role='customer' and a hashed password that does not match the plaintext password.
**Validates: Requirements 1.1, 1.5**

**Property 2: Password hashing is irreversible**
*For any* user in the database, the stored password hash should never equal the plaintext password.
**Validates: Requirements 1.5**

**Property 3: Valid login creates authenticated session**
*For any* registered user with correct credentials, logging in should create a session containing user_id and role.
**Validates: Requirements 1.3, 12.1**

**Property 4: Invalid credentials reject authentication**
*For any* login attempt with incorrect password or non-existent email, the authentication should fail and no session should be created.
**Validates: Requirements 1.4**

**Property 5: Logout clears session data**
*For any* authenticated user, logging out should clear all session data including user_id and role.
**Validates: Requirements 1.6, 12.3**

**Property 6: Session validation protects resources**
*For any* protected route, requests without valid session data should be rejected and redirected to login.
**Validates: Requirements 12.2, 12.4**

### Authorization Properties

**Property 7: Role-based access control**
*For any* user, the assigned role should be either 'customer' or 'admin', and access to routes should be restricted based on this role.
**Validates: Requirements 2.1, 2.4**

**Property 8: Customer role restrictions**
*For any* user with role='customer', attempts to access admin routes should be denied and redirected.
**Validates: Requirements 2.2**

**Property 9: Admin role permissions**
*For any* user with role='admin', access to admin dashboard and management functions should be granted.
**Validates: Requirements 2.3**

### Product Browsing Properties

**Property 10: Product catalog completeness**
*For any* product catalog query, all products in the database should be returned with name, price, image_url, and stock_quantity fields.
**Validates: Requirements 3.1**

**Property 11: Category filtering correctness**
*For any* category filter, all returned products should have category_id matching the filter, and no products from that category should be excluded.
**Validates: Requirements 3.2**

**Property 12: Search term matching**
*For any* search query, all returned products should have product_name containing the search term (case-insensitive).
**Validates: Requirements 3.3**

**Property 13: Product detail completeness**
*For any* product detail view, the response should include product_name, description, price, stock_quantity, category information, and image_url.
**Validates: Requirements 3.4**

### Cart Management Properties

**Property 14: Cart addition idempotence**
*For any* product, adding it to cart multiple times should result in a single cart entry with accumulated quantity.
**Validates: Requirements 4.1**

**Property 15: Stock validation on cart operations**
*For any* cart operation (add or update), if the requested quantity exceeds available stock_quantity, the operation should be rejected.
**Validates: Requirements 4.2, 4.3**

**Property 16: Cart removal completeness**
*For any* cart item, removing it should result in that cart entry no longer existing in the database.
**Validates: Requirements 4.4**

**Property 17: Cart total calculation correctness**
*For any* user's cart, the calculated total should equal the sum of (product.price × cart_item.quantity) for all items.
**Validates: Requirements 4.5**

### Order Processing Properties

**Property 18: Order creation atomicity**
*For any* cart with items, placing an order should atomically: create an order record with status='Pending', create order_items for each cart item, reduce stock quantities, and clear the cart.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

**Property 19: Stock reduction correctness**
*For any* order, the stock_quantity for each product should decrease by exactly the ordered quantity.
**Validates: Requirements 5.3**

**Property 20: Order rejection on insufficient stock**
*For any* order attempt where any product has insufficient stock, the entire order should be rejected and no changes should be made to stock or cart.
**Validates: Requirements 5.6**

**Property 21: Payment confirmation updates order**
*For any* order in 'Pending' status, completing payment simulation should update the order state to confirmed.
**Validates: Requirements 5.5**

### Order History Properties

**Property 22: Order history completeness**
*For any* user, viewing order history should return all orders where order.user_id matches the user's ID.
**Validates: Requirements 6.1**

**Property 23: Order detail completeness**
*For any* order detail view, the response should include order_date, total_amount, order_status, and all order_items with product details, quantities, and prices.
**Validates: Requirements 6.2**

**Property 24: Status update propagation**
*For any* order, when an admin updates the order_status, the new status should be immediately visible in the customer's order history.
**Validates: Requirements 6.3, 10.2**

### Admin Category Management Properties

**Property 25: Category creation persistence**
*For any* valid category name, creating a category should result in a category record that appears in subsequent category listings.
**Validates: Requirements 7.1, 7.2**

### Admin Product Management Properties

**Property 26: Product CRUD completeness**
*For any* product, the system should support creating with all fields, updating any field, and deleting the record entirely.
**Validates: Requirements 8.1, 8.2, 8.3**

**Property 27: Stock update persistence**
*For any* product, updating the stock_quantity should persist the new value and be reflected in subsequent queries.
**Validates: Requirements 8.4**

**Property 28: Product listing with category join**
*For any* product listing query, all products should be returned with their associated category information.
**Validates: Requirements 8.5**

### Admin User Management Properties

**Property 29: User listing excludes passwords**
*For any* user listing query, the response should include name, email, role, and created_at, but should never include the password field.
**Validates: Requirements 9.1, 9.2**

### Admin Order Management Properties

**Property 30: Admin order visibility**
*For any* admin order listing, all orders from all users should be returned with order details.
**Validates: Requirements 10.1**

**Property 31: Order detail with customer information**
*For any* order detail view (admin), the response should include complete order information plus customer details and all order_items.
**Validates: Requirements 10.3**

### Input Validation Properties

**Property 32: Input sanitization**
*For any* user input, the system should validate and sanitize the data before processing, rejecting invalid formats.
**Validates: Requirements 11.1**

**Property 33: Unauthenticated request rejection**
*For any* protected operation, requests without valid authentication should be rejected before processing.
**Validates: Requirements 11.4**

**Property 34: Error message safety**
*For any* error condition, the error message displayed to users should not contain sensitive information like database details, stack traces, or password hashes.
**Validates: Requirements 11.5**

### User Interface Properties

**Property 35: Form validation feedback**
*For any* form submission with validation errors, the system should display specific error messages for each invalid field.
**Validates: Requirements 13.2**

**Property 36: Operation feedback consistency**
*For any* successful operation, the system should display a confirmation message; for any failed operation, the system should display an error message.
**Validates: Requirements 13.3, 13.4**

## Error Handling

### Error Categories

1. **Authentication Errors**
   - Invalid credentials
   - Duplicate email registration
   - Session expiration
   - Unauthorized access attempts

2. **Validation Errors**
   - Invalid input formats
   - Missing required fields
   - Constraint violations (e.g., negative prices)

3. **Business Logic Errors**
   - Insufficient stock
   - Empty cart checkout
   - Invalid order status transitions

4. **Database Errors**
   - Connection failures
   - Query execution errors
   - Constraint violations
   - Transaction rollback scenarios

### Error Handling Strategy

```python
def handle_error(error_type, error_details):
    """
    Centralized error handling
    Process:
      - Log error with full details (for debugging)
      - Determine user-friendly message
      - Return appropriate HTTP status code
      - For database errors: rollback transaction
      - For validation errors: return field-specific messages
    """
```

### Transaction Management

All order placement operations must be wrapped in database transactions:

```python
def place_order_with_transaction(user_id):
    connection = db.get_connection()
    try:
        connection.start_transaction()
        
        # 1. Validate cart not empty
        # 2. Calculate total
        # 3. Check stock for all items
        # 4. Create order
        # 5. Create order_items
        # 6. Reduce stock
        # 7. Clear cart
        
        connection.commit()
        return success_response
    except Exception as e:
        connection.rollback()
        log_error(e)
        return error_response
    finally:
        connection.close()
```

### Input Validation

All user inputs must be validated before processing:

```python
def validate_registration(name, email, password):
    """
    Validate registration inputs
    Rules:
      - name: 1-100 characters, not empty
      - email: valid email format, unique in database
      - password: minimum 8 characters
    """

def validate_product(name, price, stock):
    """
    Validate product inputs
    Rules:
      - name: 1-200 characters, not empty
      - price: positive decimal, max 2 decimal places
      - stock: non-negative integer
    """

def validate_quantity(quantity, available_stock):
    """
    Validate quantity inputs
    Rules:
      - quantity: positive integer
      - quantity <= available_stock
    """
```

## Testing Strategy

### Dual Testing Approach

The system requires both unit testing and property-based testing for comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

Both testing approaches are complementary and necessary. Unit tests catch concrete bugs in specific scenarios, while property tests verify general correctness across many generated inputs.

### Property-Based Testing Configuration

**Library**: Use `hypothesis` for Python property-based testing

**Configuration**:
- Minimum 100 iterations per property test
- Each test must reference its design document property
- Tag format: `# Feature: online-shopping-system, Property {number}: {property_text}`

**Example Property Test Structure**:

```python
from hypothesis import given, strategies as st
import pytest

# Feature: online-shopping-system, Property 1: User registration creates customer accounts
@given(
    name=st.text(min_size=1, max_size=100),
    email=st.emails(),
    password=st.text(min_size=8, max_size=100)
)
@pytest.mark.property_test
def test_registration_creates_customer_account(name, email, password):
    """
    Property: For any valid registration data, creating a new user 
    should result in a user record with role='customer' and hashed password
    """
    # Setup: Clear test database
    # Action: Register user
    # Assert: User exists with role='customer'
    # Assert: Password is hashed (not equal to plaintext)
```

### Unit Testing Focus Areas

Unit tests should focus on:

1. **Specific Examples**
   - Successful registration with valid data
   - Successful login with correct credentials
   - Adding specific products to cart
   - Placing order with known cart contents

2. **Edge Cases**
   - Empty cart display
   - Zero stock products
   - Duplicate email registration
   - Duplicate category names

3. **Error Conditions**
   - Invalid login credentials
   - Insufficient stock scenarios
   - Invalid input formats
   - Unauthorized access attempts

4. **Integration Points**
   - Database connection handling
   - Session management
   - Transaction rollback scenarios
   - Blueprint routing

### Test Organization

```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_user.py
│   ├── test_admin.py
│   ├── test_models.py
│   └── test_database.py
├── property/
│   ├── test_auth_properties.py
│   ├── test_cart_properties.py
│   ├── test_order_properties.py
│   └── test_admin_properties.py
├── integration/
│   ├── test_order_flow.py
│   ├── test_cart_to_order.py
│   └── test_admin_workflows.py
└── conftest.py  # Pytest fixtures
```

### Test Database Setup

Use a separate test database with fixtures for setup/teardown:

```python
@pytest.fixture
def test_db():
    """Setup test database with schema"""
    db = create_test_database()
    initialize_schema(db)
    yield db
    drop_test_database(db)

@pytest.fixture
def sample_user(test_db):
    """Create sample user for testing"""
    return User.create("Test User", "test@example.com", "password123")

@pytest.fixture
def sample_products(test_db):
    """Create sample products for testing"""
    category = Category.create("Electronics")
    products = [
        Product.create("Laptop", "Gaming laptop", 999.99, 10, "laptop.jpg", category.id),
        Product.create("Mouse", "Wireless mouse", 29.99, 50, "mouse.jpg", category.id)
    ]
    return products
```

### Coverage Goals

- **Unit test coverage**: Minimum 80% code coverage
- **Property test coverage**: All 36 correctness properties implemented
- **Integration test coverage**: All major user workflows (registration → browse → cart → order)
- **Edge case coverage**: All identified edge cases tested

### Continuous Testing

- Run unit tests on every commit
- Run property tests (with reduced iterations) on every commit
- Run full property test suite (100+ iterations) before releases
- Monitor test execution time and optimize slow tests

## Configuration Management

### Configuration Structure

```python
# config.py
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'dev_user'
    MYSQL_PASSWORD = 'dev_password'
    MYSQL_DATABASE = 'shopping_dev'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'test_user'
    MYSQL_PASSWORD = 'test_password'
    MYSQL_DATABASE = 'shopping_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
```

## Deployment Considerations

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip package manager

### Installation Steps

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Configure database connection in config.py
6. Initialize database schema
7. Create admin user (manual SQL or seed script)
8. Run application: `python run.py`

### Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS in production
- [ ] Configure secure session cookies
- [ ] Set up database user with minimal privileges
- [ ] Enable MySQL SSL connections
- [ ] Implement rate limiting for authentication endpoints
- [ ] Set up logging and monitoring
- [ ] Regular security updates for dependencies
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention via parameterized queries
- [ ] XSS prevention via template escaping

### Performance Optimization

- Use database connection pooling
- Add indexes on frequently queried columns (email, category_id, user_id)
- Implement caching for product catalog
- Optimize image loading (lazy loading, CDN)
- Minimize database queries (use joins instead of multiple queries)
- Enable gzip compression for responses

## Documentation Requirements

### UML Diagrams

1. **Use Case Diagram**: Show actors (Customer, Admin) and their use cases
2. **Class Diagram**: Show all model classes and relationships
3. **Sequence Diagrams**: 
   - User registration and login
   - Product browsing and cart management
   - Order placement flow
   - Admin product management
4. **Activity Diagrams**:
   - Order processing workflow
   - Cart to order conversion
5. **ER Diagram**: Database schema with relationships
6. **Data Flow Diagram**: System data flow across tiers

### Code Documentation

- Docstrings for all functions and classes
- Inline comments for complex logic
- README with setup instructions
- API documentation for all routes
- Database schema documentation

### Academic Documentation

- System architecture overview
- Technology stack justification
- Design decisions and rationale
- Testing methodology and results
- Security measures implemented
- Future enhancement possibilities
- References and citations
