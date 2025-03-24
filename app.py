import os
from flask import Flask, request, session, redirect, jsonify
from flask_session import Session
from pymongo import MongoClient
import requests
from downloading.auth import generate_random_string, hash_string, request_user_authorization, get_token

# Configurazione MongoDB per la sessione
mongo_client = MongoClient('mongodb://localhost:27017/')

db = mongo_client.AudioProject

# Crea l'app Flask
app = Flask(__name__)

# Chiave segreta per la sessione
app.secret_key = os.urandom(24)

# Configurazione della sessione
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_MONGODB'] = mongo_client
app.config['SESSION_MONGODB_DB'] = 'AudioProject'
app.config['SESSION_MONGODB_COLLECTION'] = 'session'

# Configurazione dei cookie della sessione
app.config['SESSION_COOKIE_NAME'] = 'session'
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Impedisce l’accesso via JavaScript
app.config['SESSION_COOKIE_SECURE'] = False  # Deve essere False perché Flask gira in HTTP
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Permette i redirect di ritorno
app.config['SESSION_COOKIE_DOMAIN'] = None  # Mantiene il cookie solo per il dominio attuale
app.config['SESSION_PERMANENT'] = True  # Mantiene la sessione attiva tra le richieste

# Inizializza la sessione
Session(app)

@app.route('/')
def home():
    code_verifier = generate_random_string(64)
    session['code_verifier'] = code_verifier
    print("Cookie della sessione impostato:", dict(session))  # Debug
    return 'hello'

@app.route('/auth')
def authenticate():
    if 'code_verifier' not in session:
        code_verifier = generate_random_string(64)
        session['code_verifier'] = code_verifier
        session.permanent = True
        session.modified = True

    code_challenge = hash_string(session['code_verifier'])
    auth_url = request_user_authorization(code_challenge)
    print("Sessione prima del redirect:", dict(session))  # Debug
    return redirect(auth_url)

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    print("Sessione dopo il redirect:", dict(session))  # Debug

    if not code:
        return "Error: missing code", 400

    code_verifier = session.get('code_verifier')
    if not code_verifier:
        return "Error: missing code_verifier", 400

    print("Code Verifier trovato:", code_verifier, "Code:", code)
    token = get_token(code_verifier, code)

    session.pop('code_verifier', None)  # Pulizia sessione
    session['access_token'] = token  # Salvataggio dell'access token
    return redirect('/pagina.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
