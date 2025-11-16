from flask import render_template
from . import analytics
from ..utils.decorators import login_required

@analytics.route('/')
@login_required
def index():
    return render_template('analytics/index.html')

@analytics.route('/reports/exit-reasons')
@login_required
def exit_reasons_report():
    return render_template('analytics/exit-reasons.html')

@analytics.route('/reports/attrition')
@login_required
def attrition_report():
    return render_template('analytics/attrition-report.html')

@analytics.route('/reports/hotspots')
@login_required
def hotspots_report():
    return render_template('analytics/hotspots.html')
