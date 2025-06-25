"""
This module provides service methods for managing carpools.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging

from carpool.extensions import db
from carpool.models.carpool import Carpool
from carpool.models.user import User

logger = logging.getLogger(__name__)

def get_all_carpools() -> List[Carpool]:
    """
    Get all carpools.
    
    :return: List of carpools
    """
    try:
        return Carpool.query.all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving carpools: {e}")
        return []

def get_active_carpools() -> List[Carpool]:
    """
    Get all active carpools (not completed or cancelled).
    
    :return: List of active carpools
    """
    try:
        return Carpool.query.filter_by(status='active').all()
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving active carpools: {e}")
        return []

def get_carpool(carpool_id: int) -> Optional[Carpool]:
    """
    Get a carpool by ID.
    
    :param carpool_id: ID of the carpool
    :return: Carpool object or None if not found
    """
    try:
        return Carpool.query.get(carpool_id)
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving carpool {carpool_id}: {e}")
        return None

def create_carpool(
    name: str,
    origin: str,
    destination: str,
    departure_time: datetime,
    driver_id: str,
    max_passengers: int = 4,
    return_time: datetime = None,
    notes: str = None
) -> Optional[Carpool]:
    """
    Create a new carpool.
    
    :param name: Name/title of the carpool
    :param origin: Starting location
    :param destination: Destination location
    :param departure_time: Time of departure
    :param driver_id: ID of the driver (user)
    :param max_passengers: Maximum number of passengers, defaults to 4
    :param return_time: Optional return time
    :param notes: Optional notes about the carpool
    :return: Created Carpool or None if error
    """
    try:
        carpool = Carpool(
            name=name,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            return_time=return_time,
            max_passengers=max_passengers,
            driver_id=driver_id,
            notes=notes
        )
        db.session.add(carpool)
        db.session.commit()
        logger.info(f"Created carpool: {carpool.id} - {name}")
        return carpool
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating carpool: {e}")
        return None

def update_carpool(
    carpool_id: int,
    name: str = None,
    origin: str = None,
    destination: str = None,
    departure_time: datetime = None,
    return_time: datetime = None,
    max_passengers: int = None,
    notes: str = None,
    status: str = None
) -> Optional[Carpool]:
    """
    Update an existing carpool.
    
    :param carpool_id: ID of the carpool
    :param name: New name/title or None to keep current
    :param origin: New origin or None to keep current
    :param destination: New destination or None to keep current
    :param departure_time: New departure time or None to keep current
    :param return_time: New return time or None to keep current
    :param max_passengers: New max passengers or None to keep current
    :param notes: New notes or None to keep current
    :param status: New status or None to keep current
    :return: Updated Carpool or None if error
    """
    try:
        carpool = Carpool.query.get(carpool_id)
        if not carpool:
            logger.warning(f"Carpool not found: {carpool_id}")
            return None
        
        # Update fields if provided
        if name:
            carpool.name = name
        if origin:
            carpool.origin = origin
        if destination:
            carpool.destination = destination
        if departure_time:
            carpool.departure_time = departure_time
        if return_time is not None:  # Allow setting to None
            carpool.return_time = return_time
        if max_passengers is not None:
            # Ensure we don't reduce below current passenger count
            if max_passengers < carpool.current_passengers:
                logger.warning(f"Cannot set max_passengers below current_passengers")
                return None
            carpool.max_passengers = max_passengers
        if notes is not None:  # Allow setting to empty string
            carpool.notes = notes
        if status:
            carpool.status = status
        
        carpool.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info(f"Updated carpool: {carpool_id}")
        return carpool
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating carpool {carpool_id}: {e}")
        return None

def delete_carpool(carpool_id: int) -> bool:
    """
    Delete a carpool.
    
    :param carpool_id: ID of the carpool
    :return: True if successful, False otherwise
    """
    try:
        carpool = Carpool.query.get(carpool_id)
        if not carpool:
            logger.warning(f"Carpool not found: {carpool_id}")
            return False
        
        db.session.delete(carpool)
        db.session.commit()
        logger.info(f"Deleted carpool: {carpool_id}")
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error deleting carpool {carpool_id}: {e}")
        return False

def join_carpool(carpool_id: int, user_id: str) -> bool:
    """
    Add a passenger to a carpool.
    
    :param carpool_id: ID of the carpool
    :param user_id: Username of the user to add
    :return: True if successful, False otherwise
    """
    try:
        carpool = Carpool.query.get(carpool_id)
        user = User.query.get(user_id)
        
        if not carpool or not user:
            logger.warning(f"Carpool or user not found: {carpool_id}, {user_id}")
            return False
        
        # Check if user is already in this carpool
        if user in carpool.passengers:
            logger.warning(f"User {user_id} is already in carpool {carpool_id}")
            return False
        
        # Check if carpool can be joined
        if not carpool.can_join():
            logger.warning(f"Carpool {carpool_id} cannot be joined (full or not active)")
            return False
        
        result = carpool.add_passenger(user)
        if result:
            db.session.commit()
            logger.info(f"User {user_id} joined carpool {carpool_id}")
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error adding user {user_id} to carpool {carpool_id}: {e}")
        return False

def leave_carpool(carpool_id: int, user_id: str) -> bool:
    """
    Remove a passenger from a carpool.
    
    :param carpool_id: ID of the carpool
    :param user_id: Username of the user to remove
    :return: True if successful, False otherwise
    """
    try:
        carpool = Carpool.query.get(carpool_id)
        user = User.query.get(user_id)
        
        if not carpool or not user:
            logger.warning(f"Carpool or user not found: {carpool_id}, {user_id}")
            return False
        
        result = carpool.remove_passenger(user)
        if result:
            db.session.commit()
            logger.info(f"User {user_id} left carpool {carpool_id}")
        return result
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error removing user {user_id} from carpool {carpool_id}: {e}")
        return False

def get_user_carpools(user_id: str) -> List[Carpool]:
    """
    Get all carpools where the user is a passenger or driver.
    
    :param user_id: Username of the user
    :return: List of carpools
    """
    try:
        # Get carpools where user is a driver
        driver_carpools = Carpool.query.filter_by(driver_id=user_id).all()
        
        # Get carpools where user is a passenger
        user = User.query.get(user_id)
        if not user:
            return driver_carpools
            
        passenger_carpools = user.carpools.all()
        
        # Combine and remove duplicates
        all_carpools = list(set(driver_carpools + passenger_carpools))
        return all_carpools
    except SQLAlchemyError as e:
        logger.error(f"Error retrieving carpools for user {user_id}: {e}")
        return []
