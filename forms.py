from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, TextAreaField, FileField, SelectField, IntegerField, FloatField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CardForm(FlaskForm):
    pokemon_name = SelectField('Select Pokémon', choices=[], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    buy_out_price = FloatField('Buy-Out Price', validators=[DataRequired()])
    highest_bid = FloatField('Current Highest Bid', default=0.0)
    bidding_end_time = DateTimeField('Bidding End Time', format='%Y-%m-%d', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])
    stock = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Card')