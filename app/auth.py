import json
import os
import bcrypt
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

# Path to users.json
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'data', 'users.json')

def load_users():
    """Load users from JSON file"""
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)['users']
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_users(users):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump({'users': users}, f, indent=4)

def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user(first_name, username, password, secret_question, secret_answer):
    """Register a new user"""
    users = load_users()
    
    # Check if username already exists
    if any(user['username'] == username for user in users):
        flash('Username already exists', 'error')
        return False
    
    # Create new user
    new_user = {
        'first_name': first_name,
        'username': username,
        'password': hash_password(password),
        'secret_question': secret_question,
        'secret_answer': hash_password(secret_answer),
        'game_history': []
    }
    
    users.append(new_user)
    save_users(users)
    flash('Registration successful! Please login.', 'success')
    return True

def login_user(username, password):
    """Login a user"""
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user and verify_password(password, user['password']):
        session['user'] = username
        return True
    return False

def logout_user():
    """Logout the current user"""
    session.pop('user', None)

def get_user(username):
    """Get user data by username"""
    users = load_users()
    return next((user for user in users if user['username'] == username), None)

def update_user_password(username, new_password):
    """Update user's password"""
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user:
        user['password'] = hash_password(new_password)
        save_users(users)
        return True, "Password updated successfully"
    
    return False, "User not found"

def verify_secret_answer(username, secret_answer):
    """Verify user's secret answer"""
    user = get_user(username)
    if user and verify_password(secret_answer, user['secret_answer']):
        return True, "Secret answer verified"
    return False, "Invalid secret answer"

def save_game_score(username, game_type, score_data):
    """Save a game score for a user"""
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user:
        score_data['date'] = datetime.now().strftime("%Y-%m-%d")
        user['game_history'].append(score_data)
        save_users(users)
        return True, "Score saved successfully"
    
    return False, "User not found"

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function 