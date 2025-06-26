"""
Carpool model for managing carpool trip organization.

This module defines the Carpool model for organizing carpool trips with passenger management.
"""

from datetime import datetime
from extensions import db


class Carpool(db.Model):
    """
    Carpool model for managing carpool trip organization.
    
    Tracks trip details, passenger capacity, and organizer information.
    """
    
    __tablename__ = 'carpools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Carpool trip name
    origin = db.Column(db.String(200), nullable=False)  # Starting location
    destination = db.Column(db.String(200), nullable=False)  # End location
    departure_time = db.Column(db.DateTime, nullable=False)  # When the trip starts
    return_time = db.Column(db.DateTime, nullable=True)  # When the trip returns (optional)
    max_passengers = db.Column(db.Integer, nullable=False, default=4)  # Maximum number of passengers
    current_passengers = db.Column(db.Integer, nullable=False, default=0)  # Current passenger count
    notes = db.Column(db.Text, nullable=True)  # Additional trip information
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name: str, origin: str, destination: str, departure_time: datetime, 
                 organizer_id: int, max_passengers: int = 4, return_time: datetime = None, notes: str = None):
        """
        Initialize a new Carpool instance.
        
        :param name: Name/title of the carpool trip
        :param origin: Starting location
        :param destination: Destination location
        :param departure_time: When the trip starts
        :param organizer_id: ID of the user organizing the trip
        :param max_passengers: Maximum number of passengers (default 4)
        :param return_time: When the trip returns (optional)
        :param notes: Additional trip information
        """
        self.name = name
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.return_time = return_time
        self.max_passengers = max_passengers
        self.current_passengers = 0
        self.notes = notes
        self.organizer_id = organizer_id
    
    def __repr__(self) -> str:
        """
        String representation of the Carpool object.
        
        :return: Carpool representation string
        """
        return f'<Carpool {self.name}: {self.origin} → {self.destination}>'
    
    def is_full(self) -> bool:
        """
        Check if the carpool is at maximum capacity.
        
        :return: True if carpool is full, False otherwise
        """
        return self.current_passengers >= self.max_passengers
    
    def has_available_seats(self) -> bool:
        """
        Check if the carpool has available seats.
        
        :return: True if seats are available, False otherwise
        """
        return self.current_passengers < self.max_passengers
    
    def available_seats(self) -> int:
        """
        Get the number of available seats.
        
        :return: Number of available seats
        """
        return max(0, self.max_passengers - self.current_passengers)
    
    def is_future_trip(self) -> bool:
        """
        Check if the carpool trip is in the future.
        
        :return: True if trip is in the future, False otherwise
        """
        return self.departure_time > datetime.utcnow()
    
    def is_today_trip(self) -> bool:
        """
        Check if the carpool trip is today.
        
        :return: True if trip is today, False otherwise
        """
        return self.departure_time.date() == datetime.utcnow().date()
    
    def is_past_trip(self) -> bool:
        """
        Check if the carpool trip has already passed.
        
        :return: True if trip is in the past, False otherwise
        """
        return self.departure_time < datetime.utcnow()
    
    def can_join(self) -> bool:
        """
        Check if new passengers can join this carpool.
        
        :return: True if passengers can join, False otherwise
        """
        return self.has_available_seats() and self.is_future_trip()
    
    def can_be_modified(self) -> bool:
        """
        Check if the carpool can still be modified.
        
        :return: True if carpool can be modified, False otherwise
        """
        # Allow modifications for future trips
        return self.is_future_trip()
    
    def add_passenger(self) -> bool:
        """
        Add a passenger to the carpool if space is available.
        
        :return: True if passenger was added, False if carpool is full
        """
        if self.has_available_seats():
            self.current_passengers += 1
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def remove_passenger(self) -> bool:
        """
        Remove a passenger from the carpool.
        
        :return: True if passenger was removed, False if no passengers to remove
        """
        if self.current_passengers > 0:
            self.current_passengers -= 1
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def update_details(self, name: str = None, origin: str = None, destination: str = None,
                      departure_time: datetime = None, return_time: datetime = None,
                      max_passengers: int = None, notes: str = None) -> None:
        """
        Update carpool details.
        
        :param name: New trip name
        :param origin: New origin location
        :param destination: New destination location
        :param departure_time: New departure time
        :param return_time: New return time
        :param max_passengers: New maximum passenger count
        :param notes: New notes
        """
        if name is not None:
            self.name = name
        if origin is not None:
            self.origin = origin
        if destination is not None:
            self.destination = destination
        if departure_time is not None:
            self.departure_time = departure_time
        if return_time is not None:
            self.return_time = return_time
        if max_passengers is not None:
            # Ensure current passengers doesn't exceed new max
            self.max_passengers = max_passengers
            if self.current_passengers > max_passengers:
                self.current_passengers = max_passengers
        if notes is not None:
            self.notes = notes
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Convert Carpool object to dictionary representation.
        
        :return: Dictionary containing carpool data
        """
        return {
            'id': self.id,
            'name': self.name,
            'origin': self.origin,
            'destination': self.destination,
            'departure_time': self.departure_time.isoformat() if self.departure_time else None,
            'return_time': self.return_time.isoformat() if self.return_time else None,
            'max_passengers': self.max_passengers,
            'current_passengers': self.current_passengers,
            'available_seats': self.available_seats(),
            'notes': self.notes,
            'organizer_id': self.organizer_id,
            'organizer_username': self.organizer.username if self.organizer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_full': self.is_full(),
            'has_seats': self.has_available_seats(),
            'is_future': self.is_future_trip(),
            'is_today': self.is_today_trip(),
            'is_past': self.is_past_trip(),
            'can_join': self.can_join(),
            'can_modify': self.can_be_modified()
        }
