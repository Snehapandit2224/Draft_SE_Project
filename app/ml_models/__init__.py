from flask import Blueprint

ml_models = Blueprint('ml_models', __name__)

from . import routes
