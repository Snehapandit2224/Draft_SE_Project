import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Employee, ExitFeedback, ExitReason

app = create_app('development')

NUM_EMPLOYEES_TARGET = 50
NUM_EXIT_FEEDBACK_TARGET = 10

with app.app_context():
    emp_count = Employee.query.count()
    ef_count = ExitFeedback.query.count()

    print(f'Current employees: {emp_count}')
    print(f'Current exit_feedbacks: {ef_count}')

    # Insert employees if needed
    to_add_employees = max(0, NUM_EMPLOYEES_TARGET - emp_count)
    if to_add_employees > 0:
        print(f'Inserting {to_add_employees} employees...')
        first_names = ['Alex','Taylor','Jordan','Morgan','Casey','Riley','Jamie','Avery','Quinn','Parker']
        last_names = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Wilson','Anderson']
        depts = ['Sales','Marketing','Engineering','HR','Finance','Support']
        positions = ['Manager','Developer','Analyst','Intern','Lead','Specialist']

        for i in range(to_add_employees):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            email = f'{fn.lower()}.{ln.lower()}.{random.randint(1,9999)}@example.com'
            department = random.choice(depts)
            position = random.choice(positions)
            # hire_date between 1 month and 10 years ago
            hire_date = (datetime.now().date() - timedelta(days=random.randint(30, 3650)))
            salary = random.randint(35000, 180000)
            emp = Employee(
                first_name=fn,
                last_name=ln,
                email=email,
                department=department,
                position=position,
                hire_date=hire_date,
                salary=salary,
                is_active=True,
                status='active'
            )
            db.session.add(emp)
        db.session.commit()
        print('Employees inserted.')
    else:
        print('No new employees required.')

    # Refresh counts and list of employees
    emp_count = Employee.query.count()
    employees = Employee.query.all()
    employee_ids = [e.id for e in employees]

    # Insert exit feedbacks if needed
    ef_count = ExitFeedback.query.count()
    to_add_ef = max(0, NUM_EXIT_FEEDBACK_TARGET - ef_count)
    if to_add_ef > 0:
        print(f'Inserting {to_add_ef} exit feedbacks...')
        reasons = [ExitReason.resignation, ExitReason.termination, ExitReason.retirement]
        for i in range(to_add_ef):
            # pick a random employee; mark them terminated if not already
            emp_id = random.choice(employee_ids)
            employee = Employee.query.get(emp_id)
            # Set employee as terminated
            employee.is_active = False
            employee.status = 'terminated'

            exit_date = datetime.now().date() - timedelta(days=random.randint(0, 365))
            reason = random.choice(reasons)
            feedback = f'Sample exit feedback {random.randint(1000,9999)}'
            interview_completed = random.choice([True, False])
            interview_date = None
            if interview_completed:
                interview_date = datetime.now() - timedelta(days=random.randint(0, 30))

            ef = ExitFeedback(
                employee_id=emp_id,
                exit_date=exit_date,
                reason=reason,
                feedback=feedback,
                interview_completed=interview_completed,
                interview_date=interview_date
            )
            db.session.add(ef)
        db.session.commit()
        print('Exit feedbacks inserted and corresponding employees marked terminated.')
    else:
        print('No new exit feedbacks required.')

    # Final counts
    print('Final counts:')
    print('Employees:', Employee.query.count())
    print('Exit feedbacks:', ExitFeedback.query.count())
