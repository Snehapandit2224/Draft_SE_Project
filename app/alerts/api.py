from flask import jsonify
from . import alerts
from .. import db
from ..models import AttritionAlert

@alerts.route('/api/alerts', methods=['GET'])
def get_alerts():
    alerts = AttritionAlert.query.order_by(AttritionAlert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])
