# Online Shopping System

A full-stack web-based e-commerce platform built with Flask, MySQL, and Bootstrap 5. This system implements a three-tier architecture with role-based access control, supporting both customer and administrator roles.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Database Schema](#database-schema)
- [Security](#security)
- [API Routes](#api-routes)
- [License](#license)

## Overview

The Online Shopping System is a comprehensive e-commerce platform that enables customers to browse products, manage shopping carts, place orders, and track their purchases. Administrators can manage the product catalog, categories, users, and orders through a dedicated admin dashboard.

The system follows the MVC (Model-View-Controller) pattern and uses Flask Blueprints for modular organization. Security is paramount, with password hashing, SQL injection prevention, session management, and input validation throughout.

## Features

### Customer Features
- **User Registration & Authentication**: Secure account creation and login with password hashing
- **Product Browsing**: View all products with filtering by category and search functionality
- **Product Details**: View detailed product information including price, description, and stock availability
- **Shopping Cart**: Add, update, and remove items from cart with real-time stock validation
- **Order Processing**: Place orders with automatic stock reduction and cart clearing
- **Payment Simulation**: Simulate payment processing for orders
- **Order History**: View past orders with detailed order information and status tracking

### Administrator Features
- **Admin Dashboard**: View system statistics (total users, products, orders) and recent orders
- **Category Management**: Create and manage product categories
- **Product Management**: Full CRUD operations for products (Create, Read, Update, Delete)
- **User Management**: View all registered users and their details
- **Order Management**: View all orders and update order status (Pending, Shipped, Delivered)

### Security Features
- Password hashing using PBKDF2-SHA256
- SQL injection prevention via parameterized queries
- Session-based authentication with secure session management
- Role-based access control (Customer and Admin roles)
- Input validation and sanitization on all user inputs
- Error handling without exposing sensitive information

## Architecture

The system follows a **three-tier architecture**:

1. **Presentation Layer**: HTML5, CSS3, Bootstrap 5, JavaScript, Jinja2 Templates
2. **Application Layer**: Flask Framework with Blueprints, Business Logic & Controllers
3. **Database Layer**: MySQL Database with Data Models & Access

### Flask Blueprint Structure

- **auth**: Authentication (login, register, logout)
- **user**: Customer-facing features (browse, cart, orders)
- **admin**: Administrator features (dashboard, management)

## Project Structure

```
online-shopping-system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth/
│   │   ├── __init__.py          # Authentication routes
│   │   └── decorators.py        # Auth decorators (login_required, admin_required)
│   ├── user/
│   │   └── __init__.py          # Customer routes
│   ├── admin/
│   │   └── __init__.py          # Admin routes
│   ├── models/
│   │   ├── user.py              # User model
│   │   ├── product.py           # Product model
│   │   ├── category.py          # Category model
│   │   ├── cart.py              # Cart model
│   │   └── order.py             # Order and OrderItem models
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py                # Database connection and query execution
│   ├── utils/
│   │   ├── validation.py        # Input validation functions
│   │   └── error_handler.py     # Error handling and logging
│   ├── templates/
│   │   ├── base.html            # Base template
│   │   ├── auth/                # Authentication templates
│   │   ├── user/                # Customer templates
│   │   └── admin/               # Admin templates
│   └── static/
│       ├── css/                 # Custom CSS
│       ├── js/                  # JavaScript files
│       └── images/              # Image assets
├── tests/                       # Test suite (unit and property tests)
├── config.py                    # Configuration classes
├── run.py                       # Application entry point
├── schema.sql                   # Database schema
├── init_db.py                   # Database initialization script
├── seed_data.py                 # Sample data seeding script
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Installation

### Prerequisites

- **Python 3.8+**: Required for running the Flask application
- **MySQL 5.7+** or **MariaDB 10.3+**: Required for the database
- **pip**: Python package manager

### Setup Instructions

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd online-shopping-system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure MySQL database**:
   - Create a MySQL database named `shopping_system`
   - Update database credentials in `config.py` or set environment variables:
     ```bash
     export DB_HOST=localhost
     export DB_USER=root
     export DB_PASSWORD=your_password
     export DB_NAME=shopping_system
     ```

6. **Initialize the database**:
   ```bash
   python init_db.py
   ```
   This will create all necessary tables (users, categories, products, cart, orders, order_items).

7. **(Optional) Load sample data**:
   ```bash
   python seed_data.py
   ```
   This creates:
   - Admin user: `admin@shop.com` / `admin123`
   - Sample categories: Electronics, Clothing, Books
   - Sample products in each category

## Configuration

The application supports three configuration environments defined in `config.py`:

### Development Configuration (Default)
- Debug mode: **Enabled**
- Database: `shopping_dev`
- Session type: Filesystem
- Secret key: Development key (change in production)

### Production Configuration
- Debug mode: **Disabled**
- Database: From environment variables
- Secret key: **Must be set via environment variable**
- Recommended for deployment

### Test Configuration
- Testing mode: **Enabled**
- Database: `shopping_test`
- Used for running automated tests

### Setting Configuration

Set the `FLASK_CONFIG` environment variable:

```bash
# Development (default)
export FLASK_CONFIG=development

# Production
export FLASK_CONFIG=production
export SECRET_KEY=your-secret-key-here
export MYSQL_HOST=your-db-host
export MYSQL_USER=your-db-user
export MYSQL_PASSWORD=your-db-password
export MYSQL_DATABASE=your-db-name

# Test
export FLASK_CONFIG=test
```

## Usage

### Running the Application

1. **Activate the virtual environment** (if not already activated):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Run the Flask application**:
   ```bash
   python run.py
   ```

3. **Access the application**:
   - Open your browser and navigate to: `http://localhost:5000`
   - You will be redirected to the login page

### Default Credentials

If you ran the seed data script, you can use these credentials:

**Admin Account**:
- Email: `admin@shop.com`
- Password: `admin123`

**Customer Account**:
- Register a new account via the registration page

### Customer Workflow

1. **Register**: Create a new customer account at `/auth/register`
2. **Login**: Login with your credentials at `/auth/login`
3. **Browse Products**: View all products at `/user/products`
   - Filter by category using the dropdown
   - Search by product name using the search box
4. **View Product Details**: Click on a product to see full details
5. **Add to Cart**: Add products to your shopping cart
6. **View Cart**: Review your cart at `/user/cart`
   - Update quantities
   - Remove items
7. **Checkout**: Proceed to checkout and place your order
8. **Payment**: Simulate payment processing
9. **Order History**: View your orders at `/user/orders`

### Administrator Workflow

1. **Login**: Login with admin credentials at `/auth/login`
2. **Dashboard**: View system statistics at `/admin/dashboard`
3. **Manage Categories**: Add categories at `/admin/categories`
4. **Manage Products**: 
   - View all products at `/admin/products`
   - Add new products at `/admin/products/add`
   - Edit products at `/admin/products/edit/<product_id>`
   - Delete products
5. **View Users**: See all registered users at `/admin/users`
6. **Manage Orders**:
   - View all orders at `/admin/orders`
   - Update order status (Pending → Shipped → Delivered)

## Testing

The project includes comprehensive test coverage with both unit tests and property-based tests.

### Running Tests

**Run all tests**:
```bash
pytest
```

**Run tests with coverage report**:
```bash
pytest --cov=app
```

**Run tests with detailed output**:
```bash
pytest -v
```

**Run specific test file**:
```bash
pytest tests/test_auth_unit.py
```

**Run property-based tests only**:
```bash
pytest -m property_test
```

### Test Structure

- **Unit Tests**: Test specific examples, edge cases, and error conditions
- **Property Tests**: Test universal properties across many generated inputs using Hypothesis
- **Integration Tests**: Test complete workflows (registration → browse → cart → order)

### Test Coverage

The test suite includes:
- 36 correctness properties validated via property-based testing
- Unit tests for all models, routes, and utilities
- Integration tests for customer and admin workflows
- Minimum 80% code coverage

## Database Schema

The system uses the following MySQL tables:

### users
- `user_id` (INT, PK, AUTO_INCREMENT)
- `name` (VARCHAR(100))
- `email` (VARCHAR(100), UNIQUE)
- `password` (VARCHAR(255)) - Hashed
- `role` (ENUM: 'customer', 'admin')
- `created_at` (TIMESTAMP)

### categories
- `category_id` (INT, PK, AUTO_INCREMENT)
- `category_name` (VARCHAR(100), UNIQUE)

### products
- `product_id` (INT, PK, AUTO_INCREMENT)
- `product_name` (VARCHAR(200))
- `description` (TEXT)
- `price` (DECIMAL(10, 2))
- `stock_quantity` (INT)
- `image_url` (VARCHAR(255))
- `category_id` (INT, FK → categories)

### cart
- `cart_id` (INT, PK, AUTO_INCREMENT)
- `user_id` (INT, FK → users)
- `product_id` (INT, FK → products)
- `quantity` (INT)
- UNIQUE constraint on (user_id, product_id)

### orders
- `order_id` (INT, PK, AUTO_INCREMENT)
- `user_id` (INT, FK → users)
- `total_amount` (DECIMAL(10, 2))
- `order_date` (TIMESTAMP)
- `order_status` (ENUM: 'Pending', 'Shipped', 'Delivered')

### order_items
- `order_item_id` (INT, PK, AUTO_INCREMENT)
- `order_id` (INT, FK → orders)
- `product_id` (INT, FK → products)
- `quantity` (INT)
- `price` (DECIMAL(10, 2)) - Price at time of order

See `schema.sql` for the complete schema definition with foreign key constraints.

## Security

The application implements multiple security measures:

### Authentication & Authorization
- **Password Hashing**: All passwords are hashed using PBKDF2-SHA256 via werkzeug.security
- **Session Management**: Secure session-based authentication with Flask sessions
- **Role-Based Access Control**: Separate customer and admin roles with route protection
- **Login Required Decorator**: Protects all authenticated routes
- **Admin Required Decorator**: Restricts admin routes to admin users only

### Input Validation
- All user inputs are validated and sanitized before processing
- Email format validation
- Password strength requirements (minimum 8 characters)
- Numeric field validation (prices, quantities, IDs)
- String length validation

### SQL Injection Prevention
- All database queries use parameterized queries
- No string concatenation in SQL statements
- mysql-connector-python handles parameter escaping

### Error Handling
- Centralized error handling with logging
- User-friendly error messages without sensitive information
- No exposure of database details, stack traces, or internal errors
- Transaction rollback on database errors

### Production Security Checklist
- [ ] Change SECRET_KEY in production (use environment variable)
- [ ] Enable HTTPS for all connections
- [ ] Configure secure session cookies (httponly, secure flags)
- [ ] Set up database user with minimal privileges
- [ ] Enable MySQL SSL connections
- [ ] Implement rate limiting for authentication endpoints
- [ ] Set up logging and monitoring
- [ ] Regular security updates for dependencies
- [ ] Configure CORS policies appropriately

## API Routes

### Authentication Routes (`/auth`)
- `GET /auth/register` - Display registration form
- `POST /auth/register` - Process registration
- `GET /auth/login` - Display login form
- `POST /auth/login` - Process login
- `GET /auth/logout` - Logout user

### Customer Routes (`/user`) - Requires Login
- `GET /user/products` - Browse products (with optional category and search filters)
- `GET /user/products/<product_id>` - View product details
- `GET /user/cart` - View shopping cart
- `POST /user/cart/add/<product_id>` - Add product to cart
- `POST /user/cart/update/<cart_id>` - Update cart item quantity
- `POST /user/cart/remove/<cart_id>` - Remove item from cart
- `GET /user/checkout` - Display checkout page
- `POST /user/checkout` - Place order
- `GET /user/payment/<order_id>` - Display payment simulation
- `POST /user/payment/<order_id>` - Process payment
- `GET /user/order-confirmation/<order_id>` - Order confirmation page
- `GET /user/orders` - View order history
- `GET /user/orders/<order_id>` - View order details

### Admin Routes (`/admin`) - Requires Admin Role
- `GET /admin/dashboard` - Admin dashboard with statistics
- `GET /admin/categories` - Manage categories
- `POST /admin/categories/add` - Add new category
- `GET /admin/products` - Manage products
- `GET /admin/products/add` - Display add product form
- `POST /admin/products/add` - Create new product
- `GET /admin/products/edit/<product_id>` - Display edit product form
- `POST /admin/products/edit/<product_id>` - Update product
- `POST /admin/products/delete/<product_id>` - Delete product
- `GET /admin/users` - View all users
- `GET /admin/orders` - View all orders
- `GET /admin/orders/<order_id>` - View order details
- `POST /admin/orders/<order_id>/update-status` - Update order status

## License

This project is for educational purposes.
