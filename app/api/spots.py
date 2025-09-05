"""
Parking spots API endpoints.

Handles CRUD operations and availability queries for parking spots.
"""
from flask import request, jsonify, current_app
from flask_login import login_required
from datetime import datetime, date

from app.api import api_bp
from app.models import ParkingSpot


@api_bp.route('/spots', methods=['GET'])
@login_required
def get_spots():
    """
    Get list of parking spots with optional filtering.
    
    Query parameters:
    - date: Filter by availability on specific date (YYYY-MM-DD)
    - handicap_accessible: Filter by handicap accessibility (true/false)
    - electric_charging: Filter by electric charging capability (true/false)
    
    :return: JSON response with spots data
    """
    try:
        # Parse query parameters
        target_date = request.args.get('date')
        handicap_accessible = request.args.get('handicap_accessible')
        electric_charging = request.args.get('electric_charging')
        
        # Convert string parameters to appropriate types
        if target_date:
            try:
                target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }
                }), 400
        else:
            target_date = date.today()
        
        handicap_filter = None
        if handicap_accessible is not None:
            handicap_filter = handicap_accessible.lower() == 'true'
        
        charging_filter = None
        if electric_charging is not None:
            charging_filter = electric_charging.lower() == 'true'
        
        # Get available spots for the date
        spots = ParkingSpot.find_available_spots(
            reservation_date=target_date,
            handicap_accessible=handicap_filter,
            electric_charging=charging_filter
        )
        
        spots_data = [spot.to_dict() for spot in spots]
        
        return jsonify({
            'data': {
                'spots': spots_data,
                'count': len(spots_data),
                'date': target_date.isoformat()
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching spots: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch parking spots'
            }
        }), 500


@api_bp.route('/spots/<string:spot_id>', methods=['GET'])
@login_required
def get_spot(spot_id):
    """
    Get specific parking spot details.
    
    :param spot_id: Parking spot ID
    :return: JSON response with spot data
    """
    try:
        spot = ParkingSpot.query.get(spot_id)
        
        if not spot:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': f'Parking spot {spot_id} not found'
                }
            }), 404
        
        return jsonify({
            'data': spot.to_dict(include_reservations=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching spot {spot_id}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch parking spot details'
            }
        }), 500