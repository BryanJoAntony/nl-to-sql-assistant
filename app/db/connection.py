import sqlite3
from sqlite3 import Connection

from app.core.config import settings


def get_db_connection() -> Connection:
    conn = sqlite3.connect(settings.database_full_path)
    conn.row_factory = sqlite3.Row
    return conn