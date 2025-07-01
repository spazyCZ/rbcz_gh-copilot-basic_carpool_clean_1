#!/usr/bin/env python3
"""
Test script to verify the carpool application setup is working correctly.

This script performs basic tests to ensure all components are properly configured.
"""

import sys
import traceback
from carpool import create_app
from extensions import db
from carpool.models import User, ParkingSpot, Reservation, Carpool, Action


def test_app_creation():
    """Test that the Flask app can be created successfully."""
    try:
        app = create_app()
        print("✅ Flask app creation: SUCCESS")
        return app
    except Exception as e:
        print(f"❌ Flask app creation: FAILED - {e}")
        traceback.print_exc()
        return None


def test_database_connection(app):
    """Test database connection and basic queries."""
    try:
        with app.app_context():
            # Test basic queries
            user_count = User.query.count()
            spot_count = ParkingSpot.query.count()
            reservation_count = Reservation.query.count()
            carpool_count = Carpool.query.count()
            action_count = Action.query.count()
            
            print(f"✅ Database connection: SUCCESS")
            print(f"   - Users: {user_count}")
            print(f"   - Parking spots: {spot_count}")
            print(f"   - Reservations: {reservation_count}")
            print(f"   - Carpools: {carpool_count}")
            print(f"   - Actions: {action_count}")
            
            return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        traceback.print_exc()
        return False


def test_admin_user(app):
    """Test that the admin user exists and can authenticate."""
    try:
        with app.app_context():
            admin = User.query.filter_by(username='admin').first()
            if admin:
                if admin.check_password('admin123'):
                    print("✅ Admin user authentication: SUCCESS")
                    return True
                else:
                    print("❌ Admin user authentication: FAILED - Wrong password")
                    return False
            else:
                print("❌ Admin user: FAILED - Admin user not found")
                return False
    except Exception as e:
        print(f"❌ Admin user test: FAILED - {e}")
        traceback.print_exc()
        return False


def test_imports():
    """Test that all major modules can be imported."""
    try:
        # Test model imports
        from carpool.models import User, ParkingSpot, Reservation, Carpool, Action
        
        # Test service imports
        from carpool.services import AuthService, ReservationService, CarpoolService, AdminService
        
        # Test form imports
        from carpool.forms import LoginForm, RegisterForm, ReservationForm, CarpoolForm
        
        # Test view imports
        from carpool.views import main, auth, admin, api
        
        print("✅ Module imports: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ Module imports: FAILED - {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚗 Carpool Application Setup Test")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed. Stopping here.")
        sys.exit(1)
    
    # Test app creation
    app = test_app_creation()
    if not app:
        print("\n❌ App creation failed. Stopping here.")
        sys.exit(1)
    
    # Test database
    if not test_database_connection(app):
        print("\n❌ Database tests failed. Stopping here.")
        sys.exit(1)
    
    # Test admin user
    if not test_admin_user(app):
        print("\n❌ Admin user tests failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! The carpool application is ready to use.")
    print("\nTo start the application, run:")
    print("python run.py")


if __name__ == '__main__':
    main()
