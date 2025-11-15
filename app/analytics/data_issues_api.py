from flask import jsonify
from app.utils.decorators import conditional_jwt_required
from app.analytics import analytics
from app.models import DataIssue

@analytics.route('/api/data/issues', methods=['GET'])
@conditional_jwt_required()
def get_data_issues():
    issues = DataIssue.query.all()
    return jsonify([issue.to_dict() for issue in issues])
