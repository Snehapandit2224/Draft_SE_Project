from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user
from . import employees
from .. import db
from ..models import Employee, EmployeeHistory
from datetime import datetime

from app.utils.decorators import validate_input

@employees.route('/api/employees', methods=['POST'])
@jwt_required()
@validate_input(
    required_fields=['first_name', 'last_name', 'email', 'department', 'position', 'hire_date', 'salary'],
    email_fields=['email'],
    salary_fields=['salary']
)
def create_employee(data):
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
        hire_date=hire_date,
        salary=data['salary']
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify(employee.to_dict()), 201

@employees.route('/api/employees/<int:id>', methods=['GET', 'PUT'])
@jwt_required()
def employee_detail(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'GET':
        return jsonify(employee.to_dict())
    
    # PUT request
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

@employees.route('/api/employees', methods=['GET'])
@jwt_required()
def get_employees():
    query = Employee.query

    # Filtering
    if 'department' in request.args:
        query = query.filter(Employee.department == request.args['department'])
    if 'position' in request.args:
        query = query.filter(Employee.position == request.args['position'])
    if 'status' in request.args:
        query = query.filter(Employee.status == request.args['status'])

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    paginated_employees = query.paginate(page=page, per_page=per_page, error_out=False)
    
    employees_list = [e.to_dict() for e in paginated_employees.items]
    
    return jsonify({
        'employees': employees_list,
        'total': paginated_employees.total,
        'pages': paginated_employees.pages,
        'current_page': paginated_employees.page
    })



@employees.route('/api/employees/<int:id>/history', methods=['GET'])
@jwt_required()
def get_employee_history(id):
    employee = Employee.query.get_or_404(id)
    history = EmployeeHistory.query.filter_by(employee_id=id).all()
    return jsonify([h.to_dict() for h in history])

# Helper to convert Employee object to dictionary
def to_dict(self):
    # A more robust to_dict that handles dates
    data = {}
    for c in self.__table__.columns:
        value = getattr(self, c.name)
        if isinstance(value, datetime):
            data[c.name] = value.isoformat()
        else:
            data[c.name] = value
    return data

Employee.to_dict = to_dict
EmployeeHistory.to_dict = to_dict
