from flask import render_template
from . import analytics

@analytics.route('/')
def index():
    return render_template('analytics/index.html')

@analytics.route('/reports/exit-reasons')
def exit_reasons_report():
    return render_template('analytics/exit-reasons.html')
