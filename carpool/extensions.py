"""
This module initializes Flask extensions to be used throughout the application.
Extensions are initialized here without being bound to the application instance.
They will be initialized with the application in the application factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
talisman = Talisman()
login_manager = LoginManager()
