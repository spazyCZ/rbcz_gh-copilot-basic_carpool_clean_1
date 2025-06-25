"""
Integration tests for carpool routes.
"""
import pytest
from flask import url_for
from datetime import datetime, timedelta

from carpool.models.carpool import Carpool
from carpool.models.user import User
from carpool.extensions import db

def create_test_carpool(app, user_id=1):
    """Helper function to create a test carpool."""
    with app.app_context():
        departure_time = datetime.now() + timedelta(days=1)
        return_time = departure_time + timedelta(hours=8)
        
        carpool = Carpool(
            name='Test Carpool',
            origin='Test Origin',
            destination='Test Destination',
            departure_time=departure_time,
            return_time=return_time,
            max_passengers=4,
            driver_id=user_id
        )
        db.session.add(carpool)
        db.session.commit()
        return carpool

def test_carpool_index_page(client, app, auth):
    """
    Test the carpools index page.
    """
    # Login as test user
    auth.login()
    
    # Create a test carpool
    create_test_carpool(app)
    
    # Get the carpools index page
    response = client.get(url_for('carpools.index'))
    
    # Check that the page loads successfully
    assert response.status_code == 200
    assert b'Carpools' in response.data
    assert b'Test Carpool' in response.data
    assert b'Test Origin' in response.data
    assert b'Test Destination' in response.data

def test_my_carpools_page(client, app, auth):
    """
    Test the my carpools page.
    """
    # Login as test user
    auth.login()
    
    # Create a test carpool
    create_test_carpool(app)
    
    # Get the my carpools page
    response = client.get(url_for('carpools.my_carpools'))
    
    # Check that the page loads successfully
    assert response.status_code == 200
    assert b'My Carpools' in response.data
    assert b'Test Carpool' in response.data

def test_view_carpool_page(client, app, auth):
    """
    Test viewing a specific carpool.
    """
    # Login as test user
    auth.login()
    
    # Create a test carpool
    carpool = create_test_carpool(app)
    
    # Get the carpool view page
    response = client.get(url_for('carpools.view', id=carpool.id))
    
    # Check that the page loads successfully
    assert response.status_code == 200
    assert b'Test Carpool' in response.data
    assert b'Test Origin' in response.data
    assert b'Test Destination' in response.data
    assert b'Join Carpool' in response.data  # Join button should be visible

def test_create_carpool(client, app, auth):
    """
    Test creating a new carpool.
    """
    # Login as test user
    auth.login()
    
    # Get the new carpool page
    response = client.get(url_for('carpools.new_carpool'))
    assert response.status_code == 200
    assert b'New Carpool' in response.data
    
    # Prepare form data
    tomorrow = datetime.now() + timedelta(days=1)
    return_time = tomorrow + timedelta(hours=8)
    
    # Submit the form
    response = client.post(
        url_for('carpools.new_carpool'),
        data={
            'name': 'New Test Carpool',
            'origin': 'New Origin',
            'destination': 'New Destination',
            'departure_time': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'return_time': return_time.strftime('%Y-%m-%d %H:%M'),
            'max_passengers': 3,
            'notes': 'Test notes'
        },
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'New Test Carpool' in response.data
    assert b'has been created' in response.data
    
    # Verify in database
    with app.app_context():
        carpool = Carpool.query.filter_by(name='New Test Carpool').first()
        assert carpool is not None
        assert carpool.origin == 'New Origin'
        assert carpool.destination == 'New Destination'
        assert carpool.max_passengers == 3
        assert carpool.notes == 'Test notes'

def test_edit_carpool(client, app, auth):
    """
    Test editing a carpool.
    """
    # Login as test user
    auth.login()
    
    # Create a test carpool
    carpool = create_test_carpool(app)
    
    # Get the edit page
    response = client.get(url_for('carpools.edit_carpool', id=carpool.id))
    assert response.status_code == 200
    assert b'Edit Carpool' in response.data
    assert b'Test Carpool' in response.data
    
    # Prepare updated data
    tomorrow = datetime.now() + timedelta(days=1)
    return_time = tomorrow + timedelta(hours=8)
    
    # Submit the form
    response = client.post(
        url_for('carpools.edit_carpool', id=carpool.id),
        data={
            'name': 'Updated Carpool',
            'origin': 'Updated Origin',
            'destination': 'Updated Destination',
            'departure_time': tomorrow.strftime('%Y-%m-%d %H:%M'),
            'return_time': return_time.strftime('%Y-%m-%d %H:%M'),
            'max_passengers': 5,
            'notes': 'Updated notes'
        },
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'Updated Carpool' in response.data
    assert b'has been updated' in response.data
    
    # Verify in database
    with app.app_context():
        updated_carpool = Carpool.query.get(carpool.id)
        assert updated_carpool.name == 'Updated Carpool'
        assert updated_carpool.origin == 'Updated Origin'
        assert updated_carpool.destination == 'Updated Destination'
        assert updated_carpool.max_passengers == 5
        assert updated_carpool.notes == 'Updated notes'

def test_join_leave_carpool(client, app, auth):
    """
    Test joining and leaving a carpool.
    """
    # Login as test user (user_id=1)
    auth.login()
    
    # Create a test carpool with a different driver (user_id=2)
    with app.app_context():
        # Make sure user with ID 2 exists
        user2 = User.query.get(2)
        if not user2:
            user2 = User(
                id=2,
                username='testuser2',
                email='test2@example.com',
                password='password',
                first_name='Test',
                last_name='User2'
            )
            db.session.add(user2)
            db.session.commit()
        
        carpool = create_test_carpool(app, user_id=2)
    
    # Join the carpool
    response = client.post(
        url_for('carpools.join', id=carpool.id),
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'successfully joined the carpool' in response.data
    
    # Verify in database
    with app.app_context():
        updated_carpool = Carpool.query.get(carpool.id)
        user = User.query.get(1)  # Current logged in user
        assert user in updated_carpool.passengers
        assert updated_carpool.current_passengers == 1
    
    # Leave the carpool
    response = client.post(
        url_for('carpools.leave', id=carpool.id),
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'successfully left the carpool' in response.data
    
    # Verify in database
    with app.app_context():
        updated_carpool = Carpool.query.get(carpool.id)
        user = User.query.get(1)  # Current logged in user
        assert user not in updated_carpool.passengers
        assert updated_carpool.current_passengers == 0

def test_cancel_carpool(client, app, auth):
    """
    Test cancelling a carpool.
    """
    # Login as test user
    auth.login()
    
    # Create a test carpool
    carpool = create_test_carpool(app)
    
    # Cancel the carpool
    response = client.post(
        url_for('carpools.cancel', id=carpool.id),
        follow_redirects=True
    )
    
    # Check response
    assert response.status_code == 200
    assert b'has been cancelled' in response.data
    
    # Verify in database
    with app.app_context():
        updated_carpool = Carpool.query.get(carpool.id)
        assert updated_carpool.status == 'cancelled'
