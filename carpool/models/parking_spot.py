"""
ParkingSpot model for managing parking locations.

This module defines the ParkingSpot model with status tracking and location information.
"""

from datetime import datetime
from extensions import db


class ParkingSpot(db.Model):
    """
    ParkingSpot model for managing individual parking locations.
    
    Tracks availability status, location information, and maintenance states.
    """
    
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.String(10), primary_key=True)  # e.g., A1, B2
    status = db.Column(db.String(20), nullable=False, default='available')  # available, reserved, maintenance
    location = db.Column(db.String(100), nullable=False)  # e.g., Level A, Outdoor
    description = db.Column(db.Text, nullable=True)  # Optional spot description
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, id: str, location: str, description: str = None):
        """
        Initialize a new ParkingSpot instance.
        
        :param id: Unique identifier for the parking spot (e.g., A1, B2)
        :param location: Physical location description
        :param description: Optional additional description
        """
        self.id = id
        self.location = location
        self.description = description
        self.status = 'available'
    
    def __repr__(self) -> str:
        """
        String representation of the ParkingSpot object.
        
        :return: ParkingSpot representation string
        """
        return f'<ParkingSpot {self.id} ({self.status})>'
    
    def is_available(self) -> bool:
        """
        Check if the parking spot is available for reservation.
        
        :return: True if spot is available, False otherwise
        """
        return self.status == 'available'
    
    def is_reserved(self) -> bool:
        """
        Check if the parking spot is currently reserved.
        
        :return: True if spot is reserved, False otherwise
        """
        return self.status == 'reserved'
    
    def is_maintenance(self) -> bool:
        """
        Check if the parking spot is under maintenance.
        
        :return: True if spot is under maintenance, False otherwise
        """
        return self.status == 'maintenance'
    
    def set_available(self) -> None:
        """
        Set the parking spot status to available.
        """
        self.status = 'available'
    
    def set_reserved(self) -> None:
        """
        Set the parking spot status to reserved.
        """
        self.status = 'reserved'
    
    def set_maintenance(self) -> None:
        """
        Set the parking spot status to maintenance.
        """
        self.status = 'maintenance'
    
    def get_current_reservation(self, date=None):
        """
        Get the current reservation for this spot on a specific date.
        
        :param date: Date to check for reservation (defaults to today)
        :return: Reservation object if found, None otherwise
        """
        if date is None:
            date = datetime.utcnow().date()
        
        return next(
            (r for r in self.reservations if r.reservation_date == date),
            None
        )
    
    def to_dict(self) -> dict:
        """
        Convert ParkingSpot object to dictionary representation.
        
        :return: Dictionary containing parking spot data
        """
        return {
            'id': self.id,
            'status': self.status,
            'location': self.location,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reservations_count': len(self.reservations),
            'is_available': self.is_available(),
            'is_reserved': self.is_reserved(),
            'is_maintenance': self.is_maintenance()
        }
