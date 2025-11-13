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
    salary = db.Column(db.Float, db.CheckConstraint('salary >= 30000 AND salary <= 200000'))
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(64), default='active')

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'department': self.department,
            'position': self.position,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'salary': self.salary,
            'is_active': self.is_active,
            'status': self.status
        }

class EmployeeHistory(db.Model):
    __tablename__ = 'employee_history'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    old_status = db.Column(db.String(64))
    new_status = db.Column(db.String(64))
    changed_by = db.Column(db.String(64))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by,
            'changed_at': self.changed_at.isoformat() if self.changed_at else None
        }

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

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'attrition_probability': self.attrition_probability,
            'shap_values': self.shap_values
        }

class AttritionAlert(db.Model):
    __tablename__ = 'attrition_alerts'
    id = db.Column(db.Integer, primary_key=True)
    alert_type = db.Column(db.String(64))
    group_name = db.Column(db.String(64))
    value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'group_name': self.group_name,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ModelMetrics(db.Model):
    __tablename__ = 'model_metrics'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall
        }
