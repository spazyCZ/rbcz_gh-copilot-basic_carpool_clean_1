#!/usr/bin/env python3
"""
Main entry point for the Carpool Flask application.

This script initializes the Flask application and starts the development server.
"""

import os
import logging
from carpool import create_app
from extensions import db
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot
from werkzeug.security import generate_password_hash
from flask.cli import with_appcontext

# Create Flask application instance
app = create_app()

# Initialize Flask-Migrate
from flask_migrate import Migrate
migrate = Migrate(app, db)

# Configure logging
def configure_logging() -> None:
    """Configure logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_format = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler('carpool.log'),
            logging.StreamHandler()
        ]
    )
    
    app.logger.info('Carpool application logging configured')

# Initialize database and create sample data
def init_database() -> None:
    """Initialize database with sample data if it doesn't exist."""
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            app.logger.info('Database tables created successfully')
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # Create default admin user
                admin_user = User(
                    username='admin',
                    email='admin@carpool.local',
                    password_hash=generate_password_hash('admin123'),
                    role='administrator'
                )
                db.session.add(admin_user)
                app.logger.info('Default admin user created')
                
                # Create sample regular user
                test_user = User(
                    username='testuser',
                    email='test@carpool.local',
                    password_hash=generate_password_hash('test123'),
                    role='user'
                )
                db.session.add(test_user)
                app.logger.info('Sample test user created')
            
            # Check if parking spots exist
            if ParkingSpot.query.count() == 0:
                # Create sample parking spots
                spots = [
                    ParkingSpot(id='A1', location='Level A', description='Near elevator', status='available'),
                    ParkingSpot(id='A2', location='Level A', description='Near stairwell', status='available'),
                    ParkingSpot(id='A3', location='Level A', description='Corner spot', status='available'),
                    ParkingSpot(id='B1', location='Level B', description='Covered parking', status='available'),
                    ParkingSpot(id='B2', location='Level B', description='Wide space', status='available'),
                    ParkingSpot(id='B3', location='Level B', description='Standard spot', status='available'),
                    ParkingSpot(id='C1', location='Outdoor', description='Open air parking', status='available'),
                    ParkingSpot(id='C2', location='Outdoor', description='Near entrance', status='available'),
                    ParkingSpot(id='C3', location='Outdoor', description='Shaded area', status='maintenance'),
                    ParkingSpot(id='D1', location='VIP', description='Executive parking', status='available'),
                ]
                
                for spot in spots:
                    db.session.add(spot)
                
                app.logger.info(f'Created {len(spots)} sample parking spots')
            
            # Commit all changes
            db.session.commit()
            app.logger.info('Database initialization completed successfully')
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error initializing database: {e}', exc_info=True)
            raise

@app.cli.command()
def reset_db():
    """Reset the database by dropping and recreating all tables."""
    with app.app_context():
        db.drop_all()
        app.logger.info('All database tables dropped')
        init_database()
        print('Database reset completed successfully')

@app.cli.command()
def create_admin():
    """Create a new admin user."""
    username = input('Enter admin username: ')
    email = input('Enter admin email: ')
    password = input('Enter admin password: ')
    
    with app.app_context():
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f'User {username} already exists')
            return
        
        admin_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role='administrator'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f'Admin user {username} created successfully')

@app.cli.command()
def db_init():
    """Initialize the database."""
    with app.app_context():
        try:
            # Initialize database migrations
            migrate_instance.init_app(app, db)
            app.logger.info('Flask-Migrate initialized')
            
            # Run database migrations
            upgrade()
            app.logger.info('Database migrated to latest version')
            
            # Setup initial data
            setup_initial_data()
            app.logger.info('Initial data setup completed')
        
        except Exception as e:
            app.logger.error(f'Error during database initialization: {e}', exc_info=True)
            raise

@app.cli.command()
def db_migrate():
    """Run database migrations."""
    with app.app_context():
        try:
            # Run migration scripts
            migrate()
            app.logger.info('Database migration completed')
        except Exception as e:
            app.logger.error(f'Error during database migration: {e}', exc_info=True)
            raise

@app.cli.command()
def db_upgrade():
    """Upgrade the database to the latest version."""
    with app.app_context():
        try:
            # Apply all pending migrations
            upgrade()
            app.logger.info('Database upgraded to the latest version')
        except Exception as e:
            app.logger.error(f'Error during database upgrade: {e}', exc_info=True)
            raise

@app.cli.command()
def db_downgrade():
    """Downgrade the database to the previous version."""
    with app.app_context():
        try:
            # Downgrade the database
            downgrade()
            app.logger.info('Database downgraded to the previous version')
        except Exception as e:
            app.logger.error(f'Error during database downgrade: {e}', exc_info=True)
            raise

# CLI Commands for database management

@app.cli.command()
@with_appcontext
def init_migrations():
    """Initialize migration repository."""
    try:
        migrate_init()
        app.logger.info('Migration repository initialized')
        print('Migration repository initialized successfully')
    except Exception as e:
        app.logger.error(f'Error initializing migrations: {e}')
        print(f'Error: {e}')

@app.cli.command()
@with_appcontext
def create_migration():
    """Create a new migration."""
    message = input('Enter migration message (optional): ').strip()
    if not message:
        message = None
    
    try:
        migrate(message=message)
        app.logger.info(f'Migration created: {message}')
        print('Migration created successfully')
    except Exception as e:
        app.logger.error(f'Error creating migration: {e}')
        print(f'Error: {e}')

@app.cli.command()
@with_appcontext
def apply_migrations():
    """Apply all pending migrations."""
    try:
        upgrade()
        app.logger.info('Migrations applied successfully')
        print('Migrations applied successfully')
    except Exception as e:
        app.logger.error(f'Error applying migrations: {e}')
        print(f'Error: {e}')

@app.cli.command()
@with_appcontext
def rollback_migration():
    """Rollback to previous migration."""
    try:
        downgrade()
        app.logger.info('Migration rolled back successfully')
        print('Migration rolled back successfully')
    except Exception as e:
        app.logger.error(f'Error rolling back migration: {e}')
        print(f'Error: {e}')

@app.cli.command()
@with_appcontext
def migration_status():
    """Check migration status."""
    try:
        status = check_migration_status()
        print(f"Migration Status: {status['status']}")
        print(f"Message: {status['message']}")
        if 'current_revision' in status:
            print(f"Current Revision: {status['current_revision']}")
        if 'head_revision' in status:
            print(f"Head Revision: {status['head_revision']}")
    except Exception as e:
        app.logger.error(f'Error checking migration status: {e}')
        print(f'Error: {e}')

@app.cli.command()
@with_appcontext
def setup_initial():
    """Set up initial application data."""
    try:
        setup_initial_data()
        print('Initial data setup completed successfully')
    except Exception as e:
        app.logger.error(f'Error setting up initial data: {e}')
        print(f'Error: {e}')

if __name__ == '__main__':
    # Configure logging
    configure_logging()
    
    # Initialize database
    init_database()
    
    # Get configuration from environment
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('FLASK_PORT', 5005))
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    
    app.logger.info(f'Starting Carpool application on {host}:{port} (debug={debug_mode})')
    
    # Try to run the application with error handling
    try:
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True
        )
    except OSError as e:
        if "Address already in use" in str(e):
            app.logger.error(f'Port {port} is already in use. Trying alternative ports...')
            # Try alternative ports
            for alt_port in [5006, 5007, 5008, 5009, 8000, 8080]:
                try:
                    app.logger.info(f'Trying port {alt_port}...')
                    app.run(
                        host=host,
                        port=alt_port,
                        debug=debug_mode,
                        threaded=True
                    )
                    break
                except OSError:
                    continue
            else:
                app.logger.error('No available ports found. Please manually specify a free port.')
        else:
            app.logger.error(f'Error starting application: {e}')
            raise
