"""
This module contains imports for all views to simplify imports elsewhere.
"""
from carpool.views.auth import auth
from carpool.views.main import main
from carpool.views.parking import parking
from carpool.views.reservations import reservations
from carpool.views.admin import admin
from carpool.views.carpools import carpools

__all__ = ['auth', 'main', 'parking', 'reservations', 'admin', 'carpools']
