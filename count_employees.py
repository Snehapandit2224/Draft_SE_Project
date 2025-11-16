from app import create_app, db
from app.models import Employee
import os

# Set the environment variable for development database
os.environ['FLASK_CONFIG'] = 'development'

app = create_app('development')

with app.app_context():
    employee_count = db.session.query(Employee).count()
    print(f"Number of employees: {employee_count}")
