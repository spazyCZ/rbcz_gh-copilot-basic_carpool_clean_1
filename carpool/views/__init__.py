"""
Views package initialization.

This module imports all blueprint views to make them available when the package is imported.
"""

from .main import main_bp
from .auth import auth_bp
from .admin import admin_bp
from .api import api_bp

__all__ = ['main_bp', 'auth_bp', 'admin_bp', 'api_bp']
