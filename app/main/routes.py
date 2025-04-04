from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.main import bp
from app.auth import register_user, login_user, logout_user, verify_secret_answer, update_user_password, get_user, login_required, get_user_game_history, verify_password, save_game_score

@bp.route("/")
def index():
    user = None
    if 'username' in session:
        user = get_user(session['username'])
    return render_template("index.html", user=user)

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/history")
def history():
    return render_template('history.html')

@bp.route("/typing")
def typing():
    return render_template("typing.html")

@bp.route("/speed")
def speed():
    return render_template("speed.html")

@bp.route("/dexterity")
def dexterity():
    return render_template("dexterity.html")

@bp.route("/precision")
def precision():
    username = session.get('username') if session.get('username') else None
    return render_template("precision.html", username=username)

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
    game_history = get_user_game_history(username)
    return render_template('profile.html', user=user, game_history=game_history)

@bp.route("/save_score", methods=['POST'])
@login_required
def save_score():
    data = request.get_json()
    username = session.get('username')
    
    if username and data:
        game_type = data.get('game_type')
        score = data.get('score')
        total = data.get('total')
        
        if game_type and score is not None and total is not None:
            # Calculate percentage for the score
            percentage = (score / total) * 100
            # Save the score with the percentage
            save_game_score(username, game_type, percentage)
            return jsonify({'status': 'success'})
    
    return jsonify({'status': 'error'}), 400 