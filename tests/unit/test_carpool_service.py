"""
Tests for carpool service functions.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from carpool.services.carpool_service import (
    get_all_carpools, get_active_carpools, get_carpool,
    create_carpool, update_carpool, delete_carpool,
    join_carpool, leave_carpool, get_user_carpools
)
from carpool.models.carpool import Carpool
from carpool.models.user import User

def test_get_all_carpools(app, monkeypatch):
    """
    Test retrieving all carpools.
    """
    with app.app_context():
        # Create mock carpools
        mock_carpools = [MagicMock(), MagicMock()]
        
        # Mock the query
        mock_query = MagicMock()
        mock_query.all.return_value = mock_carpools
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Call the service function
        result = get_all_carpools()
        
        # Assert the result
        assert result == mock_carpools
        mock_query.all.assert_called_once()

def test_get_all_carpools_error(app, monkeypatch):
    """
    Test error handling when retrieving all carpools.
    """
    with app.app_context():
        # Mock the query to raise an exception
        mock_query = MagicMock()
        mock_query.all.side_effect = SQLAlchemyError("Database error")
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Call the service function
        result = get_all_carpools()
        
        # Assert the result
        assert result == []
        mock_query.all.assert_called_once()

def test_get_active_carpools(app, monkeypatch):
    """
    Test retrieving active carpools.
    """
    with app.app_context():
        # Create mock carpools
        mock_carpools = [MagicMock(), MagicMock()]
        
        # Mock the query
        mock_query = MagicMock()
        mock_filter_by = MagicMock()
        mock_filter_by.all.return_value = mock_carpools
        mock_query.filter_by.return_value = mock_filter_by
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Call the service function
        result = get_active_carpools()
        
        # Assert the result
        assert result == mock_carpools
        mock_query.filter_by.assert_called_once_with(status='active')
        mock_filter_by.all.assert_called_once()

def test_get_carpool(app, monkeypatch):
    """
    Test retrieving a specific carpool.
    """
    with app.app_context():
        # Create mock carpool
        mock_carpool = MagicMock()
        
        # Mock the query
        mock_query = MagicMock()
        mock_query.get.return_value = mock_carpool
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Call the service function
        result = get_carpool(1)
        
        # Assert the result
        assert result == mock_carpool
        mock_query.get.assert_called_once_with(1)

def test_create_carpool(app, monkeypatch):
    """
    Test creating a new carpool.
    """
    with app.app_context():
        # Mock the database session
        mock_db_session = MagicMock()
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Mock datetime
        now = datetime.now()
        future = now + timedelta(days=1)
        
        # Call the service function
        carpool = create_carpool(
            name='Test Carpool',
            origin='Origin',
            destination='Destination',
            departure_time=future,
            driver_id=1,
            max_passengers=4
        )
        
        # Assert the result
        assert carpool is not None
        assert carpool.name == 'Test Carpool'
        assert carpool.origin == 'Origin'
        assert carpool.destination == 'Destination'
        assert carpool.departure_time == future
        assert carpool.driver_id == 1
        assert carpool.max_passengers == 4
        
        # Verify db operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

def test_create_carpool_error(app, monkeypatch):
    """
    Test error handling when creating a carpool.
    """
    with app.app_context():
        # Mock the database session
        mock_db_session = MagicMock()
        mock_db_session.commit.side_effect = SQLAlchemyError("Database error")
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Mock datetime
        now = datetime.now()
        future = now + timedelta(days=1)
        
        # Call the service function
        carpool = create_carpool(
            name='Test Carpool',
            origin='Origin',
            destination='Destination',
            departure_time=future,
            driver_id=1
        )
        
        # Assert the result
        assert carpool is None
        
        # Verify db operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.rollback.assert_called_once()

def test_update_carpool(app, monkeypatch):
    """
    Test updating a carpool.
    """
    with app.app_context():
        # Create a mock carpool
        mock_carpool = MagicMock()
        mock_carpool.current_passengers = 2
        
        # Mock the query
        mock_query = MagicMock()
        mock_query.get.return_value = mock_carpool
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Mock the database session
        mock_db_session = MagicMock()
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Call the service function
        new_name = 'Updated Carpool'
        result = update_carpool(
            carpool_id=1,
            name=new_name,
            max_passengers=4
        )
        
        # Assert the result
        assert result == mock_carpool
        assert mock_carpool.name == new_name
        assert mock_carpool.max_passengers == 4
        
        # Verify db operations
        mock_query.get.assert_called_once_with(1)
        mock_db_session.commit.assert_called_once()

def test_delete_carpool(app, monkeypatch):
    """
    Test deleting a carpool.
    """
    with app.app_context():
        # Create a mock carpool
        mock_carpool = MagicMock()
        
        # Mock the query
        mock_query = MagicMock()
        mock_query.get.return_value = mock_carpool
        
        # Patch the Carpool.query
        monkeypatch.setattr(Carpool, 'query', mock_query)
        
        # Mock the database session
        mock_db_session = MagicMock()
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Call the service function
        result = delete_carpool(1)
        
        # Assert the result
        assert result is True
        
        # Verify db operations
        mock_query.get.assert_called_once_with(1)
        mock_db_session.delete.assert_called_once_with(mock_carpool)
        mock_db_session.commit.assert_called_once()

def test_join_carpool(app, monkeypatch):
    """
    Test joining a carpool.
    """
    with app.app_context():
        # Create mock objects
        mock_carpool = MagicMock()
        mock_carpool.add_passenger.return_value = True
        
        mock_user = MagicMock()
        
        # Mock the queries
        mock_carpool_query = MagicMock()
        mock_carpool_query.get.return_value = mock_carpool
        
        mock_user_query = MagicMock()
        mock_user_query.get.return_value = mock_user
        
        # Patch the queries
        monkeypatch.setattr(Carpool, 'query', mock_carpool_query)
        monkeypatch.setattr(User, 'query', mock_user_query)
        
        # Mock the database session
        mock_db_session = MagicMock()
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Call the service function
        result = join_carpool(1, 2)
        
        # Assert the result
        assert result is True
        
        # Verify operations
        mock_carpool_query.get.assert_called_once_with(1)
        mock_user_query.get.assert_called_once_with(2)
        mock_carpool.add_passenger.assert_called_once_with(mock_user)
        mock_db_session.commit.assert_called_once()

def test_leave_carpool(app, monkeypatch):
    """
    Test leaving a carpool.
    """
    with app.app_context():
        # Create mock objects
        mock_carpool = MagicMock()
        mock_carpool.remove_passenger.return_value = True
        
        mock_user = MagicMock()
        
        # Mock the queries
        mock_carpool_query = MagicMock()
        mock_carpool_query.get.return_value = mock_carpool
        
        mock_user_query = MagicMock()
        mock_user_query.get.return_value = mock_user
        
        # Patch the queries
        monkeypatch.setattr(Carpool, 'query', mock_carpool_query)
        monkeypatch.setattr(User, 'query', mock_user_query)
        
        # Mock the database session
        mock_db_session = MagicMock()
        monkeypatch.setattr('carpool.services.carpool_service.db.session', mock_db_session)
        
        # Call the service function
        result = leave_carpool(1, 2)
        
        # Assert the result
        assert result is True
        
        # Verify operations
        mock_carpool_query.get.assert_called_once_with(1)
        mock_user_query.get.assert_called_once_with(2)
        mock_carpool.remove_passenger.assert_called_once_with(mock_user)
        mock_db_session.commit.assert_called_once()
