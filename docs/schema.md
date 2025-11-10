# Database Schema

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

## `attrition_predictions`

| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `employee_id` | Integer | Foreign Key (`employees.id`) |
| `prediction_date` | DateTime | |
| `attrition_probability` | Float | |
| `shap_values` | Text | |
