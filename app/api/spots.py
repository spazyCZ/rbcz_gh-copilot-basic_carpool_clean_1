from flask import request, jsonify
from . import bp
from app.services import list_spots, create_spot


@bp.get('/spots')
def get_spots():
    spots = list_spots()
    return jsonify([
        {'id': s.id, 'status': s.status, 'location': s.location}
        for s in spots
    ])


@bp.post('/spots')
def add_spot():
    data = request.get_json() or {}
    spot = create_spot(data['id'], data.get('status', 'free'), data.get('location'))
    return jsonify({'id': spot.id, 'status': spot.status, 'location': spot.location}), 201
