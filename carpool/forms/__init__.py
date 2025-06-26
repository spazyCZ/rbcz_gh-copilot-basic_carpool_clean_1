"""
Forms package initialization.

This module imports all form classes to make them available when the package is imported.
"""

from .auth_forms import LoginForm, RegisterForm
from .reservation_forms import ReservationForm, EditReservationForm
from .carpool_forms import CarpoolForm, EditCarpoolForm
from .admin_forms import CreateUserForm, EditUserForm, CreateParkingSpotForm

__all__ = [
    'LoginForm', 'RegisterForm', 'ReservationForm', 'EditReservationForm',
    'CarpoolForm', 'EditCarpoolForm', 'CreateUserForm', 'EditUserForm', 'CreateParkingSpotForm'
]
