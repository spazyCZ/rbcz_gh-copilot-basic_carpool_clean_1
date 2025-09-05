"""
Flask extensions initialization module.

This module initializes all Flask extensions used in the application
without binding them to a specific app instance (to support app factory pattern).
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions without app binding
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)


def init_login_manager(app) -> None:
    """
    Initialize and configure the login manager.
    
    :param app: Flask application instance
    """
    login_manager.login_view = 'web.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id: str):
        """
        Load user from database by user ID for Flask-Login.
        
        :param user_id: User ID as string
        :return: User instance or None
        """
        # Import here to avoid circular imports
        from app.models.user import User
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None