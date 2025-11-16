import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Employee, User

def create_sample_employees():
    """Create sample employees."""
    app = create_app('development')
    with app.app_context():
        # Clear existing data
        db.session.query(Employee).delete()

        names = [
            ('Jane', 'Doe'),
            ('John', 'Walker'),
            ('Cessna', 'Williams'),
            ('Albert', 'Griffin'),
            ('Jack', 'Hilbert')
        ]

        for i, (first_name, last_name) in enumerate(names):
            email = f'{first_name.lower()}.{last_name.lower()}@example.com'
            department = random.choice(['Sales', 'Marketing', 'Engineering', 'HR'])
            position = random.choice(['Manager', 'Developer', 'Analyst', 'Intern'])
            hire_date = datetime.now().date() - timedelta(days=random.randint(30, 3650))
            salary = random.randint(50000, 150000)
            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                salary=salary
            )
            db.session.add(employee)
        db.session.commit()

def create_default_users():
    """Create default users."""
    app = create_app('development')
    with app.app_context():
        # Clear existing data
        db.session.query(User).delete()

        admin_user = User(username='admin', role='admin')
        admin_user.set_password('password')
        db.session.add(admin_user)

        employee_user = User(username='employee', role='employee')
        employee_user.set_password('password')
        db.session.add(employee_user)

        db.session.commit()

if __name__ == '__main__':
    create_sample_employees()
    create_default_users()
