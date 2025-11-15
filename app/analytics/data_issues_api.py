from flask import jsonify
from flask_jwt_extended import jwt_required
from app.analytics import analytics
from app.models import DataIssue

@analytics.route('/api/data/issues', methods=['GET'])
@jwt_required()
def get_data_issues():
    issues = DataIssue.query.all()
    return jsonify([issue.to_dict() for issue in issues])
