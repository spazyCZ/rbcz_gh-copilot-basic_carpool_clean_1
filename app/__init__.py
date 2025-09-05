"""
Flask application factory and initialization.

This module contains the create_app function that creates and configures
the Flask application instance with all extensions, blueprints, and configuration.
"""
import logging
import os
from typing import Optional

from flask import Flask, jsonify
from dotenv import load_dotenv

from config.settings import get_config
from app.extensions import db, migrate, login_manager, csrf, limiter, init_login_manager


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Create and configure Flask application instance.
    
    :param config_name: Configuration name ('development', 'testing', 'production')
    :return: Configured Flask application
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Create Flask app with explicit template and static paths
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__,
                template_folder=os.path.join(base_dir, 'templates'),
                static_folder=os.path.join(base_dir, 'static'))
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    init_login_manager(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    app.logger.info(f"Application created with {config_name or 'default'} configuration")
    
    return app


def register_cli_commands(app: Flask) -> None:
    """
    Register CLI commands with the application.
    
    :param app: Flask application instance
    """
    from app.cli import init_cli_commands
    init_cli_commands(app)


def configure_logging(app: Flask) -> None:
    """
    Configure application logging.
    
    :param app: Flask application instance
    """
    # Set log level from configuration
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # Create formatter for structured logging
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    
    # Console handler
    if not app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        app.logger.addHandler(console_handler)
    
    # File handler for production
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/parking_app.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers for the application.
    
    :param app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'The requested resource was not found'
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        app.logger.error(f'Internal server error: {error}')
        db.session.rollback()
        return jsonify({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An internal server error occurred'
            }
        }), 500
    
    @app.errorhandler(429)
    def ratelimit_handler(error):
        """Handle rate limit exceeded errors."""
        return jsonify({
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': 'Rate limit exceeded. Please try again later.'
            }
        }), 429


def register_blueprints(app: Flask) -> None:
    """
    Register all application blueprints.
    
    :param app: Flask application instance
    """
    # Import blueprints here to avoid circular imports
    from app.api import api_bp
    from app.web import web_bp
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register web blueprint  
    app.register_blueprint(web_bp, url_prefix='/')
    
    app.logger.info("Blueprints registered successfully")