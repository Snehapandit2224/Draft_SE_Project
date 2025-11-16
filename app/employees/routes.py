from flask import render_template
from . import employees
from ..models import Employee
from ..utils.decorators import login_required

@employees.route('/employees')
@login_required
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/employees.html', employees=employees)

@employees.route('/employees/<int:id>')
@login_required
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/employee.html', employee=employee)

