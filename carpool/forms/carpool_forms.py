"""
This module defines forms for carpool management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from datetime import datetime

class CarpoolForm(FlaskForm):
    """
    Form for creating or editing carpools.
    """
    name = StringField('Carpool Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    origin = StringField('Origin', validators=[
        DataRequired(),
        Length(max=100, message='Origin must be less than 100 characters')
    ])
    destination = StringField('Destination', validators=[
        DataRequired(),
        Length(max=100, message='Destination must be less than 100 characters')
    ])
    departure_time = DateTimeField('Departure Time', format='%Y-%m-%d %H:%M', validators=[
        DataRequired(message='Departure time is required')
    ])
    return_time = DateTimeField('Return Time', format='%Y-%m-%d %H:%M', validators=[
        Optional()
    ])
    max_passengers = IntegerField('Maximum Passengers', validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='Maximum passengers must be between 1 and 10')
    ], default=4)
    notes = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=500, message='Notes must be less than 500 characters')
    ])
    submit = SubmitField('Save Carpool')

    def validate_departure_time(self, field):
        """
        Validate that the departure time is in the future.
        
        :param field: The departure_time field
        :raises ValidationError: If the departure time is in the past
        """
        if field.data and field.data <= datetime.now():
            raise ValidationError('Departure time must be in the future')
    
    def validate_return_time(self, field):
        """
        Validate that the return time is after the departure time.
        
        :param field: The return_time field
        :raises ValidationError: If the return time is before the departure time
        """
        if field.data and self.departure_time.data and field.data <= self.departure_time.data:
            raise ValidationError('Return time must be after departure time')


class JoinCarpoolForm(FlaskForm):
    """
    Form for joining a carpool.
    """
    submit = SubmitField('Join Carpool')


class LeaveCarpoolForm(FlaskForm):
    """
    Form for leaving a carpool.
    """
    submit = SubmitField('Leave Carpool')


class CancelCarpoolForm(FlaskForm):
    """
    Form for cancelling a carpool.
    """
    submit = SubmitField('Cancel Carpool')
