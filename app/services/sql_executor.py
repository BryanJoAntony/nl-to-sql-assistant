import sqlite3
import time
from typing import Any

from app.core.exceptions import DatabaseException
from app.core.logger import error_logger, sql_logger
from app.db.connection import get_db_connection


class SQLExecutor:
    def execute(self, sql: str) -> dict[str, Any]:
        start_time = time.time()

        sql_logger.info("SQL_EXECUTION_STARTED | sql=%s", sql)

        conn = get_db_connection()

        try:
            cursor = conn.cursor()

            # Use execute(), never executescript().
            # executescript() can run multiple statements and is unsafe here.
            cursor.execute(sql)

            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description or []]

            result_rows = [dict(row) for row in rows]

            execution_time_ms = round((time.time() - start_time) * 1000, 2)

            sql_logger.info(
                "SQL_EXECUTION_COMPLETED | row_count=%s | columns=%s | duration_ms=%s",
                len(result_rows),
                columns,
                execution_time_ms,
            )

            return {
                "columns": columns,
                "rows": result_rows,
                "row_count": len(result_rows),
                "execution_time_ms": execution_time_ms,
            }

        except sqlite3.Error as exc:
            error_logger.exception("SQL_EXECUTION_FAILED | sql=%s", sql)

            raise DatabaseException(
                message="Failed to execute SQL query",
                details={
                    "database_error": str(exc),
                },
            ) from exc

        finally:
            conn.close()