"""
Authentication views and routes for the carpool application.

This module contains the authentication blueprint with routes for login,
logout, registration, and password management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from carpool.forms.auth_forms import LoginForm, RegisterForm, ChangePasswordForm, ForgotPasswordForm
from carpool.services.auth_service import AuthService
from carpool.models.action import Action

# Create authentication blueprint
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route - handles authentication form submission.
    
    :return: Rendered login template or redirect response
    """
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            # Check if input is email or username
            username_or_email = form.username.data.strip()
            
            # Try to find user by username first, then by email
            user = AuthService.get_user_by_username(username_or_email)
            if not user:
                # Try to find by email
                from carpool.models.user import User
                user = User.query.filter_by(email=username_or_email).first()
            
            # Authenticate user
            if user:
                authenticated_user = AuthService.authenticate_user(user.username, form.password.data)
                if authenticated_user:
                    # Log in the user
                    success = AuthService.login_user_session(authenticated_user, form.remember_me.data)
                    if success:
                        flash(f'Welcome back, {authenticated_user.username}!', 'success')
                        
                        # Redirect to next page or dashboard
                        next_page = request.args.get('next')
                        if next_page:
                            return redirect(next_page)
                        return redirect(url_for('main.dashboard'))
                    else:
                        flash('Login failed. Please try again.', 'error')
                else:
                    flash('Invalid username/email or password.', 'error')
            else:
                flash('Invalid username/email or password.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Login error: {e}')
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route - handles user session termination.
    
    :return: Redirect response to home page
    """
    try:
        username = current_user.username if current_user.is_authenticated else 'Unknown'
        
        # Log out the user
        success = AuthService.logout_user_session()
        if success:
            flash('You have been logged out successfully.', 'info')
        else:
            flash('Logout failed.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Logout error: {e}')
        flash('An error occurred during logout.', 'error')
    
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route - handles new account creation.
    
    :return: Rendered registration template or redirect response
    """
    # Redirect if user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Create new user account
            user = AuthService.create_user(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                password=form.password.data,
                role='user'  # Default role for new registrations
            )
            
            if user:
                flash(f'Registration successful! Welcome, {user.username}!', 'success')
                
                # Automatically log in the new user
                success = AuthService.login_user_session(user, remember=False)
                if success:
                    return redirect(url_for('main.dashboard'))
                else:
                    flash('Registration successful! Please log in.', 'info')
                    return redirect(url_for('auth.login'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Registration error: {e}')
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    Change password route - handles password update for logged-in users.
    
    :return: Rendered change password template or redirect response
    """
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            # Verify current password
            if not AuthService.verify_password(form.current_password.data, current_user.password_hash):
                flash('Current password is incorrect.', 'error')
                return render_template('auth/change_password.html', form=form)
            
            # Update password
            success = AuthService.update_user_password(current_user, form.new_password.data)
            if success:
                flash('Password changed successfully!', 'success')
                return redirect(url_for('main.profile'))
            else:
                flash('Failed to change password. Please try again.', 'error')
                
        except Exception as e:
            current_app.logger.error(f'Password change error for user {current_user.username}: {e}')
            flash('An error occurred while changing password. Please try again.', 'error')
    
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """
    Forgot password route - handles password reset requests.
    
    Note: This is a placeholder implementation. In production, you would
    implement email-based password reset functionality.
    
    :return: Rendered forgot password template
    """
    form = ForgotPasswordForm()
    
    if form.validate_on_submit():
        try:
            email = form.email.data.strip().lower()
            
            # Check if email exists in database
            from carpool.models.user import User
            user = User.query.filter_by(email=email).first()
            
            if user:
                # In a real implementation, you would:
                # 1. Generate a secure reset token
                # 2. Send password reset email
                # 3. Store token with expiration
                current_app.logger.info(f'Password reset requested for email: {email}')
                
            # Always show the same message for security (don't reveal if email exists)
            flash('If an account with that email exists, you will receive password reset instructions.', 'info')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            current_app.logger.error(f'Error in forgot password for email {form.email.data}: {e}')
            flash('An error occurred. Please try again.', 'error')
            return render_template('auth/forgot_password.html', form=form)
    
    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/account-info')
@login_required
def account_info():
    """
    Account information route - displays user account details.
    
    :return: Rendered account info template
    """
    try:
        # Get user's activity statistics
        from carpool.services.reservation_service import ReservationService
        from carpool.services.carpool_service import CarpoolService
        
        total_reservations = len(ReservationService.get_user_reservations(current_user, include_past=True))
        total_carpools = len(CarpoolService.get_user_carpools(current_user, include_past=True))
        
        # Get recent activity logs for this user
        recent_actions = Action.query.filter_by(username=current_user.username).order_by(Action.timestamp.desc()).limit(10).all()
        
        return render_template('auth/account_info.html',
                             total_reservations=total_reservations,
                             total_carpools=total_carpools,
                             recent_actions=recent_actions)
                             
    except Exception as e:
        current_app.logger.error(f'Error loading account info for user {current_user.username}: {e}')
        flash('Error loading account information. Please try again.', 'error')
        return redirect(url_for('main.profile'))


# Error handlers for authentication blueprint
@auth_bp.errorhandler(401)
def unauthorized(error):
    """
    Handle unauthorized access attempts.
    
    :param error: The error object
    :return: Redirect to login page
    """
    flash('Please log in to access this page.', 'warning')
    return redirect(url_for('auth.login'))


@auth_bp.errorhandler(403)
def forbidden(error):
    """
    Handle forbidden access attempts.
    
    :param error: The error object
    :return: Rendered error template
    """
    return render_template('errors/403.html'), 403
