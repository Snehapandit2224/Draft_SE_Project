from app import create_app, db
from app.models import Employee, ExitFeedback
import json

app = create_app('development')
app.config['TESTING'] = True
with app.test_client() as client:
    # Get an active employee to use for exit feedback
    with app.app_context():
        emp = Employee.query.filter_by(is_active=True).first()
        if emp:
            emp_id = emp.id
            print(f'Testing with employee ID {emp_id}: {emp.first_name} {emp.last_name}')
            print(f'Before: is_active={emp.is_active}, status={emp.status}')
        else:
            print('No active employees found')
            exit(1)
    
    # Submit exit feedback
    exit_data = {
        'employee_id': emp_id,
        'exit_date': '2025-11-20',
        'reason': 'resignation',
        'feedback': 'Test exit feedback'
    }
    
    r = client.post('/exit/api/exit-feedback',
                     data=json.dumps(exit_data),
                     content_type='application/json')
    print(f'\nSubmit exit feedback response: {r.status_code}')
    print(f'Response: {json.dumps(r.get_json(), indent=2)}')
    
    # Check if employee is now inactive
    with app.app_context():
        emp_after = Employee.query.get(emp_id)
        print(f'\nAfter: is_active={emp_after.is_active}, status={emp_after.status}')
