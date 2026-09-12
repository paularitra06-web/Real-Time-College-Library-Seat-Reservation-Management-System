from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    reservations = db.relationship('Reservation', backref='user', lazy=True)

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    floor = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False) # cubicle, circular, rectangular
    label = db.Column(db.String(50), nullable=False)
    reservations = db.relationship('Reservation', backref='seat', lazy=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False)
    date = db.Column(db.Date, nullable=False) # e.g. 2026-09-05
    start_time = db.Column(db.Integer, nullable=False) # hour e.g. 7, 8, 9... up to 24
    end_time = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Booked') # Booked, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
