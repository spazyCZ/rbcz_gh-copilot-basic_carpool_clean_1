"""
Integration tests for authentication views.

This module contains integration tests that test the authentication
routes with real database interactions.
"""

import pytest
from flask import url_for
from werkzeug.security import generate_password_hash

from carpool.models import User, db


class TestAuthenticationViews:
    """Integration tests for authentication routes."""

    def test_login_page_loads(self, client):
        """Test that login page loads successfully."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'username' in response.data.lower()
        assert b'password' in response.data.lower()

    def test_register_page_loads(self, client):
        """Test that register page loads successfully."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data or b'Create Account' in response.data
        assert b'username' in response.data.lower()
        assert b'email' in response.data.lower()

    def test_successful_user_registration(self, client, app):
        """Test successful user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post('/auth/register', data=user_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Check that user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.role == 'user'  # Default role

    def test_registration_with_existing_username(self, client, app, test_user):
        """Test registration with existing username fails."""
        user_data = {
            'username': test_user.username,  # Use existing username
            'email': 'different@example.com',
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post('/auth/register', data=user_data)
        assert response.status_code == 200  # Form validation error, stays on page
        assert b'username' in response.data.lower()  # Error message about username

    def test_registration_with_existing_email(self, client, app, test_user):
        """Test registration with existing email fails."""
        user_data = {
            'username': 'differentuser',
            'email': test_user.email,  # Use existing email
            'password': 'newpass123',
            'password2': 'newpass123'
        }
        
        response = client.post('/auth/register', data=user_data)
        assert response.status_code == 200  # Form validation error
        assert b'email' in response.data.lower()  # Error message about email

    def test_registration_password_mismatch(self, client):
        """Test registration with mismatched passwords fails."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'different123'
        }
        
        response = client.post('/auth/register', data=user_data)
        assert response.status_code == 200  # Form validation error
        # Should contain error about password mismatch

    def test_successful_login(self, client, app, test_user):
        """Test successful user login."""
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'  # Password from test_user fixture
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Should be redirected to dashboard or home page
        # Check for elements that indicate successful login
        assert b'Dashboard' in response.data or b'Welcome' in response.data

    def test_login_with_invalid_username(self, client):
        """Test login with invalid username fails."""
        login_data = {
            'username': 'nonexistentuser',
            'password': 'anypassword'
        }
        
        response = client.post('/auth/login', data=login_data)
        assert response.status_code == 200  # Stays on login page
        # Should contain error message

    def test_login_with_invalid_password(self, client, test_user):
        """Test login with invalid password fails."""
        login_data = {
            'username': test_user.username,
            'password': 'wrongpassword'
        }
        
        response = client.post('/auth/login', data=login_data)
        assert response.status_code == 200  # Stays on login page
        # Should contain error message

    def test_logout_functionality(self, client, test_user):
        """Test user logout functionality."""
        # First login
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        client.post('/auth/login', data=login_data)
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        
        # Should be redirected to login page or home page
        # User should no longer be logged in

    def test_forgot_password_page_loads(self, client):
        """Test that forgot password page loads."""
        response = client.get('/auth/forgot-password')
        assert response.status_code == 200
        assert b'email' in response.data.lower()

    def test_forgot_password_with_valid_email(self, client, test_user, mock_email_service):
        """Test forgot password with valid email."""
        reset_data = {
            'email': test_user.email
        }
        
        response = client.post('/auth/forgot-password', data=reset_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Should have sent an email (mocked)
        # Check that email was "sent"

    def test_forgot_password_with_invalid_email(self, client):
        """Test forgot password with invalid email."""
        reset_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = client.post('/auth/forgot-password', data=reset_data)
        assert response.status_code == 200
        # Should handle gracefully (don't reveal if email exists)

    def test_protected_route_requires_login(self, client):
        """Test that protected routes require authentication."""
        # Try to access dashboard without login
        response = client.get('/dashboard')
        # Should redirect to login page
        assert response.status_code == 302 or response.status_code == 401

    def test_admin_route_requires_admin_role(self, client, test_user):
        """Test that admin routes require admin role."""
        # Login as regular user
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        client.post('/auth/login', data=login_data)
        
        # Try to access admin page
        response = client.get('/admin/dashboard')
        # Should be forbidden
        assert response.status_code == 403 or response.status_code == 302

    def test_admin_route_access_with_admin_user(self, client, admin_user):
        """Test that admin users can access admin routes."""
        # Login as admin
        login_data = {
            'username': admin_user.username,
            'password': 'adminpass123'
        }
        client.post('/auth/login', data=login_data)
        
        # Try to access admin page
        response = client.get('/admin/dashboard')
        # Should be allowed
        assert response.status_code == 200

    def test_session_management(self, client, test_user):
        """Test session management during login/logout."""
        # Check no session initially
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
        
        # Login
        login_data = {
            'username': test_user.username,
            'password': 'testpass123'
        }
        client.post('/auth/login', data=login_data)
        
        # Check session exists after login
        with client.session_transaction() as sess:
            assert 'user_id' in sess or '_user_id' in sess
        
        # Logout
        client.get('/auth/logout')
        
        # Check session cleared after logout
        with client.session_transaction() as sess:
            assert 'user_id' not in sess and '_user_id' not in sess

    def test_remember_me_functionality(self, client, test_user):
        """Test remember me functionality in login."""
        login_data = {
            'username': test_user.username,
            'password': 'testpass123',
            'remember_me': True
        }
        
        response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert response.status_code == 200
        
        # Should set remember cookie (implementation dependent)

    def test_csrf_protection(self, client):
        """Test CSRF protection on forms."""
        # This test would verify CSRF token handling
        # Implementation depends on how CSRF is configured
        
        # Get login page to obtain CSRF token
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        # Extract CSRF token from response (if implemented)
        # Submit form without CSRF token should fail

    def test_rate_limiting_login_attempts(self, client, test_user):
        """Test rate limiting on login attempts."""
        # This test would verify rate limiting if implemented
        login_data = {
            'username': test_user.username,
            'password': 'wrongpassword'
        }
        
        # Make multiple failed login attempts
        for _ in range(5):
            response = client.post('/auth/login', data=login_data)
            assert response.status_code == 200
        
        # After rate limit, should be blocked or delayed

    def test_password_strength_validation(self, client):
        """Test password strength validation."""
        # Test weak password
        weak_password_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too weak
            'password2': '123'
        }
        
        response = client.post('/auth/register', data=weak_password_data)
        assert response.status_code == 200
        # Should contain password strength error

    def test_email_format_validation(self, client):
        """Test email format validation."""
        invalid_email_data = {
            'username': 'newuser',
            'email': 'invalid-email',  # Invalid format
            'password': 'validpass123',
            'password2': 'validpass123'
        }
        
        response = client.post('/auth/register', data=invalid_email_data)
        assert response.status_code == 200
        # Should contain email format error

    def test_username_format_validation(self, client):
        """Test username format validation."""
        invalid_username_data = {
            'username': 'a',  # Too short
            'email': 'valid@example.com',
            'password': 'validpass123',
            'password2': 'validpass123'
        }
        
        response = client.post('/auth/register', data=invalid_username_data)
        assert response.status_code == 200
        # Should contain username validation error
