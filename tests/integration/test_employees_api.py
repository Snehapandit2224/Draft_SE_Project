import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee

class TestEmployeeApiIntegration(unittest.TestCase):
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

    def test_create_and_get_employee(self):
        employee_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane.doe@example.com',
            'department': 'Marketing',
            'position': 'Marketing Manager',
            'hire_date': '2022-11-20'
        }
        # Create employee
        response = self.client.post('/employees/api/employees',
                                     data=json.dumps(employee_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        created_employee = json.loads(response.data)

        # Get employee from DB
        employee_from_db = Employee.query.get(created_employee['id'])
        self.assertIsNotNone(employee_from_db)
        self.assertEqual(employee_from_db.first_name, 'Jane')

    def test_update_employee_in_db(self):
        e = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                     department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add(e)
        db.session.commit()

        update_data = {'department': 'Sales'}
        response = self.client.put(f'/employees/api/employees/{e.id}',
                                    data=json.dumps(update_data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify update in DB
        updated_employee = Employee.query.get(e.id)
        self.assertEqual(updated_employee.department, 'Sales')
