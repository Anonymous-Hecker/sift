import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    extension TEXT,
    size_bytes INTEGER NOT NULL,
    modified_at REAL NOT NULL,
    accessed_at REAL NOT NULL,
    scanned_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_files_size ON files (size_bytes);
"""


def connect(db_path=None):
    """Open the database. If no path is provided, it will use the default path in the .sift folder."""
    if db_path is None:
        config.ensure_app_dir()
        db_path = config.DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Lets us access columns by name instead of index
    return conn


def init_db(conn):
    """Create the tables if they don't exist yet."""
    conn.executescript(SCHEMA)
    conn.commit()