from flask import Blueprint, render_template, redirect, url_for
from flask_jwt_extended import jwt_required

main = Blueprint('main', __name__)

@main.route('/')
@jwt_required()
def index():
    return render_template('index.html')

@main.route('/health')
def health_check():
    return 'OK'
