from flask import jsonify
from flask_jwt_extended import jwt_required
from . import alerts
from .. import db
from ..models import AttritionAlert

@alerts.route('/api/alerts', methods=['GET'])
@jwt_required()
def get_alerts():
    alerts = AttritionAlert.query.order_by(AttritionAlert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])
