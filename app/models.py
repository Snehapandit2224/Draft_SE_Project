from . import db

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    department = db.Column(db.String(64))
    position = db.Column(db.String(64))
    hire_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

class EmployeeHistory(db.Model):
    __tablename__ = 'employee_history'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    event = db.Column(db.String(255))
    event_date = db.Column(db.DateTime)

class ExitFeedback(db.Model):
    __tablename__ = 'exit_feedback'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    exit_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    feedback = db.Column(db.Text)

class AttritionPrediction(db.Model):
    __tablename__ = 'attrition_predictions'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    prediction_date = db.Column(db.DateTime)
    attrition_probability = db.Column(db.Float)
    shap_values = db.Column(db.Text)
