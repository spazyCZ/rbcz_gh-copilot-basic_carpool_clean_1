"""
This module provides service methods for user management.
"""
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
import logging

from carpool.extensions import db
from carpool.models.user import User

logger = logging.getLogger(__name__)

def get_all_users() -> List[User]:
    """
    Get all users.
    
    :return: List of users
    """
    try:
        return User.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving users: {e}")
        return []

def get_user(username: str) -> Optional[User]:
    """
    Get a user by username.
    
    :param username: Username of the user
    :return: User object or None if not found
    """
    try:
        return User.query.get(username)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user {username}: {e}")
        return None

def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email.
    
    :param email: Email of the user
    :return: User object or None if not found
    """
    try:
        return User.query.filter_by(email=email).first()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving user with email {email}: {e}")
        return None

def create_user(username: str, email: str, password: str, role: str = 'user') -> Optional[User]:
    """
    Create a new user.
    
    :param username: Username for the new user
    :param email: Email for the new user
    :param password: Password for the new user
    :param role: Role for the new user, defaults to 'user'
    :return: Created User or None if error
    """
    try:
        # Check if username or email already exists
        if User.query.get(username) or User.query.filter_by(email=email).first():
            logger.warning(f"Username {username} or email {email} already exists")
            return None
        
        user = User(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        logger.info(f"Created user: {username}")
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating user {username}: {e}")
        return None

def update_user(username: str, email: str = None, password: str = None, role: str = None) -> Optional[User]:
    """
    Update an existing user.
    
    :param username: Username of the user to update
    :param email: New email or None to keep current
    :param password: New password or None to keep current
    :param role: New role or None to keep current
    :return: Updated User or None if error
    """
    try:
        user = User.query.get(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return None
        
        if email:
            # Check if email is already used by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.username != username:
                logger.warning(f"Email {email} already in use by another user")
                return None
            user.email = email
            
        if password:
            user.password = password
            
        if role:
            user.role = role
        
        db.session.commit()
        logger.info(f"Updated user: {username}")
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating user {username}: {e}")
        return None

def delete_user(username: str) -> bool:
    """
    Delete a user.
    
    :param username: Username of the user to delete
    :return: True if successful, False otherwise
    """
    try:
        user = User.query.get(username)
        if not user:
            logger.warning(f"User not found: {username}")
            return False
        
        db.session.delete(user)
        db.session.commit()
        logger.info(f"Deleted user: {username}")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting user {username}: {e}")
        return False
