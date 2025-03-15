import mysql.connector
import create_fingerprint  # Ensure this imports the necessary functions
import json

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',  
    password='',  
    database='audioproject'
)

cursor = conn.cursor()

def add_song_to_database(name, artist, album, fingerprint):
    '''
    This function inserts a song and its fingerprint into the database.
    :param name: Name of the song
    :param artist: Artist of the song
    :param album: Album of the song
    :param fingerprint: Fingerprint data of the song (list or other serializable format)
    '''
    # Serialize the fingerprint as a JSON string
    fingerprint_json = json.dumps(fingerprint)

    # Insert song information into the table
    cursor.execute('''
    INSERT INTO songs (name, artist, album, fingerprint)
    VALUES (%s, %s, %s, %s)
    ''', (name, artist, album, fingerprint_json))

    # Commit the changes to the database
    conn.commit()


# Function to close the cursor and the connection to the database
def close_database_connection():
    '''
    This function closes the cursor and the connection to the database.
    '''
    cursor.close()
    conn.close()


# Load the song and generate the spectrogram
spectrogram, sr = create_fingerprint.get_spectrogram("songs\\Soulmate.wav")
# Find the peaks in the spectrogram
peaks = create_fingerprint.get_peaks(spectrogram)
# Find the anchor points
anchor_points = create_fingerprint.get_anchor_point(spectrogram,peaks)

# Generate the fingerprint of the song
fingerprint = create_fingerprint.get_fingerprint(anchor_points)

# Add the song and its fingerprint to the database
add_song_to_database("Soulmate", "Mac Miller", "The Divine Feminine", fingerprint)
