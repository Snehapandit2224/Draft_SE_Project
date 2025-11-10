from flask import render_template
from . import analytics

@analytics.route('/')
def index():
    return render_template('analytics/index.html')

@analytics.route('/reports/exit-reasons')
def exit_reasons_report():
    return render_template('analytics/exit-reasons.html')

@analytics.route('/reports/attrition')
def attrition_report():
    return render_template('analytics/attrition-report.html')

@analytics.route('/reports/hotspots')
def hotspots_report():
    return render_template('analytics/hotspots.html')
