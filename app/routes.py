@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    # Get game history and sort by timestamp in reverse order
    game_history = GameScore.query.filter_by(user_id=user.id)\
        .order_by(GameScore.timestamp.desc())\
        .limit(20)\
        .all()
    
    return render_template('profile.html', 
                         user=user, 
                         game_history=game_history,
                         active_page='profile') 