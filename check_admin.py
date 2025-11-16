from app import create_app
from app.models import User

app = create_app('development')
with app.app_context():
    u = User.query.filter_by(username='admin').first()
    print('user_exists:', bool(u))
    if u:
        print('username:', u.username)
        print('password_hash (prefix):', (u.password_hash or '')[:60] + '...')
        print('check password("password"):', u.check_password('password'))
    else:
        print('admin user not found')
