CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department_id INTEGER NOT NULL,
    job_title TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    salary INTEGER NOT NULL,
    employment_status TEXT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    department_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    project_status TEXT NOT NULL,
    budget INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS employee_projects (
    employee_project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    role_on_project TEXT NOT NULL,
    assigned_date TEXT NOT NULL,
    allocation_percent INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,
    hours_worked REAL NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS query_history (
    query_history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    generated_sql TEXT,
    final_sql TEXT,
    explanation TEXT,
    confidence REAL,
    dry_run INTEGER NOT NULL,
    was_blocked INTEGER NOT NULL,
    blocked_reason TEXT,
    row_count INTEGER,
    execution_time_ms REAL,
    created_on TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


ALLOWED_SCHEMA = {
    "departments": [
        "department_id",
        "department_name",
        "location",
    ],
    "employees": [
        "employee_id",
        "first_name",
        "last_name",
        "email",
        "department_id",
        "job_title",
        "hire_date",
        "salary",
        "employment_status",
    ],
    "projects": [
        "project_id",
        "project_name",
        "department_id",
        "start_date",
        "end_date",
        "project_status",
        "budget",
    ],
    "employee_projects": [
        "employee_project_id",
        "employee_id",
        "project_id",
        "role_on_project",
        "assigned_date",
        "allocation_percent",
    ],
    "attendance": [
        "attendance_id",
        "employee_id",
        "attendance_date",
        "status",
        "hours_worked",
    ],
}


SCHEMA_DESCRIPTION = """
Allowed database schema:

Table: departments
Columns:
- department_id
- department_name
- location

Table: employees
Columns:
- employee_id
- first_name
- last_name
- email
- department_id
- job_title
- hire_date
- salary
- employment_status

Table: projects
Columns:
- project_id
- project_name
- department_id
- start_date
- end_date
- project_status
- budget

Table: employee_projects
Columns:
- employee_project_id
- employee_id
- project_id
- role_on_project
- assigned_date
- allocation_percent

Table: attendance
Columns:
- attendance_id
- employee_id
- attendance_date
- status
- hours_worked
"""