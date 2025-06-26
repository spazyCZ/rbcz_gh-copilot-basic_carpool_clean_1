"""
Admin views and routes for the carpool application.

This module contains the admin blueprint with routes for user management,
system monitoring, parking spot management, and activity logging.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.carpool import Carpool
from carpool.models.action import Action
from carpool.forms.admin_forms import CreateUserForm, EditUserForm, CreateParkingSpotForm, EditParkingSpotForm, ActivityLogFilterForm
from carpool.services.admin_service import AdminService
from carpool.services.auth_service import AuthService
from extensions import db

# Create admin blueprint
admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """
    Decorator to require admin privileges for route access.
    
    :param f: Function to decorate
    :return: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Admin dashboard route - displays system overview and statistics.
    
    :return: Rendered admin dashboard template
    """
    try:
        # Get comprehensive system statistics
        stats = AdminService.get_system_statistics()
        
        # Get recent activity logs
        recent_actions = AdminService.get_activity_logs(limit=20)
        
        # Get activity chart data for the last 7 days
        chart_data = AdminService.get_activity_chart_data(days=7)
        
        return render_template('admin/dashboard.html',
                             stats=stats,
                             recent_actions=recent_actions,
                             chart_data=chart_data)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading admin dashboard: {e}')
        flash('Error loading admin dashboard. Please try again.', 'error')
        # Provide default values for error case
        default_stats = {
            'total_users': 0,
            'total_reservations': 0,
            'total_carpools': 0,
            'system_health': 0,
            'active_sessions': 0,
            'errors_24h': 0
        }
        return render_template('admin/dashboard.html', stats=default_stats, recent_actions=[], chart_data={})


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    Users management route - displays all system users.
    
    :return: Rendered users list template
    """
    try:
        all_users = AdminService.get_all_users()
        
        # Get user statistics for template
        system_stats = AdminService.get_system_statistics()
        stats = {
            'total_users': system_stats.get('users', {}).get('total', 0),
            'active_users': system_stats.get('users', {}).get('regular', 0) + system_stats.get('users', {}).get('administrators', 0),
            'admin_users': system_stats.get('users', {}).get('administrators', 0),
            'new_users_today': 0  # This would need a new query to get users created today
        }
        
        return render_template('admin/users.html', users=all_users, stats=stats)
        
    except Exception as e:
        current_app.logger.error(f'Error loading users list: {e}')
        flash('Error loading users. Please try again.', 'error')
        # Provide default stats for error case
        default_stats = {
            'total_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'new_users_today': 0
        }
        return render_template('admin/users.html', users=[], stats=default_stats)


@admin_bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """
    Create new user route - handles user creation form submission.
    
    :return: Rendered form template or redirect response
    """
    form = CreateUserForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = AdminService.create_user(
                admin_user=current_user,
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                password=form.password.data,
                role=form.role.data
            )
            
            if user:
                flash(f'User "{user.username}" created successfully!', 'success')
                return redirect(url_for('admin.users'))
            else:
                flash('Failed to create user. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error creating user: {e}')
            flash('An error occurred while creating the user.', 'error')
    
    # Get user statistics for template (needed by users.html template)
    try:
        system_stats = AdminService.get_system_statistics()
        stats = {
            'total_users': system_stats.get('users', {}).get('total', 0),
            'active_users': system_stats.get('users', {}).get('regular', 0) + system_stats.get('users', {}).get('administrators', 0),
            'admin_users': system_stats.get('users', {}).get('administrators', 0),
            'new_users_today': 0  # This would need a new query to get users created today
        }
    except Exception:
        stats = {'total_users': 0, 'active_users': 0, 'admin_users': 0, 'new_users_today': 0}
    
    return render_template('admin/users.html', form=form, stats=stats)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    Edit user route - handles user update form submission.
    
    :param user_id: ID of the user to edit
    :return: Rendered form template or redirect response
    """
    user = User.query.get_or_404(user_id)
    
    # Don't allow editing the current admin's own account through this interface
    if user.id == current_user.id:
        flash('Use the profile page to edit your own account.', 'info')
        return redirect(url_for('admin.users'))
    
    form = EditUserForm(original_email=user.email)
    
    if form.validate_on_submit():
        try:
            # Update user email
            user.email = form.email.data.strip().lower()
            
            # Update user role
            success = AdminService.update_user_role(current_user, user, form.role.data)
            if success:
                db.session.commit()
                flash(f'User "{user.username}" updated successfully!', 'success')
                return redirect(url_for('admin.users'))
            else:
                flash('Failed to update user. Please try again.', 'error')
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating user: {e}')
            flash('An error occurred while updating the user.', 'error')
    else:
        # Pre-populate form with existing data
        form.email.data = user.email
        form.role.data = user.role
    
    # Get user statistics for template (needed by users.html template)
    try:
        system_stats = AdminService.get_system_statistics()
        stats = {
            'total_users': system_stats.get('users', {}).get('total', 0),
            'active_users': system_stats.get('users', {}).get('regular', 0) + system_stats.get('users', {}).get('administrators', 0),
            'admin_users': system_stats.get('users', {}).get('administrators', 0),
            'new_users_today': 0  # This would need a new query to get users created today
        }
    except Exception:
        stats = {'total_users': 0, 'active_users': 0, 'admin_users': 0, 'new_users_today': 0}
    
    return render_template('admin/users.html', form=form, user=user, stats=stats)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Delete user route - handles user deletion.
    
    :param user_id: ID of the user to delete
    :return: Redirect response
    """
    user = User.query.get_or_404(user_id)
    
    # Don't allow deleting the current admin's own account
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.users'))
    
    try:
        success = AdminService.delete_user(current_user, user)
        if success:
            flash(f'User "{user.username}" deleted successfully.', 'success')
        else:
            flash('Failed to delete user. Please try again.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error deleting user: {e}')
        flash('An error occurred while deleting the user.', 'error')
    
    return redirect(url_for('admin.users'))


@admin_bp.route('/parking-spots')
@login_required
@admin_required
def parking_spots():
    """
    Parking spots management route - displays all parking spots.
    
    :return: Rendered parking spots list template
    """
    try:
        all_spots = ParkingSpot.query.order_by(ParkingSpot.id).all()
        
        # Get unique locations for filter dropdown
        locations = list(set(spot.location for spot in all_spots if spot.location))
        
        # Group spots by location for grid view
        spots_by_location = {}
        for spot in all_spots:
            location = spot.location or 'Unknown'
            if location not in spots_by_location:
                spots_by_location[location] = []
            spots_by_location[location].append(spot)
        
        # Get parking statistics for template
        system_stats = AdminService.get_system_statistics()
        parking_stats = system_stats.get('parking', {})
        stats = {
            'total_spots': parking_stats.get('total_spots', 0),
            'available_spots': parking_stats.get('available', 0),
            'reserved_spots': parking_stats.get('reserved', 0),
            'maintenance_spots': parking_stats.get('maintenance', 0)
        }
        
        return render_template('admin/parking.html', 
                             spots=all_spots,
                             all_spots=all_spots,
                             locations=locations,
                             spots_by_location=spots_by_location,
                             stats=stats)
        
    except Exception as e:
        current_app.logger.error(f'Error loading parking spots: {e}')
        flash('Error loading parking spots. Please try again.', 'error')
        # Provide default stats for error case
        default_stats = {
            'total_spots': 0,
            'available_spots': 0,
            'reserved_spots': 0,
            'maintenance_spots': 0
        }
        return render_template('admin/parking.html', 
                             spots=[], 
                             all_spots=[],
                             locations=[],
                             spots_by_location={},
                             stats=default_stats)


@admin_bp.route('/parking-spots/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_parking_spot():
    """
    Create new parking spot route - handles parking spot creation form submission.
    
    :return: Rendered form template or redirect response
    """
    form = CreateParkingSpotForm()
    
    if form.validate_on_submit():
        try:
            # Create new parking spot
            spot = AdminService.create_parking_spot(
                admin_user=current_user,
                spot_id=form.spot_id.data.strip().upper(),
                location=form.location.data.strip(),
                description=form.description.data.strip() if form.description.data else None
            )
            
            if spot:
                flash(f'Parking spot "{spot.id}" created successfully!', 'success')
                return redirect(url_for('admin.parking_spots'))
            else:
                flash('Failed to create parking spot. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error creating parking spot: {e}')
            flash('An error occurred while creating the parking spot.', 'error')
    
    # Get parking statistics for template (needed by parking.html template)
    try:
        system_stats = AdminService.get_system_statistics()
        parking_stats = system_stats.get('parking', {})
        stats = {
            'total_spots': parking_stats.get('total_spots', 0),
            'available_spots': parking_stats.get('available', 0),
            'reserved_spots': parking_stats.get('reserved', 0),
            'maintenance_spots': parking_stats.get('maintenance', 0)
        }
    except Exception:
        stats = {'total_spots': 0, 'available_spots': 0, 'reserved_spots': 0, 'maintenance_spots': 0}
    
    return render_template('admin/parking.html', 
                         form=form, 
                         spots=[], 
                         all_spots=[],
                         locations=[],
                         spots_by_location={},
                         stats=stats)


@admin_bp.route('/parking-spots/<spot_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_parking_spot(spot_id):
    """
    Edit parking spot route - handles parking spot update form submission.
    
    :param spot_id: ID of the parking spot to edit
    :return: Rendered form template or redirect response
    """
    spot = ParkingSpot.query.get_or_404(spot_id)
    form = EditParkingSpotForm()
    
    if form.validate_on_submit():
        try:
            # Update parking spot details
            spot.location = form.location.data.strip()
            spot.description = form.description.data.strip() if form.description.data else None
            
            # Update status
            success = AdminService.update_parking_spot_status(current_user, spot, form.status.data)
            if success:
                flash(f'Parking spot "{spot.id}" updated successfully!', 'success')
                return redirect(url_for('admin.parking_spots'))
            else:
                flash('Failed to update parking spot. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error updating parking spot: {e}')
            flash('An error occurred while updating the parking spot.', 'error')
    else:
        # Pre-populate form with existing data
        form.location.data = spot.location
        form.description.data = spot.description
        form.status.data = spot.status
    
    # Get parking statistics for template (needed by parking.html template)
    try:
        system_stats = AdminService.get_system_statistics()
        parking_stats = system_stats.get('parking', {})
        stats = {
            'total_spots': parking_stats.get('total_spots', 0),
            'available_spots': parking_stats.get('available', 0),
            'reserved_spots': parking_stats.get('reserved', 0),
            'maintenance_spots': parking_stats.get('maintenance', 0)
        }
    except Exception:
        stats = {'total_spots': 0, 'available_spots': 0, 'reserved_spots': 0, 'maintenance_spots': 0}
    
    return render_template('admin/parking.html', 
                         form=form, 
                         spot=spot, 
                         spots=[], 
                         all_spots=[],
                         locations=[],
                         spots_by_location={},
                         stats=stats)


@admin_bp.route('/parking-spots/<spot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_parking_spot(spot_id):
    """
    Delete parking spot route - handles parking spot deletion.
    
    :param spot_id: ID of the parking spot to delete
    :return: Redirect response
    """
    spot = ParkingSpot.query.get_or_404(spot_id)
    
    try:
        success = AdminService.delete_parking_spot(current_user, spot)
        if success:
            flash(f'Parking spot "{spot.id}" deleted successfully.', 'success')
        else:
            flash('Cannot delete parking spot with active reservations.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error deleting parking spot: {e}')
        flash('An error occurred while deleting the parking spot.', 'error')
    
    return redirect(url_for('admin.parking_spots'))


@admin_bp.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    """
    Activity logs route - displays system activity logs with filtering.
    
    :return: Rendered activity logs template
    """
    form = ActivityLogFilterForm()
    logs = []
    
    try:
        # Get filter parameters
        action_type = request.args.get('action_type', '')
        username = request.args.get('username', '')
        limit = int(request.args.get('limit', '100'))
        
        # Get filtered logs
        logs = AdminService.get_activity_logs(
            limit=limit,
            action_type=action_type if action_type else None,
            username=username if username else None
        )
        
        # Get activity statistics for template
        system_stats = AdminService.get_system_statistics()
        activity_stats = system_stats.get('activity', {})
        
        # Get additional stats that might not be in system_stats
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        
        # Count unique users who have performed actions
        unique_users_count = db.session.query(Action.username).distinct().filter(Action.username.isnot(None)).count()
        
        # Count actions in the last hour
        actions_this_hour = Action.query.filter(Action.timestamp >= hour_ago).count()
        
        stats = {
            'total_actions': activity_stats.get('total_actions', 0),
            'actions_today': activity_stats.get('today_actions', 0),
            'unique_users': unique_users_count,
            'actions_this_hour': actions_this_hour
        }
        
        # Set form data from query parameters
        form.action_type.data = action_type
        form.username.data = username
        
    except Exception as e:
        current_app.logger.error(f'Error loading activity logs: {e}')
        flash('Error loading activity logs. Please try again.', 'error')
        # Provide default stats for error case
        default_stats = {
            'total_actions': 0,
            'actions_today': 0,
            'unique_users': 0,
            'actions_this_hour': 0
        }
        stats = default_stats
    
    return render_template('admin/logs.html', form=form, logs=logs, actions=logs, stats=stats)


@admin_bp.route('/reservations')
@login_required
@admin_required
def reservations():
    """
    All reservations route - displays all system reservations.
    
    :return: Rendered reservations list template
    """
    try:
        all_reservations = Reservation.query.order_by(Reservation.reservation_date.desc()).limit(200).all()
        return render_template('admin/reservations.html', reservations=all_reservations)
        
    except Exception as e:
        current_app.logger.error(f'Error loading reservations: {e}')
        flash('Error loading reservations. Please try again.', 'error')
        return render_template('admin/reservations.html', reservations=[])


@admin_bp.route('/carpools')
@login_required
@admin_required
def carpools():
    """
    All carpools route - displays all system carpools.
    
    :return: Rendered carpools list template
    """
    try:
        all_carpools = Carpool.query.order_by(Carpool.departure_time.desc()).limit(200).all()
        return render_template('admin/carpools.html', carpools=all_carpools)
        
    except Exception as e:
        current_app.logger.error(f'Error loading carpools: {e}')
        flash('Error loading carpools. Please try again.', 'error')
        return render_template('admin/carpools.html', carpools=[])
