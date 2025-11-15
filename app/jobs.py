from apscheduler.schedulers.background import BackgroundScheduler
from .analytics.api import calculate_attrition_rates
from . import db
from .models import AttritionAlert, Employee, ExitFeedback, ModelMetrics, DataIssue
import smtplib
from email.mime.text import MIMEText
import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score
from datetime import datetime
from . import create_app

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'attrition_model.pkl')
TRANSFORMER_PATH = os.path.join(MODEL_DIR, 'transformer.pkl')

def preprocess_data(df):
    # Calculate tenure
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['tenure_days'] = (datetime.now() - df['hire_date']).dt.days
    df['tenure_years'] = df['tenure_days'] / 365.25

    # Drop unnecessary columns
    df = df.drop(columns=['hire_date', 'tenure_days'])

    return df

from app.ml_models.training import retrain_model as train_attrition_model

def retrain_model_job():
    """
    Job to retrain the model.
    """
    # Avoid running the retrain job in testing environments to prevent
    # accidental connections to production databases during test runs.
    config_name = os.getenv('FLASK_CONFIG') or 'default'
    if config_name == 'testing':
        return

    app = create_app(config_name)
    with app.app_context():
        try:
            train_attrition_model()
        except Exception:
            # Swallow exceptions to avoid crashing scheduler; errors will be
            # visible in logs during manual runs.
            return



def check_attrition_hotspots(app):
    """Checks for attrition hotspots and creates alerts."""
    with app.app_context():
        attrition_data = calculate_attrition_rates('department')
        
        df = pd.DataFrame(attrition_data)
        df['period'] = pd.to_datetime(df['period'])
        df = df.set_index(['period', 'group'])['attrition_rate'].unstack()

        # Calculate 3-month rolling average
        rolling_avg = df.rolling(window=3).mean()

        # Find hotspots
        hotspots = rolling_avg[rolling_avg > 15]
        
        for group in hotspots.columns:
            for period, value in hotspots[group].items():
                if pd.notna(value):
                    # Check if an alert for this group and period already exists
                    exists = AttritionAlert.query.filter_by(
                        alert_type='attrition_hotspot',
                        group_name=group,
                        value=value
                    ).first()

                    if not exists:
                        alert = AttritionAlert(
                            alert_type='attrition_hotspot',
                            group_name=group,
                            value=value
                        )
                        db.session.add(alert)
                        db.session.commit()
                        send_email_alert(alert)

def find_data_discrepancies(app):
    """Finds discrepancies between employees and exit_feedback tables."""
    with app.app_context():
        # Find inactive employees without exit feedback
        inactive_employees = Employee.query.filter_by(is_active=False).all()
        for emp in inactive_employees:
            feedback = ExitFeedback.query.filter_by(employee_id=emp.id).first()
            if not feedback:
                issue = DataIssue(
                    issue_type='Missing Exit Feedback',
                    entity_type='Employee',
                    entity_id=emp.id,
                    description=f'Inactive employee {emp.first_name} {emp.last_name} has no exit feedback.'
                )
                db.session.add(issue)

        # Find exit feedback for active employees
        active_employees_with_feedback = db.session.query(Employee, ExitFeedback).join(ExitFeedback).filter(Employee.is_active==True).all()
        for emp, feedback in active_employees_with_feedback:
            issue = DataIssue(
                issue_type='Exit Feedback for Active Employee',
                entity_type='Employee',
                entity_id=emp.id,
                description=f'Active employee {emp.first_name} {emp.last_name} has exit feedback.'
            )
            db.session.add(issue)
        
        db.session.commit()

def send_email_alert(alert):
    """Simulates sending an email alert."""
    msg = MIMEText(f"Attrition hotspot detected!\n\nGroup: {alert.group_name}\nAttrition Rate: {alert.value:.2f}%")
    msg['Subject'] = 'Attrition Hotspot Alert'
    msg['From'] = 'hr-alerts@example.com'
    msg['To'] = 'hr-manager@example.com'

    # This is a simulation, so we'll just print the email to the console
    print("---- EMAIL SIMULATION ----")
    print(msg.as_string())
    print("--------------------------")

def init_scheduler(app):
    """Initializes and starts the scheduler."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_attrition_hotspots, trigger="interval", days=1, args=[app])
    scheduler.add_job(func=train_attrition_model, trigger="interval", days=1)
    scheduler.add_job(func=find_data_discrepancies, trigger="interval", days=1, args=[app])
    scheduler.start()

