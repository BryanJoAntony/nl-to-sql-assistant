from app.services.sql_validator import SQLValidator


def test_valid_select_query_passes():
    validator = SQLValidator()

    result = validator.validate(
        """
        SELECT first_name, last_name, job_title
        FROM employees
        WHERE hire_date > '2023-01-01'
        """
    )

    assert result.is_safe is True
    assert result.blocked is False
    assert result.final_sql is not None
    assert "LIMIT" in result.final_sql.upper()
    assert "select_only" in result.checks_passed


def test_delete_query_blocked():
    validator = SQLValidator()

    result = validator.validate("DELETE FROM employees WHERE employee_id = 1")

    assert result.is_safe is False
    assert result.blocked is True
    assert "Only SELECT queries are allowed" in result.blocked_reason


def test_update_query_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "UPDATE employees SET salary = 100000 WHERE employee_id = 1"
    )

    assert result.is_safe is False
    assert result.blocked is True


def test_drop_query_blocked():
    validator = SQLValidator()

    result = validator.validate("DROP TABLE employees")

    assert result.is_safe is False
    assert result.blocked is True


def test_multiple_statements_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT first_name FROM employees; SELECT department_name FROM departments;"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "Multiple SQL statements" in result.blocked_reason


def test_sql_comment_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT first_name FROM employees -- get all employees"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "comments" in result.blocked_reason.lower()


def test_unknown_table_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT username FROM users"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "Unknown or disallowed table" in result.blocked_reason


def test_unknown_column_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT password_hash FROM employees"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "Unknown or disallowed column" in result.blocked_reason


def test_select_star_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT * FROM employees"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "SELECT *" in result.blocked_reason


def test_limit_added_when_missing():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT first_name, last_name FROM employees"
    )

    assert result.is_safe is True
    assert result.final_sql.endswith("LIMIT 100")


def test_large_limit_reduced():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT first_name, last_name FROM employees LIMIT 1000"
    )

    assert result.is_safe is True
    assert result.final_sql.endswith("LIMIT 100")


def test_small_limit_kept():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT first_name, last_name FROM employees LIMIT 10"
    )

    assert result.is_safe is True
    assert result.final_sql.endswith("LIMIT 10")


def test_sqlite_master_blocked():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT name FROM sqlite_master"
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "SQLite object" in result.blocked_reason


def test_union_blocked():
    validator = SQLValidator()

    result = validator.validate(
        """
        SELECT first_name FROM employees
        UNION
        SELECT department_name FROM departments
        """
    )

    assert result.is_safe is False
    assert result.blocked is True
    assert "operator" in result.blocked_reason.lower()


def test_allowed_aggregate_query_passes():
    validator = SQLValidator()

    result = validator.validate(
        "SELECT COUNT(employee_id) AS count FROM employees"
    )

    assert result.is_safe is True
    assert result.blocked is False
    assert result.final_sql is not None