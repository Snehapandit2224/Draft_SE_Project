from flask import Blueprint

exit_management = Blueprint('exit_management', __name__)

from . import routes
