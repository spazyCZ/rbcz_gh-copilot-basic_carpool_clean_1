"""
Reservation service for managing parking reservations.

This module provides business logic for parking spot reservations including
creation, modification, cancellation, and validation operations.
"""

from typing import List, Optional
from datetime import date, datetime
from flask import current_app
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.action import Action
from extensions import db


class ReservationService:
    """
    Reservation service class providing business logic for parking reservations.
    
    Handles reservation creation, modification, cancellation, and validation operations.
    """
    
    @staticmethod
    def create_reservation(user: User, spot_id: str, name: str, reservation_date: date) -> Optional[Reservation]:
        """
        Create a new parking reservation.
        
        :param user: User making the reservation
        :param spot_id: ID of the parking spot to reserve
        :param name: Name for the reservation
        :param reservation_date: Date of the reservation
        :return: Created Reservation object if successful, None otherwise
        """
        try:
            # Validate that the user can make reservations
            if not user.can_make_reservation():
                current_app.logger.warning(f'User {user.username} attempted to make reservation without permission')
                return None
            
            # Check if parking spot exists
            parking_spot = ParkingSpot.query.get(spot_id)
            if not parking_spot:
                current_app.logger.warning(f'Attempted reservation for non-existent spot: {spot_id}')
                return None
            
            # Check if spot is available
            if not parking_spot.is_available():
                current_app.logger.warning(f'Attempted reservation for unavailable spot: {spot_id}')
                return None
            
            # Check for double booking
            if Reservation.check_double_booking(spot_id, reservation_date):
                current_app.logger.warning(f'Double booking attempted for spot {spot_id} on {reservation_date}')
                return None
            
            # Create the reservation
            reservation = Reservation(
                spot_id=spot_id,
                user_id=user.id,
                name=name,
                reservation_date=reservation_date
            )
            
            db.session.add(reservation)
            db.session.commit()
            
            # Log the action
            Action.log_reservation_created(user.username, spot_id, str(reservation_date))
            current_app.logger.info(f'Reservation created: {reservation.id} by {user.username}')
            
            return reservation
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating reservation: {e}')
            return None
    
    @staticmethod
    def update_reservation(reservation: Reservation, user: User, new_name: str = None, 
                          new_spot_id: str = None, new_date: date = None) -> bool:
        """
        Update an existing reservation.
        
        :param reservation: Reservation to update
        :param user: User updating the reservation
        :param new_name: New name for the reservation
        :param new_spot_id: New parking spot ID
        :param new_date: New reservation date
        :return: True if update successful, False otherwise
        """
        try:
            # Check if user can modify this reservation
            if not (user.is_admin() or reservation.user_id == user.id):
                current_app.logger.warning(f'User {user.username} attempted to modify reservation {reservation.id} without permission')
                return False
            
            # Check if reservation can be modified
            if not reservation.can_be_modified():
                current_app.logger.warning(f'Attempted to modify past reservation: {reservation.id}')
                return False
            
            # Store original values for logging
            original_spot = reservation.spot_id
            original_date = reservation.reservation_date
            
            # Update name if provided
            if new_name is not None:
                reservation.update_name(new_name)
            
            # Update spot if provided
            if new_spot_id is not None and new_spot_id != reservation.spot_id:
                # Check if new spot exists
                parking_spot = ParkingSpot.query.get(new_spot_id)
                if not parking_spot or not parking_spot.is_available():
                    current_app.logger.warning(f'Attempted to move reservation to unavailable spot: {new_spot_id}')
                    return False
                
                # Check for double booking on new spot
                check_date = new_date if new_date else reservation.reservation_date
                if Reservation.check_double_booking(new_spot_id, check_date, reservation.id):
                    current_app.logger.warning(f'Double booking attempted for spot {new_spot_id} on {check_date}')
                    return False
                
                reservation.spot_id = new_spot_id
            
            # Update date if provided
            if new_date is not None and new_date != reservation.reservation_date:
                # Check for double booking on new date
                check_spot = new_spot_id if new_spot_id else reservation.spot_id
                if Reservation.check_double_booking(check_spot, new_date, reservation.id):
                    current_app.logger.warning(f'Double booking attempted for spot {check_spot} on {new_date}')
                    return False
                
                reservation.reservation_date = new_date
            
            db.session.commit()
            
            # Log the action
            Action.log_reservation_updated(user.username, reservation.id, reservation.spot_id)
            current_app.logger.info(f'Reservation updated: {reservation.id} by {user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating reservation {reservation.id}: {e}')
            return False
    
    @staticmethod
    def cancel_reservation(reservation: Reservation, user: User) -> bool:
        """
        Cancel an existing reservation.
        
        :param reservation: Reservation to cancel
        :param user: User cancelling the reservation
        :return: True if cancellation successful, False otherwise
        """
        try:
            # Check if user can cancel this reservation
            if not (user.is_admin() or reservation.user_id == user.id):
                current_app.logger.warning(f'User {user.username} attempted to cancel reservation {reservation.id} without permission')
                return False
            
            # Check if reservation can be cancelled
            if not reservation.can_be_cancelled():
                current_app.logger.warning(f'Attempted to cancel non-cancellable reservation: {reservation.id}')
                return False
            
            # Store info for logging
            spot_id = reservation.spot_id
            reservation_id = reservation.id
            
            # Delete the reservation
            db.session.delete(reservation)
            db.session.commit()
            
            # Log the action
            Action.log_reservation_cancelled(user.username, reservation_id, spot_id)
            current_app.logger.info(f'Reservation cancelled: {reservation_id} by {user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error cancelling reservation {reservation.id}: {e}')
            return False
    
    @staticmethod
    def get_user_reservations(user: User, include_past: bool = False) -> List[Reservation]:
        """
        Get all reservations for a specific user.
        
        :param user: User to get reservations for
        :param include_past: Whether to include past reservations
        :return: List of user's reservations
        """
        try:
            query = Reservation.query.filter_by(user_id=user.id)
            
            if not include_past:
                today = datetime.utcnow().date()
                query = query.filter(Reservation.reservation_date >= today)
            
            return query.order_by(Reservation.reservation_date.desc()).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving reservations for user {user.username}: {e}')
            return []
    
    @staticmethod
    def get_reservations_by_date(target_date: date) -> List[Reservation]:
        """
        Get all reservations for a specific date.
        
        :param target_date: Date to get reservations for
        :return: List of reservations for the date
        """
        try:
            return Reservation.query.filter_by(reservation_date=target_date).order_by(Reservation.spot_id).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving reservations for date {target_date}: {e}')
            return []
    
    @staticmethod
    def get_reservation_by_id(reservation_id: int) -> Optional[Reservation]:
        """
        Get a reservation by its ID.
        
        :param reservation_id: ID of the reservation to retrieve
        :return: Reservation object if found, None otherwise
        """
        try:
            return Reservation.query.get(reservation_id)
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving reservation by ID {reservation_id}: {e}')
            return None
    
    @staticmethod
    def get_available_spots_for_date(target_date: date) -> List[ParkingSpot]:
        """
        Get all available parking spots for a specific date.
        
        :param target_date: Date to check availability for
        :return: List of available parking spots
        """
        try:
            # Get all reserved spot IDs for the date
            reserved_spots = db.session.query(Reservation.spot_id).filter_by(reservation_date=target_date).all()
            reserved_spot_ids = [spot[0] for spot in reserved_spots]
            
            # Get all available spots not in the reserved list
            available_spots = ParkingSpot.query.filter(
                ParkingSpot.status == 'available',
                ~ParkingSpot.id.in_(reserved_spot_ids)
            ).order_by(ParkingSpot.id).all()
            
            return available_spots
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving available spots for date {target_date}: {e}')
            return []
    
    @staticmethod
    def get_reservation_statistics() -> dict:
        """
        Get reservation statistics for dashboard display.
        
        :return: Dictionary containing reservation statistics
        """
        try:
            today = datetime.utcnow().date()
            
            total_reservations = Reservation.query.count()
            future_reservations = Reservation.query.filter(Reservation.reservation_date >= today).count()
            today_reservations = Reservation.query.filter_by(reservation_date=today).count()
            total_spots = ParkingSpot.query.count()
            available_spots = ParkingSpot.query.filter_by(status='available').count()
            
            return {
                'total_reservations': total_reservations,
                'future_reservations': future_reservations,
                'today_reservations': today_reservations,
                'total_spots': total_spots,
                'available_spots': available_spots,
                'utilization_rate': round((today_reservations / total_spots * 100) if total_spots > 0 else 0, 1)
            }
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving reservation statistics: {e}')
            return {
                'total_reservations': 0,
                'future_reservations': 0,
                'today_reservations': 0,
                'total_spots': 0,
                'available_spots': 0,
                'utilization_rate': 0
            }
