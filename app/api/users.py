from flask import jsonify
from flask_login import login_required, current_user
from . import bp


@bp.get('/users/me')
@login_required
def me():
    return jsonify({'username': current_user.username, 'email': current_user.email, 'role': current_user.role})
