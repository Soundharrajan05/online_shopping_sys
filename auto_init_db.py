#!/usr/bin/env python3
"""
Automatic database initialization script
This runs automatically when the app starts on Render
No Shell access needed!
"""

import os
from app import create_app
from app.database.db_universal import Database

def check_if_initialized():
    """Check if database is already initialized"""
    try:
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Try to query users table
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            cursor.close()
            Database.release_connection(conn)
            
            print(f"✓ Database already initialized ({count} users found)")
            return True
    except Exception as e:
        print(f"Database not initialized yet: {e}")
        return False

def initialize_database():
    """Initialize database with schema"""
    print("=" * 70)
    print("Auto-Initializing Database")
    print("=" * 70)
    
    try:
        app = create_app('production')
        with app.app_context():
            # Read PostgreSQL schema
            print("1. Reading schema file...")
            with open('schema_postgresql.sql', 'r') as f:
                schema = f.read()
            
            # Execute schema
            print("2. Creating tables...")
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Split and execute each statement
            statements = [s.strip() for s in schema.split(';') if s.strip()]
            for stmt in statements:
                if stmt:
                    cursor.execute(stmt)
                    print(f"   ✓ Executed statement")
            
            conn.commit()
            cursor.close()
            Database.release_connection(conn)
            
            print("✓ Database schema created successfully!")
            return True
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def seed_database():
    """Add sample data"""
    print("=" * 70)
    print("Adding Sample Data")
    print("=" * 70)
    
    try:
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Create categories
            print("1. Creating categories...")
            categories = [
                ('Electronics',),
                ('Books',),
                ('Clothing',)
            ]
            
            for (name,) in categories:
                cursor.execute(
                    "INSERT INTO categories (category_name) VALUES (%s)",
                    (name,)
                )
            print("   ✓ 3 categories created")
            
            # Create admin user
            print("2. Creating admin user...")
            from werkzeug.security import generate_password_hash
            
            admin_password = generate_password_hash('admin123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('admin', 'admin@shop.com', admin_password, 'admin'))
            print("   ✓ Admin: admin@shop.com / admin123")
            
            # Create customer user
            print("3. Creating customer user...")
            customer_password = generate_password_hash('customer123')
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, ('customer', 'customer@test.com', customer_password, 'customer'))
            print("   ✓ Customer: customer@test.com / customer123")
            
            # Create sample products
            print("4. Creating sample products...")
            products = [
                ('HP Victus Gaming Laptop', 1, 899.99, 25, 'High-performance gaming laptop', 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500'),
                ('Dell XPS 13', 1, 1299.99, 15, 'Premium ultrabook', 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=500'),
                ('iPhone 14 Pro', 1, 999.99, 50, 'Latest iPhone model', 'https://images.unsplash.com/photo-1678652197831-2d180705cd2c?w=500'),
                ('Samsung Galaxy S23', 1, 899.99, 40, 'Flagship Android phone', 'https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=500'),
                ('Clean Code by Robert Martin', 2, 44.99, 50, 'Software engineering book', 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=500'),
                ('The Pragmatic Programmer', 2, 49.99, 30, 'Programming best practices', 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500'),
                ('Men\'s T-Shirt', 3, 19.99, 100, 'Comfortable cotton t-shirt', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=500'),
                ('Women\'s Dress', 3, 59.99, 50, 'Elegant summer dress', 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500'),
                ('Sony WH-1000XM5', 1, 399.99, 20, 'Noise-cancelling headphones', 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=500'),
                ('MacBook Pro 14"', 1, 1999.99, 10, 'Apple laptop for professionals', 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=500'),
            ]
            
            for name, cat_id, price, stock, desc, img in products:
                cursor.execute("""
                    INSERT INTO products (product_name, category_id, price, stock_quantity, description, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, cat_id, price, stock, desc, img))
            
            print(f"   ✓ {len(products)} products created")
            
            conn.commit()
            cursor.close()
            Database.release_connection(conn)
            
            print("✓ Sample data added successfully!")
            return True
    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print()
    print("=" * 70)
    print("Automatic Database Setup (No Shell Required!)")
    print("=" * 70)
    print()
    
    # Check if already initialized
    if check_if_initialized():
        print()
        print("=" * 70)
        print("✓ Database is ready! No action needed.")
        print("=" * 70)
        print()
        return True
    
    # Initialize database
    print()
    if not initialize_database():
        print()
        print("=" * 70)
        print("✗ Failed to initialize database")
        print("=" * 70)
        print()
        return False
    
    # Seed database
    print()
    if not seed_database():
        print()
        print("=" * 70)
        print("✗ Failed to seed database")
        print("=" * 70)
        print()
        return False
    
    print()
    print("=" * 70)
    print("✓ Database setup complete!")
    print()
    print("Test Credentials:")
    print("  Customer: customer@test.com / customer123")
    print("  Admin: admin@shop.com / admin123")
    print("=" * 70)
    print()
    
    return True

if __name__ == '__main__':
    main()
