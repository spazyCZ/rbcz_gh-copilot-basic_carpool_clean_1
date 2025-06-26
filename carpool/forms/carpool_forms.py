"""
Carpool forms for trip organization and management.

This module defines Flask-WTF forms for creating and editing carpool trips.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime


class CarpoolForm(FlaskForm):
    """
    Form for creating new carpool trips.
    
    Provides fields for trip details including name, locations, times, and passenger capacity.
    """
    
    name = StringField(
        'Trip Name',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={'placeholder': 'Enter trip name (e.g., "Downtown Meeting")', 'class': 'form-control'}
    )
    
    origin = StringField(
        'Origin',
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={'placeholder': 'Starting location', 'class': 'form-control'}
    )
    
    destination = StringField(
        'Destination',
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={'placeholder': 'Destination location', 'class': 'form-control'}
    )
    
    departure_time = DateTimeField(
        'Departure Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local', 'min': datetime.now().strftime('%Y-%m-%dT%H:%M')}
    )
    
    return_time = DateTimeField(
        'Return Time (Optional)',
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local'}
    )
    
    max_passengers = IntegerField(
        'Maximum Passengers',
        validators=[DataRequired(), NumberRange(min=1, max=8)],
        default=4,
        render_kw={'class': 'form-control', 'min': '1', 'max': '8'}
    )
    
    notes = TextAreaField(
        'Additional Notes',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'Any additional information about the trip...', 'class': 'form-control', 'rows': '3'}
    )
    
    submit = SubmitField(
        'Create Carpool',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_departure_time(self, departure_time):
        """
        Custom validation for departure time.
        
        :param departure_time: Departure time field to validate
        :raises ValidationError: If departure time is in the past
        """
        if departure_time.data and departure_time.data <= datetime.now():
            raise ValidationError('Departure time must be in the future.')
    
    def validate_return_time(self, return_time):
        """
        Custom validation for return time.
        
        :param return_time: Return time field to validate
        :raises ValidationError: If return time is before departure time
        """
        if return_time.data and self.departure_time.data:
            if return_time.data <= self.departure_time.data:
                raise ValidationError('Return time must be after departure time.')


class EditCarpoolForm(FlaskForm):
    """
    Form for editing existing carpool trips.
    
    Provides fields for updating trip details with pre-populated data.
    """
    
    name = StringField(
        'Trip Name',
        validators=[DataRequired(), Length(min=3, max=100)],
        render_kw={'placeholder': 'Enter trip name', 'class': 'form-control'}
    )
    
    origin = StringField(
        'Origin',
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={'placeholder': 'Starting location', 'class': 'form-control'}
    )
    
    destination = StringField(
        'Destination',
        validators=[DataRequired(), Length(min=3, max=200)],
        render_kw={'placeholder': 'Destination location', 'class': 'form-control'}
    )
    
    departure_time = DateTimeField(
        'Departure Time',
        validators=[DataRequired()],
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local'}
    )
    
    return_time = DateTimeField(
        'Return Time (Optional)',
        format='%Y-%m-%dT%H:%M',
        render_kw={'class': 'form-control', 'type': 'datetime-local'}
    )
    
    max_passengers = IntegerField(
        'Maximum Passengers',
        validators=[DataRequired(), NumberRange(min=1, max=8)],
        render_kw={'class': 'form-control', 'min': '1', 'max': '8'}
    )
    
    notes = TextAreaField(
        'Additional Notes',
        validators=[Length(max=500)],
        render_kw={'placeholder': 'Any additional information about the trip...', 'class': 'form-control', 'rows': '3'}
    )
    
    submit = SubmitField(
        'Update Carpool',
        render_kw={'class': 'btn btn-warning'}
    )
    
    def __init__(self, carpool=None, *args, **kwargs):
        """
        Initialize form with carpool data.
        
        :param carpool: Existing carpool to edit
        """
        super(EditCarpoolForm, self).__init__(*args, **kwargs)
        self.carpool = carpool
        
        # Pre-populate with existing data
        if carpool and not self.data:
            self.name.data = carpool.name
            self.origin.data = carpool.origin
            self.destination.data = carpool.destination
            self.departure_time.data = carpool.departure_time
            self.return_time.data = carpool.return_time
            self.max_passengers.data = carpool.max_passengers
            self.notes.data = carpool.notes
    
    def validate_departure_time(self, departure_time):
        """
        Custom validation for departure time.
        
        :param departure_time: Departure time field to validate
        :raises ValidationError: If departure time is in the past
        """
        if departure_time.data and departure_time.data <= datetime.now():
            raise ValidationError('Departure time must be in the future.')
    
    def validate_return_time(self, return_time):
        """
        Custom validation for return time.
        
        :param return_time: Return time field to validate
        :raises ValidationError: If return time is before departure time
        """
        if return_time.data and self.departure_time.data:
            if return_time.data <= self.departure_time.data:
                raise ValidationError('Return time must be after departure time.')
    
    def validate_max_passengers(self, max_passengers):
        """
        Custom validation for maximum passengers to ensure it's not less than current passengers.
        
        :param max_passengers: Maximum passengers field to validate
        :raises ValidationError: If new max is less than current passengers
        """
        if self.carpool and max_passengers.data < self.carpool.current_passengers:
            raise ValidationError(f'Maximum passengers cannot be less than current passengers ({self.carpool.current_passengers}).')


class JoinCarpoolForm(FlaskForm):
    """
    Simple form for joining a carpool trip.
    
    Provides a confirmation button for joining trips.
    """
    
    submit = SubmitField(
        'Join Carpool',
        render_kw={'class': 'btn btn-success'}
    )


class LeaveCarpoolForm(FlaskForm):
    """
    Simple form for leaving a carpool trip.
    
    Provides a confirmation button for leaving trips.
    """
    
    submit = SubmitField(
        'Leave Carpool',
        render_kw={'class': 'btn btn-danger'}
    )


class CarpoolSearchForm(FlaskForm):
    """
    Form for searching and filtering carpool trips.
    
    Provides fields for filtering trips by origin, destination, and date.
    """
    
    origin = StringField(
        'Origin',
        render_kw={'placeholder': 'Filter by origin...', 'class': 'form-control'}
    )
    
    destination = StringField(
        'Destination',
        render_kw={'placeholder': 'Filter by destination...', 'class': 'form-control'}
    )
    
    date_from = DateTimeField(
        'From Date',
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )
    
    date_to = DateTimeField(
        'To Date',
        format='%Y-%m-%d',
        render_kw={'class': 'form-control', 'type': 'date'}
    )
    
    submit = SubmitField(
        'Search',
        render_kw={'class': 'btn btn-outline-primary'}
    )
    
    def validate_date_to(self, date_to):
        """
        Custom validation for date range.
        
        :param date_to: End date field to validate
        :raises ValidationError: If end date is before start date
        """
        if date_to.data and self.date_from.data:
            if date_to.data < self.date_from.data:
                raise ValidationError('End date must be after start date.')
