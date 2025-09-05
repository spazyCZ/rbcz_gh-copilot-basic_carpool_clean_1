"""
Reservations API endpoints.

Handles CRUD operations for parking reservations.
"""
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date

from app.api import api_bp
from app.services import reservation_service


@api_bp.route('/reservations', methods=['GET'])
@login_required
def get_reservations():
    """
    Get reservations for the current user or all users (admin only).
    
    Query parameters:
    - include_cancelled: Include cancelled reservations (true/false)
    - start_date: Start date filter (YYYY-MM-DD)
    - end_date: End date filter (YYYY-MM-DD)
    - spot_id: Filter by specific spot
    - all_users: Get reservations for all users (admin only)
    
    :return: JSON response with reservations data
    """
    try:
        include_cancelled = request.args.get('include_cancelled', 'false').lower() == 'true'
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        spot_id = request.args.get('spot_id')
        all_users = request.args.get('all_users', 'false').lower() == 'true'
        
        # Check admin permission for all_users flag
        if all_users and not current_user.is_admin():
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'Admin privileges required to view all user reservations'
                }
            }), 403
        
        # Parse date parameters
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid start_date format. Use YYYY-MM-DD'
                    }
                }), 400
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'Invalid end_date format. Use YYYY-MM-DD'
                    }
                }), 400
        
        # Route to appropriate service method
        if start_date and end_date:
            # Get reservations by date range
            result = reservation_service.get_reservations_by_date_range(
                start_date=start_date,
                end_date=end_date,
                spot_id=spot_id
            )
        elif all_users:
            # Get upcoming reservations for all users (admin only)
            result = reservation_service.get_upcoming_reservations()
        else:
            # Get reservations for current user
            result = reservation_service.get_user_reservations(
                user_id=current_user.id,
                include_cancelled=include_cancelled
            )
        
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
        current_app.logger.error(f"Error in get_reservations endpoint: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch reservations'
            }
        }), 500


@api_bp.route('/reservations', methods=['POST'])
@login_required
def create_reservation():
    """
    Create a new parking reservation.
    
    Expected JSON payload:
    {
        "spot_id": "A1",
        "reservation_date": "2025-09-06",
        "name": "John Doe",
        "notes": "Optional notes"
    }
    
    :return: JSON response with created reservation data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body must contain JSON data'
                }
            }), 400
        
        # Extract and validate required fields
        spot_id = data.get('spot_id')
        reservation_date_str = data.get('reservation_date')
        name = data.get('name')
        notes = data.get('notes')
        
        if not spot_id:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'spot_id is required'
                }
            }), 400
        
        if not reservation_date_str:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'reservation_date is required'
                }
            }), 400
        
        if not name:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'name is required'
                }
            }), 400
        
        # Parse reservation date
        try:
            reservation_date = datetime.strptime(reservation_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid reservation_date format. Use YYYY-MM-DD'
                }
            }), 400
        
        # Create reservation via service
        result = reservation_service.create_reservation(
            user_id=current_user.id,
            spot_id=spot_id,
            reservation_date=reservation_date,
            name=name,
            notes=notes
        )
        
        if result['success']:
            return jsonify({
                'data': result
            }), 201
        else:
            # Map specific errors to HTTP status codes
            error_code = result.get('error', 'UNKNOWN_ERROR')
            status_code = 409 if error_code == 'RESERVATION_CONFLICT' else 400
            
            return jsonify({
                'error': {
                    'code': error_code,
                    'message': result.get('message', 'Unknown error')
                }
            }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error creating reservation: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to create reservation due to server error'
            }
        }), 500


@api_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@login_required
def get_reservation(reservation_id):
    """
    Get specific reservation details.
    
    :param reservation_id: Reservation ID
    :return: JSON response with reservation data
    """
    try:
        from app.models import Reservation
        
        reservation = Reservation.query.get(reservation_id)
        
        if not reservation:
            return jsonify({
                'error': {
                    'code': 'RESERVATION_NOT_FOUND',
                    'message': f'Reservation {reservation_id} not found'
                }
            }), 404
        
        # Check authorization (users can only see their own reservations, admins can see all)
        if reservation.user_id != current_user.id and not current_user.is_admin():
            return jsonify({
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': 'You can only view your own reservations'
                }
            }), 403
        
        return jsonify({
            'data': reservation.to_dict(include_relations=True)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error fetching reservation {reservation_id}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to fetch reservation details'
            }
        }), 500


@api_bp.route('/reservations/<int:reservation_id>', methods=['PATCH'])
@login_required
def update_reservation(reservation_id):
    """
    Update an existing reservation.
    
    Expected JSON payload:
    {
        "name": "New Name",
        "notes": "Updated notes"
    }
    
    :param reservation_id: Reservation ID
    :return: JSON response with updated reservation data
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body must contain JSON data'
                }
            }), 400
        
        # Extract update fields
        name = data.get('name')
        notes = data.get('notes')
        
        # Update reservation via service
        result = reservation_service.update_reservation(
            reservation_id=reservation_id,
            user_id=current_user.id,
            name=name,
            notes=notes
        )
        
        if result['success']:
            return jsonify({
                'data': result
            }), 200
        else:
            # Map specific errors to HTTP status codes
            error_code = result.get('error', 'UNKNOWN_ERROR')
            status_code = {
                'RESERVATION_NOT_FOUND': 404,
                'UNAUTHORIZED': 403,
                'RESERVATION_CANCELLED': 400
            }.get(error_code, 500)
            
            return jsonify({
                'error': {
                    'code': error_code,
                    'message': result.get('message', 'Unknown error')
                }
            }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error updating reservation {reservation_id}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to update reservation due to server error'
            }
        }), 500


@api_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
@login_required
def cancel_reservation(reservation_id):
    """
    Cancel an existing reservation.
    
    :param reservation_id: Reservation ID
    :return: JSON response with cancellation confirmation
    """
    try:
        # Cancel reservation via service
        result = reservation_service.cancel_reservation(
            reservation_id=reservation_id,
            user_id=current_user.id
        )
        
        if result['success']:
            return jsonify({
                'data': result
            }), 200
        else:
            # Map specific errors to HTTP status codes
            error_code = result.get('error', 'UNKNOWN_ERROR')
            status_code = {
                'RESERVATION_NOT_FOUND': 404,
                'UNAUTHORIZED': 403,
                'RESERVATION_ALREADY_CANCELLED': 400
            }.get(error_code, 500)
            
            return jsonify({
                'error': {
                    'code': error_code,
                    'message': result.get('message', 'Unknown error')
                }
            }), status_code
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling reservation {reservation_id}: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Failed to cancel reservation due to server error'
            }
        }), 500