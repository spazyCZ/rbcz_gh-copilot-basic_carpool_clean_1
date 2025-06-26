"""
Carpool service for managing carpool trip organization.

This module provides business logic for carpool trips including creation,
modification, deletion, and passenger management operations.
"""

from typing import List, Optional
from datetime import datetime
from flask import current_app
from carpool.models.user import User
from carpool.models.carpool import Carpool
from carpool.models.action import Action
from extensions import db


class CarpoolService:
    """
    Carpool service class providing business logic for carpool trip management.
    
    Handles carpool creation, modification, deletion, and passenger management operations.
    """
    
    @staticmethod
    def create_carpool(user: User, name: str, origin: str, destination: str, 
                      departure_time: datetime, max_passengers: int = 4, 
                      return_time: datetime = None, notes: str = None) -> Optional[Carpool]:
        """
        Create a new carpool trip.
        
        :param user: User organizing the carpool
        :param name: Name/title of the carpool trip
        :param origin: Starting location
        :param destination: Destination location
        :param departure_time: When the trip starts
        :param max_passengers: Maximum number of passengers
        :param return_time: When the trip returns (optional)
        :param notes: Additional trip information
        :return: Created Carpool object if successful, None otherwise
        """
        try:
            # Validate that the user can organize carpools
            if not user.can_organize_carpool():
                current_app.logger.warning(f'User {user.username} attempted to create carpool without permission')
                return None
            
            # Validate departure time is in the future
            if departure_time <= datetime.utcnow():
                current_app.logger.warning(f'User {user.username} attempted to create carpool with past departure time')
                return None
            
            # Validate return time if provided
            if return_time and return_time <= departure_time:
                current_app.logger.warning(f'User {user.username} attempted to create carpool with invalid return time')
                return None
            
            # Create the carpool
            carpool = Carpool(
                name=name,
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                organizer_id=user.id,
                max_passengers=max_passengers,
                return_time=return_time,
                notes=notes
            )
            
            db.session.add(carpool)
            db.session.commit()
            
            # Log the action
            Action.log_carpool_created(user.username, name)
            current_app.logger.info(f'Carpool created: {carpool.id} by {user.username}')
            
            return carpool
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating carpool: {e}')
            return None
    
    @staticmethod
    def update_carpool(carpool: Carpool, user: User, name: str = None, origin: str = None,
                      destination: str = None, departure_time: datetime = None,
                      return_time: datetime = None, max_passengers: int = None,
                      notes: str = None) -> bool:
        """
        Update an existing carpool trip.
        
        :param carpool: Carpool to update
        :param user: User updating the carpool
        :param name: New trip name
        :param origin: New origin location
        :param destination: New destination location
        :param departure_time: New departure time
        :param return_time: New return time
        :param max_passengers: New maximum passenger count
        :param notes: New notes
        :return: True if update successful, False otherwise
        """
        try:
            # Check if user can modify this carpool
            if not (user.is_admin() or carpool.organizer_id == user.id):
                current_app.logger.warning(f'User {user.username} attempted to modify carpool {carpool.id} without permission')
                return False
            
            # Check if carpool can be modified
            if not carpool.can_be_modified():
                current_app.logger.warning(f'Attempted to modify past carpool: {carpool.id}')
                return False
            
            # Validate departure time if provided
            if departure_time and departure_time <= datetime.utcnow():
                current_app.logger.warning(f'Attempted to set past departure time for carpool {carpool.id}')
                return False
            
            # Validate return time if provided
            check_departure = departure_time if departure_time else carpool.departure_time
            if return_time and return_time <= check_departure:
                current_app.logger.warning(f'Attempted to set invalid return time for carpool {carpool.id}')
                return False
            
            # Update the carpool
            carpool.update_details(
                name=name,
                origin=origin,
                destination=destination,
                departure_time=departure_time,
                return_time=return_time,
                max_passengers=max_passengers,
                notes=notes
            )
            
            db.session.commit()
            
            # Log the action
            Action.log_carpool_updated(user.username, carpool.id, carpool.name)
            current_app.logger.info(f'Carpool updated: {carpool.id} by {user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating carpool {carpool.id}: {e}')
            return False
    
    @staticmethod
    def delete_carpool(carpool: Carpool, user: User) -> bool:
        """
        Delete a carpool trip.
        
        :param carpool: Carpool to delete
        :param user: User deleting the carpool
        :return: True if deletion successful, False otherwise
        """
        try:
            # Check if user can delete this carpool
            if not (user.is_admin() or carpool.organizer_id == user.id):
                current_app.logger.warning(f'User {user.username} attempted to delete carpool {carpool.id} without permission')
                return False
            
            # Store info for logging
            carpool_id = carpool.id
            carpool_name = carpool.name
            
            # Delete the carpool
            db.session.delete(carpool)
            db.session.commit()
            
            # Log the action
            Action.log_carpool_deleted(user.username, carpool_id, carpool_name)
            current_app.logger.info(f'Carpool deleted: {carpool_id} by {user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting carpool {carpool.id}: {e}')
            return False
    
    @staticmethod
    def join_carpool(carpool: Carpool, user: User) -> bool:
        """
        Add a passenger to a carpool trip.
        
        :param carpool: Carpool to join
        :param user: User joining the carpool
        :return: True if join successful, False otherwise
        """
        try:
            # Check if carpool can accept new passengers
            if not carpool.can_join():
                current_app.logger.warning(f'User {user.username} attempted to join full/past carpool {carpool.id}')
                return False
            
            # Add passenger
            if carpool.add_passenger():
                db.session.commit()
                
                # Log the action
                details = f'Joined carpool: {carpool.name}'
                Action.log_action('carpool_joined', user.username, details)
                current_app.logger.info(f'User {user.username} joined carpool {carpool.id}')
                
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error joining carpool {carpool.id}: {e}')
            return False
    
    @staticmethod
    def leave_carpool(carpool: Carpool, user: User) -> bool:
        """
        Remove a passenger from a carpool trip.
        
        :param carpool: Carpool to leave
        :param user: User leaving the carpool
        :return: True if leave successful, False otherwise
        """
        try:
            # Remove passenger
            if carpool.remove_passenger():
                db.session.commit()
                
                # Log the action
                details = f'Left carpool: {carpool.name}'
                Action.log_action('carpool_left', user.username, details)
                current_app.logger.info(f'User {user.username} left carpool {carpool.id}')
                
                return True
            
            return False
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error leaving carpool {carpool.id}: {e}')
            return False
    
    @staticmethod
    def get_user_carpools(user: User, include_past: bool = False) -> List[Carpool]:
        """
        Get all carpools organized by a specific user.
        
        :param user: User to get carpools for
        :param include_past: Whether to include past carpools
        :return: List of user's organized carpools
        """
        try:
            query = Carpool.query.filter_by(organizer_id=user.id)
            
            if not include_past:
                query = query.filter(Carpool.departure_time >= datetime.utcnow())
            
            return query.order_by(Carpool.departure_time.desc()).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving carpools for user {user.username}: {e}')
            return []
    
    @staticmethod
    def get_available_carpools(include_past: bool = False) -> List[Carpool]:
        """
        Get all available carpools that users can join.
        
        :param include_past: Whether to include past carpools
        :return: List of available carpools
        """
        try:
            query = Carpool.query
            
            if not include_past:
                query = query.filter(Carpool.departure_time >= datetime.utcnow())
            
            return query.order_by(Carpool.departure_time.asc()).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving available carpools: {e}')
            return []
    
    @staticmethod
    def get_carpool_by_id(carpool_id: int) -> Optional[Carpool]:
        """
        Get a carpool by its ID.
        
        :param carpool_id: ID of the carpool to retrieve
        :return: Carpool object if found, None otherwise
        """
        try:
            return Carpool.query.get(carpool_id)
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving carpool by ID {carpool_id}: {e}')
            return None
    
    @staticmethod
    def get_carpool_statistics() -> dict:
        """
        Get carpool statistics for dashboard display.
        
        :return: Dictionary containing carpool statistics
        """
        try:
            now = datetime.utcnow()
            
            total_carpools = Carpool.query.count()
            future_carpools = Carpool.query.filter(Carpool.departure_time >= now).count()
            today_carpools = Carpool.query.filter(
                Carpool.departure_time >= now.replace(hour=0, minute=0, second=0),
                Carpool.departure_time < now.replace(hour=23, minute=59, second=59)
            ).count()
            
            # Calculate average occupancy
            all_carpools = Carpool.query.all()
            total_capacity = sum(c.max_passengers for c in all_carpools)
            total_passengers = sum(c.current_passengers for c in all_carpools)
            occupancy_rate = round((total_passengers / total_capacity * 100) if total_capacity > 0 else 0, 1)
            
            return {
                'total_carpools': total_carpools,
                'future_carpools': future_carpools,
                'today_carpools': today_carpools,
                'total_passengers': total_passengers,
                'occupancy_rate': occupancy_rate
            }
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving carpool statistics: {e}')
            return {
                'total_carpools': 0,
                'future_carpools': 0,
                'today_carpools': 0,
                'total_passengers': 0,
                'occupancy_rate': 0
            }
