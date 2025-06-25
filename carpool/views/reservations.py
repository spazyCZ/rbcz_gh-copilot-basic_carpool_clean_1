"""
This module defines routes for reservation management.
"""
import logging
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from carpool.forms.reservation_forms import ReservationForm
from carpool.services.parking_service import get_available_spots
from carpool.services.reservation_service import (
    get_all_reservations, get_reservation, get_user_reservations,
    create_reservation, update_reservation, delete_reservation,
    get_reservations_by_date
)
from carpool.services.action_service import log_action

reservations = Blueprint('reservations', __name__, url_prefix='/reservations')
logger = logging.getLogger(__name__)

@reservations.route('/')
@login_required
def index():
    """
    List all reservations or the current user's reservations.
    
    :return: Rendered template
    """
    # Admins see all reservations, regular users see only their own
    if current_user.is_admin():
        all_reservations = get_all_reservations()
        return render_template(
            'reservations/index.html',
            title='All Reservations',
            reservations=all_reservations,
            is_admin=True
        )
    else:
        user_reservations = get_user_reservations(current_user.username)
        return render_template(
            'reservations/index.html',
            title='My Reservations',
            reservations=user_reservations,
            is_admin=False
        )

@reservations.route('/new', methods=['GET', 'POST'])
@login_required
def new_reservation():
    """
    Create a new reservation.
    
    :return: Rendered template or redirect
    """
    # Get available spots for today (default)
    available_spots = get_available_spots(date.today())
    
    form = ReservationForm(available_spots=available_spots)
    form.username.data = current_user.username
    
    if form.validate_on_submit():
        reservation = create_reservation(
            spot_id=form.spot_id.data,
            username=current_user.username,
            reservation_date=form.reservation_date.data
        )
        
        if reservation:
            log_action('create_reservation', current_user.username)
            logger.info(f"Created reservation: Spot {reservation.spot_id} on {reservation.reservation_date} by {current_user.username}")
            flash(f'Reservation for spot {reservation.spot_id} on {reservation.reservation_date} has been created.', 'success')
            return redirect(url_for('reservations.index'))
        else:
            flash('An error occurred while creating the reservation. The spot may no longer be available.', 'danger')
    
    return render_template('reservations/form.html', title='New Reservation', form=form)

@reservations.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_reservation(id):
    """
    Edit an existing reservation.
    
    :param id: ID of the reservation to edit
    :return: Rendered template or redirect
    """
    reservation = get_reservation(id)
    if not reservation:
        flash(f'Reservation {id} not found.', 'danger')
        return redirect(url_for('reservations.index'))
    
    # Check if user is allowed to edit this reservation
    if not current_user.is_admin() and reservation.username != current_user.username:
        flash('You do not have permission to edit this reservation.', 'danger')
        return redirect(url_for('reservations.index'))
    
    # Get available spots plus the currently reserved spot
    available_spots = get_available_spots(reservation.reservation_date)
    current_spot_found = any(spot.id == reservation.spot_id for spot in available_spots)
    
    if not current_spot_found:
        from carpool.models.parking_spot import ParkingSpot
        current_spot = ParkingSpot.query.get(reservation.spot_id)
        if current_spot:
            available_spots.append(current_spot)
    
    form = ReservationForm(available_spots=available_spots, original_id=id)
    
    if request.method == 'GET':
        form.spot_id.data = reservation.spot_id
        form.username.data = reservation.username
        form.reservation_date.data = reservation.reservation_date
    
    if form.validate_on_submit():
        updated_reservation = update_reservation(
            reservation_id=id,
            spot_id=form.spot_id.data,
            reservation_date=form.reservation_date.data
        )
        
        if updated_reservation:
            log_action('update_reservation', current_user.username)
            logger.info(f"Updated reservation: {id} by {current_user.username}")
            flash(f'Reservation has been updated.', 'success')
            return redirect(url_for('reservations.index'))
        else:
            flash('An error occurred while updating the reservation. The spot may no longer be available.', 'danger')
    
    return render_template('reservations/form.html', title='Edit Reservation', form=form)

@reservations.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_reservation(id):
    """
    Delete a reservation.
    
    :param id: ID of the reservation to delete
    :return: Redirect to reservations index
    """
    reservation = get_reservation(id)
    if not reservation:
        flash(f'Reservation {id} not found.', 'danger')
        return redirect(url_for('reservations.index'))
    
    # Check if user is allowed to delete this reservation
    if not current_user.is_admin() and reservation.username != current_user.username:
        flash('You do not have permission to delete this reservation.', 'danger')
        return redirect(url_for('reservations.index'))
    
    if delete_reservation(id):
        log_action('delete_reservation', current_user.username)
        logger.info(f"Deleted reservation: {id} by {current_user.username}")
        flash('Reservation has been deleted.', 'success')
    else:
        flash('An error occurred while deleting the reservation.', 'danger')
    
    return redirect(url_for('reservations.index'))

@reservations.route('/api/available-spots', methods=['GET'])
@login_required
def api_available_spots():
    """
    Get available spots for a specific date.
    
    :return: JSON response with available spots
    """
    reservation_date_str = request.args.get('date')
    try:
        reservation_date = date.fromisoformat(reservation_date_str)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    
    available_spots = get_available_spots(reservation_date)
    spots_data = [{'id': spot.id, 'location': spot.location} for spot in available_spots]
    
    return jsonify({'spots': spots_data})

@reservations.route('/api/calendar-data', methods=['GET'])
@login_required
def api_calendar_data():
    """
    Get reservation data for calendar visualization.
    
    :return: JSON response with reservation data
    """
    # If admin, get all reservations; otherwise, get only user's reservations
    if current_user.is_admin():
        all_reservations = get_all_reservations()
    else:
        all_reservations = get_user_reservations(current_user.username)
    
    calendar_data = []
    for reservation in all_reservations:
        calendar_data.append({
            'id': reservation.id,
            'title': f'Spot {reservation.spot_id}',
            'start': reservation.reservation_date.isoformat(),
            'end': reservation.reservation_date.isoformat(),
            'username': reservation.username
        })
    
    return jsonify({'events': calendar_data})
