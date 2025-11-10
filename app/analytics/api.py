from flask import jsonify, request, make_response
from . import analytics
from .. import db
from ..models import ExitFeedback, Employee, ExitReason
from sqlalchemy import func
from datetime import datetime
import io
import csv

@analytics.route('/api/reports/exit-reasons', methods=['GET'])
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
