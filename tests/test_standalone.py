import pytest
from flask import session

def test_home_page_content(client):
    """Test the home page loads with correct content."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'MindMoves' in response.data
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
    assert b'Registration successful!' in response.data

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
        'username': 'derekstock',
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
    assert b'Username already exists' in response.data

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
    
    # 2. Test with existing username (derekstock)
    response = client.post('/forgot-password', data={
        'username': 'derekstock'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'What was your first pet' in response.data  # Secret question should be shown
    
    # 3. Test with wrong secret answer
    response = client.post('/forgot-password', data={
        'username': 'derekstock',
        'secret_answer': 'wrong_answer',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect secret answer' in response.data
    assert b'What was your first pet' in response.data  # Question should still be shown
    
    # 4. Test with missing new password
    response = client.post('/forgot-password', data={
        'username': 'derekstock',
        'secret_answer': 'wrong_answer'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data
    
    # 5. Test with missing secret answer
    response = client.post('/forgot-password', data={
        'username': 'derekstock',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data
    
    # 6. Test successful password reset
    response = client.post('/forgot-password', data={
        'username': 'derekstock',
        'secret_answer': 'test_answer',  # This should match your actual secret answer
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully' in response.data
    
    # 7. Verify can login with new password
    response = client.post('/login', data={
        'username': 'derekstock',
        'password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in' in response.data

def test_forgot_password_form_persistence(client):
    """Test that form data persists when showing errors."""
    # 1. Submit with wrong secret answer
    response = client.post('/forgot-password', data={
        'username': 'derekstock',
        'secret_answer': 'wrong_answer',
        'new_password': 'NewPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'value="derekstock"' in response.data  # Username should be preserved
    assert b'What was your first pet' in response.data  # Question should be shown 