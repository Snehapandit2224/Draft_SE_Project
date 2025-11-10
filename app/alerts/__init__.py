from flask import Blueprint

alerts = Blueprint('alerts', __name__)

from . import api
