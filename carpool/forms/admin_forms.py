"""
Admin forms for administrative operations and system management.

This module defines Flask-WTF forms for administrative operations including
user management, parking spot management, and system configuration.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from carpool.models.user import User
from carpool.models.parking_spot import ParkingSpot


class CreateUserForm(FlaskForm):
    """
    Admin form for creating new user accounts.
    
    Provides fields for username, email, password, and role selection.
    """
    
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)],
        render_kw={'placeholder': 'Enter username', 'class': 'form-control'}
    )
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'placeholder': 'Enter email address', 'class': 'form-control'}
    )
    
    password = StringField(
        'Password',
        validators=[DataRequired(), Length(min=6)],
        render_kw={'placeholder': 'Set password (min 6 characters)', 'class': 'form-control', 'type': 'password'}
    )
    
    role = SelectField(
        'Role',
        choices=[
            ('user', 'User'),
            ('administrator', 'Administrator'),
            ('guest', 'Guest')
        ],
        default='user',
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Create User',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_username(self, username):
        """
        Custom validation for username uniqueness.
        
        :param username: Username field to validate
        :raises ValidationError: If username already exists
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """
        Custom validation for email uniqueness.
        
        :param email: Email field to validate
        :raises ValidationError: If email already exists
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')


class EditUserForm(FlaskForm):
    """
    Admin form for editing existing user accounts.
    
    Provides fields for email and role changes.
    """
    
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(max=120)],
        render_kw={'class': 'form-control'}
    )
    
    role = SelectField(
        'Role',
        choices=[
            ('user', 'User'),
            ('administrator', 'Administrator'),
            ('guest', 'Guest')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Update User',
        render_kw={'class': 'btn btn-warning'}
    )
    
    def __init__(self, original_email, *args, **kwargs):
        """
        Initialize form with original email for validation.
        
        :param original_email: Original email address of the user being edited
        """
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """
        Custom validation for email uniqueness (excluding current user).
        
        :param email: Email field to validate
        :raises ValidationError: If email already exists for another user
        """
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different email.')


class CreateParkingSpotForm(FlaskForm):
    """
    Admin form for creating new parking spots.
    
    Provides fields for spot ID, location, and description.
    """
    
    spot_id = StringField(
        'Spot ID',
        validators=[DataRequired(), Length(min=1, max=10)],
        render_kw={'placeholder': 'e.g., A1, B2, C15', 'class': 'form-control'}
    )
    
    location = StringField(
        'Location',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={'placeholder': 'e.g., Level A, Outdoor, Building B', 'class': 'form-control'}
    )
    
    description = TextAreaField(
        'Description (Optional)',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'Additional details about the parking spot...', 'class': 'form-control', 'rows': '3'}
    )
    
    submit = SubmitField(
        'Create Parking Spot',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_spot_id(self, spot_id):
        """
        Custom validation for spot ID uniqueness.
        
        :param spot_id: Spot ID field to validate
        :raises ValidationError: If spot ID already exists
        """
        spot = ParkingSpot.query.get(spot_id.data)
        if spot:
            raise ValidationError('Parking spot ID already exists. Please choose a different one.')


class EditParkingSpotForm(FlaskForm):
    """
    Admin form for editing existing parking spots.
    
    Provides fields for location, description, and status updates.
    """
    
    location = StringField(
        'Location',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={'class': 'form-control'}
    )
    
    description = TextAreaField(
        'Description',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'Additional details about the parking spot...', 'class': 'form-control', 'rows': '3'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('available', 'Available'),
            ('reserved', 'Reserved'),
            ('maintenance', 'Maintenance')
        ],
        validators=[DataRequired()],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Update Parking Spot',
        render_kw={'class': 'btn btn-warning'}
    )


class ActivityLogFilterForm(FlaskForm):
    """
    Form for filtering activity logs in the admin panel.
    
    Provides fields for filtering by action type and username.
    """
    
    action_type = SelectField(
        'Action Type',
        choices=[
            ('', 'All Actions'),
            ('user_login', 'User Login'),
            ('user_logout', 'User Logout'),
            ('user_created', 'User Created'),
            ('password_changed', 'Password Changed'),
            ('reservation_created', 'Reservation Created'),
            ('reservation_updated', 'Reservation Updated'),
            ('reservation_cancelled', 'Reservation Cancelled'),
            ('carpool_created', 'Carpool Created'),
            ('carpool_updated', 'Carpool Updated'),
            ('carpool_deleted', 'Carpool Deleted'),
            ('carpool_joined', 'Carpool Joined'),
            ('carpool_left', 'Carpool Left'),
            ('admin_action', 'Admin Action')
        ],
        render_kw={'class': 'form-select'}
    )
    
    username = StringField(
        'Username',
        render_kw={'placeholder': 'Filter by username...', 'class': 'form-control'}
    )
    
    submit = SubmitField(
        'Filter',
        render_kw={'class': 'btn btn-outline-primary'}
    )


class SystemConfigForm(FlaskForm):
    """
    Form for system configuration settings.
    
    Provides fields for basic system settings and maintenance mode.
    """
    
    maintenance_mode = SelectField(
        'Maintenance Mode',
        choices=[
            ('off', 'Off'),
            ('on', 'On')
        ],
        render_kw={'class': 'form-select'}
    )
    
    max_reservations_per_user = SelectField(
        'Max Reservations Per User',
        choices=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
            ('5', '5'),
            ('10', '10'),
            ('unlimited', 'Unlimited')
        ],
        render_kw={'class': 'form-select'}
    )
    
    advance_booking_days = SelectField(
        'Advance Booking Days',
        choices=[
            ('7', '7 days'),
            ('14', '14 days'),
            ('30', '30 days'),
            ('60', '60 days'),
            ('90', '90 days')
        ],
        render_kw={'class': 'form-select'}
    )
    
    submit = SubmitField(
        'Update Settings',
        render_kw={'class': 'btn btn-primary'}
    )
