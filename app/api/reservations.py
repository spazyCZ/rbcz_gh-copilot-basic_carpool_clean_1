from datetime import datetime
from flask import request, jsonify
from . import bp
from app.services import list_reservations, create_reservation


@bp.get('/reservations')
def get_reservations():
    reservations = list_reservations()
    return jsonify([
        {
            'id': r.id,
            'spot_id': r.spot_id,
            'name': r.name,
            'reservation_date': r.reservation_date.isoformat(),
        }
        for r in reservations
    ])


@bp.post('/reservations')
def add_reservation():
    data = request.get_json() or {}
    try:
        reservation = create_reservation(
            data['spot_id'],
            data['name'],
            datetime.fromisoformat(data['reservation_date']).date(),
        )
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 409
    return jsonify(
        {
            'id': reservation.id,
            'spot_id': reservation.spot_id,
            'name': reservation.name,
            'reservation_date': reservation.reservation_date.isoformat(),
        }
    ), 201
