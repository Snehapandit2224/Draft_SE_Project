from flask import render_template
from . import employees
from ..models import Employee

@employees.route('/employees')
def list_employees():
    employees = Employee.query.all()
    return render_template('employees/employees.html', employees=employees)

@employees.route('/employees/<int:id>')
def view_employee(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/employee.html', employee=employee)

