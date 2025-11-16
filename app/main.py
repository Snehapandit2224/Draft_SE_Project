from flask import Blueprint, render_template, redirect, url_for, request
from app.utils.decorators import login_required

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html')

@main.route('/health')
def health_check():
    return 'OK'
