"""
Authentication service for user management and security.

This module provides authentication and user management functionality including
password hashing, user validation, and login/logout operations.
"""

import bcrypt
from typing import Optional
from flask import current_app
from flask_login import login_user, logout_user
from carpool.models.user import User
from carpool.models.action import Action
from extensions import db


class AuthService:
    """
    Authentication service class providing user management and security operations.
    
    Handles password hashing, user validation, login/logout operations, and user creation.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        :param password: Plain text password to hash
        :return: Hashed password string
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        :param password: Plain text password to verify
        :param hashed_password: Hashed password to check against
        :return: True if password matches, False otherwise
        """
        try:
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            current_app.logger.error(f'Password verification error: {e}')
            return False
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        :param username: Username to authenticate
        :param password: Password to verify
        :return: User object if authentication successful, None otherwise
        """
        try:
            user = User.query.filter_by(username=username).first()
            if user and AuthService.verify_password(password, user.password_hash):
                current_app.logger.info(f'Successful authentication for user: {username}')
                return user
            
            current_app.logger.warning(f'Failed authentication attempt for user: {username}')
            return None
            
        except Exception as e:
            current_app.logger.error(f'Authentication error for user {username}: {e}')
            return None
    
    @staticmethod
    def login_user_session(user: User, remember_me: bool = False) -> bool:
        """
        Log in a user and create a session.
        
        :param user: User object to log in
        :param remember_me: Whether to remember the user session
        :return: True if login successful, False otherwise
        """
        try:
            success = login_user(user, remember=remember_me)
            if success:
                # Log the login action
                Action.log_login(user.username)
                current_app.logger.info(f'User logged in: {user.username}')
            return success
            
        except Exception as e:
            current_app.logger.error(f'Login error for user {user.username}: {e}')
            return False
    
    @staticmethod
    def logout_user_session() -> bool:
        """
        Log out the current user and clear the session.
        
        :return: True if logout successful, False otherwise
        """
        try:
            from flask_login import current_user
            if current_user.is_authenticated:
                username = current_user.username
                logout_user()
                # Log the logout action
                Action.log_logout(username)
                current_app.logger.info(f'User logged out: {username}')
                return True
            return False
            
        except Exception as e:
            current_app.logger.error(f'Logout error: {e}')
            return False
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = 'user') -> Optional[User]:
        """
        Create a new user account.
        
        :param username: Unique username for the user
        :param email: User's email address
        :param password: Plain text password (will be hashed)
        :param role: User's role (default: 'user')
        :return: Created User object if successful, None otherwise
        """
        try:
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                current_app.logger.warning(f'Attempted to create user with existing username: {username}')
                return None
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                current_app.logger.warning(f'Attempted to create user with existing email: {email}')
                return None
            
            # Create new user
            user = User(username=username, email=email, role=role)
            user.password_hash = AuthService.hash_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Log the user creation
            Action.log_action('user_created', 'system', f'User {username} created with role {role}')
            current_app.logger.info(f'New user created: {username} with role {role}')
            
            return user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating user {username}: {e}')
            return None
    
    @staticmethod
    def update_user_password(user: User, new_password: str) -> bool:
        """
        Update a user's password.
        
        :param user: User object to update
        :param new_password: New plain text password
        :return: True if update successful, False otherwise
        """
        try:
            user.password_hash = AuthService.hash_password(new_password)
            db.session.commit()
            
            # Log the password change
            Action.log_action('password_changed', user.username, 'User changed password')
            current_app.logger.info(f'Password updated for user: {user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating password for user {user.username}: {e}')
            return False
    
    @staticmethod
    def update_user_role(user: User, new_role: str, admin_username: str) -> bool:
        """
        Update a user's role (admin only operation).
        
        :param user: User object to update
        :param new_role: New role for the user
        :param admin_username: Username of the admin making the change
        :return: True if update successful, False otherwise
        """
        try:
            old_role = user.role
            user.role = new_role
            db.session.commit()
            
            # Log the role change
            details = f'Changed user {user.username} role from {old_role} to {new_role}'
            Action.log_admin_action(admin_username, details)
            current_app.logger.info(f'Role updated for user {user.username}: {old_role} -> {new_role}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating role for user {user.username}: {e}')
            return False
    
    @staticmethod
    def delete_user(user: User, admin_username: str) -> bool:
        """
        Delete a user account (admin only operation).
        
        :param user: User object to delete
        :param admin_username: Username of the admin performing the deletion
        :return: True if deletion successful, False otherwise
        """
        try:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            
            # Log the user deletion
            Action.log_admin_action(admin_username, f'Deleted user account: {username}')
            current_app.logger.info(f'User deleted: {username} by admin {admin_username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting user {user.username}: {e}')
            return False
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get a user by their ID.
        
        :param user_id: ID of the user to retrieve
        :return: User object if found, None otherwise
        """
        try:
            return User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(f'Error retrieving user by ID {user_id}: {e}')
            return None
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get a user by their username.
        
        :param username: Username of the user to retrieve
        :return: User object if found, None otherwise
        """
        try:
            return User.query.filter_by(username=username).first()
        except Exception as e:
            current_app.logger.error(f'Error retrieving user by username {username}: {e}')
            return None
