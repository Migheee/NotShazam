import os
from pymongo import MongoClient

# MongoDB Configuration
mongo_client = MongoClient('mongodb://localhost:27017/')

class Config:
    """Flask app configuration."""
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = mongo_client
    SESSION_MONGODB_DB = 'AudioProject'
    SESSION_MONGODB_COLLECTION = 'session'

    # Session cookie settings
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
    SESSION_COOKIE_SECURE = False  # Should be False for HTTP
    SESSION_COOKIE_SAMESITE = 'Lax'  # Allows return redirects
    SESSION_COOKIE_DOMAIN = None  # Restricts cookie to current domain
    SESSION_PERMANENT = True  # Keeps session active across requests
