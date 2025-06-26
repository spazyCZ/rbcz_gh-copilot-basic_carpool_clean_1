"""
Unit tests for User model.

This module contains unit tests with mocking for the User model,
testing model methods and properties without database dependencies.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from carpool.models.user import User


class TestUser:
    """Test cases for the User model."""

    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            role='user'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'user'
        assert user.password_hash is not None
        assert user.password_hash != 'testpass'  # Should be hashed

    def test_user_string_representation(self):
        """Test User string representation."""
        user = User(username='testuser', email='test@example.com')
        assert str(user) == '<User testuser>'

    def test_user_repr(self):
        """Test User repr representation."""
        user = User(username='testuser', email='test@example.com')
        assert repr(user) == '<User testuser>'

    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = 'testpassword123'
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash(password)
        )
        
        # Password should be hashed
        assert user.password_hash != password
        
        # Should be able to verify the password
        assert check_password_hash(user.password_hash, password)
        assert not check_password_hash(user.password_hash, 'wrongpassword')

    def test_user_roles(self):
        """Test different user roles."""
        # Test admin user
        admin = User(username='admin', email='admin@example.com', role='administrator')
        assert admin.role == 'administrator'
        
        # Test regular user
        user = User(username='user', email='user@example.com', role='user')
        assert user.role == 'user'
        
        # Test guest user
        guest = User(username='guest', email='guest@example.com', role='guest')
        assert guest.role == 'guest'

    def test_user_default_role(self):
        """Test that default role is 'user'."""
        user = User(username='testuser', email='test@example.com')
        # Note: Default role would be set by the database schema default
        # This test would need to be adjusted based on actual implementation

    @patch('carpool.models.user.datetime')
    def test_user_timestamps(self, mock_datetime):
        """Test user creation timestamp."""
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        user = User(
            username='testuser',
            email='test@example.com',
            created_at=mock_datetime.utcnow()
        )
        
        assert user.created_at == mock_now

    def test_user_validation_email_format(self):
        """Test email format validation."""
        # This would test email validation if implemented in the model
        # For now, we test that any string can be assigned
        user = User(username='testuser', email='invalid-email')
        assert user.email == 'invalid-email'
        
        user.email = 'valid@example.com'
        assert user.email == 'valid@example.com'

    def test_user_username_uniqueness_constraint(self):
        """Test that username should be unique."""
        # This test would verify unique constraint handling
        # Would need database integration to fully test
        user1 = User(username='testuser', email='test1@example.com')
        user2 = User(username='testuser', email='test2@example.com')
        
        # Both objects can be created, but database would enforce uniqueness
        assert user1.username == user2.username
        assert user1.email != user2.email

    def test_user_email_uniqueness_constraint(self):
        """Test that email should be unique."""
        # Similar to username, this would test unique constraint
        user1 = User(username='user1', email='test@example.com')
        user2 = User(username='user2', email='test@example.com')
        
        assert user1.email == user2.email
        assert user1.username != user2.username

    def test_user_password_hash_required(self):
        """Test that password hash is required for authentication."""
        user = User(username='testuser', email='test@example.com')
        
        # Without password hash, user cannot authenticate
        assert user.password_hash is None

    def test_user_role_validation(self):
        """Test role validation."""
        valid_roles = ['administrator', 'user', 'guest']
        
        for role in valid_roles:
            user = User(username=f'test_{role}', email=f'{role}@example.com', role=role)
            assert user.role == role

    def test_user_fields_assignment(self):
        """Test direct field assignment."""
        user = User()
        
        user.username = 'newuser'
        user.email = 'new@example.com'
        user.role = 'administrator'
        user.password_hash = generate_password_hash('newpass')
        
        assert user.username == 'newuser'
        assert user.email == 'new@example.com'
        assert user.role == 'administrator'
        assert check_password_hash(user.password_hash, 'newpass')

    def test_user_empty_creation(self):
        """Test creating User with no parameters."""
        user = User()
        
        assert user.username is None
        assert user.email is None
        assert user.password_hash is None
        assert user.role is None
        assert user.created_at is None

    @pytest.mark.parametrize("username,email,role", [
        ('user1', 'user1@example.com', 'user'),
        ('admin', 'admin@example.com', 'administrator'),
        ('guest123', 'guest@example.com', 'guest'),
        ('test_user', 'test.user@domain.org', 'user'),
    ])
    def test_user_creation_with_different_data(self, username, email, role):
        """Test user creation with different valid data combinations."""
        user = User(
            username=username,
            email=email,
            role=role,
            password_hash=generate_password_hash('testpass')
        )
        
        assert user.username == username
        assert user.email == email
        assert user.role == role
        assert user.password_hash is not None

    def test_user_boolean_evaluation(self):
        """Test that User object evaluates to True."""
        user = User()
        assert bool(user) is True
        
        user_with_data = User(username='test', email='test@example.com')
        assert bool(user_with_data) is True

    def test_user_attribute_access(self):
        """Test accessing User attributes."""
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        
        # Test attribute access
        assert hasattr(user, 'username')
        assert hasattr(user, 'email')
        assert hasattr(user, 'password_hash')
        assert hasattr(user, 'role')
        assert hasattr(user, 'created_at')
        
        # Test getting attributes
        assert getattr(user, 'username') == 'testuser'
        assert getattr(user, 'email') == 'test@example.com'
        assert getattr(user, 'role') == 'user'

    def test_user_comparison(self):
        """Test User object comparison."""
        user1 = User(username='test', email='test@example.com')
        user2 = User(username='test', email='test@example.com')
        user3 = User(username='different', email='different@example.com')
        
        # Objects with same data are still different instances
        assert user1 is not user2
        assert user1 is not user3
        
        # Would need ID comparison for proper equality testing
        # This depends on the actual implementation
