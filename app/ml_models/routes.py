from flask import render_template, jsonify
from app.ml_models import ml_models

@ml_models.route('/risk-factors/<int:emp_id>')
def risk_factors_ui(emp_id):
    # This route will render a UI page to display risk factors for a given employee.
    # The actual data fetching will be done via an API call from the frontend.
    return render_template('ml_models/risk_factors.html', employee_id=emp_id)

@ml_models.route('/dashboard')
def ml_dashboard():
    return render_template('ml_models/dashboard.html')