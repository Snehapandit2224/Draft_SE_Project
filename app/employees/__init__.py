from flask import Blueprint

employees = Blueprint('employees', __name__)

from . import routes
