"""
This module defines the ParkingSpot model that represents available parking spots.
"""
from carpool.extensions import db

class ParkingSpot(db.Model):
    """
    A class representing a parking spot in the system.
    
    Attributes:
        id (str): The unique spot identifier (e.g., A1, B2)
        status (str): The current status (free or reserved)
        location (str): The location of the spot (e.g., Level A)
    """
    __tablename__ = 'parking_spots'
    
    id = db.Column(db.String(10), primary_key=True)
    status = db.Column(db.String(20), nullable=False, default='free')
    location = db.Column(db.String(100), nullable=False)
    
    # Relationships
    reservations = db.relationship('Reservation', backref='parking_spot', lazy='dynamic')
    
    def __init__(self, id: str, location: str, status: str = 'free') -> None:
        """
        Initialize a new ParkingSpot instance.
        
        :param id: Unique spot identifier
        :param location: Location of the spot
        :param status: Current status, defaults to 'free'
        """
        self.id = id
        self.location = location
        self.status = status
    
    def is_available(self) -> bool:
        """
        Check if the parking spot is available (free).
        
        :return: True if the spot is available, False otherwise
        """
        return self.status == 'free'
    
    def __repr__(self) -> str:
        """
        Return a string representation of the ParkingSpot.
        
        :return: String representation
        """
        return f'<ParkingSpot {self.id} - {self.status}>'
