from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
def init_db():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'leaderboard.db')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS leaderboard 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      player_name TEXT, 
                      score INTEGER)''')

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'leaderboard.db')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT player_name, score FROM leaderboard ORDER BY score DESC LIMIT 10')
        rows = c.fetchall()
    return jsonify([{'player': player, 'score': score} for player, score in rows])

@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = request.json
    player_name = data.get('player_name')
    score = data.get('score')
    
    if not player_name or not score:
        return jsonify({'status': 'error', 'message': 'Missing player_name or score'}), 400

    try:
        score = int(score)  # Convert score to integer
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Score must be an integer'}), 400

    db_path = os.path.join(os.path.dirname(__file__), 'data', 'leaderboard.db')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO leaderboard (player_name, score) VALUES (?, ?)', (player_name, score))
    
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(host='0.0.0.0', port=5000)