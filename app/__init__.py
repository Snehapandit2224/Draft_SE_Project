from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

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
    app.register_blueprint(ml_models_blueprint, url_prefix='/ml')

    return app
