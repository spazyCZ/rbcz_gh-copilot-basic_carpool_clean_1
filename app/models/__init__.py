"""
Models package initialization.

This module imports all model classes to ensure they are registered
with SQLAlchemy and available for migrations and relationships.
"""

# Import all models to register them with SQLAlchemy
from .user import User
from .parking_spot import ParkingSpot  
from .reservation import Reservation
from .action import Action, ActionType

# Make models available at package level
__all__ = [
    'User',
    'ParkingSpot', 
    'Reservation',
    'Action',
    'ActionType'
]