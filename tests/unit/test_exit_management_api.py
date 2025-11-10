import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee, ExitFeedback, ExitReason

class TestExitManagementApi(unittest.TestCase):
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

    def test_create_exit_feedback(self):
        e = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                     department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add(e)
        db.session.commit()

        feedback_data = {
            'employee_id': e.id,
            'exit_date': '2024-01-15',
            'reason': 'resignation',
            'feedback': 'Great place to work!'
        }
        response = self.client.post('/exit/api/exit-feedback',
                                     data=json.dumps(feedback_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('resignation', str(response.data))

    def test_create_exit_feedback_missing_fields(self):
        feedback_data = {'employee_id': 1}
        response = self.client.post('/exit/api/exit-feedback',
                                     data=json.dumps(feedback_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Missing field', str(response.data))

    def test_create_exit_feedback_invalid_reason(self):
        e = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                     department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add(e)
        db.session.commit()

        feedback_data = {
            'employee_id': e.id,
            'exit_date': '2024-01-15',
            'reason': 'invalid_reason',
            'feedback': 'Great place to work!'
        }
        response = self.client.post('/exit/api/exit-feedback',
                                     data=json.dumps(feedback_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid reason', str(response.data))

    def test_create_exit_feedback_employee_not_found(self):
        feedback_data = {
            'employee_id': 999,
            'exit_date': '2024-01-15',
            'reason': 'resignation',
            'feedback': 'Great place to work!'
        }
        response = self.client.post('/exit/api/exit-feedback',
                                     data=json.dumps(feedback_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Employee not found', str(response.data))
