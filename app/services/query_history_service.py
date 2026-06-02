from typing import Any

from app.core.logger import app_logger, error_logger
from app.db.connection import get_db_connection


class QueryHistoryService:
    def save_query_history(self, result: dict[str, Any]) -> None:
        try:
            safety = result.get("safety") or {}
            execution = result.get("execution") or {}

            conn = get_db_connection()

            conn.execute(
                """
                INSERT INTO query_history (
                    question,
                    generated_sql,
                    final_sql,
                    explanation,
                    confidence,
                    dry_run,
                    was_blocked,
                    blocked_reason,
                    row_count,
                    execution_time_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.get("question"),
                    result.get("generated_sql"),
                    result.get("final_sql"),
                    result.get("explanation"),
                    result.get("confidence"),
                    1 if result.get("dry_run") else 0,
                    1 if safety.get("blocked") else 0,
                    safety.get("blocked_reason"),
                    execution.get("row_count") if execution else None,
                    execution.get("execution_time_ms") if execution else None,
                ),
            )

            conn.commit()
            conn.close()

            app_logger.info(
                "QUERY_HISTORY_SAVED | blocked=%s | dry_run=%s",
                safety.get("blocked"),
                result.get("dry_run"),
            )

        except Exception:
            error_logger.exception("QUERY_HISTORY_SAVE_FAILED")