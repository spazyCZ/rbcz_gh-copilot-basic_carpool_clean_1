"""
API Blueprint package initialization.

This module creates and configures the API blueprint for REST endpoints.
All API routes are prefixed with /api/v1.
"""
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import route modules to register them with the blueprint
from . import health
from . import auth  
from . import spots
from . import reservations
from . import users
from . import actions