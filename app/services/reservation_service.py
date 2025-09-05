"""
Reservation service layer for managing parking reservations.

This service handles all business logic related to parking reservations,
including availability checking, conflict resolution, and CRUD operations.
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from app.extensions import db
from app.models import Reservation, ParkingSpot, User, Action, ActionType


logger = logging.getLogger(__name__)


class ReservationConflictError(Exception):
    """Exception raised when a reservation conflicts with existing reservations."""
    pass


class ReservationService:
    """
    Service class for managing parking reservations.
    
    Handles business logic for creating, updating, canceling, and retrieving
    reservations with proper conflict detection and audit logging.
    """
    
    def create_reservation(self, user_id: int, spot_id: str, reservation_date: date,
                          name: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new parking reservation with conflict checking.
        
        :param user_id: ID of user making the reservation
        :param spot_id: ID of parking spot to reserve
        :param reservation_date: Date for the reservation
        :param name: Name for the reservation
        :param notes: Optional notes for the reservation
        :return: Service result with reservation data or error
        :raises: ReservationConflictError if spot is already reserved
        """
        logger.info(f"Creating reservation for user {user_id}, spot {spot_id}, date {reservation_date}")
        
        try:
            # Validate inputs
            self._validate_reservation_data(user_id, spot_id, reservation_date, name)
            
            # Check if spot exists and is available
            spot = ParkingSpot.query.get(spot_id)
            if not spot:
                return {
                    'success': False,
                    'error': 'SPOT_NOT_FOUND',
                    'message': f'Parking spot {spot_id} not found'
                }
            
            if not spot.is_available:
                return {
                    'success': False,
                    'error': 'SPOT_UNAVAILABLE', 
                    'message': f'Parking spot {spot_id} is not available'
                }
            
            # Check for existing reservation on the same date
            existing_reservation = Reservation.find_by_spot_and_date(spot_id, reservation_date)
            if existing_reservation:
                logger.warning(f"Reservation conflict: spot {spot_id} already reserved for {reservation_date}")
                return {
                    'success': False,
                    'error': 'RESERVATION_CONFLICT',
                    'message': f'Spot {spot_id} is already reserved for {reservation_date}'
                }
            
            # Create the reservation
            reservation = Reservation.create_reservation(
                spot_id=spot_id,
                user_id=user_id,
                reservation_date=reservation_date,
                name=name,
                notes=notes
            )
            
            # Log the action
            Action.log_action(
                action_type=ActionType.RESERVATION_CREATE,
                description=f"Created reservation for spot {spot_id} on {reservation_date}",
                user_id=user_id,
                extra_data={
                    'reservation_id': reservation.id,
                    'spot_id': spot_id,
                    'reservation_date': reservation_date.isoformat(),
                    'name': name
                }
            )
            
            logger.info(f"Successfully created reservation {reservation.id}")
            
            return {
                'success': True,
                'reservation': reservation.to_dict(include_relations=True),
                'message': 'Reservation created successfully'
            }
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error creating reservation: {e}")
            return {
                'success': False,
                'error': 'RESERVATION_CONFLICT',
                'message': f'Spot {spot_id} is already reserved for {reservation_date}'
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating reservation: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to create reservation due to server error'
            }
    
    def update_reservation(self, reservation_id: int, user_id: int, 
                          name: Optional[str] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing reservation.
        
        :param reservation_id: ID of reservation to update
        :param user_id: ID of user making the update
        :param name: New name for reservation
        :param notes: New notes for reservation
        :return: Service result with updated reservation data
        """
        logger.info(f"Updating reservation {reservation_id} by user {user_id}")
        
        try:
            # Find the reservation
            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                return {
                    'success': False,
                    'error': 'RESERVATION_NOT_FOUND',
                    'message': f'Reservation {reservation_id} not found'
                }
            
            # Check authorization (user can only update their own reservations)
            if reservation.user_id != user_id:
                return {
                    'success': False,
                    'error': 'UNAUTHORIZED',
                    'message': 'You can only update your own reservations'
                }
            
            # Check if reservation is still active
            if not reservation.is_active:
                return {
                    'success': False,
                    'error': 'RESERVATION_CANCELLED',
                    'message': 'Cannot update a cancelled reservation'
                }
            
            # Store original values for logging
            original_data = {
                'name': reservation.name,
                'notes': reservation.notes
            }
            
            # Update the reservation
            reservation.update_reservation(name=name, notes=notes)
            
            # Log the action
            Action.log_action(
                action_type=ActionType.RESERVATION_UPDATE,
                description=f"Updated reservation {reservation_id}",
                user_id=user_id,
                extra_data={
                    'reservation_id': reservation_id,
                    'original_data': original_data,
                    'updated_data': {
                        'name': reservation.name,
                        'notes': reservation.notes
                    }
                }
            )
            
            logger.info(f"Successfully updated reservation {reservation_id}")
            
            return {
                'success': True,
                'reservation': reservation.to_dict(include_relations=True),
                'message': 'Reservation updated successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating reservation {reservation_id}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to update reservation due to server error'
            }
    
    def cancel_reservation(self, reservation_id: int, user_id: int) -> Dict[str, Any]:
        """
        Cancel an existing reservation.
        
        :param reservation_id: ID of reservation to cancel
        :param user_id: ID of user making the cancellation
        :return: Service result with cancellation status
        """
        logger.info(f"Cancelling reservation {reservation_id} by user {user_id}")
        
        try:
            # Find the reservation
            reservation = Reservation.query.get(reservation_id)
            if not reservation:
                return {
                    'success': False,
                    'error': 'RESERVATION_NOT_FOUND',
                    'message': f'Reservation {reservation_id} not found'
                }
            
            # Check authorization
            if reservation.user_id != user_id:
                return {
                    'success': False,
                    'error': 'UNAUTHORIZED',
                    'message': 'You can only cancel your own reservations'
                }
            
            # Check if already cancelled
            if not reservation.is_active:
                return {
                    'success': False,
                    'error': 'RESERVATION_ALREADY_CANCELLED',
                    'message': 'Reservation is already cancelled'
                }
            
            # Store data for logging
            reservation_data = {
                'spot_id': reservation.spot_id,
                'reservation_date': reservation.reservation_date.isoformat(),
                'name': reservation.name
            }
            
            # Cancel the reservation
            reservation.cancel_reservation()
            
            # Log the action
            Action.log_action(
                action_type=ActionType.RESERVATION_DELETE,
                description=f"Cancelled reservation {reservation_id}",
                user_id=user_id,
                extra_data={
                    'reservation_id': reservation_id,
                    'reservation_data': reservation_data
                }
            )
            
            logger.info(f"Successfully cancelled reservation {reservation_id}")
            
            return {
                'success': True,
                'reservation': reservation.to_dict(include_relations=True),
                'message': 'Reservation cancelled successfully'
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error cancelling reservation {reservation_id}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to cancel reservation due to server error'
            }
    
    def get_user_reservations(self, user_id: int, include_cancelled: bool = False) -> Dict[str, Any]:
        """
        Get all reservations for a specific user.
        
        :param user_id: ID of user to get reservations for
        :param include_cancelled: Whether to include cancelled reservations
        :return: Service result with list of reservations
        """
        try:
            reservations = Reservation.find_by_user(user_id, include_cancelled=include_cancelled)
            
            return {
                'success': True,
                'reservations': [r.to_dict(include_relations=True) for r in reservations],
                'count': len(reservations)
            }
            
        except Exception as e:
            logger.error(f"Error getting reservations for user {user_id}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve reservations'
            }
    
    def get_reservations_by_date_range(self, start_date: date, end_date: date,
                                     spot_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get reservations within a date range.
        
        :param start_date: Start date for range
        :param end_date: End date for range
        :param spot_id: Optional filter by specific spot
        :return: Service result with list of reservations
        """
        try:
            reservations = Reservation.get_reservations_for_date_range(
                start_date=start_date,
                end_date=end_date,
                spot_id=spot_id
            )
            
            return {
                'success': True,
                'reservations': [r.to_dict(include_relations=True) for r in reservations],
                'count': len(reservations),
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting reservations for date range {start_date} to {end_date}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve reservations'
            }
    
    def get_upcoming_reservations(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get upcoming reservations across all users.
        
        :param limit: Maximum number of reservations to return
        :return: Service result with list of upcoming reservations
        """
        try:
            reservations = Reservation.find_upcoming_reservations(limit=limit)
            
            return {
                'success': True,
                'reservations': [r.to_dict(include_relations=True) for r in reservations],
                'count': len(reservations)
            }
            
        except Exception as e:
            logger.error(f"Error getting upcoming reservations: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve upcoming reservations'
            }
    
    def _validate_reservation_data(self, user_id: int, spot_id: str, 
                                 reservation_date: date, name: str) -> None:
        """
        Validate reservation data.
        
        :param user_id: User ID to validate
        :param spot_id: Spot ID to validate
        :param reservation_date: Date to validate
        :param name: Name to validate
        :raises: ValueError if validation fails
        """
        if not user_id or user_id <= 0:
            raise ValueError("Invalid user ID")
        
        if not spot_id or not spot_id.strip():
            raise ValueError("Invalid spot ID")
        
        if not name or not name.strip():
            raise ValueError("Name is required")
        
        if reservation_date < date.today():
            raise ValueError("Cannot make reservations for past dates")
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid or inactive user")


# Create global service instance
reservation_service = ReservationService()