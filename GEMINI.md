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
*   `PUT /api/employees/<id>`: Update an existing employee.
*   `GET /api/employees/<id>/history`: Get the status history of an employee.

## Key Jira Story Mappings

*   **HR-1:** Set up project structure
*   **HR-2:** Implement employee management module
*   **HR-3:** Develop exit feedback functionality
*   **HR-4:** Create analytics dashboard
*   **HR-5:** Integrate machine learning model for attrition prediction
*   **HR-6:** Implement employee history tracking

## Prompt Usage Guidelines

@./docs/prompt-guidelines.md

### Database Schema

@./docs/schema.md
