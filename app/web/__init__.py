"""
Web Blueprint package initialization.

This module creates and configures the web blueprint for HTML views.
These views serve minimal templates that fetch data via AJAX from API endpoints.
"""
from flask import Blueprint

# Create web blueprint
web_bp = Blueprint('web', __name__)

# Import route modules to register them with the blueprint
from . import views