"""
This module defines forms for parking spot management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from carpool.models.parking_spot import ParkingSpot

class ParkingSpotForm(FlaskForm):
    """
    Form for creating or editing parking spots.
    """
    id = StringField('Spot ID', validators=[DataRequired(), Length(min=1, max=10)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    status = SelectField('Status', choices=[
        ('free', 'Free'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Maintenance')
    ], default='free', validators=[DataRequired()])
    submit = SubmitField('Save')
    
    def __init__(self, original_id=None, *args, **kwargs):
        """
        Initialize the ParkingSpotForm.
        
        :param original_id: Original ID when editing a parking spot
        """
        super(ParkingSpotForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
    
    def validate_id(self, id):
        """
        Validate that the spot ID is not already in use.
        
        :param id: Spot ID field
        :raises ValidationError: If ID is already in use by another spot
        """
        if self.original_id is None or id.data != self.original_id:
            spot = ParkingSpot.query.get(id.data)
            if spot is not None:
                raise ValidationError('Parking spot ID already in use. Please choose a different one.')
