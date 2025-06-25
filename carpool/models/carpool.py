"""
This module defines the Carpool model for the application.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import relationship
from carpool.extensions import db

class Carpool(db.Model):
    """
    A class representing a carpool in the system.
    """
    __tablename__ = 'carpools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    return_time = db.Column(db.DateTime, nullable=True)
    max_passengers = db.Column(db.Integer, nullable=False, default=4)
    current_passengers = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='active')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    driver_id = db.Column(db.String(64), db.ForeignKey('users.username'))
    driver = relationship('User', backref='driven_carpools')
    
    # CarPool passengers relationship will be handled through a separate table
    passengers = relationship(
        'User',
        secondary='carpool_passengers',
        backref=db.backref('carpools', lazy='dynamic')
    )
    
    def __repr__(self) -> str:
        """
        String representation of the carpool.
        
        :return: String representation
        """
        return f"<Carpool {self.id}: {self.name}>"
    
    def is_full(self) -> bool:
        """
        Check if the carpool is full.
        
        :return: True if the carpool is full, False otherwise
        """
        return self.current_passengers >= self.max_passengers
    
    def can_join(self) -> bool:
        """
        Check if a user can join this carpool.
        
        :return: True if the carpool can be joined, False otherwise
        """
        return (
            self.status == 'active' and
            not self.is_full() and
            self.departure_time > datetime.utcnow()
        )
    
    def add_passenger(self, user) -> bool:
        """
        Add a passenger to the carpool.
        
        :param user: User to add as passenger
        :return: True if successfully added, False otherwise
        """
        if not self.can_join() or user in self.passengers:
            return False
        
        self.passengers.append(user)
        self.current_passengers += 1
        return True
    
    def remove_passenger(self, user) -> bool:
        """
        Remove a passenger from the carpool.
        
        :param user: User to remove
        :return: True if successfully removed, False otherwise
        """
        if user not in self.passengers:
            return False
        
        self.passengers.remove(user)
        self.current_passengers -= 1
        return True


# Association table for carpool passengers
carpool_passengers = db.Table(
    'carpool_passengers',
    db.Column('user_id', db.String(64), db.ForeignKey('users.username'), primary_key=True),
    db.Column('carpool_id', db.Integer, db.ForeignKey('carpools.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)
