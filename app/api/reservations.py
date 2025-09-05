"""
Reservations API endpoints (stub).

Handles CRUD operations for parking reservations.
"""
from flask import jsonify
from flask_login import login_required

from app.api import api_bp


@api_bp.route('/reservations', methods=['GET'])
@login_required
def get_reservations():
    """Get user reservations (stub implementation)."""
    return jsonify({
        'data': {
            'reservations': [],
            'message': 'Reservations endpoint - to be implemented'
        }
    }), 200


@api_bp.route('/reservations', methods=['POST'])
@login_required
def create_reservation():
    """Create new reservation (stub implementation)."""
    return jsonify({
        'data': {
            'message': 'Create reservation endpoint - to be implemented'
        }
    }), 200