import pytest
from datetime import datetime, timedelta
from app import create_app
from app.auth import save_game_score
from bs4 import BeautifulSoup

def test_game_history_order_and_limit():
    """Test that game history shows 20 most recent scores in reverse chronological order."""
    app = create_app()
    
    with app.test_client() as client:
        # 1. Register and login a test user
        client.post('/register', data={
            'first_name': 'Test',
            'username': 'testuser',
            'password': 'TestPass123!',
            'secret_question': 'Test question?',
            'secret_answer': 'Test answer'
        })
        client.post('/login', data={
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        # 2. Create 25 test scores with different timestamps
        base_time = datetime.now()
        scores = []
        for i in range(25):
            # Add microseconds to ensure unique timestamps
            timestamp = base_time - timedelta(minutes=i, microseconds=i)
            score_data = {
                'game_type': f'Test Game {i+1}',
                'score': i+1,
                'total': 100,
                'date': timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')
            }
            scores.append(score_data)
            save_game_score('testuser', score_data['game_type'], score_data['score'], score_data['total'])
        
        # 3. Get profile page and check game history
        response = client.get('/profile')
        assert response.status_code == 200
        
        # Parse the HTML response
        soup = BeautifulSoup(response.data, 'html.parser')
        score_cards = soup.find_all('div', class_='score-card')
        
        # 4. Verify only 20 scores are shown
        assert len(score_cards) == 20, "Should show exactly 20 scores"
        
        # 5. Get the dates from the score cards
        dates = []
        for card in score_cards:
            date_text = card.find('p').text.strip()
            dates.append(datetime.strptime(date_text, '%Y-%m-%d %H:%M:%S.%f'))
        
        # 6. Verify scores are in reverse chronological order (newest first)
        for i in range(len(dates) - 1):
            assert dates[i] > dates[i + 1], f"Score at position {i} should be newer than score at position {i+1}"
        
        # 7. Verify we have the most recent scores
        # The oldest shown date should be no more than 20 minutes from the base time
        oldest_shown_date = dates[-1]
        time_difference = (base_time - oldest_shown_date).total_seconds() / 60  # Convert to minutes
        assert time_difference < 20, "Should show 20 most recent scores"
        
        # 8. Verify older scores are not shown
        for i in range(20, 25):
            game_name = f'Test Game {i+1}'
            assert game_name not in response.data.decode('utf-8'), f"Older score {game_name} should not be shown" 