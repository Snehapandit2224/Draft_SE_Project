from flask import jsonify, request, make_response
from flask_jwt_extended import jwt_required
from . import analytics
from .. import db
from ..models import ExitFeedback, Employee, ExitReason
from sqlalchemy import func
from datetime import datetime
import io
import csv

@analytics.route('/api/reports/exit-reasons', methods=['GET'])
@jwt_required()
def get_exit_reasons_report():
    query = db.session.query(
        ExitFeedback.reason,
        func.count(ExitFeedback.id).label('count')
    ).join(Employee).group_by(ExitFeedback.reason)

    # Filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    department = request.args.get('department')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(ExitFeedback.exit_date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(ExitFeedback.exit_date <= end_date)
    if department:
        query = query.filter(Employee.department == department)

    results = query.all()
    total = sum([r.count for r in results])
    
    report = [
        {
            'reason': r.reason.value if r.reason else 'Unknown',
            'count': r.count,
            'percentage': (r.count / total) * 100 if total > 0 else 0
        } for r in results
    ]

    return jsonify(report)

@analytics.route('/api/reports/exit-reasons/export', methods=['GET'])
@jwt_required()
def export_exit_reasons_report():
    query = db.session.query(
        ExitFeedback.reason,
        func.count(ExitFeedback.id).label('count')
    ).join(Employee).group_by(ExitFeedback.reason)

    # Filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    department = request.args.get('department')

    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(ExitFeedback.exit_date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(ExitFeedback.exit_date <= end_date)
    if department:
        query = query.filter(Employee.department == department)

    results = query.all()
    total = sum([r.count for r in results])
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Reason', 'Count', 'Percentage'])

    for r in results:
        writer.writerow([
            r.reason.value if r.reason else 'Unknown',
            r.count,
            (r.count / total) * 100 if total > 0 else 0
        ])

    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=exit_reasons_report.csv"
    response.headers["Content-type"] = "text/csv"
    return response

from flask import jsonify, request, make_response
from . import analytics
from .. import db
from ..models import ExitFeedback, Employee, ExitReason
from sqlalchemy import func
from datetime import datetime
import io
import csv
import pandas as pd

def calculate_attrition_rates(group_by='month'):
    # Get all employees and their exit dates
    employees_results = db.session.query(Employee).all()
    exits_results = db.session.query(ExitFeedback).all()
    employees = pd.DataFrame([e.to_dict() for e in employees_results])
    exits = pd.DataFrame([e.to_dict() for e in exits_results])

    # Merge the two dataframes
    df = pd.merge(employees, exits, left_on='id', right_on='employee_id', how='left')
    
    # Convert dates to datetime objects
    df['hire_date'] = pd.to_datetime(df['hire_date'])
    df['exit_date'] = pd.to_datetime(df['exit_date'])

    # Set the period for the report
    start_date = df['hire_date'].min()
    end_date = df['exit_date'].max()
    if pd.isna(end_date):
        end_date = datetime.now()

    # Create a date range for the report
    date_range = pd.date_range(start=start_date, end=end_date, freq='MS')

    results = []
    for period_start in date_range:
        period_end = period_start + pd.offsets.MonthEnd(1)

        # Filter employees who were active at the start of the period
        active_at_start = df[
            (df['hire_date'] < period_start) &
            ((df['exit_date'].isnull()) | (df['exit_date'] >= period_start))
        ]
        
        # Filter employees who left during the period
        left_during_period = df[
            (df['exit_date'] >= period_start) &
            (df['exit_date'] <= period_end)
        ]

        if group_by == 'department':
            groups = df['department'].unique()
        elif group_by == 'position':
            groups = df['position'].unique()
        else:
            groups = ['Overall']

        for group in groups:
            active_in_group = active_at_start
            left_in_group = left_during_period

            if group != 'Overall':
                active_in_group = active_at_start[active_at_start[group_by] == group]
                left_in_group = left_during_period[left_during_period[group_by] == group]

            num_active = len(active_in_group)
            num_left = len(left_in_group)
            
            attrition_rate = (num_left / num_active) * 100 if num_active > 0 else 0

            results.append({
                'period': period_start.strftime('%Y-%m'),
                'group': group,
                'active_employees': num_active,
                'left_employees': num_left,
                'attrition_rate': attrition_rate
            })
    return results

@analytics.route('/api/reports/attrition', methods=['GET'])
@jwt_required()
def get_attrition_report():
    group_by = request.args.get('group_by', 'month')
    results = calculate_attrition_rates(group_by)
    return jsonify(results)

@analytics.route('/api/analytics/hotspots', methods=['GET'])
@jwt_required()
def get_attrition_hotspots():
    group_by = request.args.get('group_by', 'department') # department or position
    attrition_data = calculate_attrition_rates(group_by)
    
    df = pd.DataFrame(attrition_data)
    df['period'] = pd.to_datetime(df['period'])
    df = df.set_index(['period', 'group'])['attrition_rate'].unstack()

    # Calculate 3-month rolling average
    rolling_avg = df.rolling(window=3).mean()

    # Find hotspots
    hotspots = rolling_avg[rolling_avg > 15]
    
    # Format for heatmap
    heatmap_data = []
    for group in hotspots.columns:
        for period, value in hotspots[group].items():
            if pd.notna(value):
                heatmap_data.append({
                    'group': group,
                    'period': period.strftime('%Y-%m'),
                    'attrition_rate': value
                })

    return jsonify(heatmap_data)
