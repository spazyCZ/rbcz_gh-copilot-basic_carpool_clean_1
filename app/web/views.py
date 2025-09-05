"""
Web views for serving HTML templates.

These views provide minimal HTML shells that fetch data dynamically
via JavaScript calls to API endpoints. No business data is embedded directly.
"""
from flask import render_template, request, current_app
from flask_login import login_required, current_user

from app.web import web_bp


@web_bp.route('/')
def index():
    """
    Main dashboard view.
    
    Serves the main application dashboard with empty containers
    that will be populated via JavaScript API calls.
    
    :return: Rendered dashboard template
    """
    current_app.logger.info(f"Dashboard accessed from {request.remote_addr}")
    
    return render_template('index.html')


@web_bp.route('/login')
def login():
    """
    Login page view.
    
    Serves the login form template. Authentication is handled
    via JavaScript API calls to /api/v1/auth/login.
    
    :return: Rendered login template
    """
    current_app.logger.info(f"Login page accessed from {request.remote_addr}")
    
    return render_template('login.html')


@web_bp.route('/reservations')
@login_required
def reservations():
    """
    Reservations management view.
    
    Serves the reservations management interface. All reservation
    data is loaded dynamically via API endpoints.
    
    :return: Rendered reservations template
    """
    current_app.logger.info(f"Reservations page accessed by user {current_user.username}")
    
    return render_template('reservations.html')


@web_bp.route('/spots')
@login_required
def spots():
    """
    Parking spots view.
    
    Serves the parking spots overview with availability status.
    All spot data is loaded via API calls.
    
    :return: Rendered spots template
    """
    current_app.logger.info(f"Spots page accessed by user {current_user.username}")
    
    return render_template('spots.html')