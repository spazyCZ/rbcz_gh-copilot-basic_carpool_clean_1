#!/bin/bash

# Carpool Application Quick Setup Script
# This script automates the setup process for the carpool application

set -e  # Exit on any error

echo "🚗 Carpool Application Setup Script"
echo "=================================="

# Check Python version
echo "Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found"
    exit 1
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please ensure the .env file exists."
    exit 1
fi

# Initialize database
echo "🗄️ Setting up database..."

# Check if migrations directory exists
if [ ! -d "migrations" ]; then
    echo "Initializing migration repository..."
    export FLASK_APP=run.py
    flask db init
fi

# Create and apply migrations
echo "Creating initial migration..."
export FLASK_APP=run.py
flask db migrate -m "Initial migration" || echo "Migration already exists or no changes detected"

echo "Applying migrations..."
flask db upgrade

echo "Setting up initial data..."
python -c "
import sys
sys.path.insert(0, '.')
from carpool import create_app
from extensions import db
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Check if admin user exists
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        print('Created admin user')

    # Create sample parking spots if they don't exist
    if ParkingSpot.query.count() == 0:
        for i in range(1, 21):
            spot = ParkingSpot(
                id=f'A{i:02d}',
                location='Building A'
            )
            db.session.add(spot)
        print('Created sample parking spots')

    db.session.commit()
    print('Initial data setup completed')
"

# Test the application
echo "🧪 Testing application..."
python -c "
import sys
sys.path.insert(0, '.')
from carpool import create_app
app = create_app()
with app.app_context():
    from carpool.models import User, ParkingSpot
    user_count = User.query.count()
    spot_count = ParkingSpot.query.count()
    print(f'✅ Database test successful: {user_count} users, {spot_count} parking spots')
"

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo ""
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "The application will be available at: http://localhost:5000"
echo ""
echo "For more information, see SETUP.md"
