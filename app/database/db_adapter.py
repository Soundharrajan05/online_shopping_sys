"""
Database adapter to support both MySQL (local) and PostgreSQL (production)
"""

import os
from urllib.parse import urlparse


def get_db_config():
    """
    Get database configuration based on environment
    
    Returns:
        dict: Database configuration with type and connection parameters
    """
    # Check if DATABASE_URL is set (Render.com provides this)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse PostgreSQL URL from Render.com
        # Format: postgresql://user:password@host:port/database
        parsed = urlparse(database_url)
        
        return {
            'type': 'postgresql',
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path[1:],  # Remove leading '/'
        }
    else:
        # Use MySQL configuration from environment variables (local development)
        return {
            'type': 'mysql',
            'host': os.environ.get('DB_HOST', 'localhost'),
            'port': int(os.environ.get('DB_PORT', 3306)),
            'user': os.environ.get('DB_USER', 'root'),
            'password': os.environ.get('DB_PASSWORD', ''),
            'database': os.environ.get('DB_NAME', 'shopping_system'),
        }


def get_connection_pool(config):
    """
    Create appropriate connection pool based on database type
    
    Args:
        config: Database configuration dictionary
    
    Returns:
        Connection pool object
    """
    db_type = config.get('type', 'mysql')
    
    if db_type == 'postgresql':
        # Use psycopg2 for PostgreSQL
        import psycopg2
        from psycopg2 import pool
        
        return pool.SimpleConnectionPool(
            1,  # minconn
            5,  # maxconn
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database']
        )
    else:
        # Use mysql-connector for MySQL
        from mysql.connector import pooling
        
        return pooling.MySQLConnectionPool(
            pool_name="shopping_pool",
            pool_size=5,
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            database=config['database'],
            autocommit=False
        )


def adapt_query(query, db_type='mysql'):
    """
    Adapt SQL query for different database types
    
    Args:
        query: SQL query string
        db_type: Database type ('mysql' or 'postgresql')
    
    Returns:
        Adapted query string
    """
    if db_type == 'postgresql':
        # Replace MySQL-specific syntax with PostgreSQL
        # Replace AUTO_INCREMENT with SERIAL
        query = query.replace('AUTO_INCREMENT', '')
        query = query.replace('INT PRIMARY KEY', 'SERIAL PRIMARY KEY')
        
        # Replace backticks with double quotes
        query = query.replace('`', '"')
        
        # Replace ENUM with VARCHAR (PostgreSQL doesn't have ENUM in the same way)
        # This is a simplified conversion - you may need custom handling
        
    return query
