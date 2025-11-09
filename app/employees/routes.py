from flask import render_template
from . import employees

@employees.route('/')
def index():
    return render_template('employees/index.html')
