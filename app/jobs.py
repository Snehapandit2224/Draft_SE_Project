from apscheduler.schedulers.background import BackgroundScheduler
from .analytics.api import calculate_attrition_rates
from . import db
from .models import AttritionAlert, Employee, ExitFeedback, ModelMetrics
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
    app = create_app('default')
    with app.app_context():
        train_attrition_model()



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
    scheduler.start()
