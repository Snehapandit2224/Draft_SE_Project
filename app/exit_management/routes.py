from flask import render_template
from . import exit_management

@exit_management.route('/')
def index():
    return render_template('exit_management/index.html')
