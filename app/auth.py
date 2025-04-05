import json
import os
import bcrypt
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

# Path to users.json
USERS_FILE = 'app/data/users.json'

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
    return True

def login_user(username, password):
    """Login a user"""
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user and verify_password(password, user['password']):
        session['username'] = username
        return True
    return False

def logout_user():
    """Logout the current user"""
    session.clear()

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

def save_game_score(username, game_type, score, total=None):
    """Save a game score for a user"""
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user:
        if 'game_history' not in user:
            user['game_history'] = []
        
        # Add new score with timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add the new game
        new_game = {
            'game_type': game_type,
            'score': score,
            'total': total if total is not None else 100,  # Default to 100 if total not provided
            'date': current_time
        }
        
        # Add the new game
        user['game_history'].append(new_game)
        
        # Keep only the last 10 games
        if len(user['game_history']) > 10:
            user['game_history'] = user['game_history'][-10:]
        
        save_users(users)
        return True
    return False

def get_user_game_history(username):
    """Get the last 10 games for a user"""
    user = get_user(username)
    if user and 'game_history' in user:
        # Return all games (up to 10) in chronological order
        return user['game_history']
    return []

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function 