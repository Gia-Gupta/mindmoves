import pytest
from datetime import datetime

def test_complete_user_flow(client, test_user):
    """Test complete user flow from registration to profile."""
    # 1. Register new user
    response = client.post('/register', data={
        'first_name': 'Integration',
        'username': 'integrationuser',
        'password': 'IntegrationTest123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    # 2. Login with new user
    response = client.post('/login', data={
        'username': 'integrationuser',
        'password': 'IntegrationTest123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # 3. Access profile
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'Profile' in response.data
    assert b'integrationuser' in response.data
    
    # 4. Play a game
    response = client.get('/typing')
    assert response.status_code == 200
    assert b'Typing Game' in response.data
    
    # 5. Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged out!' in response.data

def test_password_reset_flow(client, test_user):
    """Test complete password reset flow."""
    # 1. Request password reset
    response = client.get('/forgot-password')
    assert response.status_code == 200
    assert b'Forgot Password' in response.data
    
    # 2. Submit reset form
    response = client.post('/forgot-password', data={
        'username': test_user['username'],
        'secret_answer': test_user['secret_answer'],
        'new_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data
    
    # 3. Login with new password
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

def test_game_integration(client, test_user):
    """Test game integration with user profile."""
    # 1. Login
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # 2. Access game
    response = client.get('/typing')
    assert response.status_code == 200
    assert b'Typing Game' in response.data
    
    # 3. Check profile for game history
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'Game History' in response.data

def test_error_handling(client):
    """Test error handling across the application."""
    # 1. Test invalid route
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    # 2. Test invalid form submission
    response = client.post('/login', data={
        'username': '',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # 3. Test invalid registration
    response = client.post('/register', data={
        'first_name': '',
        'username': '',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data

def test_concurrent_game_sessions(client, test_user):
    """Test handling of concurrent game sessions."""
    # 1. Login
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # 2. Start multiple games
    games = ['/typing', '/speed', '/dexterity', '/precision']
    for game in games:
        response = client.get(game)
        assert response.status_code == 200
    
    # 3. Check profile for all games
    response = client.get('/profile')
    assert response.status_code == 200
    for game in games:
        assert game[1:].title() in response.data.decode()

def test_data_persistence(client, test_user):
    """Test data persistence across sessions."""
    # 1. Login and save game data
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # 2. Play a game
    response = client.get('/typing')
    assert response.status_code == 200
    
    # 3. Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    
    # 4. Login again and check data
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'Game History' in response.data 