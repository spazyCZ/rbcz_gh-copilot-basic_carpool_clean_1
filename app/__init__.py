from flask import Flask
from .config.settings import DevConfig
from .extensions import db, migrate, login_manager
from .api import bp as api_bp
from .web import bp as web_bp


def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    return app
