#!/usr/bin/env python3
"""
Initialize database for Render.com deployment
Run this script in Render shell after first deployment
"""

import os
from app import create_app
from app.database.db_universal import Database

def init_database():
    """Initialize PostgreSQL database with schema"""
    print("=" * 70)
    print("Initializing Database for Render.com")
    print("=" * 70)
    
    app = create_app('production')
    
    with app.app_context():
        try:
            # Read PostgreSQL schema
            print("\n1. Reading schema file...")
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
                    print(f"   ✓ Executed: {stmt[:50]}...")
            
            conn.commit()
            cursor.close()
            Database.release_connection(conn)
            
            print("\n" + "=" * 70)
            print("Database initialized successfully!")
            print("=" * 70)
            print("\nNext step: Run 'python seed_data.py' to add sample data")
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True


if __name__ == '__main__':
    init_database()
