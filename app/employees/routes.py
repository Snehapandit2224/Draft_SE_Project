from flask import render_template, request, url_for, redirect, flash
from flask_jwt_extended import current_user
from . import employees
from ..models import Employee, AttritionPrediction
from ..utils.decorators import login_required

@employees.route('/employees')
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/employees.html', employees=employees, current_user=current_user)

@employees.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        # This part will be handled by the API endpoint via JavaScript fetch
        pass
    return render_template('employees/add_employee.html', current_user=current_user)

@employees.route('/employees/<int:id>')
@login_required
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    attrition_prediction = AttritionPrediction.query.filter_by(employee_id=employee.id).order_by(AttritionPrediction.prediction_date.desc()).first()
    print(f"Employee ID: {employee.id}, Attrition Prediction: {attrition_prediction.attrition_probability if attrition_prediction else 'None'}")
    return render_template('employees/employee.html', employee=employee, attrition_prediction=attrition_prediction, current_user=current_user)

@employees.route('/employees/me/attrition-risk')
@login_required
def my_attrition_risk():
    if current_user.role != 'employee':
        flash('Access denied. Only employees can view their attrition risk.', 'danger')
        return redirect(url_for('main.index'))
    
    # Logic to fetch attrition risk for the current employee
    # This will involve querying the AttritionPrediction model
    # For now, we'll just render a placeholder template
    
    # Find the employee associated with the current user
    found_employee = None
    all_employees = Employee.query.all()
    for emp in all_employees:
        expected_username = f"{emp.first_name.lower()}{emp.last_name.lower()}"
        if current_user.username.startswith(expected_username):
            found_employee = emp
            break

    if found_employee:
        print(f"--- Attrition Risk Page: User '{current_user.username}' mapped to Employee ID: {found_employee.id} ---")
        return render_template('employees/attrition_risk.html', employee=found_employee, current_user=current_user)
    else:
        print(f"--- Attrition Risk Page: Employee not found for user '{current_user.username}' ---")
        flash('Employee details not found.', 'danger')
        return redirect(url_for('main.index'))

