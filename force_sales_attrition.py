from app import create_app, db
from datetime import datetime, timedelta
import random

app = create_app('development')
with app.app_context():
    from app.models import Employee, ExitFeedback, ExitReason

    # find active employees in Sales
    sales_active = Employee.query.filter_by(department='Sales', is_active=True).all()
    to_create = 0
    if len(sales_active) < 10:
        # pick from any active employees to assign to Sales then mark them terminated
        others = Employee.query.filter_by(is_active=True).all()
        needed = 10 - len(sales_active)
        picks = random.sample(others, min(len(others), needed))
        for p in picks:
            p.department = 'Sales'
            sales_active.append(p)
            db.session.add(p)
        db.session.commit()

    # reload sales_active
    sales_active = Employee.query.filter_by(department='Sales', is_active=True).all()
    create_count = 0
    for emp in sales_active[:10]:
        # mark terminated and add exit feedback in the last 90 days
        emp.is_active = False
        emp.status = 'terminated'
        exit_date = datetime.now().date() - timedelta(days=random.randint(0,90))
        ef = ExitFeedback(employee_id=emp.id, exit_date=exit_date, reason=ExitReason.resignation, feedback='Forced attrition test.', interview_completed=False)
        db.session.add(emp)
        db.session.add(ef)
        create_count += 1
    db.session.commit()
    print('Created exit feedbacks for Sales:', create_count)
