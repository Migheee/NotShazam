import os
import yt_dlp
from pydub import AudioSegment

def download_audio(song_name, artist_name):
    """
    Download a song from YouTube, convert it to WAV format, and save it locally.

    This function searches for a song on YouTube using the provided song name and artist name,
    downloads the best quality audio, and converts it from WebM format to WAV format using pydub.

    :param song_name: The name of the song to download.
    :param artist_name: The name of the artist of the song.
    :return: None
    """
    # Build the search query
    search_query = f"{song_name} {artist_name} site:youtube.com"
    
    # Set the options for the YoutubeDL
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio quality
        'outtmpl': f'songs/{song_name}.%(ext)s',  # Output path (save with proper extension)
        'noplaylist': True,  # Don't download playlists
        'quiet': True,  # Show download process
    }
    
    # Download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{search_query}", download=True)
        
        # Get the URL of the downloaded video
        video_url = result['entries'][0]['url']
        
        # This ensures the video is downloaded in the best audio format available
        ydl.download([video_url])
    
    # Assuming the downloaded file is in the 'songs' folder and has a .webm extension
    downloaded_file = f"songs/{song_name}.webm"
    
    if os.path.exists(downloaded_file):
        # Convert from webm to wav using pydub (which requires ffmpeg)
        audio = AudioSegment.from_file(downloaded_file, format="webm")
        audio.export(f"songs/{song_name}.wav", format="wav")
        
        # Optionally, remove the .webm file after conversion
        os.remove(downloaded_file)
