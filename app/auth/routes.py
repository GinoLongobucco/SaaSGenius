from flask import request, jsonify, render_template
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.auth import bp
from app.database import db, User, log_analytics_event
from datetime import datetime
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial"
    return True, "Password is valid"

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Validation
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters long'}), 400
    
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Invalid email format'}), 400
    
    is_valid, password_message = validate_password(password)
    if not is_valid:
        return jsonify({'success': False, 'message': password_message}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Create user
    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Log registration event
    log_analytics_event(
        new_user.id, 
        'user_registered', 
        {'username': new_user.username, 'email': new_user.email},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    # Auto-login after registration
    login_user(new_user, remember=True)
    
    return jsonify({
        'success': True, 
        'message': 'Registration successful',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    })

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json()
    username_or_email = data.get('username', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not username_or_email or not password:
        return jsonify({'success': False, 'message': 'Username/email and password are required'}), 400
    
    # Find user by username or email using SQLAlchemy
    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Update last login using SQLAlchemy
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log login event
    log_analytics_event(
        user.id, 
        'user_login', 
        {'username': user.username},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    login_user(user, remember=remember)
    
    return jsonify({
        'success': True, 
        'message': 'Login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'subscription_type': user.subscription_type
        }
    })

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    user_id = current_user.id
    username = current_user.username
    
    logout_user()
    
    # Log logout event
    log_analytics_event(
        user_id, 
        'user_logout', 
        {'username': username},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    if request.method == 'GET':
        # Redirect to login page for GET requests
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'subscription_type': current_user.subscription_type,
            'is_premium': current_user.is_premium()
        }
    })

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    # Validate new password
    is_valid, password_message = validate_password(new_password)
    if not is_valid:
        return jsonify({'success': False, 'message': password_message}), 400

    # Update password
    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    # Log password change event
    log_analytics_event(
        current_user.id,
        'password_changed',
        {'username': current_user.username},
        request.remote_addr,
        request.headers.get('User-Agent')
    )

    return jsonify({'success': True, 'message': 'Password changed successfully'})

@bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login with a test user"""
    # Find or create demo user
    demo_user = User.query.filter_by(username='demo').first()
    
    if not demo_user:
        # Create demo user if it doesn't exist
        password_hash = generate_password_hash('demo123')
        demo_user = User(
            username='demo',
            email='demo@saasgenius.com',
            password_hash=password_hash,
            subscription_type='premium'  # Give demo user premium access
        )
        db.session.add(demo_user)
        db.session.commit()
    
    # Update last login
    demo_user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Log demo login event
    log_analytics_event(
        demo_user.id,
        'demo_login',
        {'username': demo_user.username},
        request.remote_addr,
        request.headers.get('User-Agent')
    )
    
    login_user(demo_user, remember=False)
    
    return jsonify({
        'success': True,
        'message': 'Demo login successful',
        'user': {
            'id': demo_user.id,
            'username': demo_user.username,
            'email': demo_user.email,
            'subscription_type': demo_user.subscription_type
        }
    })