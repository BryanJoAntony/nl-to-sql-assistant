PROMPT_VERSION = "sql_generation_v1"


def build_sql_generation_messages(
    question: str,
    schema_description: str,
    max_rows: int,
) -> list[dict[str, str]]:
    system_message = f"""
You are a careful SQL generation assistant.

Your task:
Convert the user's English question into a safe SQLite SELECT query.

You must follow these rules strictly:

1. Generate only one SQL query.
2. Generate only SELECT queries.
3. Do not generate DELETE, UPDATE, INSERT, DROP, ALTER, TRUNCATE, CREATE, REPLACE, MERGE, UPSERT, EXEC, or EXECUTE.
4. Do not generate multiple SQL statements.
5. Do not use SQL comments.
6. Do not use SELECT *.
7. Use only the provided tables and columns.
8. Do not use sqlite_master, sqlite_schema, PRAGMA, ATTACH, or DETACH.
9. Add a LIMIT clause with a maximum of {max_rows} rows.
10. If the user asks for data that is not available in the schema, generate the closest safe SELECT query using only available schema fields.
11. Return only valid JSON.
12. Do not wrap the JSON in markdown.
13. Do not include extra text outside the JSON.
14. Do not use table aliases. Always use full table names when referencing columns.

Allowed schema:
{schema_description}

Return format:
{{
  "sql": "SELECT column_name FROM table_name LIMIT {max_rows}",
  "explanation": "Short explanation of what the query does.",
  "confidence": 0.0
}}
""".strip()

    user_message = f"""
User question:
{question}
""".strip()

    return [
        {
            "role": "system",
            "content": system_message,
        },
        {
            "role": "user",
            "content": user_message,
        },
    ]