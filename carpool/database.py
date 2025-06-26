# Database migration configuration and utilities
"""
Flask-Migrate configuration and database migration utilities.

This module provides database migration support using Flask-Migrate,
allowing for version-controlled database schema changes.
"""

import os
from flask import current_app
from flask_migrate import Migrate, upgrade, init, migrate, downgrade
from carpool.extensions import db
from carpool.models import *  # Import all models to ensure they're registered


def init_migrate(app):
    """
    Initialize Flask-Migrate with the Flask application.
    
    :param app: Flask application instance
    :return: Migrate instance
    """
    migrate_instance = Migrate(app, db, directory='migrations')
    return migrate_instance


def init_db():
    """
    Initialize the database with tables.
    This creates all tables defined by SQLAlchemy models.
    """
    current_app.logger.info("Initializing database tables...")
    db.create_all()
    current_app.logger.info("Database tables created successfully")


def create_migration(message: str = None):
    """
    Create a new database migration.
    
    :param message: Migration message/description
    :return: Migration script path or None if failed
    """
    try:
        if not message:
            message = "Auto-generated migration"
        
        current_app.logger.info(f"Creating migration: {message}")
        result = migrate(message=message)
        current_app.logger.info("Migration created successfully")
        return result
    except Exception as e:
        current_app.logger.error(f"Failed to create migration: {e}")
        return None


def apply_migrations():
    """
    Apply all pending migrations to the database.
    
    :return: True if successful, False otherwise
    """
    try:
        current_app.logger.info("Applying database migrations...")
        upgrade()
        current_app.logger.info("Migrations applied successfully")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to apply migrations: {e}")
        return False


def rollback_migration(revision: str = None):
    """
    Rollback database to a specific revision.
    
    :param revision: Revision ID to rollback to (default: previous revision)
    :return: True if successful, False otherwise
    """
    try:
        target = revision or "-1"
        current_app.logger.info(f"Rolling back database to revision: {target}")
        downgrade(revision=target)
        current_app.logger.info("Database rollback completed successfully")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to rollback database: {e}")
        return False


def setup_initial_data():
    """
    Set up initial data for the application.
    This includes creating default admin user and sample parking spots.
    """
    from carpool.models.user import User
    from carpool.models.parking_spot import ParkingSpot
    from carpool.services.auth_service import AuthService
    from werkzeug.security import generate_password_hash
    
    try:
        current_app.logger.info("Setting up initial data...")
        
        # Create default admin user if none exists
        admin_user = User.query.filter_by(role='administrator').first()
        if not admin_user:
            admin_data = {
                'username': 'admin',
                'email': 'admin@carpool.local',
                'password': 'admin123',
                'role': 'administrator'
            }
            
            admin_user = User(
                username=admin_data['username'],
                email=admin_data['email'],
                password_hash=generate_password_hash(admin_data['password']),
                role=admin_data['role']
            )
            
            db.session.add(admin_user)
            current_app.logger.info("Created default admin user")
        
        # Create sample parking spots if none exist
        if ParkingSpot.query.count() == 0:
            sample_spots = [
                {'id': 'A1', 'location': 'Level A', 'description': 'Near elevator'},
                {'id': 'A2', 'location': 'Level A', 'description': 'Corner spot'},
                {'id': 'A3', 'location': 'Level A', 'description': 'Regular spot'},
                {'id': 'B1', 'location': 'Level B', 'description': 'Near stairs'},
                {'id': 'B2', 'location': 'Level B', 'description': 'Wide spot'},
                {'id': 'B3', 'location': 'Level B', 'description': 'Regular spot'},
                {'id': 'C1', 'location': 'Outdoor', 'description': 'Covered parking'},
                {'id': 'C2', 'location': 'Outdoor', 'description': 'Open parking'},
                {'id': 'C3', 'location': 'Outdoor', 'description': 'End spot'},
                {'id': 'VIP1', 'location': 'VIP Section', 'description': 'Reserved for executives'},
            ]
            
            for spot_data in sample_spots:
                spot = ParkingSpot(
                    id=spot_data['id'],
                    location=spot_data['location'],
                    description=spot_data['description'],
                    status='available'
                )
                db.session.add(spot)
            
            current_app.logger.info(f"Created {len(sample_spots)} sample parking spots")
        
        db.session.commit()
        current_app.logger.info("Initial data setup completed successfully")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to set up initial data: {e}")
        raise


def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    WARNING: This will delete all data!
    
    :return: True if successful, False otherwise
    """
    try:
        current_app.logger.warning("RESETTING DATABASE - ALL DATA WILL BE LOST!")
        
        # Drop all tables
        db.drop_all()
        current_app.logger.info("Dropped all database tables")
        
        # Recreate tables
        db.create_all()
        current_app.logger.info("Recreated database tables")
        
        # Set up initial data
        setup_initial_data()
        
        current_app.logger.info("Database reset completed successfully")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to reset database: {e}")
        return False


def check_migration_status():
    """
    Check the current migration status.
    
    :return: Dictionary with migration status information
    """
    try:
        from alembic import command
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        from alembic.runtime.environment import EnvironmentContext
        from alembic.runtime.migration import MigrationContext
        
        # Get migration directory
        migrations_dir = os.path.join(current_app.root_path, '..', 'migrations')
        
        if not os.path.exists(migrations_dir):
            return {
                'status': 'not_initialized',
                'message': 'Migration repository not initialized'
            }
        
        # Create Alembic config
        config = Config()
        config.set_main_option("script_location", migrations_dir)
        
        script = ScriptDirectory.from_config(config)
        
        # Get current revision
        with current_app.app_context():
            connection = db.engine.connect()
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            connection.close()
        
        # Get head revision
        head_rev = script.get_current_head()
        
        # Check if up to date
        is_up_to_date = current_rev == head_rev
        
        return {
            'status': 'up_to_date' if is_up_to_date else 'pending_migrations',
            'current_revision': current_rev,
            'head_revision': head_rev,
            'is_up_to_date': is_up_to_date,
            'message': 'Database is up to date' if is_up_to_date else 'Migrations pending'
        }
        
    except Exception as e:
        current_app.logger.error(f"Failed to check migration status: {e}")
        return {
            'status': 'error',
            'message': f'Error checking migration status: {str(e)}'
        }
