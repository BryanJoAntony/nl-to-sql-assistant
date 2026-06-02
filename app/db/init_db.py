from app.core.logger import app_logger
from app.db.connection import get_db_connection
from app.db.schema import CREATE_TABLES_SQL
from app.db.seed_data import SEED_SQL


def setup_database() -> None:
    app_logger.info("Setting up SQLite database")

    conn = get_db_connection()

    try:
        conn.executescript(CREATE_TABLES_SQL)
        conn.executescript(SEED_SQL)
        conn.commit()
        app_logger.info("Database setup completed successfully")
    except Exception:
        app_logger.exception("Database setup failed")
        raise
    finally:
        conn.close()