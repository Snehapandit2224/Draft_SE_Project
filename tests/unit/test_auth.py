import unittest
import json
from app import create_app, db
from app.models import User
from flask_jwt_extended import create_access_token

class AuthTestCase(unittest.TestCase):
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

    def test_register(self):
        # Test user registration
        res = self.client.post('/auth/register',
                               data=json.dumps({'username': 'testuser', 'password': 'testpassword'}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('User registered successfully', str(res.data))

    def test_register_existing_user(self):
        # Test registration with an existing username
        user = User(username='testuser')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        res = self.client.post('/auth/register',
                               data=json.dumps({'username': 'testuser', 'password': 'testpassword'}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 409)
        self.assertIn('Username already exists', str(res.data))

    def test_login(self):
        # Test user login
        user = User(username='testuser')
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()

        res = self.client.post('/auth/login',
                               data=json.dumps({'username': 'testuser', 'password': 'testpassword'}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertIn('access_token', str(res.data))

    def test_login_invalid_credentials(self):
        # Test login with invalid credentials
        res = self.client.post('/auth/login',
                               data=json.dumps({'username': 'wronguser', 'password': 'wrongpassword'}),
                               content_type='application/json')
        self.assertEqual(res.status_code, 401)
        self.assertIn('Invalid credentials', str(res.data))

    def test_access_protected_endpoint_with_token(self):
        # Register a user
        self.client.post('/auth/api/register', json={
            'username': 'testuser',
            'password': 'testpassword'
        })

        # Log in the user to get a token
        res = self.client.post('/auth/api/login', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        access_token = res.json['access_token']

        # Access a protected endpoint with the token
        res = self.client.get('/employees/api/employees', headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(res.status_code, 200)

    def test_access_protected_endpoint_without_token(self):
        # Test accessing a protected endpoint without a token
        res = self.client.get('/employees/api/employees')
        self.assertEqual(res.status_code, 401)
        self.assertIn('Missing Authorization Header', str(res.data))

    def test_access_protected_endpoint_with_invalid_token(self):
        # Test accessing a protected endpoint with an invalid token
        res = self.client.get('/employees/api/employees',
                              headers={'Authorization': 'Bearer invalidtoken'})
        self.assertEqual(res.status_code, 401)
        self.assertIn('Signature verification failed', str(res.data))

if __name__ == '__main__':
    unittest.main()
