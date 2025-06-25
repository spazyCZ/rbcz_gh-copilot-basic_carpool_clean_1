"""
Integration tests for the authentication routes.
"""
import pytest
from flask import session, url_for
from carpool.models.user import User
from carpool.services.user_service import create_user

def test_login_page(client):
    """
    Test that the login page loads correctly.
    
    :param client: Flask test client
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Log In' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data

def test_valid_login_logout(client, app):
    """
    Test login and logout with valid credentials.
    
    :param client: Flask test client
    :param app: Flask application
    """
    with app.app_context():
        create_user('testuser', 'test@example.com', 'password123')
    
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123',
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome back, testuser!' in response.data
    
    # Test that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('_user_id') == 'testuser'
    
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    # Test that the user is logged out
    with client.session_transaction() as sess:
        assert sess.get('_user_id') is None

def test_invalid_login(client, app):
    """
    Test login with invalid credentials.
    
    :param client: Flask test client
    :param app: Flask application
    """
    with app.app_context():
        create_user('testuser', 'test@example.com', 'password123')
    
    # Test login with wrong password
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # Test login with non-existent user
    response = client.post('/login', data={
        'username': 'nonexistentuser',
        'password': 'password123',
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_register_page(client):
    """
    Test that the registration page loads correctly.
    
    :param client: Flask test client
    """
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'Username' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data
    assert b'Confirm Password' in response.data

def test_successful_registration(client, app):
    """
    Test successful user registration.
    
    :param client: Flask test client
    :param app: Flask application
    """
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your account has been created!' in response.data
    
    # Verify user was created
    with app.app_context():
        user = User.query.get('newuser')
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.verify_password('password123')

def test_duplicate_registration(client, app):
    """
    Test registration with duplicate username or email.
    
    :param client: Flask test client
    :param app: Flask application
    """
    with app.app_context():
        create_user('existinguser', 'existing@example.com', 'password123')
    
    # Try to register with existing username
    response = client.post('/register', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Username already registered' in response.data
    
    # Try to register with existing email
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'existing@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data
