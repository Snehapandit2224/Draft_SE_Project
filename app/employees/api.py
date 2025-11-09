from flask import request, jsonify
from . import employees
from .. import db
from ..models import Employee, EmployeeHistory
from datetime import datetime

@employees.route('/api/employees', methods=['POST'])
def create_employee():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['first_name', 'last_name', 'email', 'department', 'position', 'hire_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    try:
        hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format for hire_date. Use YYYY-MM-DD.'}), 400

    employee = Employee(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        department=data['department'],
        position=data['position'],
        hire_date=hire_date
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify(employee.to_dict()), 201

@employees.route('/api/employees/<int:id>', methods=['PUT'])
def update_employee(id):
    employee = Employee.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    if 'status' in data and data['status'] != employee.status:
        history = EmployeeHistory(
            employee_id=employee.id,
            old_status=employee.status,
            new_status=data['status'],
            changed_by='system'  # In a real app, this would be the logged-in user
        )
        db.session.add(history)

    for field in ['first_name', 'last_name', 'email', 'department', 'position', 'is_active', 'status']:
        if field in data:
            setattr(employee, field, data[field])
    
    if 'hire_date' in data:
        try:
            hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            employee.hire_date = hire_date
        except ValueError:
            return jsonify({'error': 'Invalid date format for hire_date. Use YYYY-MM-DD.'}), 400

    db.session.commit()
    return jsonify(employee.to_dict())

@employees.route('/api/employees/<int:id>/history', methods=['GET'])
def get_employee_history(id):
    employee = Employee.query.get_or_404(id)
    history = EmployeeHistory.query.filter_by(employee_id=id).all()
    return jsonify([h.to_dict() for h in history])

# Helper to convert Employee object to dictionary
def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Employee.to_dict = to_dict
EmployeeHistory.to_dict = to_dict
