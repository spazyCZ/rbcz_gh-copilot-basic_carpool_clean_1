"""
Flask extensions initialization module.

This module initializes and configures all Flask extensions used in the application.
Extensions are created here and then initialized with the app in the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_moment import Moment

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
talisman = Talisman()
moment = Moment()


def init_extensions(app):
    """
    Initialize all Flask extensions with the given app instance.
    
    :param app: Flask application instance
    """
    # Database
    db.init_app(app)
    
    # Database migrations
    migrate.init_app(app, db)
    
    # Login management
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # CSRF protection
    csrf.init_app(app)
    
    # Date/time formatting for templates
    moment.init_app(app)
    
    # Security headers (only in production)
    if not app.debug:
        talisman.init_app(
            app,
            content_security_policy={
                'default-src': "'self'",
                'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net",
                'style-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
                'font-src': "'self' https://cdnjs.cloudflare.com",
                'img-src': "'self' data:",
            },
            force_https=False,  # Set to True in production with HTTPS
        )
