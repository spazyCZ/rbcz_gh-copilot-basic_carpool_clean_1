"""
Test script to verify Flask routes.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from carpool import create_app

# Create test client
app = create_app('development')
client = app.test_client()

# Test basic routes
with app.app_context():
    # Test home page
    response = client.get('/')
    print(f"Home page status: {response.status_code}")
    
    # Test login page
    response = client.get('/login')
    print(f"Login page status: {response.status_code}")
    
    # Test register page
    response = client.get('/register')
    print(f"Register page status: {response.status_code}")
    
    # Test attempt to access protected page (should redirect to login)
    response = client.get('/dashboard', follow_redirects=False)
    print(f"Dashboard (protected) status: {response.status_code}, redirect: {'Location' in response.headers}")
    
    print("All route tests completed.")
