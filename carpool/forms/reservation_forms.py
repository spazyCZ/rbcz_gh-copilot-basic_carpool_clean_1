"""
This module defines forms for reservation management.
"""
from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from carpool.models.reservation import Reservation
from carpool.models.parking_spot import ParkingSpot

class ReservationForm(FlaskForm):
    """
    Form for creating or editing reservations.
    """
    spot_id = SelectField('Parking Spot', validators=[DataRequired()])
    username = HiddenField()
    reservation_date = DateField('Reservation Date', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Save')
    
    def __init__(self, available_spots=None, original_id=None, *args, **kwargs):
        """
        Initialize the ReservationForm.
        
        :param available_spots: List of available parking spots
        :param original_id: Original ID when editing a reservation
        """
        super(ReservationForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
        
        # Populate the spot_id dropdown with available spots
        if available_spots:
            self.spot_id.choices = [(spot.id, f"{spot.id} - {spot.location}") for spot in available_spots]
    
    def validate_reservation_date(self, reservation_date):
        """
        Validate that the reservation date is not in the past.
        
        :param reservation_date: Reservation date field
        :raises ValidationError: If date is in the past
        """
        if reservation_date.data < date.today():
            raise ValidationError('Reservation date cannot be in the past.')
    
    def validate(self, extra_validators=None):
        """
        Custom validation to check for double-booking.
        
        :param extra_validators: Additional validators to be run
        :return: True if validation passes, False otherwise
        """
        if not super(ReservationForm, self).validate(extra_validators=extra_validators):
            return False
        
        # If editing an existing reservation and not changing spot or date, validation passes
        if self.original_id is not None:
            original_reservation = Reservation.query.get(self.original_id)
            if (original_reservation.spot_id == self.spot_id.data and 
                original_reservation.reservation_date == self.reservation_date.data):
                return True
        
        # Check if the spot is already reserved for that date
        existing_reservation = Reservation.query.filter_by(
            spot_id=self.spot_id.data,
            reservation_date=self.reservation_date.data
        ).first()
        
        if existing_reservation:
            self.spot_id.errors.append('This spot is already reserved for the selected date.')
            return False
        
        # Check if the spot exists and is free
        spot = ParkingSpot.query.get(self.spot_id.data)
        if not spot or spot.status != 'free':
            self.spot_id.errors.append('This spot is not available for reservation.')
            return False
        
        return True
