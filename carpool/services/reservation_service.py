"""
This module provides service methods for managing reservations.
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
import logging

from carpool.extensions import db
from carpool.models.reservation import Reservation
from carpool.models.parking_spot import ParkingSpot
from carpool.services.parking_service import get_parking_spot

logger = logging.getLogger(__name__)

def get_all_reservations() -> List[Reservation]:
    """
    Get all reservations.
    
    :return: List of reservations
    """
    try:
        return Reservation.query.order_by(Reservation.reservation_date.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving reservations: {e}")
        return []

def get_reservation(reservation_id: int) -> Optional[Reservation]:
    """
    Get a reservation by ID.
    
    :param reservation_id: ID of the reservation
    :return: Reservation object or None if not found
    """
    try:
        return Reservation.query.get(reservation_id)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving reservation {reservation_id}: {e}")
        return None

def get_user_reservations(username: str) -> List[Reservation]:
    """
    Get all reservations for a specific user.
    
    :param username: Username of the user
    :return: List of reservations
    """
    try:
        return Reservation.query.filter_by(username=username).order_by(Reservation.reservation_date.desc()).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving reservations for user {username}: {e}")
        return []

def create_reservation(spot_id: str, username: str, reservation_date: date) -> Optional[Reservation]:
    """
    Create a new reservation.
    
    :param spot_id: ID of the parking spot
    :param username: Username of the user making the reservation
    :param reservation_date: Date of the reservation
    :return: Created Reservation or None if error
    """
    try:
        # Check if the spot is available on that date
        existing_reservation = Reservation.query.filter_by(
            spot_id=spot_id, 
            reservation_date=reservation_date
        ).first()
        
        if existing_reservation:
            logger.warning(f"Spot {spot_id} already reserved on {reservation_date}")
            return None
        
        # Check if spot exists and is free (not permanently reserved or out of service)
        spot = get_parking_spot(spot_id)
        if not spot or spot.status != 'free':
            logger.warning(f"Spot {spot_id} not available for reservation")
            return None
        
        # Create the reservation
        reservation = Reservation(spot_id=spot_id, username=username, reservation_date=reservation_date)
        db.session.add(reservation)
        db.session.commit()
        logger.info(f"Created reservation for spot {spot_id} on {reservation_date}")
        return reservation
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating reservation for spot {spot_id}: {e}")
        return None

def update_reservation(reservation_id: int, spot_id: str = None, reservation_date: date = None) -> Optional[Reservation]:
    """
    Update an existing reservation.
    
    :param reservation_id: ID of the reservation
    :param spot_id: New spot ID or None to keep current
    :param reservation_date: New date or None to keep current
    :return: Updated Reservation or None if error
    """
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            logger.warning(f"Reservation not found: {reservation_id}")
            return None
        
        # If updating the spot or date, check for conflicts
        if (spot_id and spot_id != reservation.spot_id) or (reservation_date and reservation_date != reservation.reservation_date):
            # Determine the spot and date to check
            check_spot = spot_id if spot_id else reservation.spot_id
            check_date = reservation_date if reservation_date else reservation.reservation_date
            
            # Check for existing reservations with the same spot and date
            existing_reservation = Reservation.query.filter(
                Reservation.id != reservation_id,
                Reservation.spot_id == check_spot,
                Reservation.reservation_date == check_date
            ).first()
            
            if existing_reservation:
                logger.warning(f"Spot {check_spot} already reserved on {check_date}")
                return None
            
            # Check if new spot exists and is free
            if spot_id and spot_id != reservation.spot_id:
                spot = get_parking_spot(spot_id)
                if not spot or spot.status != 'free':
                    logger.warning(f"Spot {spot_id} not available for reservation")
                    return None
        
        # Update reservation
        if spot_id:
            reservation.spot_id = spot_id
        if reservation_date:
            reservation.reservation_date = reservation_date
        
        db.session.commit()
        logger.info(f"Updated reservation: {reservation_id}")
        return reservation
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating reservation {reservation_id}: {e}")
        return None

def delete_reservation(reservation_id: int) -> bool:
    """
    Delete a reservation.
    
    :param reservation_id: ID of the reservation
    :return: True if successful, False otherwise
    """
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            logger.warning(f"Reservation not found: {reservation_id}")
            return False
        
        db.session.delete(reservation)
        db.session.commit()
        logger.info(f"Deleted reservation: {reservation_id}")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting reservation {reservation_id}: {e}")
        return False

def get_reservations_by_date(target_date: date) -> List[Reservation]:
    """
    Get all reservations for a specific date.
    
    :param target_date: Date to filter reservations
    :return: List of reservations
    """
    try:
        return Reservation.query.filter_by(reservation_date=target_date).all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving reservations for date {target_date}: {e}")
        return []
