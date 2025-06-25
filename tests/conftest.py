"""
Configuration for pytest.
"""
import os
import pytest
from carpool import create_app
from carpool.extensions import db as _db

@pytest.fixture
def app():
    """
    Create and configure a Flask app for testing.
    
    :return: Flask app instance
    """
    # Use an in-memory SQLite database for testing
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create the database and context
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def db(app):
    """
    Provide the database instance.
    
    :param app: Flask application
    :return: SQLAlchemy database instance
    """
    return _db

@pytest.fixture
def client(app):
    """
    Create a test client for the app.
    
    :param app: Flask application
    :return: Flask test client
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    Create a CLI runner for the app.
    
    :param app: Flask application
    :return: Flask CLI runner
    """
    return app.test_cli_runner()
