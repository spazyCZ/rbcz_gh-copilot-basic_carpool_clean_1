"""
Flask application factory module.

This module contains the application factory function that creates and configures
the Flask application instance with all necessary extensions and blueprints.
"""

import os
import logging
from flask import Flask
from config import config
from extensions import init_extensions


def create_app(config_name=None):
    """
    Application factory function that creates and configures the Flask app.
    
    :param config_name: Configuration environment name (development, testing, production)
    :return: Configured Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Create Flask application instance
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        from extensions import db
        from carpool.models import User, ParkingSpot, Reservation, Carpool, Action
        db.create_all()
        
        # Create default admin user if it doesn't exist
        create_default_admin(app, db)
    
    return app


def configure_logging(app):
    """
    Configure application logging.
    
    :param app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Configure file logging for production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/carpool.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Carpool application startup')


def register_blueprints(app):
    """
    Register all application blueprints.
    
    :param app: Flask application instance
    """
    from carpool.views.main import main_bp
    from carpool.views.auth import auth_bp
    from carpool.views.admin import admin_bp
    from carpool.views.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')


def create_default_admin(app, db):
    """
    Create default admin user if it doesn't exist.
    
    :param app: Flask application instance
    :param db: Database instance
    """
    from carpool.models import User
    from carpool.services.auth_service import AuthService
    
    admin_username = app.config['ADMIN_USERNAME']
    admin_email = app.config['ADMIN_EMAIL']
    admin_password = app.config['ADMIN_PASSWORD']
    
    # Check if admin user already exists
    admin_user = User.query.filter_by(username=admin_username).first()
    if not admin_user:
        admin_user = User(
            username=admin_username,
            email=admin_email,
            role='administrator'
        )
        admin_user.password_hash = AuthService.hash_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
        app.logger.info(f'Created default admin user: {admin_username}')
