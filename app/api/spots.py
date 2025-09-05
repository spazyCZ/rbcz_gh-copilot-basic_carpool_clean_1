"""
Parking spots API endpoints.

Handles CRUD operations and availability queries for parking spots.
"""
from flask import request, jsonify, current_app
from flask_login import login_required
from datetime import datetime, date

from app.api import api_bp
from app.services import spot_service


@api_bp.route('/spots', methods=['GET'])
@login_required
def get_spots():
    """
    Get list of parking spots with optional filtering.
    
    Query parameters:
    - date: Filter by availability on specific date (YYYY-MM-DD)
    - handicap_accessible: Filter by handicap accessibility (true/false)
    - electric_charging: Filter by electric charging capability (true/false)
    - search: Search query for location/description
    - location: Filter by specific location
    
    :return: JSON response with spots data
    """
    try:
        # Parse query parameters
        target_date_str = request.args.get('date')
        handicap_accessible = request.args.get('handicap_accessible')
        electric_charging = request.args.get('electric_charging')
        search_query = request.args.get('search', '').strip()
        location_filter = request.args.get('location', '').strip()
        
        # Convert and validate date parameter
        target_date = None
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }
                }), 400
        
        # Convert boolean parameters
        handicap_filter = None
        if handicap_accessible is not None:
            handicap_filter = handicap_accessible.lower() == 'true'
        
        charging_filter = None
        if electric_charging is not None:
            charging_filter = electric_charging.lower() == 'true'
        
        # Route to appropriate service method based on parameters
        if search_query:
            # Search spots by query
            filters = {}
            if handicap_filter is not None:
                filters['handicap_accessible'] = handicap_filter
            if charging_filter is not None:
                filters['electric_charging'] = charging_filter
            
            result = spot_service.search_spots(search_query, filters)
        elif location_filter:
            # Filter by location
            result = spot_service.get_spots_by_location(location_filter)
        elif target_date or handicap_filter is not None or charging_filter is not None:
            # Get available spots with filters
            result = spot_service.get_available_spots(
                target_date=target_date,
                handicap_accessible=handicap_filter,
                electric_charging=charging_filter
            )
        else:
            # Get all spots
            result = spot_service.get_all_spots()
        
        if result['success']:
            return jsonify({
                'data': result
            }), 200
        else:
            return jsonify({
                'error': {
                    'code': result.get('error', 'UNKNOWN_ERROR'),
                    'message': result.get('message', 'Unknown error')
                }
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error in get_spots endpoint: {e}")
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
    
    Query parameters:
    - include_reservations: Include upcoming reservations (true/false)
    - calendar_days: Number of days for availability calendar (default: 30)
    
    :param spot_id: Parking spot ID
    :return: JSON response with spot data
    """
    try:
        include_reservations = request.args.get('include_reservations', 'false').lower() == 'true'
        calendar_days = request.args.get('calendar_days', type=int)
        
        if calendar_days:
            # Get spot with availability calendar
            result = spot_service.get_spot_availability_calendar(
                spot_id=spot_id,
                days=min(calendar_days, 90)  # Limit to 90 days max
            )
        else:
            # Get basic spot details
            result = spot_service.get_spot_by_id(
                spot_id=spot_id,
                include_reservations=include_reservations
            )
        
        if result['success']:
            return jsonify({
                'data': result
            }), 200
        else:
            status_code = 404 if result.get('error') == 'SPOT_NOT_FOUND' else 500
            return jsonify({
                'error': {
                    'code': result.get('error', 'UNKNOWN_ERROR'),
                    'message': result.get('message', 'Unknown error')
                }
            }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error fetching spot {spot_id}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch parking spot details'
            }
        }), 500


@api_bp.route('/spots/statistics', methods=['GET'])
@login_required
def get_spots_statistics():
    """
    Get parking spots statistics.
    
    :return: JSON response with statistics data
    """
    try:
        result = spot_service.get_spots_statistics()
        
        if result['success']:
            return jsonify({
                'data': result['statistics']
            }), 200
        else:
            return jsonify({
                'error': {
                    'code': result.get('error', 'UNKNOWN_ERROR'),
                    'message': result.get('message', 'Unknown error')
                }
            }), 500
        
    except Exception as e:
        current_app.logger.error(f"Error getting spot statistics: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch spot statistics'
            }
        }), 500