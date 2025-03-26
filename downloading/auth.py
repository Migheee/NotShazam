import secrets
import os
import string
import hashlib
import base64
import requests
import pymongo
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI= os.getenv("REDIRECT_URI")
SCOPE = 'user-read-private user-read-email'

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["AudioProject"] 
collection = db["sessions"]

def generate_random_string(length=128):
    '''
    Generate a random string of the given length
    :param length: The length of the random string
    :return: The random string
    '''
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def hash_string(string):
    '''
    Hash a string using SHA-256, and encode the hash in base64
    :param string: The string to hash
    :return: The hash of the string encoded in base64
    '''
    hash_bytes = hashlib.sha256(string.encode('utf-8')).digest()  # SHA-256 hash
    return base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')  # Base64 encoding


def request_user_authorization(code_challenge, code_challenge_method='S256'):
    '''
    Request user authorization
    :return: Response object from Spotify authorization endpoint
    '''
    url = 'https://accounts.spotify.com/authorize' #URL to request user authorization

    print(CLIENT_ID)
    # Parameters for the request
    params = {   
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "code_challenge_method": code_challenge_method,
        "code_challenge": code_challenge,
        "redirect_uri":  REDIRECT_URI  #To be changed when app web server is set up
    }
    # Make the request
    response = requests.get(url, params=params)
    return f"{url}?{requests.compat.urlencode(params)}"


def get_token(code_verifier, code):
    """
    Exchange authorization code for access token.
    :param code_verifier: The original code verifier.
    :param code: Authorization code received from Spotify.
    :return: Access token.
    """
    url = "https://accounts.spotify.com/api/token"

    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    body={
        'client_id': CLIENT_ID,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI , #To be changed when app web server is set up
        'code_verifier': code_verifier
    }

    response = requests.post(url, data=body, headers=headers)
    
    return response.json()['access_token']


def refresh_token(refresh_token):
    """
    Refresh Spotify access token.
    :param refresh_token: The refresh token obtained from Spotify.
    :return: New access token.
    """
    url = "https://accounts.spotify.com/api/token"

    headers={
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    body={
        'client_id': CLIENT_ID,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(url, data=body, headers=headers)
    
    return response.json()['refresh_token']
