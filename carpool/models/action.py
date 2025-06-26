"""
Action model for system audit logging.

This module defines the Action model for tracking all user activities and system events.
"""

from datetime import datetime
from extensions import db


class Action(db.Model):
    """
    Action model for system audit logging.
    
    Tracks all user activities and system events for monitoring and debugging purposes.
    """
    
    __tablename__ = 'actions'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False, index=True)  # Type of action performed
    username = db.Column(db.String(80), nullable=False, index=True)  # User who performed the action
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    details = db.Column(db.Text, nullable=True)  # Additional action details
    
    def __init__(self, action_type: str, username: str, details: str = None):
        """
        Initialize a new Action instance.
        
        :param action_type: Type of action being logged
        :param username: Username of the user performing the action
        :param details: Additional details about the action
        """
        self.action_type = action_type
        self.username = username
        self.details = details
    
    def __repr__(self) -> str:
        """
        String representation of the Action object.
        
        :return: Action representation string
        """
        return f'<Action {self.action_type} by {self.username} at {self.timestamp}>'
    
    def to_dict(self) -> dict:
        """
        Convert Action object to dictionary representation.
        
        :return: Dictionary containing action data
        """
        return {
            'id': self.id,
            'action_type': self.action_type,
            'username': self.username,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'details': self.details,
            'formatted_timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }
    
    @staticmethod
    def log_action(action_type: str, username: str, details: str = None) -> 'Action':
        """
        Create and save a new action log entry.
        
        :param action_type: Type of action being logged
        :param username: Username of the user performing the action
        :param details: Additional details about the action
        :return: Created Action instance
        """
        action = Action(
            action_type=action_type,
            username=username,
            details=details
        )
        db.session.add(action)
        db.session.commit()
        return action
    
    @staticmethod
    def log_login(username: str) -> 'Action':
        """
        Log a user login action.
        
        :param username: Username of the user logging in
        :return: Created Action instance
        """
        return Action.log_action('user_login', username, f'User {username} logged in')
    
    @staticmethod
    def log_logout(username: str) -> 'Action':
        """
        Log a user logout action.
        
        :param username: Username of the user logging out
        :return: Created Action instance
        """
        return Action.log_action('user_logout', username, f'User {username} logged out')
    
    @staticmethod
    def log_reservation_created(username: str, spot_id: str, reservation_date: str) -> 'Action':
        """
        Log a reservation creation action.
        
        :param username: Username of the user creating the reservation
        :param spot_id: ID of the parking spot reserved
        :param reservation_date: Date of the reservation
        :return: Created Action instance
        """
        details = f'Created reservation for spot {spot_id} on {reservation_date}'
        return Action.log_action('reservation_created', username, details)
    
    @staticmethod
    def log_reservation_updated(username: str, reservation_id: int, spot_id: str) -> 'Action':
        """
        Log a reservation update action.
        
        :param username: Username of the user updating the reservation
        :param reservation_id: ID of the reservation being updated
        :param spot_id: ID of the parking spot
        :return: Created Action instance
        """
        details = f'Updated reservation {reservation_id} for spot {spot_id}'
        return Action.log_action('reservation_updated', username, details)
    
    @staticmethod
    def log_reservation_cancelled(username: str, reservation_id: int, spot_id: str) -> 'Action':
        """
        Log a reservation cancellation action.
        
        :param username: Username of the user cancelling the reservation
        :param reservation_id: ID of the reservation being cancelled
        :param spot_id: ID of the parking spot
        :return: Created Action instance
        """
        details = f'Cancelled reservation {reservation_id} for spot {spot_id}'
        return Action.log_action('reservation_cancelled', username, details)
    
    @staticmethod
    def log_carpool_created(username: str, carpool_name: str) -> 'Action':
        """
        Log a carpool creation action.
        
        :param username: Username of the user creating the carpool
        :param carpool_name: Name of the carpool trip
        :return: Created Action instance
        """
        details = f'Created carpool trip: {carpool_name}'
        return Action.log_action('carpool_created', username, details)
    
    @staticmethod
    def log_carpool_updated(username: str, carpool_id: int, carpool_name: str) -> 'Action':
        """
        Log a carpool update action.
        
        :param username: Username of the user updating the carpool
        :param carpool_id: ID of the carpool being updated
        :param carpool_name: Name of the carpool trip
        :return: Created Action instance
        """
        details = f'Updated carpool {carpool_id}: {carpool_name}'
        return Action.log_action('carpool_updated', username, details)
    
    @staticmethod
    def log_carpool_deleted(username: str, carpool_id: int, carpool_name: str) -> 'Action':
        """
        Log a carpool deletion action.
        
        :param username: Username of the user deleting the carpool
        :param carpool_id: ID of the carpool being deleted
        :param carpool_name: Name of the carpool trip
        :return: Created Action instance
        """
        details = f'Deleted carpool {carpool_id}: {carpool_name}'
        return Action.log_action('carpool_deleted', username, details)
    
    @staticmethod
    def log_admin_action(username: str, action_details: str) -> 'Action':
        """
        Log an administrative action.
        
        :param username: Username of the administrator
        :param action_details: Details of the administrative action
        :return: Created Action instance
        """
        return Action.log_action('admin_action', username, action_details)
