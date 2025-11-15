from flask import request, jsonify
from app.utils.decorators import conditional_jwt_required
from . import exit_management
from .. import db
from ..models import ExitFeedback, Employee, ExitReason
from datetime import datetime

from app.utils.decorators import validate_input

@exit_management.route('/api/exit-feedback', methods=['POST'])
@conditional_jwt_required()
@validate_input(required_fields=['employee_id', 'exit_date', 'reason', 'feedback'])
def create_exit_feedback(data):
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
@conditional_jwt_required()
def complete_exit_interview(id):
    feedback = ExitFeedback.query.get_or_404(id)
    feedback.interview_completed = True
    feedback.interview_date = datetime.utcnow()
    db.session.commit()
    return jsonify(feedback.to_dict())

@exit_management.route('/api/exit-feedback/pending', methods=['GET'])
@conditional_jwt_required()
def get_pending_exit_interviews():
    pending_feedback = ExitFeedback.query.filter_by(interview_completed=False).all()
    return jsonify([f.to_dict() for f in pending_feedback])
