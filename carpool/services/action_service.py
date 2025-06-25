"""
This module provides service methods for logging system actions.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging

from carpool.extensions import db
from carpool.models.action import Action

logger = logging.getLogger(__name__)

def log_action(action_type: str, username: str) -> Optional[Action]:
    """
    Log a system action.
    
    :param action_type: Type of action performed
    :param username: Username of the user who performed the action
    :return: Created Action or None if error
    """
    try:
        action = Action(action_type=action_type, username=username)
        db.session.add(action)
        db.session.commit()
        return action
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error logging action {action_type} by {username}: {e}")
        return None

def get_recent_actions(limit: int = 100) -> List[Action]:
    """
    Get recent system actions.
    
    :param limit: Maximum number of actions to return
    :return: List of actions
    """
    try:
        return Action.query.order_by(Action.timestamp.desc()).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving recent actions: {e}")
        return []

def get_user_actions(username: str, limit: int = 100) -> List[Action]:
    """
    Get actions performed by a specific user.
    
    :param username: Username of the user
    :param limit: Maximum number of actions to return
    :return: List of actions
    """
    try:
        return Action.query.filter_by(username=username).order_by(Action.timestamp.desc()).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving actions for user {username}: {e}")
        return []

def get_action_count_by_type() -> dict:
    """
    Get count of actions grouped by type.
    
    :return: Dictionary with action types as keys and counts as values
    """
    try:
        result = {}
        for action_type, count in db.session.query(Action.action_type, db.func.count(Action.id)).group_by(Action.action_type).all():
            result[action_type] = count
        return result
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving action counts: {e}")
        return {}
