"""
This module defines routes for carpool management.
"""
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from carpool.forms.carpool_forms import CarpoolForm, JoinCarpoolForm, LeaveCarpoolForm, CancelCarpoolForm
from carpool.services.carpool_service import (
    get_all_carpools, get_active_carpools, get_carpool,
    create_carpool, update_carpool, delete_carpool,
    join_carpool, leave_carpool, get_user_carpools
)
from carpool.services.action_service import log_action

carpools = Blueprint('carpools', __name__, url_prefix='/carpools')
logger = logging.getLogger(__name__)

@carpools.route('/')
@login_required
def index():
    """
    List all active carpools.
    
    :return: Rendered template
    """
    all_carpools = get_active_carpools()
    user_carpools = get_user_carpools(current_user.username)
    
    return render_template(
        'carpools/index.html',
        title='Carpools',
        carpools=all_carpools,
        user_carpools=user_carpools
    )

@carpools.route('/my')
@login_required
def my_carpools():
    """
    List carpools where the current user is a driver or passenger.
    
    :return: Rendered template
    """
    user_carpools = get_user_carpools(current_user.username)
    
    return render_template(
        'carpools/my_carpools.html',
        title='My Carpools',
        carpools=user_carpools
    )

@carpools.route('/new', methods=['GET', 'POST'])
@login_required
def new_carpool():
    """
    Create a new carpool.
    
    :return: Rendered template or redirect
    """
    form = CarpoolForm()
    
    if form.validate_on_submit():
        carpool = create_carpool(
            name=form.name.data,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data,
            return_time=form.return_time.data,
            max_passengers=form.max_passengers.data,
            driver_id=current_user.username,
            notes=form.notes.data
        )
        
        if carpool:
            log_action('create_carpool', current_user.username)
            logger.info(f"Created carpool: {carpool.id} by {current_user.username}")
            flash(f'Carpool "{carpool.name}" has been created.', 'success')
            return redirect(url_for('carpools.index'))
        else:
            flash('An error occurred while creating the carpool.', 'danger')
    
    return render_template('carpools/form.html', title='New Carpool', form=form)

@carpools.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_carpool(id):
    """
    Edit an existing carpool.
    
    :param id: ID of the carpool to edit
    :return: Rendered template or redirect
    """
    carpool = get_carpool(id)
    
    if not carpool:
        flash(f'Carpool not found.', 'danger')
        return redirect(url_for('carpools.index'))
    
    # Only the driver can edit the carpool
    if carpool.driver_id != current_user.username and not current_user.is_admin():
        flash('You do not have permission to edit this carpool.', 'danger')
        return redirect(url_for('carpools.index'))
    
    form = CarpoolForm()
    
    if request.method == 'GET':
        form.name.data = carpool.name
        form.origin.data = carpool.origin
        form.destination.data = carpool.destination
        form.departure_time.data = carpool.departure_time
        form.return_time.data = carpool.return_time
        form.max_passengers.data = carpool.max_passengers
        form.notes.data = carpool.notes
    
    if form.validate_on_submit():
        updated = update_carpool(
            carpool_id=id,
            name=form.name.data,
            origin=form.origin.data,
            destination=form.destination.data,
            departure_time=form.departure_time.data,
            return_time=form.return_time.data,
            max_passengers=form.max_passengers.data,
            notes=form.notes.data
        )
        
        if updated:
            log_action('update_carpool', current_user.username)
            logger.info(f"Updated carpool: {id} by {current_user.username}")
            flash(f'Carpool "{updated.name}" has been updated.', 'success')
            return redirect(url_for('carpools.view', id=id))
        else:
            flash('An error occurred while updating the carpool.', 'danger')
    
    return render_template('carpools/form.html', title='Edit Carpool', form=form, carpool=carpool)

@carpools.route('/view/<int:id>')
@login_required
def view(id):
    """
    View details of a specific carpool.
    
    :param id: ID of the carpool to view
    :return: Rendered template
    """
    carpool = get_carpool(id)
    
    if not carpool:
        flash('Carpool not found.', 'danger')
        return redirect(url_for('carpools.index'))
    
    join_form = JoinCarpoolForm()
    leave_form = LeaveCarpoolForm()
    cancel_form = CancelCarpoolForm()
    
    # Determine if the current user is the driver or a passenger
    is_driver = carpool.driver_id == current_user.username
    is_passenger = current_user in carpool.passengers
    can_join = carpool.can_join() and not is_driver and not is_passenger
    
    return render_template(
        'carpools/view.html',
        title=f'Carpool: {carpool.name}',
        carpool=carpool,
        join_form=join_form,
        leave_form=leave_form,
        cancel_form=cancel_form,
        is_driver=is_driver,
        is_passenger=is_passenger,
        can_join=can_join
    )

@carpools.route('/join/<int:id>', methods=['POST'])
@login_required
def join(id):
    """
    Join a carpool as a passenger.
    
    :param id: ID of the carpool to join
    :return: Redirect
    """
    form = JoinCarpoolForm()
    
    if form.validate_on_submit():
        carpool = get_carpool(id)
        
        if not carpool:
            flash('Carpool not found.', 'danger')
            return redirect(url_for('carpools.index'))
        
        # Check if user is already in this carpool
        if current_user in carpool.passengers:
            flash('You are already a passenger in this carpool.', 'warning')
            return redirect(url_for('carpools.view', id=id))
        
        # Check if user is the driver
        if carpool.driver_id == current_user.username:
            flash('You are the driver of this carpool.', 'warning')
            return redirect(url_for('carpools.view', id=id))
        
        success = join_carpool(id, current_user.username)
        
        if success:
            log_action('join_carpool', current_user.username)
            logger.info(f"User {current_user.username} joined carpool {id}")
            flash('You have successfully joined the carpool.', 'success')
        else:
            flash('Unable to join the carpool. It may be full or no longer active.', 'danger')
    
    return redirect(url_for('carpools.view', id=id))

@carpools.route('/leave/<int:id>', methods=['POST'])
@login_required
def leave(id):
    """
    Leave a carpool as a passenger.
    
    :param id: ID of the carpool to leave
    :return: Redirect
    """
    form = LeaveCarpoolForm()
    
    if form.validate_on_submit():
        success = leave_carpool(id, current_user.username)
        
        if success:
            log_action('leave_carpool', current_user.username)
            logger.info(f"User {current_user.username} left carpool {id}")
            flash('You have successfully left the carpool.', 'success')
        else:
            flash('Unable to leave the carpool.', 'danger')
    
    return redirect(url_for('carpools.view', id=id))

@carpools.route('/cancel/<int:id>', methods=['POST'])
@login_required
def cancel(id):
    """
    Cancel a carpool (set status to cancelled).
    
    :param id: ID of the carpool to cancel
    :return: Redirect
    """
    form = CancelCarpoolForm()
    
    if form.validate_on_submit():
        carpool = get_carpool(id)
        
        if not carpool:
            flash('Carpool not found.', 'danger')
            return redirect(url_for('carpools.index'))
        
        # Only the driver or an admin can cancel a carpool
        if carpool.driver_id != current_user.username and not current_user.is_admin():
            flash('You do not have permission to cancel this carpool.', 'danger')
            return redirect(url_for('carpools.view', id=id))
        
        updated = update_carpool(
            carpool_id=id,
            status='cancelled'
        )
        
        if updated:
            log_action('cancel_carpool', current_user.username)
            logger.info(f"Carpool {id} cancelled by {current_user.username}")
            flash('The carpool has been cancelled.', 'success')
        else:
            flash('An error occurred while cancelling the carpool.', 'danger')
    
    return redirect(url_for('carpools.view', id=id))

@carpools.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """
    Delete a carpool.
    
    :param id: ID of the carpool to delete
    :return: Redirect
    """
    carpool = get_carpool(id)
    
    if not carpool:
        flash('Carpool not found.', 'danger')
        return redirect(url_for('carpools.index'))
    
    # Only an admin can delete a carpool
    if not current_user.is_admin():
        flash('You do not have permission to delete carpools.', 'danger')
        return redirect(url_for('carpools.view', id=id))
    
    success = delete_carpool(id)
    
    if success:
        log_action('delete_carpool', current_user.username)
        logger.info(f"Carpool {id} deleted by {current_user.username}")
        flash('The carpool has been deleted.', 'success')
    else:
        flash('An error occurred while deleting the carpool.', 'danger')
    
    return redirect(url_for('carpools.index'))
