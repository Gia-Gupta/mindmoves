from flask import Flask
from flask_session import Session
import os

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flask_session')
    app.config['SESSION_FILE_THRESHOLD'] = 100
    app.config['USERS_FILE'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'data', 'users.json')
    app.config['DEBUG'] = False  # Add this line

    # Ensure session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

    # Initialize extensions
    Session(app)

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app