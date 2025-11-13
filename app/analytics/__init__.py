from flask import Blueprint

analytics = Blueprint('analytics', __name__)

from . import routes, api, reports_api, data_issues_api
