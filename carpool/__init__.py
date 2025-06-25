"""
This module initializes the Flask application using the application factory pattern.
It creates and configures the Flask app, registers blueprints, and initializes extensions.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask

from carpool.extensions import db, migrate, csrf, talisman, login_manager
from carpool.models.user import User

# Environment variables are loaded in run.py

def configure_logging(app: Flask) -> None:
    """
    Configure logging for the application.
    
    :param app: Flask application instance
    """
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/carpool.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Carpool application startup')

def create_app(config_name: str = None) -> Flask:
    """
    Create and configure a Flask application instance.
    
    :param config_name: Configuration name, defaults to development
    :return: Configured Flask application
    """
    app = Flask(__name__)
    
    # Configure app from environment or config module
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    from carpool.config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Only enable talisman if security headers are configured
    if app.config.get('SECURITY_HEADERS'):
        talisman.init_app(
            app,
            content_security_policy=app.config['SECURITY_HEADERS'].get('Content-Security-Policy'),
            force_https=app.config.get('SESSION_COOKIE_SECURE', False),
            session_cookie_secure=app.config.get('SESSION_COOKIE_SECURE', False),
            session_cookie_http_only=app.config.get('SESSION_COOKIE_HTTPONLY', True)
        )
    
    # Setup login manager
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id: str) -> User:
        """
        Load a user by ID for Flask-Login.
        
        :param user_id: User ID to load
        :return: User object or None
        """
        return User.query.get(user_id)
    
    # Register blueprints
    from carpool.views.auth import auth
    app.register_blueprint(auth)
    
    from carpool.views.main import main
    app.register_blueprint(main)
    
    from carpool.views.parking import parking
    app.register_blueprint(parking)
    
    from carpool.views.reservations import reservations
    app.register_blueprint(reservations)
    
    from carpool.views.admin import admin
    app.register_blueprint(admin)
    
    from carpool.views.carpools import carpools
    app.register_blueprint(carpools)
    
    # Configure logging
    configure_logging(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app
