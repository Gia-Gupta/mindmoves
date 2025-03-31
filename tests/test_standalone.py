import pytest
from flask import session

def test_home_page_content(client):
    """Test the home page loads with correct content."""
    # Test when not logged in
    response = client.get('/')
    assert response.status_code == 200
    assert b'Brain Training Games' in response.data
    assert b'Welcome back' not in response.data
    
    # Test when logged in
    # First register a user
    register_data = {
        'first_name': 'Test',
        'username': 'testuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }
    client.post('/register', data=register_data, follow_redirects=True)
    
    # Login with the user
    login_data = {
        'username': 'testuser',
        'password': 'TestPass123!'
    }
    client.post('/login', data=login_data, follow_redirects=True)
    
    # Check home page with logged in user
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome back, Test!' in response.data
    assert b'Brain Training Games' not in response.data
    
    # Test other content that should always be present
    assert b'Train Your Brain' in response.data
    assert b'Speed Game' in response.data
    assert b'Precision Game' in response.data
    assert b'Dexterity Game' in response.data
    assert b'Typing Game' in response.data

def test_authentication_flow(client):
    """Test the complete authentication flow."""
    # 1. Register new user
    register_data = {
        'first_name': 'Test',
        'username': 'newuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }
    response = client.post('/register', data=register_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful! Please login.' in response.data

    # 2. Login with new user
    login_data = {
        'username': 'newuser',
        'password': 'TestPass123!'
    }
    response = client.post('/login', data=login_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

    # 3. Check navigation changes when logged in
    response = client.get('/')
    assert b'Logout' in response.data
    assert b'Login' not in response.data

    # 4. Access profile page
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'newuser' in response.data

    # 5. Logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged out!' in response.data
    assert b'Login' in response.data

def test_password_reset_flow(client):
    """Test the password reset functionality."""
    # 1. Try to reset with invalid username
    reset_data = {
        'username': 'nonexistent',
        'secret_answer': 'wrong',
        'new_password': 'NewPass123!'
    }
    response = client.post('/forgot-password', data=reset_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username not found' in response.data

    # 2. Reset with valid data
    reset_data = {
        'username': 'testuser',
        'secret_answer': 'blue',
        'new_password': 'NewPass123!'
    }
    response = client.post('/forgot-password', data=reset_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data

def test_game_access(client):
    """Test access to game pages."""
    game_routes = ['/typing', '/speed', '/precision', '/dexterity']
    for route in game_routes:
        response = client.get(route)
        assert response.status_code == 200
        assert b'MindMoves' in response.data

def test_error_handling(client):
    """Test error handling for invalid inputs."""
    # Test empty login
    response = client.post('/login', data={
        'username': '',
        'password': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # Test empty registration
    response = client.post('/register', data={
        'first_name': '',
        'username': '',
        'password': '',
        'secret_question': '',
        'secret_answer': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please fill in all fields' in response.data

    # Test invalid route
    response = client.get('/nonexistent')
    assert response.status_code == 404

def test_forgot_password_flow(client):
    """Test the complete forgot password flow."""
    # 1. Test with non-existent username
    response = client.post('/forgot-password', data={
        'username': 'nonexistent'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username not found' in response.data
    
    # 2. Test with existing username (testuser)
    response = client.post('/forgot-password', data={
        'username': 'testuser'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'What is your favorite color' in response.data
    
    # 3. Test with wrong secret answer
    response = client.post('/forgot-password', data={
        'username': 'testuser',
        'secret_answer': 'wrong_answer',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect secret answer' in response.data
    
    # 4. Test with missing new password
    response = client.post('/forgot-password', data={
        'username': 'testuser',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data
    
    # 5. Test with missing secret answer
    response = client.post('/forgot-password', data={
        'username': 'testuser',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data
    
    # 6. Test successful password reset
    response = client.post('/forgot-password', data={
        'username': 'testuser',
        'secret_answer': 'blue',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data
    
    # 7. Verify can login with new password
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in' in response.data

def test_forgot_password_form_persistence(client):
    """Test that form data persists when showing errors."""
    # 1. Submit with wrong secret answer
    response = client.post('/forgot-password', data={
        'username': 'testuser',
        'secret_answer': 'wrong_answer',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'value="testuser"' in response.data  # Username should be preserved
    assert b'What is your favorite color' in response.data  # Question should be shown

def test_registration_errors(client):
    """Test registration error handling."""
    # 1. Test empty fields
    response = client.post('/register', data={
        'first_name': '',
        'username': '',
        'password': '',
        'secret_question': '',
        'secret_answer': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please fill in all fields' in response.data
    
    # 2. Test duplicate username
    # First registration
    response = client.post('/register', data={
        'first_name': 'Test',
        'username': 'uniqueuser',
        'password': 'TestPass123!',
        'secret_question': 'What was your first pet\'s name?',
        'secret_answer': 'test'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful! Please login.' in response.data
    
    # Try to register with same username
    response = client.post('/register', data={
        'first_name': 'Test2',
        'username': 'uniqueuser',
        'password': 'TestPass123!',
        'secret_question': 'What was your first pet\'s name?',
        'secret_answer': 'test'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already exists' in response.data
    
    # Verify form data is preserved
    assert b'value="Test2"' in response.data  # First name should be preserved
    assert b'value="uniqueuser"' in response.data  # Username should be preserved
    assert b'selected' in response.data  # Secret question should be selected
    
    # Verify flash message container exists
    assert b'flash-messages' in response.data
    assert b'flash-message error' in response.data
    
    # Verify JavaScript for auto-hide is present
    assert b'setTimeout(function()' in response.data
    assert b'3000' in response.data  # Check for 3 second timeout
    assert b'opacity = \'0\'' in response.data  # Check for fade out
    assert b'transform = \'translateY(-100%)\'' in response.data  # Check for slide up 

def test_game_history(client):
    """Test game history functionality."""
    # 1. Register and login a user
    register_data = {
        'first_name': 'Test',
        'username': 'gameuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }
    client.post('/register', data=register_data, follow_redirects=True)
    
    login_data = {
        'username': 'gameuser',
        'password': 'TestPass123!'
    }
    client.post('/login', data=login_data, follow_redirects=True)
    
    # 2. Check initial profile page (no games)
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'No games played yet' in response.data
    
    # 3. Save some game scores
    from app.auth import save_game_score
    save_game_score('gameuser', 'Speed Game', 100)
    save_game_score('gameuser', 'Precision Game', 85)
    save_game_score('gameuser', 'Typing Game', 120)
    
    # 4. Check profile page with game history
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'Recent Game History' in response.data
    assert b'Speed Game' in response.data
    assert b'Precision Game' in response.data
    assert b'Typing Game' in response.data
    assert b'100' in response.data
    assert b'85' in response.data
    assert b'120' in response.data
    
    # 5. Verify only last 10 games are shown
    for i in range(12):
        save_game_score('gameuser', f'Game {i}', i * 10)
    
    response = client.get('/profile')
    assert response.status_code == 200
    # Should only show games 2-11 (last 10)
    assert b'Game 2' in response.data
    assert b'Game 11' in response.data
    assert b'Game 0' not in response.data
    assert b'Game 1' not in response.data 