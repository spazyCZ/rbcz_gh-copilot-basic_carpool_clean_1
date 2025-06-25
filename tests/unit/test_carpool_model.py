"""
Tests for carpool-related models and functionality.
"""
import pytest
from datetime import datetime, timedelta
from carpool.models.carpool import Carpool
from carpool.models.user import User

def test_carpool_model_creation(app):
    """
    Test the creation of a Carpool model instance.
    """
    with app.app_context():
        # Create a test user to be the driver
        user = User(
            username='testdriver',
            email='driver@test.com',
            password='password123',
            first_name='Test',
            last_name='Driver'
        )
        
        # Create a carpool
        departure_time = datetime.now() + timedelta(days=1)
        return_time = departure_time + timedelta(hours=8)
        
        carpool = Carpool(
            name='Test Carpool',
            origin='Test Origin',
            destination='Test Destination',
            departure_time=departure_time,
            return_time=return_time,
            max_passengers=4,
            driver=user
        )
        
        assert carpool.name == 'Test Carpool'
        assert carpool.origin == 'Test Origin'
        assert carpool.destination == 'Test Destination'
        assert carpool.departure_time == departure_time
        assert carpool.return_time == return_time
        assert carpool.max_passengers == 4
        assert carpool.current_passengers == 0
        assert carpool.status == 'active'
        assert carpool.driver == user
        assert carpool.is_full() is False
        assert carpool.can_join() is True

def test_carpool_passenger_management(app):
    """
    Test adding and removing passengers from a carpool.
    """
    with app.app_context():
        # Create a test driver
        driver = User(
            username='testdriver',
            email='driver@test.com',
            password='password123',
            first_name='Test',
            last_name='Driver'
        )
        
        # Create passengers
        passengers = []
        for i in range(5):  # Create 5 passengers
            passenger = User(
                username=f'passenger{i}',
                email=f'passenger{i}@test.com',
                password='password123',
                first_name=f'Passenger',
                last_name=f'{i}'
            )
            passengers.append(passenger)
        
        # Create a carpool with 4 max passengers
        departure_time = datetime.now() + timedelta(days=1)
        carpool = Carpool(
            name='Test Carpool',
            origin='Test Origin',
            destination='Test Destination',
            departure_time=departure_time,
            max_passengers=4,
            driver=driver
        )
        
        # Add 4 passengers
        for i in range(4):
            assert carpool.add_passenger(passengers[i]) is True
            assert passengers[i] in carpool.passengers
        
        # Verify state
        assert carpool.current_passengers == 4
        assert carpool.is_full() is True
        assert carpool.can_join() is False
        
        # Try to add a 5th passenger
        assert carpool.add_passenger(passengers[4]) is False
        assert passengers[4] not in carpool.passengers
        assert carpool.current_passengers == 4
        
        # Remove a passenger
        assert carpool.remove_passenger(passengers[0]) is True
        assert passengers[0] not in carpool.passengers
        assert carpool.current_passengers == 3
        assert carpool.is_full() is False
        assert carpool.can_join() is True
        
        # Add the 5th passenger now that there's room
        assert carpool.add_passenger(passengers[4]) is True
        assert passengers[4] in carpool.passengers
        assert carpool.current_passengers == 4

def test_carpool_status_changes(app):
    """
    Test carpool status changes and effects on joining.
    """
    with app.app_context():
        # Create a test user
        user = User(
            username='testdriver',
            email='driver@test.com',
            password='password123',
            first_name='Test',
            last_name='Driver'
        )
        
        passenger = User(
            username='passenger',
            email='passenger@test.com',
            password='password123',
            first_name='Test',
            last_name='Passenger'
        )
        
        # Create a carpool
        departure_time = datetime.now() + timedelta(days=1)
        carpool = Carpool(
            name='Test Carpool',
            origin='Test Origin',
            destination='Test Destination',
            departure_time=departure_time,
            max_passengers=4,
            driver=user
        )
        
        # Verify initial state
        assert carpool.status == 'active'
        assert carpool.can_join() is True
        
        # Change status to cancelled
        carpool.status = 'cancelled'
        assert carpool.can_join() is False
        
        # Try to add a passenger
        assert carpool.add_passenger(passenger) is False
        assert passenger not in carpool.passengers
        
        # Change status back to active
        carpool.status = 'active'
        assert carpool.can_join() is True
        
        # Change departure time to the past
        carpool.departure_time = datetime.now() - timedelta(hours=1)
        assert carpool.can_join() is False
