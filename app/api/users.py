"""
Users API endpoints (stub).

Handles user profile and management operations.
"""
from flask import jsonify
from flask_login import login_required, current_user

from app.api import api_bp


@api_bp.route('/users/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current user profile."""
    return jsonify({
        'data': current_user.to_dict()
    }), 200