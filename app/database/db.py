"""
Database module — re-exports from db_universal for backward compatibility.

All code (app, tests, blueprints) can import from either
`app.database.db` or `app.database.db_universal` and will share
the same connection pool.
"""

from app.database.db_universal import (
    UniversalDatabase as Database,
    init_db,
    get_connection,
    execute_query,
)

__all__ = ["Database", "init_db", "get_connection", "execute_query"]
