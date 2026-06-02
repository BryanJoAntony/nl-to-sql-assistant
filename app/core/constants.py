BLOCKED_SQL_KEYWORDS = {
    "DELETE",
    "UPDATE",
    "INSERT",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "MERGE",
    "UPSERT",
    "EXEC",
    "EXECUTE",
}

BLOCKED_SQL_PATTERNS = {
    "--",
    "/*",
    "*/",
}

BLOCKED_SQLITE_OBJECTS = {
    "sqlite_master",
    "sqlite_schema",
    "pragma",
    "attach",
    "detach",
}

BLOCKED_SQL_OPERATORS = {
    "UNION",
    "INTERSECT",
    "EXCEPT",
}

SQL_FUNCTION_ALLOWLIST = {
    "COUNT",
    "AVG",
    "SUM",
    "MIN",
    "MAX",
    "ROUND",
}

SQL_AGGREGATE_ALIASES = {
    "count",
    "avg",
    "sum",
    "min",
    "max",
    "total",
    "average",
}

DEFAULT_HEALTH_STATUS = "ok"
DEFAULT_READY_STATUS = "ready"