"""
This module defines routes for admin functionality.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from carpool.extensions import db
from carpool.forms.auth_forms import UserForm
from carpool.services.user_service import get_all_users, get_user, create_user, update_user, delete_user
from carpool.services.action_service import log_action, get_recent_actions, get_action_count_by_type

admin = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

@admin.before_request
def check_admin():
    """
    Ensure only administrators can access admin routes.
    """
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('You do not have permission to access the admin area.', 'danger')
        return redirect(url_for('main.index'))

@admin.route('/')
@login_required
def index():
    """
    Admin dashboard.
    
    :return: Rendered template
    """
    recent_actions = get_recent_actions(10)
    action_counts = get_action_count_by_type()
    
    return render_template(
        'admin/index.html',
        title='Admin Dashboard',
        recent_actions=recent_actions,
        action_counts=action_counts
    )

@admin.route('/users')
@login_required
def users():
    """
    List all users.
    
    :return: Rendered template
    """
    all_users = get_all_users()
    return render_template(
        'admin/users.html',
        title='User Management',
        users=all_users
    )

@admin.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    """
    Create a new user.
    
    :return: Rendered template or redirect
    """
    form = UserForm()
    if form.validate_on_submit():
        user = create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data
        )
        
        if user:
            log_action('admin_create_user', current_user.username)
            logger.info(f"Admin {current_user.username} created user: {user.username}")
            flash(f'User {user.username} has been created.', 'success')
            return redirect(url_for('admin.users'))
        else:
            flash('An error occurred while creating the user.', 'danger')
    
    return render_template('admin/user_form.html', title='New User', form=form)

@admin.route('/users/edit/<string:username>', methods=['GET', 'POST'])
@login_required
def edit_user(username):
    """
    Edit an existing user.
    
    :param username: Username of the user to edit
    :return: Rendered template or redirect
    """
    user = get_user(username)
    if not user:
        flash(f'User {username} not found.', 'danger')
        return redirect(url_for('admin.users'))
    
    form = UserForm(original_username=username)
    if request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
        form.role.data = user.role
    
    if form.validate_on_submit():
        # Update username requires special handling since it's the primary key
        if form.username.data != username:
            # Create new user with new username and copy data
            new_user = create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data if form.password.data else 'dummy',  # Will be replaced if no new password
                role=form.role.data
            )
            
            if new_user:
                # If no new password provided, copy the password hash from old user
                if not form.password.data:
                    new_user.password_hash = user.password_hash
                    db.session.commit()
                
                # Delete old user
                delete_user(username)
                log_action('admin_rename_user', current_user.username)
                logger.info(f"Admin {current_user.username} renamed user: {username} to {new_user.username}")
                flash(f'User {username} has been renamed to {new_user.username}.', 'success')
                return redirect(url_for('admin.users'))
            else:
                flash('An error occurred while renaming the user.', 'danger')
        else:
            # Regular update
            updated_user = update_user(
                username=username,
                email=form.email.data,
                password=form.password.data if form.password.data else None,
                role=form.role.data
            )
            
            if updated_user:
                log_action('admin_update_user', current_user.username)
                logger.info(f"Admin {current_user.username} updated user: {username}")
                flash(f'User {username} has been updated.', 'success')
                return redirect(url_for('admin.users'))
            else:
                flash('An error occurred while updating the user.', 'danger')
    
    return render_template('admin/user_form.html', title='Edit User', form=form)

@admin.route('/users/delete/<string:username>', methods=['POST'])
@login_required
def delete_user(username):
    """
    Delete a user.
    
    :param username: Username of the user to delete
    :return: Redirect to users list
    """
    # Prevent admin from deleting themselves
    if username == current_user.username:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    if delete_user(username):
        log_action('admin_delete_user', current_user.username)
        logger.info(f"Admin {current_user.username} deleted user: {username}")
        flash(f'User {username} has been deleted.', 'success')
    else:
        flash(f'An error occurred while deleting user {username}.', 'danger')
    
    return redirect(url_for('admin.users'))

@admin.route('/logs')
@login_required
def logs():
    """
    View system logs.
    
    :return: Rendered template
    """
    # Get all actions, more recent first
    all_actions = get_recent_actions(limit=500)
    
    return render_template(
        'admin/logs.html',
        title='System Logs',
        actions=all_actions
    )
