from app.db.connection import get_db_connection
from app.db.init_db import setup_database
from app.services.query_history_service import QueryHistoryService


def test_query_history_saves_successful_execution():
    setup_database()

    service = QueryHistoryService()

    result = {
        "question": "Show employees in Engineering",
        "generated_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "final_sql": "SELECT first_name, last_name FROM employees LIMIT 100",
        "explanation": "Shows employee names.",
        "confidence": 0.95,
        "dry_run": False,
        "safety": {
            "blocked": False,
            "blocked_reason": None,
        },
        "execution": {
            "row_count": 2,
            "execution_time_ms": 3.5,
        },
    }

    service.save_query_history(result)

    conn = get_db_connection()

    row = conn.execute(
        """
        SELECT
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
        FROM query_history
        ORDER BY query_history_id DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    assert row is not None
    assert row["question"] == "Show employees in Engineering"
    assert row["generated_sql"] == "SELECT first_name, last_name FROM employees LIMIT 100"
    assert row["final_sql"] == "SELECT first_name, last_name FROM employees LIMIT 100"
    assert row["explanation"] == "Shows employee names."
    assert row["confidence"] == 0.95
    assert row["dry_run"] == 0
    assert row["was_blocked"] == 0
    assert row["blocked_reason"] is None
    assert row["row_count"] == 2
    assert row["execution_time_ms"] == 3.5


def test_query_history_saves_blocked_query():
    setup_database()

    service = QueryHistoryService()

    result = {
        "question": "Delete all employees",
        "generated_sql": "DELETE FROM employees",
        "final_sql": None,
        "explanation": "Attempts to delete employees.",
        "confidence": 0.9,
        "dry_run": True,
        "safety": {
            "blocked": True,
            "blocked_reason": "Only SELECT queries are allowed",
        },
        "execution": None,
    }

    service.save_query_history(result)

    conn = get_db_connection()

    row = conn.execute(
        """
        SELECT
            question,
            generated_sql,
            final_sql,
            dry_run,
            was_blocked,
            blocked_reason,
            row_count,
            execution_time_ms
        FROM query_history
        ORDER BY query_history_id DESC
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    assert row is not None
    assert row["question"] == "Delete all employees"
    assert row["generated_sql"] == "DELETE FROM employees"
    assert row["final_sql"] is None
    assert row["dry_run"] == 1
    assert row["was_blocked"] == 1
    assert row["blocked_reason"] == "Only SELECT queries are allowed"
    assert row["row_count"] is None
    assert row["execution_time_ms"] is None