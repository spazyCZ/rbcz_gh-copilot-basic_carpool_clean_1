"""
CLI commands for database seeding and management.

Provides Flask CLI commands for creating initial data.
"""
import click
from flask import current_app
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User, ParkingSpot, ActionType, Action


@click.command()
@with_appcontext
def seed_admin():
    """Create default administrator user."""
    config = current_app.config
    
    username = config.get('ADMIN_DEFAULT_USERNAME', 'admin')
    email = config.get('ADMIN_DEFAULT_EMAIL', 'admin@example.com')
    password = config.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
    
    # Check if admin already exists
    existing_admin = User.find_by_username(username)
    if existing_admin:
        click.echo(f'Admin user "{username}" already exists.')
        return
    
    # Create admin user
    try:
        admin_user = User.create_user(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        
        # Log the action
        Action.log_action(
            action_type=ActionType.USER_CREATE,
            description=f"Admin user created: {username}",
            user_id=admin_user.id,
            extra_data={'role': 'admin', 'created_by': 'cli_seed'}
        )
        
        click.echo(f'Admin user "{username}" created successfully.')
        click.echo(f'Email: {email}')
        click.echo(f'Password: {password}')
        click.echo('Please change the password after first login.')
        
    except Exception as e:
        click.echo(f'Error creating admin user: {e}')
        db.session.rollback()


@click.command()
@with_appcontext  
def seed_spots():
    """Create sample parking spots."""
    spots_data = [
        # Level A
        ('A1', 'Level A - Near entrance', 'Premium spot near main entrance'),
        ('A2', 'Level A - Near entrance', 'Premium spot near main entrance'),
        ('A3', 'Level A - Handicap accessible', 'Handicap accessible spot', True, False),
        ('A4', 'Level A - Electric charging', 'Electric vehicle charging spot', False, True),
        ('A5', 'Level A - Standard', 'Standard parking spot'),
        
        # Level B  
        ('B1', 'Level B - Standard', 'Standard parking spot'),
        ('B2', 'Level B - Standard', 'Standard parking spot'),
        ('B3', 'Level B - Handicap accessible', 'Handicap accessible spot', True, False),
        ('B4', 'Level B - Electric charging', 'Electric vehicle charging spot', False, True),
        ('B5', 'Level B - Standard', 'Standard parking spot'),
        
        # Ground level
        ('G1', 'Ground level - Visitor', 'Visitor parking spot'),
        ('G2', 'Ground level - Visitor', 'Visitor parking spot'),
        ('G3', 'Ground level - Handicap accessible', 'Handicap accessible visitor spot', True, False),
        ('G4', 'Ground level - Electric charging', 'Electric vehicle charging spot', False, True),
        ('G5', 'Ground level - Standard', 'Standard parking spot'),
    ]
    
    created_count = 0
    skipped_count = 0
    
    for spot_data in spots_data:
        spot_id = spot_data[0]
        location = spot_data[1]
        description = spot_data[2]
        handicap = spot_data[3] if len(spot_data) > 3 else False
        electric = spot_data[4] if len(spot_data) > 4 else False
        
        # Check if spot already exists
        existing_spot = ParkingSpot.query.get(spot_id)
        if existing_spot:
            skipped_count += 1
            continue
        
        try:
            ParkingSpot.create_spot(
                id=spot_id,
                location=location,
                description=description,
                is_handicap_accessible=handicap,
                is_electric_charging=electric
            )
            created_count += 1
            
        except Exception as e:
            click.echo(f'Error creating spot {spot_id}: {e}')
            db.session.rollback()
    
    click.echo(f'Created {created_count} parking spots.')
    if skipped_count > 0:
        click.echo(f'Skipped {skipped_count} existing spots.')


@click.command()
@with_appcontext
def seed_demo_user():
    """Create demo user for testing."""
    username = 'demo'
    email = 'demo@example.com'
    password = 'demo123'
    
    # Check if demo user already exists
    existing_user = User.find_by_username(username)
    if existing_user:
        click.echo(f'Demo user "{username}" already exists.')
        return
    
    try:
        demo_user = User.create_user(
            username=username,
            email=email,
            password=password,
            role='user'
        )
        
        # Log the action
        Action.log_action(
            action_type=ActionType.USER_CREATE,
            description=f"Demo user created: {username}",
            user_id=demo_user.id,
            extra_data={'role': 'user', 'created_by': 'cli_seed'}
        )
        
        click.echo(f'Demo user "{username}" created successfully.')
        click.echo(f'Email: {email}')
        click.echo(f'Password: {password}')
        
    except Exception as e:
        click.echo(f'Error creating demo user: {e}')
        db.session.rollback()


@click.command()
@with_appcontext
def seed_all():
    """Run all seeding commands."""
    click.echo('Starting database seeding...')
    
    # Create admin user
    click.echo('\n1. Creating admin user...')
    seed_admin.callback()
    
    # Create parking spots
    click.echo('\n2. Creating parking spots...')
    seed_spots.callback()
    
    # Create demo user
    click.echo('\n3. Creating demo user...')
    seed_demo_user.callback()
    
    click.echo('\nDatabase seeding completed!')


def init_cli_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(seed_admin)
    app.cli.add_command(seed_spots)
    app.cli.add_command(seed_demo_user)
    app.cli.add_command(seed_all)