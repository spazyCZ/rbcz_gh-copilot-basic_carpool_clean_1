"""
Reservation model for managing parking reservations.

This module defines the Reservation model linking users to parking spots for specific dates.
"""

from datetime import datetime, date
from extensions import db


class Reservation(db.Model):
    """
    Reservation model for managing parking spot reservations.
    
    Links users to parking spots for specific dates with audit tracking.
    """
    
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.String(10), db.ForeignKey('parking_spots.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # Name for the reservation
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default='active')  # Status: active, cancelled, completed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, spot_id: str, user_id: int, name: str, reservation_date: date, status: str = 'active'):
        """
        Initialize a new Reservation instance.
        
        :param spot_id: ID of the parking spot being reserved
        :param user_id: ID of the user making the reservation
        :param name: Name for the reservation
        :param reservation_date: Date of the reservation
        :param status: Status of the reservation (active, cancelled, completed)
        """
        self.spot_id = spot_id
        self.user_id = user_id
        self.name = name
        self.reservation_date = reservation_date
        self.status = status
    
    def __repr__(self) -> str:
        """
        String representation of the Reservation object.
        
        :return: Reservation representation string
        """
        return f'<Reservation {self.name} - Spot {self.spot_id} on {self.reservation_date}>'
    
    def is_future_reservation(self) -> bool:
        """
        Check if the reservation is for a future date.
        
        :return: True if reservation is in the future, False otherwise
        """
        return self.reservation_date > datetime.utcnow().date()
    
    def is_today_reservation(self) -> bool:
        """
        Check if the reservation is for today.
        
        :return: True if reservation is for today, False otherwise
        """
        return self.reservation_date == datetime.utcnow().date()
    
    def is_past_reservation(self) -> bool:
        """
        Check if the reservation is for a past date.
        
        :return: True if reservation is in the past, False otherwise
        """
        return self.reservation_date < datetime.utcnow().date()
    
    def can_be_modified(self) -> bool:
        """
        Check if the reservation can still be modified.
        
        :return: True if reservation can be modified, False otherwise
        """
        # Allow modifications for future reservations and today's reservations
        return self.reservation_date >= datetime.utcnow().date()
    
    def can_be_cancelled(self) -> bool:
        """
        Check if the reservation can be cancelled.
        
        :return: True if reservation can be cancelled, False otherwise
        """
        # Allow cancellations for future reservations only
        return self.reservation_date > datetime.utcnow().date()
    
    def update_name(self, new_name: str) -> None:
        """
        Update the reservation name.
        
        :param new_name: New name for the reservation
        """
        self.name = new_name
        self.updated_at = datetime.utcnow()
    
    def cancel_reservation(self) -> None:
        """
        Cancel the reservation by setting status to cancelled.
        """
        self.status = 'cancelled'
        self.updated_at = datetime.utcnow()
    
    def complete_reservation(self) -> None:
        """
        Complete the reservation by setting status to completed.
        """
        self.status = 'completed'
        self.updated_at = datetime.utcnow()
    
    def reactivate_reservation(self) -> None:
        """
        Reactivate a cancelled reservation.
        """
        self.status = 'active'
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """
        Check if the reservation is active.
        
        :return: True if reservation is active, False otherwise
        """
        return self.status == 'active'
    
    def is_cancelled(self) -> bool:
        """
        Check if the reservation is cancelled.
        
        :return: True if reservation is cancelled, False otherwise
        """
        return self.status == 'cancelled'
    
    def is_completed(self) -> bool:
        """
        Check if the reservation is completed.
        
        :return: True if reservation is completed, False otherwise
        """
        return self.status == 'completed'
    
    def to_dict(self) -> dict:
        """
        Convert Reservation object to dictionary representation.
        
        :return: Dictionary containing reservation data
        """
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'name': self.name,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_future': self.is_future_reservation(),
            'is_today': self.is_today_reservation(),
            'is_past': self.is_past_reservation(),
            'is_active': self.is_active(),
            'is_cancelled': self.is_cancelled(),
            'is_completed': self.is_completed(),
            'can_modify': self.can_be_modified(),
            'can_cancel': self.can_be_cancelled(),
            'user_username': self.user.username if self.user else None,
            'spot_location': self.parking_spot.location if self.parking_spot else None
        }
    
    @staticmethod
    def check_double_booking(spot_id: str, reservation_date: date, exclude_id: int = None) -> bool:
        """
        Check if a parking spot is already reserved for a specific date.
        
        :param spot_id: ID of the parking spot to check
        :param reservation_date: Date to check for existing reservations
        :param exclude_id: Reservation ID to exclude from the check (for updates)
        :return: True if spot is already reserved, False otherwise
        """
        query = Reservation.query.filter_by(
            spot_id=spot_id,
            reservation_date=reservation_date
        )
        
        if exclude_id:
            query = query.filter(Reservation.id != exclude_id)
        
        existing_reservation = query.first()
        return existing_reservation is not None
