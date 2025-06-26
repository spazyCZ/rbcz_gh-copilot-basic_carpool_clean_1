"""
Admin service for administrative operations and system management.

This module provides business logic for administrative operations including
user management, system monitoring, and activity logging.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from flask import current_app
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.carpool import Carpool
from carpool.models.action import Action
from carpool.services.auth_service import AuthService
from extensions import db


class AdminService:
    """
    Admin service class providing business logic for administrative operations.
    
    Handles user management, system monitoring, parking spot management, and activity logging.
    """
    
    @staticmethod
    def get_all_users() -> List[User]:
        """
        Get all users in the system.
        
        :return: List of all users
        """
        try:
            return User.query.order_by(User.created_at.desc()).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving all users: {e}')
            return []
    
    @staticmethod
    def create_user(admin_user: User, username: str, email: str, password: str, role: str = 'user') -> Optional[User]:
        """
        Create a new user (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param username: Username for the new user
        :param email: Email for the new user
        :param password: Password for the new user
        :param role: Role for the new user
        :return: Created User object if successful, None otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to create user')
                return None
            
            user = AuthService.create_user(username, email, password, role)
            if user:
                # Log the admin action
                details = f'Created user {username} with role {role}'
                Action.log_admin_action(admin_user.username, details)
            
            return user
            
        except Exception as e:
            current_app.logger.error(f'Error creating user by admin {admin_user.username}: {e}')
            return None
    
    @staticmethod
    def update_user_role(admin_user: User, target_user: User, new_role: str) -> bool:
        """
        Update a user's role (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param target_user: User whose role is being updated
        :param new_role: New role for the user
        :return: True if update successful, False otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to update user role')
                return False
            
            return AuthService.update_user_role(target_user, new_role, admin_user.username)
            
        except Exception as e:
            current_app.logger.error(f'Error updating user role by admin {admin_user.username}: {e}')
            return False
    
    @staticmethod
    def delete_user(admin_user: User, target_user: User) -> bool:
        """
        Delete a user (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param target_user: User to be deleted
        :return: True if deletion successful, False otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to delete user')
                return False
            
            # Don't allow admin to delete themselves
            if admin_user.id == target_user.id:
                current_app.logger.warning(f'Admin {admin_user.username} attempted to delete their own account')
                return False
            
            return AuthService.delete_user(target_user, admin_user.username)
            
        except Exception as e:
            current_app.logger.error(f'Error deleting user by admin {admin_user.username}: {e}')
            return False
    
    @staticmethod
    def create_parking_spot(admin_user: User, spot_id: str, location: str, description: str = None) -> Optional[ParkingSpot]:
        """
        Create a new parking spot (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param spot_id: Unique ID for the parking spot
        :param location: Location description
        :param description: Optional description
        :return: Created ParkingSpot object if successful, None otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to create parking spot')
                return None
            
            # Check if spot ID already exists
            if ParkingSpot.query.get(spot_id):
                current_app.logger.warning(f'Attempted to create parking spot with existing ID: {spot_id}')
                return None
            
            # Create the parking spot
            parking_spot = ParkingSpot(id=spot_id, location=location, description=description)
            db.session.add(parking_spot)
            db.session.commit()
            
            # Log the action
            details = f'Created parking spot {spot_id} at {location}'
            Action.log_admin_action(admin_user.username, details)
            current_app.logger.info(f'Parking spot created: {spot_id} by admin {admin_user.username}')
            
            return parking_spot
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error creating parking spot by admin {admin_user.username}: {e}')
            return None
    
    @staticmethod
    def update_parking_spot_status(admin_user: User, spot: ParkingSpot, new_status: str) -> bool:
        """
        Update a parking spot's status (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param spot: Parking spot to update
        :param new_status: New status for the spot
        :return: True if update successful, False otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to update parking spot status')
                return False
            
            old_status = spot.status
            spot.status = new_status
            db.session.commit()
            
            # Log the action
            details = f'Updated parking spot {spot.id} status from {old_status} to {new_status}'
            Action.log_admin_action(admin_user.username, details)
            current_app.logger.info(f'Parking spot status updated: {spot.id} by admin {admin_user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error updating parking spot status by admin {admin_user.username}: {e}')
            return False
    
    @staticmethod
    def delete_parking_spot(admin_user: User, spot: ParkingSpot) -> bool:
        """
        Delete a parking spot (admin operation).
        
        :param admin_user: Admin user performing the operation
        :param spot: Parking spot to delete
        :return: True if deletion successful, False otherwise
        """
        try:
            if not admin_user.is_admin():
                current_app.logger.warning(f'Non-admin user {admin_user.username} attempted to delete parking spot')
                return False
            
            # Check if spot has active reservations
            active_reservations = Reservation.query.filter(
                Reservation.spot_id == spot.id,
                Reservation.reservation_date >= datetime.utcnow().date()
            ).count()
            
            if active_reservations > 0:
                current_app.logger.warning(f'Attempted to delete parking spot {spot.id} with active reservations')
                return False
            
            spot_id = spot.id
            db.session.delete(spot)
            db.session.commit()
            
            # Log the action
            details = f'Deleted parking spot {spot_id}'
            Action.log_admin_action(admin_user.username, details)
            current_app.logger.info(f'Parking spot deleted: {spot_id} by admin {admin_user.username}')
            
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deleting parking spot by admin {admin_user.username}: {e}')
            return False
    
    @staticmethod
    def get_system_statistics() -> Dict:
        """
        Get comprehensive system statistics for admin dashboard.
        
        :return: Dictionary containing system statistics
        """
        try:
            now = datetime.utcnow()
            today = now.date()
            week_ago = today - timedelta(days=7)
            
            # User statistics
            total_users = User.query.count()
            admin_users = User.query.filter_by(role='administrator').count()
            regular_users = User.query.filter_by(role='user').count()
            guest_users = User.query.filter_by(role='guest').count()
            
            # Parking statistics
            total_spots = ParkingSpot.query.count()
            available_spots = ParkingSpot.query.filter_by(status='available').count()
            reserved_spots = ParkingSpot.query.filter_by(status='reserved').count()
            maintenance_spots = ParkingSpot.query.filter_by(status='maintenance').count()
            
            # Reservation statistics
            total_reservations = Reservation.query.count()
            today_reservations = Reservation.query.filter_by(reservation_date=today).count()
            future_reservations = Reservation.query.filter(Reservation.reservation_date > today).count()
            week_reservations = Reservation.query.filter(Reservation.reservation_date >= week_ago).count()
            
            # Carpool statistics
            total_carpools = Carpool.query.count()
            future_carpools = Carpool.query.filter(Carpool.departure_time >= now).count()
            today_carpools = Carpool.query.filter(
                Carpool.departure_time >= now.replace(hour=0, minute=0, second=0),
                Carpool.departure_time < now.replace(hour=23, minute=59, second=59)
            ).count()
            
            # Activity statistics
            total_actions = Action.query.count()
            today_actions = Action.query.filter(
                Action.timestamp >= now.replace(hour=0, minute=0, second=0)
            ).count()
            week_actions = Action.query.filter(Action.timestamp >= week_ago).count()
            
            return {
                'users': {
                    'total': total_users,
                    'administrators': admin_users,
                    'regular': regular_users,
                    'guests': guest_users
                },
                'parking': {
                    'total_spots': total_spots,
                    'available': available_spots,
                    'reserved': reserved_spots,
                    'maintenance': maintenance_spots,
                    'utilization_rate': round((reserved_spots / total_spots * 100) if total_spots > 0 else 0, 1)
                },
                'reservations': {
                    'total': total_reservations,
                    'today': today_reservations,
                    'future': future_reservations,
                    'week': week_reservations
                },
                'carpools': {
                    'total': total_carpools,
                    'future': future_carpools,
                    'today': today_carpools
                },
                'activity': {
                    'total_actions': total_actions,
                    'today_actions': today_actions,
                    'week_actions': week_actions
                }
            }
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving system statistics: {e}')
            return {}
    
    @staticmethod
    def get_activity_logs(limit: int = 100, action_type: str = None, username: str = None) -> List[Action]:
        """
        Get system activity logs with optional filtering.
        
        :param limit: Maximum number of logs to retrieve
        :param action_type: Filter by action type
        :param username: Filter by username
        :return: List of action logs
        """
        try:
            query = Action.query
            
            if action_type:
                query = query.filter_by(action_type=action_type)
            
            if username:
                query = query.filter_by(username=username)
            
            return query.order_by(Action.timestamp.desc()).limit(limit).all()
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving activity logs: {e}')
            return []
    
    @staticmethod
    def get_activity_chart_data(days: int = 7) -> Dict:
        """
        Get activity data for chart visualization.
        
        :param days: Number of days to include in the chart
        :return: Dictionary containing chart data
        """
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days-1)
            
            # Get daily activity counts
            daily_counts = {}
            for i in range(days):
                date = start_date + timedelta(days=i)
                count = Action.query.filter(
                    Action.timestamp >= datetime.combine(date, datetime.min.time()),
                    Action.timestamp < datetime.combine(date + timedelta(days=1), datetime.min.time())
                ).count()
                daily_counts[date.strftime('%Y-%m-%d')] = count
            
            return {
                'labels': list(daily_counts.keys()),
                'data': list(daily_counts.values())
            }
            
        except Exception as e:
            current_app.logger.error(f'Error retrieving activity chart data: {e}')
            return {'labels': [], 'data': []}
