SEED_SQL = """
INSERT OR IGNORE INTO departments (department_id, department_name, location)
VALUES
    (1, 'Engineering', 'Bangalore'),
    (2, 'Human Resources', 'Chennai'),
    (3, 'Finance', 'Mumbai'),
    (4, 'Sales', 'Delhi'),
    (5, 'Operations', 'Hyderabad');

INSERT OR IGNORE INTO employees (
    employee_id,
    first_name,
    last_name,
    email,
    department_id,
    job_title,
    hire_date,
    salary,
    employment_status
)
VALUES
    (1, 'Aarav', 'Menon', 'aarav.menon@example.com', 1, 'Backend Developer', '2023-02-10', 85000, 'Active'),
    (2, 'Meera', 'Nair', 'meera.nair@example.com', 1, 'Data Engineer', '2024-01-15', 92000, 'Active'),
    (3, 'Rohan', 'Sharma', 'rohan.sharma@example.com', 2, 'HR Executive', '2022-08-01', 55000, 'Active'),
    (4, 'Ananya', 'Iyer', 'ananya.iyer@example.com', 3, 'Financial Analyst', '2021-05-20', 78000, 'Active'),
    (5, 'Vikram', 'Rao', 'vikram.rao@example.com', 4, 'Sales Manager', '2023-11-05', 88000, 'Active'),
    (6, 'Neha', 'Thomas', 'neha.thomas@example.com', 5, 'Operations Lead', '2020-03-18', 81000, 'Inactive'),
    (7, 'Kiran', 'Das', 'kiran.das@example.com', 1, 'Frontend Developer', '2024-06-12', 76000, 'Active'),
    (8, 'Priya', 'Kapoor', 'priya.kapoor@example.com', 3, 'Accountant', '2023-07-22', 62000, 'Active');

INSERT OR IGNORE INTO projects (
    project_id,
    project_name,
    department_id,
    start_date,
    end_date,
    project_status,
    budget
)
VALUES
    (1, 'Internal Analytics Platform', 1, '2024-01-01', NULL, 'Active', 500000),
    (2, 'Employee Engagement Survey', 2, '2024-02-01', '2024-05-30', 'Completed', 80000),
    (3, 'Quarterly Budget Automation', 3, '2023-09-01', NULL, 'Active', 200000),
    (4, 'Sales CRM Cleanup', 4, '2024-03-15', NULL, 'Active', 120000),
    (5, 'Operations Workflow Review', 5, '2023-06-01', '2023-12-15', 'Completed', 150000);

INSERT OR IGNORE INTO employee_projects (
    employee_project_id,
    employee_id,
    project_id,
    role_on_project,
    assigned_date,
    allocation_percent
)
VALUES
    (1, 1, 1, 'API Developer', '2024-01-10', 80),
    (2, 2, 1, 'Data Pipeline Owner', '2024-01-12', 90),
    (3, 3, 2, 'HR Coordinator', '2024-02-05', 60),
    (4, 4, 3, 'Finance SME', '2023-09-10', 70),
    (5, 5, 4, 'Sales Owner', '2024-03-20', 50),
    (6, 6, 5, 'Operations Reviewer', '2023-06-05', 40),
    (7, 7, 1, 'UI Developer', '2024-06-20', 75),
    (8, 8, 3, 'Accounting Support', '2023-10-01', 50);

INSERT OR IGNORE INTO attendance (
    attendance_id,
    employee_id,
    attendance_date,
    status,
    hours_worked
)
VALUES
    (1, 1, '2024-07-01', 'Present', 8),
    (2, 2, '2024-07-01', 'Present', 8.5),
    (3, 3, '2024-07-01', 'Leave', 0),
    (4, 4, '2024-07-01', 'Present', 7.5),
    (5, 5, '2024-07-01', 'Present', 8),
    (6, 7, '2024-07-01', 'Present', 8),
    (7, 8, '2024-07-01', 'Half Day', 4),
    (8, 1, '2024-07-02', 'Present', 8),
    (9, 2, '2024-07-02', 'Leave', 0),
    (10, 4, '2024-07-02', 'Present', 8);
"""