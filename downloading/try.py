from dotenv import load_dotenv
import os
import base64
from requests import post
import json



load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth = f"{client_id}:{client_secret}"
    message_bytes = auth.encode('utf-8')
    auth_base64 = str(base64.b64encode(message_bytes), 'utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers={
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_headers():
    return {
        "Authorization": f"Bearer {token}"
    }

token = get_token()
print(token)
