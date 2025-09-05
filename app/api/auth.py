from flask import request, jsonify
from flask_login import login_user, logout_user, login_required
from . import bp
from app.services import get_by_username


@bp.post('/auth/login')
def login():
    data = request.get_json() or {}
    user = get_by_username(data.get('username'))
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'message': 'logged_in'})
    return jsonify({'error': 'invalid credentials'}), 401


@bp.post('/auth/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'logged_out'})
