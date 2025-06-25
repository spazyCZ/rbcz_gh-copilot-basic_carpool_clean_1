"""
This module defines the Reservation model that represents parking spot reservations.
"""
from datetime import datetime
from carpool.extensions import db

class Reservation(db.Model):
    """
    A class representing a parking spot reservation.
    
    Attributes:
        id (int): Unique reservation identifier
        spot_id (str): The ID of the reserved parking spot
        username (str): The username of the user making the reservation
        reservation_date (date): The date of the reservation
        created_at (datetime): When the reservation was created
    """
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.String(10), db.ForeignKey('parking_spots.id'), nullable=False)
    username = db.Column(db.String(64), db.ForeignKey('users.username'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, spot_id: str, username: str, reservation_date: datetime.date) -> None:
        """
        Initialize a new Reservation instance.
        
        :param spot_id: ID of the parking spot to reserve
        :param username: Username of the user making the reservation
        :param reservation_date: Date of the reservation
        """
        self.spot_id = spot_id
        self.username = username
        self.reservation_date = reservation_date
    
    def __repr__(self) -> str:
        """
        Return a string representation of the Reservation.
        
        :return: String representation
        """
        return f'<Reservation {self.id}: {self.spot_id} on {self.reservation_date}>'
