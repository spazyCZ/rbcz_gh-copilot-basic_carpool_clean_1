"""
Authentication API endpoints.

Handles user login, logout, and session management.
"""
from flask import request, jsonify, current_app, session
from flask_login import login_user, logout_user, current_user, login_required

from app.api import api_bp
from app.models import User, Action, ActionType
from app.extensions import db, limiter


@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """
    User login endpoint.
    
    Authenticates user credentials and creates session.
    Rate limited to prevent brute force attacks.
    
    :return: JSON response with user data or error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Request body must contain JSON data'
                }
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not username or not password:
            return jsonify({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Username and password are required'
                }
            }), 400
        
        # Find user by username
        user = User.find_by_username(username)
        
        if not user or not user.check_password(password):
            # Log failed login attempt
            Action.log_action(
                action_type=ActionType.LOGIN_FAILURE,
                description=f"Failed login attempt for username: {username}",
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                request_path=request.path,
                extra_data={'username': username}
            )
            
            return jsonify({
                'error': {
                    'code': 'AUTH_INVALID',
                    'message': 'Invalid username or password'
                }
            }), 401
        
        if not user.is_active:
            return jsonify({
                'error': {
                    'code': 'AUTH_INVALID',
                    'message': 'Account is deactivated'
                }
            }), 401
        
        # Login user
        login_user(user, remember=remember)
        user.update_last_login()
        
        # Log successful login
        Action.log_action(
            action_type=ActionType.LOGIN_SUCCESS,
            description=f"Successful login for user: {user.username}",
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_path=request.path
        )
        
        current_app.logger.info(f"User {user.username} logged in successfully")
        
        return jsonify({
            'data': {
                'user': user.to_dict(),
                'message': 'Login successful'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Login failed due to server error'
            }
        }), 500


@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """
    User logout endpoint.
    
    Ends user session and logs the action.
    
    :return: JSON response confirming logout
    """
    try:
        user_id = current_user.id
        username = current_user.username
        
        # Log logout action
        Action.log_action(
            action_type=ActionType.LOGOUT,
            description=f"User logout: {username}",
            user_id=user_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            request_path=request.path
        )
        
        logout_user()
        
        current_app.logger.info(f"User {username} logged out")
        
        return jsonify({
            'data': {
                'message': 'Logout successful'
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {e}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Logout failed due to server error'
            }
        }), 500