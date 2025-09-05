"""
ParkingSpot model for managing parking locations.

This module defines the ParkingSpot model for storing available
parking spaces with location and status information.
"""
from datetime import datetime
from typing import List, Optional

from app.extensions import db


class ParkingSpot(db.Model):
    """
    ParkingSpot model representing a physical parking space.
    
    Each spot has a unique identifier and location information.
    Status is determined dynamically based on reservations.
    """
    
    __tablename__ = 'parking_spots'
    
    # Primary key - using string ID like "A1", "B2"
    id = db.Column(db.String(10), primary_key=True)
    
    # Location and description
    location = db.Column(db.String(100), nullable=False)  # e.g., "Level A", "Ground Floor"
    description = db.Column(db.String(255), nullable=True)  # Optional additional info
    
    # Spot characteristics
    is_available = db.Column(db.Boolean, nullable=False, default=True, index=True)
    is_handicap_accessible = db.Column(db.Boolean, nullable=False, default=False)
    is_electric_charging = db.Column(db.Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, id: str, location: str, description: Optional[str] = None,
                 is_handicap_accessible: bool = False, is_electric_charging: bool = False) -> None:
        """
        Initialize a new ParkingSpot instance.
        
        :param id: Unique spot identifier (e.g., "A1", "B2")
        :param location: Physical location description
        :param description: Optional additional description
        :param is_handicap_accessible: Whether spot is handicap accessible
        :param is_electric_charging: Whether spot has electric charging
        """
        self.id = id
        self.location = location
        self.description = description
        self.is_handicap_accessible = is_handicap_accessible
        self.is_electric_charging = is_electric_charging
    
    def is_reserved_on_date(self, reservation_date: datetime.date) -> bool:
        """
        Check if spot is reserved on a specific date.
        
        :param reservation_date: Date to check for reservations
        :return: True if spot is reserved, False otherwise
        """
        from app.models.reservation import Reservation
        
        return Reservation.query.filter_by(
            spot_id=self.id,
            reservation_date=reservation_date
        ).first() is not None
    
    def get_reservation_for_date(self, reservation_date: datetime.date) -> Optional['Reservation']:
        """
        Get reservation for this spot on a specific date.
        
        :param reservation_date: Date to check
        :return: Reservation instance or None
        """
        from app.models.reservation import Reservation
        
        return Reservation.query.filter_by(
            spot_id=self.id,
            reservation_date=reservation_date
        ).first()
    
    def get_upcoming_reservations(self, limit: int = 10) -> List['Reservation']:
        """
        Get upcoming reservations for this spot.
        
        :param limit: Maximum number of reservations to return
        :return: List of upcoming reservations
        """
        from app.models.reservation import Reservation
        
        return Reservation.query.filter(
            Reservation.spot_id == self.id,
            Reservation.reservation_date >= datetime.now().date()
        ).order_by(Reservation.reservation_date.asc()).limit(limit).all()
    
    def to_dict(self, include_reservations: bool = False) -> dict:
        """
        Convert spot instance to dictionary representation.
        
        :param include_reservations: Whether to include reservation data
        :return: Dictionary representation of parking spot
        """
        data = {
            'id': self.id,
            'location': self.location,
            'description': self.description,
            'is_available': self.is_available,
            'is_handicap_accessible': self.is_handicap_accessible,
            'is_electric_charging': self.is_electric_charging,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_reservations:
            data['upcoming_reservations'] = [
                res.to_dict() for res in self.get_upcoming_reservations()
            ]
            
        return data
    
    @classmethod
    def find_available_spots(cls, reservation_date: datetime.date, 
                           handicap_accessible: Optional[bool] = None,
                           electric_charging: Optional[bool] = None) -> List['ParkingSpot']:
        """
        Find available spots for a specific date with optional filters.
        
        :param reservation_date: Date to check availability
        :param handicap_accessible: Filter by handicap accessibility
        :param electric_charging: Filter by electric charging capability
        :return: List of available parking spots
        """
        from app.models.reservation import Reservation
        
        # Start with base query for available spots
        query = cls.query.filter_by(is_available=True)
        
        # Apply optional filters
        if handicap_accessible is not None:
            query = query.filter_by(is_handicap_accessible=handicap_accessible)
        
        if electric_charging is not None:
            query = query.filter_by(is_electric_charging=electric_charging)
        
        # Get all spots matching criteria
        all_spots = query.all()
        
        # Filter out spots that are reserved on the target date
        available_spots = []
        for spot in all_spots:
            if not spot.is_reserved_on_date(reservation_date):
                available_spots.append(spot)
        
        return available_spots
    
    @classmethod
    def create_spot(cls, id: str, location: str, description: Optional[str] = None,
                   is_handicap_accessible: bool = False, is_electric_charging: bool = False) -> 'ParkingSpot':
        """
        Create a new parking spot and save to database.
        
        :param id: Unique spot identifier
        :param location: Physical location description
        :param description: Optional additional description
        :param is_handicap_accessible: Whether spot is handicap accessible
        :param is_electric_charging: Whether spot has electric charging
        :return: Created parking spot instance
        :raises: IntegrityError if spot ID already exists
        """
        spot = cls(
            id=id,
            location=location,
            description=description,
            is_handicap_accessible=is_handicap_accessible,
            is_electric_charging=is_electric_charging
        )
        db.session.add(spot)
        db.session.commit()
        return spot
    
    def __repr__(self) -> str:
        """String representation of ParkingSpot instance."""
        return f'<ParkingSpot {self.id} at {self.location}>'