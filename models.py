from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(256), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    cards = db.relationship('Card', backref='seller', lazy=True, foreign_keys='Card.seller_id')
    orders = db.relationship('Order', backref='buyer', lazy=True)
    bids = db.relationship('Bid', back_populates='bidder', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Card(db.Model):
    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    buy_out_price = db.Column(db.Float, nullable=False)
    highest_bid = db.Column(db.Float, nullable=True)
    highest_bidder_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bidding_end_time = db.Column(db.DateTime)
    image_url = db.Column(db.String(250), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=1)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    orders = db.relationship('Order', backref='card', lazy=True)
    highest_bidder = db.relationship('User', foreign_keys=[highest_bidder_id], backref='highest_bidder_cards')

    def __repr__(self):
        return f"<Card {self.name}>"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Order {self.id} by User {self.buyer_id}>"
    
class Bid(db.Model):
    __tablename__ = 'bids'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    bid_time = db.Column(db.DateTime, default=datetime.utcnow)

    card = db.relationship('Card', backref='bids')
    bidder = db.relationship('User', back_populates='bids')

    def __repr__(self):
        return f"<Bid {self.id} for Card {self.card_id} by User {self.user_id}>"
