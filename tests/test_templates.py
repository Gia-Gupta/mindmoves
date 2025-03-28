import pytest

def test_home_template(client):
    """Test home template renders correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'MindMoves' in response.data
    assert b'Brain Training Games' in response.data

def test_login_template(client):
    """Test login template renders correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data

def test_register_template(client):
    """Test register template renders correctly."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    assert b'First Name' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data

def test_forgot_password_template(client):
    """Test forgot password template renders correctly."""
    response = client.get('/forgot-password')
    assert response.status_code == 200
    assert b'Forgot Password' in response.data
    assert b'Username' in response.data
    assert b'Secret Answer' in response.data
    assert b'New Password' in response.data

def test_profile_template(logged_in_client):
    """Test profile template renders correctly when logged in."""
    response = logged_in_client.get('/profile')
    assert response.status_code == 200
    assert b'Profile' in response.data
    assert b'Game History' in response.data
    assert b'High Scores' in response.data

def test_flash_messages(client, test_user):
    """Test flash messages appear correctly."""
    # Test success message
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': test_user['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Successfully logged in!' in response.data
    
    # Test error message
    response = client.post('/login', data={
        'username': test_user['username'],
        'password': 'WrongPassword123!'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_navigation_state(client, logged_in_client):
    """Test navigation shows correct state based on login status."""
    # When not logged in
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Register' in response.data
    assert b'Logout' not in response.data
    assert b'Profile' not in response.data
    
    # When logged in
    response = logged_in_client.get('/')
    assert response.status_code == 200
    assert b'Login' not in response.data
    assert b'Register' not in response.data
    assert b'Logout' in response.data
    assert b'Profile' in response.data

def test_game_templates(client):
    """Test all game templates render correctly."""
    game_routes = ['/typing', '/speed', '/dexterity', '/precision']
    for route in game_routes:
        response = client.get(route)
        assert response.status_code == 200
        assert b'MindMoves' in response.data
        assert b'Start Game' in response.data

def test_about_template(client):
    """Test about template renders correctly."""
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About MindMoves' in response.data
    assert b'Brain Training Games' in response.data 