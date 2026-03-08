#!/usr/bin/env python3
"""
Diagnostic script for Render deployment issues
Run this in Render Shell to check what's wrong
"""

import os
import sys

def check_environment():
    """Check environment variables"""
    print("=" * 70)
    print("1. Checking Environment Variables")
    print("=" * 70)
    
    required_vars = {
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Flask secret key',
        'FLASK_CONFIG': 'Configuration environment'
    }
    
    all_good = True
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if var == 'DATABASE_URL':
                display = value[:20] + '...' + value[-20:] if len(value) > 40 else value
            elif var == 'SECRET_KEY':
                display = '***' + value[-4:] if len(value) > 4 else '***'
            else:
                display = value
            print(f"✓ {var}: {display}")
        else:
            print(f"✗ {var}: NOT SET ({description})")
            all_good = False
    
    print()
    return all_good

def check_database_connection():
    """Check if database connection works"""
    print("=" * 70)
    print("2. Checking Database Connection")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            print("✓ App created successfully")
            
            conn = Database.get_connection()
            print("✓ Database connection successful")
            
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"✓ PostgreSQL version: {version}")
            
            cursor.close()
            Database.release_connection(conn)
            
            print()
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print()
        return False

def check_tables():
    """Check if database tables exist"""
    print("=" * 70)
    print("3. Checking Database Tables")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Check for tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'categories', 'products', 'cart', 'orders', 'order_items']
            
            if not tables:
                print("✗ No tables found in database")
                print()
                print("FIX: Run 'python render_init.py'")
                cursor.close()
                Database.release_connection(conn)
                return False
            
            print(f"Found {len(tables)} tables:")
            all_good = True
            for table in required_tables:
                if table in tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (MISSING)")
                    all_good = False
            
            cursor.close()
            Database.release_connection(conn)
            
            print()
            if not all_good:
                print("FIX: Run 'python render_init.py'")
            
            return all_good
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        print()
        print("FIX: Run 'python render_init.py'")
        return False

def check_users():
    """Check if users exist"""
    print("=" * 70)
    print("4. Checking Users")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT email, role FROM users ORDER BY role")
            users = cursor.fetchall()
            
            if not users:
                print("✗ No users found in database")
                print()
                print("FIX: Run 'python seed_data.py'")
                cursor.close()
                Database.release_connection(conn)
                return False
            
            print(f"Found {len(users)} users:")
            for email, role in users:
                print(f"  ✓ {email} ({role})")
            
            cursor.close()
            Database.release_connection(conn)
            
            print()
            return True
    except Exception as e:
        print(f"✗ Error checking users: {e}")
        print()
        print("FIX: Run 'python seed_data.py'")
        return False

def check_products():
    """Check if products exist"""
    print("=" * 70)
    print("5. Checking Products")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("✗ No products found in database")
                print()
                print("FIX: Run 'python seed_data.py'")
                cursor.close()
                Database.release_connection(conn)
                return False
            
            print(f"✓ Found {count} products")
            
            cursor.close()
            Database.release_connection(conn)
            
            print()
            return True
    except Exception as e:
        print(f"✗ Error checking products: {e}")
        print()
        return False

def main():
    print()
    print("=" * 70)
    print("Render Deployment Diagnostic Tool")
    print("=" * 70)
    print()
    
    results = {
        'environment': check_environment(),
        'database': check_database_connection(),
        'tables': check_tables(),
        'users': check_users(),
        'products': check_products()
    }
    
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check.capitalize()}: {status}")
    
    print()
    print("=" * 70)
    
    if all(results.values()):
        print("✓ ALL CHECKS PASSED!")
        print()
        print("Your app should be working correctly.")
        print("If you still have issues, check the Render logs.")
    else:
        print("✗ SOME CHECKS FAILED")
        print()
        print("Quick Fix:")
        print("1. Run: python render_init.py")
        print("2. Run: python seed_data.py")
        print("3. Run this diagnostic again")
    
    print("=" * 70)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
