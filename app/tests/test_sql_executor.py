from app.db.init_db import setup_database
from app.services.sql_executor import SQLExecutor


def test_sql_executor_returns_rows():
    setup_database()

    executor = SQLExecutor()

    result = executor.execute(
        """
        SELECT first_name, last_name, job_title
        FROM employees
        WHERE department_id = 1
        LIMIT 10
        """
    )

    assert "columns" in result
    assert "rows" in result
    assert "row_count" in result
    assert "execution_time_ms" in result

    assert result["row_count"] >= 1
    assert "first_name" in result["columns"]
    assert "last_name" in result["columns"]
    assert "job_title" in result["columns"]


def test_sql_executor_returns_empty_result_for_no_match():
    setup_database()

    executor = SQLExecutor()

    result = executor.execute(
        """
        SELECT first_name, last_name
        FROM employees
        WHERE first_name = 'DefinitelyNotARealName'
        LIMIT 10
        """
    )

    assert result["row_count"] == 0
    assert result["rows"] == []
    assert "first_name" in result["columns"]
    assert "last_name" in result["columns"]


def test_sql_executor_returns_aggregate_result():
    setup_database()

    executor = SQLExecutor()

    result = executor.execute(
        """
        SELECT COUNT(employee_id) AS count
        FROM employees
        LIMIT 10
        """
    )

    assert result["row_count"] == 1
    assert "count" in result["columns"]
    assert result["rows"][0]["count"] >= 1