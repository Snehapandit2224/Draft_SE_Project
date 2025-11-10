import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee, EmployeeHistory

class TestEmployeeApi(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_employee(self):
        employee_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'department': 'Engineering',
            'position': 'Software Engineer',
            'hire_date': '2023-01-15'
        }
        response = self.client.post('/employees/api/employees',
                                     data=json.dumps(employee_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('John', str(response.data))

    def test_create_employee_missing_fields(self):
        employee_data = {'first_name': 'John'}
        response = self.client.post('/employees/api/employees',
                                     data=json.dumps(employee_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing field', str(response.data))

    def test_update_employee(self):
        e = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                     department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add(e)
        db.session.commit()

        update_data = {'position': 'Senior Software Engineer'}
        response = self.client.put(f'/employees/api/employees/{e.id}',
                                    data=json.dumps(update_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Senior Software Engineer', str(response.data))

    def test_update_employee_status_creates_history(self):
        e = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                     department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add(e)
        db.session.commit()

        update_data = {'status': 'on-leave'}
        response = self.client.put(f'/employees/api/employees/{e.id}',
                                    data=json.dumps(update_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        history = EmployeeHistory.query.filter_by(employee_id=e.id).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_status, 'active')
        self.assertEqual(history.new_status, 'on-leave')

    def test_get_employee(self):
        e = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                     department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add(e)
        db.session.commit()

        response = self.client.get(f'/employees/api/employees/{e.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Jane', str(response.data))

    def test_get_employees(self):
        e1 = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                      department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        e2 = Employee(first_name='John', last_name='Smith', email='john.smith@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add_all([e1, e2])
        db.session.commit()

        response = self.client.get('/employees/api/employees')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['employees']), 2)

    def test_get_employees_with_filters(self):
        e1 = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                      department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        e2 = Employee(first_name='John', last_name='Smith', email='john.smith@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add_all([e1, e2])
        db.session.commit()

        response = self.client.get('/employees/api/employees?department=Marketing')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['employees'][0]['first_name'], 'Jane')

    def test_get_employees_pagination(self):
        for i in range(15):
            e = Employee(first_name=f'First{i}', last_name=f'Last{i}', email=f'test{i}@example.com',
                         department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
            db.session.add(e)
        db.session.commit()

        response = self.client.get('/employees/api/employees?page=2&per_page=5')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['total'], 15)
        self.assertEqual(len(data['employees']), 5)
        self.assertEqual(data['current_page'], 2)
        self.assertEqual(data['pages'], 3)
