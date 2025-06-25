"""
Unit tests for user service.
"""
import pytest
from carpool.services.user_service import (
    get_all_users, get_user, get_user_by_email,
    create_user, update_user, delete_user
)
from tests.factories import UserFactory

class TestUserService:
    """
    Tests for the user_service module.
    """
    
    def test_create_user(self, app, db):
        """
        Test creating a new user.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create a new user
            user = create_user(
                username='testuser',
                email='test@example.com',
                password='password123',
                role='user'
            )
            
            # Verify user was created correctly
            assert user is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.role == 'user'
            assert user.verify_password('password123')
    
    def test_get_user(self, app, db):
        """
        Test retrieving a user by username.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create a test user
            user = UserFactory(username='getuser')
            db.session.commit()
            
            # Test retrieving the user
            retrieved_user = get_user('getuser')
            assert retrieved_user is not None
            assert retrieved_user.username == 'getuser'
            
            # Test retrieving non-existent user
            non_existent = get_user('nonexistent')
            assert non_existent is None
    
    def test_get_user_by_email(self, app, db):
        """
        Test retrieving a user by email.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create a test user
            user = UserFactory(username='emailuser', email='email@example.com')
            db.session.commit()
            
            # Test retrieving the user
            retrieved_user = get_user_by_email('email@example.com')
            assert retrieved_user is not None
            assert retrieved_user.username == 'emailuser'
            
            # Test retrieving non-existent user
            non_existent = get_user_by_email('nonexistent@example.com')
            assert non_existent is None
    
    def test_get_all_users(self, app, db):
        """
        Test retrieving all users.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create test users
            UserFactory.create_batch(5)
            db.session.commit()
            
            # Test retrieving all users
            users = get_all_users()
            assert len(users) >= 5
    
    def test_update_user(self, app, db):
        """
        Test updating a user.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create a test user
            user = UserFactory(username='updateuser', email='update@example.com')
            db.session.commit()
            
            # Update the user
            updated_user = update_user(
                username='updateuser',
                email='updated@example.com',
                role='administrator'
            )
            
            # Verify the update
            assert updated_user is not None
            assert updated_user.email == 'updated@example.com'
            assert updated_user.role == 'administrator'
            
            # Test updating non-existent user
            non_existent = update_user(username='nonexistent')
            assert non_existent is None
    
    def test_delete_user(self, app, db):
        """
        Test deleting a user.
        
        :param app: Flask application
        :param db: Database session
        """
        with app.app_context():
            # Create a test user
            user = UserFactory(username='deleteuser')
            db.session.commit()
            
            # Delete the user
            result = delete_user('deleteuser')
            assert result is True
            
            # Verify the user was deleted
            deleted_user = get_user('deleteuser')
            assert deleted_user is None
            
            # Test deleting non-existent user
            result = delete_user('nonexistent')
            assert result is False
