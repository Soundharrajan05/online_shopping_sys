"""
Universal database module supporting both MySQL and PostgreSQL
"""

import os
from urllib.parse import urlparse


class UniversalDatabase:
    """Database connection manager supporting MySQL and PostgreSQL"""
    
    _pool = None
    _db_type = None
    
    @classmethod
    def init_db(cls, config=None):
        """
        Initialize database connection pool
        
        Args:
            config: Optional dictionary with database configuration
        """
        if cls._pool is not None:
            return
        
        # Detect database type from environment
        database_url = os.environ.get('DATABASE_URL')
        
        try:
            if database_url:
                # PostgreSQL (Render.com)
                cls._db_type = 'postgresql'
                cls._init_postgresql(database_url)
            else:
                # MySQL (Local development)
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
            1,  # minconn
            10,  # maxconn
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path[1:]  # Remove leading '/'
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
            raise Exception("Database pool not initialized. Call init_db() first.")
        
        if cls._db_type == 'postgresql':
            return cls._pool.getconn()
        else:
            return cls._pool.get_connection()
    
    @classmethod
    def release_connection(cls, connection):
        """Release connection back to pool"""
        if cls._db_type == 'postgresql':
            cls._pool.putconn(connection)
        # MySQL connections are automatically returned when closed
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """
        Execute parameterized query
        
        Args:
            query: SQL query string
            params: Tuple of parameters
            fetch: Whether to fetch results
        
        Returns:
            Query results or affected rows
        """
        connection = None
        cursor = None
        try:
            connection = cls.get_connection()
            cursor = connection.cursor()
            
            # Adapt query for PostgreSQL if needed
            if cls._db_type == 'postgresql':
                query = query.replace('%s', '%s')  # Already compatible
            
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
                return results
            else:
                connection.commit()
                if query.strip().upper().startswith('INSERT'):
                    if cls._db_type == 'postgresql':
                        # PostgreSQL uses RETURNING for last insert id
                        return cursor.fetchone()[0] if cursor.rowcount > 0 else None
                    else:
                        return cursor.lastrowid
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


# Maintain backward compatibility
class Database(UniversalDatabase):
    """Alias for backward compatibility"""
    pass


def init_db(config=None):
    """Initialize database connection pool"""
    UniversalDatabase.init_db(config)


def get_connection():
    """Get database connection from pool"""
    return UniversalDatabase.get_connection()


def execute_query(query, params=None, fetch=True):
    """Execute parameterized query"""
    return UniversalDatabase.execute_query(query, params, fetch)
