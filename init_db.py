#!/usr/bin/env python3
"""
Database initialization script for the Online Shopping System

This script performs the following operations:
1. Creates the database if it doesn't exist
2. Executes the schema.sql file to create all tables
3. Sets up foreign key constraints and indexes

The script reads database configuration from environment variables or .env file.
If no configuration is provided, it uses default values (localhost, root, no password).

Usage:
    python init_db.py

Environment Variables:
    DB_HOST: MySQL host (default: localhost)
    DB_USER: MySQL user (default: root)
    DB_PASSWORD: MySQL password (default: empty)
    DB_NAME: Database name (default: shopping_system)

The script will:
- Create the database with UTF8MB4 character set for full Unicode support
- Execute all SQL statements from schema.sql
- Report success or failure for each operation

Validates: Requirements 14.7
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()


def create_database(host, user, password, db_name):
    """
    Create database if it doesn't exist
    
    Creates a new MySQL database with UTF8MB4 character set and unicode collation.
    UTF8MB4 supports full Unicode including emojis and special characters.
    
    Args:
        host: MySQL host address (e.g., 'localhost', '127.0.0.1')
        user: MySQL username with CREATE DATABASE privileges
        password: MySQL password for the user
        db_name: Name of the database to create
    
    Raises:
        SystemExit: If database creation fails
    """
    connection = None
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        # UTF8MB4 character set supports full Unicode including emojis
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
    """
    Execute SQL schema file to create tables and constraints
    
    Reads the schema.sql file and executes each SQL statement to create:
    - All database tables (users, categories, products, cart, orders, order_items)
    - Foreign key constraints for referential integrity
    - Indexes for query optimization
    - Default values and constraints
    
    Args:
        host: MySQL host address
        user: MySQL username with CREATE TABLE privileges
        password: MySQL password for the user
        db_name: Name of the database to use
        schema_file: Path to the SQL schema file (default: 'schema.sql')
    
    Raises:
        SystemExit: If schema file not found or execution fails
    """
    connection = None
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        
        cursor = connection.cursor()
        
        # Read schema file
        if not os.path.exists(schema_file):
            print(f"Error: Schema file '{schema_file}' not found.")
            sys.exit(1)
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Split by semicolon and execute each statement
        # This allows executing multiple CREATE TABLE statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                # Print first 50 characters of each statement for progress tracking
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
    """
    Main function to initialize database
    
    Orchestrates the database initialization process:
    1. Loads configuration from environment variables
    2. Creates the database
    3. Executes the schema to create tables
    4. Reports success or failure
    """
    # Get database configuration from environment or use defaults
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
    
    # Create database
    print("\nStep 1: Creating database...")
    create_database(host, user, password, db_name)
    
    # Execute schema
    print("\nStep 2: Executing schema...")
    execute_schema(host, user, password, db_name)
    
    print("\n" + "=" * 60)
    print("Database initialization completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()

