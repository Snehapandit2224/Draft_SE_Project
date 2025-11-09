from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/health')
def health_check():
    return 'OK'
