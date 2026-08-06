"""
Universal database module supporting MySQL
Optimised for Vercel serverless environment.
"""

import os
from urllib.parse import urlparse


class UniversalDatabase:
    """
    Database connection manager for MySQL.
    Supports both DATABASE_URL (mysql://...) and individual DB_* env vars.
    Designed for Vercel serverless: reuses the connection across warm invocations
    and creates a fresh one on cold starts or when the previous connection drops.
    """

    _connection = None
    _db_type = 'mysql'

    # ------------------------------------------------------------------ #
    # Initialisation
    # ------------------------------------------------------------------ #

    @classmethod
    def init_db(cls, config=None):
        """
        Initialise database connection.

        Args:
            config: Optional dict with DB_* keys (used when DATABASE_URL is absent).
        """
        if cls._connection is not None and cls._is_connection_alive():
            return

        database_url = os.environ.get('DATABASE_URL', '')

        try:
            if database_url and database_url.startswith('mysql'):
                cls._init_mysql_from_url(database_url)
            else:
                cls._init_mysql_from_config(config or {})

            print("MySQL database connection initialised.")
        except Exception as e:
            print(f"Error initialising database connection: {e}")
            raise

    @classmethod
    def _init_mysql_from_url(cls, database_url):
        """Parse mysql://user:pass@host:port/db and open a connection."""
        import mysql.connector

        parsed = urlparse(database_url)
        cls._connection = mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            autocommit=False,
            connection_timeout=30,
        )

    @classmethod
    def _init_mysql_from_config(cls, config):
        """Open a MySQL connection from individual DB_* env vars / config dict."""
        import mysql.connector

        cls._connection = mysql.connector.connect(
            host=config.get('DB_HOST') or os.environ.get('DB_HOST', 'localhost'),
            port=int(config.get('DB_PORT') or os.environ.get('DB_PORT', 3306)),
            user=config.get('DB_USER') or os.environ.get('DB_USER', 'root'),
            password=config.get('DB_PASSWORD') or os.environ.get('DB_PASSWORD', ''),
            database=config.get('DB_NAME') or os.environ.get('DB_NAME', 'shopping_system'),
            autocommit=False,
            connection_timeout=30,
        )

    # ------------------------------------------------------------------ #
    # Connection management
    # ------------------------------------------------------------------ #

    @classmethod
    def _is_connection_alive(cls):
        """Return True if the cached connection is still usable."""
        try:
            cls._connection.ping(reconnect=False)
            return True
        except Exception:
            return False

    @classmethod
    def get_connection(cls):
        """
        Return an active MySQL connection.
        Re-connects automatically if the connection has gone away (serverless cold start).
        """
        if cls._connection is None or not cls._is_connection_alive():
            cls._connection = None
            cls.init_db()
        return cls._connection

    @classmethod
    def release_connection(cls, connection):  # noqa: ARG003
        """
        No-op for the single-connection model.
        Kept for API compatibility with callers that call release_connection().
        """
        pass

    # ------------------------------------------------------------------ #
    # Query helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def execute_query(cls, query, params=None, fetch=True):
        """
        Execute a parameterised SQL query.

        Args:
            query:  SQL string with %s placeholders.
            params: Tuple/list of parameter values.
            fetch:  If True, return rows; otherwise commit and return
                    lastrowid (for INSERT) or rowcount (for UPDATE/DELETE).

        Returns:
            List of rows when fetch=True, otherwise int.
        """
        connection = cls.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute(query, params or ())

            if fetch:
                return cursor.fetchall()
            else:
                connection.commit()
                stripped = query.strip().upper()
                if stripped.startswith('INSERT'):
                    return cursor.lastrowid
                return cursor.rowcount
        except Exception as e:
            try:
                connection.rollback()
            except Exception:
                pass
            print(f"Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()


# ------------------------------------------------------------------ #
# Backward-compatible aliases
# ------------------------------------------------------------------ #

class Database(UniversalDatabase):
    """Alias kept for backward compatibility."""
    pass


def init_db(config=None):
    """Initialise the database connection."""
    UniversalDatabase.init_db(config)


def get_connection():
    """Return an active database connection."""
    return UniversalDatabase.get_connection()


def execute_query(query, params=None, fetch=True):
    """Execute a parameterised query."""
    return UniversalDatabase.execute_query(query, params, fetch)
