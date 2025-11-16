from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from config import config

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
bcrypt = Bcrypt()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    jwt.init_app(app)
    # init extensions
    # Parse CORS allowed origins (comma-separated or single)
    raw_origins = app.config.get('CORS_ALLOWED_ORIGINS', '*')
    if isinstance(raw_origins, str) and ',' in raw_origins:
        origins = [o.strip() for o in raw_origins.split(',') if o.strip()]
    else:
        origins = raw_origins
    cors.init_app(app, resources={r"/api/*": {"origins": origins}})
    bcrypt.init_app(app)

    from . import models

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .employees import employees as employees_blueprint
    app.register_blueprint(employees_blueprint, url_prefix='/employees')

    from .exit_management import exit_management as exit_management_blueprint
    app.register_blueprint(exit_management_blueprint, url_prefix='/exit')

    from .analytics import analytics as analytics_blueprint
    app.register_blueprint(analytics_blueprint, url_prefix='/analytics')

    from .ml_models import ml_models as ml_models_blueprint
    from .ml_models import api
    app.register_blueprint(ml_models_blueprint, url_prefix='/ml')

    from .alerts import alerts as alerts_blueprint
    app.register_blueprint(alerts_blueprint, url_prefix='/alerts')

    from .auth import auth as auth_blueprint
    # Register auth blueprint under /api/auth so endpoints become /api/auth/login etc.
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')

    from .health import health as health_blueprint
    app.register_blueprint(health_blueprint)

    from .errors import register_error_handlers
    register_error_handlers(app)

    # Enforce HTTPS in non-debug/non-testing environments
    from flask import request

    @app.before_request
    def enforce_https():
        if app.config.get('TESTING') or app.config.get('DEBUG'):
            return None
        # Allow turning off HTTPS enforcement (useful for tests that toggle TESTING)
        if not app.config.get('ENFORCE_HTTPS', True):
            return None
        # consider X-Forwarded-Proto header for proxy setups
        proto = request.headers.get('X-Forwarded-Proto', 'http')
        if proto != 'https' and not request.is_secure:
            return jsonify({'msg': 'HTTPS required'}), 403

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data.get("sub")
        # tokens carry subject as string (we create string identities); try to cast
        try:
            identity = int(identity)
        except Exception:
            pass
        return models.User.query.filter_by(id=identity).one_or_none()

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Signature verification failed"}), 401

    @jwt.expired_token_loader
    def expired_token_response(callback):
        return jsonify({"msg": "Token has expired"}), 401

    return app
