from apscheduler.schedulers.background import BackgroundScheduler
from .analytics.api import calculate_attrition_rates
from . import db
from .models import AttritionAlert
import smtplib
from email.mime.text import MIMEText
import pandas as pd

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
    scheduler.start()
