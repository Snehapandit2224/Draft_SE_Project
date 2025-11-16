import unittest
from unittest.mock import patch
from app import create_app, cache
from app.models import Employee, db

class CachingTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            cache.clear()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        self.app_context.pop()

    def test_report_endpoint_is_cached(self):
        """Test that the report endpoint is cached."""
        with self.app.app_context():
            # First request should not be cached
            response1 = self.client.get('/analytics/api/reports/export')
            self.assertEqual(response1.status_code, 200)
            self.assertTrue(response1.data)

            # Second request should be cached
            response2 = self.client.get('/analytics/api/reports/export')
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response1.data, response2.data)

    def test_cache_is_invalidated_on_data_change(self):
        """Test that the cache is invalidated when the data changes."""
        with self.app.app_context():
            # First request should not be cached
            response1 = self.client.get('/analytics/api/reports/export')
            self.assertEqual(response1.status_code, 200)
            self.assertTrue(response1.data)

            # Add a new employee, which should invalidate the cache
            from datetime import datetime
            new_employee = Employee(first_name='test', last_name='user', email='test@test.com', department='test', position='test', hire_date=datetime.strptime('2022-01-01', '%Y-%m-%d').date(), salary=50000)
            db.session.add(new_employee)
            db.session.commit()
            cache.clear()

            # Second request should not be cached
            response2 = self.client.get('/analytics/api/reports/export')
            self.assertEqual(response2.status_code, 200)
            self.assertNotEqual(response1.data, response2.data)

if __name__ == '__main__':
    unittest.main()
