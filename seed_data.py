#!/usr/bin/env python3
"""
Seed data script for Online Shopping System
Creates initial data including admin user, categories, and sample products
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()


def get_db_connection(host, user, password, db_name):
    """
    Create database connection
    
    Args:
        host: MySQL host
        user: MySQL user
        password: MySQL password
        db_name: Database name
    
    Returns:
        MySQL connection object
    """
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
    """Create admin user with email: admin@shop.com, password: admin123"""
    if check_admin_exists(cursor):
        print("  ✓ Admin user already exists (admin@shop.com)")
        return False
    
    hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
    query = """
        INSERT INTO users (name, email, password, role)
        VALUES (%s, %s, %s, %s)
    """
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
    """Create sample categories: Electronics, Clothing, Books"""
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
    """Create sample products for each category"""
    
    # Get category IDs
    electronics_id = get_category_id(cursor, 'Electronics')
    clothing_id = get_category_id(cursor, 'Clothing')
    books_id = get_category_id(cursor, 'Books')
    
    # Sample products data
    products = [
        # Electronics
        {
            'name': 'Laptop - Dell XPS 15',
            'description': 'High-performance laptop with Intel Core i7, 16GB RAM, 512GB SSD. Perfect for work and gaming.',
            'price': 1299.99,
            'stock': 15,
            'image': 'https://via.placeholder.com/300x300?text=Dell+XPS+15',
            'category_id': electronics_id
        },
        {
            'name': 'Wireless Mouse - Logitech MX Master 3',
            'description': 'Ergonomic wireless mouse with precision scrolling and customizable buttons.',
            'price': 99.99,
            'stock': 50,
            'image': 'https://via.placeholder.com/300x300?text=Logitech+Mouse',
            'category_id': electronics_id
        },
        {
            'name': 'Smartphone - Samsung Galaxy S23',
            'description': '6.1-inch display, 128GB storage, 5G enabled. Capture stunning photos with triple camera.',
            'price': 799.99,
            'stock': 25,
            'image': 'https://via.placeholder.com/300x300?text=Samsung+S23',
            'category_id': electronics_id
        },
        {
            'name': 'Wireless Headphones - Sony WH-1000XM5',
            'description': 'Industry-leading noise cancellation, 30-hour battery life, premium sound quality.',
            'price': 399.99,
            'stock': 30,
            'image': 'https://via.placeholder.com/300x300?text=Sony+Headphones',
            'category_id': electronics_id
        },
        {
            'name': '4K Monitor - LG UltraFine 27"',
            'description': '27-inch 4K UHD display with HDR support and USB-C connectivity.',
            'price': 549.99,
            'stock': 20,
            'image': 'https://via.placeholder.com/300x300?text=LG+Monitor',
            'category_id': electronics_id
        },
        
        # Clothing
        {
            'name': 'Men\'s Cotton T-Shirt - Navy Blue',
            'description': 'Comfortable 100% cotton t-shirt, available in multiple sizes. Perfect for casual wear.',
            'price': 24.99,
            'stock': 100,
            'image': 'https://via.placeholder.com/300x300?text=Navy+T-Shirt',
            'category_id': clothing_id
        },
        {
            'name': 'Women\'s Denim Jeans - Slim Fit',
            'description': 'Classic slim-fit jeans with stretch fabric for comfort. Available in various sizes.',
            'price': 59.99,
            'stock': 75,
            'image': 'https://via.placeholder.com/300x300?text=Denim+Jeans',
            'category_id': clothing_id
        },
        {
            'name': 'Unisex Hoodie - Gray',
            'description': 'Warm and cozy hoodie with front pocket. Perfect for cool weather.',
            'price': 44.99,
            'stock': 60,
            'image': 'https://via.placeholder.com/300x300?text=Gray+Hoodie',
            'category_id': clothing_id
        },
        {
            'name': 'Running Shoes - Nike Air Zoom',
            'description': 'Lightweight running shoes with responsive cushioning and breathable mesh.',
            'price': 129.99,
            'stock': 40,
            'image': 'https://via.placeholder.com/300x300?text=Nike+Shoes',
            'category_id': clothing_id
        },
        {
            'name': 'Winter Jacket - Waterproof',
            'description': 'Insulated winter jacket with waterproof exterior. Keeps you warm and dry.',
            'price': 149.99,
            'stock': 35,
            'image': 'https://via.placeholder.com/300x300?text=Winter+Jacket',
            'category_id': clothing_id
        },
        
        # Books
        {
            'name': 'The Pragmatic Programmer',
            'description': 'Your journey to mastery. Essential reading for software developers.',
            'price': 49.99,
            'stock': 45,
            'image': 'https://via.placeholder.com/300x300?text=Pragmatic+Programmer',
            'category_id': books_id
        },
        {
            'name': 'Clean Code by Robert Martin',
            'description': 'A handbook of agile software craftsmanship. Learn to write better code.',
            'price': 44.99,
            'stock': 50,
            'image': 'https://via.placeholder.com/300x300?text=Clean+Code',
            'category_id': books_id
        },
        {
            'name': 'Design Patterns: Elements of Reusable Object-Oriented Software',
            'description': 'Classic book on software design patterns by the Gang of Four.',
            'price': 54.99,
            'stock': 30,
            'image': 'https://via.placeholder.com/300x300?text=Design+Patterns',
            'category_id': books_id
        },
        {
            'name': 'Introduction to Algorithms',
            'description': 'Comprehensive introduction to algorithms and data structures. MIT Press.',
            'price': 89.99,
            'stock': 25,
            'image': 'https://via.placeholder.com/300x300?text=Algorithms',
            'category_id': books_id
        },
        {
            'name': 'Python Crash Course',
            'description': 'A hands-on, project-based introduction to programming with Python.',
            'price': 39.99,
            'stock': 55,
            'image': 'https://via.placeholder.com/300x300?text=Python+Course',
            'category_id': books_id
        }
    ]
    
    created_count = 0
    query = """
        INSERT INTO products (product_name, description, price, stock_quantity, image_url, category_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for product in products:
        if check_product_exists(cursor, product['name']):
            print(f"  ✓ Product '{product['name']}' already exists")
        else:
            cursor.execute(query, (
                product['name'],
                product['description'],
                product['price'],
                product['stock'],
                product['image'],
                product['category_id']
            ))
            print(f"  ✓ Created product '{product['name']}'")
            created_count += 1
    
    return created_count


def main():
    """Main function to seed database"""
    # Get database configuration from environment or use defaults
    host = os.environ.get('DB_HOST', 'localhost')
    user = os.environ.get('DB_USER', 'root')
    password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'shopping_system')
    
    print("=" * 70)
    print("Online Shopping System - Seed Data Script")
    print("=" * 70)
    print(f"Host: {host}")
    print(f"User: {user}")
    print(f"Database: {db_name}")
    print("=" * 70)
    
    # Connect to database
    connection = get_db_connection(host, user, password, db_name)
    cursor = connection.cursor()
    
    try:
        # Create admin user
        print("\n[1/3] Creating admin user...")
        create_admin_user(cursor)
        
        # Create categories
        print("\n[2/3] Creating categories...")
        categories_created = create_categories(cursor)
        
        # Create sample products
        print("\n[3/3] Creating sample products...")
        products_created = create_sample_products(cursor)
        
        # Commit all changes
        connection.commit()
        
        print("\n" + "=" * 70)
        print("Seed data completed successfully!")
        print("=" * 70)
        print(f"Summary:")
        print(f"  - Admin user: admin@shop.com (password: admin123)")
        print(f"  - Categories: 3 total (Electronics, Clothing, Books)")
        print(f"  - Products: 15 total (5 per category)")
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
