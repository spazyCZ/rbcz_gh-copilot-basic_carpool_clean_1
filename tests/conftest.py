"""
Test configuration and fixtures for the Carpool application.

This module provides common test fixtures and configuration
used across all test modules.
"""

import os
import tempfile
import pytest
from datetime import datetime, timedelta

from carpool import create_app
from carpool.models import db, User, ParkingSpot, Reservation, Carpool, Action
from carpool.services.auth_service import AuthService
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create and configure a test application instance."""
    # Create a temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Test configuration
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
        'LOGIN_DISABLED': False,
        'SERVER_NAME': 'localhost:5000'
    }
    
    # Create the app with test config
    app = create_app(test_config)
    
    with app.app_context():
        # Create all database tables
        db.create_all()
        yield app
        
        # Cleanup
        db.drop_all()
        db.session.remove()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        # Begin a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the transaction
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session
        
        yield session
        
        # Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def auth_service(app):
    """Create an AuthService instance for testing."""
    with app.app_context():
        return AuthService()


# User Fixtures
@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('testpass123'),
        role='user'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user."""
    user = User(
        username='admin',
        email='admin@example.com',
        password_hash=generate_password_hash('adminpass123'),
        role='administrator'
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def guest_user(db_session):
    """Create a guest user."""
    user = User(
        username='guest',
        email='guest@example.com',
        password_hash=generate_password_hash('guestpass123'),
        role='guest'
    )
    db_session.add(user)
    db_session.commit()
    return user


# Parking Spot Fixtures
@pytest.fixture
def parking_spot(db_session):
    """Create a test parking spot."""
    spot = ParkingSpot(
        id='A1',
        location='Level A',
        description='Near elevator',
        status='available'
    )
    db_session.add(spot)
    db_session.commit()
    return spot


@pytest.fixture
def multiple_parking_spots(db_session):
    """Create multiple test parking spots."""
    spots = [
        ParkingSpot(id='A1', location='Level A', description='Near elevator', status='available'),
        ParkingSpot(id='A2', location='Level A', description='Corner spot', status='available'),
        ParkingSpot(id='B1', location='Level B', description='Covered parking', status='available'),
        ParkingSpot(id='B2', location='Level B', description='Wide space', status='reserved'),
        ParkingSpot(id='C1', location='Outdoor', description='Open air', status='maintenance'),
    ]
    
    for spot in spots:
        db_session.add(spot)
    
    db_session.commit()
    return spots


# Reservation Fixtures
@pytest.fixture
def reservation(db_session, test_user, parking_spot):
    """Create a test reservation."""
    reservation = Reservation(
        spot_id=parking_spot.id,
        user_id=test_user.id,
        name='Test Meeting',
        reservation_date=datetime.now().date() + timedelta(days=1)
    )
    db_session.add(reservation)
    db_session.commit()
    return reservation


@pytest.fixture
def multiple_reservations(db_session, test_user, multiple_parking_spots):
    """Create multiple test reservations."""
    reservations = [
        Reservation(
            spot_id='A1',
            user_id=test_user.id,
            name='Meeting 1',
            reservation_date=datetime.now().date() + timedelta(days=1)
        ),
        Reservation(
            spot_id='A2',
            user_id=test_user.id,
            name='Meeting 2',
            reservation_date=datetime.now().date() + timedelta(days=2)
        ),
        Reservation(
            spot_id='B1',
            user_id=test_user.id,
            name='Meeting 3',
            reservation_date=datetime.now().date() + timedelta(days=3)
        ),
    ]
    
    for reservation in reservations:
        db_session.add(reservation)
    
    db_session.commit()
    return reservations


# Carpool Fixtures
@pytest.fixture
def carpool(db_session, test_user):
    """Create a test carpool."""
    carpool = Carpool(
        name='Test Carpool Trip',
        origin='Downtown Office',
        destination='Airport',
        departure_time=datetime.now() + timedelta(hours=24),
        return_time=datetime.now() + timedelta(hours=30),
        max_passengers=4,
        current_passengers=1,
        notes='Test carpool for airport trip',
        organizer_id=test_user.id
    )
    db_session.add(carpool)
    db_session.commit()
    return carpool


@pytest.fixture
def multiple_carpools(db_session, test_user, admin_user):
    """Create multiple test carpools."""
    carpools = [
        Carpool(
            name='Airport Trip',
            origin='Office',
            destination='Airport',
            departure_time=datetime.now() + timedelta(hours=24),
            return_time=datetime.now() + timedelta(hours=30),
            max_passengers=4,
            current_passengers=2,
            organizer_id=test_user.id
        ),
        Carpool(
            name='Conference Trip',
            origin='Office',
            destination='Convention Center',
            departure_time=datetime.now() + timedelta(hours=48),
            return_time=datetime.now() + timedelta(hours=56),
            max_passengers=3,
            current_passengers=1,
            organizer_id=admin_user.id
        ),
        Carpool(
            name='Team Outing',
            origin='Office',
            destination='Restaurant',
            departure_time=datetime.now() + timedelta(hours=72),
            max_passengers=6,
            current_passengers=3,
            organizer_id=test_user.id
        ),
    ]
    
    for carpool in carpools:
        db_session.add(carpool)
    
    db_session.commit()
    return carpools


# Action Log Fixtures
@pytest.fixture
def action_log(db_session, test_user):
    """Create a test action log entry."""
    action = Action(
        action_type='reservation_created',
        username=test_user.username,
        details='Created reservation for spot A1'
    )
    db_session.add(action)
    db_session.commit()
    return action


# Authentication Fixtures
@pytest.fixture
def logged_in_user(client, test_user):
    """Log in a test user and return the client."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def logged_in_admin(client, admin_user):
    """Log in an admin user and return the client."""
    with client.session_transaction() as sess:
        sess['user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client


# Form Data Fixtures
@pytest.fixture
def valid_user_data():
    """Return valid user registration data."""
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpass123',
        'password2': 'newpass123'
    }


@pytest.fixture
def valid_reservation_data(parking_spot):
    """Return valid reservation data."""
    return {
        'name': 'Test Reservation',
        'spot_id': parking_spot.id,
        'reservation_date': (datetime.now().date() + timedelta(days=1)).isoformat()
    }


@pytest.fixture
def valid_carpool_data():
    """Return valid carpool data."""
    return {
        'name': 'Test Carpool',
        'origin': 'Start Location',
        'destination': 'End Location',
        'departure_time': (datetime.now() + timedelta(hours=24)).isoformat(),
        'return_time': (datetime.now() + timedelta(hours=30)).isoformat(),
        'max_passengers': 4,
        'notes': 'Test carpool trip'
    }


# Mock data for testing
@pytest.fixture
def mock_email_service(monkeypatch):
    """Mock email service for testing."""
    emails_sent = []
    
    def mock_send_email(to, subject, body):
        emails_sent.append({
            'to': to,
            'subject': subject,
            'body': body
        })
        return True
    
    monkeypatch.setattr('carpool.services.email_service.send_email', mock_send_email)
    return emails_sent


# Utility functions for tests
def create_test_user(db_session, username='testuser', email='test@example.com', role='user'):
    """Helper function to create a test user."""
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash('testpass123'),
        role=role
    )
    db_session.add(user)
    db_session.commit()
    return user


def create_test_parking_spot(db_session, spot_id='TEST1', location='Test Location', status='available'):
    """Helper function to create a test parking spot."""
    spot = ParkingSpot(
        id=spot_id,
        location=location,
        description='Test parking spot',
        status=status
    )
    db_session.add(spot)
    db_session.commit()
    return spot


def login_user(client, username='testuser', password='testpass123'):
    """Helper function to log in a user."""
    return client.post('/auth/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)


def logout_user(client):
    """Helper function to log out a user."""
    return client.get('/auth/logout', follow_redirects=True)
