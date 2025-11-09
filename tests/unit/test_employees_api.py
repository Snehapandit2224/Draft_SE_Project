import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee

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
