from flask import jsonify, render_template
from app.utils.decorators import conditional_jwt_required, login_required
from . import alerts
from .. import db
from ..models import AttritionAlert

@alerts.route('/')
@login_required
def index():
    return render_template('alerts/index.html')

@alerts.route('/api/alerts', methods=['GET'])
@conditional_jwt_required()
def get_alerts():
    alerts = AttritionAlert.query.order_by(AttritionAlert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])
