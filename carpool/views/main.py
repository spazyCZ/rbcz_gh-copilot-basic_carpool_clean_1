"""
This module defines the main routes of the application.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from carpool.services.parking_service import get_all_parking_spots
from carpool.services.reservation_service import get_all_reservations, get_user_reservations
from carpool.services.action_service import get_recent_actions

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    """
    Render the home page.
    
    :return: Rendered template
    """
    total_spots = len(get_all_parking_spots())
    total_reservations = len(get_all_reservations())
    
    # If user is logged in, get their reservations
    user_reservations = []
    if current_user.is_authenticated:
        user_reservations = get_user_reservations(current_user.username)
    
    return render_template(
        'main/index.html',
        title='Home',
        total_spots=total_spots,
        total_reservations=total_reservations,
        user_reservations=user_reservations
    )

@main.route('/dashboard')
@login_required
def dashboard():
    """
    Render the user dashboard.
    
    :return: Rendered template
    """
    # Get user's reservations
    user_reservations = get_user_reservations(current_user.username)
    
    # If admin, get recent actions
    recent_actions = []
    if current_user.is_admin():
        recent_actions = get_recent_actions(10)
    
    return render_template(
        'main/dashboard.html',
        title='Dashboard',
        user_reservations=user_reservations,
        recent_actions=recent_actions
    )

@main.route('/profile')
@login_required
def profile():
    """
    Render the user profile page.
    
    :return: Rendered template
    """
    return render_template('main/profile.html', title='My Profile')
