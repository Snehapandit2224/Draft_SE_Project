import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee, ExitFeedback

class TestExitManagementApiIntegration(unittest.TestCase):
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

    def test_create_and_get_exit_feedback(self):
        e = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                     department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add(e)
        db.session.commit()

        feedback_data = {
            'employee_id': e.id,
            'exit_date': '2024-01-15',
            'reason': 'resignation',
            'feedback': 'It was a great experience.'
        }
        # Create feedback
        response = self.client.post('/exit/api/exit-feedback',
                                     data=json.dumps(feedback_data),
                                     content_type='application/json')
        self.assertEqual(response.status_code, 201)
        created_feedback = json.loads(response.data)

        # Get feedback from DB
        feedback_from_db = ExitFeedback.query.get(created_feedback['id'])
        self.assertIsNotNone(feedback_from_db)
        self.assertEqual(feedback_from_db.feedback, 'It was a great experience.')
