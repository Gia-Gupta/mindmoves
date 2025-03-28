import pytest
import json
from datetime import datetime

def test_user_data_storage(app, test_user):
    """Test user data is saved correctly in users.json."""
    # Read the test users file
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == test_user['username'])
        assert user['first_name'] == test_user['first_name']
        assert user['username'] == test_user['username']
        assert user['secret_question'] == test_user['secret_question']
        assert user['password'].startswith('pbkdf2:sha256:')
        assert user['secret_answer'].startswith('pbkdf2:sha256:')
        assert 'registration_date' in user
        assert 'game_history' in user
        assert 'high_scores' in user

def test_game_history_saving(app, logged_in_client):
    """Test game history is saved correctly."""
    # Simulate playing a game
    game_data = {
        'name': 'Test Game',
        'score': 85,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'icon': 'gamepad'
    }
    
    # Add game to history
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == 'testuser')
        user['game_history'].append(game_data)
    
    with open('app/data/users.json', 'w') as f:
        json.dump(users_data, f)
    
    # Check profile shows game history
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Test Game' in response.data
    assert b'85' in response.data

def test_game_history_limit(app, logged_in_client):
    """Test game history is limited to recent games."""
    # Add multiple games to history
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == 'testuser')
        
        # Add 15 games
        for i in range(15):
            game_data = {
                'name': f'Game {i}',
                'score': 80 + i,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'icon': 'gamepad'
            }
            user['game_history'].append(game_data)
    
    with open('app/data/users.json', 'w') as f:
        json.dump(users_data, f)
    
    # Check profile shows only recent games
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Game 14' in response.data  # Most recent game
    assert b'Game 0' not in response.data  # Oldest game

def test_high_scores(app, logged_in_client):
    """Test high scores are updated correctly."""
    # Add a high score
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == 'testuser')
        user['high_scores']['typing'] = {
            'score': 100,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    with open('app/data/users.json', 'w') as f:
        json.dump(users_data, f)
    
    # Check profile shows high score
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'100' in response.data
    assert b'typing' in response.data

def test_high_scores_persistence(app, logged_in_client):
    """Test high scores persist between sessions."""
    # Add initial high score
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == 'testuser')
        user['high_scores']['typing'] = {
            'score': 100,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    with open('app/data/users.json', 'w') as f:
        json.dump(users_data, f)
    
    # Simulate new session
    logged_in_client.get('/logout')
    logged_in_client.post('/login', data={
        'username': 'testuser',
        'password': 'TestPass123!'
    })
    
    # Check high score persists
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'100' in response.data
    assert b'typing' in response.data 