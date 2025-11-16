from functools import wraps
from flask import request, jsonify, redirect, url_for
import re
from flask import current_app
from flask_jwt_extended import jwt_required

def validate_input(required_fields=[], email_fields=[], salary_fields=[]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON'}), 400

            errors = {}

            # Required fields validation
            for field in required_fields:
                if field not in data:
                    errors[field] = f'{field} is required'

            if errors:
                return jsonify({'errors': errors}), 400

            # Email format validation
            for field in email_fields:
                if field in data:
                    if not re.match(r'[^@]+@[^@]+\.[^@]+', data[field]):
                        errors[field] = f'Invalid email format for {field}'

            # Salary range validation
            for field in salary_fields:
                if field in data:
                    try:
                        salary = float(data[field])
                        if not 30000 <= salary <= 200000:
                            errors[field] = f'{field} must be between 30,000 and 200,000'
                    except (ValueError, TypeError):
                        errors[field] = f'{field} must be a valid number'

            if errors:
                return jsonify({'errors': errors}), 400

            return f(data, *args, **kwargs)
        return decorated_function
    return decorator


def conditional_jwt_required():
    """Decorator factory that applies JWT protection when not in TESTING mode.

    Use as `@conditional_jwt_required()` on view functions. In testing mode it
    will bypass JWT checks so tests can call endpoints without tokens.
    """
    def decorator(fn):
        protected = jwt_required()(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if current_app.config.get('TESTING'):
                return fn(*args, **kwargs)
            return protected(*args, **kwargs)

        return wrapper

    return decorator


def login_required(f):
    """Decorator that requires user to be logged in.
    
    For HTML requests, redirects to login page.
    For API requests, returns 401 error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            from flask_jwt_extended import verify_jwt_in_request
            verify_jwt_in_request()
        except Exception:
            # Check if this is an API request or HTML request
            is_api = request.path.startswith('/api/')
            json_quality = request.accept_mimetypes.quality('application/json') or 0
            html_quality = request.accept_mimetypes.quality('text/html') or 0
            
            if is_api or json_quality > html_quality:
                return jsonify({'msg': 'Missing or invalid authentication'}), 401
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

