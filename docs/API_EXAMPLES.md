# API Examples

Base URL:

```
http://127.0.0.1:5000
```

## Health Check

### Request

```
GET /health
```

### Response

```
{
  "success": true,
  "service": "Safe NL-to-SQL Analytics Assistant",
  "status": "ok"
}
```

## API Health Check

### Request

```
GET /api/health
```

### Response

```
{
  "success": true,
  "request_id": "uuid",
  "message": "API is healthy",
  "data": {
    "service": "Safe NL-to-SQL Analytics Assistant",
    "version": "1.0.0",
    "environment": "development",
    "status": "ok"
  }
}
```

## Readiness Check

### Request

```
GET /api/ready
```

### Response

```
{
  "success": true,
  "request_id": "uuid",
  "message": "Service readiness checked",
  "data": {
    "service": "Safe NL-to-SQL Analytics Assistant",
    "status": "ready",
    "checks": {
      "database": "ok",
      "openai_api_key": "configured",
      "allowed_schema": "loaded"
    }
  }
}
```

## Query Endpoint: Dry Run

### Request

```
POST /api/query
Content-Type: application/json
```

```
{
  "question": "Show employees in Engineering who joined after 2023",
  "dry_run": true
}
```

### Response

```
{
  "success": true,
  "request_id": "uuid",
  "message": "Query processed successfully",
  "data": {
    "question": "Show employees in Engineering who joined after 2023",
    "generated_sql": "SELECT employees.first_name, employees.last_name, employees.job_title, employees.hire_date FROM employees JOIN departments ON employees.department_id = departments.department_id WHERE departments.department_name = 'Engineering' AND employees.hire_date > '2023-12-31' LIMIT 100",
    "final_sql": "SELECT employees.first_name, employees.last_name, employees.job_title, employees.hire_date FROM employees JOIN departments ON employees.department_id = departments.department_id WHERE departments.department_name = 'Engineering' AND employees.hire_date > '2023-12-31' LIMIT 100",
    "explanation": "This query retrieves Engineering employees who joined after 2023.",
    "confidence": 0.92,
    "dry_run": true,
    "safety": {
      "is_safe": true,
      "blocked": false,
      "blocked_reason": null
    },
    "execution": null
  }
}
```

## Query Endpoint: Execute Query

### Request

```
POST /api/query
Content-Type: application/json
```

```
{
  "question": "Show employees in Engineering who joined after 2023",
  "dry_run": false
}
```

### Response

```
{
  "success": true,
  "request_id": "uuid",
  "message": "Query processed successfully",
  "data": {
    "question": "Show employees in Engineering who joined after 2023",
    "generated_sql": "SELECT employees.first_name, employees.last_name, employees.job_title, employees.hire_date FROM employees JOIN departments ON employees.department_id = departments.department_id WHERE departments.department_name = 'Engineering' AND employees.hire_date > '2023-12-31' LIMIT 100",
    "final_sql": "SELECT employees.first_name, employees.last_name, employees.job_title, employees.hire_date FROM employees JOIN departments ON employees.department_id = departments.department_id WHERE departments.department_name = 'Engineering' AND employees.hire_date > '2023-12-31' LIMIT 100",
    "explanation": "This query retrieves Engineering employees who joined after 2023.",
    "confidence": 0.92,
    "dry_run": false,
    "safety": {
      "is_safe": true,
      "blocked": false
    },
    "execution": {
      "columns": [
        "first_name",
        "last_name",
        "job_title",
        "hire_date"
      ],
      "rows": [
        {
          "first_name": "Meera",
          "last_name": "Nair",
          "job_title": "Data Engineer",
          "hire_date": "2024-01-15"
        },
        {
          "first_name": "Kiran",
          "last_name": "Das",
          "job_title": "Frontend Developer",
          "hire_date": "2024-06-12"
        }
      ],
      "row_count": 2,
      "execution_time_ms": 2.14
    }
  }
}
```

## Blocked Query Example

### Request

```
POST /api/query
Content-Type: application/json
```

```
{
  "question": "Delete all employees",
  "dry_run": true
}
```

### Response

```
{
  "success": false,
  "request_id": "uuid",
  "message": "SQL validation blocked the generated query",
  "error_code": "SQL_VALIDATION_BLOCKED",
  "details": {
    "question": "Delete all employees",
    "generated_sql": "DELETE FROM employees",
    "final_sql": null,
    "explanation": "Attempts to delete employees.",
    "confidence": 0.9,
    "dry_run": true,
    "safety": {
      "is_safe": false,
      "blocked": true,
      "blocked_reason": "Only SELECT queries are allowed"
    },
    "execution": null
  }
}
```

## Optional API Key Auth

If enabled in `.env`:

```
ENABLE_API_KEY_AUTH=True
APP_API_KEY=local-demo-key
```

Then add this header in Postman:

```
X-API-Key: local-demo-key
```