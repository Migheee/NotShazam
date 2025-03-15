from pymongo import MongoClient
import create_fingerprint  # Assicurati che questo modulo contenga le funzioni necessarie

# Connessione a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["AudioProject"]
collection = db["songs"]

def add_song_to_database(name, artist, album, fingerprint):
    '''
    Questa funzione inserisce una canzone e il suo fingerprint nel database MongoDB.
    '''
    song_data = {
        "name": name,
        "artist": artist,
        "album": album,
        "fingerprint": fingerprint  # Lista di hash
    }
    collection.insert_one(song_data)
    print(f"Canzone '{name}' aggiunta al database.")

# Generazione fingerprint per una canzone
spectrogram, sr = create_fingerprint.get_spectrogram("songs/Soulmate.wav")
peaks = create_fingerprint.get_peaks(spectrogram)
anchor_points = create_fingerprint.get_anchor_point(spectrogram, peaks)
fingerprint = create_fingerprint.get_fingerprint(anchor_points)

# Salvataggio nel database
add_song_to_database("Soulmate", "Mac Miller", "The Divine Feminine", fingerprint)

# Chiudi la connessione
client.close()
