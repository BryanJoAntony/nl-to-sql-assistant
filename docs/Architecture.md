# Architecture

## Overview

Safe NL-to-SQL Analytics Assistant is a Flask backend application that converts natural language questions into safe SQL queries for a synthetic analytics database.

The application is designed around one core principle:

```
OpenAI suggests SQL.
The backend decides whether SQL is safe.
The database only receives validated, limited, read-only SQL.
```

This project is built as an independent public portfolio demo using synthetic data only.

It does not include proprietary code, data, prompts, schemas, workflows, or architecture from any employer or client project.

## High-Level Flow

```
User
↓
POST /api/query
↓
Flask Controller
↓
Request Validation
↓
NL-to-SQL Service
↓
OpenAI SQL Generation
↓
Structured JSON Parsing
↓
SQL Validator
↓
LIMIT Enforcement
↓
SQL Executor
↓
SQLite Database
↓
Response Formatter
↓
API Response
```

## Request Pipeline

When a user sends a request to `/api/query`, the system follows this pipeline:

```
1. Receive JSON request
2. Validate request body with Pydantic
3. Send user question and allowed schema to OpenAI
4. Receive structured JSON from OpenAI
5. Extract generated SQL, explanation, and confidence
6. Validate the generated SQL
7. Block unsafe SQL if validation fails
8. Enforce maximum row limit
9. Execute safe SQL using SQLite
10. Save query history for auditability
11. Return SQL, rows, explanation, confidence, and safety status
```

## Main Components

## API Layer

Location:

```
app/api/
```

Responsibilities:

```
Define API endpoints
Accept HTTP requests
Validate request payloads
Call service layer
Return standard JSON responses
```

Main files:

```
query_controller.py
health_controller.py
history_controller.py
info_controller.py
routes.py
```

Important endpoints:

```
GET  /health
GET  /api/health
GET  /api/ready
GET  /api/info
GET  /api/query-history
POST /api/query
```

## Core Layer

Location:

```
app/core/
```

Responsibilities:

```
Application configuration
Logging setup
Error handling
Startup checks
Request ID tracking
Rate limiter setup
Optional API key security
Optional mutex handling
Service container setup
```

Main files:

```
config.py
logger.py
error_handlers.py
exceptions.py
request_logging.py
rate_limiter.py
security.py
startup.py
mutex.py
service_container.py
constants.py
```

## Database Layer

Location:

```
app/db/
```

Responsibilities:

```
Create SQLite connection
Define synthetic database schema
Seed demo data
Initialize database on startup
Expose allowed schema for SQL validation and prompt construction
```

Main files:

```
connection.py
schema.py
seed_data.py
init_db.py
```

The application uses SQLite for local portability and easy setup.

The database layer is separated so another database backend such as PostgreSQL or SQL Server can be added later.

## Services Layer

Location:

```
app/services/
```

Responsibilities:

```
Generate SQL using OpenAI
Validate generated SQL
Execute safe SQL
Coordinate the full NL-to-SQL pipeline
Save query history
```

Main files:

```
openai_service.py
sql_validator.py
sql_executor.py
nl_to_sql_service.py
query_history_service.py
```

## Prompt Layer

Location:

```
app/prompts/
```

Responsibilities:

```
Build OpenAI prompt messages
Store prompt version
Provide allowed schema context to the model
Instruct model to return structured JSON
```

Main file:

```
sql_generation_prompt.py
```

The prompt is versioned using:

```
PROMPT_VERSION = "sql_generation_v1"
```

## Schema Layer

Location:

```
app/schemas/
```

Responsibilities:

```
Validate API request bodies
Validate OpenAI response format
Represent SQL validation results
```

Main files:

```
request_schema.py
openai_schema.py
sql_schema.py
response_schema.py
```

## Utils Layer

Location:

```
app/utils/
```

Responsibilities:

```
Build standard success responses
Build standard error responses
Attach request IDs to responses
```

Main file:

```
response_utils.py
```

## SQL Safety Architecture

The system does not trust generated SQL.

OpenAI-generated SQL must pass through the backend validator before execution.

The validator checks:

```
Only SELECT queries are allowed
Destructive SQL keywords are blocked
Multiple statements are blocked
SQL comments are blocked
SELECT * is blocked
Unknown tables are blocked
Unknown columns are blocked
SQLite internal objects are blocked
Unsafe SQL operators are blocked
Non-allowlisted functions are blocked
LIMIT is enforced
```

Blocked keywords include:

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

Blocked SQLite/internal objects include:

```
sqlite_master
sqlite_schema
PRAGMA
ATTACH
DETACH
```

## Allowed User Query Schema

Only these synthetic analytics tables are exposed to OpenAI and the SQL validator:

```
departments
employees
projects
employee_projects
attendance
```

The internal audit table is not exposed to OpenAI.

Internal table:

```
query_history
```

The `query_history` table is used only by controlled backend code.

It is not included in:

```
ALLOWED_SCHEMA
SCHEMA_DESCRIPTION
```

This prevents users from asking the model to query internal audit data.

## Query History and Audit Logging

The application stores query audit records in the `query_history` table.

Stored fields include:

```
question
generated_sql
final_sql
explanation
confidence
dry_run
was_blocked
blocked_reason
row_count
execution_time_ms
created_on
```

This supports traceability and review.

The audit endpoint is:

```
GET /api/query-history
```

## Logging Architecture

The application uses multiple log files by purpose:

```
logs/app.log
logs/requests.log
logs/outputs.log
logs/errors.log
logs/sql.log
logs/openai.log
```

Log purpose:

```
app.log       - startup, shutdown, app lifecycle
requests.log  - incoming HTTP requests
outputs.log   - completed responses and pipeline results
errors.log    - exceptions and failed operations
sql.log       - SQL generation, validation, and execution metadata
openai.log    - OpenAI request metadata and token usage
```

The application avoids logging secrets such as:

```
OPENAI_API_KEY
.env contents
Authorization headers
API keys
```

## Request ID Tracking

Every request receives a unique request ID.

The request ID is included in:

```
API responses
response headers
request logs
output logs
error logs
```

This makes debugging easier across logs.

Example response field:

```
{
  "request_id": "uuid"
}
```

Example response header:

```
X-Request-ID: uuid
```

## Rate Limiting

The application uses Flask-Limiter for production-style rate limiting.

Supported backends:

```
memory://
redis://
```

Local development can use:

```
RATE_LIMIT_STORAGE_URI=memory://
```

Docker/production can use Redis:

```
RATE_LIMIT_STORAGE_URI=redis://redis:6379/0
```

The `/api/query` endpoint has a stricter limit than general endpoints.

Health and info endpoints are exempt from rate limiting:

```
GET /health
GET /api/health
GET /api/ready
GET /api/info
```

## API Key Authentication

The application supports optional API key authentication.

Environment variables:

```
ENABLE_API_KEY_AUTH=False
APP_API_KEY=local-demo-key
```

When enabled, protected routes require:

```
X-API-Key: local-demo-key
```

## Startup Checks

Startup checks are handled in:

```
app/core/startup.py
```

Startup flow:

```
1. Enforce mutex if enabled
2. Create required folders
3. Validate configuration values
4. Warn if OpenAI key is missing
5. Initialize SQLite database
6. Run postflight database checks
```

## Mutex Behavior

The project includes an optional file-based mutex.

The mutex is intended only for local single-process execution.

It should remain disabled in Docker.

Recommended local setting:

```
ENABLE_MUTEX=False
```

Recommended Docker setting:

```
ENABLE_MUTEX=False
```

Reason:

```
Docker and container orchestration should manage process lifecycle and scaling.
A file-based mutex can interfere with containers, replicas, and crash recovery.
```

## Docker Architecture

Docker Compose runs two services:

```
app
redis
```

The app container runs the Flask backend with Waitress.

Redis is used for rate limiting.

Docker Compose overrides the Redis URI:

```
RATE_LIMIT_STORAGE_URI=redis://redis:6379/0
```

Docker volumes persist:

```
data/
logs/
```

## Production Server

Local development can use:

```
python run.py
```

Production-style Windows/local execution can use Waitress:

```
python serve.py
```

Docker also uses Waitress through:

```
CMD ["python", "serve.py"]
```

## Testing Architecture

Tests are stored in:

```
tests/
```

Test coverage includes:

```
health endpoints
info endpoint
query endpoint behavior
SQL validator
SQL executor
query history
rate limiting behavior
```

OpenAI calls are mocked in API tests where needed.

The CI workflow uses a dummy OpenAI key and disables external services where appropriate.

## CI/CD

GitHub Actions workflow:

```
.github/workflows/ci.yml
```

The workflow runs:

```
dependency installation
pytest test suite
```

The CI environment does not use real secrets.

## Design Decisions

## Why SQLite?

SQLite is used because:

```
It is easy to run locally
It requires no database server setup
It is suitable for synthetic demo data
It makes testing simple
It keeps focus on SQL safety rather than database administration
```

The database layer is separated so production database support can be added later.

## Why Strict SQL Validation?

The validator is intentionally strict because generated SQL should not be trusted.

It is better to block some valid advanced SQL than to allow unsafe SQL in a public demo.

## Why Redis for Rate Limiting?

Redis is preferred for production-style rate limiting because it supports shared state across multiple workers and containers.

The memory backend is kept only as a local development option.

## Why Query History?

Query history improves auditability.

It allows reviewers to inspect:

```
what the user asked
what SQL was generated
whether the query was blocked
what final SQL was executed
how many rows were returned
```

## Current Limitations

The first version intentionally blocks or avoids:

```
subqueries
UNION
SELECT *
complex functions
database-specific SQL syntax
direct user-provided SQL execution
```

## Future Improvements

Possible future improvements:

```
PostgreSQL executor
SQL Server executor
read-only database user
schema introspection
query cost estimation
role-based access control
audit dashboard
OpenAPI specification
Docker health checks
Kubernetes deployment
frontend dashboard
CI coverage reports
```
