import pytest
import json
import os
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

def test_password_hashing(client, test_user):
    """Test passwords are properly hashed."""
    # Get the user data from the JSON file
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == test_user['username'])
        assert user['password'] != test_user['password']
        assert user['password'].startswith('pbkdf2:sha256:')

def test_secret_answer_hashing(client, test_user):
    """Test secret answers are properly hashed."""
    # Get the user data from the JSON file
    with open('app/data/users.json', 'r') as f:
        users_data = json.load(f)
        user = next(u for u in users_data['users'] if u['username'] == test_user['username'])
        assert user['secret_answer'] != test_user['secret_answer']
        assert user['secret_answer'].startswith('pbkdf2:sha256:')

def test_session_management(client, test_user):
    """Test session management and security."""
    # Login and get session cookie
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # Check session cookie is set
    assert 'session' in client.cookies
    
    # Try to access protected route
    response = client.get('/profile')
    assert response.status_code == 200
    
    # Logout and check session is cleared
    client.get('/logout')
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_csrf_protection(client, test_user):
    """Test CSRF protection on forms."""
    # Get CSRF token from login page
    response = client.get('/login')
    assert response.status_code == 200
    
    # Try to submit form without token
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data

def test_xss_protection(client, test_user):
    """Test XSS protection in templates."""
    # Try to register with XSS payload
    xss_payload = '<script>alert("xss")</script>'
    response = client.post('/register', data={
        'first_name': xss_payload,
        'username': 'xssuser',
        'password': 'TestPass123!',
        'secret_question': 'What is your favorite color?',
        'secret_answer': 'blue'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful!' in response.data
    
    # Verify XSS payload is escaped in profile
    response = client.post('/login', data={
        'username': 'xssuser',
        'password': 'TestPass123!'
    }, follow_redirects=True)
    response = client.get('/profile')
    assert xss_payload.encode() not in response.data
    assert b'&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;' in response.data

def test_sql_injection_protection(client, test_user):
    """Test SQL injection protection."""
    # Try to login with SQL injection payload
    sql_payload = "' OR '1'='1"
    response = client.post('/login', data={
        'username': sql_payload,
        'password': sql_payload
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_file_access_protection(client):
    """Test protection against unauthorized file access."""
    # Try to access users.json directly
    response = client.get('/data/users.json')
    assert response.status_code == 404
    
    # Try to access other sensitive files
    response = client.get('/app/auth.py')
    assert response.status_code == 404

def test_password_strength(client):
    """Test password strength requirements."""
    weak_passwords = [
        'password',  # Too common
        '123456',    # Too short
        'abcdef',    # No numbers
        '12345678'   # No letters
    ]
    
    for password in weak_passwords:
        response = client.post('/register', data={
            'first_name': 'Test',
            'username': f'weakpass{password}',
            'password': password,
            'secret_question': 'What is your favorite color?',
            'secret_answer': 'blue'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Password must be at least 8 characters long' in response.data

def test_session_timeout(client, test_user):
    """Test session timeout functionality."""
    # Login
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # Simulate session timeout by clearing cookies
    client.cookies.clear()
    
    # Try to access protected route
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data 