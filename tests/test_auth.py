import pytest
from flask import url_for
from app.auth import verify_password, verify_secret_answer

def test_registration_success(client):
    """Test successful user registration."""
    response = client.post('/register', data={
        'first_name': 'Test',
        'username': 'testuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data

def test_registration_existing_username(client, test_user):
    """Test registration with existing username."""
    response = client.post('/register', data={
        'first_name': 'Test',
        'username': test_user['username'],
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_registration_missing_fields(client):
    """Test registration with missing fields."""
    response = client.post('/register', data={
        'first_name': 'Test',
        'username': 'testuser',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Please provide all required information' in response.data

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(client, test_user):
    """Test logout functionality."""
    # First login
    client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    })
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged out!' in response.data

def test_password_reset_success(client, test_user):
    """Test successful password reset."""
    response = client.post('/forgot-password', data={
        'username': test_user['username'],
        'secret_answer': test_user['secret_answer'],
        'new_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Password updated successfully!' in response.data

def test_password_reset_wrong_answer(client, test_user):
    """Test password reset with wrong secret answer."""
    response = client.post('/forgot-password', data={
        'username': test_user['username'],
        'secret_answer': 'wronganswer',
        'new_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect secret answer' in response.data

def test_password_reset_nonexistent_user(client):
    """Test password reset with nonexistent user."""
    response = client.post('/forgot-password', data={
        'username': 'nonexistent',
        'secret_answer': 'blue',
        'new_password': 'NewPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Incorrect secret answer' in response.data 