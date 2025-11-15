import unittest
import json
from app import create_app, db
from app.models import User

class AuthE2ETestCase(unittest.TestCase):
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

    def test_register_login_and_protected_access(self):
        # Register new user
        res = self.client.post('/api/auth/register', json={
            'username': 'e2euser',
            'password': 'e2epass'
        })
        self.assertEqual(res.status_code, 201)

        # Login and receive token
        res = self.client.post('/api/auth/login', json={
            'username': 'e2euser',
            'password': 'e2epass'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('access_token', data)
        token = data['access_token']

        # Access protected employees endpoint
        res = self.client.get('/employees/api/employees', headers={'Authorization': f'Bearer {token}'})
        # 200 with empty list (no employees created) or 200/204 depending on implementation
        self.assertIn(res.status_code, (200, 204))

    def test_protected_access_invalid_token(self):
        prev_testing = self.app.config.get('TESTING')
        prev_enforce = self.app.config.get('ENFORCE_HTTPS')
        self.app.config['TESTING'] = False
        self.app.config['ENFORCE_HTTPS'] = False
        try:
            res = self.client.get('/employees/api/employees', headers={'Authorization': 'Bearer invalidtoken'})
            self.assertEqual(res.status_code, 401)
            self.assertIn('Signature verification failed', res.get_data(as_text=True))
        finally:
            self.app.config['TESTING'] = prev_testing
            self.app.config['ENFORCE_HTTPS'] = prev_enforce

if __name__ == '__main__':
    unittest.main()
