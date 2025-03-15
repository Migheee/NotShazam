import yt_dlp
from pydub import AudioSegment
import os

def download_audio(song_name, artist_name):
    # Build the search query
    search_query = f"{song_name} {artist_name} site:youtube.com"
    
    # Set the options for the YoutubeDL
    ydl_opts = {
        'format': 'bestaudio/best',  # Best audio quality
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'wav',  # Convert to WAV
            'preferredquality': '192',  # Quality
        }],
        'outtmpl': '../songs/%(id)s.%(ext)s',  # Output path
        'noplaylist': True,  # Don't download playlists
        'quiet': False,
    }
    
    # Download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch:{search_query}", download=True)
        
        # Get the URL of the downloaded video
        video_url = result['entries'][0]['url']
        ydl.download([video_url])
    
    print(f"Audio downloaded and converted to WAV: {song_name} by {artist_name}")

def convert_audio_to_wav(input_file):
    # Convert the audio to WAV
    output_file = os.path.splitext(input_file)[0] + '.wav'
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format='wav')
    print(f"Converted audio to WAV: {output_file}")
    return output_file


song_name = "Porcelain" 
artist_name = "Moby"     

# Scarica e converte la canzone in .wav
download_audio(song_name, artist_name)
