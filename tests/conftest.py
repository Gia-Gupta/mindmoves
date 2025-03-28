import pytest
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    from app import create_app
    
    # Create a temporary directory for test data
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test users.json file with initial test user
        test_users_file = os.path.join(temp_dir, 'users.json')
        initial_user = {
            'username': 'testuser',
            'password': 'pbkdf2:sha256:260000$test_hash',  # Pre-hashed test password
            'first_name': 'Test',
            'secret_question': 'What is your favorite color?',
            'secret_answer': 'pbkdf2:sha256:260000$test_answer_hash',  # Pre-hashed answer
            'registration_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'game_history': [],
            'high_scores': {}
        }
        with open(test_users_file, 'w') as f:
            json.dump({'users': [initial_user]}, f)
            
        # Mock environment variables and paths
        with patch.dict('os.environ', {'SECRET_KEY': 'test_key'}):
            with patch('app.auth.USERS_FILE', test_users_file):
                app = create_app()
                app.config.update({
                    'TESTING': True,
                    'WTF_CSRF_ENABLED': False,
                    'SESSION_TYPE': 'filesystem',
                    'USERS_FILE': test_users_file,
                    'SECRET_KEY': 'test_key'
                })
                
                yield app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def test_user():
    """Create test user credentials."""
    return {
        'username': 'testuser',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }

@pytest.fixture
def logged_in_client(client, test_user):
    """Create a test client with a logged-in user."""
    with client.session_transaction() as sess:
        sess['user'] = test_user['username']
    return client

@pytest.fixture
def mock_session():
    """Create a mock session for testing."""
    session = MagicMock()
    session.get.return_value = None
    return session 