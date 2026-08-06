"""Create the database tables from schema.sql."""
import os
import sys
import mysql.connector
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()


def get_connection(host, port, user, password, database=None):
    kwargs = dict(host=host, port=port, user=user, password=password)
    if database:
        kwargs['database'] = database
    return mysql.connector.connect(**kwargs)


def main():
    database_url = os.environ.get('DATABASE_URL', '')

    if database_url.startswith('mysql'):
        parsed = urlparse(database_url)
        host = parsed.hostname
        port = parsed.port or 3306
        user = parsed.username
        password = parsed.password
        db_name = parsed.path.lstrip('/')
    else:
        host = os.environ.get('DB_HOST', 'localhost')
        port = int(os.environ.get('DB_PORT', 3306))
        user = os.environ.get('DB_USER', 'root')
        password = os.environ.get('DB_PASSWORD', '')
        db_name = os.environ.get('DB_NAME', 'shopping_system')

    print(f"Connecting to {host}:{port} / {db_name}")

    # Create database if using local MySQL
    if host in ('localhost', '127.0.0.1'):
        conn = get_connection(host, port, user, password)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.close()
        conn.close()
        print(f"Database '{db_name}' ready.")

    # Run schema
    conn = get_connection(host, port, user, password, db_name)
    cursor = conn.cursor()

    if not os.path.exists('schema.sql'):
        print("schema.sql not found.")
        sys.exit(1)

    with open('schema.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    for stmt in [s.strip() for s in sql.split(';') if s.strip()]:
        cursor.execute(stmt)

    conn.commit()
    cursor.close()
    conn.close()
    print("Schema applied successfully.")


if __name__ == '__main__':
    main()
