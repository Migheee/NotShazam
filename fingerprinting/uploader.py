from pymongo import MongoClient
import create_fingerprint  

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["AudioProject"]
collection = db["songs"]

def add_song_to_database(name, artist, album, fingerprint):
    '''
    This function adds a song to the database
    :param name: the name of the song
    :param artist: the artist of the song
    :param album: the album of the song
    :param fingerprint: the fingerprint of the song
    '''
    song_data = {
        "name": name,
        "artist": artist,
        "album": album,
        "fingerprint": fingerprint  # Hash Lists (fingerprints) of the song
    }
    collection.insert_one(song_data)

# Example of usage
spectrogram, sr = create_fingerprint.get_spectrogram("songs/Soulmate.wav")
peaks = create_fingerprint.get_peaks(spectrogram)
filtered_peaks = create_fingerprint.filter_peaks_by_intensity(spectrogram, peaks)
anchor_points = create_fingerprint.get_anchor_points(filtered_peaks, spectrogram)
fingerprint = create_fingerprint.get_fingerprint(anchor_points)

# Storing the song in the database
add_song_to_database("Soulmate", "Mac Miller", "The Divine Feminine", fingerprint)

# Close the MongoDB connection
client.close()
