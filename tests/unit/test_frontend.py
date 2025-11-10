import unittest
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee

class TestFrontend(unittest.TestCase):
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

    def test_employees_page(self):
        e1 = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                      department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        e2 = Employee(first_name='John', last_name='Smith', email='john.smith@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add_all([e1, e2])
        db.session.commit()

        response = self.client.get('/employees/employees')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)
        self.assertIn(b'John Smith', response.data)

    def test_employee_page(self):
        e = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                     department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add(e)
        db.session.commit()

        response = self.client.get(f'/employees/employees/{e.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)
        self.assertIn(b'Marketing', response.data)
