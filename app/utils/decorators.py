from functools import wraps
from flask import request, jsonify
import re

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
