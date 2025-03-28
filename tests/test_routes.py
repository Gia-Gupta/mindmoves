import pytest
from flask import url_for

def test_home_page(client):
    """Test home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'MindMoves' in response.data
    assert b'Train Your Brain' in response.data

def test_about_page(client):
    """Test about page loads correctly."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About MindMoves' in response.data

def test_game_pages(client):
    """Test all game pages load correctly."""
    game_routes = ['/typing', '/speed', '/dexterity', '/precision']
    for route in game_routes:
        response = client.get(route)
        assert response.status_code == 200
        assert b'MindMoves' in response.data

def test_profile_redirect_when_not_logged_in(client):
    """Test profile page redirects to login when not authenticated."""
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_profile_access_when_logged_in(logged_in_client):
    """Test profile page loads when authenticated."""
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Welcome' in response.data
    assert b'@testuser' in response.data

def test_login_form_submission(client, test_user):
    """Test login form submission."""
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

def test_register_form_submission(client):
    """Test registration form submission."""
    response = client.post('/register', data={
        'first_name': 'Test',
        'username': 'testuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data

def test_forgot_password_form_submission(client, test_user):
    """Test forgot password form submission."""
    response = client.post('/forgot-password', data={
        'username': test_user['username'],
        'secret_answer': test_user['secret_answer'],
        'new_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data

def test_navigation_links(client):
    """Test navigation links are present and working."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home' in response.data
    assert b'About' in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data

def test_navigation_links_when_logged_in(logged_in_client):
    """Test navigation links when user is logged in."""
    response = logged_in_client.get('/')
    assert response.status_code == 200
    assert b'Home' in response.data
    assert b'About' in response.data
    assert b'Logout' in response.data
    assert b'Profile' in response.data 