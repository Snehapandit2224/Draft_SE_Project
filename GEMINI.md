# HR Attrition Analysis System

This project is a Flask-based web application for analyzing employee attrition.

## Tech Stack

*   **Backend:** Flask, Python
*   **Database:** MySQL
*   **Frontend:** Bootstrap
*   **Libraries:** SQLAlchemy, Alembic, pandas, scikit-learn, shap, matplotlib

## Directory Layout

```
/
|-- app/
|   |-- __init__.py
|   |-- models.py
|   |-- main.py
|   |-- analytics/
|   |-- employees/
|   |-- exit_management/
|   |-- ml_models/
|   |-- static/
|   |-- templates/
|-- docs/
|   |-- schema.md
|   |-- prompt-guidelines.md
|-- migrations/
|-- tests/
|-- config.py
|-- requirements.txt
|-- run.py
|-- .flaskenv
|-- GEMINI.md
```

## API Endpoints

*   `POST /api/employees`: Create a new employee.
*   `GET /api/employees/<id>`: Get a single employee by ID.
*   `GET /api/employees`: Get a list of employees with filters (department, position, status) and pagination.
*   `PUT /api/employees/<id>`: Update an existing employee.
*   `GET /api/employees/<id>/history`: Get the status history of an employee.
*   `POST /api/exit-feedback`: Submit new exit feedback.
*   `PATCH /api/exit-feedback/<id>/complete`: Mark an exit interview as completed.
*   `GET /api/exit-feedback/pending`: Get a list of pending exit interviews.
*   `GET /api/reports/exit-reasons`: Get aggregated exit reasons (counts, percentages) with date and department filters.
*   `GET /api/reports/exit-reasons/export`: Export aggregated exit reasons as CSV.
*   `GET /api/reports/attrition`: Get attrition rates by department, role, and time with pagination.
*   `GET /api/analytics/hotspots`: Identify attrition hotspots using 3-month rolling averages.
*   `GET /api/alerts`: Get a list of all attrition alerts.

## Key Jira Story Mappings

*   **HR-1:** Set up project structure
*   **HR-2:** Implement employee management module
*   **HR-3:** Develop exit feedback functionality
*   **HR-4:** Create analytics dashboard
*   **HR-5:** Integrate machine learning model for attrition prediction
*   **HR-6:** Implement employee history tracking

## Background Jobs

*   Daily job to check for attrition hotspots and create alerts.

## Prompt Usage Guidelines

@./docs/prompt-guidelines.md

### Database Schema

## `employees`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `first_name` | String(64) | |
| `last_name` | String(64) | |
| `email` | String(120) | Unique, Index |
| `department` | String(64) | |
| `position` | String(64) | |
| `hire_date` | Date | |
| `is_active` | Boolean | Default: True |
| `status` | String(64) | Default: 'active' |

## `employee_history`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `employee_id` | Integer | Foreign Key (`employees.id`) |
| `old_status` | String(64) | |
| `new_status` | String(64) | |
| `changed_by` | String(64) | |
| `changed_at` | DateTime | |

## `exit_feedback`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `employee_id` | Integer | Foreign Key (`employees.id`) |
| `exit_date` | Date | |
| `reason` | Text | |
| `feedback` | Text | |
| `interview_completed` | Boolean | Default: False |
| `interview_date` | DateTime | |

## `attrition_predictions`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `employee_id` | Integer | Foreign Key (`employees.id`) |
| `prediction_date` | DateTime | |
| `attrition_probability` | Float | |
| `shap_values` | Text | |

## `attrition_alerts`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `alert_type` | String(64) | |
| `group_name` | String(64) | |
| `value` | Float | |
| `created_at` | DateTime | |
