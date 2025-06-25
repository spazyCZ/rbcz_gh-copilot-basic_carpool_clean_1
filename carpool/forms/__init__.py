"""
This module contains imports for all forms to simplify imports elsewhere.
"""
from carpool.forms.auth_forms import LoginForm, RegistrationForm, UserForm
from carpool.forms.parking_forms import ParkingSpotForm
from carpool.forms.reservation_forms import ReservationForm
from carpool.forms.carpool_forms import CarpoolForm, JoinCarpoolForm, LeaveCarpoolForm, CancelCarpoolForm

__all__ = [
    'LoginForm', 'RegistrationForm', 'UserForm', 
    'ParkingSpotForm', 'ReservationForm',
    'CarpoolForm', 'JoinCarpoolForm', 'LeaveCarpoolForm', 'CancelCarpoolForm'
]
