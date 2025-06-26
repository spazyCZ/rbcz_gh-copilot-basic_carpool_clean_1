"""
Test factories for generating test data.

This module provides factory classes for creating test objects
with realistic data using the factory-boy library.
"""

import factory
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from carpool.models import db, User, ParkingSpot, Reservation, Carpool, Action


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password_hash = factory.LazyFunction(lambda: generate_password_hash('testpass123'))
    role = 'user'
    created_at = factory.LazyFunction(datetime.utcnow)

    @factory.post_generation
    def set_password(obj, create, extracted, **kwargs):
        """Set a specific password if provided."""
        if extracted:
            obj.password_hash = generate_password_hash(extracted)


class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""
    role = 'administrator'
    username = factory.Sequence(lambda n: f'admin{n}')


class GuestUserFactory(UserFactory):
    """Factory for creating guest User instances."""
    role = 'guest'
    username = factory.Sequence(lambda n: f'guest{n}')


class ParkingSpotFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating ParkingSpot instances."""
    
    class Meta:
        model = ParkingSpot
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    id = factory.Sequence(lambda n: f'A{n}')
    location = factory.Iterator(['Level A', 'Level B', 'Level C', 'Outdoor', 'VIP'])
    description = factory.Faker('sentence', nb_words=4)
    status = factory.Iterator(['available', 'reserved', 'maintenance'])
    created_at = factory.LazyFunction(datetime.utcnow)


class AvailableParkingSpotFactory(ParkingSpotFactory):
    """Factory for creating available ParkingSpot instances."""
    status = 'available'


class ReservedParkingSpotFactory(ParkingSpotFactory):
    """Factory for creating reserved ParkingSpot instances."""
    status = 'reserved'


class MaintenanceParkingSpotFactory(ParkingSpotFactory):
    """Factory for creating maintenance ParkingSpot instances."""
    status = 'maintenance'


class ReservationFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Reservation instances."""
    
    class Meta:
        model = Reservation
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    spot_id = factory.SubFactory(AvailableParkingSpotFactory)
    user_id = factory.SubFactory(UserFactory)
    name = factory.Faker('catch_phrase')
    reservation_date = factory.LazyFunction(
        lambda: (datetime.now() + timedelta(days=factory.Faker('random_int', min=1, max=30).generate())).date()
    )
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class PastReservationFactory(ReservationFactory):
    """Factory for creating past Reservation instances."""
    reservation_date = factory.LazyFunction(
        lambda: (datetime.now() - timedelta(days=factory.Faker('random_int', min=1, max=30).generate())).date()
    )


class TodayReservationFactory(ReservationFactory):
    """Factory for creating today's Reservation instances."""
    reservation_date = factory.LazyFunction(lambda: datetime.now().date())


class CarpoolFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Carpool instances."""
    
    class Meta:
        model = Carpool
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    name = factory.Faker('catch_phrase')
    origin = factory.Faker('city')
    destination = factory.Faker('city')
    departure_time = factory.LazyFunction(
        lambda: datetime.now() + timedelta(
            hours=factory.Faker('random_int', min=1, max=72).generate()
        )
    )
    return_time = factory.LazyAttribute(
        lambda obj: obj.departure_time + timedelta(
            hours=factory.Faker('random_int', min=2, max=12).generate()
        ) if obj.departure_time else None
    )
    max_passengers = factory.Faker('random_int', min=2, max=8)
    current_passengers = factory.LazyAttribute(
        lambda obj: factory.Faker('random_int', min=1, max=obj.max_passengers).generate()
    )
    notes = factory.Faker('text', max_nb_chars=200)
    organizer_id = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class FullCarpoolFactory(CarpoolFactory):
    """Factory for creating full Carpool instances."""
    current_passengers = factory.LazyAttribute(lambda obj: obj.max_passengers)


class AvailableCarpoolFactory(CarpoolFactory):
    """Factory for creating available Carpool instances."""
    current_passengers = factory.LazyAttribute(
        lambda obj: factory.Faker('random_int', min=1, max=obj.max_passengers - 1).generate()
    )


class PastCarpoolFactory(CarpoolFactory):
    """Factory for creating past Carpool instances."""
    departure_time = factory.LazyFunction(
        lambda: datetime.now() - timedelta(
            hours=factory.Faker('random_int', min=1, max=168).generate()
        )
    )
    return_time = factory.LazyAttribute(
        lambda obj: obj.departure_time + timedelta(
            hours=factory.Faker('random_int', min=2, max=12).generate()
        ) if obj.departure_time else None
    )


class ActionFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Action instances."""
    
    class Meta:
        model = Action
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    action_type = factory.Iterator([
        'user_login',
        'user_logout',
        'user_registered',
        'reservation_created',
        'reservation_updated',
        'reservation_cancelled',
        'carpool_created',
        'carpool_updated',
        'carpool_deleted',
        'user_joined_carpool',
        'user_left_carpool',
        'admin_user_created',
        'admin_user_updated',
        'admin_parking_spot_created',
        'admin_parking_spot_updated'
    ])
    username = factory.Faker('user_name')
    timestamp = factory.LazyFunction(
        lambda: datetime.utcnow() - timedelta(
            hours=factory.Faker('random_int', min=0, max=168).generate()
        )
    )
    details = factory.Faker('sentence')


class LoginActionFactory(ActionFactory):
    """Factory for creating login Action instances."""
    action_type = 'user_login'
    details = factory.LazyAttribute(lambda obj: f'User {obj.username} logged in')


class ReservationActionFactory(ActionFactory):
    """Factory for creating reservation Action instances."""
    action_type = 'reservation_created'
    details = factory.LazyAttribute(lambda obj: f'User {obj.username} created a reservation')


class CarpoolActionFactory(ActionFactory):
    """Factory for creating carpool Action instances."""
    action_type = 'carpool_created'
    details = factory.LazyAttribute(lambda obj: f'User {obj.username} created a carpool')


# Batch creation functions
def create_sample_users(count=10, admin_count=2, guest_count=3):
    """Create a batch of sample users."""
    users = []
    
    # Create regular users
    for _ in range(count):
        users.append(UserFactory())
    
    # Create admin users
    for _ in range(admin_count):
        users.append(AdminUserFactory())
    
    # Create guest users
    for _ in range(guest_count):
        users.append(GuestUserFactory())
    
    return users


def create_sample_parking_spots(count=20):
    """Create a batch of sample parking spots."""
    spots = []
    
    # Create spots with different statuses
    available_count = int(count * 0.7)  # 70% available
    reserved_count = int(count * 0.2)   # 20% reserved
    maintenance_count = count - available_count - reserved_count  # Remainder in maintenance
    
    for _ in range(available_count):
        spots.append(AvailableParkingSpotFactory())
    
    for _ in range(reserved_count):
        spots.append(ReservedParkingSpotFactory())
    
    for _ in range(maintenance_count):
        spots.append(MaintenanceParkingSpotFactory())
    
    return spots


def create_sample_reservations(count=30, users=None, spots=None):
    """Create a batch of sample reservations."""
    reservations = []
    
    # Create different types of reservations
    future_count = int(count * 0.6)    # 60% future
    past_count = int(count * 0.3)      # 30% past
    today_count = count - future_count - past_count  # Remainder today
    
    for _ in range(future_count):
        reservation = ReservationFactory()
        if users:
            reservation.user_id = factory.Faker('random_element', elements=users).generate().id
        if spots:
            available_spots = [s for s in spots if s.status == 'available']
            if available_spots:
                reservation.spot_id = factory.Faker('random_element', elements=available_spots).generate().id
        reservations.append(reservation)
    
    for _ in range(past_count):
        reservation = PastReservationFactory()
        if users:
            reservation.user_id = factory.Faker('random_element', elements=users).generate().id
        if spots:
            reservation.spot_id = factory.Faker('random_element', elements=spots).generate().id
        reservations.append(reservation)
    
    for _ in range(today_count):
        reservation = TodayReservationFactory()
        if users:
            reservation.user_id = factory.Faker('random_element', elements=users).generate().id
        if spots:
            available_spots = [s for s in spots if s.status == 'available']
            if available_spots:
                reservation.spot_id = factory.Faker('random_element', elements=available_spots).generate().id
        reservations.append(reservation)
    
    return reservations


def create_sample_carpools(count=15, users=None):
    """Create a batch of sample carpools."""
    carpools = []
    
    # Create different types of carpools
    available_count = int(count * 0.6)  # 60% available
    full_count = int(count * 0.2)       # 20% full
    past_count = count - available_count - full_count  # Remainder past
    
    for _ in range(available_count):
        carpool = AvailableCarpoolFactory()
        if users:
            carpool.organizer_id = factory.Faker('random_element', elements=users).generate().id
        carpools.append(carpool)
    
    for _ in range(full_count):
        carpool = FullCarpoolFactory()
        if users:
            carpool.organizer_id = factory.Faker('random_element', elements=users).generate().id
        carpools.append(carpool)
    
    for _ in range(past_count):
        carpool = PastCarpoolFactory()
        if users:
            carpool.organizer_id = factory.Faker('random_element', elements=users).generate().id
        carpools.append(carpool)
    
    return carpools


def create_sample_actions(count=100, users=None):
    """Create a batch of sample action logs."""
    actions = []
    
    # Create different types of actions
    login_count = int(count * 0.3)        # 30% login actions
    reservation_count = int(count * 0.4)   # 40% reservation actions
    carpool_count = int(count * 0.2)       # 20% carpool actions
    other_count = count - login_count - reservation_count - carpool_count  # Remainder other
    
    for _ in range(login_count):
        action = LoginActionFactory()
        if users:
            user = factory.Faker('random_element', elements=users).generate()
            action.username = user.username
        actions.append(action)
    
    for _ in range(reservation_count):
        action = ReservationActionFactory()
        if users:
            user = factory.Faker('random_element', elements=users).generate()
            action.username = user.username
        actions.append(action)
    
    for _ in range(carpool_count):
        action = CarpoolActionFactory()
        if users:
            user = factory.Faker('random_element', elements=users).generate()
            action.username = user.username
        actions.append(action)
    
    for _ in range(other_count):
        action = ActionFactory()
        if users:
            user = factory.Faker('random_element', elements=users).generate()
            action.username = user.username
        actions.append(action)
    
    return actions


def populate_test_database():
    """Populate the database with comprehensive test data."""
    # Create users
    users = create_sample_users(count=15, admin_count=3, guest_count=5)
    
    # Create parking spots
    spots = create_sample_parking_spots(count=25)
    
    # Create reservations
    reservations = create_sample_reservations(count=40, users=users, spots=spots)
    
    # Create carpools
    carpools = create_sample_carpools(count=20, users=users)
    
    # Create action logs
    actions = create_sample_actions(count=150, users=users)
    
    return {
        'users': users,
        'spots': spots,
        'reservations': reservations,
        'carpools': carpools,
        'actions': actions
    }
