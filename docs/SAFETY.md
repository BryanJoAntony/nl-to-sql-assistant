# Safety Design

## Core Principle

OpenAI suggests SQL.  
The backend decides whether SQL is safe.  
The database only receives validated, limited, read-only SQL.

## Project Scope

This project is an independent portfolio demo built from scratch using synthetic data.

It does not include proprietary code, data, prompts, schemas, workflows, or architecture from any employer or client project.

## Threat Model

The system assumes that generated SQL may be unsafe, incomplete, or incorrect.

Possible risks include:

- Destructive SQL commands
- Data modification queries
- Multiple SQL statements
- SQL comments hiding malicious statements
- Unknown tables
- Unknown columns
- Unrestricted result sets
- Access to internal SQLite metadata
- Unsafe SQL functions or operators

## Safety Pipeline

```
User question
↓
OpenAI SQL generation
↓
Structured JSON parsing
↓
SQL validation
↓
LIMIT enforcement
↓
Safe execution
↓
Response formatting
```

## SQL Validation Rules

The backend blocks destructive or unsafe SQL keywords:

```
DELETE
UPDATE
INSERT
DROP
ALTER
TRUNCATE
CREATE
REPLACE
MERGE
UPSERT
EXEC
EXECUTE
```

The backend also blocks unsafe SQL patterns and objects:

```
Multiple SQL statements
SQL comments
SELECT *
UNION
INTERSECT
EXCEPT
sqlite_master
sqlite_schema
PRAGMA
ATTACH
DETACH
Unknown tables
Unknown columns
Non-allowlisted functions
```

## Allowlisted Tables

Only these synthetic demo tables are allowed:

```
departments
employees
projects
employee_projects
attendance
```

## Row Limit Enforcement

The backend enforces a maximum row limit.

If the generated SQL has no `LIMIT`, the backend adds one.

If the generated SQL has a `LIMIT` greater than the configured maximum, the backend reduces it.

Example:

```
SELECT first_name, last_name FROM employees
```

Becomes:

```
SELECT first_name, last_name FROM employees LIMIT 100
```

## Read-Only Execution

The SQL executor only uses:

```
cursor.execute(sql)
```

It does not use:

```
cursor.executescript(sql)
```

This prevents accidental execution of multiple SQL statements.

## Dry Run Mode

Dry run mode allows generated SQL to be reviewed without execution.

Example request:

```
{
  "question": "Show employees in Engineering",
  "dry_run": true
}
```

In dry run mode, the API returns:

```
Generated SQL
Final validated SQL
Safety status
No execution rows
```

## Logging

The application uses separate log files for:

```
App lifecycle
Incoming requests
API outputs
Errors
SQL generation, validation, and execution
OpenAI metadata
```

The application does not log:

```
OpenAI API keys
Environment file contents
Authorization headers
Full secrets
```

## Known Limitations

This first version is intentionally strict.

It may block some valid advanced SQL patterns such as:

```
Subqueries
UNION
Complex functions
SELECT *
Database-specific syntax
```

This is intentional for a safe first version.

## Future Improvements

Possible future additions:

```
Read-only database user
PostgreSQL support
SQL Server support
Query cost estimation
Rate limiting
Audit dashboard
Role-based access control
Schema introspection
Docker deployment
CI/CD pipeline
```