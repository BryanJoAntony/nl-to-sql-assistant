import re

import sqlparse
from sqlparse.sql import Identifier, IdentifierList
from sqlparse.tokens import DML, Keyword, Name, Wildcard

from app.core.config import settings
from app.core.constants import (
    BLOCKED_SQL_KEYWORDS,
    BLOCKED_SQL_OPERATORS,
    BLOCKED_SQL_PATTERNS,
    BLOCKED_SQLITE_OBJECTS,
    SQL_AGGREGATE_ALIASES,
    SQL_FUNCTION_ALLOWLIST,
)
from app.core.logger import sql_logger
from app.db.schema import ALLOWED_SCHEMA
from app.schemas.sql_schema import SQLValidationResult


class SQLValidator:
    def __init__(self, allowed_schema: dict[str, list[str]] | None = None):
        self.allowed_schema = allowed_schema or ALLOWED_SCHEMA
        self.allowed_tables = set(self.allowed_schema.keys())
        self.allowed_columns = {
            column
            for columns in self.allowed_schema.values()
            for column in columns
        }

    def validate(self, sql: str) -> SQLValidationResult:
        sql_logger.info("SQL_VALIDATION_STARTED | sql=%s", sql)

        checks_passed: list[str] = []
        detected_tables: list[str] = []
        detected_columns: list[str] = []

        normalized_sql = self._normalize_sql(sql)

        if not normalized_sql:
            return self._blocked(sql, "SQL query is empty", checks_passed)

        if self._contains_blocked_comment_patterns(normalized_sql):
            return self._blocked(sql, "SQL comments are not allowed", checks_passed)

        checks_passed.append("no_comments")

        if self._has_multiple_statements(normalized_sql):
            return self._blocked(
                sql,
                "Multiple SQL statements are not allowed",
                checks_passed,
            )

        checks_passed.append("single_statement")

        if not self._is_select_query(normalized_sql):
            return self._blocked(sql, "Only SELECT queries are allowed", checks_passed)

        checks_passed.append("select_only")

        blocked_keyword = self._find_blocked_keyword(normalized_sql)
        if blocked_keyword:
            return self._blocked(
                sql,
                f"Blocked SQL keyword detected: {blocked_keyword}",
                checks_passed,
            )

        checks_passed.append("no_blocked_keywords")

        blocked_operator = self._find_blocked_operator(normalized_sql)
        if blocked_operator:
            return self._blocked(
                sql,
                f"Blocked SQL operator detected: {blocked_operator}",
                checks_passed,
            )

        checks_passed.append("no_blocked_operators")

        blocked_object = self._find_blocked_sqlite_object(normalized_sql)
        if blocked_object:
            return self._blocked(
                sql,
                f"Blocked SQLite object detected: {blocked_object}",
                checks_passed,
            )

        checks_passed.append("no_blocked_sqlite_objects")

        if self._contains_select_star(normalized_sql):
            return self._blocked(sql, "SELECT * is not allowed", checks_passed)

        checks_passed.append("no_select_star")

        detected_tables = self._extract_tables(normalized_sql)

        unknown_tables = [
            table for table in detected_tables
            if table not in self.allowed_tables
        ]

        if unknown_tables:
            return self._blocked(
                sql,
                f"Unknown or disallowed table detected: {unknown_tables[0]}",
                checks_passed,
                detected_tables=detected_tables,
            )

        checks_passed.append("allowlisted_tables")

        detected_columns = self._extract_columns(normalized_sql)

        unknown_columns = [
            column
            for column in detected_columns
            if column not in self.allowed_columns
            and column.lower() not in SQL_AGGREGATE_ALIASES
        ]

        if unknown_columns:
            return self._blocked(
                sql,
                f"Unknown or disallowed column detected: {unknown_columns[0]}",
                checks_passed,
                detected_tables=detected_tables,
                detected_columns=detected_columns,
            )

        checks_passed.append("allowlisted_columns")

        disallowed_function = self._find_disallowed_function(normalized_sql)

        if disallowed_function:
            return self._blocked(
                sql,
                f"Disallowed SQL function detected: {disallowed_function}",
                checks_passed,
                detected_tables=detected_tables,
                detected_columns=detected_columns,
            )

        checks_passed.append("allowlisted_functions")

        final_sql = self._enforce_limit(normalized_sql)
        checks_passed.append("limit_enforced")

        sql_logger.info(
            "SQL_VALIDATION_PASSED | final_sql=%s | tables=%s | columns=%s",
            final_sql,
            detected_tables,
            detected_columns,
        )

        return SQLValidationResult(
            is_safe=True,
            blocked=False,
            original_sql=sql,
            final_sql=final_sql,
            blocked_reason=None,
            checks_passed=checks_passed,
            detected_tables=detected_tables,
            detected_columns=detected_columns,
        )

    def _blocked(
        self,
        sql: str,
        reason: str,
        checks_passed: list[str],
        detected_tables: list[str] | None = None,
        detected_columns: list[str] | None = None,
    ) -> SQLValidationResult:
        sql_logger.warning(
            "SQL_VALIDATION_BLOCKED | reason=%s | sql=%s",
            reason,
            sql,
        )

        return SQLValidationResult(
            is_safe=False,
            blocked=True,
            original_sql=sql,
            final_sql=None,
            blocked_reason=reason,
            checks_passed=checks_passed,
            detected_tables=detected_tables or [],
            detected_columns=detected_columns or [],
        )

    def _normalize_sql(self, sql: str) -> str:
        cleaned_sql = sql.strip()

        if cleaned_sql.endswith(";"):
            cleaned_sql = cleaned_sql[:-1].strip()

        return cleaned_sql

    def _contains_blocked_comment_patterns(self, sql: str) -> bool:
        return any(pattern in sql for pattern in BLOCKED_SQL_PATTERNS)

    def _has_multiple_statements(self, sql: str) -> bool:
        statements = [
            statement
            for statement in sqlparse.parse(sql)
            if str(statement).strip()
        ]

        return len(statements) != 1

    def _is_select_query(self, sql: str) -> bool:
        parsed = sqlparse.parse(sql)

        if not parsed:
            return False

        statement = parsed[0]

        for token in statement.tokens:
            if token.ttype in (DML, Keyword):
                return token.value.upper() == "SELECT"

            if not token.is_whitespace:
                return token.value.upper() == "SELECT"

        return False

    def _find_blocked_keyword(self, sql: str) -> str | None:
        upper_sql = sql.upper()

        for keyword in BLOCKED_SQL_KEYWORDS:
            pattern = rf"\b{re.escape(keyword)}\b"

            if re.search(pattern, upper_sql):
                return keyword

        return None

    def _find_blocked_operator(self, sql: str) -> str | None:
        upper_sql = sql.upper()

        for operator in BLOCKED_SQL_OPERATORS:
            pattern = rf"\b{re.escape(operator)}\b"

            if re.search(pattern, upper_sql):
                return operator

        return None

    def _find_blocked_sqlite_object(self, sql: str) -> str | None:
        lower_sql = sql.lower()

        for blocked_object in BLOCKED_SQLITE_OBJECTS:
            pattern = rf"\b{re.escape(blocked_object)}\b"

            if re.search(pattern, lower_sql):
                return blocked_object

        return None

    def _contains_select_star(self, sql: str) -> bool:
        parsed = sqlparse.parse(sql)

        if not parsed:
            return False

        for token in parsed[0].flatten():
            if token.ttype is Wildcard and token.value == "*":
                return True

        return False

    def _extract_tables(self, sql: str) -> list[str]:
        tables: list[str] = []
        parsed = sqlparse.parse(sql)

        if not parsed:
            return tables

        statement = parsed[0]
        from_seen = False
        join_seen = False

        for token in statement.tokens:
            token_upper = token.value.upper()

            if token.is_whitespace:
                continue

            if token_upper == "FROM":
                from_seen = True
                continue

            if token_upper.endswith("JOIN") or token_upper == "JOIN":
                join_seen = True
                continue

            if from_seen or join_seen:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        table_name = identifier.get_real_name()
                        if table_name:
                            tables.append(table_name)

                elif isinstance(token, Identifier):
                    table_name = token.get_real_name()
                    if table_name:
                        tables.append(table_name)

                elif token.ttype is Name:
                    tables.append(token.value)

                from_seen = False
                join_seen = False

        return list(dict.fromkeys(tables))

    def _extract_columns(self, sql: str) -> list[str]:
        columns: list[str] = []
        parsed = sqlparse.parse(sql)

        if not parsed:
            return columns

        statement = parsed[0]

        sql_keywords = {
            "SELECT",
            "FROM",
            "WHERE",
            "JOIN",
            "INNER",
            "LEFT",
            "RIGHT",
            "ON",
            "AND",
            "OR",
            "GROUP",
            "BY",
            "ORDER",
            "LIMIT",
            "ASC",
            "DESC",
            "AS",
            "HAVING",
        }

        for token in statement.flatten():
            value = token.value

            if token.is_whitespace:
                continue

            if token.ttype not in (Name,):
                continue

            lower_value = value.lower()
            upper_value = value.upper()

            if lower_value in self.allowed_tables:
                continue

            if upper_value in SQL_FUNCTION_ALLOWLIST:
                continue

            if upper_value in sql_keywords:
                continue

            if value.isnumeric():
                continue

            columns.append(value)

        return list(dict.fromkeys(columns))

    def _find_disallowed_function(self, sql: str) -> str | None:
        function_pattern = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\("
        functions = re.findall(function_pattern, sql)

        for function_name in functions:
            upper_function_name = function_name.upper()

            if upper_function_name not in SQL_FUNCTION_ALLOWLIST:
                return function_name

        return None

    def _enforce_limit(self, sql: str) -> str:
        max_rows = settings.MAX_QUERY_ROWS

        limit_pattern = r"\bLIMIT\s+(\d+)\b"
        limit_match = re.search(limit_pattern, sql, flags=re.IGNORECASE)

        if not limit_match:
            return f"{sql} LIMIT {max_rows}"

        current_limit = int(limit_match.group(1))

        if current_limit <= max_rows:
            return sql

        return re.sub(
            limit_pattern,
            f"LIMIT {max_rows}",
            sql,
            flags=re.IGNORECASE,
        )