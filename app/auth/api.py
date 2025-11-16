from flask import request, jsonify, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies
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

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.form
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        response = redirect(url_for('main.index'))
        response.set_cookie('access_token_cookie', access_token)
        return response
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@auth.route('/logout')
def logout():
    response = redirect(url_for('auth.login'))
    unset_jwt_cookies(response)
    return response

@auth.route('/profile')
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict())

