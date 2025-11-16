from flask import render_template, jsonify
from app.ml_models import ml_models
from app.utils.decorators import login_required

@ml_models.route('/')
@login_required
def index():
    return render_template('ml_models/index.html')

@ml_models.route('/risk-factors/<int:emp_id>')
@login_required
def risk_factors_ui(emp_id):
    # This route will render a UI page to display risk factors for a given employee.
    # The actual data fetching will be done via an API call from the frontend.
    return render_template('ml_models/risk_factors.html', employee_id=emp_id)

@ml_models.route('/dashboard')
@login_required
def ml_dashboard():
    return render_template('ml_models/dashboard.html')