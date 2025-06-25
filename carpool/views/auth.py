"""
This module defines authentication-related routes.
"""
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse

from carpool.forms.auth_forms import LoginForm, RegistrationForm
from carpool.services.user_service import get_user, create_user
from carpool.services.action_service import log_action

auth = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    
    :return: Rendered template or redirect
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.username.data)
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password', 'danger')
            logger.warning(f"Failed login attempt for username: {form.username.data}")
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        log_action('user_login', user.username)
        logger.info(f"User logged in: {user.username}")
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Log In', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    Handle user logout.
    
    :return: Redirect to index
    """
    username = current_user.username
    logout_user()
    log_action('user_logout', username)
    logger.info(f"User logged out: {username}")
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.
    
    :return: Rendered template or redirect
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if user:
            log_action('user_registration', user.username)
            logger.info(f"New user registered: {user.username}")
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', title='Register', form=form)
