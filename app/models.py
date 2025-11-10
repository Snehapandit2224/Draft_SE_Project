from . import db
from sqlalchemy import event
from datetime import datetime
from sqlalchemy.orm.attributes import get_history
import enum

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
    status = db.Column(db.String(64), default='active')

class EmployeeHistory(db.Model):
    __tablename__ = 'employee_history'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    old_status = db.Column(db.String(64))
    new_status = db.Column(db.String(64))
    changed_by = db.Column(db.String(64))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

import enum

class ExitReason(enum.Enum):
    resignation = 'resignation'
    termination = 'termination'
    retirement = 'retirement'

class ExitFeedback(db.Model):
    __tablename__ = 'exit_feedback'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    exit_date = db.Column(db.Date)
    reason = db.Column(db.Enum(ExitReason))
    feedback = db.Column(db.Text)
    interview_completed = db.Column(db.Boolean, default=False)
    interview_date = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'exit_date': self.exit_date.isoformat() if self.exit_date else None,
            'reason': self.reason.value if self.reason else None,
            'feedback': self.feedback,
            'interview_completed': self.interview_completed,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None
        }

class AttritionPrediction(db.Model):
    __tablename__ = 'attrition_predictions'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    prediction_date = db.Column(db.DateTime)
    attrition_probability = db.Column(db.Float)
    shap_values = db.Column(db.Text)
