"""
Reservation model for managing parking reservations.

This module defines the Reservation model with unique constraint
to prevent double-booking of parking spots.
"""
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError

from app.extensions import db


class Reservation(db.Model):
    """
    Reservation model for storing parking spot reservations.
    
    Implements unique constraint on (spot_id, reservation_date) 
    to prevent double-booking conflicts.
    """
    
    __tablename__ = 'reservations'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    spot_id = db.Column(db.String(10), db.ForeignKey('parking_spots.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Reservation details
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # Name of person making reservation
    notes = db.Column(db.Text, nullable=True)  # Optional additional notes
    
    # Status tracking
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    # Unique constraint to prevent double booking
    __table_args__ = (
        UniqueConstraint('spot_id', 'reservation_date', name='uq_spot_date'),
        {'extend_existing': True}
    )
    
    def __init__(self, spot_id: str, user_id: int, reservation_date: date, name: str, notes: Optional[str] = None) -> None:
        """
        Initialize a new Reservation instance.
        
        :param spot_id: ID of the parking spot to reserve
        :param user_id: ID of the user making the reservation
        :param reservation_date: Date of the reservation
        :param name: Name of the person for the reservation
        :param notes: Optional additional notes
        """
        self.spot_id = spot_id
        self.user_id = user_id
        self.reservation_date = reservation_date
        self.name = name
        self.notes = notes
    
    def cancel_reservation(self) -> None:
        """
        Cancel this reservation by marking it as inactive.
        """
        self.is_active = False
        self.cancelled_at = datetime.utcnow()
        db.session.commit()
    
    def update_reservation(self, name: Optional[str] = None, notes: Optional[str] = None) -> None:
        """
        Update reservation details.
        
        :param name: New name for the reservation
        :param notes: New notes for the reservation
        """
        if name is not None:
            self.name = name
        if notes is not None:
            self.notes = notes
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_upcoming(self) -> bool:
        """
        Check if reservation is for a future date.
        
        :return: True if reservation is upcoming, False otherwise
        """
        return self.reservation_date >= datetime.now().date()
    
    def is_today(self) -> bool:
        """
        Check if reservation is for today.
        
        :return: True if reservation is for today, False otherwise
        """
        return self.reservation_date == datetime.now().date()
    
    def to_dict(self, include_relations: bool = False) -> dict:
        """
        Convert reservation instance to dictionary representation.
        
        :param include_relations: Whether to include related object data
        :return: Dictionary representation of reservation
        """
        data = {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'name': self.name,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None
        }
        
        if include_relations:
            # Include related spot and user data
            if self.parking_spot:
                data['parking_spot'] = self.parking_spot.to_dict()
            if self.user:
                data['user'] = {
                    'id': self.user.id,
                    'username': self.user.username,
                    'email': self.user.email
                }
        
        return data
    
    @classmethod
    def find_by_spot_and_date(cls, spot_id: str, reservation_date: date) -> Optional['Reservation']:
        """
        Find reservation by spot ID and date.
        
        :param spot_id: Parking spot ID
        :param reservation_date: Reservation date
        :return: Reservation instance or None
        """
        return cls.query.filter_by(
            spot_id=spot_id,
            reservation_date=reservation_date,
            is_active=True
        ).first()
    
    @classmethod
    def find_by_user(cls, user_id: int, include_cancelled: bool = False) -> List['Reservation']:
        """
        Find all reservations for a specific user.
        
        :param user_id: User ID to search for
        :param include_cancelled: Whether to include cancelled reservations
        :return: List of reservations
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if not include_cancelled:
            query = query.filter_by(is_active=True)
        
        return query.order_by(cls.reservation_date.desc()).all()
    
    @classmethod
    def find_upcoming_reservations(cls, limit: int = 50) -> List['Reservation']:
        """
        Find upcoming active reservations.
        
        :param limit: Maximum number of reservations to return
        :return: List of upcoming reservations
        """
        return cls.query.filter(
            cls.reservation_date >= datetime.now().date(),
            cls.is_active == True
        ).order_by(cls.reservation_date.asc()).limit(limit).all()
    
    @classmethod
    def create_reservation(cls, spot_id: str, user_id: int, reservation_date: date, 
                          name: str, notes: Optional[str] = None) -> 'Reservation':
        """
        Create a new reservation with conflict detection.
        
        :param spot_id: Parking spot ID
        :param user_id: User ID making the reservation
        :param reservation_date: Date of reservation
        :param name: Name for the reservation
        :param notes: Optional notes
        :return: Created reservation instance
        :raises: IntegrityError if spot is already reserved for that date
        """
        reservation = cls(
            spot_id=spot_id,
            user_id=user_id,
            reservation_date=reservation_date,
            name=name,
            notes=notes
        )
        
        try:
            db.session.add(reservation)
            db.session.commit()
            return reservation
        except IntegrityError as e:
            db.session.rollback()
            # Re-raise with more specific error information
            raise IntegrityError(
                f"Spot {spot_id} is already reserved for {reservation_date}",
                orig=e.orig,
                params=e.params
            )
    
    @classmethod
    def get_reservations_for_date_range(cls, start_date: date, end_date: date, 
                                       spot_id: Optional[str] = None) -> List['Reservation']:
        """
        Get reservations within a date range, optionally filtered by spot.
        
        :param start_date: Start date for the range
        :param end_date: End date for the range
        :param spot_id: Optional spot ID filter
        :return: List of reservations in date range
        """
        query = cls.query.filter(
            cls.reservation_date >= start_date,
            cls.reservation_date <= end_date,
            cls.is_active == True
        )
        
        if spot_id:
            query = query.filter_by(spot_id=spot_id)
        
        return query.order_by(cls.reservation_date.asc()).all()
    
    def __repr__(self) -> str:
        """String representation of Reservation instance."""
        return f'<Reservation {self.spot_id} on {self.reservation_date} for {self.name}>'