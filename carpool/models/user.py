"""
User model for authentication and authorization.

This module defines the User model with authentication capabilities and role-based access control.
"""

from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    """
    User model for managing user accounts with role-based access control.
    
    Inherits from UserMixin to provide Flask-Login integration for session management.
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # administrator, user, guest
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True, cascade='all, delete-orphan')
    organized_carpools = db.relationship('Carpool', backref='organizer', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username: str, email: str, role: str = 'user'):
        """
        Initialize a new User instance.
        
        :param username: Unique username for the user
        :param email: User's email address
        :param role: User's role (administrator, user, guest)
        """
        self.username = username
        self.email = email
        self.role = role
    
    def __repr__(self) -> str:
        """
        String representation of the User object.
        
        :return: User representation string
        """
        return f'<User {self.username}>'
    
    def is_admin(self) -> bool:
        """
        Check if the user has administrator privileges.
        
        :return: True if user is an administrator, False otherwise
        """
        return self.role == 'administrator'
    
    def can_make_reservation(self) -> bool:
        """
        Check if the user can make parking reservations.
        
        :return: True if user can make reservations, False otherwise
        """
        return self.role in ['administrator', 'user']
    
    def can_organize_carpool(self) -> bool:
        """
        Check if the user can organize carpool trips.
        
        :return: True if user can organize carpools, False otherwise
        """
        return self.role in ['administrator', 'user']
    
    def to_dict(self) -> dict:
        """
        Convert User object to dictionary representation.
        
        :return: Dictionary containing user data
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reservations_count': len(self.reservations),
            'carpools_organized': len(self.organized_carpools)
        }
