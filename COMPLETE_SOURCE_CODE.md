# Online Shopping System - Complete Source Code

This document contains all the source code for the Flask-based Online Shopping System mini project.

## Table of Contents
1. [Project Structure](#project-structure)
2. [Configuration Files](#configuration-files)
3. [Database Files](#database-files)
4. [Application Core](#application-core)
5. [Models](#models)
6. [Blueprints](#blueprints)
7. [Utilities](#utilities)
8. [Templates](#templates)
9. [Static Files](#static-files)
10. [Setup Instructions](#setup-instructions)

---

## Project Structure

```
online-shopping-system/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth/
│   │   ├── __init__.py          # Authentication routes
│   │   └── decorators.py        # Auth decorators
│   ├── user/
│   │   └── __init__.py          # Customer routes
│   ├── admin/
│   │   └── __init__.py          # Admin routes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model
│   │   ├── product.py           # Product model
│   │   ├── category.py          # Category model
│   │   ├── cart.py              # Cart model
│   │   └── order.py             # Order models
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                # MySQL database
│   │   └── db_universal.py      # Universal DB adapter
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validation.py        # Input validation
│   │   └── error_handler.py     # Error handling
│   ├── templates/               # HTML templates
│   └── static/                  # CSS, JS, images
├── config.py                    # Configuration
├── run.py                       # Entry point
├── init_db.py                   # DB initialization
├── seed_data.py                 # Sample data
├── schema.sql                   # MySQL schema
├── schema_postgresql.sql        # PostgreSQL schema
└── requirements.txt             # Dependencies
```

---

## Configuration Files

### requirements.txt
```txt
# Flask Framework - Web application framework
Flask==3.0.0

# MySQL Database Connector - Database driver for MySQL
mysql-connector-python==8.2.0

# PostgreSQL Database Connector - For Render.com deployment
psycopg2-binary==2.9.10

# Werkzeug - WSGI utility library (includes password hashing)
werkzeug==3.0.1

# Gunicorn - Production WSGI server
gunicorn==21.2.0

# Python-dotenv - Environment variable management
python-dotenv==1.0.0

# Testing Framework - Unit testing
pytest==7.4.3

# Property-Based Testing - Hypothesis for property tests
hypothesis==6.92.1

# Test Coverage - Code coverage measurement
pytest-cov==4.1.0
```

### .env.example
```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=shopping_system

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_CONFIG=development

# Production Database URL (for Render.com)
# DATABASE_URL=postgresql://user:password@host:port/database
```

### config.py
```python
"""
Configuration module for the Online Shopping System
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SESSION_TYPE = 'filesystem'
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'shopping_system'
    DB_POOL_SIZE = 5


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')


class TestConfig(Config):
    """Test configuration"""
    DEBUG = True
    TESTING = True
    DB_NAME = 'shopping_system_test'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestConfig,
    'default': DevelopmentConfig
}
```

### run.py
```python
"""
Application entry point for the Online Shopping System
"""

import os
from app import create_app

config_name = os.environ.get('FLASK_CONFIG') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
```

---

## Database Files

### schema.sql (MySQL)
```sql
-- Online Shopping System Database Schema

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS cart;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Users Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer', 'admin') DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories Table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    INDEX idx_category_name (category_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Products Table
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    INDEX idx_product_name (product_name),
    INDEX idx_category_id (category_id),
    INDEX idx_stock (stock_quantity),
    CHECK (price >= 0),
    CHECK (stock_quantity >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Cart Table
CREATE TABLE cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id),
    INDEX idx_user_id (user_id),
    CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Orders Table
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_status ENUM('Pending', 'Shipped', 'Delivered') DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_order_date (order_date),
    INDEX idx_order_status (order_status),
    CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order_Items Table
CREATE TABLE order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id),
    CHECK (quantity > 0),
    CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### init_db.py
```python
#!/usr/bin/env python3
"""Database initialization script"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import sys

load_dotenv()


def create_database(host, user, password, db_name):
    """Create database if it doesn't exist"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"Database '{db_name}' created successfully or already exists.")
        cursor.close()
        
    except Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)
    finally:
        if connection and connection.is_connected():
            connection.close()


def execute_schema(host, user, password, db_name, schema_file='schema.sql'):
    """Execute SQL schema file"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        
        cursor = connection.cursor()
        
        if not os.path.exists(schema_file):
            print(f"Error: Schema file '{schema_file}' not found.")
            sys.exit(1)
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                print(f"Executed: {statement[:50]}...")
        
        connection.commit()
        print(f"\nSchema executed successfully on database '{db_name}'.")
        cursor.close()
        
    except Error as e:
        print(f"Error executing schema: {e}")
        if connection:
            connection.rollback()
        sys.exit(1)
    finally:
        if connection and connection.is_connected():
            connection.close()


def main():
    """Main function"""
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'shopping_system')
    
    print("=" * 60)
    print("Online Shopping System - Database Initialization")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"User: {user}")
    print(f"Database: {db_name}")
    print("=" * 60)
    
    print("\nStep 1: Creating database...")
    create_database(host, user, password, db_name)
    
    print("\nStep 2: Executing schema...")
    execute_schema(host, user, password, db_name)
    
    print("\n" + "=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
```

### seed_data.py
```python
#!/usr/bin/env python3
"""Seed data script - Creates admin user, categories, and sample products"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import sys

load_dotenv()


def get_db_connection(host, user, password, db_name):
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def check_admin_exists(cursor):
    """Check if admin user already exists"""
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ('admin@shop.com',))
    count = cursor.fetchone()[0]
    return count > 0


def create_admin_user(cursor):
    """Create admin user"""
    if check_admin_exists(cursor):
        print("  ✓ Admin user already exists (admin@shop.com)")
        return False
    
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    query = "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, ('Admin User', 'admin@shop.com', hashed_password, 'admin'))
    print("  ✓ Created admin user (email: admin@shop.com, password: admin123)")
    return True


def check_category_exists(cursor, category_name):
    """Check if category already exists"""
    cursor.execute("SELECT COUNT(*) FROM categories WHERE category_name = %s", (category_name,))
    count = cursor.fetchone()[0]
    return count > 0


def get_category_id(cursor, category_name):
    """Get category ID by name"""
    cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (category_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def create_categories(cursor):
    """Create sample categories"""
    categories = ['Electronics', 'Clothing', 'Books']
    created_count = 0
    
    for category_name in categories:
        if check_category_exists(cursor, category_name):
            print(f"  ✓ Category '{category_name}' already exists")
        else:
            cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
            print(f"  ✓ Created category '{category_name}'")
            created_count += 1
    
    return created_count


def check_product_exists(cursor, product_name):
    """Check if product already exists"""
    cursor.execute("SELECT COUNT(*) FROM products WHERE product_name = %s", (product_name,))
    count = cursor.fetchone()[0]
    return count > 0


def create_sample_products(cursor):
    """Create sample products"""
    electronics_id = get_category_id(cursor, 'Electronics')
    clothing_id = get_category_id(cursor, 'Clothing')
    books_id = get_category_id(cursor, 'Books')
    
    products = [
        # Electronics
        ('Laptop - Dell XPS 15', 'High-performance laptop with Intel Core i7, 16GB RAM, 512GB SSD', 
         1299.99, 15, 'https://via.placeholder.com/300x300?text=Dell+XPS+15', electronics_id),
        ('Wireless Mouse - Logitech MX Master 3', 'Ergonomic wireless mouse with precision scrolling', 
         99.99, 50, 'https://via.placeholder.com/300x300?text=Logitech+Mouse', electronics_id),
        ('Smartphone - Samsung Galaxy S23', '6.1-inch display, 128GB storage, 5G enabled', 
         799.99, 25, 'https://via.placeholder.com/300x300?text=Samsung+S23', electronics_id),
        ('Wireless Headphones - Sony WH-1000XM5', 'Industry-leading noise cancellation, 30-hour battery', 
         399.99, 30, 'https://via.placeholder.com/300x300?text=Sony+Headphones', electronics_id),
        ('4K Monitor - LG UltraFine 27"', '27-inch 4K UHD display with HDR support', 
         549.99, 20, 'https://via.placeholder.com/300x300?text=LG+Monitor', electronics_id),
        
        # Clothing
        ('Men\'s Cotton T-Shirt - Navy Blue', 'Comfortable 100% cotton t-shirt', 
         24.99, 100, 'https://via.placeholder.com/300x300?text=Navy+T-Shirt', clothing_id),
        ('Women\'s Denim Jeans - Slim Fit', 'Classic slim-fit jeans with stretch fabric', 
         59.99, 75, 'https://via.placeholder.com/300x300?text=Denim+Jeans', clothing_id),
        ('Unisex Hoodie - Gray', 'Warm and cozy hoodie with front pocket', 
         44.99, 60, 'https://via.placeholder.com/300x300?text=Gray+Hoodie', clothing_id),
        ('Running Shoes - Nike Air Zoom', 'Lightweight running shoes with responsive cushioning', 
         129.99, 40, 'https://via.placeholder.com/300x300?text=Nike+Shoes', clothing_id),
        ('Winter Jacket - Waterproof', 'Insulated winter jacket with waterproof exterior', 
         149.99, 35, 'https://via.placeholder.com/300x300?text=Winter+Jacket', clothing_id),
        
        # Books
        ('The Pragmatic Programmer', 'Your journey to mastery', 
         49.99, 45, 'https://via.placeholder.com/300x300?text=Pragmatic+Programmer', books_id),
        ('Clean Code by Robert Martin', 'A handbook of agile software craftsmanship', 
         44.99, 50, 'https://via.placeholder.com/300x300?text=Clean+Code', books_id),
        ('Design Patterns', 'Elements of Reusable Object-Oriented Software', 
         54.99, 30, 'https://via.placeholder.com/300x300?text=Design+Patterns', books_id),
        ('Introduction to Algorithms', 'Comprehensive introduction to algorithms', 
         89.99, 25, 'https://via.placeholder.com/300x300?text=Algorithms', books_id),
        ('Python Crash Course', 'A hands-on, project-based introduction to Python', 
         39.99, 55, 'https://via.placeholder.com/300x300?text=Python+Course', books_id)
    ]
    
    created_count = 0
    query = """
        INSERT INTO products (product_name, description, price, stock_quantity, image_url, category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for product in products:
        if check_product_exists(cursor, product[0]):
            print(f"  ✓ Product '{product[0]}' already exists")
        else:
            cursor.execute(query, product)
            print(f"  ✓ Created product '{product[0]}'")
            created_count += 1
    
    return created_count


def main():
    """Main function"""
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'shopping_system')
    
    print("=" * 70)
    print("Online Shopping System - Seed Data Script")
    print("=" * 70)
    
    connection = get_db_connection(host, user, password, db_name)
    cursor = connection.cursor()
    
    try:
        print("\n[1/3] Creating admin user...")
        create_admin_user(cursor)
        
        print("\n[2/3] Creating categories...")
        create_categories(cursor)
        
        print("\n[3/3] Creating sample products...")
        create_sample_products(cursor)
        
        connection.commit()
        
        print("\n" + "=" * 70)
        print("Seed data completed successfully!")
        print("Admin: admin@shop.com / admin123")
        print("=" * 70)
        
    except Error as e:
        connection.rollback()
        print(f"\n✗ Error seeding data: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        connection.close()


if __name__ == '__main__':
    main()
```

---

## Application Core

### app/__init__.py
```python
"""Flask application factory module"""

from flask import Flask, render_template, session, redirect, url_for
from config import config


def create_app(config_name='default'):
    """Flask application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure session security
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    if not app.config.get('TESTING'):
        app.config['SESSION_COOKIE_SECURE'] = False
    
    # Initialize database
    from app.database.db_universal import init_db
    init_db(app.config)
    
    # Register blueprints
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.user import user_bp
    app.register_blueprint(user_bp)
    
    from app.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from app.utils.error_handler import log_error
        log_error(error, "Internal Server Error")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html'), 400
    
    # Home route
    @app.route('/')
    def index():
        """Home route with role-based redirection"""
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.browse_products'))
        return redirect(url_for('auth.login'))
    
    return app
```

### app/database/__init__.py
```python
"""Database package"""
```

### app/database/db.py
```python
"""MySQL database connection manager"""

import mysql.connector
from mysql.connector import pooling, Error


class Database:
    """Database connection manager with connection pooling"""
    
    _pool = None
    
    @classmethod
    def init_db(cls, config):
        """Initialize database connection pool"""
        if cls._pool is not None:
            return
            
        try:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="shopping_pool",
                pool_size=config.get('DB_POOL_SIZE', 5),
                host=config.get('DB_HOST', 'localhost'),
                user=config.get('DB_USER', 'root'),
                password=config.get('DB_PASSWORD', ''),
                database=config.get('DB_NAME', 'shopping_system'),
                autocommit=False
            )
            print(f"Database connection pool initialized for {config.get('DB_NAME')}")
        except Error as e:
            print(f"Error initializing database pool: {e}")
            raise
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        if cls._pool is None:
            raise Exception("Database pool not initialized. Call init_db() first.")
        return cls._pool.get_connection()
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """Execute parameterized query"""
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                else:
                    return cursor.rowcount
        except Error as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


def init_db(config):
    """Initialize database connection pool"""
    Database.init_db(config)


def get_connection():
    """Get database connection from pool"""
    return Database.get_connection()


def execute_query(query, params=None, fetch=True):
    """Execute parameterized query"""
    return Database.execute_query(query, params, fetch)
```

### app/database/db_universal.py
```python
"""Universal database module supporting both MySQL and PostgreSQL"""

import os
from urllib.parse import urlparse


class UniversalDatabase:
    """Database connection manager supporting MySQL and PostgreSQL"""
    
    _pool = None
    _db_type = None
    
    @classmethod
    def init_db(cls, config=None):
        """Initialize database connection pool"""
        if cls._pool is not None:
            return
        
        database_url = os.environ.get('DATABASE_URL')
        
        try:
            if database_url:
                cls._db_type = 'postgresql'
                cls._init_postgresql(database_url)
            else:
                cls._db_type = 'mysql'
                cls._init_mysql(config or {})
                
            print(f"Database connection pool initialized ({cls._db_type})")
        except Exception as e:
            print(f"Error initializing database pool: {e}")
            raise
    
    @classmethod
    def _init_postgresql(cls, database_url):
        """Initialize PostgreSQL connection pool"""
        import psycopg2
        from psycopg2 import pool
        
        parsed = urlparse(database_url)
        
        cls._pool = pool.SimpleConnectionPool(
            1, 10,
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]
        )
    
    @classmethod
    def _init_mysql(cls, config):
        """Initialize MySQL connection pool"""
        from mysql.connector import pooling
        
        cls._pool = pooling.MySQLConnectionPool(
            pool_name="shopping_pool",
            pool_size=config.get('DB_POOL_SIZE', 5),
            host=config.get('DB_HOST', 'localhost'),
            user=config.get('DB_USER', 'root'),
            password=config.get('DB_PASSWORD', ''),
            database=config.get('DB_NAME', 'shopping_system'),
            autocommit=False
        )
    
    @classmethod
    def get_connection(cls):
        """Get connection from pool"""
        if cls._pool is None:
            raise Exception("Database pool not initialized")
        
        if cls._db_type == 'postgresql':
            return cls._pool.getconn()
        else:
            return cls._pool.get_connection()
    
    @classmethod
    def release_connection(cls, connection):
        """Release connection back to pool"""
        if cls._db_type == 'postgresql':
            cls._pool.putconn(connection)
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """Execute parameterized query"""
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                else:
                    return cursor.rowcount
        except Exception as e:
            if connection:
                connection.rollback()
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                if cls._db_type == 'postgresql':
                    cls.release_connection(connection)
                else:
                    connection.close()


class Database(UniversalDatabase):
    """Alias for backward compatibility"""
    pass


def init_db(config=None):
    """Initialize database"""
    UniversalDatabase.init_db(config)


def get_connection():
    """Get connection"""
    return UniversalDatabase.get_connection()


def execute_query(query, params=None, fetch=True):
    """Execute query"""
    return UniversalDatabase.execute_query(query, params, fetch)
```

---

## Models

### app/models/__init__.py
```python
"""Models package"""
```


### app/models/user.py
```python
"""User model for authentication and user management"""

from app.database.db_universal import execute_query
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    """User model representing a system user"""
    
    def __init__(self, user_id, name, email, password, role, created_at):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.created_at = created_at
    
    @staticmethod
    def create(name, email, password, role='customer'):
        """Create a new user"""
        from app.database.db_universal import Database
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        query = """
            INSERT INTO users (name, email, password, role)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
        """
        params = (name, email, hashed_password, role)
        
        connection = Database.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            user_id = cursor.fetchone()[0]
            connection.commit()
            cursor.close()
            Database.release_connection(connection)
            return user_id
        except Exception as e:
            connection.rollback()
            cursor.close()
            Database.release_connection(connection)
            raise
    
    @staticmethod
    def find_by_email(email):
        """Find a user by email"""
        query = """
            SELECT user_id, name, email, password, role, created_at
            FROM users WHERE email = %s
        """
        results = execute_query(query, (email,), fetch=True)
        
        if results:
            row = results[0]
            return User(row[0], row[1], row[2], row[3], row[4], row[5])
        return None
    
    @staticmethod
    def find_by_id(user_id):
        """Find a user by ID"""
        query = """
            SELECT user_id, name, email, password, role, created_at
            FROM users WHERE user_id = %s
        """
        results = execute_query(query, (user_id,), fetch=True)
        
        if results:
            row = results[0]
            return User(row[0], row[1], row[2], row[3], row[4], row[5])
        return None
    
    def verify_password(self, password):
        """Verify password"""
        return check_password_hash(self.password, password)
    
    def to_dict(self, include_password=False):
        """Convert to dictionary"""
        user_dict = {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }
        if include_password:
            user_dict['password'] = self.password
        return user_dict
```

### app/models/product.py
```python
"""Product model for managing products"""

from app.database.db_universal import Database


class Product:
    """Product model"""
    
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
        """Create a new product"""
        query = """
            INSERT INTO products 
            (product_name, description, price, stock_quantity, image_url, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            product_id = Database.execute_query(
                query, 
                (product_name, description, price, stock_quantity, image_url, category_id),
                fetch=False
            )
            return Product(product_id, product_name, description, price, 
                         stock_quantity, image_url, category_id)
        except Exception as e:
            print(f"Error creating product: {e}")
            raise
    
    @staticmethod
    def get_all(category_id=None, search_term=None):
        """Retrieve all products with optional filtering"""
        query = """
            SELECT product_id, product_name, description, price, 
                   stock_quantity, image_url, category_id
            FROM products WHERE 1=1
        """
        params = []
        
        if category_id is not None:
            query += " AND category_id = %s"
            params.append(category_id)
        
        if search_term:
            query += " AND product_name LIKE %s"
            params.append(f"%{search_term}%")
        
        query += " ORDER BY product_name"
        
        try:
            results = Database.execute_query(query, tuple(params) if params else None, fetch=True)
            return [Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) 
                   for row in results]
        except Exception as e:
            print(f"Error retrieving products: {e}")
            raise
    
    @staticmethod
    def get_by_id(product_id):
        """Retrieve a product by ID"""
        query = """
            SELECT product_id, product_name, description, price, 
                   stock_quantity, image_url, category_id
            FROM products WHERE product_id = %s
        """
        try:
            results = Database.execute_query(query, (product_id,), fetch=True)
            if results:
                row = results[0]
                return Product(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            return None
        except Exception as e:
            print(f"Error retrieving product: {e}")
            raise
    
    @staticmethod
    def update(product_id, product_name=None, description=None, price=None, 
               stock_quantity=None, image_url=None, category_id=None):
        """Update product fields"""
        update_fields = []
        params = []
        
        if product_name is not None:
            update_fields.append("product_name = %s")
            params.append(product_name)
        
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        
        if price is not None:
            update_fields.append("price = %s")
            params.append(price)
        
        if stock_quantity is not None:
            update_fields.append("stock_quantity = %s")
            params.append(stock_quantity)
        
        if image_url is not None:
            update_fields.append("image_url = %s")
            params.append(image_url)
        
        if category_id is not None:
            update_fields.append("category_id = %s")
            params.append(category_id)
        
        if not update_fields:
            return 0
        
        query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = %s"
        params.append(product_id)
        
        try:
            rows_affected = Database.execute_query(query, tuple(params), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating product: {e}")
            raise
    
    @staticmethod
    def delete(product_id):
        """Delete a product"""
        query = "DELETE FROM products WHERE product_id = %s"
        try:
            rows_affected = Database.execute_query(query, (product_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error deleting product: {e}")
            raise
    
    @staticmethod
    def reduce_stock(product_id, quantity):
        """Reduce stock quantity"""
        query = """
            UPDATE products 
            SET stock_quantity = stock_quantity - %s 
            WHERE product_id = %s AND stock_quantity >= %s
        """
        try:
            rows_affected = Database.execute_query(
                query, (quantity, product_id, quantity), fetch=False
            )
            if rows_affected == 0:
                raise ValueError(f"Insufficient stock for product {product_id}")
            return rows_affected
        except Exception as e:
            print(f"Error reducing stock: {e}")
            raise
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'description': self.description,
            'price': float(self.price),
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'category_id': self.category_id
        }
```

### app/models/category.py
```python
"""Category model for product categorization"""

from app.database.db_universal import Database


class Category:
    """Category model"""
    
    def __init__(self, category_id, category_name):
        self.category_id = category_id
        self.category_name = category_name
    
    @staticmethod
    def create(category_name):
        """Create a new category"""
        query = "INSERT INTO categories (category_name) VALUES (%s)"
        try:
            category_id = Database.execute_query(query, (category_name,), fetch=False)
            return Category(category_id, category_name)
        except Exception as e:
            print(f"Error creating category: {e}")
            raise
    
    @staticmethod
    def get_all():
        """Retrieve all categories"""
        query = "SELECT category_id, category_name FROM categories ORDER BY category_name"
        try:
            results = Database.execute_query(query, fetch=True)
            return [Category(row[0], row[1]) for row in results]
        except Exception as e:
            print(f"Error retrieving categories: {e}")
            raise
    
    @staticmethod
    def exists(category_name):
        """Check if category exists"""
        query = "SELECT COUNT(*) FROM categories WHERE category_name = %s"
        try:
            results = Database.execute_query(query, (category_name,), fetch=True)
            return results[0][0] > 0
        except Exception as e:
            print(f"Error checking category: {e}")
            raise
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'category_id': self.category_id,
            'category_name': self.category_name
        }
```

### app/models/cart.py
```python
"""Cart model for managing shopping cart"""

from app.database.db_universal import Database


class Cart:
    """Cart model"""
    
    def __init__(self, cart_id, user_id, product_id, quantity):
        self.cart_id = cart_id
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity
    
    @staticmethod
    def add_item(user_id, product_id, quantity):
        """Add or update cart item with stock validation"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        # Check stock
        stock_query = "SELECT stock_quantity FROM products WHERE product_id = %s"
        stock_result = Database.execute_query(stock_query, (product_id,), fetch=True)
        
        if not stock_result:
            raise ValueError(f"Product {product_id} not found")
        
        available_stock = stock_result[0][0]
        
        # Check if item already in cart
        check_query = "SELECT cart_id, quantity FROM cart WHERE user_id = %s AND product_id = %s"
        existing = Database.execute_query(check_query, (user_id, product_id), fetch=True)
        
        if existing:
            cart_id = existing[0][0]
            current_quantity = existing[0][1]
            new_quantity = current_quantity + quantity
            
            if new_quantity > available_stock:
                raise ValueError(f"Insufficient stock. Available: {available_stock}")
            
            update_query = "UPDATE cart SET quantity = %s WHERE cart_id = %s"
            Database.execute_query(update_query, (new_quantity, cart_id), fetch=False)
            return cart_id
        else:
            if quantity > available_stock:
                raise ValueError(f"Insufficient stock. Available: {available_stock}")
            
            insert_query = "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)"
            cart_id = Database.execute_query(insert_query, (user_id, product_id, quantity), fetch=False)
            return cart_id
    
    @staticmethod
    def get_user_cart(user_id):
        """Get all cart items for user"""
        query = """
            SELECT c.cart_id, c.user_id, c.product_id, c.quantity,
                   p.product_name, p.description, p.price, p.stock_quantity, p.image_url
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
            ORDER BY c.cart_id
        """
        try:
            results = Database.execute_query(query, (user_id,), fetch=True)
            cart_items = []
            for row in results:
                cart_items.append({
                    'cart_id': row[0],
                    'user_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'product_name': row[4],
                    'description': row[5],
                    'price': float(row[6]),
                    'stock_quantity': row[7],
                    'image_url': row[8],
                    'subtotal': float(row[6]) * row[3]
                })
            return cart_items
        except Exception as e:
            print(f"Error retrieving cart: {e}")
            raise
    
    @staticmethod
    def update_quantity(cart_id, quantity):
        """Update cart item quantity"""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if quantity == 0:
            return Cart.remove_item(cart_id)
        
        # Check stock
        check_query = """
            SELECT c.product_id, p.stock_quantity
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.cart_id = %s
        """
        result = Database.execute_query(check_query, (cart_id,), fetch=True)
        
        if not result:
            raise ValueError(f"Cart item {cart_id} not found")
        
        available_stock = result[0][1]
        
        if quantity > available_stock:
            raise ValueError(f"Insufficient stock. Available: {available_stock}")
        
        update_query = "UPDATE cart SET quantity = %s WHERE cart_id = %s"
        try:
            rows_affected = Database.execute_query(update_query, (quantity, cart_id), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating cart: {e}")
            raise
    
    @staticmethod
    def remove_item(cart_id):
        """Remove cart item"""
        query = "DELETE FROM cart WHERE cart_id = %s"
        try:
            rows_affected = Database.execute_query(query, (cart_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error removing cart item: {e}")
            raise
    
    @staticmethod
    def clear_cart(user_id):
        """Clear all cart items for user"""
        query = "DELETE FROM cart WHERE user_id = %s"
        try:
            rows_affected = Database.execute_query(query, (user_id,), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error clearing cart: {e}")
            raise
    
    @staticmethod
    def calculate_total(user_id):
        """Calculate cart total"""
        query = """
            SELECT SUM(p.price * c.quantity) as total
            FROM cart c
            JOIN products p ON c.product_id = p.product_id
            WHERE c.user_id = %s
        """
        try:
            result = Database.execute_query(query, (user_id,), fetch=True)
            if result and result[0][0] is not None:
                return float(result[0][0])
            return 0.0
        except Exception as e:
            print(f"Error calculating total: {e}")
            raise
```

### app/models/order.py
```python
"""Order and OrderItem models"""

from app.database.db_universal import Database


class Order:
    """Order model"""
    
    def __init__(self, order_id, user_id, total_amount, order_date, order_status):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.order_date = order_date
        self.order_status = order_status
    
    @staticmethod
    def create(user_id, total_amount):
        """Create a new order"""
        query = """
            INSERT INTO orders (user_id, total_amount, order_status)
            VALUES (%s, %s, 'Pending')
        """
        try:
            order_id = Database.execute_query(query, (user_id, total_amount), fetch=False)
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            raise
    
    @staticmethod
    def get_user_orders(user_id):
        """Get all orders for a user"""
        query = """
            SELECT order_id, user_id, total_amount, order_date, order_status
            FROM orders WHERE user_id = %s
            ORDER BY order_date DESC
        """
        try:
            results = Database.execute_query(query, (user_id,), fetch=True)
            return [Order(row[0], row[1], row[2], row[3], row[4]) for row in results]
        except Exception as e:
            print(f"Error retrieving orders: {e}")
            raise
    
    @staticmethod
    def get_all_orders():
        """Get all orders (admin)"""
        query = """
            SELECT o.order_id, o.user_id, o.total_amount, o.order_date, o.order_status,
                   u.name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.user_id
            ORDER BY o.order_date DESC
        """
        try:
            results = Database.execute_query(query, None, fetch=True)
            orders = []
            for row in results:
                orders.append({
                    'order_id': row[0],
                    'user_id': row[1],
                    'total_amount': float(row[2]),
                    'order_date': row[3],
                    'order_status': row[4],
                    'user_name': row[5],
                    'user_email': row[6]
                })
            return orders
        except Exception as e:
            print(f"Error retrieving orders: {e}")
            raise
    
    @staticmethod
    def get_by_id(order_id):
        """Get order by ID"""
        query = """
            SELECT order_id, user_id, total_amount, order_date, order_status
            FROM orders WHERE order_id = %s
        """
        try:
            results = Database.execute_query(query, (order_id,), fetch=True)
            if results:
                row = results[0]
                return Order(row[0], row[1], row[2], row[3], row[4])
            return None
        except Exception as e:
            print(f"Error retrieving order: {e}")
            raise
    
    @staticmethod
    def update_status(order_id, status):
        """Update order status"""
        valid_statuses = ['Pending', 'Shipped', 'Delivered']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status")
        
        query = "UPDATE orders SET order_status = %s WHERE order_id = %s"
        try:
            rows_affected = Database.execute_query(query, (status, order_id), fetch=False)
            return rows_affected
        except Exception as e:
            print(f"Error updating order status: {e}")
            raise
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'order_id': self.order_id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'order_date': self.order_date,
            'order_status': self.order_status
        }


class OrderItem:
    """OrderItem model"""
    
    def __init__(self, order_item_id, order_id, product_id, quantity, price):
        self.order_item_id = order_item_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
    
    @staticmethod
    def create(order_id, product_id, quantity, price):
        """Create a new order item"""
        query = """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
        """
        try:
            order_item_id = Database.execute_query(
                query, (order_id, product_id, quantity, price), fetch=False
            )
            return order_item_id
        except Exception as e:
            print(f"Error creating order item: {e}")
            raise
    
    @staticmethod
    def get_order_items(order_id):
        """Get all items for an order"""
        query = """
            SELECT oi.order_item_id, oi.order_id, oi.product_id, oi.quantity, oi.price,
                   p.product_name, p.description, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = %s
            ORDER BY oi.order_item_id
        """
        try:
            results = Database.execute_query(query, (order_id,), fetch=True)
            order_items = []
            for row in results:
                order_items.append({
                    'order_item_id': row[0],
                    'order_id': row[1],
                    'product_id': row[2],
                    'quantity': row[3],
                    'price': float(row[4]),
                    'product_name': row[5],
                    'description': row[6],
                    'image_url': row[7],
                    'subtotal': float(row[4]) * row[3]
                })
            return order_items
        except Exception as e:
            print(f"Error retrieving order items: {e}")
            raise
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'order_item_id': self.order_item_id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': float(self.price)
        }
```

---

## Blueprints

### app/auth/__init__.py
```python
"""Authentication blueprint"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.user import User
from app.utils.validation import validate_email, validate_password, validate_name
from app.utils.error_handler import log_error
from app.auth.decorators import login_required, admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        # Validate name
        name_valid, sanitized_name, name_error = validate_name(name)
        if not name_valid:
            flash(name_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=email)
        
        # Validate email
        email_valid, sanitized_email, email_error = validate_email(email)
        if not email_valid:
            flash(email_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            flash(password_error, 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Check if email exists
        try:
            existing_user = User.find_by_email(sanitized_email)
            if existing_user:
                flash('Email already registered', 'error')
                return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        except Exception as e:
            log_error(e, "register - check existing user")
            flash('Registration failed', 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
        
        # Create user
        try:
            user_id = User.create(sanitized_name, sanitized_email, password, role='customer')
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            log_error(e, "register - create user")
            flash('Registration failed', 'error')
            return render_template('auth/register.html', name=sanitized_name, email=sanitized_email)
    
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('auth/login.html', email=email)
        
        # Sanitize email
        email_valid, sanitized_email, email_error = validate_email(email)
        if not email_valid:
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html', email=email)
        
        try:
            user = User.find_by_email(sanitized_email)
            
            if user and user.verify_password(password):
                # Create session
                session['user_id'] = user.user_id
                session['role'] = user.role
                session['name'] = user.name
                
                flash(f'Welcome back, {user.name}!', 'success')
                
                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.browse_products'))
            else:
                flash('Invalid email or password', 'error')
                return render_template('auth/login.html', email=email)
        except Exception as e:
            log_error(e, "login")
            flash('Login failed', 'error')
            return render_template('auth/login.html', email=email)
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))
```

### app/auth/decorators.py
```python
"""Authorization decorators"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('user.browse_products'))
        
        return f(*args, **kwargs)
    return decorated_function
```

