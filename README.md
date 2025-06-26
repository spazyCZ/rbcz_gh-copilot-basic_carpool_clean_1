# rbcz_gh-copilot-basic_carpool
Flask GUI application for carpool parking reservations

## Context:
Modern web application for managing carpool parking reservations using Flask and SQLite. The application provides a comprehensive system for users to manage parking spots, make reservations, and administrators to oversee the entire system with detailed logging and analytics.

## Key Features:

### Core Functionality
- **Database Integration**: All data stored in SQLite with comprehensive models
- **User Authentication**: Secure login/logout with Flask-Login
- **Role-Based Access Control**: Administrator, user, and guest roles
- **Parking Spot Management**: Create, update, and delete parking spots
- **Reservation System**: Make, edit, and cancel reservations
- **Double-Booking Prevention**: Automatic validation to prevent conflicts
- **User Profile Management**: View and manage user account information

### Advanced Features
- **Admin Dashboard**: Comprehensive administrative interface with:
  - User management (create, edit, delete, role assignment)
  - System activity monitoring with Chart.js visualizations
  - Detailed logging system with filterable activity logs
  - Quick statistics overview
- **Carpool Management**: Full CRUD operations for carpool trips
- **Responsive Design**: Bootstrap 5 UI with modern styling
- **Real-time Data**: AJAX-powered dynamic content loading
- **Form Validation**: Flask-WTF forms with CSRF protection
- **Security Features**: Password hashing, session management, input validation

### User Interface
- **Dashboard**: Activity overview with statistics and charts
- **Profile Management**: User account details and reservation history
- **Admin Tools**: Complete administrative control panel
- **Logging System**: Comprehensive audit trail with filtering capabilities
- **Modern UI**: Clean, responsive design with FontAwesome icons

# Database Schema

The application uses SQLite with the following enhanced schema:

```mermaid
erDiagram
    User {
        int id PK
        string username "Unique username"
        string email "User email address"
        string password_hash "Hashed password"
        string role "administrator, user, guest"
        datetime created_at "Account creation timestamp"
    }
    
    ParkingSpot {
        string id PK "e.g., A1, B2"
        string status "available, reserved, maintenance"
        string location "e.g., Level A, Outdoor"
        string description "Optional spot description"
        datetime created_at "Spot creation timestamp"
    }
    
    Reservation {
        int id PK
        string spot_id FK "References ParkingSpot.id"
        int user_id FK "References User.id"
        string name "Name for reservation"
        date reservation_date "Date of reservation"
        datetime created_at "Reservation creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    Carpool {
        int id PK
        string name "Carpool trip name"
        string origin "Starting location"
        string destination "End location"
        datetime departure_time "When the trip starts"
        datetime return_time "When the trip returns"
        int max_passengers "Maximum number of passengers"
        int current_passengers "Current passenger count"
        string notes "Additional trip information"
        int organizer_id FK "References User.id"
        datetime created_at "Trip creation timestamp"
        datetime updated_at "Last update timestamp"
    }
    
    Action {
        int id PK
        string action_type "Type of action performed"
        string username "User who performed action"
        datetime timestamp "When action occurred"
        string details "Additional action details"
    }
    
    User ||--o{ Reservation : "makes"
    User ||--o{ Carpool : "organizes"
    User ||--o{ Action : "performs"
    ParkingSpot ||--o{ Reservation : "reserved_as"
```

## Main Entities:

- **User**: User accounts with authentication and role-based permissions
- **ParkingSpot**: Physical parking locations with status tracking
- **Reservation**: Parking reservations linking users to spots
- **Carpool**: Carpool trip organization with passenger management
- **Action**: System audit log for tracking all user activities

## Technical Stack:

- **Backend**: Flask 2.3+ with Python 3.9+
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, Chart.js, jQuery 3.x
- **Authentication**: Flask-Login with password hashing
- **Forms**: Flask-WTF with CSRF protection
- **Testing**: pytest with factory-boy for test data
- **Security**: Flask-Talisman for security headers

## Project Structure:

```
carpool/
├── __init__.py           # Application factory
├── config.py            # Configuration settings
├── extensions.py        # Flask extensions
├── models/              # SQLAlchemy models
├── views/               # Route handlers (blueprints)
├── services/            # Business logic layer
├── forms/               # WTF forms
├── templates/           # Jinja2 templates
├── static/              # CSS, JS, images
tests/
├── unit/                # Unit tests with mocking
├── integration/         # Integration tests
├── conftest.py          # Test configuration
└── factories.py         # Test data factories
```

## Installation & Setup:

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`
3. Initialize database: `flask db upgrade`
4. Run application: `python run.py`
5. Access at `http://localhost:5000`

## Testing:

- Run all tests: `pytest`
- Run with coverage: `pytest --cov=carpool`
- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`


