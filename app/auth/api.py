from flask import request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models import User
from app.auth import auth
from app.utils.decorators import validate_input

@auth.route('/register', methods=['POST'])
@validate_input(required_fields=['username', 'password'])
def register(data):
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
@validate_input(required_fields=['username', 'password'])
def login(data):
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401
