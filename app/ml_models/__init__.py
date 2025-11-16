from flask import Blueprint

ml_models = Blueprint('ml_models', __name__)

# Ensure submodules that register routes are imported when the package is imported
from . import routes, api