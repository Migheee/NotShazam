from dotenv import load_dotenv
import os
import base64
from requests import get, post
import json

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    '''
    This function retrieves the token for the Spotify API
    :return: the token
    '''

    # Encode the client_id and client_secret
    auth = f"{client_id}:{client_secret}"
    message_bytes = auth.encode('utf-8')
    auth_base64 = str(base64.b64encode(message_bytes), 'utf-8')

    # Get the token
    url = "https://accounts.spotify.com/api/token"
    headers = {
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


def get_auth_headers(token):
    '''
    This function returns the headers for the Spotify API
    :param token: the token
    :return: the headers
    '''
    return {
        "Authorization": f"Bearer {token}"
    }


def get_song_metadata(song_id, token):
    '''
    This function retrieves the metadata of a song
    :param song_id: the id of the song
    :param token: the token
    :return: the song name, the artist and the album
    '''

    # Construct the URL for the Spotify API request
    url = f"https://api.spotify.com/v1/tracks/{song_id}"  
    headers = get_auth_headers(token)  

    # Make the GET request to the Spotify API
    result = get(url, headers=headers) 

    # Parse the JSON response to get the song metadata 
    song_metadata = result.json()  

    # Extract the song name, artist name, and album name from the metadata
    song_name = song_metadata["name"]  
    artist_name = song_metadata["artists"][0]["name"]  
    album_name = song_metadata["album"]["name"]  
    return song_name, artist_name, album_name  


def get_songs_from_playlist(playlist_id, token):
    '''
    This function retrieves the songs from a playlist
    :param playlist_id: the id of the playlist
    :param token: the token
    :return: the list of songs
    '''

    # Construct the URL for the Spotify API request
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"  
    headers = get_auth_headers(token)  

    # Make the GET request to the Spotify API
    result = get(url, headers=headers)  

    # Parse the JSON response to get the songs
    playlist_metadata = result.json()  

    # Extract the list of songs from the metadata
    songs = playlist_metadata["items"]  
    for song in songs:
        try:
            song_name = song["track"]["name"]
            artist_name = song["track"]["artists"][0]["name"]  
            print(f"Song: {song_name}")
            print(f"Artist: {artist_name}")
        except:
            print("Error")

    return songs

token = get_token()
song_id="5JgTIfS7FfSE9tuebzX8HC"
song_name, artist_name, album_name = get_song_metadata(song_id, token)
print(f"Song: {song_name}")
print(f"Artist: {artist_name}")
print(f"Album: {album_name}")

playlist_id="3b3AgBdPfyDvq1xi26vdYh"
token = get_token()
songs = get_songs_from_playlist(playlist_id, token)
