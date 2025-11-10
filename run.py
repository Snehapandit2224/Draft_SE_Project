import os
from app import create_app, db
from app.models import Employee, EmployeeHistory, ExitFeedback, AttritionPrediction, AttritionAlert
from flask_migrate import Migrate
from app.jobs import init_scheduler

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Employee=Employee, EmployeeHistory=EmployeeHistory,
                ExitFeedback=ExitFeedback, AttritionPrediction=AttritionPrediction,
                AttritionAlert=AttritionAlert)

if __name__ == '__main__':
    init_scheduler(app)
    app.run(debug=True)
