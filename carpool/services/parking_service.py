"""
This module provides service methods for managing parking spots.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
import logging

from carpool.extensions import db
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation

logger = logging.getLogger(__name__)

def get_all_parking_spots() -> List[ParkingSpot]:
    """
    Get all parking spots.
    
    :return: List of parking spots
    """
    try:
        return ParkingSpot.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving parking spots: {e}")
        return []

def get_parking_spot(spot_id: str) -> Optional[ParkingSpot]:
    """
    Get a parking spot by ID.
    
    :param spot_id: ID of the parking spot
    :return: ParkingSpot object or None if not found
    """
    try:
        return ParkingSpot.query.get(spot_id)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving parking spot {spot_id}: {e}")
        return None

def create_parking_spot(spot_id: str, location: str, status: str = 'free') -> Optional[ParkingSpot]:
    """
    Create a new parking spot.
    
    :param spot_id: ID of the parking spot
    :param location: Location of the parking spot
    :param status: Initial status, defaults to 'free'
    :return: Created ParkingSpot or None if error
    """
    try:
        parking_spot = ParkingSpot(id=spot_id, location=location, status=status)
        db.session.add(parking_spot)
        db.session.commit()
        logger.info(f"Created parking spot: {spot_id}")
        return parking_spot
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating parking spot {spot_id}: {e}")
        return None

def update_parking_spot(spot_id: str, location: str = None, status: str = None) -> Optional[ParkingSpot]:
    """
    Update an existing parking spot.
    
    :param spot_id: ID of the parking spot
    :param location: New location or None to keep current
    :param status: New status or None to keep current
    :return: Updated ParkingSpot or None if error
    """
    try:
        parking_spot = ParkingSpot.query.get(spot_id)
        if not parking_spot:
            logger.warning(f"Parking spot not found: {spot_id}")
            return None
        
        if location:
            parking_spot.location = location
        if status:
            parking_spot.status = status
        
        db.session.commit()
        logger.info(f"Updated parking spot: {spot_id}")
        return parking_spot
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating parking spot {spot_id}: {e}")
        return None

def delete_parking_spot(spot_id: str) -> bool:
    """
    Delete a parking spot.
    
    :param spot_id: ID of the parking spot
    :return: True if successful, False otherwise
    """
    try:
        parking_spot = ParkingSpot.query.get(spot_id)
        if not parking_spot:
            logger.warning(f"Parking spot not found: {spot_id}")
            return False
        
        db.session.delete(parking_spot)
        db.session.commit()
        logger.info(f"Deleted parking spot: {spot_id}")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting parking spot {spot_id}: {e}")
        return False

def get_available_spots(reservation_date: date) -> List[ParkingSpot]:
    """
    Get available parking spots for a specific date.
    
    :param reservation_date: Date to check availability
    :return: List of available parking spots
    """
    try:
        # Get all parking spots
        all_spots = ParkingSpot.query.all()
        
        # Get spots that are already reserved for the given date
        reserved_spot_ids = [
            res.spot_id for res in Reservation.query.filter_by(reservation_date=reservation_date).all()
        ]
        
        # Filter out reserved spots
        available_spots = [spot for spot in all_spots if spot.id not in reserved_spot_ids and spot.status == 'free']
        
        return available_spots
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving available parking spots for {reservation_date}: {e}")
        return []
