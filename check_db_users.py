from app import create_app, db
from app.models import User
import os

# Set the environment variable for development database
os.environ['FLASK_CONFIG'] = 'development'

app = create_app('development')

with app.app_context():
    users = User.query.all()
    print(f"Found {len(users)} users in the database:")
    for user in users:
        print(f"  - Username: {user.username}, Role: {user.role}")
