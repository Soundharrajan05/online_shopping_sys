import mysql.connector
from mysql.connector import pooling, Error


class Database:
    """Database connection manager with connection pooling"""
    
    _pool = None
    
    @classmethod
    def init_db(cls, config):
        """
        Initialize database connection pool
        
        Args:
            config: Dictionary with DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_POOL_SIZE
        """
        # Skip if pool already initialized for the same database
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
        """
        Get connection from pool
        
        Returns:
            MySQL connection object
        """
        if cls._pool is None:
            raise Exception("Database pool not initialized. Call init_db() first.")
        return cls._pool.get_connection()
    
    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """
        Execute parameterized query
        
        Args:
            query: SQL query string with %s placeholders
            params: Tuple of parameters for the query
            fetch: Whether to fetch results (True for SELECT, False for INSERT/UPDATE/DELETE)
        
        Returns:
            For SELECT: List of tuples with query results
            For INSERT: Last inserted ID
            For UPDATE/DELETE: Number of affected rows
        """
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
