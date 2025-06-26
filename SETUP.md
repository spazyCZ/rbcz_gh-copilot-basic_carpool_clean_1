# Carpool Application Setup Guide

This guide will help you set up and run the Carpool Flask application.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (for version control)

## Installation Steps

### 1. Clone or Navigate to the Project Directory

```bash
cd /data/projects/code_workspace/rbcz_gh-copilot-basic_carpool_clean_2/rbcz_gh-copilot-basic_carpool_clean_1
```

### 2. Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

The `.env` file is already created with default values. Review and modify if needed:

```bash
# View current configuration
cat .env

# Edit if necessary
nano .env  # or your preferred editor
```

### 5. Quick Setup (Recommended)

Use the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
- Create and activate a virtual environment
- Install all required dependencies
- Initialize the database with Flask-Migrate
- Create sample data (admin user and parking spots)
- Test the application setup

### 6. Manual Database Setup (Alternative)

If you prefer to set up manually:

```bash
# Set Flask app
export FLASK_APP=run.py

# Initialize migration repository
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade

# Run setup test
python test_setup.py
```

### 7. Verify Setup

You can run the test script to verify everything is working:

```bash
python test_setup.py
```

### 8. Run the Application

```bash
# Start the development server
python run.py
```

The application will be available at: http://localhost:5000

## Default Login Credentials

- **Administrator:**
  - Username: `admin`
  - Password: `admin123`

- **Test User:**
  - Username: `testuser`
  - Password: `test123`

## Application Features

### For Regular Users:
- Dashboard with personal statistics
- Make parking reservations
- View and manage reservations
- Create and join carpools
- Profile management

### For Administrators:
- Admin dashboard with system analytics
- User management (create, edit, delete users)
- Parking spot management
- Activity logs and monitoring
- System statistics and charts

## Key URLs

- **Home/Dashboard:** http://localhost:5000/
- **Login:** http://localhost:5000/auth/login
- **Register:** http://localhost:5000/auth/register
- **Reservations:** http://localhost:5000/reservations
- **Carpools:** http://localhost:5000/carpools
- **Admin Panel:** http://localhost:5000/admin (admin users only)

## Directory Structure

```
carpool/
├── __init__.py              # Application factory
├── config.py               # Configuration settings
├── extensions.py           # Flask extensions setup
├── database.py             # Database utilities and migration helpers
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── parking_spot.py
│   ├── reservation.py
│   ├── carpool.py
│   └── action.py
├── services/               # Business logic layer
│   ├── auth_service.py
│   ├── reservation_service.py
│   ├── carpool_service.py
│   └── admin_service.py
├── forms/                  # WTF forms
│   ├── auth_forms.py
│   ├── reservation_forms.py
│   ├── carpool_forms.py
│   └── admin_forms.py
├── views/                  # Route handlers (blueprints)
│   ├── main.py            # Main application routes
│   ├── auth.py            # Authentication routes
│   ├── admin.py           # Admin panel routes
│   └── api.py             # JSON API endpoints
├── templates/              # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── auth/              # Authentication templates
│   ├── reservations/      # Reservation templates
│   ├── carpools/          # Carpool templates
│   ├── admin/             # Admin panel templates
│   └── errors/            # Error page templates
└── static/                # CSS, JS, images
    ├── css/
    │   └── main.css
    └── js/
        ├── main.js
        ├── charts.js
        └── dashboard.js
```

## CLI Commands

The application provides several Flask CLI commands for management:

```bash
# Database management
flask init-migrations      # Initialize migration repository
flask create-migration     # Create a new migration
flask apply-migrations     # Apply pending migrations
flask rollback-migration   # Rollback last migration
flask migration-status     # Check migration status
flask setup-initial        # Set up initial data
flask reset-db             # Reset database (WARNING: deletes all data)

# User management
flask create-admin          # Create a new admin user
```

## Development

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-flask factory-boy

# Run all tests
pytest

# Run with coverage
pytest --cov=carpool

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

### Code Quality

```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black carpool/
isort carpool/

# Check code quality
flake8 carpool/
```

## Production Deployment

For production deployment, consider:

1. **Environment Variables:**
   - Set `FLASK_ENV=production`
   - Use a strong `SECRET_KEY`
   - Configure a production database (PostgreSQL recommended)

2. **WSGI Server:**
   - Use Gunicorn or uWSGI instead of the development server
   - Example: `gunicorn -w 4 -b 0.0.0.0:8000 run:app`

3. **Database:**
   - Use PostgreSQL for production
   - Update `DATABASE_URL` in `.env`

4. **Security:**
   - Use HTTPS in production
   - Set up proper firewall rules
   - Enable security headers

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure virtual environment is activated
   - Check that all dependencies are installed: `pip install -r requirements.txt`

2. **Database Errors:**
   - Initialize migrations: `flask init-migrations`
   - Apply migrations: `flask apply-migrations`

3. **Port Already in Use:**
   - Change the port in `.env`: `FLASK_PORT=5001`
   - Or kill the process using the port

4. **Template Not Found:**
   - Ensure all template files are in place
   - Check that the application structure matches the guide

### Logs

Application logs are written to:
- Console output (when running in debug mode)
- `carpool.log` file in the project root

### Getting Help

If you encounter issues:
1. Check the application logs
2. Verify all dependencies are installed
3. Ensure the database is properly initialized
4. Check that all environment variables are set correctly

## Features Overview

### Technology Stack
- **Backend:** Flask 2.3+ with Python 3.9+
- **Database:** SQLite (development) / PostgreSQL (production)
- **Frontend:** Bootstrap 5, Chart.js, jQuery
- **Authentication:** Flask-Login with bcrypt password hashing
- **Forms:** Flask-WTF with CSRF protection
- **Migrations:** Flask-Migrate (Alembic)
- **Testing:** pytest with factory-boy

### Security Features
- Password hashing with Werkzeug
- CSRF protection on all forms
- Session-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention through ORM

### Performance Features
- Database indexing on critical fields
- Efficient queries with SQLAlchemy
- AJAX for dynamic content loading
- Responsive design for mobile devices

## Next Steps

After setup:
1. Login with admin credentials
2. Create additional parking spots in the admin panel
3. Register test users
4. Test the reservation and carpool functionality
5. Explore the admin dashboard and analytics

Enjoy using the Carpool application!
