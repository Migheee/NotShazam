from flask import Flask, request, session, redirect
from flask_session import Session  
from downloading import auth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

# Flask-Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
Session(app)  

@app.route('/auth')
def authenticate():
    code_verifier = auth.generate_random_string(64)
    code_challenge = auth.hash_string(code_verifier)

    session['code_verifier'] = code_verifier  # Store the code_verifier in the session
    auth_url = auth.request_user_authorization(code_challenge)

    return redirect(auth_url)  # Redirect the user to the authorization URL

@app.route('/callback')
def callback():
    code = request.args.get('code')  # Retrieve the authorization code from the query parameters
    code_verifier = session.get('code_verifier')  # Retrieve the code_verifier from the session
    if not code_verifier:
        return "Error: missing code_verifier", 400
    session.pop('code_verifier', None)  # Remove the code_verifier from the session
    token = auth.get_token(code_verifier, code)
    return token

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')

