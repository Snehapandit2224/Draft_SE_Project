from flask import Blueprint, render_template, redirect, url_for, request
from flask_jwt_extended import current_user
from app.utils.decorators import login_required
from app.models import Employee, User # Import User model as well

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    if current_user.role == 'employee':
        # Assuming username is first_name.lower() + last_name.lower()
        # This is a simplified way to link, a proper foreign key would be better
        # Need to handle cases where username might have numbers appended for uniqueness
        username_parts = current_user.username.lower()
        
        # Attempt to find employee by exact username match (firstnamelastname)
        employee = Employee.query.filter(
            (Employee.first_name.ilike(username_parts + '%')) &
            (Employee.last_name.ilike('%')) # This part is tricky without a clear separator
        ).first()

        # A more robust way would be to store employee_id in the User model
        # For now, let's try to split the username
        # This is a heuristic and might fail if names are complex or have numbers
        found_employee = None
        all_employees = Employee.query.all()
        for emp in all_employees:
            expected_username = f"{emp.first_name.lower()}{emp.last_name.lower()}"
            if current_user.username.startswith(expected_username):
                found_employee = emp
                break
        
        if found_employee:
            return render_template('index.html', employee=found_employee, is_employee=True, current_user=current_user)
        else:
            # Fallback if employee not found, maybe show a generic message or error
            return render_template('index.html', message="Employee details not found.", is_employee=True, current_user=current_user)
    else: # Admin or other roles
        return render_template('index.html', is_employee=False, current_user=current_user)

@main.route('/health')
def health_check():
    return 'OK'
