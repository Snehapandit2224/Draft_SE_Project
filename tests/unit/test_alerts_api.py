import unittest
import json
import sys
import os
from datetime import date
from unittest.mock import patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app import create_app, db
from app.models import Employee, ExitFeedback, ExitReason, AttritionAlert
from app.jobs import check_attrition_hotspots

class TestAlertsApi(unittest.TestCase):
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

    def test_get_alerts(self):
        alert1 = AttritionAlert(alert_type='attrition_hotspot', group_name='Engineering', value=20.0)
        alert2 = AttritionAlert(alert_type='attrition_hotspot', group_name='Marketing', value=25.0)
        db.session.add_all([alert1, alert2])
        db.session.commit()

        response = self.client.get('/alerts/api/alerts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    @patch('app.jobs.send_email_alert')
    def test_check_attrition_hotspots_creates_alert_and_sends_email(self, mock_send_email):
        # Create 10 employees in Engineering
        for i in range(10):
            e = Employee(first_name=f'John{i}', last_name='Doe', email=f'john.doe{i}@example.com',
                         department='Engineering', position='Software Engineer', hire_date=date(2023, 1, 1))
            db.session.add(e)
        db.session.commit()

        # Create exits to create a hotspot in Engineering
        feedback1 = ExitFeedback(employee_id=1, exit_date=date(2023, 2, 15), reason=ExitReason.resignation, feedback='...')
        feedback2 = ExitFeedback(employee_id=2, exit_date=date(2023, 3, 15), reason=ExitReason.resignation, feedback='...')
        feedback3 = ExitFeedback(employee_id=3, exit_date=date(2023, 3, 15), reason=ExitReason.resignation, feedback='...')
        feedback4 = ExitFeedback(employee_id=4, exit_date=date(2023, 4, 15), reason=ExitReason.resignation, feedback='...')
        feedback5 = ExitFeedback(employee_id=5, exit_date=date(2023, 4, 15), reason=ExitReason.resignation, feedback='...')
        db.session.add_all([feedback1, feedback2, feedback3, feedback4, feedback5])
        db.session.commit()

        with self.app.app_context():
            check_attrition_hotspots(self.app)

        alerts = AttritionAlert.query.all()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0].group_name, 'Engineering')
        mock_send_email.assert_called_once()
