"""
This module defines the User model that represents users in the application.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from carpool.extensions import db

class User(db.Model, UserMixin):
    """
    A class representing a user in the system.
    
    Attributes:
        username (str): The user's unique username
        password_hash (str): The hashed password
        role (str): The user's role (administrator, user, or guest)
        email (str): The user's email address
        created_at (datetime): When the user account was created
    """
    __tablename__ = 'users'
    
    username = db.Column(db.String(64), primary_key=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')
    actions = db.relationship('Action', backref='user', lazy='dynamic')
    
    def __init__(self, username: str, email: str, password: str, role: str = 'user') -> None:
        """
        Initialize a new User instance.
        
        :param username: User's unique username
        :param email: User's email address
        :param password: User's plain text password (will be hashed)
        :param role: User's role, defaults to 'user'
        """
        self.username = username
        self.email = email
        self.password = password
        self.role = role
    
    @property
    def password(self) -> None:
        """
        Prevent password from being accessed.
        
        :raises AttributeError: Always raised when password is accessed
        """
        raise AttributeError('Password is not a readable attribute')
    
    @password.setter
    def password(self, password: str) -> None:
        """
        Set password hash.
        
        :param password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the stored hash.
        
        :param password: Password to verify
        :return: True if the password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self) -> bool:
        """
        Check if the user has administrator role.
        
        :return: True if user is an administrator, False otherwise
        """
        return self.role == 'administrator'
    
    def get_id(self) -> str:
        """
        Override the get_id method required by Flask-Login.
        
        :return: The username as string
        """
        return self.username
    
    def __repr__(self) -> str:
        """
        Return a string representation of the User.
        
        :return: String representation
        """
        return f'<User {self.username}>'
