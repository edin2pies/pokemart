from flask import render_template, redirect, url_for, flash, request
from app import app, db
from models import User, Card, Order
from forms import RegistrationForm, LoginForm, CardForm
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    cards = Card.query.all()
    return render_template('index.html', cards=cards)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', method=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/add_card', methods=['GET', 'POST'])
@login_required
def add_card():
    form = CardForm()
    if form.validate_on_submit():
        new_card = Card(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
            seller_id=current_user.id
        )
        db.session.add(new_card)
        db.session.commit()
        flash('Card listed successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_card.html', form=form)

@app.route('/card/<int:card_id>')
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    return render_template('card_detail.html', card=card)

@app.route('/buy/<int:card_id>', methods=['POST'])
@login_required
def buy_card(card_id):
    card = Card.query.get_or_404(card_id)
    quantity = int(request.form.get('quantity', 1))
    if quantity < 1:
        flash('Invalid quantity.', 'danger')
        return redirect(url_for('card_detail', card_id=card_id))
    total_price = card.price * quantity
    new_order = Order(
        buyer_id=current_user.id,
        card_id=card.id,
        quantity=quantity,
        total_price=total_price
    )
    db.session.add(new_order)
    db.session.commit()
    flash('Purchase successful!', 'success')
    return redirect(url_for('index'))