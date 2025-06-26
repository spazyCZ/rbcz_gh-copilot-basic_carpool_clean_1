"""
API views and routes for the carpool application.

This module contains the API blueprint with JSON endpoints for AJAX calls,
data visualization, and mobile/external integrations.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.carpool import Carpool
from carpool.models.action import Action
from carpool.services.reservation_service import ReservationService
from carpool.services.carpool_service import CarpoolService
from carpool.services.admin_service import AdminService

# Create API blueprint
api_bp = Blueprint('api', __name__)


@api_bp.route('/dashboard-stats')
@login_required
def dashboard_stats():
    """
    API endpoint for dashboard statistics.
    
    :return: JSON response with dashboard statistics
    """
    try:
        # Get reservation statistics
        reservation_stats = ReservationService.get_reservation_statistics()
        
        # Get carpool statistics
        carpool_stats = CarpoolService.get_carpool_statistics()
        
        # Get user-specific statistics
        user_reservations = len(ReservationService.get_user_reservations(current_user, include_past=False))
        user_carpools = len(CarpoolService.get_user_carpools(current_user, include_past=False))
        
        return jsonify({
            'success': True,
            'data': {
                'reservations': reservation_stats,
                'carpools': carpool_stats,
                'user': {
                    'reservations': user_reservations,
                    'carpools': user_carpools
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching dashboard stats: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500


@api_bp.route('/available-spots/<date_str>')
@login_required
def available_spots(date_str):
    """
    API endpoint for available parking spots on a specific date.
    
    :param date_str: Date string in YYYY-MM-DD format
    :return: JSON response with available spots
    """
    try:
        # Parse the date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get available spots for the date
        spots = ReservationService.get_available_spots_for_date(target_date)
        
        # Convert to JSON format
        spots_data = [spot.to_dict() for spot in spots]
        
        return jsonify({
            'success': True,
            'date': date_str,
            'available_spots': spots_data,
            'count': len(spots_data)
        })
        
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    except Exception as e:
        current_app.logger.error(f'Error fetching available spots: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch available spots'}), 500


@api_bp.route('/reservations-chart-data')
@login_required
def reservations_chart_data():
    """
    API endpoint for reservations chart data (last 7 days).
    
    :return: JSON response with chart data
    """
    try:
        # Get the last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Get daily reservation counts
        daily_counts = {}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            count = Reservation.query.filter_by(reservation_date=current_date).count()
            daily_counts[current_date.strftime('%Y-%m-%d')] = count
        
        return jsonify({
            'success': True,
            'labels': list(daily_counts.keys()),
            'data': list(daily_counts.values()),
            'title': 'Reservations (Last 7 Days)'
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching reservations chart data: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch chart data'}), 500


@api_bp.route('/carpools-chart-data')
@login_required
def carpools_chart_data():
    """
    API endpoint for carpools chart data (next 7 days).
    
    :return: JSON response with chart data
    """
    try:
        # Get the next 7 days
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
        
        # Get daily carpool counts
        daily_counts = {}
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            next_date = current_date + timedelta(days=1)
            
            count = Carpool.query.filter(
                Carpool.departure_time >= current_date,
                Carpool.departure_time < next_date
            ).count()
            
            daily_counts[current_date.strftime('%Y-%m-%d')] = count
        
        return jsonify({
            'success': True,
            'labels': list(daily_counts.keys()),
            'data': list(daily_counts.values()),
            'title': 'Carpools (Next 7 Days)'
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching carpools chart data: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch chart data'}), 500


@api_bp.route('/carpool/<int:carpool_id>/join', methods=['POST'])
@login_required
def join_carpool(carpool_id):
    """
    API endpoint for joining a carpool trip.
    
    :param carpool_id: ID of the carpool to join
    :return: JSON response with success status
    """
    try:
        carpool = CarpoolService.get_carpool_by_id(carpool_id)
        
        if not carpool:
            return jsonify({'success': False, 'error': 'Carpool not found'}), 404
        
        # Check if user can join
        if not carpool.can_join():
            return jsonify({'success': False, 'error': 'Cannot join this carpool'}), 400
        
        # Join the carpool
        success = CarpoolService.join_carpool(carpool, current_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully joined {carpool.name}',
                'available_seats': carpool.available_seats()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to join carpool'}), 400
            
    except Exception as e:
        current_app.logger.error(f'Error joining carpool: {e}')
        return jsonify({'success': False, 'error': 'An error occurred'}), 500


@api_bp.route('/carpool/<int:carpool_id>/leave', methods=['POST'])
@login_required
def leave_carpool(carpool_id):
    """
    API endpoint for leaving a carpool trip.
    
    :param carpool_id: ID of the carpool to leave
    :return: JSON response with success status
    """
    try:
        carpool = CarpoolService.get_carpool_by_id(carpool_id)
        
        if not carpool:
            return jsonify({'success': False, 'error': 'Carpool not found'}), 404
        
        # Leave the carpool
        success = CarpoolService.leave_carpool(carpool, current_user)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully left {carpool.name}',
                'available_seats': carpool.available_seats()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to leave carpool'}), 400
            
    except Exception as e:
        current_app.logger.error(f'Error leaving carpool: {e}')
        return jsonify({'success': False, 'error': 'An error occurred'}), 500


@api_bp.route('/admin/activity-chart-data')
@login_required
def admin_activity_chart_data():
    """
    API endpoint for admin activity chart data.
    
    :return: JSON response with activity chart data
    """
    try:
        # Check admin permissions
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        days = int(request.args.get('days', 7))
        chart_data = AdminService.get_activity_chart_data(days=days)
        
        return jsonify({
            'success': True,
            'labels': chart_data['labels'],
            'data': chart_data['data'],
            'title': f'System Activity (Last {days} Days)'
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching admin chart data: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch chart data'}), 500


@api_bp.route('/admin/system-stats')
@login_required
def admin_system_stats():
    """
    API endpoint for admin system statistics.
    
    :return: JSON response with system statistics
    """
    try:
        # Check admin permissions
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        stats = AdminService.get_system_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching system stats: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch statistics'}), 500


@api_bp.route('/quick-reservation', methods=['POST'])
@login_required
def quick_reservation():
    """
    API endpoint for creating quick reservations for today.
    
    :return: JSON response with reservation status
    """
    try:
        if not current_user.can_make_reservation():
            return jsonify({'success': False, 'error': 'You do not have permission to make reservations'}), 403
        
        data = request.get_json()
        name = data.get('name', '').strip()
        spot_id = data.get('spot_id', '').strip()
        
        if not name or not spot_id:
            return jsonify({'success': False, 'error': 'Name and spot ID are required'}), 400
        
        # Create reservation for today
        reservation = ReservationService.create_reservation(
            user=current_user,
            spot_id=spot_id,
            name=name,
            reservation_date=date.today()
        )
        
        if reservation:
            return jsonify({
                'success': True,
                'message': f'Reservation created for spot {spot_id}',
                'reservation': reservation.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to create reservation'}), 400
            
    except Exception as e:
        current_app.logger.error(f'Error creating quick reservation: {e}')
        return jsonify({'success': False, 'error': 'An error occurred'}), 500


@api_bp.route('/user-activity')
@login_required
def user_activity():
    """
    API endpoint for user's recent activity.
    
    :return: JSON response with user activity
    """
    try:
        # Get user's recent actions
        recent_actions = Action.query.filter_by(username=current_user.username).order_by(Action.timestamp.desc()).limit(10).all()
        
        # Convert to JSON format
        actions_data = [action.to_dict() for action in recent_actions]
        
        return jsonify({
            'success': True,
            'data': actions_data
        })
        
    except Exception as e:
        current_app.logger.error(f'Error fetching user activity: {e}')
        return jsonify({'success': False, 'error': 'Failed to fetch activity'}), 500


# Dashboard API endpoints for real-time updates and charts

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_real_stats():
    """
    Real-time dashboard statistics endpoint.
    
    :return: JSON response with current dashboard statistics
    """
    try:
        from carpool.extensions import db
        from sqlalchemy import func
        
        # Get current statistics
        total_reservations = Reservation.query.count()
        active_carpools = Carpool.query.filter(
            Carpool.departure_time > datetime.now()
        ).count()
        available_spots = ParkingSpot.query.filter_by(status='available').count()
        system_users = User.query.count()
        
        # Calculate utilization percentage
        total_spots = ParkingSpot.query.count()
        reserved_spots = ParkingSpot.query.filter_by(status='reserved').count()
        utilization_percentage = (reserved_spots / total_spots * 100) if total_spots > 0 else 0
        
        return jsonify({
            'success': True,
            'total_reservations': total_reservations,
            'active_carpools': active_carpools,
            'available_spots': available_spots,
            'system_users': system_users,
            'utilization_percentage': round(utilization_percentage, 1)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dashboard/reservations-trend')
@login_required
def reservations_trend():
    """
    Get reservations trend data for chart.
    
    :return: JSON response with trend data
    """
    try:
        from carpool.extensions import db
        from sqlalchemy import func
        
        # Get last 7 days of reservations
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Query reservations by date
        reservations_by_date = db.session.query(
            func.date(Reservation.created_at).label('date'),
            func.count(Reservation.id).label('count')
        ).filter(
            func.date(Reservation.created_at) >= start_date,
            func.date(Reservation.created_at) <= end_date
        ).group_by(
            func.date(Reservation.created_at)
        ).all()
        
        # Create data structure for chart
        labels = []
        values = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime('%a'))
            
            # Find count for this date
            count = 0
            for res_date, res_count in reservations_by_date:
                if res_date == current_date:
                    count = res_count
                    break
            values.append(count)
        
        return jsonify({
            'success': True,
            'labels': labels,
            'values': values
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching reservations trend: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dashboard/parking-utilization')
@login_required
def parking_utilization():
    """
    Get parking utilization data for chart.
    
    :return: JSON response with utilization data
    """
    try:
        # Get spot counts by status
        available_count = ParkingSpot.query.filter_by(status='available').count()
        reserved_count = ParkingSpot.query.filter_by(status='reserved').count()
        maintenance_count = ParkingSpot.query.filter_by(status='maintenance').count()
        
        return jsonify({
            'success': True,
            'labels': ['Available', 'Reserved', 'Maintenance'],
            'values': [available_count, reserved_count, maintenance_count]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching parking utilization: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dashboard/carpool-activity')
@login_required
def carpool_activity():
    """
    Get carpool activity data for chart.
    
    :return: JSON response with carpool activity data
    """
    try:
        from carpool.extensions import db
        from sqlalchemy import func
        
        # Get last 7 days of carpool activity
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Query carpools by creation date
        carpools_by_date = db.session.query(
            func.date(Carpool.created_at).label('date'),
            func.count(Carpool.id).label('count')
        ).filter(
            func.date(Carpool.created_at) >= start_date,
            func.date(Carpool.created_at) <= end_date
        ).group_by(
            func.date(Carpool.created_at)
        ).all()
        
        # Create data structure for chart
        labels = []
        values = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime('%a'))
            
            # Find count for this date
            count = 0
            for carpool_date, carpool_count in carpools_by_date:
                if carpool_date == current_date:
                    count = carpool_count
                    break
            values.append(count)
        
        return jsonify({
            'success': True,
            'labels': labels,
            'values': values
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching carpool activity: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dashboard/weekly-stats')
@login_required
def weekly_stats():
    """
    Get weekly statistics for combined chart.
    
    :return: JSON response with weekly statistics
    """
    try:
        from carpool.extensions import db
        from sqlalchemy import func
        
        # Get last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6)
        
        # Query reservations and carpools by date
        reservations_by_date = db.session.query(
            func.date(Reservation.created_at).label('date'),
            func.count(Reservation.id).label('count')
        ).filter(
            func.date(Reservation.created_at) >= start_date,
            func.date(Reservation.created_at) <= end_date
        ).group_by(
            func.date(Reservation.created_at)
        ).all()
        
        carpools_by_date = db.session.query(
            func.date(Carpool.created_at).label('date'),
            func.count(Carpool.id).label('count')
        ).filter(
            func.date(Carpool.created_at) >= start_date,
            func.date(Carpool.created_at) <= end_date
        ).group_by(
            func.date(Carpool.created_at)
        ).all()
        
        # Create data structure for chart
        labels = []
        reservations = []
        carpools = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime('%a'))
            
            # Find reservation count for this date
            res_count = 0
            for res_date, count in reservations_by_date:
                if res_date == current_date:
                    res_count = count
                    break
            reservations.append(res_count)
            
            # Find carpool count for this date
            carpool_count = 0
            for carpool_date, count in carpools_by_date:
                if carpool_date == current_date:
                    carpool_count = count
                    break
            carpools.append(carpool_count)
        
        return jsonify({
            'success': True,
            'labels': labels,
            'reservations': reservations,
            'carpools': carpools
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching weekly stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/dashboard/recent-activity')
@login_required
def recent_activity():
    """
    Get recent activity for dashboard feed.
    
    :return: JSON response with recent activities
    """
    try:
        # Get last 10 actions
        recent_actions = Action.query.order_by(
            Action.timestamp.desc()
        ).limit(10).all()
        
        activities = []
        for action in recent_actions:
            activity_type = 'system'
            if 'reservation' in action.action_type:
                activity_type = 'reservation'
            elif 'carpool' in action.action_type:
                activity_type = 'carpool'
            elif 'user' in action.action_type:
                activity_type = 'user'
            elif 'admin' in action.action_type:
                activity_type = 'admin'
            
            activities.append({
                'type': activity_type,
                'description': action.details or f"{action.username} performed {action.action_type}",
                'timestamp': action.timestamp.isoformat(),
                'username': action.username
            })
        
        return jsonify(activities)
        
    except Exception as e:
        current_app.logger.error(f"Error fetching recent activity: {e}")
        return jsonify([]), 500

# Health check and utility endpoints

@api_bp.route('/health-check')
def health_check():
    """
    Health check endpoint for monitoring.
    
    :return: JSON response with health status
    """
    try:
        from carpool.extensions import db
        
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
        
    except Exception as e:
        current_app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/error-report', methods=['POST'])
def error_report():
    """
    Endpoint for submitting error reports.
    
    :return: JSON response indicating success/failure
    """
    try:
        data = request.get_json()
        
        # Log the error report
        current_app.logger.error(
            f"User error report: {data.get('description', 'No description')} | "
            f"URL: {data.get('url', 'Unknown')} | "
            f"Browser: {data.get('browser_info', 'Unknown')} | "
            f"User: {data.get('email', 'Anonymous')}"
        )
        
        # In a real implementation, you might send an email or save to database
        
        return jsonify({'success': True, 'message': 'Error report received'})
        
    except Exception as e:
        current_app.logger.error(f"Error processing error report: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/access-denied-log', methods=['POST'])
def access_denied_log():
    """
    Log access denied attempts for analytics.
    
    :return: JSON response
    """
    try:
        data = request.get_json()
        
        # Log access denied attempt
        current_app.logger.warning(
            f"Access denied: {data.get('url', 'Unknown URL')} | "
            f"User: {current_user.username if current_user.is_authenticated else 'Anonymous'} | "
            f"IP: {request.remote_addr} | "
            f"User Agent: {data.get('user_agent', 'Unknown')}"
        )
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error logging access denied: {e}")
        return jsonify({'success': False}), 500

# Error handlers for API blueprint
@api_bp.errorhandler(404)
def api_not_found(error):
    """
    Handle API 404 errors.
    
    :param error: The error object
    :return: JSON error response
    """
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    """
    Handle API 500 errors.
    
    :param error: The error object
    :return: JSON error response
    """
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
