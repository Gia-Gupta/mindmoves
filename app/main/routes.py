from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.main import bp
from app.auth import register_user, login_user, logout_user, verify_secret_answer, update_user_password, get_user, login_required, get_user_game_history, verify_password, save_game_score
import json
from datetime import datetime

@bp.route("/")
def index():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'WordNinja.jpg')
    return render_template("index.html", user=user)

@bp.route("/about")
def about():
    user = None
    if session.get('username'):
        try:
            with open('app/data/users.json', 'r') as f:
                data = json.load(f)
                users = data['users']
                user = next((user for user in users if user['username'] == session.get('username')), None)
                if user:
                    user['avatar'] = user.get('avatar', 'WordNinja.jpg')
        except FileNotFoundError:
            pass
    return render_template('about.html', user=user)

@bp.route("/history")
@login_required
def history():
    username = session.get('username')
    try:
        with open('app/data/users.json', 'r') as f:
            data = json.load(f)
            users = data['users']
            user = next((user for user in users if user['username'] == username), None)
            if user:
                game_history = user.get('game_history', [])
                user['avatar'] = user.get('avatar', 'wordNinja.jpg')
                return render_template('history.html', user=user, game_history=game_history)
    except FileNotFoundError:
        flash('Error loading user data', 'error')
    return redirect(url_for('main.index'))

@bp.route("/typing")
def typing():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'wordNinja.jpg')
    return render_template("typing.html", user=user)

@bp.route("/speed")
def speed():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'wordNinja.jpg')
    return render_template("speed.html", user=user)

@bp.route("/dexterity")
def dexterity():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'wordNinja.jpg')
    return render_template("dexterity.html", user=user)

@bp.route("/precision")
def precision():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'wordNinja.jpg')
    return render_template("precision.html", user=user)

@bp.route("/balance")
def balance():
    user = None
    if session.get('username'):
        user = get_user(session['username'])
        if user:
            user['avatar'] = user.get('avatar', 'wordNinja.jpg')
    return render_template("balance.html", user=user)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if login_user(username, password):
            flash('Successfully logged in!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        username = request.form.get('username')
        password = request.form.get('password')
        secret_question = request.form.get('secret_question')
        secret_answer = request.form.get('secret_answer')
        
        if not all([first_name, username, password, secret_question, secret_answer]):
            flash('Please fill in all fields', 'error')
            return render_template('auth/register.html',
                                first_name=first_name,
                                username=username,
                                secret_question=secret_question)
        
        # Check if username exists before attempting registration
        if get_user(username):
            flash('Username already exists', 'error')
            return render_template('auth/register.html',
                                first_name=first_name,
                                username=username,
                                secret_question=secret_question)
        
        if register_user(first_name, username, password, secret_question, secret_answer):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        
        # If registration failed for any other reason, preserve form data
        return render_template('auth/register.html',
                            first_name=first_name,
                            username=username,
                            secret_question=secret_question)
    
    return render_template('auth/register.html')

@bp.route("/logout")
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    session.clear()
    return redirect(url_for('main.index'))

@bp.route("/forgot-password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        secret_answer = request.form.get('secret_answer')
        new_password = request.form.get('new_password')
        
        # First step: username submission
        if not secret_answer and not new_password:
            user = get_user(username)
            if user:
                return render_template('auth/forgot_password.html', 
                                    secret_question=user['secret_question'],
                                    username=username)
            else:
                flash('Username not found', 'error')
                return render_template('auth/forgot_password.html', username=username)
        
        # Second step: password reset
        if secret_answer and new_password:
            user = get_user(username)
            if not user:
                flash('Username not found', 'error')
                return render_template('auth/forgot_password.html', username=username)
                
            is_valid, message = verify_secret_answer(username, secret_answer)
            if is_valid:
                if update_user_password(username, new_password):
                    flash('Password updated successfully!', 'success')
                    return redirect(url_for('main.login'))
                else:
                    flash('Failed to update password', 'error')
                    return render_template('auth/forgot_password.html', 
                                        secret_question=user['secret_question'],
                                        username=username)
            else:
                flash('Incorrect secret answer', 'error')
                return render_template('auth/forgot_password.html', 
                                    secret_question=user['secret_question'],
                                    username=username)
        else:
            flash('Please provide all required information', 'error')
            if username:
                user = get_user(username)
                if user:
                    return render_template('auth/forgot_password.html',
                                        secret_question=user['secret_question'],
                                        username=username)
    
    return render_template('auth/forgot_password.html')

@bp.route("/profile")
@login_required
def profile():
    username = session.get('username')
    user = get_user(username)
    if user:
        game_history = user.get('game_history', [])
        user['avatar'] = user.get('avatar', 'WordNinja.jpg')  # Default to WordNinja if no avatar set
        return render_template('profile.html', user=user, game_history=game_history)
    else:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))

@bp.route("/save_score", methods=['POST'])
def save_score():
    if not session.get('username'):
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()
    game_type = data.get('game_type')
    score = data.get('score')
    total = data.get('total')

    if not all([game_type, score is not None, total is not None]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        with open('app/data/users.json', 'r') as f:
            data = json.load(f)
            users = data['users']
    except FileNotFoundError:
        return jsonify({'error': 'Users file not found'}), 500

    username = session.get('username')
    user = next((user for user in users if user['username'] == username), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    score_data = {
        'game_type': game_type,
        'score': score,
        'total': total,
        'date': current_time  # Using 'date' to be consistent with existing records
    }

    if 'game_history' not in user:
        user['game_history'] = []
    user['game_history'].append(score_data)

    try:
        with open('app/data/users.json', 'w') as f:
            json.dump({'users': users}, f, indent=4)
        return jsonify({'message': 'Score saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route("/update_avatar", methods=['POST'])
def update_avatar():
    if not session.get('username'):
        return jsonify({'error': 'User not logged in'}), 401

    data = request.get_json()
    avatar_name = data.get('avatar_name')

    if not avatar_name:
        return jsonify({'error': 'Avatar name is required'}), 400

    try:
        with open('app/data/users.json', 'r') as f:
            data = json.load(f)
            users = data['users']
    except FileNotFoundError:
        return jsonify({'error': 'Users file not found'}), 500

    username = session.get('username')
    user_found = False
    
    # Find and update the user in the array
    for user in users:
        if user['username'] == username:
            user['avatar'] = avatar_name
            user_found = True
            break

    if not user_found:
        return jsonify({'error': 'User not found'}), 404

    try:
        with open('app/data/users.json', 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify({'message': 'Avatar updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 