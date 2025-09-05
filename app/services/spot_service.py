"""
Parking spot service layer for managing parking spot operations.

This service handles all business logic related to parking spots,
including availability checking, filtering, and status management.
"""
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import logging

from app.extensions import db
from app.models import ParkingSpot, Reservation


logger = logging.getLogger(__name__)


class SpotService:
    """
    Service class for managing parking spots.
    
    Handles business logic for retrieving spots, checking availability,
    and filtering spots based on various criteria.
    """
    
    def get_all_spots(self, include_unavailable: bool = False) -> Dict[str, Any]:
        """
        Get all parking spots.
        
        :param include_unavailable: Whether to include unavailable spots
        :return: Service result with list of spots
        """
        try:
            if include_unavailable:
                spots = ParkingSpot.query.all()
            else:
                spots = ParkingSpot.query.filter_by(is_available=True).all()
            
            return {
                'success': True,
                'spots': [spot.to_dict() for spot in spots],
                'count': len(spots)
            }
            
        except Exception as e:
            logger.error(f"Error getting all spots: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve parking spots'
            }
    
    def get_spot_by_id(self, spot_id: str, include_reservations: bool = False) -> Dict[str, Any]:
        """
        Get a specific parking spot by ID.
        
        :param spot_id: ID of the spot to retrieve
        :param include_reservations: Whether to include upcoming reservations
        :return: Service result with spot data
        """
        try:
            spot = ParkingSpot.query.get(spot_id)
            
            if not spot:
                return {
                    'success': False,
                    'error': 'SPOT_NOT_FOUND',
                    'message': f'Parking spot {spot_id} not found'
                }
            
            return {
                'success': True,
                'spot': spot.to_dict(include_reservations=include_reservations)
            }
            
        except Exception as e:
            logger.error(f"Error getting spot {spot_id}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve parking spot'
            }
    
    def get_available_spots(self, target_date: Optional[date] = None,
                           handicap_accessible: Optional[bool] = None,
                           electric_charging: Optional[bool] = None) -> Dict[str, Any]:
        """
        Get available parking spots for a specific date with optional filters.
        
        :param target_date: Date to check availability (defaults to today)
        :param handicap_accessible: Filter by handicap accessibility
        :param electric_charging: Filter by electric charging capability
        :return: Service result with list of available spots
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            # Get spots that match the criteria and are available on the target date
            available_spots = ParkingSpot.find_available_spots(
                reservation_date=target_date,
                handicap_accessible=handicap_accessible,
                electric_charging=electric_charging
            )
            
            # Enrich spot data with availability info for the target date
            spots_data = []
            for spot in available_spots:
                spot_dict = spot.to_dict()
                spot_dict['is_available_on_date'] = True
                spot_dict['checked_date'] = target_date.isoformat()
                spots_data.append(spot_dict)
            
            return {
                'success': True,
                'spots': spots_data,
                'count': len(spots_data),
                'filters': {
                    'date': target_date.isoformat(),
                    'handicap_accessible': handicap_accessible,
                    'electric_charging': electric_charging
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting available spots for {target_date}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve available spots'
            }
    
    def get_spot_availability_calendar(self, spot_id: str, 
                                     start_date: Optional[date] = None,
                                     days: int = 30) -> Dict[str, Any]:
        """
        Get availability calendar for a specific spot.
        
        :param spot_id: ID of the spot
        :param start_date: Start date for calendar (defaults to today)
        :param days: Number of days to include
        :return: Service result with availability calendar
        """
        if start_date is None:
            start_date = date.today()
        
        try:
            spot = ParkingSpot.query.get(spot_id)
            if not spot:
                return {
                    'success': False,
                    'error': 'SPOT_NOT_FOUND',
                    'message': f'Parking spot {spot_id} not found'
                }
            
            calendar_data = []
            current_date = start_date
            
            for i in range(days):
                is_reserved = spot.is_reserved_on_date(current_date)
                reservation = spot.get_reservation_for_date(current_date) if is_reserved else None
                
                day_data = {
                    'date': current_date.isoformat(),
                    'is_available': not is_reserved and spot.is_available,
                    'is_reserved': is_reserved,
                    'reservation': reservation.to_dict() if reservation else None
                }
                
                calendar_data.append(day_data)
                current_date = date.fromordinal(current_date.toordinal() + 1)
            
            return {
                'success': True,
                'spot': spot.to_dict(),
                'calendar': calendar_data,
                'period': {
                    'start_date': start_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting availability calendar for spot {spot_id}: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve availability calendar'
            }
    
    def get_spots_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about parking spots.
        
        :return: Service result with spot statistics
        """
        try:
            total_spots = ParkingSpot.query.count()
            available_spots = ParkingSpot.query.filter_by(is_available=True).count()
            handicap_spots = ParkingSpot.query.filter_by(is_handicap_accessible=True).count()
            electric_spots = ParkingSpot.query.filter_by(is_electric_charging=True).count()
            
            # Get today's reservations
            today = date.today()
            today_reservations = Reservation.query.filter(
                Reservation.reservation_date == today,
                Reservation.is_active == True
            ).count()
            
            # Calculate availability for today
            available_today = len(ParkingSpot.find_available_spots(today))
            
            statistics = {
                'total_spots': total_spots,
                'available_spots': available_spots,
                'unavailable_spots': total_spots - available_spots,
                'handicap_accessible_spots': handicap_spots,
                'electric_charging_spots': electric_spots,
                'today_statistics': {
                    'date': today.isoformat(),
                    'reserved_count': today_reservations,
                    'available_count': available_today,
                    'occupancy_rate': (today_reservations / total_spots * 100) if total_spots > 0 else 0
                }
            }
            
            return {
                'success': True,
                'statistics': statistics
            }
            
        except Exception as e:
            logger.error(f"Error getting spot statistics: {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve spot statistics'
            }
    
    def search_spots(self, query: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search parking spots by location or description.
        
        :param query: Search query string
        :param filters: Additional filters (handicap_accessible, electric_charging, etc.)
        :return: Service result with matching spots
        """
        try:
            # Start with base query
            spots_query = ParkingSpot.query.filter_by(is_available=True)
            
            # Apply text search
            if query and query.strip():
                search_pattern = f"%{query.strip()}%"
                spots_query = spots_query.filter(
                    db.or_(
                        ParkingSpot.id.ilike(search_pattern),
                        ParkingSpot.location.ilike(search_pattern),
                        ParkingSpot.description.ilike(search_pattern)
                    )
                )
            
            # Apply filters
            if filters:
                if filters.get('handicap_accessible') is not None:
                    spots_query = spots_query.filter_by(
                        is_handicap_accessible=filters['handicap_accessible']
                    )
                
                if filters.get('electric_charging') is not None:
                    spots_query = spots_query.filter_by(
                        is_electric_charging=filters['electric_charging']
                    )
            
            spots = spots_query.all()
            
            return {
                'success': True,
                'spots': [spot.to_dict() for spot in spots],
                'count': len(spots),
                'query': query,
                'filters': filters or {}
            }
            
        except Exception as e:
            logger.error(f"Error searching spots with query '{query}': {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to search parking spots'
            }
    
    def get_spots_by_location(self, location: str) -> Dict[str, Any]:
        """
        Get spots filtered by location.
        
        :param location: Location to filter by
        :return: Service result with spots at the location
        """
        try:
            spots = ParkingSpot.query.filter(
                ParkingSpot.location.ilike(f"%{location}%"),
                ParkingSpot.is_available == True
            ).all()
            
            return {
                'success': True,
                'spots': [spot.to_dict() for spot in spots],
                'count': len(spots),
                'location': location
            }
            
        except Exception as e:
            logger.error(f"Error getting spots by location '{location}': {e}")
            return {
                'success': False,
                'error': 'INTERNAL_ERROR',
                'message': 'Failed to retrieve spots by location'
            }


# Create global service instance
spot_service = SpotService()