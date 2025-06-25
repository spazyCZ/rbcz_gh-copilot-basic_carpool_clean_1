"""
This module defines routes for parking spot management.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from carpool.forms.parking_forms import ParkingSpotForm
from carpool.services.parking_service import (
    get_all_parking_spots, get_parking_spot,
    create_parking_spot, update_parking_spot, delete_parking_spot
)
from carpool.services.action_service import log_action

parking = Blueprint('parking', __name__, url_prefix='/parking')
logger = logging.getLogger(__name__)

@parking.route('/')
@login_required
def index():
    """
    List all parking spots.
    
    :return: Rendered template
    """
    parking_spots = get_all_parking_spots()
    return render_template(
        'parking/index.html',
        title='Parking Spots',
        parking_spots=parking_spots
    )

@parking.route('/new', methods=['GET', 'POST'])
@login_required
def new_spot():
    """
    Create a new parking spot.
    
    :return: Rendered template or redirect
    """
    # Only admin can create parking spots
    if not current_user.is_admin():
        flash('You do not have permission to create parking spots.', 'danger')
        return redirect(url_for('parking.index'))
    
    form = ParkingSpotForm()
    if form.validate_on_submit():
        spot = create_parking_spot(
            spot_id=form.id.data,
            location=form.location.data,
            status=form.status.data
        )
        
        if spot:
            log_action('create_parking_spot', current_user.username)
            logger.info(f"Created parking spot: {spot.id} by {current_user.username}")
            flash(f'Parking spot {spot.id} has been created.', 'success')
            return redirect(url_for('parking.index'))
        else:
            flash('An error occurred while creating the parking spot.', 'danger')
    
    return render_template('parking/form.html', title='New Parking Spot', form=form)

@parking.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_spot(id):
    """
    Edit an existing parking spot.
    
    :param id: ID of the parking spot to edit
    :return: Rendered template or redirect
    """
    # Only admin can edit parking spots
    if not current_user.is_admin():
        flash('You do not have permission to edit parking spots.', 'danger')
        return redirect(url_for('parking.index'))
    
    spot = get_parking_spot(id)
    if not spot:
        flash(f'Parking spot {id} not found.', 'danger')
        return redirect(url_for('parking.index'))
    
    form = ParkingSpotForm(original_id=id)
    if request.method == 'GET':
        form.id.data = spot.id
        form.location.data = spot.location
        form.status.data = spot.status
    
    if form.validate_on_submit():
        updated_spot = None
        
        # If ID changed, we need to create a new spot and delete the old one
        if form.id.data != id:
            new_spot = create_parking_spot(
                spot_id=form.id.data,
                location=form.location.data,
                status=form.status.data
            )
            
            if new_spot:
                delete_parking_spot(id)
                updated_spot = new_spot
        else:
            # Otherwise, just update the existing spot
            updated_spot = update_parking_spot(
                spot_id=id,
                location=form.location.data,
                status=form.status.data
            )
        
        if updated_spot:
            log_action('update_parking_spot', current_user.username)
            logger.info(f"Updated parking spot: {updated_spot.id} by {current_user.username}")
            flash(f'Parking spot {updated_spot.id} has been updated.', 'success')
            return redirect(url_for('parking.index'))
        else:
            flash('An error occurred while updating the parking spot.', 'danger')
    
    return render_template('parking/form.html', title='Edit Parking Spot', form=form)

@parking.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete_spot(id):
    """
    Delete a parking spot.
    
    :param id: ID of the parking spot to delete
    :return: Redirect to parking spots index
    """
    # Only admin can delete parking spots
    if not current_user.is_admin():
        flash('You do not have permission to delete parking spots.', 'danger')
        return redirect(url_for('parking.index'))
    
    if delete_parking_spot(id):
        log_action('delete_parking_spot', current_user.username)
        logger.info(f"Deleted parking spot: {id} by {current_user.username}")
        flash(f'Parking spot {id} has been deleted.', 'success')
    else:
        flash(f'An error occurred while deleting parking spot {id}.', 'danger')
    
    return redirect(url_for('parking.index'))
