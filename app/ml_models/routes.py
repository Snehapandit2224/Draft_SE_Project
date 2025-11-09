from flask import render_template
from . import ml_models

@ml_models.route('/')
def index():
    return render_template('ml_models/index.html')
