from flask import Flask, request, session, redirect, jsonify, render_template
from flask_session import Session
from config import Config, mongo_client
from downloading.auth import (
    generate_random_string, hash_string, request_user_authorization, get_token
)
from downloading.metadata import get_song_metadata
from downloading.download import download_audio
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize session
Session(app)

@app.route('/')
def home():
    """Home route to set up session code verifier."""
    try:
        session['code_verifier'] = generate_random_string(64)
        return 'Hello'
    except Exception as e:
        logger.exception("Error in home route")
        return "Internal Server Error", 500

@app.route('/auth')
def authenticate():
    """Authentication route to generate authorization URL."""
    session.setdefault('code_verifier', generate_random_string(64))
    session.permanent = True
    session.modified = True
    
    auth_url = request_user_authorization(hash_string(session['code_verifier']))
    return redirect(auth_url)

@app.route('/callback', methods=['GET'])
def callback():
    """Callback route to handle authorization response."""
    code = request.args.get('code')
    if not code:
        return "Error: missing code", 400

    code_verifier = session.pop('code_verifier', None)
    if not code_verifier:
        return "Error: missing code_verifier", 400

    session['access_token'] = get_token(code_verifier, code)
    return render_template('prova.html')

@app.route('/download', methods=['POST'])
def download_song():
    """Route to handle song download request."""
    data = request.get_json()
    track_id = data.get('id')

    if not track_id:
        return "Error: missing track ID", 400

    try:
        # Retrieve song metadata
        song_name, artist_name, album_name = get_song_metadata(track_id, session.get('access_token'))
        download_audio(song_name, artist_name)
        return f"Download started successfully for song: {song_name}", 200
    except Exception as e:
        logger.exception("Error handling download request")
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
