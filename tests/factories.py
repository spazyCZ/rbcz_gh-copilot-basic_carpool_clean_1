"""
Factory classes for generating test data.
"""
import factory
from datetime import date, datetime, timedelta
from factory.alchemy import SQLAlchemyModelFactory

from carpool.extensions import db
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from carpool.models.reservation import Reservation
from carpool.models.action import Action
from carpool.models.carpool import Carpool

class UserFactory(SQLAlchemyModelFactory):
    """
    Factory for creating User instances.
    """
    class Meta:
        model = User
        sqlalchemy_session = db.session
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    password = factory.PostGenerationMethodCall('password', 'password123')
    role = 'user'
    created_at = factory.LazyFunction(datetime.utcnow)

class AdminFactory(UserFactory):
    """
    Factory for creating admin User instances.
    """
    role = 'administrator'

class ParkingSpotFactory(SQLAlchemyModelFactory):
    """
    Factory for creating ParkingSpot instances.
    """
    class Meta:
        model = ParkingSpot
        sqlalchemy_session = db.session
    
    id = factory.Sequence(lambda n: f'A{n}')
    status = 'free'
    location = factory.Sequence(lambda n: f'Level {n//10 + 1}')

class ReservationFactory(SQLAlchemyModelFactory):
    """
    Factory for creating Reservation instances.
    """
    class Meta:
        model = Reservation
        sqlalchemy_session = db.session
    
    spot_id = factory.SubFactory(ParkingSpotFactory, status='free')
    username = factory.SubFactory(UserFactory)
    reservation_date = factory.LazyFunction(lambda: date.today() + timedelta(days=1))
    created_at = factory.LazyFunction(datetime.utcnow)

class ActionFactory(SQLAlchemyModelFactory):
    """
    Factory for creating Action instances.
    """
    class Meta:
        model = Action
        sqlalchemy_session = db.session
    
    action_type = factory.Sequence(lambda n: f'action_type_{n}')
    username = factory.SubFactory(UserFactory)
    timestamp = factory.LazyFunction(datetime.utcnow)

class CarpoolFactory(SQLAlchemyModelFactory):
    """
    Factory for creating Carpool instances.
    """
    class Meta:
        model = Carpool
        sqlalchemy_session = db.session
    
    name = factory.Sequence(lambda n: f'Carpool {n}')
    origin = factory.Sequence(lambda n: f'Origin {n}')
    destination = factory.Sequence(lambda n: f'Destination {n}')
    departure_time = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(days=1))
    return_time = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(days=1, hours=8))
    max_passengers = 4
    current_passengers = 0
    status = 'active'
    driver = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)
