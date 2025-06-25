"""
This module defines the Action model that represents system actions.
"""
from datetime import datetime
from carpool.extensions import db

class Action(db.Model):
    """
    A class representing a system action.
    
    Attributes:
        id (int): Unique action identifier
        action_type (str): The type of action performed
        username (str): The username of the user who performed the action
        timestamp (datetime): When the action occurred
    """
    __tablename__ = 'actions'
    
    id = db.Column(db.Integer, primary_key=True)
    action_type = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(64), db.ForeignKey('users.username'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, action_type: str, username: str) -> None:
        """
        Initialize a new Action instance.
        
        :param action_type: Type of action performed
        :param username: Username of the user who performed the action
        """
        self.action_type = action_type
        self.username = username
    
    def __repr__(self) -> str:
        """
        Return a string representation of the Action.
        
        :return: String representation
        """
        return f'<Action {self.id}: {self.action_type} by {self.username} at {self.timestamp}>'
