"""
Main views and routes for the carpool application.

This module contains the main blueprint with routes for dashboard, reservations,
carpools, and user profile management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, date
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.carpool import Carpool
from carpool.models.action import Action
from carpool.forms.reservation_forms import ReservationForm, EditReservationForm, QuickReservationForm
from carpool.forms.carpool_forms import CarpoolForm, EditCarpoolForm, JoinCarpoolForm, LeaveCarpoolForm
from carpool.services.reservation_service import ReservationService
from carpool.services.carpool_service import CarpoolService
from extensions import db

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page route - displays welcome page or redirects to dashboard if logged in.
    
    :return: Rendered template or redirect response
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Get some basic statistics for the welcome page
    total_spots = ParkingSpot.query.count()
    total_users = User.query.count()
    active_carpools = Carpool.query.filter(Carpool.departure_time >= datetime.utcnow()).count()
    
    return render_template('index.html', 
                         total_spots=total_spots,
                         total_users=total_users,
                         active_carpools=active_carpools)


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard route - displays overview of user's activities and statistics.
    
    :return: Rendered dashboard template
    """
    try:
        # Get user's reservations
        user_reservations = ReservationService.get_user_reservations(current_user, include_past=False)
        
        # Get user's carpools
        user_carpools = CarpoolService.get_user_carpools(current_user, include_past=False)
        
        # Get today's reservations count
        today = date.today()
        today_reservations = len([r for r in user_reservations if r.reservation_date == today])
        
        # Get available spots for today
        available_today = len(ReservationService.get_available_spots_for_date(today))
        
        # Get system statistics
        reservation_stats = ReservationService.get_reservation_statistics()
        carpool_stats = CarpoolService.get_carpool_statistics()
        
        # Create combined stats object for template
        stats = {
            'total_spots': reservation_stats.get('total_spots', 0),
            'available_spots': reservation_stats.get('available_spots', 0),
            'my_reservations': len(user_reservations),
            'active_carpools': carpool_stats.get('future_carpools', 0)
        }
        
        return render_template('dashboard.html',
                             user_reservations=user_reservations[:5],  # Last 5
                             user_carpools=user_carpools[:5],  # Last 5
                             today_reservations=today_reservations,
                             available_today=available_today,
                             reservation_stats=reservation_stats,
                             carpool_stats=carpool_stats,
                             stats=stats)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading dashboard for user {current_user.username}: {e}')
        flash('Error loading dashboard. Please try again.', 'error')
        # Provide default values for error case
        default_stats = {
            'total_spots': 0,
            'available_spots': 0,
            'my_reservations': 0,
            'active_carpools': 0
        }
        return render_template('dashboard.html',
                             user_reservations=[],
                             user_carpools=[],
                             today_reservations=0,
                             available_today=0,
                             reservation_stats={},
                             carpool_stats={},
                             stats=default_stats)


@main_bp.route('/reservations')
@login_required
def reservations():
    """
    Reservations overview route - displays user's current and past reservations.
    
    :return: Rendered reservations template
    """
    try:
        current_app.logger.info(f'Fetching reservations for user {current_user.username} (ID: {current_user.id})')
        
        # Get user's reservations
        current_reservations = ReservationService.get_user_reservations(current_user, include_past=False)
        current_app.logger.info(f'Found {len(current_reservations)} current reservations for user {current_user.username}')
        
        # Log details of current reservations
        for reservation in current_reservations:
            current_app.logger.debug(f'Current reservation: ID={reservation.id}, Spot={reservation.spot_id}, Date={reservation.reservation_date}, Status={reservation.status}')
        
        past_reservations = ReservationService.get_user_reservations(current_user, include_past=True)
        past_reservations = [r for r in past_reservations if r.is_past_reservation()]
        current_app.logger.info(f'Found {len(past_reservations)} past reservations for user {current_user.username}')
        
        # Log details of past reservations
        for reservation in past_reservations:
            current_app.logger.debug(f'Past reservation: ID={reservation.id}, Spot={reservation.spot_id}, Date={reservation.reservation_date}, Status={reservation.status}')
        
        current_app.logger.info(f'Successfully loaded reservations view for user {current_user.username} - {len(current_reservations)} current, {len(past_reservations)} past')
        
        return render_template('reservations/list.html',
                             current_reservations=current_reservations,
                             past_reservations=past_reservations)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading reservations for user {current_user.username}: {e}', exc_info=True)
        flash('Error loading reservations. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/reservations/new', methods=['GET', 'POST'])
@login_required
def new_reservation():
    """
    Create new reservation route - handles reservation form submission.
    
    :return: Rendered form template or redirect response
    """
    if not current_user.can_make_reservation():
        flash('You do not have permission to make reservations.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = ReservationForm()
    
    if form.validate_on_submit():
        current_app.logger.info(f'User {current_user.username} attempting to create reservation for spot {form.spot_id.data} on {form.reservation_date.data}')
        try:
            # Create the reservation
            reservation = ReservationService.create_reservation(
                user=current_user,
                spot_id=form.spot_id.data,
                name=form.name.data,
                reservation_date=form.reservation_date.data
            )
            
            if reservation:
                current_app.logger.info(f'Successfully created reservation ID {reservation.id} for user {current_user.username}: spot={reservation.spot_id}, date={reservation.reservation_date}')
                flash(f'Reservation created successfully for spot {reservation.spot_id}!', 'success')
                return redirect(url_for('main.reservations'))
            else:
                current_app.logger.warning(f'Failed to create reservation for user {current_user.username}: spot={form.spot_id.data}, date={form.reservation_date.data} - service returned None')
                flash('Failed to create reservation. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error creating reservation for user {current_user.username}: spot={form.spot_id.data}, date={form.reservation_date.data} - {e}', exc_info=True)
            flash('An error occurred while creating the reservation.', 'error')
    
    return render_template('reservations/make.html', form=form)


@main_bp.route('/reservations/<int:reservation_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reservation(reservation_id):
    """
    Edit reservation route - handles reservation update form submission.
    
    :param reservation_id: ID of the reservation to edit
    :return: Rendered form template or redirect response
    """
    current_app.logger.info(f'User {current_user.username} attempting to edit reservation ID: {reservation_id}')
    
    reservation = ReservationService.get_reservation_by_id(reservation_id)
    
    if not reservation:
        current_app.logger.warning(f'Reservation ID {reservation_id} not found for edit attempt by user {current_user.username}')
        flash('Reservation not found.', 'error')
        return redirect(url_for('main.reservations'))
    
    current_app.logger.info(f'Retrieved reservation for editing: ID={reservation.id}, User={reservation.user_id}, Spot={reservation.spot_id}, Date={reservation.reservation_date}')
    
    # Check if user can edit this reservation
    if not (current_user.is_admin() or reservation.user_id == current_user.id):
        current_app.logger.warning(f'User {current_user.username} denied permission to edit reservation {reservation_id} (belongs to user ID {reservation.user_id})')
        flash('You do not have permission to edit this reservation.', 'error')
        return redirect(url_for('main.reservations'))
    
    # Check if reservation can be modified
    if not reservation.can_be_modified():
        current_app.logger.info(f'Reservation {reservation_id} cannot be modified (past date or cancelled)')
        flash('This reservation cannot be modified.', 'error')
        return redirect(url_for('main.reservations'))
    
    form = EditReservationForm(reservation=reservation)
    
    if form.validate_on_submit():
        current_app.logger.info(f'User {current_user.username} attempting to update reservation {reservation_id}: new_spot={form.spot_id.data}, new_date={form.reservation_date.data}, new_name={form.name.data}')
        try:
            # Update the reservation
            success = ReservationService.update_reservation(
                reservation=reservation,
                user=current_user,
                new_name=form.name.data,
                new_spot_id=form.spot_id.data,
                new_date=form.reservation_date.data
            )
            
            if success:
                current_app.logger.info(f'Successfully updated reservation {reservation_id} for user {current_user.username}')
                flash('Reservation updated successfully!', 'success')
                return redirect(url_for('main.reservations'))
            else:
                current_app.logger.warning(f'Failed to update reservation {reservation_id} for user {current_user.username} - service returned False')
                flash('Failed to update reservation. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error updating reservation {reservation_id} for user {current_user.username}: {e}', exc_info=True)
            flash('An error occurred while updating the reservation.', 'error')
    
    return render_template('reservations/edit.html', form=form, reservation=reservation)


@main_bp.route('/reservations/<int:reservation_id>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    """
    Cancel reservation route - handles reservation cancellation.
    
    :param reservation_id: ID of the reservation to cancel
    :return: Redirect response
    """
    current_app.logger.info(f'User {current_user.username} attempting to cancel reservation ID: {reservation_id}')
    
    reservation = ReservationService.get_reservation_by_id(reservation_id)
    
    if not reservation:
        current_app.logger.warning(f'Reservation ID {reservation_id} not found for cancellation attempt by user {current_user.username}')
        flash('Reservation not found.', 'error')
        return redirect(url_for('main.reservations'))
    
    current_app.logger.info(f'Retrieved reservation for cancellation: ID={reservation.id}, User={reservation.user_id}, Spot={reservation.spot_id}, Date={reservation.reservation_date}, Status={reservation.status}')
    
    # Check if user can cancel this reservation
    if not (current_user.is_admin() or reservation.user_id == current_user.id):
        current_app.logger.warning(f'User {current_user.username} denied permission to cancel reservation {reservation_id} (belongs to user ID {reservation.user_id})')
        flash('You do not have permission to cancel this reservation.', 'error')
        return redirect(url_for('main.reservations'))
    
    try:
        # Cancel the reservation
        success = ReservationService.cancel_reservation(reservation, current_user)
        
        if success:
            current_app.logger.info(f'Successfully cancelled reservation {reservation_id} for user {current_user.username}')
            flash('Reservation cancelled successfully.', 'success')
        else:
            current_app.logger.warning(f'Failed to cancel reservation {reservation_id} for user {current_user.username} - service returned False')
            flash('Failed to cancel reservation. Please try again.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Error cancelling reservation {reservation_id} for user {current_user.username}: {e}', exc_info=True)
        flash('An error occurred while cancelling the reservation.', 'error')
    
    return redirect(url_for('main.reservations'))


@main_bp.route('/carpools')
@login_required
def carpools():
    """
    Carpools overview route - displays available and user's carpools.
    
    :return: Rendered carpools template
    """
    try:
        # Get available carpools
        available_carpools = CarpoolService.get_available_carpools(include_past=False)
        
        # Get user's organized carpools
        user_carpools = CarpoolService.get_user_carpools(current_user, include_past=False)
        
        return render_template('carpools/list.html',
                             available_carpools=available_carpools,
                             user_carpools=user_carpools)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading carpools for user {current_user.username}: {e}')
        flash('Error loading carpools. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))


@main_bp.route('/carpools/new', methods=['GET', 'POST'])
@login_required
def new_carpool():
    """
    Create new carpool route - handles carpool form submission.
    
    :return: Rendered form template or redirect response
    """
    if not current_user.can_organize_carpool():
        flash('You do not have permission to organize carpools.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = CarpoolForm()
    
    if form.validate_on_submit():
        try:
            # Create the carpool
            carpool = CarpoolService.create_carpool(
                user=current_user,
                name=form.name.data,
                origin=form.origin.data,
                destination=form.destination.data,
                departure_time=form.departure_time.data,
                max_passengers=form.max_passengers.data,
                return_time=form.return_time.data,
                notes=form.notes.data
            )
            
            if carpool:
                flash(f'Carpool "{carpool.name}" created successfully!', 'success')
                return redirect(url_for('main.carpools'))
            else:
                flash('Failed to create carpool. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Error creating carpool: {e}')
            flash('An error occurred while creating the carpool.', 'error')
    
    return render_template('carpools/create.html', form=form)


@main_bp.route('/carpools/<int:carpool_id>')
@login_required
def carpool_detail(carpool_id):
    """
    Carpool detail route - displays detailed information about a carpool.
    
    :param carpool_id: ID of the carpool to display
    :return: Rendered carpool detail template
    """
    carpool = CarpoolService.get_carpool_by_id(carpool_id)
    
    if not carpool:
        flash('Carpool not found.', 'error')
        return redirect(url_for('main.carpools'))
    
    join_form = JoinCarpoolForm()
    leave_form = LeaveCarpoolForm()
    
    return render_template('carpools/detail.html',
                         carpool=carpool,
                         join_form=join_form,
                         leave_form=leave_form)


@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    User profile route - displays user account information and activity.
    Also handles profile updates via POST requests.
    
    :return: Rendered profile template or redirect response
    """
    if request.method == 'POST':
        try:
            # Handle profile update
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            
            # Basic validation
            if not username or not email:
                flash('Username and email are required.', 'error')
                return redirect(url_for('main.profile'))
            
            # Check if username is already taken (by another user)
            existing_user = User.query.filter(User.username == username, User.id != current_user.id).first()
            if existing_user:
                flash('Username is already taken.', 'error')
                return redirect(url_for('main.profile'))
            
            # Check if email is already taken (by another user)
            existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_email:
                flash('Email is already taken.', 'error')
                return redirect(url_for('main.profile'))
            
            # Update user information
            current_user.username = username
            current_user.email = email
            db.session.commit()
            
            # Log the profile update action
            from carpool.models.action import Action
            action = Action(
                username=current_user.username,
                action_type='profile_update',
                details=f'Updated profile: username={username}, email={email}',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')
            )
            db.session.add(action)
            db.session.commit()
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('main.profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating profile for user {current_user.username}: {e}')
            flash('Error updating profile. Please try again.', 'error')
            return redirect(url_for('main.profile'))
    
    # Handle GET request - display profile
    try:
        # Get user's recent reservations
        recent_reservations = ReservationService.get_user_reservations(current_user, include_past=True)[:10]
        
        # Get user's recent carpools
        recent_carpools = CarpoolService.get_user_carpools(current_user, include_past=True)[:10]
        
        # Get user's activity statistics
        total_reservations = len(ReservationService.get_user_reservations(current_user, include_past=True))
        total_carpools = len(CarpoolService.get_user_carpools(current_user, include_past=True))
        
        # Get upcoming reservations count
        upcoming_reservations = len(ReservationService.get_user_reservations(current_user, include_past=False))
        
        # Create stats object for template
        stats = {
            'total_reservations': total_reservations,
            'upcoming_reservations': upcoming_reservations,
            'carpools_organized': total_carpools,
            'carpools_joined': 0  # This would require additional logic to track joined carpools
        }
        
        return render_template('profile.html',
                             recent_reservations=recent_reservations,
                             recent_carpools=recent_carpools,
                             total_reservations=total_reservations,
                             total_carpools=total_carpools,
                             stats=stats)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading profile for user {current_user.username}: {e}')
        flash('Error loading profile. Please try again.', 'error')
        # Provide default values for error case
        default_stats = {
            'total_reservations': 0,
            'upcoming_reservations': 0,
            'carpools_organized': 0,
            'carpools_joined': 0
        }
        return render_template('profile.html',
                             recent_reservations=[],
                             recent_carpools=[],
                             total_reservations=0,
                             total_carpools=0,
                             stats=default_stats)


@main_bp.route('/join-carpool', methods=['POST'])
@login_required
def join_carpool():
    """
    Join a carpool route - allows users to join an existing carpool.
    
    :return: Redirect response with success or error message
    """
    carpool_id = request.form.get('carpool_id')
    if not carpool_id:
        flash('Invalid carpool ID.', 'error')
        return redirect(url_for('main.carpools'))
    
    try:
        carpool = Carpool.query.get_or_404(carpool_id)
        
        # Check if user is already in this carpool
        if current_user in carpool.passengers:
            flash('You are already a member of this carpool.', 'info')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Check if carpool has space
        if len(carpool.passengers) >= carpool.max_passengers:
            flash('This carpool is already full.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Check if user is the driver
        if carpool.driver_id == current_user.id:
            flash('You cannot join your own carpool as a passenger.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Add user to carpool
        carpool.passengers.append(current_user)
        db.session.commit()
        
        # Log the action
        action = Action(
            user_id=current_user.id,
            action_type='carpool_join',
            description=f"Joined carpool '{carpool.title}'"
        )
        db.session.add(action)
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.email} joined carpool {carpool_id}")
        flash('Successfully joined the carpool!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error joining carpool {carpool_id}: {e}")
        flash('An error occurred while joining the carpool. Please try again.', 'error')
    
    return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))


@main_bp.route('/leave-carpool', methods=['POST'])
@login_required
def leave_carpool():
    """
    Leave a carpool route - allows users to leave a carpool they've joined.
    
    :return: Redirect response with success or error message
    """
    carpool_id = request.form.get('carpool_id')
    if not carpool_id:
        flash('Invalid carpool ID.', 'error')
        return redirect(url_for('main.carpools'))
    
    try:
        carpool = Carpool.query.get_or_404(carpool_id)
        
        # Check if user is in this carpool
        if current_user not in carpool.passengers:
            flash('You are not a member of this carpool.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Check if user is the driver (drivers cannot leave, they must cancel)
        if carpool.driver_id == current_user.id:
            flash('As the driver, you cannot leave the carpool. Use cancel instead.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Remove user from carpool
        carpool.passengers.remove(current_user)
        db.session.commit()
        
        # Log the action
        action = Action(
            user_id=current_user.id,
            action_type='carpool_leave',
            description=f"Left carpool '{carpool.title}'"
        )
        db.session.add(action)
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.email} left carpool {carpool_id}")
        flash('Successfully left the carpool.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error leaving carpool {carpool_id}: {e}")
        flash('An error occurred while leaving the carpool. Please try again.', 'error')
    
    return redirect(url_for('main.carpools'))


@main_bp.route('/cancel-carpool', methods=['POST'])
@login_required
def cancel_carpool():
    """
    Cancel a carpool route - allows drivers to cancel their own carpools.
    
    :return: Redirect response with success or error message
    """
    carpool_id = request.form.get('carpool_id')
    if not carpool_id:
        flash('Invalid carpool ID.', 'error')
        return redirect(url_for('main.carpools'))
    
    try:
        carpool = Carpool.query.get_or_404(carpool_id)
        
        # Check if user is the driver
        if carpool.driver_id != current_user.id:
            flash('Only the driver can cancel a carpool.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Check if carpool has already departed
        if carpool.departure_time <= datetime.utcnow():
            flash('Cannot cancel a carpool that has already departed.', 'error')
            return redirect(url_for('main.carpool_detail', carpool_id=carpool_id))
        
        # Store carpool title for logging
        carpool_title = carpool.title
        
        # Remove the carpool (this will also remove passenger associations)
        db.session.delete(carpool)
        db.session.commit()
        
        # Log the action
        action = Action(
            user_id=current_user.id,
            action_type='carpool_cancel',
            description=f"Cancelled carpool '{carpool_title}'"
        )
        db.session.add(action)
        db.session.commit()
        
        current_app.logger.info(f"User {current_user.email} cancelled carpool {carpool_id}")
        flash('Carpool has been cancelled successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error cancelling carpool {carpool_id}: {e}")
        flash('An error occurred while cancelling the carpool. Please try again.', 'error')
    
    return redirect(url_for('main.carpools'))


# User loader for Flask-Login
from extensions import login_manager

@login_manager.user_loader
def load_user(user_id):
    """
    User loader function for Flask-Login.
    
    :param user_id: ID of the user to load
    :return: User object if found, None otherwise
    """
    try:
        return User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None
