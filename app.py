from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, User, Card, Order
from forms import RegistrationForm, LoginForm, CardForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Create databse tables
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after initializing extensions to avoid circular imports
import routes

if __name__ == '__main__':
    app.run(debug=True)