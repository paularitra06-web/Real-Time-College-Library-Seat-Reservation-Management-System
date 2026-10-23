from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, time, timedelta
from . import db
from .models import User, Seat, Reservation

main = Blueprint('main', __name__)

from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_and_expire_reservations():
    """
    Auto-expires reservations:
    Each booking session is valid up to 12:30 AM of that night (library closing).
    Once past 12:30 AM, any remaining 'Booked' reservation is automatically updated to 'Expired'.
    """
    now = datetime.now()
    active_reservations = Reservation.query.filter_by(status='Booked').all()
    changed = False
    for r in active_reservations:
        # Expiry timestamp is 12:30 AM of the next morning (r.date + 1 day at 00:30:00)
        expiry_dt = datetime.combine(r.date + timedelta(days=1), datetime.min.time()) + timedelta(minutes=30)
        if now >= expiry_dt:
            r.status = 'Expired'
            changed = True
    if changed:
        db.session.commit()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        reg_no = request.form.get('reg_no')
        password = request.form.get('password')
        
        user = User.query.filter_by(reg_no=reg_no).first()
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return redirect(url_for('main.login'))
        
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        reg_no = request.form.get('reg_no')
        name = request.form.get('name')
        password = request.form.get('password')
        
        user = User.query.filter_by(reg_no=reg_no).first()
        if user:
            flash('Registration number already exists.')
            return redirect(url_for('main.register'))
        
        new_user = User(reg_no=reg_no, name=name, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/api/seats', methods=['GET'])
@login_required
def get_seats():
    # Automatically expire any past sessions before querying
    check_and_expire_reservations()
    
    floor = request.args.get('floor', 1, type=int)
    booking_date_str = request.args.get('date', date.today().isoformat())
    start_hour = request.args.get('time', 7, type=int)

    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    seats = Seat.query.filter_by(floor=floor).all()
    
    # Get all active reservations for this floor, date and time
    reservations = Reservation.query.filter_by(date=booking_date, status='Booked').filter(
        Reservation.start_time <= start_hour,
        Reservation.end_time > start_hour
    ).all()
    
    booked_seat_ids = [r.seat_id for r in reservations]
    
    seat_data = []
    for s in seats:
        seat_data.append({
            'id': s.id,
            'label': s.label,
            'type': s.type,
            'is_booked': s.id in booked_seat_ids
        })
        
    return jsonify({'seats': seat_data})

@main.route('/api/active-booking', methods=['GET'])
@login_required
def get_active_booking():
    """
    Returns the user's active booking for today along with remaining time until 12:30 AM closing.
    """
    check_and_expire_reservations()
    now = datetime.now()
    
    # Get current user's latest booking that is still active ('Booked')
    active = Reservation.query.filter_by(
        user_id=current_user.id,
        status='Booked'
    ).order_by(Reservation.date.desc(), Reservation.start_time.desc()).first()
    
    if not active:
        return jsonify({'has_active': False})
        
    # Expiry is 12:30 AM of the next morning following the reservation date
    expiry_dt = datetime.combine(active.date + timedelta(days=1), datetime.min.time()) + timedelta(minutes=30)
    remaining_seconds = int((expiry_dt - now).total_seconds())
    
    if remaining_seconds <= 0:
        active.status = 'Expired'
        db.session.commit()
        return jsonify({'has_active': False})
        
    return jsonify({
        'has_active': True,
        'id': active.id,
        'seat_label': active.seat.label,
        'seat_type': active.seat.type.capitalize(),
        'floor': active.seat.floor,
        'date': active.date.strftime('%Y-%m-%d'),
        'slot': f"{active.start_time:02d}:00 - {active.end_time:02d}:00",
        'closing_time': '12:30 AM',
        'expiry_iso': expiry_dt.isoformat(),
        'remaining_seconds': remaining_seconds
    })

@main.route('/api/book', methods=['POST'])
@login_required
def book_seat():
    check_and_expire_reservations()
    
    data = request.json
    seat_id = data.get('seat_id')
    booking_date_str = data.get('date')
    start_hour = data.get('start_time')
    
    if not all([seat_id, booking_date_str, start_hour]):
        return jsonify({'error': 'Missing data'}), 400
        
    try:
        booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    now = datetime.now()
    
    # Rules: Book only for today, from 7:00 AM onwards
    if booking_date != now.date():
        return jsonify({'error': 'You can only book seats for today.'}), 400
        
    if now.hour < 7:
        return jsonify({'error': 'Booking opens at 7:00 AM.'}), 400
        
    if start_hour < 7 or start_hour >= 24:
        return jsonify({'error': 'Invalid time slot.'}), 400
        
    # Check if seat already booked
    existing = Reservation.query.filter_by(seat_id=seat_id, date=booking_date, status='Booked').filter(
        Reservation.start_time <= start_hour,
        Reservation.end_time > start_hour
    ).first()
    
    if existing:
        return jsonify({'error': 'Seat is already booked for this time.'}), 400
        
    # Create reservation
    new_res = Reservation(
        user_id=current_user.id,
        seat_id=seat_id,
        date=booking_date,
        start_time=start_hour,
        end_time=start_hour + 1
    )
    db.session.add(new_res)
    db.session.commit()
    
    return jsonify({'message': 'Seat booked successfully!'})

@main.route('/history')
@login_required
def history():
    check_and_expire_reservations()
    reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).order_by(Reservation.date.desc(), Reservation.start_time.desc()).all()
    return render_template('history.html', reservations=reservations)

@main.route('/helpline')
@login_required
def helpline():
    return render_template('helpline.html')
