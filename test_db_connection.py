#!/usr/bin/env python3
"""
Test database connection and table existence
This will help diagnose registration issues
"""

import os
import sys

def test_connection():
    """Test basic database connection"""
    print("=" * 70)
    print("Testing Database Connection")
    print("=" * 70)
    
    # Check environment variables
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("✗ DATABASE_URL not set!")
        return False
    
    print(f"✓ DATABASE_URL is set")
    print(f"  Connection: {database_url[:30]}...{database_url[-20:]}")
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Test query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            Database.release_connection(conn)
            
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tables():
    """Test if required tables exist"""
    print()
    print("=" * 70)
    print("Testing Database Tables")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.database.db_universal import Database
        
        app = create_app('production')
        with app.app_context():
            conn = Database.get_connection()
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['users', 'categories', 'products', 'cart', 'orders', 'order_items']
            
            if not tables:
                print("✗ No tables found!")
                print()
                print("SOLUTION: Database needs initialization")
                print("The auto_init_db.py should run automatically on next deployment")
                cursor.close()
                Database.release_connection(conn)
                return False
            
            print(f"Found {len(tables)} tables:")
            all_present = True
            for table in required_tables:
                if table in tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (MISSING)")
                    all_present = False
            
            cursor.close()
            Database.release_connection(conn)
            
            if not all_present:
                print()
                print("SOLUTION: Some tables are missing")
                print("The auto_init_db.py should create them on next deployment")
            
            return all_present
    except Exception as e:
        print(f"✗ Error checking tables: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_creation():
    """Test if we can create a user"""
    print()
    print("=" * 70)
    print("Testing User Creation")
    print("=" * 70)
    
    try:
        from app import create_app
        from app.models.user import User
        
        app = create_app('production')
        with app.app_context():
            # Try to find existing test user
            test_email = "test_" + str(os.urandom(4).hex()) + "@example.com"
            
            print(f"Attempting to create test user: {test_email}")
            
            user_id = User.create(
                name="Test User",
                email=test_email,
                password="testpass123",
                role="customer"
            )
            
            print(f"✓ User created successfully! ID: {user_id}")
            
            # Verify user exists
            user = User.find_by_email(test_email)
            if user:
                print(f"✓ User verified: {user.name} ({user.email})")
                return True
            else:
                print("✗ User creation succeeded but verification failed")
                return False
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print()
    print("=" * 70)
    print("Database Diagnostic Tool")
    print("=" * 70)
    print()
    
    results = {
        'connection': test_connection(),
        'tables': test_tables(),
        'user_creation': test_user_creation()
    }
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    print()
    print("=" * 70)
    
    if all(results.values()):
        print("✓ ALL TESTS PASSED!")
        print()
        print("Database is working correctly.")
        print("Registration should work now.")
    else:
        print("✗ SOME TESTS FAILED")
        print()
        print("Likely causes:")
        print("1. Database tables don't exist yet")
        print("2. auto_init_db.py hasn't run yet")
        print("3. Database connection issue")
        print()
        print("Solution:")
        print("1. Check Render logs for auto-initialization messages")
        print("2. Try manual redeploy: Clear cache & deploy")
        print("3. Verify DATABASE_URL is correct")
    
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
