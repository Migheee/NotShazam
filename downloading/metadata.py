from requests import get, post
import json


def get_auth_headers(token):
    '''
    This function returns the authorization headers
    :param token: the token
    :return: the authorization headers
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


