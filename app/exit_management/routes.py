from flask import render_template
from . import exit_management
from ..utils.decorators import login_required

@exit_management.route('/')
@login_required
def index():
    return render_template('exit_management/index.html')
