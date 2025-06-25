"""
Simple test script to verify the Flask application setup.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from carpool import create_app
from carpool.extensions import db
from carpool.models.user import User

# Create app and setup test context
app = create_app('development')
with app.app_context():
    # Try to create all tables
    db.create_all()
    
    # Try to add a test user
    try:
        test_user = User(
            username='testadmin',
            email='admin@example.com',
            password='password123',
            role='administrator'
        )
        
        # Check if user exists
        existing_user = User.query.get('testadmin')
        if not existing_user:
            db.session.add(test_user)
            db.session.commit()
            print("Test user created successfully.")
        else:
            print("Test user already exists.")
        
        # Verify user can be retrieved
        user = User.query.get('testadmin')
        if user:
            print(f"User found: {user.username}, role: {user.role}")
        else:
            print("User not found!")
            
    except Exception as e:
        print(f"Error creating test user: {e}")
        db.session.rollback()

print("Test completed.")
