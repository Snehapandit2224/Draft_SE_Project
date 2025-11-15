import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db

app = create_app('testing')
with app.app_context():
    db.drop_all()
    db.create_all()
    client = app.test_client()

    # Register
    r = client.post('/api/auth/register', json={'username': 'dbguser', 'password': 'dbgpass'})
    print('register', r.status_code, r.get_data(as_text=True))

    # Login
    r = client.post('/api/auth/login', json={'username': 'dbguser', 'password': 'dbgpass'})
    print('login', r.status_code, r.get_data(as_text=True))
    try:
        token = r.get_json().get('access_token')
    except Exception:
        token = None
    print('token:', token)
    print('JWT_SECRET_KEY in app config:', app.config.get('JWT_SECRET_KEY'))
    # Try manual PyJWT decode
    try:
        import jwt as pyjwt
        decoded = pyjwt.decode(token, app.config.get('JWT_SECRET_KEY'), algorithms=["HS256"], options={"verify_exp": False})
        print('PyJWT decode success:', decoded)
    except Exception as e:
        print('PyJWT decode error:', e)

    # Access protected
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    r = client.get('/employees/api/employees', headers=headers)
    print('protected', r.status_code, r.get_data(as_text=True))
