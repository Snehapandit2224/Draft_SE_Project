import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Employee, User

def create_sample_employees():
    """Create sample employees."""
    app = create_app('development')
    with app.app_context():
        # Clear ALL existing data for Employees and Users
        db.session.query(Employee).delete()
        db.session.query(User).delete()
        db.session.commit() # Commit deletions to ensure a clean slate

        # Re-create admin user
        admin_user = User(username='admin', role='admin')
        admin_user.set_password('password')
        db.session.add(admin_user)
        db.session.commit() # Commit admin user before adding employees
        print(f"Admin user created: Username='{admin_user.username}', Password='password'")

        first_names = ['Jane', 'John', 'Cessna', 'Albert', 'Jack', 'Emily', 'Michael', 'Sarah', 'David', 'Laura',
                       'Chris', 'Anna', 'James', 'Olivia', 'Daniel', 'Sophia', 'Matthew', 'Isabella', 'Joseph', 'Mia',
                       'Robert', 'Charlotte', 'Charles', 'Amelia', 'Thomas', 'Harper', 'George', 'Evelyn', 'William', 'Abigail',
                       'Richard', 'Elizabeth', 'Kenneth', 'Sofia', 'Paul', 'Avery', 'Steven', 'Ella', 'Edward', 'Scarlett',
                       'Brian', 'Grace', 'Ronald', 'Chloe', 'Anthony', 'Victoria', 'Kevin', 'Riley', 'Jason', 'Aria']
        last_names = ['Doe', 'Walker', 'Williams', 'Griffin', 'Hilbert', 'Smith', 'Jones', 'Brown', 'Davis', 'Miller',
                      'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson',
                      'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez', 'Lewis', 'Lee', 'Walker', 'Hall', 'Allen',
                      'Young', 'Hernandez', 'King', 'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker',
                      'Nelson', 'Carter', 'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans']

        employees_to_add = []
        for i in range(50):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'{first_name.lower()}.{last_name.lower()}@example.com' # Removed 'i'
            department = random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations'])
            position = random.choice(['Manager', 'Developer', 'Analyst', 'Intern', 'Director', 'Associate'])
            hire_date = datetime.now().date() - timedelta(days=random.randint(30, 3650))
            salary = random.randint(50000, 150000)
            is_active = True
            status = 'active'
            if i % 10 == 0: # Make some employees inactive for variety
                is_active = False
                status = random.choice(['terminated', 'resigned'])

            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                salary=salary,
                is_active=is_active,
                status=status
            )
            employees_to_add.append(employee)
            db.session.add(employee)
        db.session.commit()

        # Create users for each employee
        for employee in employees_to_add: # Removed 'i' from enumerate
            username = f"{employee.first_name.lower()}{employee.last_name.lower()}" # Removed 'i'
            user = User(username=username, role='employee')
            user.set_password(username) # Password is also the concatenated name
            db.session.add(user)
            print(f"Generated Employee User: Username='{username}', Password='{username}'")
        db.session.commit()
        
        total_users = db.session.query(User).count()
        print(f"Total users in database after seeding: {total_users}")

def create_default_users():
    """This function is no longer needed as admin user is created in create_sample_employees."""
    pass

if __name__ == '__main__':
    create_sample_employees()
    # create_default_users() # No longer call this as admin is created in create_sample_employees

