import pytest
from datetime import datetime
import json
import os

def test_user_data_persistence(client, app):
    """Test user data is properly persisted."""
    # Register a new user
    user_data = {
        'first_name': 'Data',
        'username': 'datauser',
        'password': 'DataTest123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'red'
    }
    response = client.post('/register', data=user_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify user data was saved
    users_file = app.config['USERS_FILE']
    assert os.path.exists(users_file)
    
    with open(users_file, 'r') as f:
        users_data = json.load(f)
        user = next((u for u in users_data['users'] if u['username'] == 'datauser'), None)
        assert user is not None
        assert user['first_name'] == 'Data'
        assert 'password' in user  # Password should be hashed
        assert 'secret_answer' in user  # Secret answer should be hashed
        assert 'game_history' in user
        assert isinstance(user['game_history'], list)

def test_game_history_recording(client, app):
    """Test game history is properly recorded."""
    # First login
    login_data = {
        'username': 'derekstock',
        'password': 'TestPass123!'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Simulate playing a game
    game_data = {
        'game_type': 'memory',
        'score': 100,
        'duration': 60
    }
    response = client.post('/game/memory/complete', data=game_data, follow_redirects=True)
    assert response.status_code == 200
    
    # Verify game history was updated
    users_file = app.config['USERS_FILE']
    with open(users_file, 'r') as f:
        users_data = json.load(f)
        user = next((u for u in users_data['users'] if u['username'] == 'derekstock'), None)
        assert user is not None
        assert len(user['game_history']) > 0
        latest_game = user['game_history'][0]
        assert latest_game['game_type'] == 'memory'
        assert latest_game['score'] == 100
        assert latest_game['duration'] == 60

def test_data_integrity(client, app):
    """Test data integrity and format."""
    users_file = app.config['USERS_FILE']
    with open(users_file, 'r') as f:
        users_data = json.load(f)
        assert 'users' in users_data
        assert isinstance(users_data['users'], list)
        
        for user in users_data['users']:
            assert 'username' in user
            assert 'password' in user
            assert 'first_name' in user
            assert 'secret_question' in user
            assert 'secret_answer' in user
            assert 'registration_date' in user
            assert 'game_history' in user
            assert 'high_scores' in user
            
            # Verify data types
            assert isinstance(user['username'], str)
            assert isinstance(user['password'], str)
            assert isinstance(user['first_name'], str)
            assert isinstance(user['secret_question'], str)
            assert isinstance(user['secret_answer'], str)
            assert isinstance(user['registration_date'], str)
            assert isinstance(user['game_history'], list)
            assert isinstance(user['high_scores'], dict) 