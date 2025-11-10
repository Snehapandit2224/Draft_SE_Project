from flask import request, jsonify
from . import exit_management
from .. import db
from ..models import ExitFeedback, Employee, ExitReason
from datetime import datetime

@exit_management.route('/api/exit-feedback', methods=['POST'])
def create_exit_feedback():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    required_fields = ['employee_id', 'exit_date', 'reason', 'feedback']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    employee = Employee.query.get(data['employee_id'])
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    try:
        exit_date = datetime.strptime(data['exit_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format for exit_date. Use YYYY-MM-DD.'}), 400

    try:
        reason = ExitReason(data['reason'])
    except ValueError:
        return jsonify({'error': 'Invalid reason. Must be one of: resignation, termination, retirement'}), 400

    feedback = ExitFeedback(
        employee_id=data['employee_id'],
        exit_date=exit_date,
        reason=reason,
        feedback=data['feedback']
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify(feedback.to_dict()), 201

@exit_management.route('/api/exit-feedback/<int:id>/complete', methods=['PATCH'])
def complete_exit_interview(id):
    feedback = ExitFeedback.query.get_or_404(id)
    feedback.interview_completed = True
    feedback.interview_date = datetime.utcnow()
    db.session.commit()
    return jsonify(feedback.to_dict())

@exit_management.route('/api/exit-feedback/pending', methods=['GET'])
def get_pending_exit_interviews():
    pending_feedback = ExitFeedback.query.filter_by(interview_completed=False).all()
    return jsonify([f.to_dict() for f in pending_feedback])
