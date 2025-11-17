import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Employee, User, ExitFeedback, ExitReason

def create_terminated_employees():
    """Create 20 terminated employees."""
    app = create_app('development')
    with app.app_context():
        first_names = ['James', 'Olivia', 'Daniel', 'Sophia', 'Matthew', 'Isabella', 'Joseph', 'Mia',
                       'Robert', 'Charlotte', 'Charles', 'Amelia', 'Thomas', 'Harper', 'George', 'Evelyn', 'William', 'Abigail',
                       'Richard', 'Elizabeth']
        last_names = ['Smith', 'Jones', 'Brown', 'Davis', 'Miller',
                      'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson',
                      'Garcia', 'Martinez', 'Robinson', 'Clark', 'Rodriguez']

        employees_to_add = []
        for i in range(20):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            # to avoid email collision
            email = f'{first_name.lower()}.{last_name.lower()}{i}@example.com'
            department = random.choice(['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations'])
            position = random.choice(['Manager', 'Developer', 'Analyst', 'Intern', 'Director', 'Associate'])
            hire_date = datetime.now().date() - timedelta(days=random.randint(30, 3650))
            salary = random.randint(50000, 150000)
            
            status = random.choice(list(ExitReason))

            employee = Employee(
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                salary=salary,
                is_active=False,
                status=status.value
            )
            db.session.add(employee)
            db.session.commit()
            employees_to_add.append(employee)

            exit_date = hire_date + timedelta(days=random.randint(30, (datetime.now().date() - hire_date).days))
            exit_feedback = ExitFeedback(
                employee_id=employee.id,
                exit_date=exit_date,
                reason=status,
                feedback="Sample feedback"
            )
            db.session.add(exit_feedback)
            db.session.commit()

            username = f"{employee.first_name.lower()}{employee.last_name.lower()}{i}"
            user = User(username=username, role='employee')
            user.set_password(username)
            db.session.add(user)
            print(f"Generated Terminated Employee User: Username='{username}', Password='{username}'")
        
        db.session.commit()
        
        total_employees = db.session.query(Employee).count()
        print(f"Total employees in database after seeding: {total_employees}")

if __name__ == '__main__':
    create_terminated_employees()
