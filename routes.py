from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from app import app, db
from models import User, Card, Order, CartItem
from forms import RegistrationForm, LoginForm, CardForm
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import json

@app.route('/api/pokemon', methods=['GET'])
def get_pokemon():
    # Load Pokemon data from JSON file
    with open('pokemon_data.json') as f:
        pokemon_data = json.load(f)
    return jsonify(pokemon_data)

@app.route('/')
def index():
    # Get the filter parameters from the request
    name_filter = request.args.get('name')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Start with the base query
    query = Card.query

    # Apply filters based on user input
    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))  # Filter by name

    if min_price is not None:
        query = query.filter(Card.price >= min_price)  # Filter by minimum price

    if max_price is not None:
        query = query.filter(Card.price <= max_price)  # Filter by maximum price

    # Paginate the results
    page = request.args.get('page', 1, type=int)
    cards = query.paginate(page=page, per_page=10)

    return render_template('index.html', cards=cards)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
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
    
    with open('pokemon_data.json') as f:
        pokemon_data = json.load(f)

    form.pokemon_name.choices = [(pokemon['name'], pokemon['name']) for pokemon in pokemon_data]

    if form.validate_on_submit():
        # Use the form data to create a new card
        card = Card(
            name=form.pokemon_name.data,  # Get selected Pokémon name
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
            seller_id=current_user.id
        )
        db.session.add(card)
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

@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total_price = sum(item.card.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/add_to_card/<int:card_id>', methods=['POST'])
@login_required
def add_to_cart(card_id):
    quantity = request.form.get('quantity', 1, type=int)
    cart_item = CartItem(user_id=current_user.id, card_id=card_id, quantity=quantity)
    db.session.add(cart_item)
    db.session.commit()
    flash('Card added to cart!', 'success')
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    # Implement payment processing logic here
    # After processing, clear the clart:
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()
    flash('Purchase successful!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.user_id == current_user.id:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart!', 'success')
    else:
        flash('You cannot remove this item.', 'danger')
    return redirect(url_for('view_cart'))