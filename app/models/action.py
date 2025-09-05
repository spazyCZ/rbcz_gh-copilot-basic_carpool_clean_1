"""
Action model for audit logging and system activity tracking.

This module defines the Action model for storing all significant
system activities for auditing and monitoring purposes.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
import json

from app.extensions import db


class ActionType:
    """Constants for different types of actions that can be logged."""
    
    # Reservation actions
    RESERVATION_CREATE = "RESERVATION_CREATE"
    RESERVATION_UPDATE = "RESERVATION_UPDATE"
    RESERVATION_DELETE = "RESERVATION_DELETE"
    
    # Authentication actions
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    
    # User management actions
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    
    # System actions
    BACKUP_START = "BACKUP_START"
    BACKUP_FINISH = "BACKUP_FINISH"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"
    
    # Admin actions
    ADMIN_LOGIN = "ADMIN_LOGIN"
    ADMIN_ACTION = "ADMIN_ACTION"
    CONFIG_CHANGE = "CONFIG_CHANGE"


class Action(db.Model):
    """
    Action model for storing audit trail and system activity logs.
    
    Records all significant system activities with user context,
    timestamps, and optional metadata for comprehensive auditing.
    """
    
    __tablename__ = 'actions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    
    # User context (nullable for system actions)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Request context
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    user_agent = db.Column(db.String(255), nullable=True)
    request_path = db.Column(db.String(255), nullable=True)
    
    # Additional metadata (stored as JSON)
    extra_data = db.Column(db.Text, nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    def __init__(self, action_type: str, description: str, user_id: Optional[int] = None,
                 ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                 request_path: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize a new Action instance.
        
        :param action_type: Type of action (use ActionType constants)
        :param description: Human-readable description of the action
        :param user_id: ID of user who performed the action (None for system actions)
        :param ip_address: IP address of the request
        :param user_agent: User agent string from the request
        :param request_path: Request path that triggered the action
        :param extra_data: Additional data about the action
        """
        self.action_type = action_type
        self.description = description
        self.user_id = user_id
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.request_path = request_path
        
        if extra_data:
            self.extra_data = json.dumps(extra_data)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata as parsed dictionary.
        
        :return: Metadata dictionary or empty dict if none
        """
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_metadata(self, extra_data: Dict[str, Any]) -> None:
        """
        Set metadata from dictionary.
        
        :param extra_data: Dictionary to store as JSON metadata
        """
        self.extra_data = json.dumps(extra_data) if extra_data else None
    
    def to_dict(self, include_user: bool = False) -> dict:
        """
        Convert action instance to dictionary representation.
        
        :param include_user: Whether to include user information
        :return: Dictionary representation of action
        """
        data = {
            'id': self.id,
            'action_type': self.action_type,
            'description': self.description,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_path': self.request_path,
            'metadata': self.get_metadata(),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
        
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            }
        
        return data
    
    @classmethod
    def log_action(cls, action_type: str, description: str, user_id: Optional[int] = None,
                   ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                   request_path: Optional[str] = None, extra_data: Optional[Dict[str, Any]] = None) -> 'Action':
        """
        Create and save a new action log entry.
        
        :param action_type: Type of action (use ActionType constants)
        :param description: Human-readable description
        :param user_id: ID of user who performed the action
        :param ip_address: IP address of the request
        :param user_agent: User agent string
        :param request_path: Request path
        :param extra_data: Additional data about the action
        :return: Created action instance
        """
        action = cls(
            action_type=action_type,
            description=description,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            extra_data=extra_data
        )
        
        db.session.add(action)
        db.session.commit()
        return action
    
    @classmethod
    def get_recent_actions(cls, limit: int = 50, action_type: Optional[str] = None,
                          user_id: Optional[int] = None) -> List['Action']:
        """
        Get recent actions with optional filtering.
        
        :param limit: Maximum number of actions to return
        :param action_type: Filter by action type
        :param user_id: Filter by user ID
        :return: List of recent actions
        """
        query = cls.query
        
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_actions_by_date_range(cls, start_date: datetime, end_date: datetime,
                                 action_type: Optional[str] = None) -> List['Action']:
        """
        Get actions within a date range.
        
        :param start_date: Start of date range
        :param end_date: End of date range
        :param action_type: Optional action type filter
        :return: List of actions in date range
        """
        query = cls.query.filter(
            cls.timestamp >= start_date,
            cls.timestamp <= end_date
        )
        
        if action_type:
            query = query.filter_by(action_type=action_type)
        
        return query.order_by(cls.timestamp.desc()).all()
    
    @classmethod
    def get_user_actions(cls, user_id: int, limit: int = 100) -> List['Action']:
        """
        Get all actions performed by a specific user.
        
        :param user_id: User ID to get actions for
        :param limit: Maximum number of actions to return
        :return: List of user actions
        """
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.timestamp.desc()
        ).limit(limit).all()
    
    @classmethod
    def cleanup_old_actions(cls, days_to_keep: int = 180) -> int:
        """
        Clean up old action records to manage database size.
        
        :param days_to_keep: Number of days of actions to keep
        :return: Number of actions deleted
        """
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days_to_keep)
        
        # Count actions to be deleted
        count = cls.query.filter(cls.timestamp < cutoff_date).count()
        
        # Delete old actions
        cls.query.filter(cls.timestamp < cutoff_date).delete()
        db.session.commit()
        
        return count
    
    def __repr__(self) -> str:
        """String representation of Action instance."""
        return f'<Action {self.action_type} at {self.timestamp}>'