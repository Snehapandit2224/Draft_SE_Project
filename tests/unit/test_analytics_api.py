import unittest
import json
import sys
import os
from datetime import date
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee, ExitFeedback, ExitReason

class TestAnalyticsApi(unittest.TestCase):
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

    def test_get_exit_reasons_report(self):
        e1 = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        e2 = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                      department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add_all([e1, e2])
        db.session.commit()

        feedback1 = ExitFeedback(employee_id=e1.id, exit_date=date(2024, 1, 15), reason=ExitReason.resignation,
                                 feedback='...')
        feedback2 = ExitFeedback(employee_id=e2.id, exit_date=date(2024, 1, 16), reason=ExitReason.termination,
                                 feedback='...')
        feedback3 = ExitFeedback(employee_id=e1.id, exit_date=date(2024, 1, 17), reason=ExitReason.resignation,
                                 feedback='...')
        db.session.add_all([feedback1, feedback2, feedback3])
        db.session.commit()

        response = self.client.get('/analytics/api/reports/exit-reasons')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        
        resignation_data = next((item for item in data if item["reason"] == "resignation"), None)
        self.assertIsNotNone(resignation_data)
        self.assertEqual(resignation_data['count'], 2)

    def test_get_exit_reasons_report_with_filters(self):
        e1 = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        e2 = Employee(first_name='Jane', last_name='Doe', email='jane.doe@example.com',
                      department='Marketing', position='Marketing Manager', hire_date=date(2022, 11, 20))
        db.session.add_all([e1, e2])
        db.session.commit()

        feedback1 = ExitFeedback(employee_id=e1.id, exit_date=date(2024, 1, 15), reason=ExitReason.resignation,
                                 feedback='...')
        feedback2 = ExitFeedback(employee_id=e2.id, exit_date=date(2024, 1, 16), reason=ExitReason.termination,
                                 feedback='...')
        db.session.add_all([feedback1, feedback2])
        db.session.commit()

        response = self.client.get('/analytics/api/reports/exit-reasons?department=Engineering')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['reason'], 'resignation')

    def test_export_exit_reasons_report(self):
        e1 = Employee(first_name='John', last_name='Doe', email='john.doe@example.com',
                      department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 15))
        db.session.add(e1)
        db.session.commit()

        feedback1 = ExitFeedback(employee_id=e1.id, exit_date=date(2024, 1, 15), reason=ExitReason.resignation,
                                 feedback='...')
        db.session.add(feedback1)
        db.session.commit()

        response = self.client.get('/analytics/api/reports/exit-reasons/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/csv')
        self.assertIn(b'Reason,Count,Percentage', response.data)
        self.assertIn(b'resignation,1,100.0', response.data)
