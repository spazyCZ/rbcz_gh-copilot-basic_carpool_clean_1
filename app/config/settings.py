import os

class BaseConfig:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    TESTING = False

class DevConfig(BaseConfig):
    DEBUG = True

class TestConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

class ProdConfig(BaseConfig):
    DEBUG = False
