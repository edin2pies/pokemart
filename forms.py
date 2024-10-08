from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, FileField
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
    name = StringField('Card Name', validators=[DataRequired(), Length(min=1, max=150)])
    description = TextAreaField('Description', validators=[Length(max=500)])
    price = FloatField('Price ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    image_url = StringField('Image URL', validators=[Length(max=250)])
    stock = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Card')