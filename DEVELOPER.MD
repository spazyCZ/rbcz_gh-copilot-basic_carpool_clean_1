# Developer Documentation

This document provides comprehensive guidelines for developing, maintaining, and contributing to the rbcz_gh-copilot-basic_carpool project.

## Development Environment Setup

### Prerequisites
- Python 3.9+ installed
- Git configured
- Virtual environment tool (venv/virtualenv)
- PostgreSQL (for production) or SQLite (for development)

### Local Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd rbcz_gh-copilot-basic_carpool_clean_1

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create initial admin user (optional)
python scripts/create_admin.py

# Run the application
python run.py
```

### Environment Variables
Create a `.env` file with the following variables:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///carpool.db
MAIL_SERVER=your-mail-server
MAIL_USERNAME=your-mail-username
MAIL_PASSWORD=your-mail-password
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-admin-password
```

## Code Architecture

### Application Structure
```
carpool/
├── __init__.py           # Application factory
├── config.py            # Configuration settings
├── extensions.py        # Flask extensions
├── models/              # SQLAlchemy models
│   ├── __init__.py
│   ├── user.py
│   ├── parking_spot.py
│   ├── reservation.py
│   ├── carpool.py
│   └── action.py
├── views/               # Route handlers (blueprints)
│   ├── __init__.py
│   ├── auth.py
│   ├── main.py
│   ├── admin.py
│   ├── api.py
│   └── carpool.py
├── services/            # Business logic layer
│   ├── __init__.py
│   ├── user_service.py
│   ├── reservation_service.py
│   ├── carpool_service.py
│   └── logging_service.py
├── forms/               # WTF forms
│   ├── __init__.py
│   ├── auth_forms.py
│   ├── reservation_forms.py
│   └── carpool_forms.py
├── templates/           # Jinja2 templates
│   ├── base.html
│   ├── auth/
│   ├── admin/
│   └── carpool/
└── static/              # CSS, JS, images
    ├── css/
    ├── js/
    └── images/
```

### Design Patterns Used
- **Application Factory Pattern**: Flask app creation in `carpool/__init__.py`
- **Blueprint Pattern**: Modular route organization
- **Service Layer Pattern**: Business logic separation in `services/`
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Test data generation

### MVC Architecture
- **Models**: Data structure and business logic using SQLAlchemy
- **Views**: Route handlers in Flask blueprints
- **Templates**: Presentation logic using Jinja2
- **Controllers**: Service layer for business logic

## API Documentation

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout  
- `POST /auth/register` - User registration

### Reservation Endpoints
- `GET /api/reservations` - List all reservations
- `POST /api/reservations` - Create new reservation
- `PUT /api/reservations/<id>` - Update reservation
- `DELETE /api/reservations/<id>` - Delete reservation

### Carpool Endpoints
- `GET /api/carpools` - List all carpool trips
- `POST /api/carpools` - Create new carpool trip
- `PUT /api/carpools/<id>` - Update carpool trip
- `DELETE /api/carpools/<id>` - Delete carpool trip

### Admin Endpoints
- `GET /api/admin/users` - List all users (admin only)
- `POST /api/admin/users` - Create new user (admin only)
- `PUT /api/admin/users/<id>` - Update user (admin only)
- `DELETE /api/admin/users/<id>` - Delete user (admin only)
- `GET /api/admin/stats` - System statistics (admin only)
- `GET /api/admin/logs` - Activity logs (admin only)

### Chart Data Endpoints
- `GET /api/chart/reservations-by-date` - Reservations chart data
- `GET /api/chart/user-activity` - User activity chart data
- `GET /api/chart/parking-utilization` - Parking utilization data

## Database Management

### Migrations
```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Downgrade to previous migration
flask db downgrade

# Show migration history
flask db history

# Show current revision
flask db current
```

### Database Seeding
```bash
# Seed with sample data
python scripts/seed_database.py

# Create test data
python scripts/create_test_data.py

# Create admin user
python scripts/create_admin.py
```

### Backup and Restore
```bash
# Backup SQLite database
cp instance/carpool.db backups/carpool_$(date +%Y%m%d_%H%M%S).db

# Backup PostgreSQL database
pg_dump carpool_db > backups/carpool_$(date +%Y%m%d_%H%M%S).sql

# Restore SQLite database
cp backups/carpool_backup.db instance/carpool.db

# Restore PostgreSQL database
psql carpool_db < backups/carpool_backup.sql
```

## Testing Strategy

### Test Structure
```
tests/
├── conftest.py          # Test configuration and fixtures
├── factories.py         # Test data factories
├── unit/               # Unit tests with mocking
│   ├── test_models.py
│   ├── test_services.py
│   └── test_forms.py
└── integration/        # Integration tests
    ├── test_auth_routes.py
    ├── test_api_endpoints.py
    └── test_admin_routes.py
```

### Test Types
- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: Database and API endpoint testing
- **End-to-End Tests**: Complete workflow testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=carpool --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py

# Run tests with specific marker
pytest -m "unit"

# Run tests in parallel
pytest -n auto

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v
```

### Test Data Management
```python
# Using factories for test data
from tests.factories import UserFactory, ReservationFactory, CarpoolFactory

def test_user_creation():
    """Test user creation with factory."""
    user = UserFactory()
    assert user.username is not None
    assert user.email is not None

def test_reservation_creation():
    """Test reservation creation with dependencies."""
    user = UserFactory()
    reservation = ReservationFactory(user=user)
    assert reservation.user_id == user.id
```

### Test Configuration
- Test database: `test_carpool.db`
- Test environment variables in `tests/.env.test`
- Mock external services in unit tests
- Use separate test configuration in `config.py`

## Security Best Practices

### Input Validation
```python
# Use Flask-WTF for form validation
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length

class ReservationForm(FlaskForm):
    """Form for creating parking reservations."""
    
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    reservation_date = DateField('Date', validators=[DataRequired()])
    spot_id = SelectField('Parking Spot', validators=[DataRequired()])
    
    def validate_reservation_date(self, field):
        """Custom validation for reservation date."""
        if field.data < datetime.date.today():
            raise ValidationError('Reservation date cannot be in the past.')
```

### Authentication and Authorization
```python
# Use Flask-Login for authentication
from flask_login import login_required, current_user
from functools import wraps

def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'administrator':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin users management page."""
    pass
```

### Security Headers
```python
# Use Flask-Talisman for security headers
from flask_talisman import Talisman

def configure_security(app):
    """Configure security headers."""
    Talisman(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': "'self' 'unsafe-inline'",
            'style-src': "'self' 'unsafe-inline'",
            'img-src': "'self' data:",
        },
        force_https=app.config.get('FORCE_HTTPS', False),
        session_cookie_secure=True,
        session_cookie_http_only=True
    )
```

## Frontend Development

### Chart.js Integration
```javascript
// static/js/charts.js
/**
 * Initialize dashboard charts
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeReservationChart();
    initializeUserActivityChart();
});

/**
 * Initialize reservation trends chart
 */
function initializeReservationChart() {
    const ctx = document.getElementById('reservationChart').getContext('2d');
    
    fetch('/api/chart/reservations-by-date')
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Reservation Trends'
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
        });
}
```

### AJAX Requests
```javascript
// static/js/reservations.js
/**
 * Handle reservation form submission via AJAX
 * @param {Event} event - Form submission event
 */
function handleReservationSubmission(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    fetch('/api/reservations', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrf_token]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Reservation created successfully', 'success');
            location.reload();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
    });
}
```

## Logging and Monitoring

### Logging Configuration
```python
# carpool/logging_config.py
import logging
import logging.handlers
import os
from flask import Flask

def configure_logging(app: Flask) -> None:
    """Configure application logging."""
    
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/carpool.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Carpool application startup')
```

### Usage in Routes
```python
# carpool/views/reservations.py
import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

@reservations_bp.route('/api/reservations', methods=['POST'])
@login_required
def create_reservation():
    """Create a new parking reservation."""
    
    logger.info(f"Creating reservation for user {current_user.username}")
    
    try:
        # Business logic here
        reservation = reservation_service.create_reservation(form_data)
        logger.info(f"Reservation {reservation.id} created successfully")
        return jsonify({'success': True, 'reservation_id': reservation.id})
        
    except ValidationError as e:
        logger.warning(f"Validation error in reservation creation: {e}")
        return jsonify({'success': False, 'message': str(e)}), 400
        
    except Exception as e:
        logger.error(f"Unexpected error in reservation creation: {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Internal server error'}), 500
```

## Deployment

### Production Deployment
```bash
# Set production environment
export FLASK_ENV=production

# Install production dependencies
pip install -r requirements.txt

# Set secure configuration
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
export DATABASE_URL=postgresql://user:pass@localhost/carpool_prod

# Run database migrations
flask db upgrade

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 "carpool:create_app()"
```

### Docker Deployment
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "carpool:create_app()"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://carpool:password@db:5432/carpool
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: carpool
      POSTGRES_USER: carpool
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Environment-Specific Configurations
- **Development**: SQLite, debug mode enabled, detailed logging
- **Testing**: In-memory SQLite, test data, mock external services
- **Production**: PostgreSQL, security headers, structured logging, monitoring

## Contributing Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Write comprehensive docstrings
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable and function names

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Pull Request Process
1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass (`pytest`)
4. Update documentation if needed
5. Run pre-commit hooks
6. Submit pull request with clear description

### Commit Message Format
```
feat: add user profile management
fix: resolve reservation double-booking issue
docs: update API documentation
test: add integration tests for carpool service
refactor: improve reservation service structure
style: format code with black
```

## Troubleshooting

### Common Issues

#### Database Migration Errors
```bash
# Reset migrations (development only)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Fix migration conflicts
flask db stamp head
flask db migrate -m "Fix migration conflict"
flask db upgrade
```

#### Permission Errors
- Check file permissions on database file
- Ensure Flask user has write access to instance folder
- Verify virtual environment activation

#### Import Errors
- Verify virtual environment is activated
- Check PYTHONPATH includes project root
- Ensure all dependencies are installed
- Check for circular imports

#### Template Not Found
- Verify template path in `render_template()`
- Check template directory structure
- Ensure Jinja2 loader configuration is correct

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Flask debug mode
export FLASK_DEBUG=1
flask run
```

### Performance Monitoring
- Use Flask-DebugToolbar for development
- Monitor database query performance with SQLAlchemy logging
- Check static file serving efficiency
- Profile slow endpoints with Flask-Profiler

### Database Debugging
```python
# Enable SQLAlchemy query logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Print all queries in development
app.config['SQLALCHEMY_ECHO'] = True
```

## Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)

### Development Tools
- **VS Code Extensions**: Python, Flask, SQLAlchemy
- **Database Tools**: pgAdmin, SQLite Browser
- **Testing Tools**: pytest, coverage.py
- **Code Quality**: black, flake8, mypy, pre-commit

### Project-Specific Resources
- Project wiki (if available)
- Issue tracker
- Code review guidelines
- Deployment documentation