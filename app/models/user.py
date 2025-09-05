"""
User model for authentication and authorization.

This module defines the User model for storing user accounts with
secure password hashing and Flask-Login integration.
"""
from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    """
    User model for storing user account information.
    
    Integrates with Flask-Login for session management and provides
    secure password hashing using Werkzeug.
    """
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User identification and authentication
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User roles and status
    role = db.Column(db.String(20), nullable=False, default='user', index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    actions = db.relationship('Action', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username: str, email: str, password: str, role: str = 'user') -> None:
        """
        Initialize a new User instance.
        
        :param username: Unique username for the user
        :param email: Unique email address for the user
        :param password: Plain text password (will be hashed)
        :param role: User role ('user', 'admin', 'guest')
        """
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
    
    def set_password(self, password: str) -> None:
        """
        Set user password with secure hashing.
        
        :param password: Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check if provided password matches the stored hash.
        
        :param password: Plain text password to verify
        :return: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """
        Check if user has administrator privileges.
        
        :return: True if user is an admin, False otherwise
        """
        return self.role == 'admin'
    
    def update_last_login(self) -> None:
        """Update the last login timestamp to current time."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert user instance to dictionary representation.
        
        :param include_sensitive: Whether to include sensitive fields
        :return: Dictionary representation of user
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            # Only include in administrative contexts
            data['password_hash'] = self.password_hash
            
        return data
    
    @classmethod
    def find_by_username(cls, username: str) -> Optional['User']:
        """
        Find user by username.
        
        :param username: Username to search for
        :return: User instance or None if not found
        """
        return cls.query.filter_by(username=username, is_active=True).first()
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """
        Find user by email address.
        
        :param email: Email address to search for
        :return: User instance or None if not found
        """
        return cls.query.filter_by(email=email, is_active=True).first()
    
    @classmethod
    def create_user(cls, username: str, email: str, password: str, role: str = 'user') -> 'User':
        """
        Create a new user and save to database.
        
        :param username: Unique username
        :param email: Unique email address
        :param password: Plain text password
        :param role: User role
        :return: Created user instance
        :raises: IntegrityError if username or email already exists
        """
        user = cls(username=username, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return user
    
    def __repr__(self) -> str:
        """String representation of User instance."""
        return f'<User {self.username}>'