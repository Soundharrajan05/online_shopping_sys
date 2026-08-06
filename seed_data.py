"""Seed the database with an admin user, categories and sample products."""
import os
import sys
import mysql.connector
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()


def get_connection():
    database_url = os.environ.get('DATABASE_URL', '')
    if database_url.startswith('mysql'):
        parsed = urlparse(database_url)
        return mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/')
        )
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=int(os.environ.get('DB_PORT', 3306)),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'shopping_system')
    )


def main():
    conn = get_connection()
    cursor = conn.cursor()

    # Admin user
    cursor.execute('SELECT COUNT(*) FROM users WHERE email=%s', ('admin@shop.com',))
    if cursor.fetchone()[0] == 0:
        hashed = generate_password_hash('admin123', method='pbkdf2:sha256')
        cursor.execute(
            'INSERT INTO users (name, email, password, role) VALUES (%s,%s,%s,%s)',
            ('Admin', 'admin@shop.com', hashed, 'admin')
        )
        print('Created admin: admin@shop.com / admin123')
    else:
        print('Admin already exists')

    # Categories
    for cat in ['Electronics', 'Clothing', 'Books']:
        cursor.execute('SELECT COUNT(*) FROM categories WHERE category_name=%s', (cat,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO categories (category_name) VALUES (%s)', (cat,))
            print(f'Created category: {cat}')

    conn.commit()

    cursor.execute('SELECT category_id, category_name FROM categories')
    cats = {name: cid for cid, name in cursor.fetchall()}

    products = [
        ('Laptop - Dell XPS 15', 'High-performance laptop with Intel Core i7, 16GB RAM, 512GB SSD.', 1299.99, 15,
         'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=300&h=300&fit=crop', cats['Electronics']),
        ('Wireless Mouse - Logitech MX Master 3', 'Ergonomic wireless mouse with precision scrolling.', 99.99, 50,
         'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop', cats['Electronics']),
        ('Smartphone - Samsung Galaxy S23', '6.1-inch display, 128GB storage, 5G enabled.', 799.99, 25,
         'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300&h=300&fit=crop', cats['Electronics']),
        ('Wireless Headphones - Sony WH-1000XM5', 'Industry-leading noise cancellation, 30-hour battery.', 399.99, 30,
         'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&h=300&fit=crop', cats['Electronics']),
        ('4K Monitor - LG UltraFine 27"', '27-inch 4K UHD display with HDR support.', 549.99, 20,
         'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=300&h=300&fit=crop', cats['Electronics']),
        ("Men's Cotton T-Shirt", 'Comfortable 100% cotton t-shirt, casual wear.', 24.99, 100,
         'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop', cats['Clothing']),
        ("Women's Denim Jeans - Slim Fit", 'Classic slim-fit jeans with stretch fabric.', 59.99, 75,
         'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&h=300&fit=crop', cats['Clothing']),
        ('Unisex Hoodie - Gray', 'Warm and cozy hoodie with front pocket.', 44.99, 60,
         'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=300&h=300&fit=crop', cats['Clothing']),
        ('Running Shoes - Nike Air Zoom', 'Lightweight running shoes with responsive cushioning.', 129.99, 40,
         'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop', cats['Clothing']),
        ('Winter Jacket - Waterproof', 'Insulated winter jacket, keeps you warm and dry.', 149.99, 35,
         'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=300&h=300&fit=crop', cats['Clothing']),
        ('The Pragmatic Programmer', 'Essential reading for software developers.', 49.99, 45,
         'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=300&fit=crop', cats['Books']),
        ('Clean Code by Robert Martin', 'A handbook of agile software craftsmanship.', 44.99, 50,
         'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=300&fit=crop', cats['Books']),
        ('Design Patterns: Gang of Four', 'Classic book on software design patterns.', 54.99, 30,
         'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=300&fit=crop', cats['Books']),
        ('Introduction to Algorithms', 'Comprehensive intro to algorithms and data structures.', 89.99, 25,
         'https://images.unsplash.com/photo-1509228627152-72ae9ae6848d?w=300&h=300&fit=crop', cats['Books']),
        ('Python Crash Course', 'A hands-on, project-based introduction to Python.', 39.99, 55,
         'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=300&h=300&fit=crop', cats['Books']),
    ]

    for p in products:
        cursor.execute('SELECT COUNT(*) FROM products WHERE product_name=%s', (p[0],))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                'INSERT INTO products (product_name, description, price, stock_quantity, image_url, category_id) VALUES (%s,%s,%s,%s,%s,%s)', p)
            print(f'Created: {p[0]}')
        else:
            print(f'Exists:  {p[0]}')

    conn.commit()
    cursor.close()
    conn.close()
    print('\nDone.')


if __name__ == '__main__':
    main()
