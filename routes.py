from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from app import app, db
from models import User, Card, Order, Bid
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
    price_range = request.args.get('price_range')

    # Start with the base query
    query = Card.query

    # Apply filters based on user input
    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))  # Filter by name

    if price_range:
        if price_range == '50+':
            query = query.filter(Card.buy_out_price > 50)  # Filter for cards over $50
        else:
            min_price, max_price = price_range.split('-')
            query = query.filter(Card.buy_out_price >= float(min_price))
            if max_price != '+':
                query = query.filter(Card.buy_out_price <= float(max_price))

    # Sort the query results by price (low to high)
    query = query.order_by(Card.buy_out_price.asc())

    # Paginate the results
    page = request.args.get('page', 1, type=int)
    cards = query.paginate(page=page, per_page=12)

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
            buy_out_price=form.buy_out_price.data,
            highest_bid=form.highest_bid.data,
            bidding_end_time=form.bidding_end_time.data,
            image_url=form.image_url.data,
            seller_id=current_user.id
        )
        db.session.add(card)
        db.session.commit()
        flash('Card listed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_card.html', form=form)

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

@app.route('/view_active_bids')
@login_required
def view_active_bids():
    # Query for the active bids for the current user
    active_bids = Card.query.filter(Card.highest_bidder_id == current_user.id).all()
    return render_template('active_bids.html', active_bids=active_bids)

@app.route('/finalize_bid/<int:card_id>', methods=['POST'])
@login_required
def finalize_bid(card_id):
    card = Card.query.get_or_404(card_id)

    # Ensure the current user is the highest bidder
    if card.highest_bidder_id != current_user.id:
        flash('You are not the highest bidder.', 'danger')
        return redirect(url_for('card_detail', card_id=card_id))

    # Implement payment processing logic here (if needed)
    # ...

    # Optionally, mark the card as sold or remove it from bidding
    db.session.delete(card)  # or update the card's status
    db.session.commit()
    flash('Bid finalized successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/remove_bid/<int:card_id>', methods=['POST'])
@login_required
def remove_bid(card_id):
    # Get the card and ensure the user is the highest bidder
    card = Card.query.get_or_404(card_id)

    # Find the bid associated with the current user
    bid = Bid.query.filter_by(card_id=card.id, user_id=current_user.id).first()

    if bid:
        # Ensure that the current user is the highest bidder
        if card.highest_bidder_id == current_user.id:
            # Delete the bid from the bids table
            db.session.delete(bid)  # Delete the bid
            card.highest_bidder_id = None  # Reset highest bidder
            card.highest_bid = None  # Reset highest bid
            db.session.commit()  # Commit the changes
            flash('Your bid has been removed.', 'success')
        else:
            flash('You cannot remove this bid.', 'danger')
    else:
        flash('You do not have an active bid on this card.', 'danger')

    return redirect(url_for('view_active_bids'))


@app.route('/my_listings', methods=['GET', 'POST'])
@login_required
def my_listings():
    cards = Card.query.filter_by(seller_id=current_user.id).all()  # Get the cards for the logged-in user
    return render_template('my_listings.html', cards=cards)

@app.route('/remove_listing/<int:card_id>', methods=['POST'])
@login_required
def remove_listing(card_id):
    # Check if the card is in any active bids
    active_bid = Bid.query.filter_by(card_id=card_id).first()  # Replace with your actual Bid model

    if active_bid:
        flash('Cannot remove the listing while there is an active bid.', 'danger')
        return redirect(url_for('my_listings'))

    # If not in active bids, proceed to remove the listing
    listing = Card.query.get(card_id)
    if listing:
        db.session.delete(listing)
        db.session.commit()
        flash('Listing removed successfully!', 'success')
    else:
        flash('Listing not found.', 'danger')

    print("Checking for active bids on card ID:", card_id)
    print("Active Bid Found:", active_bid)

    return redirect(url_for('my_listings'))

@app.route('/update_price/<int:card_id>', methods=['POST'])
@login_required
def update_price(card_id):
    # Check if the card is in any active bids
    active_bids = Bid.query.filter_by(card_id=card_id).first()  # Replace with your actual Bid model

    if active_bids:
        flash('Cannot update the price while there is an active bid.', 'danger')
        return redirect(url_for('my_listings'))

    # If not in active bids, proceed to update the price
    card = Card.query.get(card_id)
    if card:
        new_price = request.form.get('new_price')
        if new_price:
            card.buy_out_price = float(new_price)  # Update buy-out price
            db.session.commit()
            flash('Price updated successfully!', 'success')
        else:
            flash('Invalid price.', 'danger')
    else:
        flash('Card not found.', 'danger')

    return redirect(url_for('my_listings'))

@app.route('/card/<int:card_id>')
def card_detail(card_id):
    card = Card.query.get_or_404(card_id)
    return render_template('card_detail.html', card=card)

@app.route('/place_bid/<int:card_id>', methods=['POST'])
@login_required
def place_bid(card_id):
    card = Card.query.get_or_404(card_id)
    bid_amount = float(request.form.get('bid_amount', 0))

    # Check if the bid_amount is greater than the current highest bid
    if card.highest_bid is None or bid_amount > card.highest_bid:
        # Update the card's highest bid and highest bidder
        card.highest_bid = bid_amount
        card.highest_bidder_id = current_user.id  # Assuming the user is the highest bidder

        # Create a new bid entry
        new_bid = Bid(card_id=card.id, user_id=current_user.id, bid_amount=bid_amount)
        db.session.add(new_bid)

        db.session.commit()
        flash('Your bid has been placed successfully!', 'success')
    else:
        flash('Your bid must be higher than the current highest bid.', 'danger')

    return redirect(url_for('card_detail', card_id=card.id))
