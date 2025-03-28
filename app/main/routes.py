from flask import render_template, request, redirect, url_for, flash, session
from app.main import bp
from app.auth import register_user, login_user, logout_user, verify_secret_answer, update_user_password, get_user, login_required

@bp.route("/")
def home():
    return render_template("index.html")

@bp.route("/about")
def about():
    return render_template("about.html")

@bp.route("/gameView")
def gameView():
    return render_template("gameView.html")

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
    return render_template("precision.html")

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if login_user(username, password):
            flash('Successfully logged in!', 'success')
            return redirect(url_for('main.home'))
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
        
        if register_user(first_name, username, password, secret_question, secret_answer):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        else:
            flash('Username already exists', 'error')
    
    return render_template('auth/register.html')

@bp.route("/logout")
def logout():
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('main.home'))

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
    username = session.get('user')
    user = get_user(username)
    if user:
        return render_template('user/profile.html', user=user)
    return redirect(url_for('main.login')) 